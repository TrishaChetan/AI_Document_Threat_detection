"""Turn a scan report into a remediation plan: fix tickets with due dates.

Scanners report symptoms; teams fix causes. Several ZAP alerts usually share
one fix (CSP, X-Frame-Options and X-Content-Type-Options are all "add the
security headers in the web-server config"), so findings are grouped into
tickets by fix theme, falling back to one ticket per alert type.

Each ticket gets a due date from a severity SLA counted from the scan date
(defaults below, override per team), and is flagged overdue once that passes.

    cd backend
    python remediation_plan.py ../reports/zap/xml/webgoat_scan_01.xml
    python remediation_plan.py report.json --format csv -o plan.csv --sla high=14,medium=60
"""
from __future__ import annotations

import csv
import io
import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta

from services.findings_export import _plain

DEFAULT_SLA_DAYS = {"High": 30, "Medium": 90, "Low": 180, "Informational": 365, "Unknown": 180}
SEVERITY_RANK = {"High": 3, "Medium": 2, "Low": 1, "Informational": 0, "Unknown": 0}

# (key, ticket title, title regex, where the fix lives, effort, how to fix)
THEMES = [
    ("headers", "Add missing HTTP security headers",
     r"content security policy|csp\b|anti-clickjacking|x-frame-options|x-content-type-options|"
     r"strict-transport-security|hsts|permissions policy|referrer-policy|cross-origin-.*policy",
     "Web server / reverse proxy config", "S",
     "Set the headers once for every response in the web server, load balancer or app middleware "
     "(e.g. Content-Security-Policy, X-Frame-Options: DENY, X-Content-Type-Options: nosniff, "
     "Strict-Transport-Security)."),
    ("cookies", "Harden session cookie flags",
     r"cookie",
     "Application code (session/cookie settings)", "S",
     "Set HttpOnly, Secure and SameSite=Lax (or Strict) on session and auth cookies in the "
     "framework's cookie settings."),
    ("disclosure", "Stop leaking server and framework versions",
     r"server leaks|x-powered-by|version information|banner information|x-aspnet-version|debug error",
     "Web server / reverse proxy config", "S",
     "Remove or blank the Server, X-Powered-By and similar headers and turn off verbose error pages."),
    ("injection", "Fix injection flaws (validate and parameterise input)",
     r"sql injection|command injection|code injection|xpath|ldap injection|remote os command|"
     r"server side include|template injection|xml external entity|xxe",
     "Application code", "L",
     "Use parameterised queries / safe APIs everywhere user input reaches an interpreter, and add "
     "regression tests for the affected parameters."),
    ("xss", "Fix cross-site scripting (encode output)",
     r"cross site scripting|cross-site scripting|xss",
     "Application code", "M",
     "Encode output for its context (HTML, attribute, JS, URL), avoid innerHTML-style sinks, and "
     "back it up with a Content-Security-Policy."),
    ("transport", "Enforce HTTPS everywhere",
     r"mixed content|insecure transport|http to https|secure pages include|weak cipher|tls",
     "Web server / reverse proxy config", "M",
     "Redirect all HTTP to HTTPS, serve every sub-resource over HTTPS and disable weak TLS settings."),
    ("csrf", "Add CSRF protection to state-changing forms",
     r"anti-csrf|csrf",
     "Application code", "M",
     "Use the framework's CSRF tokens on every POST/PUT/DELETE form and API, plus SameSite cookies."),
]
_THEME_RES = [(k, t, re.compile(rx, re.I), w, e, h) for k, t, rx, w, e, h in THEMES]


@dataclass
class Ticket:
    id: str
    title: str
    severity: str
    due: str
    days_left: int
    overdue: bool
    where: str
    effort: str
    how_to_fix: str
    findings: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    cwes: list[str] = field(default_factory=list)


def parse_sla(text: str | None) -> dict[str, int]:
    """'high=14,medium=60' -> DEFAULT_SLA_DAYS with those overridden."""
    sla = dict(DEFAULT_SLA_DAYS)
    for part in filter(None, (p.strip() for p in (text or "").split(","))):
        name, _, days = part.partition("=")
        key = name.strip().capitalize()
        if key == "Info":
            key = "Informational"
        if key not in sla or not days.strip().isdigit():
            raise ValueError(f"bad SLA entry '{part}' — use e.g. high=14,medium=60,low=120")
        sla[key] = int(days)
    return sla


def scan_date(report) -> date:
    """Date the scan ran: ZAP writes 'Sun, 26 Jul 2026 12:55:12'; ISO dates also work."""
    raw = (getattr(report.scan_info, "generated_at", "") or "").strip()
    m = re.search(r"\d{4}-\d{2}-\d{2}", raw)
    if m:
        return date.fromisoformat(m.group(0))
    m = re.search(r"(\d{1,2}) ([A-Za-z]{3}) (\d{4})", raw)
    if m:
        try:
            return datetime.strptime(" ".join(m.groups()), "%d %b %Y").date()
        except ValueError:
            pass
    return date.today()


