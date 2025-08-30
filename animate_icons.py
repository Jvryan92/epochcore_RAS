#!/usr/bin/env python3
"""
StrategyDECK Icon Animation Module

This module adds animation capabilities to the SVG icons, allowing for dynamic
effects like rotation, pulsing, morphing, and path animations for web applications.
"""

import argparse
import json
import os
import random
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Output directories
ASSETS_DIR = ROOT / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
ANIMATED_DIR = ASSETS_DIR / "animated"

# Ensure the animated directory exists
ANIMATED_DIR.mkdir(parents=True, exist_ok=True)

# Animation presets
ANIMATION_PRESETS = {
    "pulse": {
        "type": "scale",
        "keyframes": [
            {"time": "0%", "scale": 1.0, "opacity": 1.0},
            {"time": "50%", "scale": 1.2, "opacity": 0.8},
            {"time": "100%", "scale": 1.0, "opacity": 1.0}
        ],
        "duration": "2s",
        "iteration": "infinite",
        "timing": "ease-in-out"
    },
    "rotate": {
        "type": "rotate",
        "keyframes": [
            {"time": "0%", "rotate": 0},
            {"time": "100%", "rotate": 360}
        ],
        "duration": "3s",
        "iteration": "infinite",
        "timing": "linear"
    },
    "bounce": {
        "type": "translate",
        "keyframes": [
            {"time": "0%", "translateY": 0},
            {"time": "50%", "translateY": -10},
            {"time": "100%", "translateY": 0}
        ],
        "duration": "1s",
        "iteration": "infinite",
        "timing": "ease-in-out"
    },
    "fade": {
        "type": "opacity",
        "keyframes": [
            {"time": "0%", "opacity": 1.0},
            {"time": "50%", "opacity": 0.3},
            {"time": "100%", "opacity": 1.0}
        ],
        "duration": "2.5s",
        "iteration": "infinite",
        "timing": "ease-in-out"
    },
    "morph": {
        "type": "path",
        "keyframes": [
            {"time": "0%", "path": "original"},
            {"time": "50%", "path": "transformed"},
            {"time": "100%", "path": "original"}
        ],
        "duration": "3s",
        "iteration": "infinite",
        "timing": "ease-in-out"
    },
    "color-shift": {
        "type": "color",
        "keyframes": [
            {"time": "0%", "color": "original"},
            {"time": "33%", "color": "alternate1"},
            {"time": "66%", "color": "alternate2"},
            {"time": "100%", "color": "original"}
        ],
        "duration": "4s",
        "iteration": "infinite",
        "timing": "linear"
    }
}


def parse_svg(svg_content: str) -> Optional[ET.Element]:
    """Parse SVG content and return the root element"""
    try:
        # Hack to handle namespaces properly in ElementTree
        svg_content = re.sub(r'xmlns="[^"]+"', '', svg_content, count=1)

        # Parse the SVG
        root = ET.fromstring(svg_content)
        return root
    except Exception as e:
        print(f"Error parsing SVG: {e}")
        return None


