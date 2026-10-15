"""
LLM story generation providers.

Each provider implements generate_text(); the shared generate_script()
workflow (prompt loading, duration instruction, retry, empty-response
guard) lives in BaseStoryGenerator.
"""
import time
from abc import ABC, abstractmethod


class GenerationError(Exception):
    """Raised when story generation fails. Retryable errors are retried by the base class."""

    def __init__(self, message, retryable=False):
        super().__init__(message)
        self.retryable = retryable


def is_retryable_error(exc):
    """Best-effort classification of transient API errors across SDKs."""
    status = getattr(exc, "code", None)
    if not isinstance(status, int):
        status = getattr(exc, "status_code", None)
    if isinstance(status, int) and status in (408, 429, 500, 502, 503, 504):
        return True
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return True
    name = type(exc).__name__
    return name in ("APIConnectionError", "APITimeoutError", "ConnectError", "ReadTimeout")


class BaseStoryGenerator(ABC):
    provider_name = "base"
    default_model = None

    def __init__(self, model=None):
        self.model = model or self.default_model

    @abstractmethod
    def generate_text(self, prompt):
        """Send a prompt to the provider and return the raw response text."""

    def _get_prompt(self, file_path):
        try:
            with open(file_path, "r") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"The file '{file_path}' was not found.")
        except IOError as e:
            raise IOError(f"An error occurred while reading the file '{file_path}': {e}")

    def generate_script(self, filePath, duration=60):
        """Fetches the story + timestamped script from the provider."""
        base_prompt = self._get_prompt(filePath)
        duration_instruction = f"\nPlease ensure the generated script is approximately {duration} seconds long when narrated."
        final_prompt = base_prompt + duration_instruction

        print(f"Fetching story from {self.provider_name} [{self.model}] (Target Duration: {duration}s)...")

        return self._generate_with_retry(final_prompt)

    def _generate_with_retry(self, prompt, attempts=3):
        last_error = None
        for attempt in range(1, attempts + 1):
            try:
                text = self.generate_text(prompt)
            except GenerationError as e:
                if not e.retryable or attempt == attempts:
                    raise
                last_error = e
                wait = 2 ** (attempt - 1)
                print(f"Generation attempt {attempt}/{attempts} failed ({e}); retrying in {wait}s...")
                time.sleep(wait)
            else:
                if not text or not text.strip():
                    raise GenerationError(
                        f"{self.provider_name} returned an empty response "
                        "(possibly blocked by safety filters)."
                    )
                return text.strip()
        raise last_error
