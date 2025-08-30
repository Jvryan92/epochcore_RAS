#!/usr/bin/env python3
"""
StrategyDECK Glyph System Setup

This script checks and installs the required dependencies for the
StrategyDECK Endless Glyph Generation System.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path


def check_package(package_name):
    """Check if a Python package is installed"""
    return importlib.util.find_spec(package_name) is not None


def install_package(package_name):
    """Install a Python package using pip"""
    print(f"Installing {package_name}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])


def main():
    """Main entry point"""
    print("=" * 60)
    print(" StrategyDECK Endless Glyph System Setup ".center(60, "="))
    print("=" * 60)

    # Check for required packages
    required_packages = {
        "cairosvg": "Required for PNG conversion",
        "pillow": "Required for image processing",
        "cssselect": "Helpful for advanced SVG manipulation",
        "tinycss": "Helpful for CSS in SVG"
    }

    print("\nChecking for required packages...")
    missing_packages = []

    for package, description in required_packages.items():
        if check_package(package.lower()):
            print(f"✅ {package} - Installed")
        else:
            print(f"❌ {package} - Missing ({description})")
            missing_packages.append(package)

    # Install missing packages
    if missing_packages:
        print("\nThe following packages need to be installed:")
        for package in missing_packages:
            print(f"  - {package}: {required_packages[package]}")

        install_all = input(
            "\nInstall all missing packages? (y/n): ").lower().strip() == "y"

        if install_all:
            for package in missing_packages:
                try:
                    install_package(package)
                    print(f"✅ {package} installed successfully")
                except Exception as e:
                    print(f"❌ Failed to install {package}: {str(e)}")
        else:
            print("\nPackages not installed. You can install them manually with:")
            print(f"pip install {' '.join(missing_packages)}")
    else:
        print("\nAll required packages are already installed!")

    # Check for glyph generator script
    script_path = Path(__file__).parent / "scripts" / "endless_glyph_generator.py"
    if script_path.exists():
        print("\n✅ Endless Glyph Generator script found")
    else:
        print("\n❌ Endless Glyph Generator script not found at:")
        print(f"   {script_path}")
        print("   Make sure the script exists before running the system")

    # Print next steps
    print("\n" + "=" * 60)
    print(" Setup Complete ".center(60, "="))
    print("=" * 60)

    print("\nNext Steps:")
    print("1. Generate glyphs with the demo script:")
    print("   python glyph_demo.py --all-themes")
    print("2. Try a specific theme:")
    print("   python glyph_demo.py --theme cosmic --complexity 3")
    print("3. Generate random variations:")
    print("   python glyph_demo.py --count 10")
    print("\nFor more information, see the documentation:")
    print("docs/ENDLESS_GLYPH_SYSTEM.md")
    print("docs/ENDLESS_GLYPH_SYSTEM_README.md")


if __name__ == "__main__":
    main()
