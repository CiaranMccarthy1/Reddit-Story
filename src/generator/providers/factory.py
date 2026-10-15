"""Provider factory: builds a story generator from config."""
import os

from .base import BaseStoryGenerator, GenerationError
from .gemini import GeminiStoryGenerator
from .openai_compat import OpenAIStoryGenerator, OpenRouterStoryGenerator

PROVIDERS = ("gemini", "openai", "openrouter")


def create_generator(config):
    """Build a story generator from a loaded Config.

    ``config`` is a src.generator.config.Config instance (or any object
    with .provider, .model, and .api_key_env attributes).
    """
    if config.provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider '{config.provider}'. Valid providers: {', '.join(PROVIDERS)}"
        )

    api_key = os.getenv(config.api_key_env)
    if not api_key:
        raise GenerationError(
            f"{config.provider} selected but {config.api_key_env} is not set. "
            f"Add it to your .env file (see .env.template)."
        )

    if config.provider == "gemini":
        return GeminiStoryGenerator(api_key=api_key, model=config.model)
    if config.provider == "openai":
        return OpenAIStoryGenerator(api_key=api_key, model=config.model)
    return OpenRouterStoryGenerator(api_key=api_key, model=config.model)
