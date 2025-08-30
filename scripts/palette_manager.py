#!/usr/bin/env python3
"""
StrategyDECK Color Palette Manager

A tool for creating, managing and testing color palettes for the StrategyDECK icon system.
This allows users to create custom color schemes and visualize them before generating icons.

Usage:
  python palette_manager.py --create my-custom-palette
  python palette_manager.py --edit metallic
  python palette_manager.py --preview neon
  python palette_manager.py --export my-custom-palette --format css
"""

import argparse
import colorsys
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# Try to import from generate_icons
try:
    from generate_icons import FINISH_COLORS, TOKENS
except ImportError:
    # Default values if import fails
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

# Palette configuration
CONFIG_DIR = ROOT / "config"
CONFIG_DIR.mkdir(exist_ok=True)

# Import enhanced palettes if available
try:
    from enhanced_icon_generator import ENHANCED_PALETTES
except ImportError:
    ENHANCED_PALETTES = {
        "neon": {
            "neon-blue": "#00FFFF",
            "neon-green": "#39FF14",
            "neon-pink": "#FF10F0",
            "neon-yellow": "#FFFF00",
            "neon-orange": "#FF9933",
            "neon-purple": "#9D00FF",
        },
        "pastel": {
            "pastel-blue": "#A7C7E7",
            "pastel-green": "#C1E1C1",
            "pastel-pink": "#FFD1DC",
            "pastel-yellow": "#FFFACD",
            "pastel-orange": "#FFD8B1",
            "pastel-purple": "#CBC3E3",
        },
        "metallic": {
            "silver": "#C0C0C0",
            "gold": "#FFD700",
            "bronze": "#CD7F32",
            "platinum": "#E5E4E2",
            "titanium": "#878681",
            "chrome": "#DDDDDD",
        }
    }


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple) -> str:
    """Convert RGB tuple to hex color"""
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"


def lighten_color(hex_color: str, amount: float = 0.1) -> str:
    """Lighten a color by the given amount"""
    rgb = hex_to_rgb(hex_color)
    hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    hsv = (hsv[0], hsv[1], min(1.0, hsv[2] + amount))
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return rgb_to_hex((int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))


def darken_color(hex_color: str, amount: float = 0.1) -> str:
    """Darken a color by the given amount"""
    rgb = hex_to_rgb(hex_color)
    hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    hsv = (hsv[0], hsv[1], max(0.0, hsv[2] - amount))
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return rgb_to_hex((int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))


def get_complementary_color(hex_color: str) -> str:
    """Get the complementary color"""
    rgb = hex_to_rgb(hex_color)
    hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    hsv = ((hsv[0] + 0.5) % 1.0, hsv[1], hsv[2])
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    return rgb_to_hex((int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255)))


def get_all_palettes() -> Dict[str, Dict[str, str]]:
    """Get all available palettes"""
    palettes = {}

    # Add built-in finish colors
    palettes["default"] = FINISH_COLORS

    # Add enhanced palettes
    palettes.update(ENHANCED_PALETTES)

    # Add custom palettes from config directory
    for palette_file in CONFIG_DIR.glob("*_palette.json"):
        palette_name = palette_file.stem.replace("_palette", "")
        try:
            with open(palette_file, "r", encoding="utf-8") as f:
                palettes[palette_name] = json.load(f)
        except Exception as e:
            print(f"Error loading palette {palette_name}: {e}")

    return palettes


def save_palette(name: str, colors: Dict[str, str]) -> bool:
    """Save a palette to a JSON file"""
    try:
        palette_path = CONFIG_DIR / f"{name}_palette.json"
        with open(palette_path, "w", encoding="utf-8") as f:
            json.dump(colors, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving palette: {e}")
        return False


def create_palette(name: str, base_color: Optional[str] = None) -> Dict[str, str]:
    """Create a new palette based on a base color"""
    if not base_color:
        base_color = TOKENS["brand_orange"]  # Default orange

    # Generate variations
    palette = {}

    # Generate main color
    palette[f"{name}-main"] = base_color

    # Generate light/dark variants
    palette[f"{name}-light"] = lighten_color(base_color, 0.2)
    palette[f"{name}-dark"] = darken_color(base_color, 0.2)

    # Generate complementary color
    comp_color = get_complementary_color(base_color)
    palette[f"{name}-complement"] = comp_color

    # Generate accent colors (30 and 60 degrees away in hue)
    rgb = hex_to_rgb(base_color)
    hsv = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)

    # Accent 1 (30 degrees)
    accent1_hsv = ((hsv[0] + 0.083) % 1.0, hsv[1], hsv[2])
    rgb = colorsys.hsv_to_rgb(accent1_hsv[0], accent1_hsv[1], accent1_hsv[2])
    palette[f"{name}-accent1"] = rgb_to_hex((int(rgb[0]*255),
                                            int(rgb[1]*255), int(rgb[2]*255)))

    # Accent 2 (60 degrees)
    accent2_hsv = ((hsv[0] + 0.167) % 1.0, hsv[1], hsv[2])
    rgb = colorsys.hsv_to_rgb(accent2_hsv[0], accent2_hsv[1], accent2_hsv[2])
    palette[f"{name}-accent2"] = rgb_to_hex((int(rgb[0]*255),
                                            int(rgb[1]*255), int(rgb[2]*255)))

    return palette


