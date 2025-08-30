"""
Test suite for the palette manager
"""

from scripts.palette_manager import (
    create_palette,
    darken_color,
    get_complementary_color,
    hex_to_rgb,
    lighten_color,
    rgb_to_hex,
)
import json

# Add parent directory to path to allow imports
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestPaletteManager(unittest.TestCase):
    """Test cases for palette manager"""

    def test_hex_to_rgb(self):
        """Test hex to RGB conversion"""
        self.assertEqual(hex_to_rgb("#FF0000"), (255, 0, 0))
        self.assertEqual(hex_to_rgb("#00FF00"), (0, 255, 0))
        self.assertEqual(hex_to_rgb("#0000FF"), (0, 0, 255))
        self.assertEqual(hex_to_rgb("#FFFFFF"), (255, 255, 255))
        self.assertEqual(hex_to_rgb("#000000"), (0, 0, 0))

    def test_rgb_to_hex(self):
        """Test RGB to hex conversion"""
        self.assertEqual(rgb_to_hex((255, 0, 0)), "#ff0000")
        self.assertEqual(rgb_to_hex((0, 255, 0)), "#00ff00")
        self.assertEqual(rgb_to_hex((0, 0, 255)), "#0000ff")
        self.assertEqual(rgb_to_hex((255, 255, 255)), "#ffffff")
        self.assertEqual(rgb_to_hex((0, 0, 0)), "#000000")

    def test_lighten_color(self):
        """Test color lightening"""
        # Test with black (should get gray)
        self.assertNotEqual(lighten_color("#000000", 0.5), "#000000")

        # Test with white (should stay white)
        self.assertEqual(lighten_color("#FFFFFF", 0.5), "#ffffff")

        # Test with red
        lightened_red = lighten_color("#FF0000", 0.2)
        rgb = hex_to_rgb(lightened_red)
        self.assertEqual(rgb[0], 255)  # Red channel stays at max
        self.assertTrue(rgb[1] > 0)  # Other channels increase
        self.assertTrue(rgb[2] > 0)

    def test_darken_color(self):
        """Test color darkening"""
        # Test with white (should get gray)
        self.assertNotEqual(darken_color("#FFFFFF", 0.5), "#FFFFFF")

        # Test with black (should stay black)
        self.assertEqual(darken_color("#000000", 0.5), "#000000")

        # Test with red
        darkened_red = darken_color("#FF0000", 0.2)
        rgb = hex_to_rgb(darkened_red)
        self.assertTrue(rgb[0] < 255)  # Red channel decreases
        self.assertEqual(rgb[1], 0)    # Other channels stay at 0
        self.assertEqual(rgb[2], 0)

    def test_get_complementary_color(self):
        """Test complementary color calculation"""
        # Red -> Cyan
        self.assertEqual(get_complementary_color("#FF0000").lower(), "#00ffff")

        # Green -> Magenta
        self.assertEqual(get_complementary_color("#00FF00").lower(), "#ff00ff")

        # Blue -> Yellow
        self.assertEqual(get_complementary_color("#0000FF").lower(), "#ffff00")

    def test_create_palette(self):
        """Test palette creation"""
        # Create a palette with a base color
        palette = create_palette("test", "#FF0000")

        # Should have at least 5 colors
        self.assertTrue(len(palette) >= 5)

        # Should include the base color
        self.assertEqual(palette["test-main"], "#FF0000")

        # Should include light and dark variants
        self.assertTrue("test-light" in palette)
        self.assertTrue("test-dark" in palette)

        # Should include complementary color
        self.assertTrue("test-complement" in palette)


if __name__ == "__main__":
    unittest.main()
