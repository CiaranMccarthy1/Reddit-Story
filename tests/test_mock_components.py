

import unittest
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Configure sys.path to allow imports from src/generator
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator.audio_generator import AudioGenerator

# --- AudioGenerator Tests (edge-tts interaction) ---

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
