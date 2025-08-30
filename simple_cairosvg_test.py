#!/usr/bin/env python3
"""
Simple test script for cairosvg
"""

import sys
from pathlib import Path

# Make sure we're using the right Python
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Check path
print(f"sys.path: {sys.path}")

# Try to import cairosvg
try:
    import cairosvg
    print(f"Successfully imported cairosvg (version: {cairosvg.__version__})")
except ImportError as e:
    print(f"Failed to import cairosvg: {e}")
    sys.exit(1)

# Create a simple test SVG
test_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <rect width="100" height="100" fill="#FF6A00"/>
    <circle cx="50" cy="50" r="40" fill="#FFFFFF"/>
</svg>
"""

# Create output directory
output_dir = Path("/workspaces/epochcore_RAS/assets/debug")
output_dir.mkdir(parents=True, exist_ok=True)

# Save the test SVG
test_svg_path = output_dir / "simple_test.svg"
test_svg_path.write_text(test_svg)
print(f"Created test SVG at {test_svg_path}")

# Try to convert to PNG
test_png_path = output_dir / "simple_test.png"
try:
    cairosvg.svg2png(
        bytestring=test_svg.encode('utf-8'),
        write_to=str(test_png_path),
        output_width=100,
        output_height=100
    )
    print(f"Successfully converted to PNG: {test_png_path}")
except Exception as e:
    print(f"Error converting to PNG: {e}")
    import traceback
    traceback.print_exc()
