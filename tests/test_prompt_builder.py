from schemas.vulnerability_schema import Vulnerability
from ai.prompt_builder import PromptBuilder

vulnerability = Vulnerability(
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

prompt = PromptBuilder.build(vulnerability)

print(prompt)