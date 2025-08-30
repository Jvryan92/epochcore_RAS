#!/usr/bin/env python3
"""
Debug Bake SVG (CLI Version)

A command-line version of the SVG color replacement debugging tool
for the StrategyDECK Icon Generation System. This script can test
the color replacement process without requiring tkinter.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "scripts"))

try:
    from generate_icons import FINISH_COLORS, TOKENS, bake_svg, pick_master
except ImportError:
    print("Error: Could not import generate_icons module. Using fallbacks.")

    # Define fallbacks for testing
    TOKENS = {
        "paper": "#FFFFFF",
        "slate_950": "#060607",
        "brand_orange": "#FF6A00",
        "ink": "#000000",
        "copper": "#B87333",
        "burnt_orange": "#CC5500",
        "matte": "#333333",
        "embossed": "#F5F5F5",
    }

    FINISH_COLORS = {
        "flat-orange": "#FF6A00",
        "matte-carbon": "#333333",
        "satin-black": "#000000",
        "burnt-orange": "#CC5500",
        "copper-foil": "#B87333",
        "embossed-paper": "#F5F5F5",
    }

    def bake_svg(master_svg: str, mode: str, finish: str) -> str:
        """Fallback implementation of bake_svg"""
        bg = TOKENS["paper"] if mode == "light" else TOKENS["slate_950"]
        fg = FINISH_COLORS.get(finish, TOKENS["brand_orange"])
        svg = master_svg.replace("#FF6A00", bg)  # replace background rect
        svg = svg.replace("#FFFFFF", fg)  # replace icon shapes
        return svg

    def pick_master(size_px: int) -> Path:
        """Fallback implementation of pick_master"""
        return Path("assets/masters/strategy_icon_micro.svg")

# Directory setup
ROOT_DIR = SCRIPT_DIR
ASSETS_DIR = ROOT_DIR / "assets"
MASTERS_DIR = ASSETS_DIR / "masters"
OUTPUT_DIR = ASSETS_DIR / "debug"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ColorReplacementStep:
    """Represents a single step in the color replacement process"""

    def __init__(self, original: str, replacement: str, description: str):
        self.original = original
        self.replacement = replacement
        self.description = description

    def __str__(self) -> str:
        return f"{self.original} → {self.replacement}: {self.description}"


def apply_replacements(svg_content: str, mode: str, finish: str) -> tuple:
    """Apply color replacements and track steps"""
    if not svg_content:
        return "", []

    # Start with original content
    content = svg_content
    replacement_steps = []

    # Determine background and foreground colors
    bg_color = TOKENS["paper"] if mode == "light" else TOKENS["slate_950"]
    fg_color = FINISH_COLORS.get(finish, TOKENS["brand_orange"])

    # Replace background color (#FF6A00)
    replacement_steps.append(
        ColorReplacementStep("#FF6A00", bg_color, "Background replacement")
    )
    content = content.replace("#FF6A00", bg_color)

    # Replace foreground color (#FFFFFF)
    replacement_steps.append(
        ColorReplacementStep("#FFFFFF", fg_color, "Foreground replacement")
    )
    content = content.replace("#FFFFFF", fg_color)

    return content, replacement_steps


def export_report(output_path: Path, master_svg_path: Path, master_content: str,
                  baked_content: str, mode: str, finish: str, steps: list) -> None:
    """Export a debugging report"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("StrategyDECK SVG Debug Report\n")
        f.write("============================\n\n")

        f.write(f"Master SVG: {master_svg_path}\n")
        f.write(f"Mode: {mode}\n")
        f.write(f"Finish: {finish}\n\n")

        f.write("Color Replacement Steps:\n")
        for i, step in enumerate(steps, 1):
            f.write(f"  {i}. {step.original} → {step.replacement}: {step.description}\n")
        f.write("\n")

        f.write("Original SVG Content:\n")
        f.write("---------------------\n")
        f.write(master_content[:1000])
        if len(master_content) > 1000:
            f.write("...\n")
        f.write("\n\n")

        f.write("Baked SVG Content:\n")
        f.write("------------------\n")
        f.write(baked_content[:1000])
        if len(baked_content) > 1000:
            f.write("...\n")

    print(f"Exported debug report to {output_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Debug SVG baking process (CLI version)")
    parser.add_argument("--svg", help="Path to SVG file to debug", required=True)
    parser.add_argument(
        "--mode", choices=["light", "dark"], default="light", help="Icon mode")
    parser.add_argument("--finish", default="flat-orange", help="Icon finish")
    parser.add_argument("--output", help="Output path for baked SVG")
    parser.add_argument("--report", help="Output path for debug report")

    args = parser.parse_args()

    svg_path = Path(args.svg)
    if not svg_path.exists():
        print(f"Error: SVG file not found: {svg_path}")
        return 1

    try:
        # Load SVG
        with open(svg_path, "r", encoding="utf-8") as f:
            master_svg = f.read()

        # Apply replacements using our own function
        baked_svg, steps = apply_replacements(master_svg, args.mode, args.finish)

        # Also try the bake_svg function if available
        try:
            module_baked_svg = bake_svg(master_svg, args.mode, args.finish)
            print("Used bake_svg function from generate_icons module")
        except Exception as e:
            module_baked_svg = baked_svg
            print(f"Warning: Could not use bake_svg function: {e}")

        # Print replacement steps
        print("\nColor Replacement Steps:")
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")

        # Save output or print to console
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(module_baked_svg)

            print(f"\nBaked SVG saved to {output_path}")
        else:
            print("\nBaked SVG Content:")
            print("------------------")
            print(module_baked_svg[:200] +
                  "..." if len(module_baked_svg) > 200 else module_baked_svg)

        # Export report if requested
        if args.report:
            report_path = Path(args.report)
            export_report(
                report_path, svg_path, master_svg, module_baked_svg,
                args.mode, args.finish, steps
            )

        return 0

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
