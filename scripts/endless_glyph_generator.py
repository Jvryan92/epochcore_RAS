#!/usr/bin/env python3
"""
Endless Glyph Generator for StrategyDECK

This script extends the StrategyDECK icon generation system to create
procedurally generated glyphs with unique properties, animations,
and thematic elements.

Features:
- Procedural glyph generation with infinite variations
- SVG animation support with CSS and SMIL animations
- Theme-based generation (biome, urban, mystic, cosmic, etc.)
- Custom color palettes for each glyph type
- Multiple glyph complexity levels
- Support for animation export
"""

import argparse
import concurrent.futures
import json
import math
import os
import random
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# Check for CairoSVG availability upfront
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False
    print("Note: CairoSVG is not installed. PNG export will be disabled.")
    print("To enable PNG export, install CairoSVG: pip install cairosvg")

try:
    from enhanced_icon_generator import (
        ASSETS,
        OUT,
        ROOT,
        IconGenerationStats,
        IconVariant,
        batch_generate_icons,
        load_custom_palette,
        process_variant,
    )
    from generate_icons import maybe_export_png
except ImportError:
    print("Error: Could not import from enhanced_icon_generator.py")
    print("Make sure enhanced_icon_generator.py exists in the scripts directory")
    sys.exit(1)

# Define glyph themes with their color palettes
GLYPH_THEMES = {
    "biome": {
        "primary": "#2F855A",    # Green
        "secondary": "#68D391",  # Light green
        "accent": "#F0FFF4",     # Pale green
        "base": "#1C4532"        # Dark green
    },
    "urban": {
        "primary": "#3182CE",    # Blue
        "secondary": "#63B3ED",  # Light blue
        "accent": "#EBF8FF",     # Pale blue
        "base": "#2A4365"        # Dark blue
    },
    "mystic": {
        "primary": "#6B46C1",    # Purple
        "secondary": "#B794F4",  # Light purple
        "accent": "#FAF5FF",     # Pale purple
        "base": "#44337A"        # Dark purple
    },
    "cosmic": {
        "primary": "#1A202C",    # Almost black
        "secondary": "#4A5568",  # Gray
        "accent": "#E2E8F0",     # Light gray
        "base": "#000000"        # Pure black
    },
    "raid": {
        "primary": "#C53030",    # Red
        "secondary": "#FC8181",  # Light red
        "accent": "#FFF5F5",     # Pale red
        "base": "#822727"        # Dark red
    },
    "shadow": {
        "primary": "#4A5568",    # Gray
        "secondary": "#718096",  # Light gray
        "accent": "#F7FAFC",     # Almost white
        "base": "#2D3748"        # Dark gray
    },
    "primal": {
        "primary": "#DD6B20",    # Orange
        "secondary": "#F6AD55",  # Light orange
        "accent": "#FFFAF0",     # Pale orange
        "base": "#7B341E"        # Dark orange
    },
    "underworld": {
        "primary": "#805AD5",    # Indigo
        "secondary": "#D6BCFA",  # Light indigo
        "accent": "#FAF5FF",     # Pale indigo
        "base": "#553C9A"        # Dark indigo
    },
    "renaissance": {
        "primary": "#38B2AC",    # Teal
        "secondary": "#81E6D9",  # Light teal
        "accent": "#E6FFFA",     # Pale teal
        "base": "#285E61"        # Dark teal
    }
}

