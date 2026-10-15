"""Google Gemini story generator."""
from google import genai

from .base import BaseStoryGenerator, GenerationError, is_retryable_error


class GeminiStoryGenerator(BaseStoryGenerator):
    provider_name = "gemini"
    default_model = "gemini-2.5-flash"

    def __init__(self, api_key, model=None):
        super().__init__(model)
        if not api_key:
            raise ValueError("Gemini API key is required.")
        self.client = genai.Client(api_key=api_key)

    def generate_text(self, prompt):
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
        except Exception as e:
            raise GenerationError(f"Gemini request failed: {e}", retryable=is_retryable_error(e)) from e

        if response.text is None:
            raise GenerationError("Gemini returned no text (possibly blocked by safety filters).")
        return response.text