def generate_animation_css(animation_id: str, preset: Dict) -> str:
    """Generate CSS animation for the given preset"""
    animation_type = preset["type"]
    keyframes = preset["keyframes"]
    duration = preset.get("duration", "2s")
    iteration = preset.get("iteration", "infinite")
    timing = preset.get("timing", "ease-in-out")

    # Build keyframes CSS
    keyframes_css = f"@keyframes {animation_id} {{\n"

    for keyframe in keyframes:
        time = keyframe["time"]
        keyframes_css += f"  {time} {{\n"

        if animation_type == "scale":
            scale = keyframe.get("scale", 1.0)
            opacity = keyframe.get("opacity", 1.0)
            keyframes_css += f"    transform: scale({scale});\n"
            keyframes_css += f"    opacity: {opacity};\n"
        elif animation_type == "rotate":
            rotate = keyframe.get("rotate", 0)
            keyframes_css += f"    transform: rotate({rotate}deg);\n"
        elif animation_type == "translate":
            translateX = keyframe.get("translateX", 0)
            translateY = keyframe.get("translateY", 0)
            keyframes_css += f"    transform: translate({translateX}px, {translateY}px);\n"
        elif animation_type == "opacity":
            opacity = keyframe.get("opacity", 1.0)
            keyframes_css += f"    opacity: {opacity};\n"
        elif animation_type == "color":
            color = keyframe.get("color", "original")
            if color != "original" and color != "transformed" and color != "alternate1" and color != "alternate2":
                keyframes_css += f"    fill: {color};\n"

        keyframes_css += "  }\n"

    keyframes_css += "}\n"

    # Add animation application class
    animation_class = f".{animation_id}-animation {{\n"
    animation_class += f"  animation: {animation_id} {duration} {timing} {iteration};\n"

    if animation_type == "scale" or animation_type == "rotate" or animation_type == "translate":
        animation_class += "  transform-origin: center;\n"
        animation_class += "  transform-box: fill-box;\n"

    animation_class += "}\n"

    return keyframes_css + animation_class


