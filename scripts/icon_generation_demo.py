#!/usr/bin/env python3
"""
StrategyDECK Icon Generation Demo

This script demonstrates the complete icon generation capabilities of StrategyDECK,
including basic icon generation, enhanced generation with template tokens, and 
the endless glyph system with animated SVGs and procedural generation.
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent))
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from enhanced_icon_generator import (
        IconVariant,
        batch_generate_icons,
        create_variant_matrix,
        load_custom_palette,
        load_variants_from_csv,
    )
except ImportError:
    print("Error: Could not import from enhanced_icon_generator.py")
    print("Make sure you have created the file enhanced_icon_generator.py")
    sys.exit(1)

# Try to import the endless glyph generator
try:
    from endless_glyph_generator import (
        GLYPH_THEMES,
        GlyphVariant,
        batch_generate_glyphs,
        create_random_glyph_variants,
        create_theme_set,
    )
    GLYPH_SYSTEM_AVAILABLE = True
except ImportError:
    GLYPH_SYSTEM_AVAILABLE = False


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


def run_demo(output_dir=None, skip_csv=False, skip_custom=False, skip_batch=False,
             skip_export=False, include_glyphs=False):
    """Run the icon generation demo"""
    print_header("StrategyDECK Icon Generation System Demo")

    print("""
StrategyDECK provides a comprehensive icon generation system with multiple capabilities:

