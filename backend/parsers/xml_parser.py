from pathlib import Path

from lxml import etree

from schemas.report_schema import ScanInfo, ScanReport, ScanSummary
from schemas.vulnerability_schema import Vulnerability


class XMLParser:

    def __init__(self, xml_path):
        self.xml_path = Path(xml_path)

    def parse(self):

        try:
            tree = etree.parse(str(self.xml_path))
            root = tree.getroot()

        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML file: {e}")

        # A ZAP report has one <site> per scanned host. Read all of them —
        # previously only the first was parsed and the rest were dropped.
        sites = root.findall("site")

        if not sites:
            raise ValueError("Invalid OWASP ZAP report: Missing <site> element.")

        if all(site.find("alerts") is None for site in sites):
            raise ValueError("Invalid OWASP ZAP report: Missing <alerts> element.")

        target = ", ".join(dict.fromkeys(site.get("name", "") for site in sites if site.get("name")))
        generated = root.get("generated", "")

        alerts = [alert for site in sites for alert in site.findall("alerts/alertitem")]

        vulnerabilities = []

        high = 0
        medium = 0
        low = 0
        informational = 0

        severity_map = {
            "3": "High",
            "2": "Medium",
            "1": "Low",
            "0": "Informational"
        }

        for alert in alerts:

            severity = severity_map.get(
                alert.findtext("riskcode", "0"),
                "Unknown"
            )

            if severity == "High":
                high += 1
            elif severity == "Medium":
                medium += 1
            elif severity == "Low":
                low += 1
            else:
                informational += 1

            instance = alert.find("instances/instance")

            references = []

            reference = alert.findtext("reference", "").strip()

            if reference:
                references.append(reference)

            vulnerabilities.append(
                Vulnerability(
                    title=alert.findtext("alert", ""),
                    severity=severity,
                    confidence=alert.findtext("confidencedesc", ""),
                    description=alert.findtext("desc", ""),
                    affected_url=instance.findtext("uri", "") if instance is not None else "",
                    parameter=instance.findtext("param", "") if instance is not None else "",
                    evidence=instance.findtext("evidence", "") if instance is not None else "",
                    solution=alert.findtext("solution", ""),
                    references=references,
                    cwe=alert.findtext("cweid", ""),
                    wasc=alert.findtext("wascid", "")
                )
            )

        summary = ScanSummary(
            total=len(vulnerabilities),
            high=high,
            medium=medium,
            low=low,
            informational=informational
        )

        scan_info = ScanInfo(
            scanner="OWASP ZAP",
            report_name=self.xml_path.name,
            target=target,
            generated_at=generated
        )

        return ScanReport(
            scan_info=scan_info,
            summary=summary,
            vulnerabilities=vulnerabilities
        )