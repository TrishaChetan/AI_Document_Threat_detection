from collections import Counter


class KnowledgeBaseStatistics:

    def __init__(self, kb):
        self.kb = kb

    def total_entries(self):
        return len(self.kb.database)

    def static_entries(self):
        count = 0

        for entry in self.kb.database.values():
            if entry.get("metadata", {}).get("source") == "static":
                count += 1

        return count

    def learned_entries(self):
        count = 0

        for entry in self.kb.database.values():
            if entry.get("metadata", {}).get("source") == "llm":
                count += 1

        return count

    def total_hits(self):
        hits = 0

        for entry in self.kb.database.values():
            hits += entry.get("metadata", {}).get("hits", 0)

        return hits

    def average_hits(self):
        entries = self.total_entries()

        if entries == 0:
            return 0

        return round(self.total_hits() / entries, 2)

    def most_used(self):
        if not self.kb.database:
            return None

        title, entry = max(
            self.kb.database.items(),
            key=lambda item: item[1].get("metadata", {}).get("hits", 0)
        )

        return {
            "title": title,
            "hits": entry.get("metadata", {}).get("hits", 0)
        }

    def least_used(self):
        if not self.kb.database:
            return None

        title, entry = min(
            self.kb.database.items(),
            key=lambda item: item[1].get("metadata", {}).get("hits", 0)
        )

        return {
            "title": title,
            "hits": entry.get("metadata", {}).get("hits", 0)
        }

    def source_breakdown(self):
        counter = Counter()

        for entry in self.kb.database.values():
            source = entry.get("metadata", {}).get("source", "unknown")
            counter[source] += 1

        return dict(counter)

    def summary(self):
        return {
            "total_entries": self.total_entries(),
            "static_entries": self.static_entries(),
            "learned_entries": self.learned_entries(),
            "total_hits": self.total_hits(),
            "average_hits": self.average_hits(),
            "most_used": self.most_used(),
            "least_used": self.least_used(),
            "source_breakdown": self.source_breakdown()
        }