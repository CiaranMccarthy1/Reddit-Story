import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator.config import Config, load_config
from src.generator.providers import (
    GenerationError,
    GeminiStoryGenerator,
    OpenAIStoryGenerator,
    OpenRouterStoryGenerator,
    create_generator,
)
from src.generator.providers.base import BaseStoryGenerator

MOCK_SCRIPT = (
    "SECTION 1: STORY\nMocked story.\n"
    "SECTION 2: TIMESTAMPED SCRIPT\n00:00:00: \"test line.\""
)


# --- Gemini Provider ---

class TestGeminiProvider(unittest.TestCase):

    @patch('src.generator.providers.gemini.genai.Client')
    def test_generate_script_success(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.models.generate_content.return_value = MagicMock(text=MOCK_SCRIPT)

        generator = GeminiStoryGenerator(api_key='TEST_KEY', model='gemini-test')

        with patch('builtins.open', mock_open(read_data="Initial prompt content")):
            result = generator.generate_script("mock/story.txt", duration=45)

        MockClient.assert_called_once_with(api_key='TEST_KEY')

        call_args = mock_client.models.generate_content.call_args
        self.assertEqual(call_args.kwargs['model'], 'gemini-test')
        self.assertIn("45 seconds long", call_args.kwargs['contents'])
        self.assertIn("SECTION 1:", result)

    def test_init_requires_api_key(self):
        with self.assertRaises(ValueError):
            GeminiStoryGenerator(api_key=None)

    @patch('src.generator.providers.gemini.genai.Client')
    def test_empty_response_raises(self, MockClient):
        MockClient.return_value.models.generate_content.return_value = MagicMock(text=None)
        generator = GeminiStoryGenerator(api_key='TEST_KEY')

        with self.assertRaisesRegex(GenerationError, "no text"):
            generator.generate_text("prompt")

    @patch('src.generator.providers.gemini.genai.Client')
    def test_retries_on_retryable_error(self, MockClient):
        mock_client = MockClient.return_value
        rate_limit_error = Exception("429 rate limited")
        rate_limit_error.code = 429
        mock_client.models.generate_content.side_effect = [rate_limit_error, MagicMock(text=MOCK_SCRIPT)]
        generator = GeminiStoryGenerator(api_key='TEST_KEY')

        with patch('src.generator.providers.base.time.sleep'):
            result = generator._generate_with_retry("prompt")

        self.assertEqual(mock_client.models.generate_content.call_count, 2)
        self.assertIn("SECTION 1:", result)

    @patch('src.generator.providers.gemini.genai.Client')
    def test_fatal_error_not_retried(self, MockClient):
        mock_client = MockClient.return_value
        auth_error = Exception("401 unauthorized")
        auth_error.code = 401
        mock_client.models.generate_content.side_effect = auth_error
        generator = GeminiStoryGenerator(api_key='TEST_KEY')

        with patch('src.generator.providers.base.time.sleep') as mock_sleep:
            with self.assertRaises(GenerationError):
                generator._generate_with_retry("prompt")

        mock_sleep.assert_not_called()
        self.assertEqual(mock_client.models.generate_content.call_count, 1)


# --- OpenAI Provider ---

class TestOpenAIProvider(unittest.TestCase):

    @patch('src.generator.providers.openai_compat.OpenAI')
    def test_generate_script_success(self, MockOpenAI):
        mock_client = MockOpenAI.return_value
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=MOCK_SCRIPT))]
        )

        generator = OpenAIStoryGenerator(api_key='TEST_KEY', model='gpt-test')

        with patch('builtins.open', mock_open(read_data="Initial prompt content")):
            result = generator.generate_script("mock/story.txt", duration=30)

        MockOpenAI.assert_called_once_with(api_key='TEST_KEY', base_url=None)
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], 'gpt-test')
        self.assertIn("30 seconds long", call_args.kwargs['messages'][0]['content'])
        self.assertIn("SECTION 1:", result)

    def test_init_requires_api_key(self):
        with self.assertRaises(ValueError):
            OpenAIStoryGenerator(api_key='')

    @patch('src.generator.providers.openai_compat.OpenAI')
    def test_empty_choices_raises(self, MockOpenAI):
        MockOpenAI.return_value.chat.completions.create.return_value = MagicMock(choices=[])
        generator = OpenAIStoryGenerator(api_key='TEST_KEY')

        with self.assertRaisesRegex(GenerationError, "no text"):
            generator.generate_text("prompt")


# --- OpenRouter Provider ---

class TestOpenRouterProvider(unittest.TestCase):

    @patch('src.generator.providers.openai_compat.OpenAI')
    def test_uses_openrouter_base_url_and_headers(self, MockOpenAI):
        mock_client = MockOpenAI.return_value
        mock_client.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=MOCK_SCRIPT))]
        )

        generator = OpenRouterStoryGenerator(api_key='TEST_KEY', model='anthropic/claude')

        MockOpenAI.assert_called_once_with(
            api_key='TEST_KEY',
            base_url='https://openrouter.ai/api/v1',
        )

        result = generator.generate_text("prompt")
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], 'anthropic/claude')
        self.assertIn('HTTP-Referer', call_args.kwargs['extra_headers'])
        self.assertIn('X-Title', call_args.kwargs['extra_headers'])
        self.assertIn("SECTION 1:", result)

    def test_default_model(self):
        with patch('src.generator.providers.openai_compat.OpenAI'):
            generator = OpenRouterStoryGenerator(api_key='TEST_KEY')
        self.assertEqual(generator.model, 'openai/gpt-4o-mini')


