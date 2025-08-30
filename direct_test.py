#!/usr/bin/env python3
"""
Simple test script for cairosvg with explicit Python path
"""

import subprocess
import sys
from pathlib import Path

# Use explicit Python path from virtual environment
venv_python = Path("/workspaces/epochcore_RAS/venv/bin/python")

# Create output directory
output_dir = Path("/workspaces/epochcore_RAS/assets/debug")
output_dir.mkdir(parents=True, exist_ok=True)

# Create a simple test SVG
test_svg = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
    <rect width="100" height="100" fill="#FF6A00"/>
    <circle cx="50" cy="50" r="40" fill="#FFFFFF"/>
</svg>
"""

# Save test SVG
test_svg_path = output_dir / "direct_test.svg"
test_svg_path.write_text(test_svg)
print(f"Created test SVG at {test_svg_path}")

# Create a test Python script
test_script = """
import sys
print(f"Python: {sys.executable}")
try:
    import cairosvg
    print(f"CairoSVG version: {cairosvg.__version__}")
    from PIL import Image
    print(f"Pillow imported successfully")
    
    # Convert SVG to PNG
    svg_path = r"{0}"
    png_path = r"{1}"
    cairosvg.svg2png(url=svg_path, write_to=png_path)
    print(f"Conversion successful: {{png_path}}")
except Exception as e:
    print(f"Error: {{e}}")
    import traceback
    traceback.print_exc()
"""

test_script = test_script.format(
    str(test_svg_path),
    str(test_svg_path.with_suffix(".png"))
)

test_script_path = output_dir / "test_script.py"
test_script_path.write_text(test_script)
print(f"Created test script at {test_script_path}")

# Run the script with the virtual environment Python
cmd = [str(venv_python), str(test_script_path)]
print(f"Running: {' '.join(cmd)}")

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Error: {result.stderr}")
except subprocess.CalledProcessError as e:
    print(f"Process error: {e}")
    print(f"Output: {e.stdout}")
    print(f"Error: {e.stderr}")
except Exception as e:
    print(f"Exception: {e}")
