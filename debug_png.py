#!/usr/bin/env python3
"""
Debug PNG conversion
"""

import sys
from pathlib import Path

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from generate_icons import maybe_export_png
except ImportError:
    print("Error: Could not import from generate_icons.py")
    print("Make sure generate_icons.py exists in the scripts directory")
    sys.exit(1)

# Simple test SVG
test_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <rect x="10" y="10" width="80" height="80" fill="#FF0000" />
</svg>"""

# Test paths
output_dir = Path(ROOT) / "assets" / "debug"
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "test.png"

print(f"SCRIPT_DIR: {SCRIPT_DIR}")
print(f"ROOT: {ROOT}")
print(f"Output directory: {output_dir}")
print(f"Output path: {output_path}")

print("\nTesting PNG conversion:")
try:
    # Try to convert SVG to PNG
    result = maybe_export_png(test_svg.encode("utf-8"), output_path, 100)
    print(f"PNG conversion result: {result}")

    if result:
        print(f"PNG file created: {output_path.exists()}")
    else:
        print("PNG conversion failed")

    # Try directly with cairosvg
    print("\nTrying with cairosvg directly:")
    try:
        import cairosvg
        print("CairoSVG imported successfully")

        # Make sure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Try conversion
        cairosvg.svg2png(
            bytestring=test_svg.encode("utf-8"),
            write_to=str(output_path),
            output_width=100,
            output_height=100,
        )
        print(f"Direct conversion successful: {output_path.exists()}")
    except Exception as e:
        print(f"Error with direct cairosvg conversion: {e}")

except Exception as e:
    print(f"Error: {e}")
