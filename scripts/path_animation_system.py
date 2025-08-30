#!/usr/bin/env python3
"""
StrategyDECK Path Animation System

This module provides advanced path-based animations for SVG icons and glyphs,
allowing for morphing between shapes, path following, stroke animations,
and other complex SVG path effects.

Features:
- Path morphing between different shapes
- Path following for elements (motion along a defined path)
- Stroke dash animations (drawing effects)
- Path extrusion and 3D-like effects
- Synchronized multi-path animations
- Interactive path manipulation
"""

import json
import math
import os
import random
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(ROOT))

# Try to import animate_icons
try:
    from animate_icons import (
        ANIMATION_PRESETS,
        add_animation_to_svg,
        generate_animation_css,
        parse_svg,
    )
except ImportError:
    print("Error: Could not import from animate_icons.py")
    print("Make sure animate_icons.py exists in the workspace")
    sys.exit(1)

# Output directories
ASSETS_DIR = ROOT / "assets"
ANIMATED_DIR = ASSETS_DIR / "animated"
PATH_ANIM_DIR = ANIMATED_DIR / "path_animations"

# Ensure the path animation directory exists
PATH_ANIM_DIR.mkdir(parents=True, exist_ok=True)

# Path animation presets
PATH_ANIMATION_PRESETS = {
    "draw": {
        "type": "stroke-dash",
        "keyframes": [
            {"time": "0%", "dash-offset": "1000"},
            {"time": "100%", "dash-offset": "0"}
        ],
        "duration": "4s",
        "iteration": "infinite",
        "timing": "ease-in-out"
    },
    "flow": {
        "type": "stroke-flow",
        "keyframes": [
            {"time": "0%", "dash-offset": "0"},
            {"time": "100%", "dash-offset": "1000"}
        ],
        "duration": "7s",
        "iteration": "infinite",
        "timing": "linear"
    },
    "reveal": {
        "type": "stroke-dash",
        "keyframes": [
            {"time": "0%", "dash-offset": "1000", "dash-array": "1000 1000"},
            {"time": "50%", "dash-offset": "0", "dash-array": "1000 1000"},
            {"time": "50.1%", "dash-offset": "0", "dash-array": "0 1000"},
            {"time": "100%", "dash-offset": "0", "dash-array": "0 1000"}
        ],
        "duration": "5s",
        "iteration": "infinite",
        "timing": "ease-in-out"
    },
    "pulse-path": {
        "type": "stroke-width",
        "keyframes": [
            {"time": "0%", "stroke-width": "1"},
            {"time": "50%", "stroke-width": "4"},
            {"time": "100%", "stroke-width": "1"}
        ],
        "duration": "2s",
        "iteration": "infinite",
        "timing": "ease-in-out"
    },
    "morph-geometric": {
        "type": "path-morph",
        "shapes": [
            "M50,10 L90,50 L50,90 L10,50 Z",  # Diamond
            "M25,25 L75,25 L75,75 L25,75 Z",  # Square
            "M50,10 L90,90 L10,90 Z",         # Triangle
            "M50,10 L90,50 L50,90 L10,50 Z"   # Diamond
        ],
        "duration": "8s",
        "iteration": "infinite",
        "timing": "ease-in-out"
    },
    "morph-organic": {
        "type": "path-morph",
        "shapes": [
            "M50,10 Q65,40 80,40 Q65,60 80,90 Q50,80 20,90 Q35,60 20,40 Q35,40 50,10",  # Organic 1
            "M25,40 Q40,20 50,40 Q60,10 75,40 Q95,65 75,80 Q60,95 50,70 Q40,95 25,80 Q5,65 25,40",  # Organic 2
            "M50,15 Q80,15 80,50 Q80,80 50,85 Q20,80 20,50 Q20,15 50,15",  # Blob
            "M50,10 Q65,40 80,40 Q65,60 80,90 Q50,80 20,90 Q35,60 20,40 Q35,40 50,10"   # Organic 1
        ],
        "duration": "12s",
        "iteration": "infinite",
        "timing": "ease-in-out"
    },
    "follow-path": {
        "type": "motion-path",
        "path": "M10,50 C20,30 40,30 50,50 C60,70 80,70 90,50",
        "duration": "6s",
        "iteration": "infinite",
        "timing": "ease-in-out",
        "rotateAuto": True
    },
    "orbit": {
        "type": "motion-path",
        "path": "M50,10 A40,40 0 0 1 90,50 A40,40 0 0 1 50,90 A40,40 0 0 1 10,50 A40,40 0 0 1 50,10 Z",
        "duration": "10s",
        "iteration": "infinite",
        "timing": "linear",
        "rotateAuto": True
    },
    "zigzag": {
        "type": "motion-path",
        "path": "M10,50 L30,30 L50,70 L70,30 L90,50",
        "duration": "5s",
        "iteration": "infinite",
        "timing": "ease-in-out",
        "rotateAuto": False
    },
    "wave": {
        "type": "path-transform",
        "transforms": [
            {"translate": [0, 0], "scale": 1, "rotate": 0},
            {"translate": [0, -10], "scale": 1.05, "rotate": 5},
            {"translate": [0, 0], "scale": 1, "rotate": 0},
            {"translate": [0, 10], "scale": 0.95, "rotate": -5},
            {"translate": [0, 0], "scale": 1, "rotate": 0}
        ],
        "duration": "4s",
        "iteration": "infinite",
        "timing": "ease-in-out"
    }
}


