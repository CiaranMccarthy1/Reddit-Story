
import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Fix import path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator.video_generator import VideoGenerator

class TestVideoGenerator(unittest.TestCase):
    def setUp(self):
        self.mock_assets_manager = MagicMock()
        self.video_gen = VideoGenerator(self.mock_assets_manager)
        
        self.mock_bg_path = "mock_bg.mp4"
        self.mock_audio_path = "mock_audio.mp3"
        self.mock_output_path = "output.mp4"
        self.mock_script_data = [
            {'start': 0, 'text': "Hello"},
            {'start': 2, 'text': "World"}
        ]

    @patch('src.generator.video_generator.VideoFileClip')
    @patch('src.generator.video_generator.AudioFileClip')
    @patch('src.generator.video_generator.ImageClip')
    @patch('src.generator.video_generator.create_text_image')
    @patch('src.generator.video_generator.CompositeVideoClip')
    def test_create_video_flow(self, MockComposite, MockCreateTextImage, MockImageClip, MockAudioClip, MockVideoClip):
        # --- Setup Mocks ---
        
        # Audio Mock
        mock_audio = MockAudioClip.return_value
        mock_audio.duration = 10
        
        # Background Video Mock
        mock_bg = MockVideoClip.return_value
        mock_bg.w = 1920
        mock_bg.h = 1080
        mock_bg.duration = 5 # Shorter than audio to test looping
        
        # Mocking chainable methods (crop, loop, set_audio, subclip)
        mock_bg.crop.return_value = mock_bg
        mock_bg.loop.return_value = mock_bg
        mock_bg.set_audio.return_value = mock_bg
        mock_bg.subclip.return_value = mock_bg
        
        # TextClip Mock
        mock_text_clip_instance = MockImageClip.return_value
        mock_text_clip_instance.set_position.return_value = mock_text_clip_instance
        mock_text_clip_instance.set_start.return_value = mock_text_clip_instance
        mock_text_clip_instance.set_end.return_value = mock_text_clip_instance
        mock_text_clip_instance.set_duration.return_value = mock_text_clip_instance

        # Composite Video Mock
        mock_final_video = MockComposite.return_value

        # --- Execution ---
        self.video_gen.create_video(
            self.mock_bg_path, 
            self.mock_audio_path, 
            self.mock_script_data, 
            self.mock_output_path
        )

        # --- Assertions ---
        
        # 1. Inputs loaded?
        MockAudioClip.assert_called_with(self.mock_audio_path)
        MockVideoClip.assert_called_with(self.mock_bg_path)
        
        # 2. Logic checks inside create_video
        # It calculates target width based on 9:16 aspect ratio (h * 9/16)
        # It calls crop
        mock_bg.crop.assert_called_once()
        
        # It should loop because bg duration (5) < audio duration (10)
        mock_bg.loop.assert_called_with(duration=10)
        
        # It should set audio
        mock_bg.set_audio.assert_called_with(mock_audio)
        
        # 3. TextClips created?
        # Check custom renderer called
        # With dynamic captions (larger chunks), we expect at least as many clips as script items (if 1 chunk per line min)
        # But actually, if we have chunks, we have >= 1 per line.
        self.assertTrue(MockCreateTextImage.call_count >= len(self.mock_script_data))
        self.assertTrue(MockImageClip.call_count >= len(self.mock_script_data))
        
        # 4. Composite created?
        MockComposite.assert_called_once()
        
        # 5. File written?
        mock_final_video.write_videofile.assert_called_once_with(
            self.mock_output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac'
        )

    @patch('src.generator.video_generator.VideoFileClip')
    @patch('src.generator.video_generator.AudioFileClip')
    @patch('src.generator.video_generator.ImageClip')
    @patch('src.generator.video_generator.create_text_image')
    @patch('src.generator.video_generator.CompositeVideoClip')
    def test_create_video_no_loop(self, MockComposite, MockCreateTextImage, MockImageClip, MockAudioClip, MockVideoClip):
        # Case where BG is longer than audio
        mock_audio = MockAudioClip.return_value
        mock_audio.duration = 5
        
        mock_bg = MockVideoClip.return_value
        mock_bg.duration = 10 
        mock_bg.subclip.return_value = mock_bg
        mock_bg.crop.return_value = mock_bg

        # Run
        self.video_gen.create_video(
            self.mock_bg_path, 
            self.mock_audio_path, 
            self.mock_script_data, 
            self.mock_output_path
        )
        
        # Verify subclip called, loop NOT called
        mock_bg.subclip.assert_called_with(0, 5)
        # Note: In the code, loop is only called if bg < duration.
        # We can verify it wasn't called by checking the mock's method calls.
        # However, since loop is a method on the VideoFileClip instance, ensure we check that specific instance.
        mock_bg.loop.assert_not_called()
