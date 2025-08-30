"""
Test suite for the framework exporter
"""

from scripts.icon_framework_exporter import (
    FrameworkConfig,
    camel_to_kebab,
    extract_svg_content,
    kebab_to_camel,
    snake_to_camel,
    to_component_name,
)
import shutil

# Add parent directory to path to allow imports
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestFrameworkExporter(unittest.TestCase):
    """Test cases for framework exporter"""

    def setUp(self):
        """Set up test environment"""
        # Create temporary directory for test output
        self.test_dir = tempfile.mkdtemp()
        self.output_dir = Path(self.test_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)

        # Create a simple test SVG
        self.svg_path = Path(self.test_dir) / "test_icon.svg"
        self.svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <rect x="2" y="2" width="20" height="20" fill="#FF6A00" />
  <circle cx="12" cy="12" r="6" fill="#FFFFFF" />
</svg>'''
        self.svg_path.write_text(self.svg_content)

    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_camel_to_kebab(self):
        """Test camelCase to kebab-case conversion"""
        self.assertEqual(camel_to_kebab("testCase"), "test-case")
        self.assertEqual(camel_to_kebab("TestCase"), "test-case")
        self.assertEqual(camel_to_kebab("testCaseExample"), "test-case-example")
        self.assertEqual(camel_to_kebab("test"), "test")

    def test_snake_to_camel(self):
        """Test snake_case to camelCase conversion"""
        self.assertEqual(snake_to_camel("test_case"), "testCase")
        self.assertEqual(snake_to_camel("test_case_example"), "testCaseExample")
        self.assertEqual(snake_to_camel("test"), "test")

    def test_kebab_to_camel(self):
        """Test kebab-case to camelCase conversion"""
        self.assertEqual(kebab_to_camel("test-case"), "testCase")
        self.assertEqual(kebab_to_camel("test-case-example"), "testCaseExample")
        self.assertEqual(kebab_to_camel("test"), "test")

    def test_to_component_name(self):
        """Test conversion to component name"""
        self.assertEqual(to_component_name("test_icon"), "TestIconIcon")
        self.assertEqual(to_component_name("test-icon"), "TestIconIcon")
        self.assertEqual(to_component_name("TestIcon"), "TesticonIcon")
        self.assertEqual(to_component_name("test"), "TestIcon")

    def test_extract_svg_content(self):
        """Test extracting content from SVG file"""
        inner_content, viewbox_size, raw_content = extract_svg_content(self.svg_path)

        # Check extracted viewBox size
        self.assertEqual(viewbox_size, 24)

        # Check that inner content includes the shapes
        self.assertTrue("<rect" in inner_content)
        self.assertTrue("<circle" in inner_content)

        # Check that raw content matches original
        self.assertEqual(raw_content, self.svg_content)

    def test_framework_config(self):
        """Test FrameworkConfig dataclass"""
        config = FrameworkConfig(
            name="test",
            file_extension=".test",
            component_template="Component: {ComponentName}",
            index_template="Index: {fileName}",
            package_json={"name": "test-package"}
        )

        self.assertEqual(config.name, "test")
        self.assertEqual(config.file_extension, ".test")
        self.assertEqual(config.component_template, "Component: {ComponentName}")
        self.assertEqual(config.index_template, "Index: {fileName}")
        self.assertEqual(config.package_json, {"name": "test-package"})
        self.assertEqual(config.extra_files, {})


if __name__ == "__main__":
    unittest.main()