def get_path_length(d: str) -> float:
    """
    Estimate the length of an SVG path.
    This is a simplified approximation for animation purposes.
    """
    # Simple approximation based on the length of the path string
    # For more accurate results, we would need a proper path parsing library
    return len(d) * 2


def normalize_path(d: str) -> str:
    """
    Normalize SVG path data to make it easier to manipulate.
    Converts relative commands to absolute, etc.
    """
    # This is a simplified implementation
    # In a real-world scenario, you'd use a proper SVG path parser
    return d


def generate_path_keyframes(path_data: str, keyframes_count: int = 10) -> List[str]:
    """
    Generate intermediate path data for morphing animations.
    This creates interpolated paths between random variations of the original.
    """
    keyframes = [path_data]

    for _ in range(keyframes_count - 1):
        # Create a slightly transformed path for morphing
        transformed = path_data.replace(
            r'([0-9]+(\.[0-9]+)?)',
            lambda m: str(float(m.group(0)) + (random.random() - 0.5) * 5),
            count=10  # Only transform some values to keep the shape recognizable
        )
        keyframes.append(transformed)

    return keyframes


def apply_path_animation(svg_content: str, animation_type: str, target_elements: List[str] = None,
                         custom_duration: str = None) -> str:
    """
    Apply path-specific animation to an SVG.
    """
    # Parse SVG
    root = parse_svg(svg_content)
    if root is None:
        return svg_content

    # Get animation preset
    preset = PATH_ANIMATION_PRESETS.get(animation_type)
    if preset is None:
        print(f"Unknown path animation type: {animation_type}")
        return svg_content

    # Create a unique ID for this animation
    animation_id = f"strategydeck-path-{animation_type}-{uuid.uuid4().hex[:8]}"

    # Modify preset if custom duration is provided
    if custom_duration:
        preset = preset.copy()
        preset["duration"] = custom_duration

    # Find the elements to animate
    path_elements = []

    # If target elements are specified, find them
    if target_elements:
        for target in target_elements:
            if target == "all-paths":
                # Add all paths
                for path in root.findall(".//path"):
                    path_elements.append(path)
            elif target.startswith("#"):
                # Find by ID
                element_id = target[1:]
                for element in root.findall(".//*[@id='{}']".format(element_id)):
                    if element.tag.endswith('path'):
                        path_elements.append(element)
            elif target == "foreground-paths":
                # Find all paths except in background elements
                background_rect = root.find(".//rect")
                for path in root.findall(".//path"):
                    if path != background_rect:
                        path_elements.append(path)
    else:
        # Default: animate all path elements
        for path in root.findall(".//path"):
            path_elements.append(path)

    # Apply animation based on type
    if preset["type"] == "stroke-dash" or preset["type"] == "stroke-flow":
        # Add dash array and dash offset animations
        for path in path_elements:
            # Get the path data
            path_data = path.get("d", "")
            if not path_data:
                continue

            # Calculate path length for dash array
            path_length = get_path_length(path_data)

            # Set initial dash array and offset
            if "dash-array" not in preset["keyframes"][0]:
                path.set("stroke-dasharray", f"{path_length}")

            # Create a unique animation class for this path
            path_anim_id = f"{animation_id}-{path_elements.index(path)}"

            # Add the animation class
            current_class = path.get("class", "")
            if current_class:
                path.set("class", f"{current_class} {path_anim_id}-animation")
            else:
                path.set("class", f"{path_anim_id}-animation")

            # Create custom keyframes for this path
            path_preset = preset.copy()
            for kf in path_preset["keyframes"]:
                if "dash-array" in kf:
                    kf["dash-array"] = kf["dash-array"].replace(
                        "1000", str(path_length))
                if "dash-offset" in kf:
                    kf["dash-offset"] = kf["dash-offset"].replace(
                        "1000", str(path_length))

            # Generate CSS animation
            path_css = generate_path_animation_css(path_anim_id, path_preset)

            # Store CSS for later insertion
            if not hasattr(root, "path_animations"):
                root.path_animations = []
            root.path_animations.append(path_css)

    elif preset["type"] == "stroke-width":
        # Add stroke width animation
        for path in path_elements:
            # Make sure the path has a stroke
            if not path.get("stroke"):
                if path.get("fill") and path.get("fill") != "none":
                    # Use fill color for stroke
                    path.set("stroke", path.get("fill"))
                else:
                    # Default stroke color
                    path.set("stroke", "#000000")

            # Create a unique animation class for this path
            path_anim_id = f"{animation_id}-{path_elements.index(path)}"

            # Add the animation class
            current_class = path.get("class", "")
            if current_class:
                path.set("class", f"{current_class} {path_anim_id}-animation")
            else:
                path.set("class", f"{path_anim_id}-animation")

            # Generate CSS animation
            path_css = generate_path_animation_css(path_anim_id, preset)

            # Store CSS for later insertion
            if not hasattr(root, "path_animations"):
                root.path_animations = []
            root.path_animations.append(path_css)

    elif preset["type"] == "path-morph":
        # Add path morphing JavaScript
        js_code = generate_morph_js(animation_id, preset["shapes"])

        # Apply to selected paths
        for path in path_elements:
            # Need to ensure each path has an ID
            if not path.get("id"):
                path.set("id", f"morph-path-{uuid.uuid4().hex[:8]}")

            # Flag this path for morphing
            path.set("class", f"{path.get('class', '')} {animation_id}-morph")

            # Store original path data
            path.set("data-original-d", path.get("d", ""))

        # Add JS script tag
        if not hasattr(root, "scripts"):
            root.scripts = []
        root.scripts.append(js_code)

    elif preset["type"] == "motion-path":
        # For motion path, we'll create a separate element that moves along a path
        for i, element in enumerate(path_elements):
            # Skip if this is the path we're following
            if i == 0 and len(path_elements) > 1:
                continue

            # Get element ID or create one
            element_id = element.get("id")
            if not element_id:
                element_id = f"motion-element-{uuid.uuid4().hex[:8]}"
                element.set("id", element_id)

            # Create a unique animation ID
            motion_anim_id = f"{animation_id}-{i}"

            # Add motion path JS
            js_code = generate_motion_path_js(
                motion_anim_id,
                element_id,
                preset["path"],
                float(preset["duration"].replace("s", "")),
                preset.get("rotateAuto", False)
            )

            # Add JS script tag
            if not hasattr(root, "scripts"):
                root.scripts = []
            root.scripts.append(js_code)

    elif preset["type"] == "path-transform":
        # Add transform animation
        for path in path_elements:
            # Create a unique animation class for this path
            path_anim_id = f"{animation_id}-{path_elements.index(path)}"

            # Add the animation class
            current_class = path.get("class", "")
            if current_class:
                path.set("class", f"{current_class} {path_anim_id}-animation")
            else:
                path.set("class", f"{path_anim_id}-animation")

            # Generate CSS for path transforms
            css = generate_transform_css(path_anim_id, preset)

            # Store CSS for later insertion
            if not hasattr(root, "path_animations"):
                root.path_animations = []
            root.path_animations.append(css)

    # Serialize the updated SVG
    serialized = ET.tostring(root, encoding="unicode")

    # Reinsert the SVG namespace
    serialized = serialized.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"')

    # Add the style tag with animations if any
    if hasattr(root, "path_animations") and root.path_animations:
        style_content = "\n".join(root.path_animations)
        style_tag = f"<style>\n{style_content}</style>"
        serialized = serialized.replace("</svg>", f"{style_tag}</svg>")

    # Add scripts if any
    if hasattr(root, "scripts") and root.scripts:
        script_content = "\n".join(root.scripts)
        serialized = serialized.replace("</svg>", f"{script_content}</svg>")

    return serialized


