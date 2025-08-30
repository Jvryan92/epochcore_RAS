#!/usr/bin/env python3
"""
StrategyDECK Animation System Integration

This module serves as a central integration point for all animation capabilities
in the StrategyDECK system, combining the core animation module, glyph animations,
and the advanced path-based animation system into a unified interface.

Features:
- Single entry point for all animation types
- Smart automation to determine the best animation for content
- Batch processing for animations across multiple files
- Tools for animation sequence creation and playback
- Demo generation with unified interface
"""

import argparse
import json
import os
import random
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

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
        process_icon,
    )
except ImportError:
    print("Error: Could not import from animate_icons.py")
    print("Make sure animate_icons.py exists in the workspace")
    sys.exit(1)

# Import from path_animation_system if available
try:
    from scripts.path_animation_system import (
        PATH_ANIM_DIR,
        PATH_ANIMATION_PRESETS,
        apply_path_animation,
        apply_path_animation_to_svg,
        create_path_animation_demo,
    )
    PATH_ANIMATIONS_AVAILABLE = True
except ImportError:
    print("Warning: Could not import from path_animation_system.py")
    print("Path-based animations will not be available.")
    PATH_ANIMATIONS_AVAILABLE = False

# Import from glyph_animation_bridge if available
try:
    from scripts.glyph_animation_bridge import (
        ANIMATION_SEQUENCES,
        THEME_ANIMATION_MAPPING,
        apply_animation_sequence,
        apply_animation_to_glyph,
        generate_theme_animation_set,
    )
    GLYPH_ANIMATIONS_AVAILABLE = True
except ImportError:
    print("Warning: Could not import from glyph_animation_bridge.py")
    print("Glyph-specific animations will not be available.")
    GLYPH_ANIMATIONS_AVAILABLE = False

# Output directories
UNIFIED_ANIM_DIR = ANIMATED_DIR / "unified"
UNIFIED_ANIM_DIR.mkdir(parents=True, exist_ok=True)

# Unified animation type mapping
ANIMATION_TYPE_MAPPING = {
    # Basic animations from animate_icons.py
    "pulse": {"module": "basic", "category": "transform"},
    "rotate": {"module": "basic", "category": "transform"},
    "bounce": {"module": "basic", "category": "transform"},
    "fade": {"module": "basic", "category": "opacity"},
    "morph": {"module": "basic", "category": "path"},
    "color-shift": {"module": "basic", "category": "color"},

    # Path animations from path_animation_system.py
    "draw": {"module": "path", "category": "stroke"},
    "flow": {"module": "path", "category": "stroke"},
    "reveal": {"module": "path", "category": "stroke"},
    "pulse-path": {"module": "path", "category": "stroke"},
    "morph-geometric": {"module": "path", "category": "path"},
    "morph-organic": {"module": "path", "category": "path"},
    "follow-path": {"module": "path", "category": "motion"},
    "orbit": {"module": "path", "category": "motion"},
    "zigzag": {"module": "path", "category": "motion"},
    "wave": {"module": "path", "category": "transform"},

    # Glyph sequences from glyph_animation_bridge.py
    "cosmic-pulsar": {"module": "glyph", "category": "sequence"},
    "mystic-ritual": {"module": "glyph", "category": "sequence"},
    "primal-energy": {"module": "glyph", "category": "sequence"},
    "shadow-stealth": {"module": "glyph", "category": "sequence"},
    "urban-techno": {"module": "glyph", "category": "sequence"},
    "raid-alert": {"module": "glyph", "category": "sequence"},
    "renaissance-flow": {"module": "glyph", "category": "sequence"},
    "biome-growth": {"module": "glyph", "category": "sequence"},
    "underworld-portal": {"module": "glyph", "category": "sequence"}
}

