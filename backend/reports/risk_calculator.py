class RiskCalculator:

    WEIGHTS = {
        "Critical": 40,
        "High": 25,
        "Medium": 10,
        "Low": 3,
        "Informational": 0
    }

    @classmethod
    def calculate(cls, vulnerabilities):

        counts = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Informational": 0
        }

        score = 0

        for vulnerability in vulnerabilities:

            severity = vulnerability.priority

            if severity not in counts:
                continue

            counts[severity] += 1
            score += cls.WEIGHTS.get(severity, 0)

        return {
            "overall_score": min(score, 100),
            "counts": counts
        }