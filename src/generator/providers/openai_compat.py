"""OpenAI-compatible story generators (OpenAI and OpenRouter)."""
from openai import OpenAI

from .base import BaseStoryGenerator, GenerationError, is_retryable_error


class OpenAICompatStoryGenerator(BaseStoryGenerator):
    provider_name = "openai-compatible"
    default_model = "gpt-4o-mini"
    base_url = None
    extra_headers = None

    def __init__(self, api_key, model=None):
        super().__init__(model)
        if not api_key:
            raise ValueError(f"{self.provider_name} API key is required.")
        self.client = OpenAI(api_key=api_key, base_url=self.base_url)

    def generate_text(self, prompt):
        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if self.extra_headers:
            kwargs["extra_headers"] = self.extra_headers

        try:
            response = self.client.chat.completions.create(**kwargs)
        except Exception as e:
            raise GenerationError(
                f"{self.provider_name} request failed: {e}", retryable=is_retryable_error(e)
            ) from e

        text = response.choices[0].message.content if response.choices else None
        if text is None:
            raise GenerationError(f"{self.provider_name} returned no text in the response.")
        return text


class OpenAIStoryGenerator(OpenAICompatStoryGenerator):
    provider_name = "openai"
    default_model = "gpt-4o-mini"


class OpenRouterStoryGenerator(OpenAICompatStoryGenerator):
    provider_name = "openrouter"
    default_model = "openai/gpt-4o-mini"
    base_url = "https://openrouter.ai/api/v1"
    extra_headers = {
        "HTTP-Referer": "https://github.com/CiaranMccarthy1/reddit_story",
        "X-Title": "Reddit Story Generator",
    }
