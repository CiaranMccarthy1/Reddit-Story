

import unittest
import shutil
from pathlib import Path
import sys
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator.asset_manager import AssetManager

class TestAssetManager(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create a temporary root directory for testing
        cls.test_root = Path("temp_test_project_root")
        cls.test_root.mkdir(exist_ok=True)
        
        # Instantiate AssetManager pointing to the test root
        cls.manager = AssetManager(cls.test_root)

    def setUp(self):
        # Reset session ID before each test
        self.manager.current_session_id = None

    @classmethod
    def tearDownClass(cls):
        # Clean up the temporary directory after all tests
        if cls.test_root.exists():
            shutil.rmtree(cls.test_root)

    def test_01_initialization_creates_folders(self):
        # Check if the necessary directories were created
        self.assertTrue(self.manager.assets_dir.exists())
        self.assertTrue(self.manager.output_dir.exists())
        self.assertTrue(self.manager.temp_dir.exists())

    def test_02_get_output_path(self):
        # 1. With Index
        path_idx = self.manager.get_output_path(i=1)
        self.assertTrue(path_idx.endswith("video1.mp4"))
        
        # 2. With Session
        session_id = self.manager.create_session()
        path_session = self.manager.get_output_path()
        self.assertIn(session_id, path_session)
        self.assertTrue(path_session.endswith(".mp4"))
        
        # 3. Fallback (No session, no index)
        self.manager.current_session_id = None
        path_fallback = self.manager.get_output_path()
        self.assertIn("video_", path_fallback)

    def test_03_save_script_writes_file_to_temp(self):
        # Verify it writes to session dir if active
        session_id = self.manager.create_session()
        
        test_content = "This is a test script content for review."
        filename = "test_script.txt"
        
        saved_path = self.manager.save_script(test_content, filename)
        
        # Should be in temp/session_id/filename
        expected_path = self.manager.temp_dir / session_id / filename
        self.assertEqual(saved_path, str(expected_path))
        self.assertTrue(expected_path.exists())
        
        with open(expected_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, test_content)

    def test_04_get_background_video_success(self):
        # Create a dummy video file in assets
        dummy_video = self.manager.assets_dir / "bg.mp4"
        dummy_video.touch()
        
        path = self.manager.get_background_video()
        self.assertEqual(path, str(dummy_video))
        
        dummy_video.unlink() # Clean up

    def test_05_get_background_video_failure(self):
        # Ensure no video exists, expecting FileNotFoundError
        with self.assertRaises(FileNotFoundError):
            self.manager.get_background_video()

    @patch('src.generator.asset_manager.Path.exists')
    def test_06_get_font_path(self, MockExists):
        # Case 1: Exists
        MockExists.return_value = True
        font = self.manager.get_font_path()
        self.assertIn("arial.ttf", font.lower())

        # Case 2: Does not exist
        MockExists.return_value = False
        font = self.manager.get_font_path()
        self.assertEqual(font, "Arial")

    def test_07_get_output_path_timestamp(self):
        # Test getting output path without index (triggers timestamp logic)
        path = self.manager.get_output_path(i=None)
        self.assertIn("video_", path)
        self.assertTrue(path.endswith(".mp4"))

    def test_08_save_audio(self):
        # 1. With Session
        session_id = self.manager.create_session()
        path = self.manager.save_audio(filename="test.mp3")
        expected = self.manager.temp_dir / session_id / "test.mp3"
        self.assertEqual(path, str(expected))
        
        # 2. Without Session
        self.manager.current_session_id = None
        path_fallback = self.manager.save_audio(filename="fallback.mp3")
        expected_fallback = self.manager.temp_dir / "fallback.mp3"
        self.assertEqual(path_fallback, str(expected_fallback))