def generate_path_animation_css(animation_id: str, preset: Dict) -> str:
    """Generate CSS for path-specific animations"""
    animation_type = preset["type"]
    keyframes = preset["keyframes"]
    duration = preset.get("duration", "3s")
    iteration = preset.get("iteration", "infinite")
    timing = preset.get("timing", "ease-in-out")

    # Build keyframes CSS
    keyframes_css = f"@keyframes {animation_id} {{\n"

    for keyframe in keyframes:
        time = keyframe["time"]
        keyframes_css += f"  {time} {{\n"

        if animation_type == "stroke-dash" or animation_type == "stroke-flow":
            if "dash-array" in keyframe:
                keyframes_css += f"    stroke-dasharray: {keyframe['dash-array']};\n"
            if "dash-offset" in keyframe:
                keyframes_css += f"    stroke-dashoffset: {keyframe['dash-offset']};\n"
        elif animation_type == "stroke-width":
            if "stroke-width" in keyframe:
                keyframes_css += f"    stroke-width: {keyframe['stroke-width']};\n"

        keyframes_css += "  }\n"

    keyframes_css += "}\n"

    # Add animation application class
    animation_class = f".{animation_id}-animation {{\n"
    animation_class += f"  animation: {animation_id} {duration} {timing} {iteration};\n"

    # Add specific styles based on animation type
    if animation_type == "stroke-dash" or animation_type == "stroke-flow":
        animation_class += "  fill: none;\n"  # Ensure the fill doesn't obscure the stroke
        animation_class += "  stroke-linecap: round;\n"  # Rounded line caps look better

    animation_class += "}\n"

    return keyframes_css + animation_class


