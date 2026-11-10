import math


class RiskCalculator:
    """Turns a list of findings into a 0-100 risk score and a rating.

    The old formula summed weights and clipped at 100, so a scan with 4 High
    findings scored the same 100/100 as one with 40 — every real-world scan
    saturated and scores stopped being comparable. Now:

    * The single worst finding sets a floor (one Critical is always >= 85).
    * Additional findings add risk with diminishing returns
      (100 * (1 - e^(-points / SCALE))), so the score keeps moving between
      "a few issues" and "a lot of issues" without ever exceeding 100.
    """

    WEIGHTS = {
        "Critical": 40,
        "High": 25,
        "Medium": 10,
        "Low": 3,
        "Informational": 0
    }

    # Minimum score implied by the most severe finding present
    FLOORS = {
        "Critical": 85,
        "High": 50,
        "Medium": 25,
        "Low": 5,
        "Informational": 0
    }

    # Points at which the curve reaches ~63/100
    SCALE = 100

    RATINGS = [
        (85, "Critical"),
        (50, "High"),
        (25, "Medium"),
        (1, "Low"),
        (0, "None"),
    ]

    @classmethod
    def rating_for(cls, score):
        for threshold, label in cls.RATINGS:
            if score >= threshold:
                return label
        return "None"

    @classmethod
    def calculate(cls, vulnerabilities):

        counts = {
            "Critical": 0,
            "High": 0,
            "Medium": 0,
            "Low": 0,
            "Informational": 0
        }

        points = 0

        for vulnerability in vulnerabilities:

            severity = vulnerability.priority

            if severity not in counts:
                continue

            counts[severity] += 1
            points += cls.WEIGHTS.get(severity, 0)

        curve = 100 * (1 - math.exp(-points / cls.SCALE))
        floor = max((cls.FLOORS[s] for s, n in counts.items() if n), default=0)
        score = round(max(curve, floor))

        return {
            "overall_score": min(score, 100),
            "rating": cls.rating_for(score),
            "counts": counts
        }
