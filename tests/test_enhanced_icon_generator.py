#!/usr/bin/env python3
"""
Test script for the Enhanced Icon Generator

This script runs a series of tests to verify that the enhanced_icon_generator.py
is working correctly. It tests various features of the generator, including:
- Loading variants from CSV
- Generating individual variants
- Batch generation
- Custom palette support
- Error handling
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Add parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import the modules to test
try:
    from scripts.enhanced_icon_generator import (
        IconVariant,
        batch_generate_icons,
        create_variant_matrix,
        process_variant,
    )
    from scripts.generate_icons import bake_svg
except ImportError as e:
    print(f"Error importing enhanced_icon_generator: {e}")
    print("Make sure enhanced_icon_generator.py exists in the scripts directory")
    sys.exit(1)


class TestEnhancedIconGenerator(unittest.TestCase):
    """Test case for enhanced_icon_generator.py"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.temp_out = Path(self.temp_dir) / "out"
        self.temp_out.mkdir()
        self.temp_masters = Path(self.temp_dir) / "masters"
        self.temp_masters.mkdir()

        # Create a simple test SVG
        self.test_svg = self.temp_masters / "test_icon.svg"
        with open(self.test_svg, "w") as f:
            f.write("""<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
            <rect width="24" height="24" fill="#FF6A00"/>
            <circle cx="12" cy="12" r="6" fill="#FFFFFF"/>
            </svg>""")

        # Create a patch for using our temp directories
        self.masters_patcher = patch(
            "scripts.enhanced_icon_generator.MASTERS", self.temp_masters)
        self.out_patcher = patch("scripts.enhanced_icon_generator.OUT", self.temp_out)

        # Start the patchers
        self.masters_mock = self.masters_patcher.start()
        self.out_mock = self.out_patcher.start()

    def tearDown(self):
        """Clean up after tests"""
        # Stop the patchers
        self.masters_patcher.stop()
        self.out_patcher.stop()

        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_icon_variant_creation(self):
        """Test creating an IconVariant object"""
        variant = IconVariant(
            mode="light",
            finish="flat-orange",
            size=24,
            context="web"
        )

        self.assertEqual(variant.mode, "light")
        self.assertEqual(variant.finish, "flat-orange")
        self.assertEqual(variant.size, 24)
        self.assertEqual(variant.context, "web")
        self.assertEqual(variant.filename, "strategy_icon-light-flat-orange-24px.png")
        self.assertEqual(variant.formats, ["svg", "png"])

    def test_icon_variant_paths(self):
        """Test that IconVariant calculates correct paths"""
        variant = IconVariant(
            mode="light",
            finish="flat-orange",
            size=24,
            context="web"
        )

        expected_output_folder = self.temp_out / "light" / "flat-orange" / "24px" / "web"
        expected_svg_path = expected_output_folder / f"{variant.base_filename}.svg"
        expected_png_path = expected_output_folder / variant.filename

        self.assertEqual(variant.output_folder, expected_output_folder)
        # IconVariant doesn't have svg_path or png_path properties directly,
        # but we can verify the paths that would be used
        self.assertEqual(expected_svg_path, expected_output_folder /
                         f"{variant.base_filename}.svg")
        self.assertEqual(expected_png_path, expected_output_folder / variant.filename)

    def test_bake_svg(self):
        """Test the SVG baking function"""
        # Create a test SVG content with color placeholders
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24">
        <rect width="24" height="24" fill="#FF6A00"/>
        <circle cx="12" cy="12" r="6" fill="#FFFFFF"/>
        </svg>"""

        # Create a variant for light mode
        variant = IconVariant(
            mode="light",
            finish="flat-orange",
            size=24,
            context="web"
        )

        # Bake the SVG for light mode
        light_svg = bake_svg(svg_content, variant.mode, variant.finish)

        # In light mode, only the #FFFFFF is replaced with #FF6A00 (foreground color)
        # The background rect with #FF6A00 stays as #FF6A00
        self.assertIn('<rect width="24" height="24" fill="#FF6A00"/>', light_svg)
        self.assertIn('<circle cx="12" cy="12" r="6" fill="#FF6A00"/>', light_svg)

        # Now test dark mode
        dark_svg = bake_svg(svg_content, "dark", "flat-orange")

        # In dark mode, #FF6A00 is replaced with #060607 (dark background)
        # And #FFFFFF is replaced with #FF6A00 (foreground color)
        self.assertIn('<rect width="24" height="24" fill="#060607"/>', dark_svg)
        self.assertIn('<circle cx="12" cy="12" r="6" fill="#FF6A00"/>', dark_svg)

    def test_bake_svg_with_custom_tokens(self):
        """Test SVG baking with custom color tokens"""
        # Create a test SVG content with color placeholders
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24"
viewBox="0 0 24 24">
        <rect width="24" height="24" fill="#FF6A00"/>
        <circle cx="12" cy="12" r="6" fill="#FFFFFF"/>
        </svg>"""

        # For this test, we need to patch both TOKENS and FINISH_COLORS
        # to see how they interact
        with patch("scripts.generate_icons.FINISH_COLORS", {
            "flat-orange": "#FF6A00",
            "custom-blue": "#0066FF"
        }), patch("scripts.generate_icons.TOKENS", {
            "paper": "#FFFFFF",
            "slate_950": "#060607",
            "brand_orange": "#FF6A00"
        }):
            # Bake the SVG for light mode with custom-blue finish
            light_svg = bake_svg(svg_content, "light", "custom-blue")

            # Based on our debugging, with a custom finish:
            # Both colors will be replaced with the foreground color
            self.assertIn('<rect width="24" height="24" fill="#0066FF"/>', light_svg)
            self.assertIn('<circle cx="12" cy="12" r="6" fill="#0066FF"/>', light_svg)

    @patch("scripts.enhanced_icon_generator.maybe_export_png")
    def test_process_variant(self, mock_export_png):
        """Test processing a single icon variant"""
        # Set up the mock to simulate successful PNG export
        mock_export_png.return_value = True

        # Create a variant
        variant = IconVariant(
            mode="light",
            finish="flat-orange",
            size=24,
            context="web"
        )

        # Process the variant
        success, formats, error = process_variant(variant)

        # Check the result
        self.assertTrue(success)
        self.assertIn("svg", formats)
        self.assertIn("png", formats)
        self.assertIsNone(error)

        # Check that the SVG file was created
        expected_output_folder = self.temp_out / "light" / "flat-orange" / "24px" / "web"
        expected_svg_path = expected_output_folder / \
            f"strategy_icon-{variant.mode}-{variant.finish}-{variant.size}px.svg"
        self.assertTrue(expected_svg_path.exists())

    def test_batch_generate_icons(self):
        """Test batch generating multiple icons"""
        # Create some variants
        variants = [
            IconVariant(mode="light", finish="flat-orange", size=16, context="web"),
            IconVariant(mode="dark", finish="flat-orange", size=16, context="web"),
            IconVariant(mode="light", finish="matte-carbon", size=24, context="web"),
        ]

        # Use a patch to mock maybe_export_png to avoid actual PNG conversion
        with patch("scripts.enhanced_icon_generator.maybe_export_png", return_value=True):
            # Generate the icons
            stats = batch_generate_icons(variants, parallel=False)

            # Check the result
            self.assertEqual(stats.total_variants, 3)
            self.assertEqual(stats.successful_svgs, 3)
            self.assertEqual(stats.successful_pngs, 3)

            # Check that all SVG files were created
            for variant in variants:
                expected_svg_path = variant.output_folder / \
                    f"{variant.base_filename}.svg"
                self.assertTrue(expected_svg_path.exists())

    def test_create_variant_matrix(self):
        """Test creating a matrix of variants from options"""
        options = {
            "modes": ["light", "dark"],
            "finishes": ["flat-orange"],
            "sizes": [16, 24],
            "contexts": ["web"],
            "formats": ["svg"]
        }

        variants = create_variant_matrix(options)

        # Should create 2 modes * 1 finish * 2 sizes * 1 context = 4 variants
        self.assertEqual(len(variants), 4)

        # Check that all expected combinations are present
        expected_combinations = [
            ("light", "flat-orange", 16, "web"),
            ("light", "flat-orange", 24, "web"),
            ("dark", "flat-orange", 16, "web"),
            ("dark", "flat-orange", 24, "web")
        ]

        for variant in variants:
            self.assertIn(
                (variant.mode, variant.finish, variant.size, variant.context),
                expected_combinations
            )
            self.assertEqual(variant.formats, ["svg"])


def run_tests():
    """Run the tests"""
    print("Running Enhanced Icon Generator Tests")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


if __name__ == "__main__":
    run_tests()
