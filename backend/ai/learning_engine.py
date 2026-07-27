from ai.validator import RecommendationValidator


class LearningEngine:

    def __init__(self, kb):
        self.kb = kb

    def learn(self, title, recommendation):

        if not RecommendationValidator.validate(recommendation):
            print(f"[LEARN] Validation failed: {title}")
            return False

        if self.kb.exists(title):
            print(f"[LEARN] Already exists: {title}")
            return False

        try:
            self.kb.add(title, recommendation)
            print(f"[LEARN] Added to Knowledge Base: {title}")
            return True

        except Exception as e:
            print(f"[LEARN] Failed to save '{title}': {e}")
            return False