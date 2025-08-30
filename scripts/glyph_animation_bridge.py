#!/usr/bin/env python3
"""
StrategyDECK Glyph Animation Bridge

This module bridges the Endless Glyph Generator system with the Animation Module,
allowing for enhanced animation capabilities for glyphs and advanced interactive
SVG effects.

Features:
- Applies sophisticated animations from animate_icons.py to procedurally generated glyphs
- Supports path morphing, color transitions, and complex animation sequences
- Creates interactive animated glyph collections with theme-based defaults
- Generates HTML demos with animation controls for easy preview
"""

import argparse
import json
import os
import random
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPT_DIR))

# Import from animate_icons module
try:
    from animate_icons import (
        ANIMATED_DIR,
        ANIMATION_PRESETS,
        add_animation_to_svg,
        create_demo_html,
    )
except ImportError:
    print("Error: Could not import from animate_icons.py")
    print("Make sure animate_icons.py exists in the workspace")
    sys.exit(1)

# Import from endless_glyph_generator
try:
    from endless_glyph_generator import (
        GLYPH_THEMES,
        GlyphVariant,
        create_theme_set,
        generate_glyph_svg,
        process_glyph_variant,
    )
except ImportError:
    print("Error: Could not import from endless_glyph_generator.py")
    print("Make sure endless_glyph_generator.py exists in the scripts directory")
    sys.exit(1)

# Output directories
GLYPH_ANIMATED_DIR = ANIMATED_DIR / "glyphs"
GLYPH_ANIMATED_DIR.mkdir(parents=True, exist_ok=True)

# Theme-specific animation mappings
# Maps each glyph theme to its most suitable animation type
THEME_ANIMATION_MAPPING = {
    "biome": "pulse",
    "urban": "bounce",
    "mystic": "fade",
    "cosmic": "rotate",
    "raid": "pulse",
    "shadow": "fade",
    "primal": "color-shift",
    "underworld": "morph",
    "renaissance": "rotate"
}

# Advanced animation sequences that combine multiple animations
ANIMATION_SEQUENCES = {
    "cosmic-pulsar": [
        {"type": "pulse", "duration": "3s", "target": "foreground"},
        {"type": "rotate", "duration": "20s", "target": "all"}
    ],
    "mystic-ritual": [
        {"type": "fade", "duration": "2s", "target": "foreground"},
        {"type": "color-shift", "duration": "5s", "target": "foreground",
         "colors": ["#6B46C1", "#B794F4", "#553C9A"]}
    ],
    "primal-energy": [
        {"type": "pulse", "duration": "1s", "target": "foreground"},
        {"type": "color-shift", "duration": "3s", "target": "foreground",
         "colors": ["#DD6B20", "#F6AD55", "#7B341E"]}
    ],
    "shadow-stealth": [
        {"type": "fade", "duration": "4s", "target": "all"},
        {"type": "morph", "duration": "7s", "target": "foreground"}
    ],
    "urban-techno": [
        {"type": "bounce", "duration": "1s", "target": "foreground"},
        {"type": "color-shift", "duration": "4s", "target": "foreground",
         "colors": ["#3182CE", "#63B3ED", "#2A4365"]}
    ],
    "raid-alert": [
        {"type": "pulse", "duration": "0.5s", "target": "foreground"},
        {"type": "rotate", "duration": "10s", "target": "all"}
    ],
    "renaissance-flow": [
        {"type": "rotate", "duration": "15s", "target": "all"},
        {"type": "morph", "duration": "5s", "target": "foreground"}
    ],
    "biome-growth": [
        {"type": "pulse", "duration": "4s", "target": "foreground"},
        {"type": "color-shift", "duration": "6s", "target": "foreground",
         "colors": ["#2F855A", "#68D391", "#1C4532"]}
    ],
    "underworld-portal": [
        {"type": "morph", "duration": "6s", "target": "foreground"},
        {"type": "rotate", "duration": "12s", "target": "all"}
    ]
}