def add_animation_to_svg(svg_content: str, animation_type: str, target_elements: List[str] = None,
                         alternate_colors: List[str] = None, custom_duration: str = None) -> str:
    """Add animation to SVG content"""
    # Parse SVG
    root = parse_svg(svg_content)
    if root is None:
        return svg_content

    # Get animation preset
    preset = ANIMATION_PRESETS.get(animation_type)
    if preset is None:
        print(f"Unknown animation type: {animation_type}")
        return svg_content

    # Create a unique ID for this animation
    animation_id = f"strategydeck-{animation_type}-{uuid.uuid4().hex[:8]}"

    # Modify preset if custom duration is provided
    if custom_duration:
        preset = preset.copy()
        preset["duration"] = custom_duration

    # Generate animation CSS
    animation_css = generate_animation_css(animation_id, preset)

    # Find the elements to animate
    elements_to_animate = []

    # If target elements are specified, find them
    if target_elements:
        for target in target_elements:
            if target == "all":
                # Add all paths and shapes
                for path in root.findall(".//path"):
                    elements_to_animate.append(path)
                for rect in root.findall(".//rect"):
                    elements_to_animate.append(rect)
                for circle in root.findall(".//circle"):
                    elements_to_animate.append(circle)
                for polygon in root.findall(".//polygon"):
                    elements_to_animate.append(polygon)
            elif target.startswith("#"):
                # Find by ID
                element_id = target[1:]
                for element in root.findall(".//*[@id='{}']".format(element_id)):
                    elements_to_animate.append(element)
            elif target == "background":
                # Find the background rectangle (usually the first rect)
                background_rect = root.find(".//rect")
                if background_rect is not None:
                    elements_to_animate.append(background_rect)
            elif target == "foreground":
                # Find all elements except the background rect
                background_rect = root.find(".//rect")
                for path in root.findall(".//path"):
                    if path != background_rect:
                        elements_to_animate.append(path)
                for circle in root.findall(".//circle"):
                    if circle != background_rect:
                        elements_to_animate.append(circle)
                for polygon in root.findall(".//polygon"):
                    if polygon != background_rect:
                        elements_to_animate.append(polygon)
    else:
        # Default: animate foreground elements (paths, circles, polygons)
        background_rect = root.find(".//rect")
        for path in root.findall(".//path"):
            if path != background_rect:
                elements_to_animate.append(path)
        for circle in root.findall(".//circle"):
            if circle != background_rect:
                elements_to_animate.append(circle)
        for polygon in root.findall(".//polygon"):
            if polygon != background_rect:
                elements_to_animate.append(polygon)

    # Apply animation class to elements
    for element in elements_to_animate:
        # Get current class or create empty
        current_class = element.get("class", "")
        if current_class:
            element.set("class", f"{current_class} {animation_id}-animation")
        else:
            element.set("class", f"{animation_id}-animation")

        # If it's a color animation, save original color and add alternates
        if animation_type == "color-shift" and alternate_colors:
            # Save original fill if it exists
            original_fill = element.get("fill")
            if original_fill:
                element.set("data-original-fill", original_fill)

            # Add alternate colors as data attributes
            # Only use first two alternates
            for i, color in enumerate(alternate_colors[:2], 1):
                element.set(f"data-alternate-fill-{i}", color)

    # Serialize the updated SVG
    # ET doesn't preserve namespaces properly, so we need to hack it
    serialized = ET.tostring(root, encoding="unicode")

    # Reinsert the SVG namespace
    serialized = serialized.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"')

    # Add the style tag with animations
    style_tag = f"<style>\n{animation_css}</style>"
    serialized = serialized.replace("</svg>", f"{style_tag}</svg>")

    # For morphing animations, add JS to handle path morphing
    if animation_type == "morph":
        morph_js = """
<script>
(function() {
  // Simple path morphing function
  function morphPaths() {
    const paths = document.querySelectorAll('path[class*="-animation"]');
    paths.forEach(path => {
      // Save original path data
      if (!path.getAttribute('data-original-d')) {
        path.setAttribute('data-original-d', path.getAttribute('d'));
        
        // Create a slightly transformed version by moving some points
        const originalD = path.getAttribute('d');
        const transformedD = createTransformedPath(originalD);
        path.setAttribute('data-transformed-d', transformedD);
      }
    });
  }
  
  // Function to create a transformed version of a path
  function createTransformedPath(pathData) {
    // Simple transformation: add a small random offset to each coordinate
    return pathData.replace(/([0-9]+(\.[0-9]+)?)/g, (match) => {
      const num = parseFloat(match);
      const offset = (Math.random() - 0.5) * 5; // Random offset between -2.5 and 2.5
      return (num + offset).toFixed(2);
    });
  }
  
  // Initialize morphing when SVG is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', morphPaths);
  } else {
    morphPaths();
  }
})();
</script>
"""
        serialized = serialized.replace("</svg>", f"{morph_js}</svg>")

    # For color-shift animations, add JS to handle color changes
    if animation_type == "color-shift":
        color_js = """
<script>
(function() {
  // Initialize color animations
  function initColorAnimations() {
    // Find all elements with our animation class
    const elements = document.querySelectorAll('[class*="-animation"]');
    
    elements.forEach(element => {
      // Only process elements with data-original-fill or a fill attribute
      const originalFill = element.getAttribute('data-original-fill') || element.getAttribute('fill');
      if (originalFill) {
        element.setAttribute('data-original-fill', originalFill);
        
        // If no alternates defined, create some
        if (!element.hasAttribute('data-alternate-fill-1')) {
          // Generate complementary colors
          const alternate1 = generateComplementaryColor(originalFill);
          const alternate2 = generateTriadicColor(originalFill);
          
          element.setAttribute('data-alternate-fill-1', alternate1);
          element.setAttribute('data-alternate-fill-2', alternate2);
        }
      }
    });
  }
  
  // Generate a complementary color
  function generateComplementaryColor(hexColor) {
    // Parse the hex color
    let r = parseInt(hexColor.substr(1, 2), 16);
    let g = parseInt(hexColor.substr(3, 2), 16);
    let b = parseInt(hexColor.substr(5, 2), 16);
    
    // Invert the colors
    r = 255 - r;
    g = 255 - g;
    b = 255 - b;
    
    // Convert back to hex
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  }
  
  // Generate a triadic color
  function generateTriadicColor(hexColor) {
    // Parse the hex color
    let r = parseInt(hexColor.substr(1, 2), 16);
    let g = parseInt(hexColor.substr(3, 2), 16);
    let b = parseInt(hexColor.substr(5, 2), 16);
    
    // Rotate the colors (120° in RGB space, simplified)
    const temp = r;
    r = g;
    g = b;
    b = temp;
    
    // Convert back to hex
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
  }
  
  // Initialize when SVG is loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initColorAnimations);
  } else {
    initColorAnimations();
  }
})();
</script>
"""
        serialized = serialized.replace("</svg>", f"{color_js}</svg>")

    return serialized


