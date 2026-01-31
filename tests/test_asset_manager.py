

import unittest
import shutil
from pathlib import Path
import sys


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
        video_index = 1
        path = self.manager.get_output_path(i=video_index)
        
        expected_filename = f"video{video_index}.mp4"

        expected_dir = self.manager.output_dir / "finalVideo"
        
        expected_path = str(expected_dir / expected_filename)
        
        self.assertEqual(path, expected_path)

    def test_03_save_script_writes_file_to_temp(self):
        test_content = "This is a test script content for review."
        filename = "test_script.txt"
        
        saved_path = self.manager.save_script(test_content, filename)
        
        expected_path = self.manager.temp_dir / filename
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

    def test_06_get_font_path(self):
        font = self.manager.get_font_path()
        self.assertEqual(font, "Arial")

    def test_07_get_output_path_timestamp(self):
        # Test getting output path without index (triggers timestamp logic)
        path = self.manager.get_output_path(i=None)
        self.assertIn("video_", path)
        self.assertTrue(path.endswith(".mp4"))

    def test_08_save_audio(self):
        # Test save_audio method (currently it just returns path, doesn't write bytes locally in the snippet logic provided earlier? 
        # Wait, the code says: return str(self.temp_dir / filename)
        # It doesn't write anything? 
        # Lines 34-35: def save_audio(self, audio_bytes=None, filename="narration.mp3"): return str(self.temp_dir / filename)
        # So it's just a path helper? 
        # Yes.
        path = self.manager.save_audio(filename="test.mp3")
        expected = self.manager.temp_dir / "test.mp3"
        self.assertEqual(path, str(expected))