#!/usr/bin/env python3
"""
StrategyDECK PNG Conversion Debug Tool

This script provides comprehensive debugging capabilities for the SVG to PNG 
conversion process in the StrategyDECK Icon Generation System.
"""

import argparse
import importlib.util
import io
import os
import platform
import subprocess
import sys
import traceback
from pathlib import Path

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Create debug output directory
DEBUG_DIR = ROOT / "assets" / "debug"
DEBUG_DIR.mkdir(parents=True, exist_ok=True)


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)

# Check for CairoSVG


def check_cairosvg():
    """Check if CairoSVG is installed and working"""
    print_section("CairoSVG Installation Check")

    # Method 1: Check using importlib
    spec = importlib.util.find_spec("cairosvg")
    if spec is None:
        print("❌ CairoSVG is not installed (importlib check)")
        return False

    print("✅ CairoSVG module is available (importlib check)")

    # Method 2: Try importing
    try:
        import cairosvg
        print(f"✅ CairoSVG imported successfully (version: {cairosvg.__version__})")

        # Check for cairocffi
        try:
            import cairocffi
            print(f"✅ Cairocffi is available (version: {cairocffi.__version__})")
        except ImportError:
            print("ℹ️ Cairocffi is not installed (using Pycairo instead)")

        return True
    except ImportError as e:
        print(f"❌ Failed to import CairoSVG: {str(e)}")
        return False

# Test SVG to PNG conversion using CairoSVG directly


def test_direct_conversion():
    """Test direct SVG to PNG conversion using CairoSVG"""
    print_section("Direct CairoSVG Conversion Test")

    # Create a simple test SVG
    test_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="40" fill="#FF6A00" />
        <text x="50" y="55" font-family="sans-serif" font-size="12" text-anchor="middle" fill="white">
            Test
        </text>
    </svg>
    """

    test_svg_path = DEBUG_DIR / "test_direct.svg"
    test_png_path = DEBUG_DIR / "test_direct.png"

    # Write the test SVG
    test_svg_path.write_text(test_svg)
    print(f"✅ Created test SVG file: {test_svg_path}")

    # Try to convert using CairoSVG
    try:
        import cairosvg
        cairosvg.svg2png(
            file_obj=open(test_svg_path, "rb"),
            write_to=str(test_png_path)
        )
        print(f"✅ Successfully converted to PNG: {test_png_path}")
        return True
    except ImportError:
        print("❌ CairoSVG not available for direct conversion")
        return False
    except Exception as e:
        print(f"❌ Error during direct conversion: {str(e)}")
        traceback.print_exc()
        return False

# Test conversion using BytesIO


def test_bytesio_conversion():
    """Test SVG to PNG conversion using BytesIO"""
    print_section("BytesIO Conversion Test")

    # Create a simple test SVG
    test_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="40" fill="#3182CE" />
        <text x="50" y="55" font-family="sans-serif" font-size="12" text-anchor="middle" fill="white">
            BytesIO
        </text>
    </svg>
    """

    test_png_path = DEBUG_DIR / "test_bytesio.png"

    # Try conversion
    try:
        from io import BytesIO

        import cairosvg

        # Convert to BytesIO first
        svg_bytes = test_svg.encode('utf-8')
        png_bytes = cairosvg.svg2png(bytestring=svg_bytes)

        # Save the PNG
        with open(test_png_path, 'wb') as f:
            f.write(png_bytes)

        print(f"✅ Successfully converted to PNG using BytesIO: {test_png_path}")
        return True
    except ImportError:
        print("❌ CairoSVG not available for BytesIO conversion")
        return False
    except Exception as e:
        print(f"❌ Error during BytesIO conversion: {str(e)}")
        traceback.print_exc()
        return False

# Test conversion from the generate_icons module


def test_module_conversion():
    """Test PNG conversion using functions from generate_icons module"""
    print_section("Module Function Conversion Test")

    try:
        # Try to import from our generation script
        try:
            from generate_icons import maybe_export_png
            print("✅ Successfully imported maybe_export_png from generate_icons")
            module_available = True
        except ImportError:
            print("❌ Could not import maybe_export_png from generate_icons")
            module_available = False

        if not module_available:
            return False

        # Create a simple test SVG
        test_svg = """
        <svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="#38A169" />
            <text x="50" y="55" font-family="sans-serif" font-size="12" text-anchor="middle" fill="white">
                Module
            </text>
        </svg>
        """

        test_png_path = DEBUG_DIR / "test_module.png"

        # Try conversion
        result = maybe_export_png(
            test_svg.encode("utf-8"),
            test_png_path,
            100
        )

        if result:
            print(
                f"✅ Successfully converted to PNG using maybe_export_png: {test_png_path}")
        else:
            print("❌ maybe_export_png failed but did not raise an exception")

        return result

    except Exception as e:
        print(f"❌ Error during module conversion: {str(e)}")
        traceback.print_exc()
        return False

# Check system dependencies