def generate_transform_css(animation_id: str, preset: Dict) -> str:
    """Generate CSS for transform animations"""
    transforms = preset["transforms"]
    duration = preset.get("duration", "3s")
    iteration = preset.get("iteration", "infinite")
    timing = preset.get("timing", "ease-in-out")

    # Build keyframes CSS
    keyframes_css = f"@keyframes {animation_id} {{\n"

    for i, transform in enumerate(transforms):
        # Calculate percentage for this keyframe
        percentage = int(100 * i / (len(transforms) - 1)) if len(transforms) > 1 else 0
        keyframes_css += f"  {percentage}% {{\n"

        # Add transform properties
        transform_value = ""
        if "translate" in transform:
            tx, ty = transform["translate"]
            transform_value += f"translate({tx}px, {ty}px) "
        if "scale" in transform:
            transform_value += f"scale({transform['scale']}) "
        if "rotate" in transform:
            transform_value += f"rotate({transform['rotate']}deg) "

        keyframes_css += f"    transform: {transform_value.strip()};\n"
        keyframes_css += "  }\n"

    keyframes_css += "}\n"

    # Add animation application class
    animation_class = f".{animation_id}-animation {{\n"
    animation_class += f"  animation: {animation_id} {duration} {timing} {iteration};\n"
    animation_class += "  transform-origin: center;\n"
    animation_class += "  transform-box: fill-box;\n"
    animation_class += "}\n"

    return keyframes_css + animation_class


