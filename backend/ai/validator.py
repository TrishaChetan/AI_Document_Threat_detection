from schemas.ai_response_schema import AIRecommendation


class RecommendationValidator:

    VALID_PRIORITIES = {
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL"
    }

    @staticmethod
    def validate(rec: AIRecommendation) -> bool:

        if rec is None:
            return False

        if not rec.summary.strip():
            return False

        if not rec.business_impact.strip():
            return False

        if not rec.technical_analysis.strip():
            return False

        if not rec.remediation_steps:
            return False

        if len(rec.remediation_steps) < 3:
            return False

        if not all(step.strip() for step in rec.remediation_steps):
            return False

        if rec.priority.strip().upper() not in RecommendationValidator.VALID_PRIORITIES:
            return False

        return True