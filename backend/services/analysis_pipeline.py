from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from ai.recommendation_engine import RecommendationEngine
from database.scan_repository import scan_repository
from parsers.xml_parser import XMLParser
from reports.pdf_generator import PDFGenerator
from reports.report_builder import ReportBuilder
from schemas.enhanced_vulnerability import EnhancedVulnerability


class AnalysisPipeline:

    def __init__(self):
        self.ai_engine = RecommendationEngine()
        self.report_builder = ReportBuilder()

    def run(self, file_path: Path):

        parser = XMLParser(str(file_path))
        scan = parser.parse()

        ai_results = []
        enhanced_vulnerabilities = []

        for vulnerability in scan.vulnerabilities:

            recommendation = self.ai_engine.analyze(vulnerability)

            enhanced = EnhancedVulnerability(
                title=vulnerability.title,
                severity=vulnerability.severity,
                priority=recommendation.priority,
                summary=recommendation.summary,
                business_impact=recommendation.business_impact,
                technical_analysis=recommendation.technical_analysis,
                remediation_steps=recommendation.remediation_steps,
            )

            enhanced_vulnerabilities.append(enhanced)

            ai_results.append(
                {
                    "title": vulnerability.title,
                    "severity": vulnerability.severity,
                    "recommendation": recommendation.model_dump(),
                }
            )

        report = self.report_builder.build(
            scan.scan_info.target,
            enhanced_vulnerabilities,
        )

        scan_id = f"GX-{uuid4().hex[:8].upper()}"

        pdf_generator = PDFGenerator(f"{scan_id}.pdf")
        pdf_path = pdf_generator.generate(report)

        pdf_filename = Path(pdf_path).name

        summary = (
            scan.summary.model_dump()
            if hasattr(scan.summary, "model_dump")
            else scan.summary
        )

        scan_document = {
            "scan_id": scan_id,
            "target": scan.scan_info.target,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "risk_score": report["risk"]["overall_score"],
            "status": "Completed",
            "summary": summary,
            "pdf_report": {
                "filename": pdf_filename,
                "download_url": f"/api/v1/report/{pdf_filename}",
            },
        }

        scan_repository.create(scan_document)

        return {
            "success": True,
            "status": "completed",
            "scan_id": scan_id,
            "summary": summary,
            "scan": scan.model_dump(),
            "ai_recommendations": ai_results,
            "pdf_report": {
                "filename": pdf_filename,
                "download_url": f"/api/v1/report/{pdf_filename}",
            },
        }