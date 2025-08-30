"""
Test suite for the enhanced icon generation system
"""

from scripts.enhanced_icon_generator import (
    IconGenerationStats,
    IconVariant,
    create_variant_matrix,
    process_variant,
)
import os
import shutil

# Add parent directory to path to allow imports
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestEnhancedIconGeneration(unittest.TestCase):
    """Test cases for enhanced icon generation"""

    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test output
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.test_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)

        # Override global output directory
        import scripts.enhanced_icon_generator
        self._original_out = scripts.enhanced_icon_generator.OUT
        scripts.enhanced_icon_generator.OUT = self.output_dir

    def tearDown(self):
        """Clean up test environment"""
        # Restore original output directory
        import scripts.enhanced_icon_generator
        scripts.enhanced_icon_generator.OUT = self._original_out

        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_icon_variant_class(self):
        """Test IconVariant dataclass"""
        # Test with minimal parameters
        variant = IconVariant(mode="light", finish="flat-orange",
                              size=16, context="web")

        self.assertEqual(variant.mode, "light")
        self.assertEqual(variant.finish, "flat-orange")
        self.assertEqual(variant.size, 16)
        self.assertEqual(variant.context, "web")
        self.assertEqual(variant.base_filename, "strategy_icon-light-flat-orange-16px")
        self.assertEqual(variant.output_folder, self.output_dir /
                         "light" / "flat-orange" / "16px" / "web")

        # Test with custom filename
        variant = IconVariant(
            mode="dark",
            finish="matte-carbon",
            size=32,
            context="print",
            filename="custom-name.png"
        )

        self.assertEqual(variant.filename, "custom-name.png")
        self.assertEqual(variant.base_filename, "custom-name")

    def test_create_variant_matrix(self):
        """Test creation of variant matrix"""
        options = {
            "modes": ["light", "dark"],
            "finishes": ["flat-orange"],
            "sizes": [16, 32],
            "contexts": ["web"]
        }

        variants = create_variant_matrix(options)

        self.assertEqual(len(variants), 4)  # 2 modes * 1 finish * 2 sizes * 1 context

        # Check first variant
        self.assertEqual(variants[0].mode, "light")
        self.assertEqual(variants[0].finish, "flat-orange")
        self.assertEqual(variants[0].size, 16)
        self.assertEqual(variants[0].context, "web")

        # Check last variant
        self.assertEqual(variants[3].mode, "dark")
        self.assertEqual(variants[3].finish, "flat-orange")
        self.assertEqual(variants[3].size, 32)
        self.assertEqual(variants[3].context, "web")

    def test_icon_generation_stats(self):
        """Test IconGenerationStats class"""
        stats = IconGenerationStats()

        # Record some statistics
        variant1 = IconVariant(mode="light", finish="flat-orange",
                               size=16, context="web")
        variant2 = IconVariant(mode="dark", finish="matte-carbon",
                               size=32, context="print")

        stats.record_success(variant1, ["svg", "png"])
        stats.record_success(variant2, ["svg", "png", "webp"])
        stats.record_failure(variant1, "Test error")

        stats.add_processing_time(0.5)
        stats.add_processing_time(1.0)

        self.assertEqual(stats.total_variants, 3)
        self.assertEqual(stats.successful_svgs, 2)
        self.assertEqual(stats.successful_pngs, 2)
        self.assertEqual(stats.successful_additional_formats["webp"], 1)
        self.assertEqual(len(stats.failed_variants), 1)
        self.assertEqual(stats.average_processing_time, 0.75)


if __name__ == "__main__":
    unittest.main()