# --- Base class behavior ---

class FlakyGenerator(BaseStoryGenerator):
    provider_name = "flaky"
    default_model = "flaky-1"

    def __init__(self, outcomes):
        super().__init__()
        self.outcomes = list(outcomes)

    def generate_text(self, prompt):
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class TestBaseGenerator(unittest.TestCase):

    def test_empty_response_raises(self):
        generator = FlakyGenerator([""])
        with self.assertRaisesRegex(GenerationError, "empty response"):
            generator._generate_with_retry("prompt")

    def test_whitespace_response_raises(self):
        generator = FlakyGenerator(["   \n  "])
        with self.assertRaisesRegex(GenerationError, "empty response"):
            generator._generate_with_retry("prompt")

    def test_retry_exhausted_raises(self):
        error = GenerationError("busy", retryable=True)
        generator = FlakyGenerator([error, GenerationError("busy", retryable=True), error])

        with patch('src.generator.providers.base.time.sleep'):
            with self.assertRaisesRegex(GenerationError, "busy"):
                generator._generate_with_retry("prompt")

    def test_generate_script_file_not_found(self):
        generator = FlakyGenerator(["ok"])
        with self.assertRaises(FileNotFoundError):
            generator.generate_script("nonexistent_file.txt")

    def test_generate_script_io_error(self):
        generator = FlakyGenerator(["ok"])
        with patch('builtins.open', side_effect=IOError("Disk error")):
            with self.assertRaises(IOError):
                generator.generate_script("broken.txt")


# --- Factory ---

class TestFactory(unittest.TestCase):

    def test_unknown_provider_raises(self):
        config = Config(provider="claude", model=None, api_key_env="X")
        with self.assertRaisesRegex(ValueError, "Unknown provider"):
            create_generator(config)

    def test_missing_api_key_raises(self):
        config = Config(provider="gemini", model=None, api_key_env="DEFINITELY_NOT_SET_KEY")
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(GenerationError, "DEFINITELY_NOT_SET_KEY"):
                create_generator(config)

    @patch('src.generator.providers.gemini.genai.Client')
    def test_creates_gemini_generator(self, MockClient):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'key'}):
            generator = create_generator(Config(provider="gemini", model="m1", api_key_env="GEMINI_API_KEY"))
        self.assertIsInstance(generator, GeminiStoryGenerator)
        self.assertEqual(generator.model, "m1")

    @patch('src.generator.providers.openai_compat.OpenAI')
    def test_creates_openai_generator(self, MockOpenAI):
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'key'}):
            generator = create_generator(Config(provider="openai", model="m1", api_key_env="OPENAI_API_KEY"))
        self.assertIsInstance(generator, OpenAIStoryGenerator)

    @patch('src.generator.providers.openai_compat.OpenAI')
    def test_creates_openrouter_generator(self, MockOpenAI):
        with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'key'}):
            generator = create_generator(Config(provider="openrouter", model="m1", api_key_env="OPENROUTER_API_KEY"))
        self.assertIsInstance(generator, OpenRouterStoryGenerator)


# --- Config loading ---

class TestLoadConfig(unittest.TestCase):

    def _write_config(self, content):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        path = Path(self.tmpdir.name) / "config.toml"
        path.write_text(content)
        return path

    def test_defaults_without_config_file(self):
        config = load_config(project_root=tempfile.gettempdir() + "/does-not-exist-config-dir")
        self.assertEqual(config.provider, "gemini")
        self.assertEqual(config.model, "gemini-2.5-flash")
        self.assertEqual(config.api_key_env, "GEMINI_API_KEY")

    def test_loads_provider_from_config_file(self):
        path = self._write_config('[provider]\nname = "openrouter"\n')
        config = load_config(config_path=path)
        self.assertEqual(config.provider, "openrouter")
        self.assertEqual(config.model, "openai/gpt-4o-mini")
        self.assertEqual(config.api_key_env, "OPENROUTER_API_KEY")

    def test_section_model_and_key_env_override(self):
        path = self._write_config(
            '[provider]\nname = "openai"\n'
            '[openai]\nmodel = "gpt-4o"\napi_key_env = "CUSTOM_KEY"\n'
        )
        config = load_config(config_path=path)
        self.assertEqual(config.model, "gpt-4o")
        self.assertEqual(config.api_key_env, "CUSTOM_KEY")

    def test_cli_flags_override_config_file(self):
        path = self._write_config('[provider]\nname = "gemini"\n')
        config = load_config(config_path=path, provider="openai", model="cli-model")
        self.assertEqual(config.provider, "openai")
        self.assertEqual(config.model, "cli-model")
        self.assertEqual(config.api_key_env, "OPENAI_API_KEY")

    def test_invalid_provider_in_config_raises(self):
        path = self._write_config('[provider]\nname = "bogus"\n')
        with self.assertRaisesRegex(ValueError, "Unknown provider"):
            load_config(config_path=path)


if __name__ == "__main__":
    unittest.main()