def apply_animation_to_glyph(
    glyph_variant: GlyphVariant,
    animation_type: str = None,
    target_elements: List[str] = None,
    alternate_colors: List[str] = None,
    custom_duration: str = None
) -> Tuple[str, Path]:
    """Apply animation to a glyph variant and return the SVG content and path"""
    # Generate the basic SVG content
    svg_content = generate_glyph_svg(glyph_variant)

    # Determine animation type if not specified
    if not animation_type:
        animation_type = THEME_ANIMATION_MAPPING.get(glyph_variant.theme, "pulse")

    # Determine target elements if not specified
    if not target_elements:
        target_elements = ["foreground"]

    # Determine alternate colors if not specified for color-shift
    if animation_type == "color-shift" and not alternate_colors:
        theme_colors = GLYPH_THEMES.get(glyph_variant.theme, GLYPH_THEMES["biome"])
        alternate_colors = [
            theme_colors["primary"],
            theme_colors["secondary"],
            theme_colors["accent"]
        ]

    # Apply animation
    animated_svg = add_animation_to_svg(
        svg_content,
        animation_type,
        target_elements,
        alternate_colors,
        custom_duration
    )

    # Create output path
    output_filename = f"{glyph_variant.theme}_{animation_type}_{glyph_variant.size}px_{glyph_variant.seed}.svg"
    output_path = GLYPH_ANIMATED_DIR / output_filename

    # Write animated SVG
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(animated_svg)

    return animated_svg, output_path


def apply_animation_sequence(
    glyph_variant: GlyphVariant,
    sequence_name: str = None
) -> Tuple[str, Path]:
    """Apply a complex animation sequence to a glyph variant"""
    # Generate the basic SVG content
    svg_content = generate_glyph_svg(glyph_variant)

    # Determine sequence if not specified
    if not sequence_name:
        # Try to find a sequence matching the theme
        sequence_name = f"{glyph_variant.theme}-" + next(
            (name.split('-')[1] for name in ANIMATION_SEQUENCES
             if name.startswith(glyph_variant.theme)),
            "pulsar"  # default fallback
        )

    # Get sequence definition or fall back to a simpler animation
    sequence = ANIMATION_SEQUENCES.get(
        sequence_name,
        ANIMATION_SEQUENCES.get(f"{glyph_variant.theme}-pulsar",
                                [{"type": "pulse", "target": "foreground"}])
    )

    # Apply each animation in the sequence
    animated_svg = svg_content
    for animation_step in sequence:
        animation_type = animation_step.get("type")
        target_elements = animation_step.get("target", ["foreground"])
        if not isinstance(target_elements, list):
            target_elements = [target_elements]

        alternate_colors = animation_step.get("colors")
        custom_duration = animation_step.get("duration")

        animated_svg = add_animation_to_svg(
            animated_svg,
            animation_type,
            target_elements,
            alternate_colors,
            custom_duration
        )

    # Create output path
    output_filename = f"{glyph_variant.theme}_{sequence_name}_{glyph_variant.size}px_{glyph_variant.seed}.svg"
    output_path = GLYPH_ANIMATED_DIR / output_filename

    # Write animated SVG
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(animated_svg)

    return animated_svg, output_path


def generate_theme_animation_set(theme: str, size: int = 64, count: int = 5) -> List[Path]:
    """Generate a set of animated glyphs for a specific theme with different animations"""
    glyph_variants = []
    animated_paths = []

    # Create base glyph variants
    for i in range(count):
        seed = random.randint(1, 10000)
        variant = GlyphVariant(
            mode="dark" if theme in ["cosmic", "shadow", "underworld"] else "light",
            finish=theme,
            size=size,
            context="web",
            theme=theme,
            complexity=random.randint(1, 3),
            animated=True,
            seed=seed
        )
        glyph_variants.append(variant)

    # Apply different animations to each variant
    for variant in glyph_variants:
        # Apply theme-specific animation
        _, path = apply_animation_to_glyph(
            variant,
            animation_type=THEME_ANIMATION_MAPPING.get(theme)
        )
        animated_paths.append(path)

        # Apply a sequence if available for this theme
        for seq_name in ANIMATION_SEQUENCES:
            if seq_name.startswith(theme):
                _, path = apply_animation_sequence(variant, seq_name)
                animated_paths.append(path)
                break

    return animated_paths


