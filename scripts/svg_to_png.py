#!/usr/bin/env python3
"""
SVG to PNG Conversion Script

This script provides a fallback method for converting SVG files to PNG
when cairosvg is not available. It uses external tools like Inkscape,
rsvg-convert, or ImageMagick.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def convert_svg_to_png(svg_path, png_path, size):
    """
    Convert an SVG file to PNG using various methods.

    Args:
        svg_path: Path to the SVG file
        png_path: Path to save the PNG file
        size: Size in pixels (width/height)

    Returns:
        bool: True if conversion was successful, False otherwise
    """
    methods = [
        convert_using_inkscape,
        convert_using_rsvg_convert,
        convert_using_imagemagick
    ]

    for method in methods:
        try:
            if method(svg_path, png_path, size):
                return True
        except Exception as e:
            print(f"Method {method.__name__} failed: {e}")

    return False


def convert_using_inkscape(svg_path, png_path, size):
    """Convert using Inkscape CLI"""
    try:
        inkscape_path = shutil.which("inkscape")
        if not inkscape_path:
            print("Inkscape not found")
            return False

        print(f"Using Inkscape at: {inkscape_path}")
        cmd = [
            inkscape_path,
            "--export-filename", png_path,
            "-w", str(size),
            "-h", str(size),
            svg_path
        ]

        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Inkscape error: {result.stderr}")
            return False

        print(f"Successfully converted to: {png_path}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"Inkscape error: {e}")
        return False


def convert_using_rsvg_convert(svg_path, png_path, size):
    """Convert using rsvg-convert"""
    try:
        rsvg_path = shutil.which("rsvg-convert")
        if not rsvg_path:
            print("rsvg-convert not found")
            return False

        print(f"Using rsvg-convert at: {rsvg_path}")
        cmd = [
            rsvg_path,
            "-w", str(size),
            "-h", str(size),
            "-o", png_path,
            svg_path
        ]

        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"rsvg-convert error: {result.stderr}")
            return False

        print(f"Successfully converted to: {png_path}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"rsvg-convert error: {e}")
        return False


def convert_using_imagemagick(svg_path, png_path, size):
    """Convert using ImageMagick"""
    try:
        convert_path = shutil.which("convert")
        if not convert_path:
            print("ImageMagick not found")
            return False

        print(f"Using ImageMagick at: {convert_path}")
        cmd = [
            convert_path,
            "-background", "none",
            "-size", f"{size}x{size}",
            svg_path,
            "-resize", f"{size}x{size}",
            png_path
        ]

        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"ImageMagick error: {result.stderr}")
            return False

        print(f"Successfully converted to: {png_path}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"ImageMagick error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Convert SVG to PNG")
    parser.add_argument("svg_path", help="Path to the SVG file")
    parser.add_argument("png_path", help="Path to save the PNG file")
    parser.add_argument("--size", type=int, default=64, help="Size in pixels")

    args = parser.parse_args()

    success = convert_svg_to_png(args.svg_path, args.png_path, args.size)

    if success:
        print(f"Successfully converted {args.svg_path} to {args.png_path}")
        return 0
    else:
        print(f"Failed to convert {args.svg_path} to {args.png_path}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