def _theme(title: str):
    for key, ttitle, rx, where, effort, how in _THEME_RES:
        if rx.search(title or ""):
            return key, ttitle, where, effort, how
    return None


def build_plan(report, today: date | None = None, sla: dict[str, int] | None = None,
               include_info: bool = False) -> dict:
    sla = sla or DEFAULT_SLA_DAYS
    today = today or date.today()
    found = scan_date(report)
    groups: dict[str, dict] = {}
    for v in report.vulnerabilities:
        if v.severity == "Informational" and not include_info:
            continue
        theme = _theme(v.title)
        if theme:
            key, title, where, effort, how = theme
        else:
            key = "alert:" + (v.title or "Finding").lower()
            title, where = v.title or "Finding", "Application or server (see finding)"
            effort = "M" if v.severity == "High" else "S"
            how = _plain(v.solution) or "See the scanner's references for this finding."
        g = groups.setdefault(key, {"title": title, "where": where, "effort": effort, "how": how,
                                    "sev": v.severity, "findings": [], "urls": [], "cwes": []})
        if SEVERITY_RANK.get(v.severity, 0) > SEVERITY_RANK.get(g["sev"], 0):
            g["sev"] = v.severity
        if v.title not in g["findings"]:
            g["findings"].append(v.title)
        if v.affected_url and v.affected_url not in g["urls"]:
            g["urls"].append(v.affected_url)
        if v.cwe and v.cwe not in ("-1", "0") and v.cwe not in g["cwes"]:
            g["cwes"].append(v.cwe)

    tickets = []
    for g in groups.values():
        due = found + timedelta(days=sla.get(g["sev"], 180))
        tickets.append(Ticket(id="", title=g["title"], severity=g["sev"], due=due.isoformat(),
                              days_left=(due - today).days, overdue=due < today, where=g["where"],
                              effort=g["effort"], how_to_fix=g["how"], findings=g["findings"],
                              urls=g["urls"], cwes=g["cwes"]))
    # most urgent first: severity, then overdue / soonest due, then widest impact
    tickets.sort(key=lambda t: (-SEVERITY_RANK.get(t.severity, 0), t.days_left, -len(t.findings), -len(t.urls)))
    for i, t in enumerate(tickets, 1):
        t.id = f"FIX-{i:02d}"
    return {
        "target": report.scan_info.target,
        "scan_date": found.isoformat(),
        "as_of": today.isoformat(),
        "sla_days": sla,
        "findings_in": sum(len(t.findings) for t in tickets),
        "tickets": [asdict(t) for t in tickets],
        "overdue": sum(t.overdue for t in tickets),
    }


def to_markdown(plan: dict) -> str:
    out = [f"# Remediation plan — {plan['target']}", "",
           f"Scan {plan['scan_date']} · as of {plan['as_of']} · {plan['findings_in']} finding type(s) → "
           f"**{len(plan['tickets'])} ticket(s)**" + (f" · ⚠️ {plan['overdue']} overdue" if plan["overdue"] else ""),
           "", "| Ticket | Severity | Due | Fix in | Effort | Covers |", "|---|---|---|---|---|---|"]
    for t in plan["tickets"]:
        due = f"**{t['due']} (overdue {-t['days_left']}d)**" if t["overdue"] else f"{t['due']} ({t['days_left']}d)"
        out.append(f"| {t['id']} {t['title']} | {t['severity']} | {due} | {t['where']} | {t['effort']} | "
                   f"{len(t['findings'])} finding(s), {len(t['urls'])} URL(s) |")
    for t in plan["tickets"]:
        out += ["", f"## {t['id']} · {t['title']}", "",
                f"**Severity:** {t['severity']} · **Due:** {t['due']} · **Fix in:** {t['where']} · **Effort:** {t['effort']}",
                "", t["how_to_fix"], "", "Findings: " + "; ".join(t["findings"])]
        if t["cwes"]:
            out.append("CWE: " + ", ".join(f"[CWE-{c}](https://cwe.mitre.org/data/definitions/{c}.html)" for c in t["cwes"]))
        if t["urls"]:
            out.append("Affected: " + ", ".join(t["urls"][:10]) + (f" … +{len(t['urls']) - 10} more" if len(t["urls"]) > 10 else ""))
    return "\n".join(out) + "\n"


def to_csv(plan: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "title", "severity", "due", "days_left", "overdue", "where", "effort",
                "findings", "urls", "cwes", "how_to_fix"])
    for t in plan["tickets"]:
        w.writerow([t["id"], t["title"], t["severity"], t["due"], t["days_left"], "yes" if t["overdue"] else "no",
                    t["where"], t["effort"], " | ".join(t["findings"]), " ".join(t["urls"]),
                    " ".join(t["cwes"]), t["how_to_fix"]])
    return buf.getvalue()