# Combined animation presets for documentation and UI
ALL_ANIMATION_PRESETS = {
    **ANIMATION_PRESETS,
    **(PATH_ANIMATION_PRESETS if PATH_ANIMATIONS_AVAILABLE else {}),
    **(ANIMATION_SEQUENCES if GLYPH_ANIMATIONS_AVAILABLE else {})
}


def get_available_animations() -> Dict[str, Dict]:
    """Get a dictionary of all available animations with metadata"""
    available = {}

    # Add basic animations
    for name, preset in ANIMATION_PRESETS.items():
        available[name] = {
            "type": preset["type"],
            "module": "basic",
            "duration": preset.get("duration", "2s"),
            "description": f"Basic {preset['type']} animation"
        }

    # Add path animations if available
    if PATH_ANIMATIONS_AVAILABLE:
        for name, preset in PATH_ANIMATION_PRESETS.items():
            available[name] = {
                "type": preset["type"],
                "module": "path",
                "duration": preset.get("duration", "3s"),
                "description": f"Path-based {preset['type']} animation"
            }

    # Add glyph animations if available
    if GLYPH_ANIMATIONS_AVAILABLE:
        for name, sequence in ANIMATION_SEQUENCES.items():
            # Extract theme from sequence name
            theme = name.split("-")[0] if "-" in name else "generic"
            effect = name.split("-")[1] if "-" in name else name

            available[name] = {
                "type": "sequence",
                "module": "glyph",
                "theme": theme,
                "duration": "varies",
                "description": f"{theme.capitalize()} theme {effect} sequence"
            }

    return available


def analyze_svg_content(svg_content: str) -> Dict[str, any]:
    """
    Analyze SVG content to determine its structure and best animation approaches.
    Returns information about paths, shapes, and recommended animations.
    """
    root = ET.fromstring(svg_content)

    # Count various elements
    path_count = len(root.findall(".//path"))
    circle_count = len(root.findall(".//circle"))
    rect_count = len(root.findall(".//rect"))
    polygon_count = len(root.findall(".//polygon"))

    # Determine if it's path-heavy
    path_heavy = path_count > (circle_count + rect_count + polygon_count)

    # Look for potential glyph themes
    potential_themes = []
    for theme in ["biome", "urban", "mystic", "cosmic", "raid", "shadow",
                  "primal", "underworld", "renaissance"]:
        if theme in svg_content.lower():
            potential_themes.append(theme)

    # Determine if it has recognizable glyph structure
    is_glyph_like = len(potential_themes) > 0 or "glyph" in svg_content.lower()

    # Recommend animations based on structure
    recommended_animations = []

    if path_heavy and PATH_ANIMATIONS_AVAILABLE:
        # Recommend path-based animations for path-heavy SVGs
        if path_count == 1:
            recommended_animations.extend(["draw", "pulse-path", "flow"])
        else:
            recommended_animations.extend(["morph-geometric", "reveal", "wave"])

    if is_glyph_like and GLYPH_ANIMATIONS_AVAILABLE:
        # Recommend theme-specific animations for glyph-like SVGs
        for theme in potential_themes:
            if theme in THEME_ANIMATION_MAPPING:
                base_anim = THEME_ANIMATION_MAPPING[theme]
                recommended_animations.append(base_anim)

                # Add theme sequences if available
                for seq_name in ANIMATION_SEQUENCES:
                    if seq_name.startswith(theme):
                        recommended_animations.append(seq_name)
                        break

    # Always add some basic animations
    if circle_count > 0:
        recommended_animations.append("pulse")
    recommended_animations.extend(["rotate", "fade", "color-shift"])

    # Remove duplicates while preserving order
    seen = set()
    unique_recommendations = []
    for anim in recommended_animations:
        if anim not in seen:
            seen.add(anim)
            unique_recommendations.append(anim)

    return {
        "elements": {
            "paths": path_count,
            "circles": circle_count,
            "rectangles": rect_count,
            "polygons": polygon_count
        },
        "path_heavy": path_heavy,
        "is_glyph_like": is_glyph_like,
        "potential_themes": potential_themes,
        "recommended_animations": unique_recommendations[:5]  # Top 5 recommendations
    }


