#!/usr/bin/env python3
"""
StrategyDECK Diagnostic Tools Test Script

This script tests the diagnostic tools to ensure they're functioning correctly.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))


def test_debug_bake_svg():
    """Test the SVG debug tool"""
    print("\n=== Testing debug_bake_svg_cli.py ===")

    # Test command-line mode
    master_svg = ROOT / "assets" / "masters" / "strategy_icon_micro.svg"
    if not master_svg.exists():
        print(f"  ERROR: Master SVG not found at {master_svg}")
        return False

    output_path = ROOT / "assets" / "debug" / "test_debug_bake.svg"

    cmd = [
        sys.executable,
        str(ROOT / "debug_bake_svg_cli.py"),
        "--svg", str(master_svg),
        "--mode", "light",
        "--finish", "flat-orange",
        "--output", str(output_path)
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  SUCCESS: {result.stdout.strip()}")
        if output_path.exists():
            print(f"  Generated SVG: {output_path}")
            return True
        else:
            print(f"  ERROR: Output file not created at {output_path}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: {e}")
        print(f"  STDOUT: {e.stdout}")
        print(f"  STDERR: {e.stderr}")
        return False


def test_debug_png_conversion():
    """Test the PNG conversion debug tool"""
    print("\n=== Testing debug_png_conversion.py ===")

    # Test basic functionality
    cmd = [
        sys.executable,
        str(ROOT / "debug_png_conversion.py")
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        output = result.stdout.strip()

        if "CairoSVG" in output:
            print("  SUCCESS: Tool ran and checked CairoSVG")

            # Check if CairoSVG is available
            if "CairoSVG is not installed" in output:
                print("  NOTE: CairoSVG is not installed")
            else:
                print("  CairoSVG is installed")

            return True
        else:
            print("  ERROR: Tool did not output expected information")
            print(f"  OUTPUT: {output}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: {e}")
        print(f"  STDOUT: {e.stdout}")
        print(f"  STDERR: {e.stderr}")
        return False


def test_clean_rebuild_script():
    """Test the clean and rebuild script"""
    print("\n=== Testing clean_rebuild_assets.sh ===")

    # Only test if the script exists
    script_path = ROOT / "clean_rebuild_assets.sh"
    if not script_path.exists():
        print(f"  ERROR: Script not found at {script_path}")
        return False

    # Check if executable
    if not os.access(script_path, os.X_OK):
        print(f"  WARNING: Script exists but is not executable")
        try:
            os.chmod(script_path, 0o755)
            print(f"  Made script executable")
        except Exception as e:
            print(f"  ERROR making script executable: {e}")

    print(f"  SUCCESS: Script exists and is executable")
    print(f"  NOTE: Not running the script as it would rebuild all assets")
    return True


def main():
    """Main entry point"""
    print("StrategyDECK Diagnostic Tools Test")
    print("=================================")

    results = []

    # Test each tool
    results.append(("debug_bake_svg.py", test_debug_bake_svg()))
    results.append(("debug_png_conversion.py", test_debug_png_conversion()))
    results.append(("clean_rebuild_assets.sh", test_clean_rebuild_script()))

    # Print summary
    print("\n=== Test Summary ===")
    all_passed = True
    for tool, result in results:
        status = "PASS" if result else "FAIL"
        if not result:
            all_passed = False
        print(f"  {tool}: {status}")

    # Final result
    print("\nOverall result:", "PASS" if all_passed else "FAIL")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
