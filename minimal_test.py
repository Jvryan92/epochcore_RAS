#!/usr/bin/env python3
"""
Minimal direct test for SVG to PNG conversion
"""

import subprocess
from pathlib import Path

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
test_svg_path = output_dir / "minimal_test.svg"
test_svg_path.write_text(test_svg)
print(f"Created test SVG at {test_svg_path}")

# Create a minimal test script
test_script = """
import sys
print(f"Python: {sys.executable}")

try:
    import cairosvg
    print(f"CairoSVG version: {cairosvg.__version__}")
    
    from PIL import Image
    print("PIL imported successfully")
    
    svg_path = r"%s"
    png_path = r"%s"
    
    print(f"Converting {svg_path} to {png_path}")
    cairosvg.svg2png(url=svg_path, write_to=png_path)
    print("Conversion successful!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
"""

# Format with string placeholders
svg_path_str = str(test_svg_path)
png_path_str = str(test_svg_path.with_suffix(".png"))
test_script = test_script % (svg_path_str, png_path_str)

test_script_path = output_dir / "minimal_test.py"
test_script_path.write_text(test_script)
print(f"Created test script at {test_script_path}")

# Run the script with the virtual environment Python
venv_python = "/workspaces/epochcore_RAS/.venv/bin/python3"
cmd = [venv_python, str(test_script_path)]
print(f"Running: {' '.join(cmd)}")

try:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("Process completed successfully")
    print(f"Output:\n{result.stdout}")
    if result.stderr:
        print(f"Error output:\n{result.stderr}")
except subprocess.CalledProcessError as e:
    print(f"Process error (code {e.returncode})")
    print(f"Output:\n{e.stdout}")
    print(f"Error output:\n{e.stderr}")
except Exception as e:
    print(f"Exception: {e}")

# Check if PNG was created
png_path = test_svg_path.with_suffix(".png")
if png_path.exists():
    print(f"SUCCESS: PNG file created at {png_path}")
else:
    print(f"FAILURE: PNG file was not created at {png_path}")
