
import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator.pipeline import VideoGenerationPipeline, PipelineError

class TestPipelineIntegration(unittest.TestCase):
    def setUp(self):
        self.mock_fetcher = MagicMock()
        self.mock_script_builder = MagicMock()
        self.mock_audio_gen = MagicMock()
        self.mock_video_gen = MagicMock()
        self.mock_assets_mgr = MagicMock()
        
        self.pipeline = VideoGenerationPipeline(
            self.mock_fetcher,
            self.mock_script_builder,
            self.mock_audio_gen,
            self.mock_video_gen,
            self.mock_assets_mgr
        )

    def test_pipeline_run_success(self):
        # --- Mock Return Values ---
        self.mock_fetcher.generate_script.return_value = "RAW_AI_OUTPUT"
        
        # Script builder returns (story_text, script_data_list)
        mock_script_data = [{'start': 0, 'text': 'Hi'}]
        self.mock_script_builder.parse_response.return_value = ("Story Text", mock_script_data)
        
        self.mock_assets_mgr.create_session.return_value = "video_123"
        self.mock_assets_mgr.save_audio.return_value = "audio.mp3"
        self.mock_assets_mgr.get_background_video.return_value = "bg.mp4"
        self.mock_assets_mgr.get_output_path.return_value = "final.mp4"
        
        # --- Run ---
        prompt_file = "dummyprompt.txt"
        output_path = self.pipeline.run(prompt_file, duration=90)
        
        # --- Assertions ---
        # 0. Returns the output path
        self.assertEqual(output_path, "final.mp4")
        
        # 1. Fetcher called with prompt file and duration
        self.mock_fetcher.generate_script.assert_called_with(prompt_file, 90)
        
        # 2. Script Parsed
        self.mock_script_builder.parse_response.assert_called_with("RAW_AI_OUTPUT")
        
        # 3. Assets Saved
        self.mock_assets_mgr.save_script.assert_called()
        self.mock_assets_mgr.save_audio.assert_called()
        
        # 4. Audio Generated
        self.mock_audio_gen.generate_narration.assert_called_with(mock_script_data, "audio.mp3")
        
        # 5. Video Created
        self.mock_video_gen.create_video.assert_called_with("bg.mp4", "audio.mp3", mock_script_data, "final.mp4")
        
        # 6. Session created
        self.mock_assets_mgr.create_session.assert_called_once()

    def test_pipeline_missing_script_data_halts(self):
        # Simulate parse failure (empty script data)
        self.mock_fetcher.generate_script.return_value = "BAD_OUTPUT"
        self.mock_script_builder.parse_response.return_value = ("Story", []) # Empty list!
        
        with self.assertRaises(PipelineError):
            self.pipeline.run("prompt.txt")
        
        # Verify it stopped early
        self.mock_audio_gen.generate_narration.assert_not_called()
        self.mock_video_gen.create_video.assert_not_called()

    def test_background_video_checked_before_llm_call(self):
        # Fail-fast: a missing background video must surface before any API call.
        self.mock_assets_mgr.get_background_video.side_effect = FileNotFoundError("no bg")

        with self.assertRaises(FileNotFoundError):
            self.pipeline.run("prompt.txt")

        self.mock_fetcher.generate_script.assert_not_called()

    def test_background_video_resolved_before_generate_script(self):
        call_order = []
        self.mock_assets_mgr.get_background_video.side_effect = lambda: (
            call_order.append('background_video') or "bg.mp4"
        )
        self.mock_fetcher.generate_script.side_effect = lambda *a, **k: (
            call_order.append('generate_script') or "RAW_AI_OUTPUT"
        )
        self.mock_script_builder.parse_response.return_value = ("Story", [{'start': 0, 'text': 'Hi'}])
        self.mock_assets_mgr.create_session.return_value = "video_123"
        self.mock_assets_mgr.save_audio.return_value = "audio.mp3"
        self.mock_assets_mgr.get_output_path.return_value = "final.mp4"

        self.pipeline.run("prompt.txt")

        self.assertEqual(call_order, ['background_video', 'generate_script'])
