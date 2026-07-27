import json
from pathlib import Path
from datetime import datetime, timezone

from ai.matcher import VulnerabilityMatcher
from schemas.ai_response_schema import AIRecommendation


class KnowledgeBase:

    def __init__(self):

        self.db_path = Path(__file__).parent.parent / "data" / "vulnerability_db.json"

        self.load()

    def load(self):

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.db_path.exists():
            self.database = {}
            self.save()
            return

        with open(self.db_path, "r", encoding="utf-8") as f:
            self.database = json.load(f)

    def save(self):

        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.database, f, indent=4)

    def find(self, title):

        key = VulnerabilityMatcher.normalize(title)

        if key not in self.database:
            return None

        self.increment_hit(key)

        return AIRecommendation(**self.database[key]["recommendation"])

    def exists(self, title):

        key = VulnerabilityMatcher.normalize(title)

        return key in self.database

    def add(self, title, recommendation, source="llm"):

        key = VulnerabilityMatcher.normalize(title)

        now = datetime.now(timezone.utc).isoformat()

        self.database[key] = {
            "recommendation": recommendation.model_dump(),
            "metadata": {
                "source": source,
                "hits": 1,
                "created_at": now,
                "last_seen": now
            }
        }

        self.save()

    def increment_hit(self, key):

        if key not in self.database:
            return

        metadata = self.database[key]["metadata"]

        metadata["hits"] += 1
        metadata["last_seen"] = datetime.now(timezone.utc).isoformat()

        self.save()

    def get_metadata(self, title):

        key = VulnerabilityMatcher.normalize(title)

        return self.database.get(key, {}).get("metadata")

    def reload(self):

        self.load()