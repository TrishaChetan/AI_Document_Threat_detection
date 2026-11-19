"""Security gate for CI: pass or fail a build based on a ZAP report.

Policy (all optional):
    fail_on    lowest severity that fails the build on its own   (default "High")
    max        allowed counts per severity, e.g. {"Medium": 5}
    ignore     accepted risks: [{"match": "Cookie No HttpOnly Flag" | "cwe:1004",
                                 "until": "2026-12-31", "reason": "fix in v2.3"}]
               An ignore stops applying after its `until` date, so accepted
               risks can't be forgotten forever.

With a baseline report only *new* findings (and findings whose severity went
up) count, so a legacy app can adopt the gate without fixing everything first.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date

from services.scan_diff import SEVERITY_RANK, diff_reports

SEVERITIES = ["High", "Medium", "Low", "Informational"]


@dataclass
class Policy:
    fail_on: str = "High"
    max: dict[str, int] = field(default_factory=dict)
    ignore: list[dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "Policy":
        p = cls(fail_on=_sev(d.get("fail_on", "High")) if d.get("fail_on") not in (None, "none") else "none",
                max={_sev(k): int(v) for k, v in (d.get("max") or {}).items()},
                ignore=list(d.get("ignore") or []))
        for rule in p.ignore:
            if not isinstance(rule, dict) or not rule.get("match"):
                raise ValueError("each ignore entry needs a 'match' (finding title or cwe:<id>)")
            if rule.get("until"):
                date.fromisoformat(rule["until"])  # raises ValueError on a bad date
        return p

    @classmethod
    def load(cls, path: str) -> "Policy":
        with open(path, encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))


def _sev(name: str) -> str:
    n = str(name).strip().capitalize()
    n = "Informational" if n in ("Info", "Informational") else n
    if n not in SEVERITIES:
        raise ValueError(f"unknown severity '{name}' — use High, Medium, Low or Informational")
    return n


def _ignored(f: dict, rules: list[dict], today: date) -> dict | None:
    for r in rules:
        if r.get("until") and date.fromisoformat(r["until"]) < today:
            continue
        m = str(r["match"]).strip()
        if m.lower().startswith("cwe:"):
            if (f.get("cwe") or "") == m[4:].strip():
                return r
        elif m.lower() == (f.get("title") or "").lower():
            return r
    return None


def evaluate(report, policy: Policy, baseline=None, today: date | None = None) -> dict:
    today = today or date.today()
    if baseline is not None:
        d = diff_reports(baseline, report)
        findings = d["new"] + [f for f in d["severity_changed"]
                               if SEVERITY_RANK.get(f["severity"], 0) > SEVERITY_RANK.get(f["previous_severity"], 0)]
        scope = f"new since baseline; {d['summary']['fixed']} fixed, {d['summary']['persisting']} unchanged"
    else:
        findings = [{"title": v.title, "severity": v.severity, "cwe": v.cwe, "affected_url": v.affected_url,
                     "parameter": v.parameter} for v in report.vulnerabilities]
        scope = "all findings"

    counted, waived, expired = [], [], []
    for f in findings:
        rule = _ignored(f, policy.ignore, today)
        if rule:
            waived.append({**f, "reason": rule.get("reason", ""), "until": rule.get("until")})
        else:
            counted.append(f)
    for r in policy.ignore:
        if r.get("until") and date.fromisoformat(r["until"]) < today:
            expired.append(r)

    counts = {s: sum(1 for f in counted if f["severity"] == s) for s in SEVERITIES}
    violations = []
    if policy.fail_on != "none":
        limit = SEVERITY_RANK[policy.fail_on]
        for f in counted:
            if SEVERITY_RANK.get(f["severity"], 0) >= limit:
                violations.append({"type": "severity", "finding": f,
                                   "message": f"{f['severity']}: {f['title']}"
                                              + (f" at {f['affected_url']}" if f.get("affected_url") else "")})
    for sev, allowed in policy.max.items():
        if counts.get(sev, 0) > allowed:
            violations.append({"type": "budget", "severity": sev,
                               "message": f"{counts[sev]} {sev} finding(s), budget is {allowed}"})
    return {"passed": not violations, "scope": scope, "counts": counts, "violations": violations,
            "waived": waived, "expired_ignores": expired,
            "target": report.scan_info.target, "policy": {"fail_on": policy.fail_on, "max": policy.max}}


def format_text(res: dict) -> str:
    lines = [("✅ PASS" if res["passed"] else "⛔ FAIL") + f" — {res['target']} ({res['scope']})",
             "  counted: " + (", ".join(f"{n} {s}" for s, n in res["counts"].items() if n) or "none")]
    for v in res["violations"]:
        lines.append(f"  ✗ {v['message']}")
    for w in res["waived"]:
        lines.append(f"  · waived: {w['title']}" + (f" (until {w['until']})" if w.get("until") else "")
                     + (f" — {w['reason']}" if w.get("reason") else ""))
    for r in res["expired_ignores"]:
        lines.append(f"  ! ignore for '{r['match']}' expired on {r['until']} — it counts again")
    return "\n".join(lines)


def github_annotations(res: dict) -> list[str]:
    """Workflow commands GitHub Actions turns into annotations on the run."""
    out = []
    for v in res["violations"]:
        out.append(f"::error title=Security gate::{v['message']}")
    for r in res["expired_ignores"]:
        out.append(f"::warning title=Expired risk acceptance::{r['match']} (expired {r['until']})")
    return out


def markdown_summary(res: dict) -> str:
    rows = "\n".join(f"| {s} | {n} |" for s, n in res["counts"].items())
    md = [f"### Security gate: {'✅ passed' if res['passed'] else '⛔ failed'}", "",
          f"Target `{res['target']}` · {res['scope']}", "", "| Severity | Counted |", "|---|---|", rows]
    if res["violations"]:
        md += ["", "**Why it failed**", ""] + [f"- {v['message']}" for v in res["violations"]]
    if res["waived"]:
        md += ["", "**Accepted risks**", ""] + [f"- {w['title']}" + (f" (until {w['until']})" if w.get("until") else "")
                                               for w in res["waived"]]
    return "\n".join(md) + "\n"