def generate_morph_js(animation_id: str, shapes: List[str]) -> str:
    """Generate JavaScript for path morphing"""
    shapes_json = json.dumps(shapes)

    return f"""
<script>
(function() {{
    // Path morphing shapes
    const shapes = {shapes_json};
    
    // Get all paths marked for morphing
    const morphPaths = document.querySelectorAll('.{animation_id}-morph');
    
    // Set up morphing animation
    morphPaths.forEach(path => {{
        let currentShapeIndex = 0;
        let isAnimating = false;
        
        // Save original path if not already saved
        if (!path.getAttribute('data-original-d')) {{
            path.setAttribute('data-original-d', path.getAttribute('d'));
        }}
        
        // Function to animate to the next shape
        function animateToNextShape() {{
            if (isAnimating) return;
            
            // Get current and next shape
            const currentShape = shapes[currentShapeIndex];
            currentShapeIndex = (currentShapeIndex + 1) % shapes.length;
            const nextShape = shapes[currentShapeIndex];
            
            // Mark as animating
            isAnimating = true;
            
            // Animate to next shape
            const startTime = performance.now();
            const duration = {float(preset.get('duration', '5s').replace('s', '')) * 1000 / len(shapes)};
            
            function animate(time) {{
                const elapsed = time - startTime;
                const progress = Math.min(elapsed / duration, 1);
                
                // Use easing function
                const easedProgress = 0.5 - 0.5 * Math.cos(progress * Math.PI);
                
                // Set the path data
                if (progress < 1) {{
                    requestAnimationFrame(animate);
                }} else {{
                    // Animation complete
                    path.setAttribute('d', nextShape);
                    isAnimating = false;
                    
                    // Wait before animating to next shape
                    setTimeout(animateToNextShape, 100);
                }}
            }}
            
            // Start animation
            requestAnimationFrame(animate);
        }}
        
        // Start the animation loop
        setTimeout(animateToNextShape, 100);
    }});
}})();
</script>
"""


def generate_motion_path_js(animation_id: str, element_id: str, path_data: str,
                            duration: float, rotate_auto: bool) -> str:
    """Generate JavaScript for motion path animation"""
    return f"""
<script>
(function() {{
    // Motion path animation for element {element_id}
    const element = document.getElementById('{element_id}');
    if (!element) return;
    
    // Create a hidden path to follow
    const svgNS = "http://www.w3.org/2000/svg";
    const motionPath = document.createElementNS(svgNS, "path");
    motionPath.setAttribute("d", "{path_data}");
    motionPath.setAttribute("fill", "none");
    motionPath.setAttribute("stroke", "none");
    motionPath.setAttribute("id", "{animation_id}-path");
    element.parentNode.appendChild(motionPath);
    
    // Get the total length of the path
    const pathLength = motionPath.getTotalLength();
    
    // Get the original position and transformations
    const originalTransform = element.getAttribute('transform') || '';
    
    // Animation variables
    let startTime = null;
    const animDuration = {duration * 1000};
    const rotateAuto = {str(rotate_auto).lower()};
    
    // Animation function
    function animateMotion(timestamp) {{
        if (!startTime) startTime = timestamp;
        
        // Calculate progress
        const elapsed = (timestamp - startTime) % animDuration;
        const progress = elapsed / animDuration;
        
        // Get point on path
        const point = motionPath.getPointAtLength(progress * pathLength);
        
        // Calculate rotation if needed
        let rotation = "";
        if (rotateAuto) {{
            // Get angle by sampling two close points
            const pointAhead = motionPath.getPointAtLength(Math.min((progress + 0.01) * pathLength, pathLength));
            const angle = Math.atan2(pointAhead.y - point.y, pointAhead.x - point.x) * 180 / Math.PI;
            rotation = ` rotate(${{angle}} ${{point.x}} ${{point.y}})`;
        }}
        
        // Apply transformation
        element.setAttribute('transform', `translate(${{point.x}} ${{point.y}})${{rotation}} ${{originalTransform}}`);
        
        // Continue animation
        requestAnimationFrame(animateMotion);
    }}
    
    // Start animation
    requestAnimationFrame(animateMotion);
}})();
</script>
"""


def apply_path_animation_to_svg(svg_path: Path, animation_type: str, output_dir: Path = None,
                                target_elements: List[str] = None, custom_duration: str = None) -> Path:
    """Apply path animation to an SVG file and save the result"""
    # Read the SVG file
    try:
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
    except Exception as e:
        print(f"Error reading SVG file {svg_path}: {e}")
        return None

    # Apply animation
    animated_svg = apply_path_animation(
        svg_content,
        animation_type,
        target_elements,
        custom_duration
    )

    # Create output path
    if output_dir is None:
        output_dir = PATH_ANIM_DIR

    output_path = output_dir / f"path_{animation_type}_{svg_path.name}"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the animated SVG
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(animated_svg)
        return output_path
    except Exception as e:
        print(f"Error writing animated SVG to {output_path}: {e}")
        return None


