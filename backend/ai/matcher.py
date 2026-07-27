import re


class VulnerabilityMatcher:

    @staticmethod
    def normalize(title: str) -> str:

        if not title:
            return ""

        title = title.lower().strip()

        title = re.sub(r"[^a-z0-9\s]", " ", title)
        title = re.sub(r"\s+", " ", title)

        return title

    @staticmethod
    def is_match(title1: str, title2: str) -> bool:
        return VulnerabilityMatcher.normalize(title1) == VulnerabilityMatcher.normalize(title2)