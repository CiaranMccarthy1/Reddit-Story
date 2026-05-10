

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
    @patch('src.generator.content_fetcher.genai.Client')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="Initial prompt content")
    def test_01_generate_script_success(self, MockOpen, MockClient, MockGetenv):
    
        mock_client_instance = MockClient.return_value
        mock_client_instance.models.generate_content.return_value = MOCK_GEMINI_RESPONSE
    
        fetcher = ContentFetcher()
    
        MOCK_FILE_PATH = "mock/story.txt"
        result = fetcher.generate_script(filePath=MOCK_FILE_PATH, duration=45) 
        
        # Verify file was opened
        MockOpen.assert_called_with(MOCK_FILE_PATH, 'r') 

        # Assertions
        MockClient.assert_called_once_with(api_key='TEST_API_KEY')
        
        # Verify generate_content called with prompt containing duration
        call_args = mock_client_instance.models.generate_content.call_args
        self.assertIsNotNone(call_args, "generate_content should be called")
        prompt_text = call_args.kwargs.get('contents') if call_args.kwargs else call_args[1].get('contents', call_args[0][0] if not call_args.kwargs and call_args[0] else call_args.kwargs.get('contents'))
        if not prompt_text and call_args.kwargs and 'contents' in call_args.kwargs: prompt_text = call_args.kwargs['contents']
        elif not prompt_text and call_args[1] and 'contents' in call_args[1]: prompt_text = call_args[1]['contents']
        elif not prompt_text and len(call_args[0]) > 0: prompt_text = call_args[0][0] # Fallback just in case
        elif not prompt_text and call_args.kwargs: prompt_text = call_args.kwargs.get('contents', "")

        # A cleaner way:
        prompt_text = call_args.kwargs.get('contents') if call_args.kwargs and 'contents' in call_args.kwargs else call_args[0][1] if len(call_args[0]) > 1 else call_args.kwargs.get('contents') if call_args.kwargs else call_args[1].get('contents') if call_args[1] else call_args[0][0] if len(call_args[0])>0 else ""

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
        
        # We need to mock env for init to pass
        with patch('src.generator.content_fetcher.os.getenv', return_value='KEY'), \
             patch('src.generator.content_fetcher.genai.Client'):
             
             fetcher = ContentFetcher()
             
             with self.assertRaises(FileNotFoundError):
                 fetcher.generate_script("non_existent_file.txt")

    def test_04_get_prompt_io_error(self):
        with patch('src.generator.content_fetcher.os.getenv', return_value='KEY'), \
             patch('src.generator.content_fetcher.genai.Client'), \
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

    @patch('src.generator.audio_generator.concatenate_audioclips')
    @patch('src.generator.audio_generator.AudioFileClip')
    @patch('src.generator.audio_generator.edge_tts.Communicate')
    def test_01_generate_narration_calls_edge_tts_correctly(self, MockCommunicate, MockAudioFileClip, MockConcat):
        # Setup mock communicate
        mock_instance = MockCommunicate.return_value
        mock_instance.save = unittest.mock.AsyncMock()

        # Setup mock audio clip
        mock_clip = MagicMock()
        mock_clip.duration = 2.0
        MockAudioFileClip.return_value = mock_clip

        # Setup mock concat
        mock_final_audio = MagicMock()
        MockConcat.return_value = mock_final_audio
        
        self.generator.generate_narration(self.script_data, self.output_path)

        # Assertions
        # Check if Communicate was instantiated for each line
        self.assertEqual(MockCommunicate.call_count, 2)
        MockCommunicate.assert_any_call("First sentence.", "en-US-ChristopherNeural", rate="-10%")
        MockCommunicate.assert_any_call("Second sentence.", "en-US-ChristopherNeural", rate="-10%")
        
        # Check if final audio was saved
        mock_final_audio.write_audiofile.assert_called_once_with(self.output_path, logger=None)

        # Verify timestamps were updated correctly
        self.assertEqual(self.script_data[0]['start'], 0.0)
        self.assertEqual(self.script_data[1]['start'], 2.0)