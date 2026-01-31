
import unittest
import numpy as np
from pathlib import Path
from src.generator.text_renderer import create_text_image

class TestTextRenderer(unittest.TestCase):
    def test_create_text_image_basic(self):
        text = "Hello World"
        img_array = create_text_image(text, "Arial", 50, 1000)
        
        # Check shape: (height, width, 4) -> RGBA
        self.assertEqual(len(img_array.shape), 3)
        self.assertEqual(img_array.shape[2], 4)
        
    def test_text_wrapping(self):
        text = "This is a very long sentence that should definitely wrap to the next line because the max width is small."
        # Use a small max width to force wrapping
        img_array = create_text_image(text, "Arial", 50, 200)
        
        # We can't easily assert exactly how many lines without OCR or inspecting internals, 
        # but we can ensure the image isn't super wide (respected max_width roughly)
        # Note: The function adds padding, so width might be > 200, but not width of full text.
        height, width, _ = img_array.shape
        self.assertTrue(height > 50) # Definitely more than one line
        
    def test_single_word_overflow(self):
        # Case where a single word is wider than max_width
        text = "Supercalifragilisticexpialidocious"
        # Very small width
        img_array = create_text_image(text, "Arial", 50, 10)
        
        # Should contain the word (not crash, and likely just expand width)
        # We verify it runs and produces an image
        self.assertIsNotNone(img_array)
        self.assertTrue(img_array.shape[1] > 10) # Width should expand to fit the word