def process_icon(icon_path: Path, animation_type: str, output_dir: Path,
                 target_elements: List[str] = None, alternate_colors: List[str] = None,
                 custom_duration: str = None) -> Path:
    """Process a single icon file"""
    # Read the SVG file
    try:
        with open(icon_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
    except Exception as e:
        print(f"Error reading SVG file {icon_path}: {e}")
        return None

    # Add animation
    animated_svg = add_animation_to_svg(
        svg_content,
        animation_type,
        target_elements,
        alternate_colors,
        custom_duration
    )

    # Create output directory structure
    relative_path = icon_path.relative_to(ICONS_DIR)
    output_path = output_dir / relative_path.parent / \
        f"{animation_type}_{relative_path.name}"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the animated SVG
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(animated_svg)
        return output_path
    except Exception as e:
        print(f"Error writing animated SVG to {output_path}: {e}")
        return None


def process_icons(mode: str, finish: str, size: str, context: str, animation_type: str,
                  target_elements: List[str] = None, alternate_colors: List[str] = None,
                  custom_duration: str = None) -> List[Path]:
    """Process icons matching the specified criteria"""
    # Construct the path pattern
    if mode:
        base_dir = ICONS_DIR / mode
    else:
        base_dir = ICONS_DIR

    if finish:
        base_dir = base_dir / finish

    if size:
        base_dir = base_dir / size

    if context:
        base_dir = base_dir / context

    # Find all SVG files
    svg_files = list(base_dir.glob("**/*.svg"))

    if not svg_files:
        print(f"No SVG files found at {base_dir}")
        return []

    # Process each file
    animated_files = []
    for svg_file in svg_files:
        output_path = process_icon(
            svg_file,
            animation_type,
            ANIMATED_DIR,
            target_elements,
            alternate_colors,
            custom_duration
        )
        if output_path:
            animated_files.append(output_path)

    return animated_files


def create_demo_html(animated_files: List[Path], animation_type: str) -> Path:
    """Create an HTML demo page showing all animated icons"""
    demo_path = ANIMATED_DIR / f"{animation_type}_demo.html"

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrategyDECK Animated Icons Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
            margin: 0;
            padding: 20px;
        }
        
        h1, h2 {
            color: #FF6A00;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .icon-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            grid-gap: 20px;
            margin-top: 20px;
        }
        
        .icon-card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            padding: 15px;
            text-align: center;
            transition: transform 0.2s;
        }
        
        .icon-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        
        .icon-container {
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 10px;
        }
        
        .icon-container svg {
            max-width: 100%;
            max-height: 100%;
        }
        
        .icon-label {
            font-size: 12px;
            color: #666;
            word-break: break-word;
        }
        
        .animation-controls {
            margin: 20px 0;
            padding: 15px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .toggle-button {
            background-color: #FF6A00;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .toggle-button:hover {
            background-color: #CC5500;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>StrategyDECK Animated Icons</h1>
        <p>Interactive demo of SVG icons with CSS animations and JavaScript enhancements.</p>
        
        <div class="animation-controls">
            <h2>Animation Controls</h2>
            <button id="toggleAnimations" class="toggle-button">Pause All Animations</button>
            <button id="resetAnimations" class="toggle-button">Reset Animations</button>
        </div>
        
        <div class="icon-grid">
"""

    # Add each icon
    for i, icon_path in enumerate(animated_files):
        # Get relative path for display
        rel_path = icon_path.relative_to(ANIMATED_DIR)

        # Read SVG content
        try:
            with open(icon_path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
        except Exception as e:
            print(f"Error reading SVG file {icon_path}: {e}")
            continue

        # Add to HTML
        html += f"""
            <div class="icon-card">
                <div class="icon-container" id="icon-{i}">
                    {svg_content}
                </div>
                <div class="icon-label">{rel_path}</div>
            </div>
"""

    # Add control script
    html += """
        </div>
    </div>
    
    <script>
        // Animation control functions
        document.getElementById('toggleAnimations').addEventListener('click', function() {
            const button = document.getElementById('toggleAnimations');
            const icons = document.querySelectorAll('svg [class*="-animation"]');
            
            if (button.textContent === 'Pause All Animations') {
                icons.forEach(element => {
                    element.style.animationPlayState = 'paused';
                });
                button.textContent = 'Resume All Animations';
            } else {
                icons.forEach(element => {
                    element.style.animationPlayState = 'running';
                });
                button.textContent = 'Pause All Animations';
            }
        });
        
        document.getElementById('resetAnimations').addEventListener('click', function() {
            const icons = document.querySelectorAll('svg [class*="-animation"]');
            
            icons.forEach(element => {
                // Reset by removing and re-adding the animation class
                const classes = element.getAttribute('class').split(' ');
                const animationClass = classes.find(c => c.includes('-animation'));
                
                if (animationClass) {
                    element.classList.remove(animationClass);
                    setTimeout(() => {
                        element.classList.add(animationClass);
                    }, 10);
                }
            });
        });
    </script>
</body>
</html>
"""

    # Write the HTML file
    try:
        with open(demo_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return demo_path
    except Exception as e:
        print(f"Error writing demo HTML to {demo_path}: {e}")
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Add animations to StrategyDECK SVG icons")

    # Icon selection options
    parser.add_argument("--mode", choices=["light", "dark"], help="Icon mode")
    parser.add_argument(
        "--finish", help="Icon finish (e.g., flat-orange, matte-carbon)")
    parser.add_argument("--size", help="Icon size (e.g., 16px, 32px)")
    parser.add_argument("--context", help="Icon context (e.g., web, print)")

    # Animation options
    parser.add_argument("--animation", choices=list(ANIMATION_PRESETS.keys()), required=True,
                        help="Type of animation to apply")
    parser.add_argument("--target", action="append",
                        help="Target elements to animate (e.g., all, foreground, background, #elementId)")
    parser.add_argument("--colors", action="append",
                        help="Alternate colors for color-shift animation (hex format)")
    parser.add_argument(
        "--duration", help="Custom animation duration (e.g., 2s, 500ms)")

    # Output options
    parser.add_argument("--demo", action="store_true", help="Create an HTML demo page")
    parser.add_argument("--open", action="store_true",
                        help="Open the demo page in a browser")

    args = parser.parse_args()

    # Process icons
    animated_files = process_icons(
        args.mode,
        args.finish,
        args.size,
        args.context,
        args.animation,
        args.target,
        args.colors,
        args.duration
    )

    # Print results
    if animated_files:
        print(f"Successfully animated {len(animated_files)} icons")
        for file_path in animated_files[:5]:  # Show first 5
            print(f"  - {file_path}")
        if len(animated_files) > 5:
            print(f"  ... and {len(animated_files) - 5} more")
    else:
        print("No icons were animated")
        return 1

    # Create demo if requested
    if args.demo:
        demo_path = create_demo_html(animated_files, args.animation)
        if demo_path:
            print(f"Created demo page at {demo_path}")

            # Open in browser if requested
            if args.open:
                try:
                    import webbrowser
                    webbrowser.open(f"file://{demo_path.absolute()}")
                    print(f"Opened demo page in browser")
                except Exception as e:
                    print(f"Error opening demo page in browser: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