def create_path_animation_demo(svg_paths: List[Path], animation_types: List[str] = None) -> Path:
    """Create an HTML demo page showing path animations"""
    if animation_types is None:
        animation_types = list(PATH_ANIMATION_PRESETS.keys())

    # Process each SVG with each animation type
    animated_files = []
    for svg_path in svg_paths:
        for animation_type in animation_types:
            output_path = apply_path_animation_to_svg(
                svg_path,
                animation_type
            )
            if output_path:
                animated_files.append(output_path)

    # Create demo HTML
    demo_path = PATH_ANIM_DIR / "path_animation_demo.html"

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrategyDECK Path Animation Demo</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h1>StrategyDECK Path Animation Demo</h1>
        <p>Interactive demo of advanced SVG path animations.</p>
        
        <div class="animation-controls">
            <h2>Animation Controls</h2>
            <button id="toggleAnimations" class="toggle-button">Pause All Animations</button>
            <button id="resetAnimations" class="toggle-button">Reset Animations</button>
        </div>
"""

    # Group by animation type
    grouped_files = {}
    for file_path in animated_files:
        # Extract animation type from filename
        anim_type = file_path.name.split('_')[1]
        if anim_type not in grouped_files:
            grouped_files[anim_type] = []
        grouped_files[anim_type].append(file_path)

    # Add sections for each animation type
    for anim_type, files in grouped_files.items():
        html += f"""
        <div class="animation-section">
            <h2>{anim_type.replace('-', ' ').title()} Animation</h2>
            <p>{PATH_ANIMATION_PRESETS[anim_type]["type"].replace('-', ' ').title()} effect with {PATH_ANIMATION_PRESETS[anim_type]["duration"]} duration.</p>
            
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
            original_name = file_path.name.split('_', 2)[-1]

            # Add to HTML
            html += f"""
                <div class="icon-card">
                    <div class="icon-type">{anim_type.replace('-', ' ').title()}</div>
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


def generate_interactive_path_editor(svg_path: Path) -> Path:
    """Generate an interactive HTML editor for path animations"""
    # Read the SVG file
    try:
        with open(svg_path, 'r', encoding='utf-8') as f:
            svg_content = f.read()
    except Exception as e:
        print(f"Error reading SVG file {svg_path}: {e}")
        return None

    # Create editor HTML
    editor_path = PATH_ANIM_DIR / f"editor_{svg_path.name.replace('.svg', '.html')}"

    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrategyDECK Path Animation Editor</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            display: flex;
            height: 100vh;
        }
        
        .editor-sidebar {
            width: 300px;
            background-color: #f8f9fa;
            border-right: 1px solid #ddd;
            padding: 20px;
            overflow-y: auto;
        }
        
        .preview-area {
            flex: 1;
            padding: 20px;
            display: flex;
            flex-direction: column;
        }
        
        .preview-container {
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #f0f0f0;
            border-radius: 8px;
            overflow: hidden;
        }
        
        h1, h2, h3 {
            color: #FF6A00;
        }
        
        .control-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        select, input, textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        
        button {
            background-color: #FF6A00;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            margin-right: 10px;
        }
        
        button:hover {
            background-color: #CC5500;
        }
        
        .button-group {
            margin-top: 20px;
        }
        
        .code-output {
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            font-family: monospace;
            white-space: pre-wrap;
            margin-top: 20px;
            max-height: 200px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="editor-sidebar">
        <h1>Path Animation Editor</h1>
        
        <div class="control-group">
            <label for="animation-type">Animation Type</label>
            <select id="animation-type">
                <option value="draw">Draw (Stroke Dash)</option>
                <option value="flow">Flow (Continuous)</option>
                <option value="reveal">Reveal (Appear)</option>
                <option value="pulse-path">Pulse (Stroke Width)</option>
                <option value="morph-geometric">Morph (Geometric)</option>
                <option value="morph-organic">Morph (Organic)</option>
                <option value="follow-path">Follow Path</option>
                <option value="orbit">Orbit</option>
                <option value="zigzag">Zigzag</option>
                <option value="wave">Wave Transform</option>
            </select>
        </div>
        
        <div class="control-group">
            <label for="duration">Duration (seconds)</label>
            <input type="number" id="duration" value="5" min="0.1" step="0.1">
        </div>
        
        <div class="control-group">
            <label for="timing">Timing Function</label>
            <select id="timing">
                <option value="linear">Linear</option>
                <option value="ease" selected>Ease</option>
                <option value="ease-in">Ease In</option>
                <option value="ease-out">Ease Out</option>
                <option value="ease-in-out">Ease In Out</option>
            </select>
        </div>
        
        <div class="control-group">
            <label for="target-element">Target Element</label>
            <select id="target-element">
                <option value="all-paths">All Paths</option>
                <option value="foreground-paths">Foreground Paths</option>
            </select>
        </div>
        
        <div class="button-group">
            <button id="apply-animation">Apply Animation</button>
            <button id="reset">Reset</button>
        </div>
        
        <div class="control-group">
            <label for="code-output">Animation Code</label>
            <div id="code-output" class="code-output">// Animation code will appear here</div>
        </div>
        
        <div class="button-group">
            <button id="copy-code">Copy Code</button>
            <button id="download-svg">Download SVG</button>
        </div>
    </div>
    
    <div class="preview-area">
        <h2>Preview</h2>
        <div class="preview-container" id="preview">
            <!-- SVG will be inserted here -->
        </div>
    </div>
    
    <script>
        // Original SVG content
        const originalSvg = `""" + svg_content + """`;
        
        // Current SVG content
        let currentSvg = originalSvg;
        
        // DOM elements
        const preview = document.getElementById('preview');
        const animationType = document.getElementById('animation-type');
        const duration = document.getElementById('duration');
        const timing = document.getElementById('timing');
        const targetElement = document.getElementById('target-element');
        const applyButton = document.getElementById('apply-animation');
        const resetButton = document.getElementById('reset');
        const codeOutput = document.getElementById('code-output');
        const copyCodeButton = document.getElementById('copy-code');
        const downloadButton = document.getElementById('download-svg');
        
        // Initialize preview
        preview.innerHTML = originalSvg;
        
        // Apply animation button
        applyButton.addEventListener('click', function() {
            // Get animation parameters
            const type = animationType.value;
            const durationValue = `${duration.value}s`;
            const timingValue = timing.value;
            const target = targetElement.value;
            
            // Make a request to a hypothetical server-side function
            // In a real implementation, this would call your Python function
            // For this demo, we'll simulate the result
            
            // Show a "loading" message
            preview.innerHTML = '<div style="text-align: center;"><p>Applying animation...</p></div>';
            
            // Simulate server-side processing
            setTimeout(() => {
                // This is where you would actually call your Python function
                // For demo, we'll add a simple CSS animation
                let animatedSvg = originalSvg;
                
                // Add a style tag with animation
                const styleTag = `<style>
                    @keyframes ${type}-anim {
                        0% { opacity: 1; }
                        50% { opacity: 0.5; }
                        100% { opacity: 1; }
                    }
                    
                    path {
                        animation: ${type}-anim ${durationValue} ${timingValue} infinite;
                    }
                </style>`;
                
                animatedSvg = animatedSvg.replace('</svg>', `${styleTag}</svg>`);
                
                // Update the preview
                preview.innerHTML = animatedSvg;
                currentSvg = animatedSvg;
                
                // Update code output
                codeOutput.textContent = `// Applied ${type} animation
// Duration: ${durationValue}
// Timing: ${timingValue}
// Target: ${target}

// Python code to generate this:
from scripts.path_animation_system import apply_path_animation_to_svg
from pathlib import Path

svg_path = Path("your_svg_file.svg")
animation_type = "${type}"
custom_duration = "${durationValue}"
target_elements = ["${target}"]

output_path = apply_path_animation_to_svg(
    svg_path,
    animation_type,
    target_elements=target_elements,
    custom_duration=custom_duration
)`;
            }, 500);
        });
        
        // Reset button
        resetButton.addEventListener('click', function() {
            preview.innerHTML = originalSvg;
            currentSvg = originalSvg;
            codeOutput.textContent = "// Animation code will appear here";
        });
        
        // Copy code button
        copyCodeButton.addEventListener('click', function() {
            navigator.clipboard.writeText(codeOutput.textContent)
                .then(() => {
                    copyCodeButton.textContent = "Copied!";
                    setTimeout(() => {
                        copyCodeButton.textContent = "Copy Code";
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy: ', err);
                });
        });
        
        // Download SVG button
        downloadButton.addEventListener('click', function() {
            const blob = new Blob([currentSvg], {type: 'image/svg+xml'});
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = 'animated_icon.svg';
            document.body.appendChild(a);
            a.click();
            
            setTimeout(() => {
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
            }, 0);
        });
    </script>
</body>
</html>
"""

    # Write the HTML file
    try:
        with open(editor_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return editor_path
    except Exception as e:
        print(f"Error writing editor HTML to {editor_path}: {e}")
        return None


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="StrategyDECK Path Animation System")

    parser.add_argument(
        "--svg", type=str, help="SVG file to animate")
    parser.add_argument(
        "--animation", choices=list(PATH_ANIMATION_PRESETS.keys()),
        help="Type of animation to apply")
    parser.add_argument(
        "--target", action="append",
        help="Target elements to animate (e.g., all-paths, foreground-paths, #elementId)")
    parser.add_argument(
        "--duration", type=str, help="Custom animation duration (e.g., 2s, 500ms)")
    parser.add_argument(
        "--demo", action="store_true", help="Create a demo HTML page")
    parser.add_argument(
        "--editor", action="store_true", help="Create an interactive editor for the SVG")
    parser.add_argument(
        "--open", action="store_true", help="Open the resulting file in a browser")

    args = parser.parse_args()

    if args.svg:
        svg_path = Path(args.svg)
        if not svg_path.exists():
            print(f"Error: SVG file not found: {svg_path}")
            return 1

        if args.editor:
            # Create an interactive editor
            editor_path = generate_interactive_path_editor(svg_path)
            if editor_path:
                print(f"Created interactive editor at: {editor_path}")

                if args.open:
                    try:
                        import webbrowser
                        webbrowser.open(f"file://{editor_path.absolute()}")
                    except Exception as e:
                        print(f"Error opening editor in browser: {e}")

        elif args.animation:
            # Apply specific animation
            output_path = apply_path_animation_to_svg(
                svg_path,
                args.animation,
                target_elements=args.target,
                custom_duration=args.duration
            )

            if output_path:
                print(f"Created animated SVG: {output_path}")

                if args.open:
                    try:
                        import webbrowser
                        webbrowser.open(f"file://{output_path.absolute()}")
                    except Exception as e:
                        print(f"Error opening SVG in browser: {e}")

        elif args.demo:
            # Create a demo with all animation types
            demo_path = create_path_animation_demo([svg_path])
            if demo_path:
                print(f"Created demo page at: {demo_path}")

                if args.open:
                    try:
                        import webbrowser
                        webbrowser.open(f"file://{demo_path.absolute()}")
                    except Exception as e:
                        print(f"Error opening demo in browser: {e}")

        else:
            print("Error: Please specify --animation, --demo, or --editor")
            return 1

    else:
        # Without a specific SVG, try to find some to animate
        from glob import glob

        # Look for SVG files in the assets directory
        svg_files = list(Path(ASSETS_DIR).glob("**/masters/*.svg"))
        if not svg_files:
            svg_files = list(Path(ASSETS_DIR).glob("**/*.svg"))

        if svg_files:
            if args.demo:
                # Create a demo with all animation types
                demo_path = create_path_animation_demo(
                    svg_files[:5])  # Limit to 5 files
                if demo_path:
                    print(
                        f"Created demo page with {len(svg_files[:5])} SVG files at: {demo_path}")

                    if args.open:
                        try:
                            import webbrowser
                            webbrowser.open(f"file://{demo_path.absolute()}")
                        except Exception as e:
                            print(f"Error opening demo in browser: {e}")
            else:
                print("Found SVG files to animate:")
                for svg in svg_files[:5]:
                    print(f"  - {svg}")
                if len(svg_files) > 5:
                    print(f"  ... and {len(svg_files) - 5} more")

                print("\nUse --svg to specify a file, or --demo to create a demo page")
        else:
            print("Error: No SVG files found. Please specify an SVG file with --svg")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
