#!/usr/bin/env python3
"""
StrategyDECK Animation & Glyph Showcase

This script demonstrates the integrated animation system and endless glyph generator,
creating a comprehensive showcase of all animation capabilities with interactive demos.
"""

import argparse
import concurrent.futures
import os
import random
import shutil
import subprocess
import sys
import tempfile
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(ROOT))

# Output directories
SHOWCASE_DIR = ROOT / "assets" / "showcase"
SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)


def run_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """Run a command and return success status and output"""
    print(f"{description}...")
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        print(f"Error: {e}")
        return False, str(e)


def create_standard_icon_animations() -> List[str]:
    """Create standard icon animations"""
    animated_icons = []

    for animation_type in ["pulse", "rotate", "fade", "bounce", "color-shift", "morph"]:
        cmd = [
            sys.executable,
            str(ROOT / "animate_icons.py"),
            "--mode", "light",
            "--finish", "flat-orange",
            "--size", "64px",
            "--animation", animation_type,
            "--demo"
        ]

        success, output = run_command(
            cmd,
            f"Creating {animation_type} animation for standard icons"
        )

        if success:
            # Try to find the demo path in output
            lines = output.splitlines()
            for line in lines:
                if "Created demo page at" in line:
                    demo_path = line.split("Created demo page at")[-1].strip(": ")
                    animated_icons.append(demo_path)
                    break

    return animated_icons


def create_glyph_animations() -> List[str]:
    """Create glyph animations with the glyph animation bridge"""
    animated_glyphs = []

    # First create a glyph showcase
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "glyph_animation_bridge.py"),
        "--showcase",
        "--demo"
    ]

    success, output = run_command(
        cmd,
        "Creating glyph animation showcase"
    )

    if success:
        # Try to find the demo path in output
        lines = output.splitlines()
        for line in lines:
            if "Created showcase demo at" in line:
                demo_path = line.split("Created showcase demo at")[-1].strip(": ")
                animated_glyphs.append(demo_path)
                break

    # Then create individual themed glyphs
    for theme in ["cosmic", "urban", "mystic", "raid"]:
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "glyph_animation_bridge.py"),
            "--theme", theme,
            "--demo"
        ]

        success, output = run_command(
            cmd,
            f"Creating {theme} glyph animations"
        )

        if success:
            # Try to find the demo path in output
            lines = output.splitlines()
            for line in lines:
                if "Created demo at" in line:
                    demo_path = line.split("Created demo at")[-1].strip(": ")
                    animated_glyphs.append(demo_path)
                    break

    return animated_glyphs


def create_animation_designer() -> Optional[str]:
    """Create the animation designer interface"""
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "animation_designer.py")
    ]

    success, output = run_command(
        cmd,
        "Creating animation designer interface"
    )

    if success:
        # Try to find the designer path in output
        lines = output.splitlines()
        for line in lines:
            if "Created animation designer at" in line:
                designer_path = line.split(
                    "Created animation designer at")[-1].strip(": ")
                return designer_path

    return None