# Animation definitions for each theme
ANIMATIONS = {
    "biome": [
        """<animate attributeName="opacity" values="0.7;1;0.7" dur="3s" repeatCount="indefinite" />""",
        """<animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="30s" repeatCount="indefinite" />"""
    ],
    "urban": [
        """<animate attributeName="stroke-dashoffset" values="1000;0" dur="5s" repeatCount="indefinite" />""",
        """<animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite" />"""
    ],
    "mystic": [
        """<animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="20s" repeatCount="indefinite" />""",
        """<animate attributeName="r" values="18;22;18" dur="3s" repeatCount="indefinite" />"""
    ],
    "cosmic": [
        """<animate attributeName="r" values="40;45;40" dur="4s" repeatCount="indefinite" />""",
        """<animateTransform attributeName="transform" type="rotate" from="0 50 50" to="-360 50 50" dur="60s" repeatCount="indefinite" />"""
    ],
    "raid": [
        """<animate attributeName="stroke-width" values="2;4;2" dur="1s" repeatCount="indefinite" />""",
        """<animate attributeName="opacity" values="0.7;1;0.7" dur="0.5s" repeatCount="indefinite" />"""
    ],
    "shadow": [
        """<animate attributeName="opacity" values="0.3;0.7;0.3" dur="4s" repeatCount="indefinite" />""",
        """<animateTransform attributeName="transform" type="translate" values="0,0;3,0;0,0" dur="3s" repeatCount="indefinite" />"""
    ],
    "primal": [
        """<animate attributeName="fill" values="{{primary}};{{secondary}};{{primary}}" dur="2s" repeatCount="indefinite" />""",
        """<animateTransform attributeName="transform" type="scale" values="1;1.1;1" dur="1.5s" repeatCount="indefinite" />"""
    ],
    "underworld": [
        """<animate attributeName="stroke-dasharray" values="1,150;90,150;1,150" dur="5s" repeatCount="indefinite" />""",
        """<animateTransform attributeName="transform" type="skewX" values="0;10;0;-10;0" dur="7s" repeatCount="indefinite" />"""
    ],
    "renaissance": [
        """<animateTransform attributeName="transform" type="rotate" from="0 50 50" to="360 50 50" dur="15s" repeatCount="indefinite" />""",
        """<animate attributeName="stroke-width" values="1;2;1" dur="4s" repeatCount="indefinite" />"""
    ]
}

# Base SVG shapes for each theme
BASE_SHAPES = {
    "biome": """
        <circle cx="50" cy="50" r="40" fill="{{base}}" />
        <path d="M50,10 Q65,40 80,40 Q65,60 80,90 Q50,80 20,90 Q35,60 20,40 Q35,40 50,10" fill="{{primary}}" />
        <circle cx="50" cy="50" r="15" fill="{{secondary}}" />
    """,
    "urban": """
        <rect x="10" y="10" width="80" height="80" fill="{{base}}" />
        <path d="M10,10 L90,10 L90,90 L10,90 Z" fill="none" stroke="{{secondary}}" stroke-width="2" stroke-dasharray="5,5" />
        <circle cx="50" cy="50" r="25" fill="{{primary}}" />
        <path d="M30,30 L70,30 L70,70 L30,70 Z" fill="none" stroke="{{accent}}" stroke-width="1" />
    """,
    "mystic": """
        <circle cx="50" cy="50" r="40" fill="{{base}}" />
        <circle cx="50" cy="50" r="35" fill="none" stroke="{{secondary}}" stroke-width="2" />
        <path d="M50,15 L60,40 L85,40 L65,55 L75,80 L50,65 L25,80 L35,55 L15,40 L40,40 Z" fill="{{primary}}" />
        <circle cx="50" cy="50" r="10" fill="{{accent}}" />
    """,
    "cosmic": """
        <circle cx="50" cy="50" r="42" fill="{{base}}" />
        <circle cx="50" cy="50" r="40" fill="none" stroke="{{accent}}" stroke-width="0.5" />
        <circle cx="50" cy="50" r="20" fill="{{primary}}" />
        <circle cx="50" cy="50" r="5" fill="{{secondary}}" />
        <ellipse cx="50" cy="50" rx="42" ry="10" fill="none" stroke="{{secondary}}" stroke-width="0.5" transform="rotate(0,50,50)" />
        <ellipse cx="50" cy="50" rx="42" ry="10" fill="none" stroke="{{secondary}}" stroke-width="0.5" transform="rotate(60,50,50)" />
        <ellipse cx="50" cy="50" rx="42" ry="10" fill="none" stroke="{{secondary}}" stroke-width="0.5" transform="rotate(120,50,50)" />
    """,
    "raid": """
        <circle cx="50" cy="50" r="40" fill="{{base}}" />
        <path d="M50,10 L90,50 L50,90 L10,50 Z" fill="{{primary}}" />
        <circle cx="50" cy="50" r="20" fill="{{secondary}}" />
        <path d="M50,30 L70,50 L50,70 L30,50 Z" fill="{{base}}" />
        <circle cx="50" cy="50" r="10" fill="{{accent}}" />
    """,
    "shadow": """
        <rect x="10" y="10" width="80" height="80" rx="10" fill="{{base}}" />
        <path d="M20,20 L80,20 L80,80 L20,80 Z" fill="{{primary}}" opacity="0.7" />
        <circle cx="35" cy="35" r="10" fill="{{secondary}}" opacity="0.7" />
        <circle cx="65" cy="65" r="10" fill="{{secondary}}" opacity="0.7" />
    """,
    "primal": """
        <circle cx="50" cy="50" r="40" fill="{{base}}" />
        <path d="M50,15 L85,50 L50,85 L15,50 Z" fill="{{primary}}" />
        <path d="M50,30 L70,50 L50,70 L30,50 Z" fill="{{secondary}}" />
        <circle cx="50" cy="50" r="10" fill="{{accent}}" />
    """,
    "underworld": """
        <rect x="10" y="10" width="80" height="80" fill="{{base}}" />
        <path d="M10,10 L90,90 M10,90 L90,10" stroke="{{secondary}}" stroke-width="2" fill="none" />
        <circle cx="50" cy="50" r="30" fill="{{primary}}" />
        <path d="M50,20 L60,45 L85,45 L65,60 L75,85 L50,70 L25,85 L35,60 L15,45 L40,45 Z" fill="none" stroke="{{accent}}" stroke-width="1" />
    """,
    "renaissance": """
        <circle cx="50" cy="50" r="40" fill="{{base}}" />
        <path d="M50,10 A40,40 0 0 1 90,50 A40,40 0 0 1 50,90 A40,40 0 0 1 10,50 A40,40 0 0 1 50,10 Z" fill="none" stroke="{{primary}}" stroke-width="2" />
        <circle cx="50" cy="50" r="25" fill="{{primary}}" opacity="0.7" />
        <path d="M50,25 L60,40 L75,40 L65,55 L70,70 L50,60 L30,70 L35,55 L25,40 L40,40 Z" fill="{{secondary}}" />
    """
}