def check_system_deps():
    """Check system dependencies for CairoSVG"""
    print_section("System Dependencies Check")

    system = platform.system()
    print(f"Operating System: {system} ({platform.version()})")

    # Check for Cairo
    if system in ["Linux", "Darwin"]:  # Linux or macOS
        try:
            result = subprocess.run(
                ["pkg-config", "--exists", "cairo"],
                check=False
            )
            if result.returncode == 0:
                print("✅ Cairo is installed (pkg-config check)")

                # Get Cairo version
                try:
                    version_result = subprocess.run(
                        ["pkg-config", "--modversion", "cairo"],
                        check=True,
                        capture_output=True,
                        text=True
                    )
                    print(f"✅ Cairo version: {version_result.stdout.strip()}")
                except Exception:
                    pass
            else:
                print("❌ Cairo is not installed (pkg-config check)")

                # Suggest installation command
                if system == "Linux":
                    if os.path.exists("/etc/debian_version"):
                        print("  Suggestion: sudo apt-get install libcairo2-dev")
                    elif os.path.exists("/etc/redhat-release"):
                        print("  Suggestion: sudo yum install cairo-devel")
                elif system == "Darwin":  # macOS
                    print("  Suggestion: brew install cairo")
        except FileNotFoundError:
            print("⚠️ pkg-config not found, cannot check for Cairo")
            if system == "Linux":
                print("  Suggestion: sudo apt-get install pkg-config")
            elif system == "Darwin":  # macOS
                print("  Suggestion: brew install pkg-config")
    elif system == "Windows":
        print("ℹ️ On Windows, Cairo is typically bundled with Python packages")
        print("  Suggestion: pip install cairocffi")

    # Check for Python dev packages
    try:
        import sysconfig
        include_dir = sysconfig.get_path('include')
        if os.path.exists(include_dir):
            print(f"✅ Python development headers found: {include_dir}")
        else:
            print("❌ Python development headers not found")
            if system == "Linux":
                print(
                    f"  Suggestion: sudo apt-get install python{sys.version_info.major}.{sys.version_info.minor}-dev")
    except Exception as e:
        print(f"⚠️ Could not check for Python dev headers: {str(e)}")

    # Check for additional dependencies
    try:
        import PIL
        print(f"✅ Pillow is installed (version: {PIL.__version__})")
    except (ImportError, AttributeError):
        print("ℹ️ Pillow is not installed (optional for some SVG operations)")

# Print system information


def print_system_info():
    """Print system information"""
    print_section("System Information")

    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")

    # Environment variables related to Cairo
    print("\nRelevant environment variables:")
    for var in ["LD_LIBRARY_PATH", "PKG_CONFIG_PATH", "PYTHONPATH"]:
        if var in os.environ:
            print(f"  {var}={os.environ[var]}")

    # Print pip packages
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            check=True,
            capture_output=True,
            text=True
        )
        print("\nInstalled packages:")
        packages = result.stdout.splitlines()
        # Filter for relevant packages
        relevant = ["cairo", "pycairo", "cairocffi", "cairosvg",
                    "pillow", "lxml", "cssselect", "tinycss", "defusedxml"]
        print("  Package       | Version")
        print("  ------------- | -------")
        for line in packages:
            if any(r.lower() in line.lower() for r in relevant):
                parts = line.split()
                if len(parts) >= 2:
                    name, version = parts[0], parts[1]
                    print(f"  {name:<13} | {version}")
    except Exception as e:
        print(f"⚠️ Could not get installed packages: {str(e)}")

# Test endless glyph system conversion if available


def test_endless_glyph():
    """Test PNG conversion in endless glyph system if available"""
    print_section("Endless Glyph System Test")

    # Check if endless_glyph_generator.py exists
    glyph_path = SCRIPT_DIR / "endless_glyph_generator.py"
    if not glyph_path.exists():
        print(f"ℹ️ Endless glyph system not found at {glyph_path}")
        return

    print(f"✅ Found endless glyph system at {glyph_path}")

    # Try to import the module
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        import endless_glyph_generator
        print(f"✅ Successfully imported endless_glyph_generator module")

        # Try to generate a glyph
        try:
            output_path = DEBUG_DIR / "test_glyph"
            glyph = endless_glyph_generator.generate_glyph(
                theme="quantum",
                output_path=output_path,
                size=128,
                animate=True
            )

            if glyph:
                print(f"✅ Successfully generated glyph: {output_path}.svg")
                # Check if PNG was also generated
                if (output_path.with_suffix('.png')).exists():
                    print(f"✅ Successfully generated PNG: {output_path}.png")
                else:
                    print(f"❌ PNG was not generated")
        except Exception as e:
            print(f"❌ Error generating glyph: {str(e)}")
            traceback.print_exc()
    except ImportError as e:
        print(f"❌ Failed to import endless_glyph_generator: {str(e)}")

# Identify potential issues