def create_master_showcase(
    icon_demos: List[str],
    glyph_demos: List[str],
    designer_path: Optional[str]
) -> str:
    """Create a master showcase HTML page that links to all demos"""

    showcase_path = SHOWCASE_DIR / "animation_showcase.html"

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrategyDECK Animation System Showcase</title>
    <style>
        :root {
            --primary: #FF6A00;
            --primary-dark: #CC5500;
            --bg-dark: #1a1a1a;
            --bg-light: #f8f9fa;
            --text-dark: #333;
            --text-light: #f8f9fa;
            --border: #ddd;
            --panel-bg: #fff;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-dark);
            background-color: var(--bg-light);
            margin: 0;
            padding: 0;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background-color: var(--primary);
            color: white;
            padding: 40px 0;
            text-align: center;
            margin-bottom: 40px;
        }
        
        header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        
        header p {
            margin: 10px 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .section {
            margin-bottom: 40px;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        h2 {
            color: var(--primary);
            border-bottom: 2px solid var(--primary);
            padding-bottom: 10px;
            margin-top: 0;
        }
        
        .demo-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .demo-card {
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .demo-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .demo-preview {
            height: 200px;
            background-color: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        
        .demo-preview iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        
        .demo-preview img {
            max-width: 100%;
            max-height: 100%;
        }
        
        .demo-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .demo-preview:hover .demo-overlay {
            opacity: 1;
        }
        
        .demo-overlay-button {
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .demo-info {
            padding: 15px;
        }
        
        .demo-info h3 {
            margin-top: 0;
            margin-bottom: 10px;
            color: var(--text-dark);
        }
        
        .demo-info p {
            margin: 0;
            color: #666;
        }
        
        .feature-highlight {
            display: flex;
            margin-top: 20px;
            background-color: #f9f9f9;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        }
        
        .feature-image {
            flex: 0 0 40%;
        }
        
        .feature-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .feature-content {
            flex: 0 0 60%;
            padding: 20px;
        }
        
        .feature-content h3 {
            margin-top: 0;
            color: var(--primary);
        }
        
        .btn {
            display: inline-block;
            background-color: var(--primary);
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: bold;
            transition: background-color 0.2s;
            margin-top: 10px;
        }
        
        .btn:hover {
            background-color: var(--primary-dark);
        }
        
        footer {
            background-color: var(--text-dark);
            color: white;
            padding: 20px 0;
            text-align: center;
            margin-top: 40px;
        }
        
        footer p {
            margin: 0;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>StrategyDECK Animation System</h1>
            <p>Comprehensive showcase of SVG animation capabilities for icons and glyphs</p>
        </div>
    </header>
    
    <div class="container">
        <div class="section">
            <h2>Animation System Overview</h2>
            <p>The StrategyDECK Animation System provides sophisticated animation capabilities for SVG icons and procedurally generated glyphs. The system supports multiple animation types, including pulsing, rotation, color transitions, and path morphing.</p>
            
            <div class="feature-highlight">
                <div class="feature-image">
                    <img src="https://via.placeholder.com/600x400/FF6A00/FFFFFF?text=Animation+System" alt="Animation System">
                </div>
                <div class="feature-content">
                    <h3>Key Features</h3>
                    <ul>
                        <li>CSS and SMIL animation support for maximum compatibility</li>
                        <li>Multiple animation types with customizable parameters</li>
                        <li>Interactive HTML demos with animation controls</li>
                        <li>Seamless integration with the Endless Glyph Generator</li>
                        <li>Visual animation designer for creating custom animations</li>
                    </ul>
                    <a href="#designer" class="btn">Try the Designer</a>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Standard Icon Animations</h2>
            <p>Predefined animations applied to the standard StrategyDECK icons in various styles and sizes.</p>
            
            <div class="demo-grid">
"""

    # Add icon demos
    for i, demo_path in enumerate(icon_demos):
        demo_name = Path(demo_path).stem
        animation_type = demo_name.split('_')[0]

        html += f"""
                <div class="demo-card">
                    <div class="demo-preview">
                        <iframe src="{demo_path}" title="{demo_name}"></iframe>
                        <div class="demo-overlay">
                            <a href="{demo_path}" target="_blank" class="demo-overlay-button">Open Demo</a>
                        </div>
                    </div>
                    <div class="demo-info">
                        <h3>{animation_type.capitalize()} Animation</h3>
                        <p>Standard icon animation with {animation_type} effect</p>
                    </div>
                </div>
"""

    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>Glyph Animations</h2>
            <p>Advanced animations for procedurally generated glyphs with theme-specific effects.</p>
            
            <div class="demo-grid">
"""

    # Add glyph demos
    for i, demo_path in enumerate(glyph_demos):
        demo_name = Path(demo_path).stem
        theme_name = "Theme" if "showcase" in demo_name else demo_name.split('-')[0]

        html += f"""
                <div class="demo-card">
                    <div class="demo-preview">
                        <iframe src="{demo_path}" title="{demo_name}"></iframe>
                        <div class="demo-overlay">
                            <a href="{demo_path}" target="_blank" class="demo-overlay-button">Open Demo</a>
                        </div>
                    </div>
                    <div class="demo-info">
                        <h3>{theme_name.capitalize()} Glyph Animations</h3>
                        <p>Procedurally generated glyphs with theme-specific animations</p>
                    </div>
                </div>
"""

    html += """
            </div>
        </div>
"""

    # Add designer section if available
    if designer_path:
        html += f"""
        <div class="section" id="designer">
            <h2>Animation Designer</h2>
            <p>Create custom animations for any SVG icon or glyph with the interactive animation designer.</p>
            
            <div class="feature-highlight">
                <div class="feature-image">
                    <img src="https://via.placeholder.com/600x400/FF6A00/FFFFFF?text=Animation+Designer" alt="Animation Designer">
                </div>
                <div class="feature-content">
                    <h3>Visual Animation Designer</h3>
                    <p>The Animation Designer allows you to:</p>
                    <ul>
                        <li>Browse and select from all available SVG icons and glyphs</li>
                        <li>Apply multiple animations with customizable parameters</li>
                        <li>Preview animations in real-time with playback controls</li>
                        <li>Export animated SVGs for use in web applications</li>
                        <li>Copy generated SVG code for direct embedding</li>
                    </ul>
                    <a href="{designer_path}" target="_blank" class="btn">Open Animation Designer</a>
                </div>
            </div>
        </div>
"""

    html += """
        <div class="section">
            <h2>Animation System Documentation</h2>
            <p>Learn how to use the StrategyDECK Animation System in your projects.</p>
            
            <div class="feature-highlight">
                <div class="feature-content">
                    <h3>Using the Animation System</h3>
                    <p>The animation system can be used in several ways:</p>
                    <ul>
                        <li><strong>Command-line:</strong> Use the <code>animate_icons.py</code> script to apply animations to existing SVG icons.</li>
                        <li><strong>Glyph Integration:</strong> Use the <code>glyph_animation_bridge.py</code> script to create animated glyphs.</li>
                        <li><strong>Visual Designer:</strong> Use the interactive designer to create and preview animations visually.</li>
                        <li><strong>API:</strong> Import and use the animation functions directly in your Python code.</li>
                    </ul>
                    <h3>Example Usage</h3>
                    <pre><code>python animate_icons.py --mode light --finish flat-orange --animation pulse --demo</code></pre>
                    <pre><code>python scripts/glyph_animation_bridge.py --theme cosmic --animation rotate --demo</code></pre>
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <div class="container">
            <p>&copy; 2023 StrategyDECK Animation System. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>
"""

    with open(showcase_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return str(showcase_path)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="StrategyDECK Animation & Glyph Showcase")

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Generate a quick showcase with fewer examples"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the showcase in a browser when done"
    )

    args = parser.parse_args()

    print("Generating StrategyDECK Animation & Glyph Showcase...")

    # Create standard icon animations
    icon_demos = create_standard_icon_animations()
    print(f"Created {len(icon_demos)} standard icon animation demos")

    # Create glyph animations
    glyph_demos = create_glyph_animations()
    print(f"Created {len(glyph_demos)} glyph animation demos")

    # Create animation designer
    designer_path = create_animation_designer()
    if designer_path:
        print(f"Created animation designer at: {designer_path}")
    else:
        print("Failed to create animation designer")

    # Create master showcase
    showcase_path = create_master_showcase(icon_demos, glyph_demos, designer_path)
    print(f"Created master showcase at: {showcase_path}")

    # Open in browser if requested
    if args.open:
        try:
            webbrowser.open(f"file://{Path(showcase_path).absolute()}")
            print(f"Opened showcase in browser")
        except Exception as e:
            print(f"Error opening showcase in browser: {e}")
            print(f"You can manually open the file at: {showcase_path}")

    print("\nShowcase generation complete!")
    print(f"To view the showcase, open: {showcase_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