@dataclass
class GlyphVariant(IconVariant):
    """Extends IconVariant with glyph-specific properties"""
    theme: str = "biome"
    complexity: int = 1
    animated: bool = True
    seed: Optional[int] = None

    def __post_init__(self):
        super().__post_init__()
        if self.seed is None:
            self.seed = random.randint(1, 10000)

        # Set the filename if not provided
        if self.filename is None:
            self.filename = f"glyph-{self.theme}-{self.mode}-{self.size}px-{self.seed}.png"

        # Ensure custom_colors includes theme colors
        if self.custom_colors is None:
            self.custom_colors = {}

        # Add theme colors if not already present
        if self.theme in GLYPH_THEMES:
            theme_colors = GLYPH_THEMES[self.theme]
            for color_key, color_value in theme_colors.items():
                if color_key not in self.custom_colors:
                    self.custom_colors[color_key] = color_value


def generate_glyph_svg(variant: GlyphVariant) -> str:
    """Generate a complete SVG for a glyph variant"""
    random.seed(variant.seed)

    # Get base shape for the theme
    base_shape = BASE_SHAPES.get(variant.theme, BASE_SHAPES["biome"])

    # Add complexity based on level
    extra_elements = generate_complexity_elements(variant)

    # Add animations if requested
    animation_elements = ""
    if variant.animated and variant.theme in ANIMATIONS:
        animation_elements = "\n        ".join(ANIMATIONS[variant.theme])

    # Create the SVG with all elements
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="{variant.size}" height="{variant.size}">
    <defs>
        <filter id="glow{variant.seed}" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>
    <g id="glyph-{variant.theme}-{variant.seed}">
        {base_shape}
        {extra_elements}
        <g filter="url(#glow{variant.seed})">
            {animation_elements}
        </g>
    </g>
