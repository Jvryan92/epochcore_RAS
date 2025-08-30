#!/usr/bin/env python3
"""
StrategyDECK Endless Glyph Demo

This script demonstrates the StrategyDECK endless glyph generation system 
by creating various themed glyphs with different properties and animations.
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from scripts.endless_glyph_generator import (
        GLYPH_THEMES,
        GlyphVariant,
        batch_generate_glyphs,
        create_complete_glyph_set,
        create_random_glyph_variants,
        create_theme_set,
    )
except ImportError:
    print("Error: Could not import from endless_glyph_generator.py")
    print("Make sure you have created the file scripts/endless_glyph_generator.py")
    sys.exit(1)


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "="))
    print("=" * 60)


def print_section(title):
    """Print a formatted section title"""
    print("\n" + "-" * 50)
    print(f" {title} ".center(50))
    print("-" * 50)


def run_demo(output_dir=None, theme=None, count=5, complexity=2, all_themes=False):
    """Run the endless glyph generation demo"""
    print_header("StrategyDECK Endless Glyph Demo")

    # Ensure output directory
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Override global output directory
        from scripts.endless_glyph_generator import OUT as GLYPH_OUT
        globals()["OUT"] = output_path
        GLYPH_OUT = output_path
        print(f"Using custom output directory: {output_path}")

    demo_stats = {}

    # Generate specific theme set
    if theme:
        print_section(f"Generating {theme.title()} Theme Glyphs")

        try:
            start_time = time.time()
            variants = create_theme_set(theme, sizes=[64, 96])
            print(f"Created {len(variants)} variants for {theme} theme")

            print("\nGenerating glyphs...")
            stats = batch_generate_glyphs(variants, parallel=True, optimize=False)

            demo_stats[theme] = {
                "variants": len(variants),
                "time": time.time() - start_time,
                "success_svg": stats.successful_svgs,
                "success_png": stats.successful_pngs
            }

            print(
                f"\nCompleted {theme} theme generation in {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"Error during {theme} theme generation: {e}")

    # Generate random glyphs
    if not theme and not all_themes:
        print_section("Generating Random Glyphs")

        try:
            start_time = time.time()
            variants = create_random_glyph_variants(count)
            print(f"Created {len(variants)} random glyph variants")

            print("\nGenerating glyphs...")
            stats = batch_generate_glyphs(variants, parallel=True, optimize=False)

            demo_stats["random"] = {
                "variants": len(variants),
                "time": time.time() - start_time,
                "success_svg": stats.successful_svgs,
                "success_png": stats.successful_pngs
            }

            print(
                f"\nCompleted random glyph generation in {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"Error during random glyph generation: {e}")

    # Generate all themes
    if all_themes:
        print_section("Generating All Theme Glyphs")

        try:
            start_time = time.time()

            # We'll generate a simplified set to keep the demo quick
            variants = []
            for theme_name in GLYPH_THEMES.keys():
                # Just create one glyph per theme to demonstrate
                variant = GlyphVariant(
                    mode="dark",
                    finish=theme_name,
                    size=96,
                    context="web",
                    theme=theme_name,
                    complexity=complexity,
                    animated=True
                )
                variants.append(variant)

            print(f"Created {len(variants)} theme variants")

            print("\nGenerating glyphs...")
            stats = batch_generate_glyphs(variants, parallel=True, optimize=False)

            demo_stats["all_themes"] = {
                "variants": len(variants),
                "time": time.time() - start_time,
                "success_svg": stats.successful_svgs,
                "success_png": stats.successful_pngs
            }

            print(
                f"\nCompleted all themes generation in {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"Error during all themes generation: {e}")

    # Print summary
    print_header("Demo Summary")

    for demo_type, stats in demo_stats.items():
        print(f"\n{demo_type.title()} Generation:")
        print(f"  Variants: {stats['variants']}")
        print(f"  Time: {stats['time']:.2f}s")
        print(f"  SVG Success: {stats.get('success_svg', 0)}")
        print(f"  PNG Success: {stats.get('success_png', 0)}")

    print("\nDemo completed successfully!")

    # Note about PNG conversion
    print("\nNote: If PNG conversion failed, you can still view the SVG files directly.")
    print("PNG conversion requires CairoSVG which may not be installed in your environment.")
    print("Install with: pip install cairosvg")

    # Provide next steps
    print("\nNext Steps:")
    print("1. Explore the generated glyphs in the output directory")
    print("2. Try creating glyphs with different themes using --theme")
    print("3. Experiment with complexity levels using --complexity")
    print("4. Generate a full set of all themes with --all-themes")
    print("5. Create random variations with --count")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="StrategyDECK Endless Glyph Demo")

    parser.add_argument("--output-dir", help="Custom output directory")
    parser.add_argument("--theme", choices=GLYPH_THEMES.keys(),
                        help="Generate specific theme")
    parser.add_argument("--count", type=int, default=5,
                        help="Number of random glyphs to generate")
    parser.add_argument("--complexity", type=int,
                        choices=[1, 2, 3], default=2, help="Complexity level")
    parser.add_argument("--all-themes", action="store_true", help="Generate all themes")

    args = parser.parse_args()

    run_demo(
        output_dir=args.output_dir,
        theme=args.theme,
        count=args.count,
        complexity=args.complexity,
        all_themes=args.all_themes
    )


if __name__ == "__main__":
    main()
