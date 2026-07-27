from ai.llm_service import LLMService

llm = LLMService()

response = llm.generate(
    "Explain SQL Injection in 5 concise bullet points."
)

print(response)