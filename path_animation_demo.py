#!/usr/bin/env python3
"""
StrategyDECK Path Animation Demo

This script demonstrates the capabilities of the StrategyDECK path animation system
by creating animated examples of various path effects, transitions, and interactive
animations. It generates a comprehensive showcase of all path animation techniques.
"""

import argparse
import os
import random
import sys
import webbrowser
from pathlib import Path

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SCRIPT_DIR / "scripts"))

# Try to import the path animation system
try:
    from scripts.path_animation_system import (
        PATH_ANIM_DIR,
        PATH_ANIMATION_PRESETS,
        apply_path_animation_to_svg,
        create_path_animation_demo,
    )
except ImportError:
    print("Error: Could not import from path_animation_system.py")
    print("Make sure path_animation_system.py exists in the scripts directory")
    sys.exit(1)

# Try to import the animation system integration
try:
    from scripts.animation_system_integration import (
        UNIFIED_ANIM_DIR,
        analyze_svg_content,
        create_unified_demo,
        process_svg_file,
    )
except ImportError:
    print("Error: Could not import from animation_system_integration.py")
    print("Make sure animation_system_integration.py exists in the scripts directory")
    sys.exit(1)

# Master SVG files
ASSETS_DIR = ROOT / "assets"
MASTERS_DIR = ASSETS_DIR / "masters"
ICONS_DIR = ASSETS_DIR / "icons"
DEMO_OUTPUT_DIR = ROOT / "demos" / "path_animations"

# Create demo output directory
DEMO_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def create_basic_shape_svgs():
    """Create basic SVG shapes for animation demonstrations"""
    shapes = {
        "circle": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <circle cx="50" cy="50" r="40" fill="none" stroke="#FF6A00" stroke-width="2" />
</svg>""",
        "square": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <rect x="10" y="10" width="80" height="80" fill="none" stroke="#FF6A00" stroke-width="2" />
</svg>""",
        "triangle": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <path d="M50,10 L90,90 L10,90 Z" fill="none" stroke="#FF6A00" stroke-width="2" />
</svg>""",
        "star": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <path d="M50,10 L61,35 L90,38 L70,57 L75,85 L50,72 L25,85 L30,57 L10,38 L39,35 Z" fill="none" stroke="#FF6A00" stroke-width="2" />
</svg>""",
        "spiral": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <path d="M50,50 m0,-40 a40,40 0 1,1 0,80 a30,30 0 1,0 0,-60 a20,20 0 1,1 0,40 a10,10 0 1,0 0,-20 a5,5 0 1,1 0,10" fill="none" stroke="#FF6A00" stroke-width="2" />
</svg>""",
        "wave": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <path d="M10,50 C20,30 30,70 40,50 C50,30 60,70 70,50 C80,30 90,70 100,50" fill="none" stroke="#FF6A00" stroke-width="2" />
</svg>""",
        "zigzag": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <path d="M10,50 L30,30 L50,70 L70,30 L90,50" fill="none" stroke="#FF6A00" stroke-width="2" />
</svg>""",
        "grid": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <path d="M10,10 L90,10 M10,30 L90,30 M10,50 L90,50 M10,70 L90,70 M10,90 L90,90 M10,10 L10,90 M30,10 L30,90 M50,10 L50,90 M70,10 L70,90 M90,10 L90,90" fill="none" stroke="#FF6A00" stroke-width="2" />
</svg>"""
    }

    # Create SVG files
    shape_paths = {}
    for name, svg_content in shapes.items():
        output_path = DEMO_OUTPUT_DIR / f"basic_{name}.svg"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        shape_paths[name] = output_path

    return shape_paths


def create_animation_matrix(shape_paths):
    """Create a matrix of all animations applied to all shapes"""
    animated_paths = []

    # Apply each animation to each shape
    for shape_name, shape_path in shape_paths.items():
        for animation_name in PATH_ANIMATION_PRESETS.keys():
            # Apply animation
            output_path = apply_path_animation_to_svg(
                shape_path,
                animation_name,
                output_dir=DEMO_OUTPUT_DIR / "matrix"
            )

            if output_path:
                animated_paths.append(output_path)
                print(f"✓ Created {animation_name} animation for {shape_name}")
            else:
                print(f"✗ Failed to create {animation_name} animation for {shape_name}")

    return animated_paths


def create_advanced_examples():
    """Create advanced examples of path animations"""
    examples = {}

    # Complex path example
    complex_path = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <path d="M20,50 C20,40 30,30 50,30 C70,30 80,40 80,50 C80,60 70,70 50,70 C30,70 20,60 20,50 Z" fill="none" stroke="#FF6A00" stroke-width="2" />
    <path d="M35,35 C40,30 60,30 65,35 C70,40 70,60 65,65 C60,70 40,70 35,65 C30,60 30,40 35,35 Z" fill="none" stroke="#3182CE" stroke-width="1.5" />
    <circle cx="50" cy="50" r="5" fill="#FF6A00" />
