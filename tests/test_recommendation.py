from schemas.vulnerability_schema import Vulnerability
from ai.recommendation_engine import RecommendationEngine

v = Vulnerability(
    title="Content Security Policy Header Not Set",
    severity="Medium",
    confidence="High",
    description="The application does not define a Content Security Policy.",
    affected_url="http://localhost:8082",
    parameter="",
    evidence="",
    solution="Configure CSP",
    references=[],
    cwe="693",
    wasc="15"
)

engine = RecommendationEngine()

from ai.prompt_builder import PromptBuilder
from ai.llm_service import LLMService

prompt = PromptBuilder.build(v)

llm = LLMService()

response = llm.generate(prompt)

print(response)