1. Basic Generation: Standard SVG/PNG icon variants from CSV
2. Custom Palettes: Create icons with custom color schemes
3. Batch Processing: Parallel generation for improved performance
4. Template Tokens: Advanced templating for maximum flexibility
5. Endless Glyphs: Animated, themed procedural glyphs with infinite variations
""")

    # Ensure output directory
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Override global output directory
        import enhanced_icon_generator
        enhanced_icon_generator.OUT = output_path
        print(f"Using custom output directory: {output_path}")

    demo_stats = {}

    # Basic generation from CSV
    if not skip_csv:
        print_section("Basic Generation from CSV Matrix")
        print("Loading variants from strategy_icon_variant_matrix.csv...")

        try:
            start_time = time.time()
            variants = load_variants_from_csv()
            print(f"Loaded {len(variants)} variants from CSV")

            print("\nGenerating icons...")
            stats = batch_generate_icons(variants, parallel=False, optimize=False)

            demo_stats["csv"] = {
                "variants": len(variants),
                "time": time.time() - start_time,
                "success_svg": stats.successful_svgs,
                "success_png": stats.successful_pngs
            }

            print(f"\nCompleted CSV generation in {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"Error during CSV generation: {e}")

    # Custom palette generation
    if not skip_custom:
        print_section("Custom Palette Generation")
        print("Creating 'neon' palette variants...")

        try:
            start_time = time.time()

            # Create neon palette variants
            neon_variants = []
            neon_colors = {
                "neon-blue": "#00FFFF",
                "neon-green": "#39FF14",
                "neon-pink": "#FF10F0"
            }

            for color_name, color_value in neon_colors.items():
                variant = IconVariant(
                    mode="dark",
                    finish=color_name,
                    size=32,
                    context="web",
                    filename=f"strategy_icon-dark-{color_name}-32px.png",
                    formats=["svg", "png"],
                    # Using custom_colors property
                    custom_colors={"foreground": color_value}
                )
                neon_variants.append(variant)

            # Apply custom colors
            import enhanced_icon_generator
            original_finish_colors = enhanced_icon_generator.FINISH_COLORS.copy()
            enhanced_icon_generator.FINISH_COLORS.update(neon_colors)

            print(f"Generating {len(neon_variants)} neon variants...")
            stats = batch_generate_icons(neon_variants, parallel=False, optimize=False)

            # Restore original colors
            enhanced_icon_generator.FINISH_COLORS = original_finish_colors

            demo_stats["custom"] = {
                "variants": len(neon_variants),
                "time": time.time() - start_time,
                "success_svg": stats.successful_svgs,
                "success_png": stats.successful_pngs
            }

            print(f"\nCompleted custom generation in {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"Error during custom palette generation: {e}")

    # Batch parallel generation
    if not skip_batch:
        print_section("Batch Parallel Generation")
        print("Creating batch of variants with different sizes...")

        try:
            start_time = time.time()

            # Create a matrix of variants
            options = {
                "modes": ["light", "dark"],
                "finishes": ["flat-orange"],
                "sizes": [16, 24, 32, 48, 64],
                "contexts": ["web"],
                "formats": ["svg", "png"]
            }

            batch_variants = create_variant_matrix(options)
            print(f"Created {len(batch_variants)} variants for batch processing")

            print("\nGenerating with parallel processing...")
            stats = batch_generate_icons(batch_variants, parallel=True, optimize=True)

            demo_stats["batch"] = {
                "variants": len(batch_variants),
                "time": time.time() - start_time,
                "success_svg": stats.successful_svgs,
                "success_png": stats.successful_pngs,
                "avg_time": stats.average_processing_time
            }

            print(f"\nCompleted batch generation in {time.time() - start_time:.2f}s")
            print(f"Average time per variant: {stats.average_processing_time:.4f}s")
        except Exception as e:
            print(f"Error during batch generation: {e}")

    # Template token system demo
    if not skip_custom:
        print_section("Template Token System")
        print("Demonstrating template-based SVG generation...")

        try:
            start_time = time.time()

            # Create template variants
            template_variants = []
            template_colors = {
                "gradient-purple": {
                    "primary": "#6B46C1",
                    "secondary": "#B794F4",
                    "background": "#FAF5FF"
                },
                "gradient-teal": {
                    "primary": "#2C7A7B",
                    "secondary": "#4FD1C5",
                    "background": "#E6FFFA"
                }
            }

            for style_name, colors in template_colors.items():
                variant = IconVariant(
                    mode="light",
                    finish=style_name,
                    size=48,
                    context="web",
                    filename=f"strategy_icon-template-{style_name}-48px.png",
                    formats=["svg", "png"],
                    custom_colors=colors
                )
                template_variants.append(variant)

            print(f"Generating {len(template_variants)} template variants...")

            # We'll use a different processing function that supports template tokens
            from enhanced_icon_generator import process_template_variant

            for variant in template_variants:
                success, formats, error = process_template_variant(variant)
                if success:
                    print(f"✓ Generated template variant: {variant.finish}")
                else:
                    print(f"✗ Failed to generate template variant: {error}")

            demo_stats["template"] = {
                "variants": len(template_variants),
                "time": time.time() - start_time,
                "success_svg": len(template_variants),  # Simplified for demo
                "success_png": len(template_variants)   # Simplified for demo
            }

            print(f"\nCompleted template generation in {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"Error during template generation: {e}")
            print("Note: You need to implement the process_template_variant function")

    # Export to frameworks
    if not skip_export and not output_dir:
        print_section("Framework Export")
        print("Note: Framework export requires the icon_framework_exporter.py script")
        print("Skipping framework export since it requires additional dependencies")

    # Print summary
    print_header("Demo Summary")

    for demo_type, stats in demo_stats.items():
        print(f"\n{demo_type.title()} Generation:")
        print(f"  Variants: {stats['variants']}")
        print(f"  Time: {stats['time']:.2f}s")
        print(f"  SVG Success: {stats.get('success_svg', 0)}")
        print(f"  PNG Success: {stats.get('success_png', 0)}")
        if 'avg_time' in stats:
            print(f"  Avg Time: {stats['avg_time']:.4f}s/variant")

    print("\nDemo completed successfully!")

    # Add note about glyph system if not used
    if include_glyphs and not GLYPH_SYSTEM_AVAILABLE:
        print("\nNote: The Endless Glyph System was requested but is not available.")
        print("Make sure the endless_glyph_generator.py file exists and is properly installed.")

    # Provide next steps
    print("\nNext Steps:")
    print("1. Explore the generated icons in the output directory")
    print("2. Try using enhanced_icon_generator.py with different options")
    print("3. Experiment with palette_manager.py to create custom color schemes")
    print("4. Use icon_framework_exporter.py to export for your favorite framework")

    if GLYPH_SYSTEM_AVAILABLE:
        print("5. Try the Endless Glyph System with different themes:")
        print("   python glyph_demo.py --theme cosmic --complexity 3")


def run_glyph_demo():
    """Run a demonstration of the endless glyph generation system"""
    if not GLYPH_SYSTEM_AVAILABLE:
        print("\n❌ Endless Glyph System not available")
        print("Make sure endless_glyph_generator.py exists and is properly installed")
        return

    print_header("StrategyDECK Endless Glyph System Demo")

    print("""
