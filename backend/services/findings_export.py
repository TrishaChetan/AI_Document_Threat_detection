"""Export parsed findings to SARIF 2.1.0 or CSV.

SARIF is the standard static/dynamic-analysis results format read by GitHub
code scanning (Security tab), Azure DevOps, GitLab and the VS Code SARIF
viewer. Each ZAP alert type becomes a SARIF rule (with CWE/WASC tags and the
ZAP solution as help text) and each finding a result located at its URL.

    cd backend
    python export_findings.py ../reports/zap/xml/dvwa_scan_01.xml --format sarif -o zap.sarif
    python export_findings.py report.json --format csv -o findings.csv

Upload to GitHub:  gh api repos/OWNER/REPO/code-scanning/sarifs ... or use
github/codeql-action/upload-sarif in a workflow.
"""
from __future__ import annotations

import csv
import hashlib
import html
import io
import re

SARIF_LEVEL = {"High": "error", "Medium": "warning", "Low": "note", "Informational": "none", "Unknown": "none"}
# GitHub code scanning orders alerts by this 0-10 "security-severity"
SECURITY_SEVERITY = {"High": "8.0", "Medium": "5.5", "Low": "3.0", "Informational": "0.0", "Unknown": "0.0"}
CSV_FIELDS = ["severity", "title", "cwe", "wasc", "confidence", "affected_url", "parameter", "evidence",
              "description", "solution", "references"]


def _plain(text: str | None) -> str:
    """ZAP descriptions contain <p> tags and entities — make them readable."""
    if not text:
        return ""
    text = re.sub(r"</p>\s*<p>|<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def _rule_id(v) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (v.title or "finding").lower()).strip("-")
    return f"zap/{v.cwe or 'na'}/{slug}"[:120]


def to_sarif(report) -> dict:
    rules: dict[str, dict] = {}
    results = []
    for v in report.vulnerabilities:
        rid = _rule_id(v)
        if rid not in rules:
            tags = ["security"] + ([f"external/cwe/cwe-{v.cwe}"] if v.cwe and v.cwe != "-1" else []) \
                   + ([f"external/wasc/wasc-{v.wasc}"] if v.wasc else [])
            rules[rid] = {
                "id": rid,
                "name": re.sub(r"[^A-Za-z0-9]", "", (v.title or "Finding").title())[:60] or "Finding",
                "shortDescription": {"text": v.title or "Finding"},
                "fullDescription": {"text": _plain(v.description)[:1000] or v.title or "Finding"},
                "help": {"text": _plain(v.solution) or "See references."},
                "helpUri": (v.references or [None])[0] or (f"https://cwe.mitre.org/data/definitions/{v.cwe}.html"
                                                            if v.cwe and v.cwe != "-1" else None),
                "defaultConfiguration": {"level": SARIF_LEVEL.get(v.severity, "warning")},
                "properties": {"tags": tags, "security-severity": SECURITY_SEVERITY.get(v.severity, "0.0")},
            }
            if not rules[rid]["helpUri"]:
                del rules[rid]["helpUri"]
        where = v.affected_url or report.scan_info.target or "unknown"
        msg = f"{v.title} at {where}" + (f" (parameter '{v.parameter}')" if v.parameter else "")
        if v.evidence:
            msg += f". Evidence: {v.evidence[:200]}"
        fingerprint = hashlib.sha256("|".join([rid, where, v.parameter or ""]).encode()).hexdigest()
        results.append({
            "ruleId": rid,
            "level": SARIF_LEVEL.get(v.severity, "warning"),
            "message": {"text": msg},
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": where}}}],
            "partialFingerprints": {"primaryLocationLineHash": fingerprint},
            "properties": {"severity": v.severity, "confidence": v.confidence},
        })
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": report.scan_info.scanner or "OWASP ZAP",
                "informationUri": "https://www.zaproxy.org/",
                "rules": list(rules.values()),
            }},
            "automationDetails": {"id": f"zap/{report.scan_info.report_name}"},
            "results": results,
        }],
    }


def to_csv(report) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_FIELDS)
    w.writeheader()
    order = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3}
    for v in sorted(report.vulnerabilities, key=lambda v: (order.get(v.severity, 9), v.title or "")):
        w.writerow({
            "severity": v.severity, "title": v.title, "cwe": v.cwe, "wasc": v.wasc, "confidence": v.confidence,
            "affected_url": v.affected_url, "parameter": v.parameter, "evidence": v.evidence,
            "description": _plain(v.description), "solution": _plain(v.solution),
            "references": " ".join(v.references or []),
        })
    return buf.getvalue()