</svg>"""

    # Nested path example
    nested_path = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <g id="outer">
        <path d="M10,10 L90,10 L90,90 L10,90 Z" fill="none" stroke="#FF6A00" stroke-width="2" />
        <g id="inner">
            <path d="M30,30 L70,30 L70,70 L30,70 Z" fill="none" stroke="#3182CE" stroke-width="1.5" />
            <path d="M40,40 L60,40 L60,60 L40,60 Z" fill="none" stroke="#805AD5" stroke-width="1" />
        </g>
    </g>
</svg>"""

    # Text path example
    text_path = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
    <path id="curve" d="M10,50 C30,10 70,10 90,50" fill="none" stroke="#FF6A00" stroke-width="1" />
    <text font-size="10">
        <textPath href="#curve">StrategyDECK Path Animations</textPath>
    </text>
</svg>"""

    # Create SVG files
    examples["complex"] = DEMO_OUTPUT_DIR / "advanced_complex.svg"
    with open(examples["complex"], "w", encoding="utf-8") as f:
        f.write(complex_path)

    examples["nested"] = DEMO_OUTPUT_DIR / "advanced_nested.svg"
    with open(examples["nested"], "w", encoding="utf-8") as f:
        f.write(nested_path)

    examples["text"] = DEMO_OUTPUT_DIR / "advanced_text.svg"
    with open(examples["text"], "w", encoding="utf-8") as f:
        f.write(text_path)

    # Apply specific animations to each example
    animated_examples = []

    # Complex path with morphing
    animated_path = apply_path_animation_to_svg(
        examples["complex"],
        "morph-organic",
        output_dir=DEMO_OUTPUT_DIR / "advanced"
    )
    if animated_path:
        animated_examples.append(animated_path)

    # Nested paths with different animations for each path
    animated_path = apply_path_animation_to_svg(
        examples["nested"],
        "draw",
        target_elements=["all-paths"],
        output_dir=DEMO_OUTPUT_DIR / "advanced"
    )
    if animated_path:
        animated_examples.append(animated_path)

    # Text path with flow animation
    animated_path = apply_path_animation_to_svg(
        examples["text"],
        "flow",
        output_dir=DEMO_OUTPUT_DIR / "advanced"
    )
    if animated_path:
        animated_examples.append(animated_path)

    return animated_examples


def find_existing_icons():
    """Find existing SVG icons in the assets directory"""
    icon_paths = []

    # Check for master SVGs first
    master_svgs = list(MASTERS_DIR.glob("*.svg"))
    if master_svgs:
        icon_paths.extend(master_svgs)

    # If no masters, look in the icons directory
    if not icon_paths:
        icon_paths = list(ICONS_DIR.glob("**/*.svg"))[:5]  # Limit to 5 icons

    return icon_paths


def create_demo_page(animated_paths):
    """Create a comprehensive demo page"""
    # Use the built-in demo page generator
    demo_path = create_path_animation_demo(animated_paths)
    return demo_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="StrategyDECK Path Animation Demo")

    parser.add_argument(
        "--open", action="store_true",
        help="Open the demo page in a browser after creation"
    )
    parser.add_argument(
        "--basic-only", action="store_true",
        help="Only create basic shape animations"
    )
    parser.add_argument(
        "--advanced-only", action="store_true",
        help="Only create advanced examples"
    )
    parser.add_argument(
        "--icons-only", action="store_true",
        help="Only animate existing icons"
    )

    args = parser.parse_args()

    animated_paths = []

    if args.basic_only:
        # Only create basic shape animations
        shape_paths = create_basic_shape_svgs()
        animated_paths.extend(create_animation_matrix(shape_paths).values())

    elif args.advanced_only:
        # Only create advanced examples
        animated_paths.extend(create_advanced_examples())

    elif args.icons_only:
        # Only animate existing icons
        icon_paths = find_existing_icons()
        for icon_path in icon_paths:
            for animation_name in ["draw", "flow", "morph-geometric", "follow-path"]:
                animated_path = apply_path_animation_to_svg(
                    icon_path,
                    animation_name,
                    output_dir=DEMO_OUTPUT_DIR / "icons"
                )
                if animated_path:
                    animated_paths.append(animated_path)

    else:
        # Create all demo types
        print("Creating basic shape animations...")
        shape_paths = create_basic_shape_svgs()
        animated_paths.extend(create_animation_matrix(shape_paths))

        print("\nCreating advanced examples...")
        animated_paths.extend(create_advanced_examples())

        print("\nAnimating existing icons...")
        icon_paths = find_existing_icons()
        for icon_path in icon_paths:
            for animation_name in ["draw", "flow", "morph-geometric", "follow-path"]:
                animated_path = apply_path_animation_to_svg(
                    icon_path,
                    animation_name,
                    output_dir=DEMO_OUTPUT_DIR / "icons"
                )
                if animated_path:
                    animated_paths.append(animated_path)
                    print(f"✓ Applied {animation_name} to {icon_path.name}")
                else:
                    print(f"✗ Failed to apply {animation_name} to {icon_path.name}")

    # Create demo page
    print(f"\nCreating demo page with {len(animated_paths)} animated SVGs...")
    demo_path = create_demo_page(animated_paths)

    if demo_path:
        print(f"✓ Demo page created at: {demo_path}")

        if args.open:
            try:
                print("Opening demo page in browser...")
                webbrowser.open(f"file://{demo_path.absolute()}")
            except Exception as e:
                print(f"Error opening demo page: {e}")
    else:
        print("✗ Failed to create demo page")

    return 0


if __name__ == "__main__":
    sys.exit(main())
