import math


class BatchPlanner:

    def __init__(self, max_prompt_chars=12000, max_batches=8):
        self.max_prompt_chars = max(1, max_prompt_chars)
        self.max_batches = max(1, max_batches)

    def estimate_size(self, vulnerability):

        total = 0

        total += len(vulnerability.title or "")
        total += len(vulnerability.description or "")
        total += len(vulnerability.solution or "")

        if vulnerability.references:
            total += sum(len(reference) for reference in vulnerability.references)

        return total

    def create_batches(self, vulnerabilities):

        if not vulnerabilities:
            return []

        total = len(vulnerabilities)

        sizes = [self.estimate_size(v) for v in vulnerabilities]
        total_size = sum(sizes)

        prompt_batches = math.ceil(total_size / self.max_prompt_chars)

        if total <= 10:
            vuln_batches = 2
        elif total <= 25:
            vuln_batches = 4
        elif total <= 50:
            vuln_batches = 6
        elif total <= 100:
            vuln_batches = 8
        else:
            vuln_batches = 10

        required_batches = max(prompt_batches, vuln_batches)
        required_batches = min(required_batches, self.max_batches)
        required_batches = max(1, required_batches)

        batch_size = math.ceil(total / required_batches)

        return [
            vulnerabilities[i:i + batch_size]
            for i in range(0, total, batch_size)
        ]