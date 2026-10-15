"""Configuration loading (TOML + environment)."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11
    import tomli as tomllib

from .providers.factory import PROVIDERS, create_generator

DEFAULT_CONFIG_FILE = "config.toml"

DEFAULTS = {
    "provider": "gemini",
    "models": {
        "gemini": "gemini-2.5-flash",
        "openai": "gpt-4o-mini",
        "openrouter": "openai/gpt-4o-mini",
    },
    "api_key_env": {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
    },
}


@dataclass
class Config:
    provider: str = DEFAULTS["provider"]
    model: Optional[str] = None
    api_key_env: str = field(default=DEFAULTS["api_key_env"]["gemini"])

    def resolved_model(self):
        return self.model or DEFAULTS["models"][self.provider]


def load_config(project_root=None, config_path=None, provider=None, model=None):
    """Load config from TOML with CLI overrides. Keys always come from env vars.

    Precedence: CLI flags > config.toml > built-in defaults.
    """
    load_dotenv()

    path = Path(config_path) if config_path else Path(project_root or ".") / DEFAULT_CONFIG_FILE
    data = {}
    if path.is_file():
        with open(path, "rb") as f:
            data = tomllib.load(f)

    provider = provider or data.get("provider", {}).get("name") or DEFAULTS["provider"]
    if provider not in PROVIDERS:
        raise ValueError(
            f"Unknown provider '{provider}'. Valid providers: {', '.join(PROVIDERS)}"
        )

    provider_section = data.get(provider, {})
    model = model or provider_section.get("model") or DEFAULTS["models"][provider]
    api_key_env = provider_section.get("api_key_env") or DEFAULTS["api_key_env"][provider]

    return Config(provider=provider, model=model, api_key_env=api_key_env)


def build_generator(config):
    """Create the story generator for a loaded Config, resolving the model default."""
    if config.model is None:
        config.model = config.resolved_model()
    return create_generator(config)