def generate_complete_animation_showcase() -> Dict[str, List[Path]]:
    """Generate a complete showcase of all themes and animations"""
    showcase = {}

    for theme in GLYPH_THEMES:
        print(f"Generating animated showcase for {theme} theme...")
        showcase[theme] = generate_theme_animation_set(theme, size=96, count=2)

    return showcase


def create_animation_showcase_demo(showcase: Dict[str, List[Path]]) -> Path:
    """Create an HTML demo showcasing all animated glyphs by theme"""
    all_paths = []
    for theme_paths in showcase.values():
        all_paths.extend(theme_paths)

    demo_path = create_demo_html(all_paths, "glyph-showcase")
    return demo_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="StrategyDECK Glyph Animation Bridge")

    parser.add_argument(
        "--theme",
        choices=GLYPH_THEMES.keys(),
        help="Generate animated glyphs for specific theme"
    )
    parser.add_argument(
        "--animation",
        choices=list(ANIMATION_PRESETS.keys()),
        help="Type of animation to apply"
    )
    parser.add_argument(
        "--sequence",
        choices=list(ANIMATION_SEQUENCES.keys()),
        help="Animation sequence to apply"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=96,
        help="Glyph size in pixels"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="Number of glyphs to generate per theme"
    )
    parser.add_argument(
        "--showcase",
        action="store_true",
        help="Generate complete showcase of all themes and animations"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Create HTML demo page"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open demo in browser"
    )

    args = parser.parse_args()

    if args.showcase:
        print("Generating complete animation showcase...")
        showcase = generate_complete_animation_showcase()

        if args.demo:
            demo_path = create_animation_showcase_demo(showcase)
            print(f"Created showcase demo at: {demo_path}")

            if args.open:
                try:
                    import webbrowser
                    webbrowser.open(f"file://{demo_path.absolute()}")
                    print(f"Opened demo page in browser")
                except Exception as e:
                    print(f"Error opening demo page in browser: {e}")

        # Print summary
        total_glyphs = sum(len(paths) for paths in showcase.values())
        print(
            f"\nGenerated {total_glyphs} animated glyphs across {len(showcase)} themes")

    elif args.theme:
        print(f"Generating animated glyphs for {args.theme} theme...")

        if args.sequence:
            # Generate a single glyph with the specified sequence
            variant = GlyphVariant(
                mode="dark" if args.theme in [
                    "cosmic", "shadow", "underworld"] else "light",
                finish=args.theme,
                size=args.size,
                context="web",
                theme=args.theme,
                complexity=2,
                animated=True,
                seed=random.randint(1, 10000)
            )

            _, path = apply_animation_sequence(variant, args.sequence)
            paths = [path]

            print(f"Applied animation sequence '{args.sequence}' to glyph: {path}")

        elif args.animation:
            # Generate a single glyph with the specified animation
            variant = GlyphVariant(
                mode="dark" if args.theme in [
                    "cosmic", "shadow", "underworld"] else "light",
                finish=args.theme,
                size=args.size,
                context="web",
                theme=args.theme,
                complexity=2,
                animated=True,
                seed=random.randint(1, 10000)
            )

            _, path = apply_animation_to_glyph(variant, args.animation)
            paths = [path]

            print(f"Applied animation '{args.animation}' to glyph: {path}")

        else:
            # Generate a set of glyphs with theme-specific animations
            paths = generate_theme_animation_set(args.theme, args.size, args.count)

            print(f"Generated {len(paths)} animated glyphs for {args.theme} theme")

        if args.demo:
            demo_path = create_demo_html(paths, f"{args.theme}-animations")
            print(f"Created demo at: {demo_path}")

            if args.open:
                try:
                    import webbrowser
                    webbrowser.open(f"file://{demo_path.absolute()}")
                    print(f"Opened demo page in browser")
                except Exception as e:
                    print(f"Error opening demo page in browser: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
