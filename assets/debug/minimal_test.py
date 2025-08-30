
import sys
print(f"Python: {sys.executable}")

try:
    import cairosvg
    print(f"CairoSVG version: {cairosvg.__version__}")
    
    from PIL import Image
    print("PIL imported successfully")
    
    svg_path = r"/workspaces/epochcore_RAS/assets/debug/minimal_test.svg"
    png_path = r"/workspaces/epochcore_RAS/assets/debug/minimal_test.png"
    
    print(f"Converting {svg_path} to {png_path}")
    cairosvg.svg2png(url=svg_path, write_to=png_path)
    print("Conversion successful!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
