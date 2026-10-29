from google import genai
from google.genai import types

from src.config import GEMINI_API_KEY, GEMINI_MODEL


class GeminiClient:
    """Client for generating text with Gemini."""

    def __init__(self) -> None:
        self.client = genai.Client(
            api_key=GEMINI_API_KEY,
            http_options=types.HttpOptions(
                timeout=30_000
            ),
        )
        self.model = GEMINI_MODEL

    def generate(self, prompt: str) -> str:
        """Send a prompt to Gemini and return the generated text."""

        if not prompt or not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned no text response.")

        return response.text.strip()