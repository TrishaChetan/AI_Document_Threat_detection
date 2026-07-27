import os

from dotenv import load_dotenv
from openai import OpenAI

from ai.retry import RetryExecutor

load_dotenv()


class LLMService:

    def __init__(self):

        api_key = os.getenv("NVIDIA_API_KEY")
        base_url = os.getenv("NVIDIA_BASE_URL")
        model = os.getenv("NVIDIA_MODEL")

        if not api_key:
            raise ValueError("NVIDIA_API_KEY is not configured.")

        if not base_url:
            raise ValueError("NVIDIA_BASE_URL is not configured.")

        if not model:
            raise ValueError("NVIDIA_MODEL is not configured.")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=60
        )

        self.model = model
        self.retry = RetryExecutor()

    def generate(self, prompt):

        def request():

            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior cybersecurity consultant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1200
            )

            if not response.choices:
                raise RuntimeError("LLM returned no response.")

            content = response.choices[0].message.content

            if not content:
                raise RuntimeError("LLM returned an empty response.")

            return content

        return self.retry.run(request)