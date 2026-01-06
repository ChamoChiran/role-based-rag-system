from typing import Optional
import os
from google import genai

class LLMClient:
    """
    Generic LLM Client wrapper.
    """
    def __init__(self, model: str, api_key: Optional[str] = None):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def __call__(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text.strip()
