import json

from ai.knowledge_base import KnowledgeBase
from ai.learning_engine import LearningEngine
from ai.llm_service import LLMService
from ai.prompt_builder import PromptBuilder
from schemas.ai_response_schema import AIRecommendation


class RecommendationEngine:

    def __init__(self):

        self.kb = KnowledgeBase()
        self.llm = LLMService()
        self.learning_engine = LearningEngine(self.kb)

    def analyze(self, vulnerability):

        recommendation = self.kb.find(vulnerability.title)

        if recommendation:
            print(f"[KB] {vulnerability.title}")
            return recommendation

        print(f"[LLM] {vulnerability.title}")

        prompt = PromptBuilder.build(vulnerability)

        response = self.llm.generate(prompt)

        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON received from LLM: {e}")

        priority_mapping = {
            "CRITICAL": "Critical",
            "HIGH": "High",
            "MEDIUM": "Medium",
            "LOW": "Low",
            "INFORMATIONAL": "Informational",
            "INFO": "Informational",
        }

        if "priority" in data and isinstance(data["priority"], str):
            normalized = data["priority"].strip().upper()
            data["priority"] = priority_mapping.get(
                normalized,
                data["priority"].strip().capitalize(),
            )

        try:
            recommendation = AIRecommendation(**data)
        except Exception as e:
            raise RuntimeError(f"Invalid AI recommendation format: {e}")

        try:
            self.learning_engine.learn(
                vulnerability.title,
                recommendation
            )
        except Exception as e:
            print(f"[KB] Failed to learn '{vulnerability.title}': {e}")

        return recommendation