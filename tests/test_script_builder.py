

import unittest
import sys
from pathlib import Path

# Configure sys.path to allow imports from src/generator
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator.script_builder import ScriptBuilder

class TestScriptBuilder(unittest.TestCase):
    
    def setUp(self):
        self.builder = ScriptBuilder()
        self.mock_response = """
        SECTION 1: STORY
        The air was thick with silence. This story will be saved.

        SECTION 2: TIMESTAMPED SCRIPT
        00:00:00: "First line."
        00:00:05: "Second line."
        00:00:12: "Third line."
        """

    def test_01_parse_valid_response(self):
        story, script = self.builder.parse_response(self.mock_response)
        
        # Test Story parsing
        self.assertIn("The air was thick with silence.", story)
        self.assertNotIn("SECTION 1:", story)
        
        # Test Script parsing
        self.assertEqual(len(script), 3)
        self.assertEqual(script[0]['start'], 0)
        self.assertEqual(script[1]['start'], 5)
        self.assertEqual(script[2]['text'], "Third line.")

    def test_02_handle_malformed_timestamp(self):
        malformed_response = """
        SECTION 1: STORY
        A short story.
        SECTION 2: TIMESTAMPED SCRIPT
        00:00:00: "First line."
        00:00:05; "Malformed line." # Note the semicolon, should be skipped
        00:00:10: "Third line."
        """
        story, script = self.builder.parse_response(malformed_response)
        
        self.assertEqual(len(script), 2) # Only two lines were correctly formatted
        self.assertEqual(script[1]['start'], 10)

    def test_03_handle_missing_script_section(self):
        missing_script_section = "SECTION 1: STORY\nOnly the story is here."
        story, script = self.builder.parse_response(missing_script_section)
        
        self.assertIn("Only the story is here.", story)
        self.assertEqual(len(script), 0) # Script should be empty

    def test_04_empty_input(self):
        story, script = self.builder.parse_response("")
        self.assertEqual(story, "")
        self.assertEqual(script, [])

    def test_05_whitespace_handling(self):
        response = """
        SECTION 1: STORY
          Story with extra spaces.   
        SECTION 2: TIMESTAMPED SCRIPT
          00:00:01: "  Text with spaces.  "
        """
        story, script = self.builder.parse_response(response)
        
        self.assertEqual(story, "Story with extra spaces.")
        self.assertEqual(script[0]['text'], "Text with spaces.")