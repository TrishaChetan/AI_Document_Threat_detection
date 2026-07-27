from datetime import datetime, timezone

from ai.knowledge_base import KnowledgeBase
from ai.statistics import KnowledgeBaseStatistics
from reports.executive_summary import ExecutiveSummary
from reports.risk_calculator import RiskCalculator


class ReportBuilder:

    def __init__(self):
        self.kb = KnowledgeBase()
        self.stats = KnowledgeBaseStatistics(self.kb)

    def build(self, target, vulnerabilities):

        risk = RiskCalculator.calculate(vulnerabilities)
        summary = ExecutiveSummary.generate(risk)

        report = {
            "generated_at": datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S UTC"),
            "target": target,
            "risk": risk,
            "summary": summary,
            "statistics": self.stats.summary(),
            "vulnerabilities": [
                {
                    "title": vulnerability.title,
                    "severity": vulnerability.severity,
                    "priority": vulnerability.priority,
                    "summary": vulnerability.summary,
                    "business_impact": vulnerability.business_impact,
                    "technical_analysis": vulnerability.technical_analysis,
                    "remediation_steps": vulnerability.remediation_steps,
                }
                for vulnerability in vulnerabilities
            ],
        }

        return report