"""Compare two scan reports of the same application.

Answers the question every re-test asks: what did the last release fix, what
did it introduce, and what is still open?

Findings are matched on (title, CWE, URL path, parameter). The host/port and
query string are ignored, so a re-scan against staging vs. localhost, or with
different session tokens in the URL, still lines up. A finding whose severity
changed between scans is reported as "changed".
"""
from __future__ import annotations

from urllib.parse import urlsplit

SEVERITY_RANK = {"High": 3, "Medium": 2, "Low": 1, "Informational": 0, "Unknown": 0}


def _path(url: str | None) -> str:
    if not url:
        return ""
    parts = urlsplit(url if "://" in url else "http://x/" + url.lstrip("/"))
    return (parts.path or "/").rstrip("/").lower() or "/"


def finding_key(v) -> tuple:
    return (
        (v.title or "").strip().lower(),
        (v.cwe or "").strip(),
        _path(v.affected_url),
        (v.parameter or "").strip().lower(),
    )


def _brief(v) -> dict:
    return {
        "title": v.title,
        "severity": v.severity,
        "cwe": v.cwe,
        "affected_url": v.affected_url,
        "parameter": v.parameter,
    }


def _sorted(items):
    return sorted(items, key=lambda d: (-SEVERITY_RANK.get(d["severity"], 0), d["title"]))


def diff_reports(baseline, current) -> dict:
    """baseline/current: ScanReport objects (from parsers.parse_report)."""
    old = {}
    for v in baseline.vulnerabilities:
        old.setdefault(finding_key(v), v)
    new = {}
    for v in current.vulnerabilities:
        new.setdefault(finding_key(v), v)

    introduced = [_brief(new[k]) for k in new.keys() - old.keys()]
    fixed = [_brief(old[k]) for k in old.keys() - new.keys()]
    persisting, changed = [], []
    for k in old.keys() & new.keys():
        o, n = old[k], new[k]
        if o.severity != n.severity:
            changed.append({**_brief(n), "previous_severity": o.severity})
        else:
            persisting.append(_brief(n))

    def count(items, sev):
        return sum(1 for i in items if i["severity"] == sev)

    high_delta = count(introduced, "High") - count(fixed, "High")
    if not old and not new:
        trend = "no findings in either scan"
    elif high_delta < 0 or (high_delta == 0 and len(fixed) > len(introduced)):
        trend = "improved"
    elif high_delta > 0 or len(introduced) > len(fixed):
        trend = "regressed"
    else:
        trend = "unchanged"

    return {
        "baseline": {"report": baseline.scan_info.report_name, "target": baseline.scan_info.target,
                     "findings": len(old)},
        "current": {"report": current.scan_info.report_name, "target": current.scan_info.target,
                    "findings": len(new)},
        "summary": {
            "new": len(introduced),
            "fixed": len(fixed),
            "persisting": len(persisting),
            "severity_changed": len(changed),
            "new_high": count(introduced, "High"),
            "fixed_high": count(fixed, "High"),
            "trend": trend,
        },
        "new": _sorted(introduced),
        "fixed": _sorted(fixed),
        "severity_changed": _sorted(changed),
        "persisting": _sorted(persisting),
    }


def format_diff(d: dict) -> str:
    s = d["summary"]
    lines = [
        f"Baseline: {d['baseline']['report']} ({d['baseline']['findings']} findings)",
        f"Current:  {d['current']['report']} ({d['current']['findings']} findings)",
        f"Trend: {s['trend'].upper()}  ·  {s['new']} new ({s['new_high']} High)  ·  "
        f"{s['fixed']} fixed ({s['fixed_high']} High)  ·  {s['persisting']} still open  ·  "
        f"{s['severity_changed']} changed severity",
    ]
    for label, key in (("NEW", "new"), ("FIXED", "fixed"), ("CHANGED", "severity_changed")):
        for f in d[key]:
            where = f["affected_url"] or ""
            prev = f" (was {f['previous_severity']})" if "previous_severity" in f else ""
            lines.append(f"  {label:<8} [{f['severity']}{prev}] {f['title']}  {where}")
    return "\n".join(lines)
