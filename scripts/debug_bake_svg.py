#!/usr/bin/env python3
"""
Debug script to understand how bake_svg works
"""

from generate_icons import FINISH_COLORS, TOKENS, bake_svg
import sys
from pathlib import Path

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))


def main():
    # Create a test SVG
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
    <rect width="24" height="24" fill="#FF6A00"/>
    <circle cx="12" cy="12" r="6" fill="#FFFFFF"/>
    </svg>"""

    print("Original SVG content:")
    print(svg_content)
    print("\nReplacement colors:")
    print(f"Light mode background: {TOKENS['paper']}")
    print(f"Dark mode background: {TOKENS['slate_950']}")
    print(f"Flat-orange foreground: {FINISH_COLORS['flat-orange']}")

    # Bake SVG for light mode
    light_svg = bake_svg(svg_content, "light", "flat-orange")
    print("\nLight mode SVG after baking:")
    print(light_svg)

    # Bake SVG for dark mode
    dark_svg = bake_svg(svg_content, "dark", "flat-orange")
    print("\nDark mode SVG after baking:")
    print(dark_svg)

    # Create another test SVG with different color positions
    svg_content2 = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
    <rect width="24" height="24" fill="{{mode_bg}}"/>
    <circle cx="12" cy="12" r="6" fill="{{accent}}"/>
    </svg>"""

    print("\nAlternative SVG with template tokens:")
    print(svg_content2)

    # Try to bake with template tokens - this likely won't work with the current implementation
    template_svg = bake_svg(svg_content2, "light", "flat-orange")
    print("\nTemplate SVG after baking (likely unchanged):")
    print(template_svg)


if __name__ == "__main__":
    main()
