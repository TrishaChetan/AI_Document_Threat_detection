class ExecutiveSummary:

    @staticmethod
    def generate(risk):

        counts = risk.get("counts", {})

        critical = counts.get("Critical", 0)
        high = counts.get("High", 0)
        medium = counts.get("Medium", 0)
        low = counts.get("Low", 0)

        total = critical + high + medium + low

        overall_score = risk.get("overall_score", 0)
        rating = risk.get("rating")

        if critical or high:
            advice = "Immediate remediation is recommended for all Critical and High severity findings."
        elif medium:
            advice = "No Critical or High findings. Plan fixes for the Medium severity issues in the next release."
        elif low:
            advice = "Only Low severity findings were identified. Address them as part of routine hardening."
        else:
            advice = "No actionable vulnerabilities were identified in this scan."

        rating_text = f" ({rating} risk)" if rating else ""

        return (
            f"The scan identified {total} security vulnerabilit{'y' if total == 1 else 'ies'}.\n\n"
            f"Critical : {critical}\n"
            f"High : {high}\n"
            f"Medium : {medium}\n"
            f"Low : {low}\n\n"
            f"Overall Security Risk Score : {overall_score}/100{rating_text}\n\n"
            f"{advice}"
        )