</svg>"""

    # Replace color tokens
    for color_key, color_value in variant.custom_colors.items():
        svg = svg.replace(f"{{{{%s}}}}" % color_key, color_value)

    return svg


def generate_complexity_elements(variant: GlyphVariant) -> str:
    """Generate additional SVG elements based on complexity level"""
    if variant.complexity <= 1:
        return ""

    elements = []
    theme_colors = variant.custom_colors

    # Add more elements based on complexity level
    for i in range(variant.complexity - 1):
        # Add circles
        radius = random.randint(3, 10)
        cx = random.randint(20, 80)
        cy = random.randint(20, 80)
        color_key = random.choice(list(theme_colors.keys()))
        opacity = random.uniform(0.3, 0.9)

        elements.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" '
            f'fill="{theme_colors[color_key]}" opacity="{opacity:.1f}" />'
        )

        # Add lines
        x1, y1 = random.randint(10, 90), random.randint(10, 90)
        x2, y2 = random.randint(10, 90), random.randint(10, 90)
        stroke_width = random.randint(1, 3)
        color_key = random.choice(list(theme_colors.keys()))
        opacity = random.uniform(0.3, 0.9)

        elements.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{theme_colors[color_key]}" stroke-width="{stroke_width}" opacity="{opacity:.1f}" />'
        )

    return "\n        ".join(elements)


def process_glyph_variant(variant: GlyphVariant, optimize: bool = False) -> Tuple[bool, List[str], Optional[str]]:
    """Process a single glyph variant"""
    try:
        # Create output directory
        variant.output_folder.mkdir(parents=True, exist_ok=True)

        # Generate the SVG content
        svg_content = generate_glyph_svg(variant)

        # Write SVG file
        svg_path = variant.output_folder / f"{variant.base_filename}.svg"
        svg_path.write_text(svg_content, encoding="utf-8")

        # Generate PNG if requested
        successful_formats = ["svg"]
        if "png" in variant.formats:
            try:
                png_path = variant.output_folder / variant.filename

                # Check if CairoSVG is available
                if CAIROSVG_AVAILABLE:
                    png_ok = maybe_export_png(
                        svg_content.encode("utf-8"), png_path, variant.size
                    )
                    if png_ok:
                        successful_formats.append("png")
                    else:
                        print(f"Warning: PNG generation failed for {variant.filename}")
                else:
                    # No CairoSVG, so just report that PNG was skipped
                    print(
                        f"Skipping PNG generation for {variant.filename} (CairoSVG not available)")
            except Exception as e:
                print(f"Warning: PNG generation error for {variant.filename}: {e}")
                # Continue without PNG generation - SVG is still valid

        return True, successful_formats, None
    except Exception as e:
        return False, [], str(e)


def batch_generate_glyphs(
    variants: List[GlyphVariant],
    parallel: bool = True,
    optimize: bool = False
) -> IconGenerationStats:
    """Generate multiple glyph variants, optionally in parallel"""
    stats = IconGenerationStats()

    if parallel:
        # Process variants in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_variant = {
                executor.submit(process_glyph_variant, variant, optimize): variant
                for variant in variants
            }

            for future in concurrent.futures.as_completed(future_to_variant):
                variant = future_to_variant[future]
                success, formats, error = future.result()

                if success:
                    stats.record_success(variant, formats)
                    print(f"✓ Generated {variant.theme} glyph: {variant.filename}")
                else:
                    stats.record_failure(variant, error)
                    print(f"✗ Failed {variant.theme} glyph: {error}")
    else:
        # Process variants sequentially
        for variant in variants:
            start_time = time.time()
            success, formats, error = process_glyph_variant(variant, optimize)
            processing_time = time.time() - start_time
            stats.add_processing_time(processing_time)

            if success:
                stats.record_success(variant, formats)
                print(f"✓ Generated {variant.theme} glyph: {variant.filename}")
            else:
                stats.record_failure(variant, error)
                print(f"✗ Failed {variant.theme} glyph: {error}")

    return stats


def create_random_glyph_variants(count: int = 10) -> List[GlyphVariant]:
    """Create a set of random glyph variants"""
    variants = []
    themes = list(GLYPH_THEMES.keys())
    modes = ["light", "dark"]
    sizes = [48, 64, 96, 128]

    for _ in range(count):
        theme = random.choice(themes)
        variant = GlyphVariant(
            mode=random.choice(modes),
            finish=theme,  # Use theme as finish for consistency
            size=random.choice(sizes),
            context="web",
            theme=theme,
            complexity=random.randint(1, 3),
            animated=random.choice([True, False]),
            seed=random.randint(1, 10000)
        )
        variants.append(variant)

    return variants


def create_theme_set(theme: str, sizes: List[int] = [48, 64, 96, 128]) -> List[GlyphVariant]:
    """Create a complete set of variants for a specific theme"""
    variants = []
    modes = ["light", "dark"]
    complexity_levels = [1, 2, 3]

    for mode in modes:
        for size in sizes:
            for complexity in complexity_levels:
                variant = GlyphVariant(
                    mode=mode,
                    finish=theme,  # Use theme as finish for consistency
                    size=size,
                    context="web",
                    theme=theme,
                    complexity=complexity,
                    animated=True,
                    seed=hash(f"{theme}-{mode}-{size}-{complexity}") % 10000
                )
                variants.append(variant)

    return variants


def create_complete_glyph_set() -> List[GlyphVariant]:
    """Create a complete set of all possible glyph variants"""
    variants = []

    for theme in GLYPH_THEMES.keys():
        variants.extend(create_theme_set(theme))

    return variants


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Endless Glyph Generator for StrategyDECK")

    parser.add_argument("--output-dir", help="Custom output directory")
    parser.add_argument(
        "--theme", choices=GLYPH_THEMES.keys(),
        help="Generate glyphs for specific theme")
    parser.add_argument(
        "--count", type=int, default=10,
        help="Number of random glyphs to generate")
    parser.add_argument(
        "--mode", choices=["light", "dark", "both"], default="both",
        help="Color mode")
    parser.add_argument(
        "--size", type=int, default=64,
        help="Icon size in pixels")
    parser.add_argument(
        "--complexity", type=int, choices=[1, 2, 3], default=2,
        help="Complexity level")
    parser.add_argument(
        "--all-themes", action="store_true",
        help="Generate all themes")
    parser.add_argument(
        "--seed", type=int,
        help="Random seed for reproducibility")
    parser.add_argument(
        "--no-animation", action="store_true",
        help="Disable animations")
    parser.add_argument(
        "--force-png", action="store_true",
        help="Force PNG generation even if CairoSVG is not available")

    args = parser.parse_args()

    # Set random seed if provided
    if args.seed:
        random.seed(args.seed)

    # Set output directory if provided
    if args.output_dir:
        output_path = Path(args.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        global OUT
        OUT = output_path

    # Print CairoSVG status
    if not CAIROSVG_AVAILABLE and not args.force_png:
        print("\n⚠️ CairoSVG is not installed. PNG export will be disabled.")
        print("   To enable PNG export, install CairoSVG: pip install cairosvg")
        print("   SVG files will still be generated correctly.\n")

    # Determine which variants to generate
    variants = []

    if args.all_themes:
        print(f"Generating complete glyph set for all themes...")
        variants = create_complete_glyph_set()
    elif args.theme:
        print(f"Generating glyph set for theme: {args.theme}")
        variants = create_theme_set(args.theme)
    else:
        print(f"Generating {args.count} random glyph variants...")
        variants = create_random_glyph_variants(args.count)

    # Generate the glyphs
    stats = batch_generate_glyphs(variants, parallel=True, optimize=False)

    # Print summary
    print("\nGlyph Generation Summary:")
    print(f"Total variants: {len(variants)}")
    print(f"Successful SVGs: {stats.successful_svgs}")
    print(f"Successful PNGs: {stats.successful_pngs}")

    if stats.successful_pngs == 0 and not CAIROSVG_AVAILABLE:
        print("\nℹ️ To enable PNG conversion, install CairoSVG:")
        print("   pip install cairosvg")

    print(f"Average processing time: {stats.average_processing_time:.4f}s")

    # Output sample command to view the glyphs
    output_dir = OUT / "glyphs"
    print(f"\nTo view generated glyphs, check the directory: {output_dir}")
    print("SVG files can be viewed in any modern web browser to see animations.")


if __name__ == "__main__":
    main()
