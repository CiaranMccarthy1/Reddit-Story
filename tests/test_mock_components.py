

import unittest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Configure sys.path to allow imports from src/generator
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator.content_fetcher import ContentFetcher
from src.generator.audio_generator import AudioGenerator

# --- Mock Data ---
MOCK_GEMINI_RESPONSE = MagicMock()
MOCK_GEMINI_RESPONSE.text = "SECTION 1: STORY\nMocked story.\nSECTION 2: TIMESTAMPED SCRIPT\n00:00:00: \"test line.\""

# --- ContentFetcher Tests (API interaction) ---

class TestContentFetcher(unittest.TestCase):
    
    @patch('src.generator.content_fetcher.os.getenv', return_value='TEST_API_KEY')
    @patch('src.generator.content_fetcher.genai.configure')
    @patch('src.generator.content_fetcher.genai.GenerativeModel')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="Initial prompt content")
    def test_01_generate_script_success(self, MockOpen, MockGenerativeModel, MockConfigure, MockGetenv):
    
        mock_model_instance = MockGenerativeModel.return_value
        mock_model_instance.generate_content.return_value = MOCK_GEMINI_RESPONSE
    
        fetcher = ContentFetcher()
    
        MOCK_FILE_PATH = "mock/story.txt"
        result = fetcher.generate_script(filePath=MOCK_FILE_PATH, duration=45) 
        
        # Verify file was opened
        MockOpen.assert_called_with(MOCK_FILE_PATH, 'r') 

        # Assertions
        MockConfigure.assert_called_once_with(api_key='TEST_API_KEY')
        
        # Verify generate_content called with prompt containing duration
        call_args = mock_model_instance.generate_content.call_args
        self.assertIsNotNone(call_args, "generate_content should be called")
        prompt_text = call_args[0][0]
        self.assertIn("45 seconds long", prompt_text)
        
        self.assertIn("SECTION 1:", result)

    @patch('src.generator.content_fetcher.os.getenv', return_value=None)
    def test_02_init_raises_error_no_api_key(self, MockGetenv):
        with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY not found"):
            ContentFetcher()

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_03_get_prompt_file_not_found(self, MockOpen):
        # Note: We can't easily mock open to raise generic FileNotFoundError globally without side effects, 
        # so we rely on the method executing the try/except block.
        # However, _get_prompt is internal. We can access it via generate_script.
        # But generate_script calls _get_prompt.
        
        fetcher = ContentFetcher() # Needs API key mock setup which is in class decorator? No, it's not. 
        # We need to mock env for init to pass
        with patch('src.generator.content_fetcher.os.getenv', return_value='KEY'), \
             patch('src.generator.content_fetcher.genai.configure'), \
             patch('src.generator.content_fetcher.genai.GenerativeModel'):
             
             fetcher = ContentFetcher()
             
             with self.assertRaises(FileNotFoundError):
                 fetcher.generate_script("non_existent_file.txt")

    def test_04_get_prompt_io_error(self):
        with patch('src.generator.content_fetcher.os.getenv', return_value='KEY'), \
             patch('src.generator.content_fetcher.genai.configure'), \
             patch('src.generator.content_fetcher.genai.GenerativeModel'), \
             patch('builtins.open', side_effect=IOError("Disk error")):
             
             fetcher = ContentFetcher()
             with self.assertRaises(IOError):
                 fetcher.generate_script("exist.txt")

# --- AudioGenerator Tests (gTTS interaction) ---

class TestAudioGenerator(unittest.TestCase):
    
    def setUp(self):
        self.generator = AudioGenerator()
        self.script_data = [
            {'start': 0, 'text': "First sentence."},
            {'start': 5, 'text': "Second sentence."}
        ]
        self.output_path = "temp/narration.mp3"

    @patch('src.generator.audio_generator.edge_tts.Communicate')
    def test_01_generate_narration_calls_edge_tts_correctly(self, MockCommunicate):
        # Setup mock instance
        mock_instance = MockCommunicate.return_value
        mock_instance.save = unittest.mock.AsyncMock()
        
        self.generator.generate_narration(self.script_data, self.output_path)

        # Expected full text: concatenated strings
        expected_text = "First sentence. Second sentence."

        # Assertions
        # 1. Check if Communicate was instantiated with the correct text and voice
        MockCommunicate.assert_called_with(expected_text, "en-US-ChristopherNeural", rate="-10%")
        
        # 2. Check if the save method was called with the correct path
        mock_instance.save.assert_called_once_with(self.output_path)