def apply_animation(svg_content: str, animation_type: str, **kwargs) -> str:
    """
    Apply animation to SVG content based on animation type.
    Automatically selects the appropriate animation module.
    """
    # Get animation module
    animation_info = ANIMATION_TYPE_MAPPING.get(animation_type)
    if not animation_info:
        print(
            f"Warning: Unknown animation type '{animation_type}'. Using basic pulse animation.")
        return add_animation_to_svg(svg_content, "pulse", **kwargs)

    module_type = animation_info["module"]

    if module_type == "basic":
        # Use basic animations from animate_icons
        return add_animation_to_svg(svg_content, animation_type, **kwargs)

    elif module_type == "path" and PATH_ANIMATIONS_AVAILABLE:
        # Use path-based animations
        return apply_path_animation(svg_content, animation_type, **kwargs)

    elif module_type == "glyph" and GLYPH_ANIMATIONS_AVAILABLE:
        # For glyph sequences, we need to convert to a GlyphVariant first
        # This is a simplified approach - in a real implementation,
        # you would need to extract more information from the SVG
        print("Warning: Glyph sequences cannot be directly applied to arbitrary SVGs.")
        print("Using basic animation instead.")
        return add_animation_to_svg(svg_content, "pulse", **kwargs)

    else:
        # Fallback to basic animations
        print(f"Warning: Animation module '{module_type}' not available.")
        return add_animation_to_svg(svg_content, "pulse", **kwargs)


def process_svg_file(svg_path: Path, animation_type: str, output_dir: Path = None, **kwargs) -> Path:
    """Process a single SVG file with the specified animation"""
    try:
        # Read the SVG file
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()

        # Analyze content
        analysis = analyze_svg_content(svg_content)

        # If no animation type specified, use the first recommended one
        if not animation_type and analysis["recommended_animations"]:
            animation_type = analysis["recommended_animations"][0]
            print(f"Using recommended animation: {animation_type}")
        elif not animation_type:
            animation_type = "pulse"  # Default fallback

        # Apply animation
        animated_svg = apply_animation(svg_content, animation_type, **kwargs)

        # Create output path
        if output_dir is None:
            output_dir = UNIFIED_ANIM_DIR

        output_path = output_dir / f"animated_{animation_type}_{svg_path.name}"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the animated SVG
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(animated_svg)

        return output_path

    except Exception as e:
        print(f"Error processing SVG file {svg_path}: {e}")
        return None


def batch_process_svg_files(svg_paths: List[Path], animation_type: str = None,
                            output_dir: Path = None, **kwargs) -> List[Path]:
    """Process multiple SVG files with the specified animation"""
    processed_files = []

    for svg_path in svg_paths:
        # Process each file
        output_path = process_svg_file(svg_path, animation_type, output_dir, **kwargs)
        if output_path:
            processed_files.append(output_path)
            print(f"✓ Animated {svg_path.name} with {animation_type}")
        else:
            print(f"✗ Failed to animate {svg_path.name}")

    return processed_files