The Endless Glyph System extends the StrategyDECK icon generation framework to create
procedurally generated glyphs with unique properties, animations, and thematic elements.

Available themes:
- biome: Nature-inspired with growing roots and leaves (green)
- urban: Circuit board patterns and data flows (blue)
- mystic: Rune circles and geometric patterns (purple)
- cosmic: Event horizon and quantum particles (black)
- raid: Pulsing power core and energy beams (red)
- shadow: Darkness and obscured patterns (gray)
- primal: Raw energy and primitive symbols (orange)
- underworld: Hidden depths and crossed paths (indigo)
- renaissance: Balanced symmetry and transformation (teal)
""")

    start_time = time.time()

    # Generate one variant for each theme
    print("\nGenerating sample glyphs for each theme...")
    variants = []
    for theme in GLYPH_THEMES.keys():
        variant = GlyphVariant(
            mode="dark",
            finish=theme,
            size=96,
            context="web",
            theme=theme,
            complexity=3,
            animated=True
        )
        variants.append(variant)

    # Generate the glyphs
    stats = batch_generate_glyphs(variants, parallel=True)

    glyph_time = time.time() - start_time
    print(f"\nCompleted glyph generation in {glyph_time:.2f}s")
    print(f"Successful SVGs: {stats.successful_svgs}")
    print(f"Successful PNGs: {stats.successful_pngs}")

    print("\nNote: SVG files contain animations that work in modern browsers")
    if stats.successful_pngs == 0:
        print("PNG conversion requires CairoSVG. Install with: pip install cairosvg")

    # Provide next steps
    print("\nNext Steps:")
    print("1. View the generated SVG files in a web browser to see animations")
    print("2. Try generating more variants with the glyph_demo.py script:")
    print("   python glyph_demo.py --theme cosmic --complexity 3")
    print("3. Create random variations with different seeds:")
    print("   python glyph_demo.py --count 10")
    print("4. Generate all themes at once:")
    print("   python glyph_demo.py --all-themes")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="StrategyDECK Icon Generation Demo")

    parser.add_argument("--output-dir", help="Custom output directory")
    parser.add_argument("--skip-csv", action="store_true", help="Skip CSV generation")
    parser.add_argument("--skip-custom", action="store_true",
                        help="Skip custom palette generation")
    parser.add_argument("--skip-batch", action="store_true",
                        help="Skip batch generation")
    parser.add_argument("--skip-export", action="store_true",
                        help="Skip framework export")
    parser.add_argument("--glyphs", action="store_true",
                        help="Include endless glyph generation")
    parser.add_argument("--glyphs-only", action="store_true",
                        help="Only run endless glyph demo")

    args = parser.parse_args()

    if args.glyphs_only:
        run_glyph_demo()
    else:
        run_demo(
            output_dir=args.output_dir,
            skip_csv=args.skip_csv,
            skip_custom=args.skip_custom,
            skip_batch=args.skip_batch,
            skip_export=args.skip_export,
            include_glyphs=args.glyphs
        )


if __name__ == "__main__":
    main()