def export_palette(name: str, format_type: str) -> str:
    """Export a palette to various formats (CSS, SCSS, JSON)"""
    palettes = get_all_palettes()

    if name not in palettes:
        return f"Error: Palette '{name}' not found"

    palette = palettes[name]

    if format_type == "css":
        output = ":root {\n"
        for color_name, color_value in palette.items():
            output += f"  --color-{color_name}: {color_value};\n"
        output += "}\n"
        return output

    elif format_type == "scss":
        output = "// StrategyDECK Palette: " + name + "\n"
        for color_name, color_value in palette.items():
            output += f"$color-{color_name}: {color_value};\n"
        return output

    elif format_type == "json":
        return json.dumps(palette, indent=2)

    elif format_type == "python":
        output = f"{name.upper()}_COLORS = {{\n"
        for color_name, color_value in palette.items():
            output += f"    \"{color_name}\": \"{color_value}\",\n"
        output += "}\n"
        return output

    return f"Unsupported format: {format_type}"


def print_palette(name: str, palette: Dict[str, str]):
    """Print a palette to the console"""
    print(f"\nPalette: {name}")
    print("-" * (len(name) + 10))

    for color_name, color_value in palette.items():
        # Try to use terminal colors if possible
        try:
            rgb = hex_to_rgb(color_value)
            r, g, b = rgb
            print(f"\033[38;2;{r};{g};{b}m■\033[0m {color_name}: {color_value}")
        except:
            print(f"■ {color_name}: {color_value}")

    print()


def preview_palette(name: str):
    """Generate a preview of a palette"""
    palettes = get_all_palettes()

    if name not in palettes:
        print(f"Error: Palette '{name}' not found")
        return

    palette = palettes[name]

    # Print the palette
    print_palette(name, palette)

    # Try to generate HTML preview
    preview_html = generate_html_preview(name, palette)
    preview_path = CONFIG_DIR / f"{name}_preview.html"

    try:
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(preview_html)
        print(f"HTML preview saved to: {preview_path}")

        # Try to open in browser
        try:
            import webbrowser
            webbrowser.open(f"file://{preview_path}")
        except:
            pass
    except Exception as e:
        print(f"Error saving preview: {e}")