def create_unified_demo(animated_files: List[Path]) -> Path:
    """Create an HTML demo page showing all animations"""
    # Group files by animation type
    animation_groups = {}

    for file_path in animated_files:
        # Extract animation type from filename
        parts = file_path.name.split('_')
        if len(parts) >= 2:
            anim_type = parts[1]
            if anim_type not in animation_groups:
                animation_groups[anim_type] = []
            animation_groups[anim_type].append(file_path)

    # Create demo HTML
    demo_path = UNIFIED_ANIM_DIR / "animation_showcase.html"

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrategyDECK Animation Showcase</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
            margin: 0;
            padding: 20px;
        }
        
        h1, h2, h3 {
            color: #FF6A00;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .animation-section {
            margin-bottom: 40px;
            border-bottom: 1px solid #ddd;
            padding-bottom: 20px;
        }
        
        .icon-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
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
            height: 120px;
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
        
        .icon-type {
            font-weight: bold;
            color: #FF6A00;
            margin-bottom: 5px;
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
        
        .animation-nav {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 20px 0;
        }
        
        .animation-nav a {
            display: inline-block;
            padding: 5px 10px;
            background-color: #f0f0f0;
            border-radius: 4px;
            color: #333;
            text-decoration: none;
            font-size: 14px;
        }
        
        .animation-nav a:hover {
            background-color: #FF6A00;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>StrategyDECK Animation Showcase</h1>
        <p>Interactive demo of all animation types across the StrategyDECK system.</p>
        
        <div class="animation-controls">
            <h2>Animation Controls</h2>
            <button id="toggleAnimations" class="toggle-button">Pause All Animations</button>
            <button id="resetAnimations" class="toggle-button">Reset Animations</button>
        </div>
        
        <div class="animation-nav">
            <h3>Jump to Animation Type:</h3>
"""

    # Add navigation links
    for anim_type in animation_groups.keys():
        html += f'            <a href="#{anim_type}">{anim_type.replace("-", " ").title()}</a>\n'

    html += """
        </div>
"""

    # Add sections for each animation type
    for anim_type, files in animation_groups.items():
        # Get animation info if available
        anim_info = ANIMATION_TYPE_MAPPING.get(anim_type, {})
        module_type = anim_info.get("module", "unknown")
        category = anim_info.get("category", "unknown")

        html += f"""
        <div class="animation-section" id="{anim_type}">
            <h2>{anim_type.replace("-", " ").title()} Animation</h2>
            <p>Animation type: <strong>{category}</strong> | Module: <strong>{module_type}</strong></p>
            
            <div class="icon-grid">
"""

        for file_path in files:
            # Read SVG content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
            except Exception as e:
                print(f"Error reading SVG file {file_path}: {e}")
                continue

            # Extract original filename
            original_name = "_".join(file_path.name.split('_')[2:])

            # Add to HTML
            html += f"""
                <div class="icon-card">
                    <div class="icon-type">{anim_type.replace("-", " ").title()}</div>
                    <div class="icon-container">
                        {svg_content}
                    </div>
                    <div class="icon-label">{original_name}</div>
                </div>
"""

        html += """
            </div>
        </div>
"""

    # Add control script and close HTML
    html += """
        <script>
            // Animation control functions
            document.getElementById('toggleAnimations').addEventListener('click', function() {
                const button = document.getElementById('toggleAnimations');
                const animatedElements = document.querySelectorAll('svg [class*="-animation"]');
                
                if (button.textContent === 'Pause All Animations') {
                    animatedElements.forEach(element => {
                        element.style.animationPlayState = 'paused';
                    });
                    button.textContent = 'Resume All Animations';
                } else {
                    animatedElements.forEach(element => {
                        element.style.animationPlayState = 'running';
                    });
                    button.textContent = 'Pause All Animations';
                }
            });
            
            document.getElementById('resetAnimations').addEventListener('click', function() {
                // For CSS animations
                const animatedElements = document.querySelectorAll('svg [class*="-animation"]');
                animatedElements.forEach(element => {
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
                
                // For JavaScript animations (reload the page)
                location.reload();
            });
        </script>
    </div>
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


def create_animation_preview_ui(svg_paths: List[Path]) -> Path:
    """Create an interactive UI for previewing animations on SVGs"""
    # Create interactive HTML
    ui_path = UNIFIED_ANIM_DIR / "animation_preview_ui.html"

    # Get available animations
    animations = get_available_animations()
    animation_options = ""
    for name, info in animations.items():
        animation_options += f'<option value="{name}">{name.replace("-", " ").title()} ({info["module"]})</option>\n'

    # Create file selector options
    file_options = ""
    for i, path in enumerate(svg_paths):
        file_options += f'<option value="{i}">{path.name}</option>\n'

    # Prepare file data
    file_data = []
    for path in svg_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                svg_content = f.read()
                file_data.append({
                    "name": path.name,
                    "content": svg_content
                })
        except Exception as e:
            print(f"Error reading SVG file {path}: {e}")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrategyDECK Animation Preview</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            min-height: 100vh;
        }}
        
        .sidebar {{
            width: 300px;
            background-color: #f8f9fa;
            border-right: 1px solid #ddd;
            padding: 20px;
            overflow-y: auto;
        }}
        
        .main-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        
        .preview-container {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #f0f0f0;
            padding: 20px;
        }}
        
        .preview-svg {{
            max-width: 100%;
            max-height: 500px;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            padding: 20px;
        }}
        
        h1, h2, h3 {{
            color: #FF6A00;
        }}
        
        .control-group {{
            margin-bottom: 20px;
        }}
        
        label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }}
        
        select, input, textarea {{
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 10px;
        }}
        
        button {{
            background-color: #FF6A00;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        button:hover {{
            background-color: #CC5500;
        }}
        
        .animation-options {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }}
        
        .animation-option {{
            padding: 6px 12px;
            background-color: #f0f0f0;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .animation-option:hover {{
            background-color: #FF6A00;
            color: white;
        }}
        
        .status-message {{
            margin-top: 20px;
            padding: 10px;
            border-radius: 4px;
            background-color: #f0f0f0;
        }}
        
        .info-panel {{
            margin-top: 20px;
            background-color: #f8f9fa;
            border-top: 1px solid #ddd;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <h1>Animation Preview</h1>
        
        <div class="control-group">
            <label for="file-selector">Select SVG File</label>
            <select id="file-selector">
                {file_options}
            </select>
        </div>
        
        <div class="control-group">
            <label for="animation-type">Animation Type</label>
            <select id="animation-type">
                {animation_options}
            </select>
        </div>
        
        <div class="control-group">
            <label>Recommended Animations</label>
            <div id="recommended-animations" class="animation-options">
                <!-- Will be populated dynamically -->
            </div>
        </div>
        
        <div class="control-group">
            <label for="duration">Duration (seconds)</label>
            <input type="number" id="duration" value="3" min="0.1" step="0.1">
        </div>
        
        <div class="control-group">
            <label for="target-element">Target Elements</label>
            <select id="target-element">
                <option value="all">All Elements</option>
                <option value="foreground">Foreground Elements</option>
                <option value="background">Background Elements</option>
                <option value="all-paths">All Paths</option>
                <option value="foreground-paths">Foreground Paths</option>
            </select>
        </div>
        
        <button id="apply-animation">Apply Animation</button>
        <button id="reset-preview">Reset Preview</button>
        
        <div id="status-message" class="status-message">
            Select a file and animation to begin
        </div>
    </div>
    
    <div class="main-content">
        <div class="preview-container">
            <div class="preview-svg" id="preview-container">
                <!-- SVG will be shown here -->
                <p>Select an SVG file to preview</p>
            </div>
        </div>
        
        <div class="info-panel">
            <h3>SVG Analysis</h3>
            <div id="svg-analysis">
                <!-- Analysis will be shown here -->
            </div>
        </div>
    </div>
    
    <script>
        // SVG file data
        const svgFiles = {json.dumps(file_data)};
        
        // DOM elements
        const fileSelector = document.getElementById('file-selector');
        const animationType = document.getElementById('animation-type');
        const duration = document.getElementById('duration');
        const targetElement = document.getElementById('target-element');
        const applyButton = document.getElementById('apply-animation');
        const resetButton = document.getElementById('reset-preview');
        const previewContainer = document.getElementById('preview-container');
        const statusMessage = document.getElementById('status-message');
        const svgAnalysis = document.getElementById('svg-analysis');
        const recommendedAnimations = document.getElementById('recommended-animations');
        
        // Current SVG content
        let currentSvgContent = '';
        let originalSvgContent = '';
        
        // Initialize with first file
        if (svgFiles.length > 0) {{
            loadSvgFile(0);
        }}
        
        // File selector change
        fileSelector.addEventListener('change', function() {{
            loadSvgFile(parseInt(this.value));
        }});
        
        // Apply animation button
        applyButton.addEventListener('click', function() {{
            applyAnimation();
        }});
        
        // Reset button
        resetButton.addEventListener('click', function() {{
            previewContainer.innerHTML = originalSvgContent;
            currentSvgContent = originalSvgContent;
            statusMessage.textContent = 'Preview reset to original SVG';
        }});
        
        // Function to load an SVG file
        function loadSvgFile(index) {{
            if (index >= 0 && index < svgFiles.length) {{
                const file = svgFiles[index];
                originalSvgContent = file.content;
                currentSvgContent = file.content;
                previewContainer.innerHTML = file.content;
                
                // Analyze SVG
                analyzeSvg(file.content);
                
                statusMessage.textContent = `Loaded: ${{file.name}}`;
            }}
        }}
        
        // Function to analyze SVG
        function analyzeSvg(svgContent) {{
            // This is a simplified client-side analysis
            // In a real implementation, you would call the server-side analyze_svg_content function
            
            // Count elements
            const parser = new DOMParser();
            const svgDoc = parser.parseFromString(svgContent, "image/svg+xml");
            
            const paths = svgDoc.querySelectorAll('path').length;
            const circles = svgDoc.querySelectorAll('circle').length;
            const rects = svgDoc.querySelectorAll('rect').length;
            const polygons = svgDoc.querySelectorAll('polygon').length;
            
            // Determine if path-heavy
            const pathHeavy = paths > (circles + rects + polygons);
            
            // Look for potential themes
            const themes = ['biome', 'urban', 'mystic', 'cosmic', 'raid', 
                           'shadow', 'primal', 'underworld', 'renaissance'];
            const potentialThemes = [];
            
            for (const theme of themes) {{
                if (svgContent.toLowerCase().includes(theme)) {{
                    potentialThemes.push(theme);
                }}
            }}
            
            // Determine if it's glyph-like
            const isGlyphLike = potentialThemes.length > 0 || 
                               svgContent.toLowerCase().includes('glyph');
            
            // Recommend animations
            const recommendations = [];
            
            if (pathHeavy) {{
                if (paths === 1) {{
                    recommendations.push('draw', 'pulse-path', 'flow');
                }} else {{
                    recommendations.push('morph-geometric', 'reveal', 'wave');
                }}
            }}
            
            if (isGlyphLike) {{
                for (const theme of potentialThemes) {{
                    recommendations.push(`${{theme}}-pulsar`);
                }}
            }}
            
            if (circles > 0) {{
                recommendations.push('pulse');
            }}
            recommendations.push('rotate', 'fade', 'color-shift');
            
            // Display analysis
            svgAnalysis.innerHTML = `
                <p><strong>Elements:</strong> ${{paths}} paths, ${{circles}} circles, ${{rects}} rectangles, ${{polygons}} polygons</p>
                <p><strong>Path-heavy:</strong> ${{pathHeavy ? 'Yes' : 'No'}}</p>
                <p><strong>Glyph-like:</strong> ${{isGlyphLike ? 'Yes' : 'No'}}</p>
                <p><strong>Potential themes:</strong> ${{potentialThemes.length ? potentialThemes.join(', ') : 'None detected'}}</p>
            `;
            
            // Display recommended animations
            recommendedAnimations.innerHTML = '';
            const uniqueRecs = [...new Set(recommendations)].slice(0, 5);
            
            for (const rec of uniqueRecs) {{
                const option = document.createElement('div');
                option.className = 'animation-option';
                option.textContent = rec.replace('-', ' ').replace(/\\b\\w/g, c => c.toUpperCase());
                option.onclick = function() {{
                    animationType.value = rec;
                    applyAnimation();
                }};
                recommendedAnimations.appendChild(option);
            }}
        }}
        
        // Function to apply animation
        function applyAnimation() {{
            const type = animationType.value;
            const durationValue = `${{duration.value}}s`;
            const target = targetElement.value;
            
            // Show status
            statusMessage.textContent = `Applying ${{type}} animation...`;
            
            // In a real implementation, this would call the server-side apply_animation function
            // For this demo, we'll simulate by adding a simple CSS animation
            
            setTimeout(() => {{
                // Simulate animation by adding a style tag
                let animatedSvg = originalSvgContent;
                
                // Add a style tag with animation
                const styleTag = `<style>
                    @keyframes ${{type}}-anim {{
                        0% {{ opacity: 1; transform: scale(1); }}
                        50% {{ opacity: 0.8; transform: scale(1.1); }}
                        100% {{ opacity: 1; transform: scale(1); }}
                    }}
                    
                    path, circle, rect, polygon, ellipse {{
                        animation: ${{type}}-anim ${{durationValue}} ease-in-out infinite;
                        transform-origin: center;
                        transform-box: fill-box;
                    }}
                </style>`;
                
                animatedSvg = animatedSvg.replace('</svg>', `${{styleTag}}</svg>`);
                
                // Update the preview
                previewContainer.innerHTML = animatedSvg;
                currentSvgContent = animatedSvg;
                
                statusMessage.textContent = `Applied ${{type}} animation with ${{durationValue}} duration`;
            }}, 500);
        }}
    </script>
</body>
</html>
"""

    # Write the HTML file
    try:
        with open(ui_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return ui_path
    except Exception as e:
        print(f"Error writing UI HTML to {ui_path}: {e}")
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="StrategyDECK Animation System Integration")

    parser.add_argument(
        "--svg", type=str, help="SVG file or directory to animate")
    parser.add_argument(
        "--animation", help="Animation type to apply")
    parser.add_argument(
        "--target", action="append",
        help="Target elements to animate (e.g., all, foreground, background)")
    parser.add_argument(
        "--duration", type=str, help="Custom animation duration (e.g., 2s, 500ms)")
    parser.add_argument(
        "--demo", action="store_true", help="Create a demo showcase")
    parser.add_argument(
        "--preview", action="store_true", help="Create an interactive preview UI")
    parser.add_argument(
        "--list", action="store_true", help="List available animations")
    parser.add_argument(
        "--analyze", action="store_true", help="Analyze SVG and recommend animations")
    parser.add_argument(
        "--open", action="store_true", help="Open the resulting file in a browser")

    args = parser.parse_args()

    if args.list:
        # List available animations
        animations = get_available_animations()

        print("\nAvailable Animations in StrategyDECK System:")
        print("============================================")

        # Group by module
        by_module = {}
        for name, info in animations.items():
            module = info.get("module", "unknown")
            if module not in by_module:
                by_module[module] = []
            by_module[module].append((name, info))

        # Print grouped list
        for module, anims in by_module.items():
            print(f"\n{module.upper()} ANIMATIONS:")
            print("-" * (len(module) + 11))

            for name, info in anims:
                desc = info.get("description", "")
                duration = info.get("duration", "?")
                print(f"  - {name:20} | Duration: {duration:5} | {desc}")

        return 0

    if args.svg:
        svg_path = Path(args.svg)

        # Handle directory vs file
        if svg_path.is_dir():
            # Find all SVG files in directory
            svg_files = list(svg_path.glob("**/*.svg"))
            if not svg_files:
                print(f"Error: No SVG files found in directory: {svg_path}")
                return 1
            print(f"Found {len(svg_files)} SVG files in {svg_path}")
        elif svg_path.exists() and svg_path.suffix.lower() == '.svg':
            # Single file
            svg_files = [svg_path]
        else:
            print(f"Error: Invalid SVG path: {svg_path}")
            return 1

        if args.analyze:
            # Analyze SVG files
            for svg_file in svg_files:
                try:
                    with open(svg_file, 'r', encoding='utf-8') as f:
                        svg_content = f.read()

                    print(f"\nAnalysis for {svg_file.name}:")
                    print("-" * (len(svg_file.name) + 12))

                    analysis = analyze_svg_content(svg_content)

                    print(f"Elements: {analysis['elements']['paths']} paths, "
                          f"{analysis['elements']['circles']} circles, "
                          f"{analysis['elements']['rectangles']} rectangles, "
                          f"{analysis['elements']['polygons']} polygons")
                    print(f"Path-heavy: {analysis['path_heavy']}")
                    print(f"Glyph-like: {analysis['is_glyph_like']}")

                    if analysis['potential_themes']:
                        print(
                            f"Potential themes: {', '.join(analysis['potential_themes'])}")
                    else:
                        print("Potential themes: None detected")

                    print("\nRecommended animations:")
                    for anim in analysis['recommended_animations']:
                        anim_info = ANIMATION_TYPE_MAPPING.get(anim, {})
                        module = anim_info.get("module", "unknown")
                        print(f"  - {anim:15} ({module})")

                except Exception as e:
                    print(f"Error analyzing {svg_file}: {e}")

            return 0

        elif args.preview:
            # Create interactive preview UI
            ui_path = create_animation_preview_ui(svg_files)
            if ui_path:
                print(f"Created interactive preview UI at: {ui_path}")

                if args.open:
                    try:
                        import webbrowser
                        webbrowser.open(f"file://{ui_path.absolute()}")
                        print(f"Opened preview UI in browser")
                    except Exception as e:
                        print(f"Error opening UI in browser: {e}")

            return 0

        elif args.demo:
            # Create demo showcase
            # Process all files with various animations first
            processed_files = []

            # Use a selection of animations
            animations_to_use = ["pulse", "rotate", "fade", "color-shift"]

            # Add path animations if available
            if PATH_ANIMATIONS_AVAILABLE:
                animations_to_use.extend(["draw", "flow", "reveal", "orbit"])

            for animation in animations_to_use:
                files = batch_process_svg_files(
                    svg_files[:5],  # Limit to 5 files per animation type
                    animation,
                    target_elements=args.target,
                    custom_duration=args.duration
                )
                processed_files.extend(files)

            # Create demo HTML
            demo_path = create_unified_demo(processed_files)
            if demo_path:
                print(f"Created demo showcase at: {demo_path}")

                if args.open:
                    try:
                        import webbrowser
                        webbrowser.open(f"file://{demo_path.absolute()}")
                        print(f"Opened demo showcase in browser")
                    except Exception as e:
                        print(f"Error opening demo in browser: {e}")

            return 0

        else:
            # Process files with specified animation
            processed_files = batch_process_svg_files(
                svg_files,
                args.animation,
                target_elements=args.target,
                custom_duration=args.duration
            )

            # Print summary
            print(
                f"\nSuccessfully animated {len(processed_files)} of {len(svg_files)} SVG files")

            # Open first file if requested
            if args.open and processed_files:
                try:
                    import webbrowser
                    webbrowser.open(f"file://{processed_files[0].absolute()}")
                    print(f"Opened animated SVG in browser")
                except Exception as e:
                    print(f"Error opening SVG in browser: {e}")

            return 0

    else:
        # No SVG specified, show help
        parser.print_help()

        # If --list was specified, we already showed the list
        if not args.list:
            print("\nTip: Use --list to see available animations")
            print("     Use --svg to specify an SVG file or directory")

        return 1


if __name__ == "__main__":
    sys.exit(main())