def identify_issues(has_cairosvg, direct_conversion, bytesio_conversion, module_conversion):
    """Identify potential issues based on test results"""
    print_section("Issue Diagnosis")

    issues = []
    fixes = []

    if not has_cairosvg:
        issues.append("CairoSVG is not installed")
        fixes.append("Install CairoSVG: pip install cairosvg")

    if has_cairosvg and not (direct_conversion or bytesio_conversion or module_conversion):
        issues.append("CairoSVG is installed but all conversion methods failed")
        fixes.append("Try installing cairocffi: pip install cairocffi")

        # Check system-specific issues
        system = platform.system()
        if system == "Linux":
            issues.append("Missing system dependencies for Cairo")
            if os.path.exists("/etc/debian_version"):
                fixes.append(
                    "Install Cairo development files: sudo apt-get install libcairo2-dev")
            elif os.path.exists("/etc/redhat-release"):
                fixes.append(
                    "Install Cairo development files: sudo yum install cairo-devel")
        elif system == "Darwin":  # macOS
            issues.append("Missing Cairo on macOS")
            fixes.append("Install Cairo: brew install cairo")
        elif system == "Windows":
            issues.append("Cairo configuration issue on Windows")
            fixes.append("Try using cairocffi instead: pip install cairocffi")

    if not direct_conversion and bytesio_conversion:
        issues.append("Direct file conversion failed but BytesIO conversion worked")
        fixes.append("Use BytesIO method for conversions in your code")

    if not module_conversion and (direct_conversion or bytesio_conversion):
        issues.append("Module conversion failed but direct CairoSVG conversion worked")
        fixes.append("Check for errors in maybe_export_png implementation")

    # Print issues and fixes
    if issues:
        print("Identified Issues:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")

        print("\nSuggested Fixes:")
        for i, fix in enumerate(fixes, 1):
            print(f"{i}. {fix}")
    else:
        print("✅ No issues identified! All tests passed.")


def generate_report(filename="png_debug_report.txt"):
    """Generate a comprehensive debug report"""
    print_section("Generating Debug Report")

    report_path = DEBUG_DIR / filename

    # Capture output to both console and file
    original_stdout = sys.stdout

    with open(report_path, 'w') as f:
        class TeeOutput:
            def write(self, data):
                original_stdout.write(data)
                f.write(data)

            def flush(self):
                original_stdout.flush()
                f.flush()

        sys.stdout = TeeOutput()

        # Run all tests and capture results
        print_section("StrategyDECK PNG Conversion Debug Report")
        print(f"Generated at: {import_time().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"System: {platform.platform()}")
        print(f"Python: {sys.version}")

        has_cairosvg = check_cairosvg()
        direct = test_direct_conversion()
        bytesio = test_bytesio_conversion()
        module = test_module_conversion()

        check_system_deps()
        print_system_info()
        test_endless_glyph()

        identify_issues(has_cairosvg, direct, bytesio, module)

        # Reset stdout
        sys.stdout = original_stdout

    print(f"Debug report generated: {report_path}")
    return report_path


def import_time():
    """Import time module and return current time"""
    import datetime
    return datetime.datetime.now()

# Main function


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Debug SVG to PNG conversion issues in StrategyDECK"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate a comprehensive debug report"
    )
    parser.add_argument(
        "--endless-glyph",
        action="store_true",
        help="Test endless glyph system specifically"
    )
    parser.add_argument(
        "--test-file",
        type=str,
        help="Test conversion with a specific SVG file"
    )

    args = parser.parse_args()

    print("=" * 60)
    print(" StrategyDECK PNG Conversion Debug Tool ".center(60, "="))
    print("=" * 60)

    print(f"Debug directory: {DEBUG_DIR}")

    # Test specific file if provided
    if args.test_file:
        test_file = Path(args.test_file)
        if not test_file.exists():
            print(f"Error: File not found: {test_file}")
            return

        print(f"\nTesting conversion of specific file: {test_file}")
        try:
            import cairosvg
            output_path = DEBUG_DIR / f"{test_file.stem}_test.png"

            cairosvg.svg2png(
                url=str(test_file),
                write_to=str(output_path)
            )
            print(f"✅ Successfully converted to PNG: {output_path}")
        except ImportError:
            print("❌ CairoSVG not available")
        except Exception as e:
            print(f"❌ Error during conversion: {str(e)}")
            traceback.print_exc()
        return

    # Generate full report if requested
    if args.report:
        report_path = generate_report()
        print(f"\nFull debug report generated: {report_path}")
        return

    # Test endless glyph system specifically
    if args.endless_glyph:
        test_endless_glyph()
        return

    # Run all tests by default
    has_cairosvg = check_cairosvg()
    direct = test_direct_conversion()
    bytesio = test_bytesio_conversion()
    module = test_module_conversion()

    check_system_deps()
    identify_issues(has_cairosvg, direct, bytesio, module)

    print("\nFor more detailed information, run with --report flag")


if __name__ == "__main__":
    main()