def generate_html_preview(name: str, palette: Dict[str, str]) -> str:
    """Generate HTML preview for a palette"""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrategyDECK Palette: {name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .palette-container {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
        }}
        .color-card {{
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .color-sample {{
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .color-info {{
            padding: 15px;
            background-color: white;
        }}
        .color-name {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .color-hex {{
            font-family: monospace;
            color: #666;
        }}
        .preview-section {{
            margin-top: 40px;
        }}
        .preview-light, .preview-dark {{
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .preview-light {{
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #EEEEEE;
        }}
        .preview-dark {{
            background-color: #060607;
            color: #FFFFFF;
        }}
        .icon-preview {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 15px;
        }}
        .icon {{
            width: 100px;
            height: 100px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            color: white;
        }}
    </style>
</head>
<body>
    <h1>StrategyDECK Palette: {name}</h1>
    
    <div class="palette-container">
"""

    # Add color cards
    for color_name, color_value in palette.items():
        # Calculate contrast color for text
        rgb = hex_to_rgb(color_value)
        brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
        text_color = "#FFFFFF" if brightness < 128 else "#000000"

        html += f"""
        <div class="color-card">
            <div class="color-sample" style="background-color: {color_value}; color: {text_color};">
                <span>Aa</span>
            </div>
            <div class="color-info">
                <div class="color-name">{color_name}</div>
                <div class="color-hex">{color_value}</div>
            </div>
        </div>"""

    # Add preview sections
    html += """
    </div>
    
    <div class="preview-section">
        <h2>Light Mode Preview</h2>
        <div class="preview-light">
            <h3>Icons with this palette</h3>
            <div class="icon-preview">
"""

    # Add light mode icon previews
    for color_name, color_value in palette.items():
        html += f"""
                <div class="icon" style="background-color: #FFFFFF; border: 1px solid #EEEEEE;">
                    <div style="width: 80%; height: 80%; background-color: {color_value}; border-radius: 4px;"></div>
                </div>"""

    html += """
            </div>
        </div>
        
        <h2>Dark Mode Preview</h2>
        <div class="preview-dark">
            <h3>Icons with this palette</h3>
            <div class="icon-preview">
"""

    # Add dark mode icon previews
    for color_name, color_value in palette.items():
        html += f"""
                <div class="icon" style="background-color: #060607;">
                    <div style="width: 80%; height: 80%; background-color: {color_value}; border-radius: 4px;"></div>
                </div>"""

    html += """
            </div>
        </div>
    </div>
</body>
</html>
"""

    return html


def interactive_edit(name: str):
    """Interactive palette editor"""
    palettes = get_all_palettes()

    if name not in palettes:
        print(f"Error: Palette '{name}' not found")
        return

    palette = palettes[name].copy()

    try:
        while True:
            # Clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')

            # Print the current palette
            print_palette(name, palette)

            print("Palette Editor Commands:")
            print("  [a] Add color")
            print("  [e] Edit color")
            print("  [d] Delete color")
            print("  [s] Save palette")
            print("  [p] Preview palette")
            print("  [q] Quit without saving")

            choice = input("\nEnter command: ").strip().lower()

            if choice == 'a':
                # Add color
                color_name = input("Enter color name: ").strip()
                if not color_name:
                    continue

                color_value = input("Enter color value (hex): ").strip()
                if not color_value.startswith('#'):
                    color_value = '#' + color_value

                try:
                    # Validate hex color
                    hex_to_rgb(color_value)
                    palette[color_name] = color_value
                except:
                    print("Invalid hex color. Press Enter to continue.")
                    input()

            elif choice == 'e':
                # Edit color
                names = list(palette.keys())
                for i, name in enumerate(names):
                    print(f"  [{i+1}] {name}: {palette[name]}")

                try:
                    idx = int(input("\nEnter color number to edit: ")) - 1
                    if 0 <= idx < len(names):
                        color_name = names[idx]
                        new_value = input(
                            f"Enter new value for {color_name} (hex): ").strip()
                        if not new_value.startswith('#'):
                            new_value = '#' + new_value

                        try:
                            # Validate hex color
                            hex_to_rgb(new_value)
                            palette[color_name] = new_value
                        except:
                            print("Invalid hex color. Press Enter to continue.")
                            input()
                except:
                    pass

            elif choice == 'd':
                # Delete color
                names = list(palette.keys())
                for i, name in enumerate(names):
                    print(f"  [{i+1}] {name}: {palette[name]}")

                try:
                    idx = int(input("\nEnter color number to delete: ")) - 1
                    if 0 <= idx < len(names):
                        color_name = names[idx]
                        confirm = input(
                            f"Are you sure you want to delete {color_name}? (y/n): ").strip().lower()
                        if confirm == 'y':
                            del palette[color_name]
                except:
                    pass

            elif choice == 's':
                # Save palette
                if save_palette(name, palette):
                    print(f"Palette '{name}' saved successfully!")
                else:
                    print("Error saving palette. Press Enter to continue.")
                input()

            elif choice == 'p':
                # Preview
                os.system('cls' if os.name == 'nt' else 'clear')
                print_palette(name, palette)
                input("Press Enter to continue...")

            elif choice == 'q':
                # Quit
                confirm = input("Quit without saving? (y/n): ").strip().lower()
                if confirm == 'y':
                    return

    except KeyboardInterrupt:
        print("\nExiting editor...")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="StrategyDECK Color Palette Manager")

    # Main commands (mutually exclusive)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true",
                       help="List all available palettes")
    group.add_argument("--create", metavar="NAME", help="Create a new color palette")
    group.add_argument("--edit", metavar="NAME", help="Edit an existing palette")
    group.add_argument("--preview", metavar="NAME", help="Preview a palette")
    group.add_argument("--export", metavar="NAME",
                       help="Export a palette to a specific format")

    # Options for create
    parser.add_argument("--base-color", help="Base color for new palette (hex)")

    # Options for export
    parser.add_argument("--format", choices=["css", "scss", "json", "python"],
                        default="css", help="Export format")

    args = parser.parse_args()

    # Create config directory if it doesn't exist
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if args.list:
        # List all palettes
        palettes = get_all_palettes()
        print("\nAvailable Palettes:")
        print("-" * 20)

        for name, palette in palettes.items():
            print(f"{name} ({len(palette)} colors)")

        print("\nUse --preview <name> to see palette details")

    elif args.create:
        # Create new palette
        name = args.create
        palettes = get_all_palettes()

        if name in palettes:
            print(f"Error: Palette '{name}' already exists")
            return

        palette = create_palette(name, args.base_color)
        if save_palette(name, palette):
            print(f"Created palette '{name}' with {len(palette)} colors")
            print_palette(name, palette)

            # Ask if user wants to edit
            edit = input(
                "Do you want to edit this palette now? (y/n): ").strip().lower()
            if edit == 'y':
                interactive_edit(name)
        else:
            print(f"Error creating palette '{name}'")

    elif args.edit:
        # Edit palette
        interactive_edit(args.edit)

    elif args.preview:
        # Preview palette
        preview_palette(args.preview)

    elif args.export:
        # Export palette
        output = export_palette(args.export, args.format)
        print(output)

        # Ask if user wants to save to file
        save_to_file = input("Save to file? (y/n): ").strip().lower()
        if save_to_file == 'y':
            extension = ".css" if args.format == "css" else \
                ".scss" if args.format == "scss" else \
                ".json" if args.format == "json" else ".py"

            filename = f"{args.export}_{args.format}{extension}"
            file_path = CONFIG_DIR / filename

            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(output)
                print(f"Saved to {file_path}")
            except Exception as e:
                print(f"Error saving file: {e}")


if __name__ == "__main__":
    main()
