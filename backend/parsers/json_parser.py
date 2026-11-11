"""Parser for OWASP ZAP's JSON report ("Traditional JSON Report").

Produced by `zap-baseline.py -J report.json`, `zap-full-scan.py -J ...`, the
ZAP GitHub Actions and Report -> Generate Report -> JSON in the desktop app.
Returns the same ScanReport as XMLParser, so the rest of the pipeline is
unchanged.

Unlike the XML parser, findings from every scanned site are included.
"""
import json
from pathlib import Path

from schemas.report_schema import ScanInfo, ScanReport, ScanSummary
from schemas.vulnerability_schema import Vulnerability

SEVERITY_MAP = {
    "3": "High",
    "2": "Medium",
    "1": "Low",
    "0": "Informational"
}

CONFIDENCE_MAP = {
    "4": "Confirmed",
    "3": "High",
    "2": "Medium",
    "1": "Low",
    "0": "False Positive"
}


def _text(value) -> str:
    return "" if value is None else str(value).strip()


class JSONParser:

    def __init__(self, json_path):
        self.json_path = Path(json_path)

    def parse(self):

        try:
            data = json.loads(self.json_path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"Invalid JSON file: {e}")

        if not isinstance(data, dict) or "site" not in data:
            raise ValueError("Invalid OWASP ZAP JSON report: Missing 'site'.")

        sites = data["site"]
        if isinstance(sites, dict):
            sites = [sites]

        vulnerabilities = []
        counts = {"High": 0, "Medium": 0, "Low": 0, "Informational": 0}

        for site in sites:
            for alert in site.get("alerts", []) or []:

                severity = SEVERITY_MAP.get(_text(alert.get("riskcode", "0")), "Informational")
                counts[severity] += 1

                instances = alert.get("instances") or [{}]
                instance = instances[0]

                reference = _text(alert.get("reference"))
                confidence = CONFIDENCE_MAP.get(_text(alert.get("confidence")), "")
                if not confidence:
                    # e.g. "High (Medium)" -> "Medium"
                    riskdesc = _text(alert.get("riskdesc"))
                    confidence = riskdesc.split("(")[-1].rstrip(")") if "(" in riskdesc else ""

                vulnerabilities.append(
                    Vulnerability(
                        title=_text(alert.get("alert") or alert.get("name")),
                        severity=severity,
                        confidence=confidence,
                        description=_text(alert.get("desc")),
                        affected_url=_text(instance.get("uri")),
                        parameter=_text(instance.get("param")),
                        evidence=_text(instance.get("evidence")),
                        solution=_text(alert.get("solution")),
                        references=[reference] if reference else [],
                        cwe=_text(alert.get("cweid")),
                        wasc=_text(alert.get("wascid"))
                    )
                )

        if not vulnerabilities and not sites:
            raise ValueError("Invalid OWASP ZAP JSON report: no sites found.")

        summary = ScanSummary(
            total=len(vulnerabilities),
            high=counts["High"],
            medium=counts["Medium"],
            low=counts["Low"],
            informational=counts["Informational"]
        )

        targets = list(dict.fromkeys(_text(s.get("@name")) for s in sites if s.get("@name")))

        scan_info = ScanInfo(
            scanner="OWASP ZAP",
            report_name=self.json_path.name,
            target=", ".join(targets),
            generated_at=_text(data.get("@generated"))
        )

        return ScanReport(
            scan_info=scan_info,
            summary=summary,
            vulnerabilities=vulnerabilities
        )
