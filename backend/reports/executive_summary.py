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

        return (
            f"The scan identified {total} security vulnerabilities.\n\n"
            f"Critical : {critical}\n"
            f"High : {high}\n"
            f"Medium : {medium}\n"
            f"Low : {low}\n\n"
            f"Overall Security Risk Score : {overall_score}/100\n\n"
            f"Immediate remediation is recommended for all Critical and High severity findings."
        )