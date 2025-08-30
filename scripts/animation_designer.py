#!/usr/bin/env python3
"""
StrategyDECK Animation Designer

This module creates an interactive HTML-based animation designer for SVG icons,
allowing users to visually design and preview custom animations, then export the
results as standalone SVG files with embedded animations.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import random
import re
from typing import Dict, List, Optional, Set, Any
import shutil
import webbrowser

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(ROOT))

# Import from animate_icons module
try:
    from animate_icons import (
        ANIMATION_PRESETS,
        add_animation_to_svg,
        parse_svg,
        generate_animation_css,
        ANIMATED_DIR
    )
except ImportError:
    print("Error: Could not import from animate_icons.py")
    print("Make sure animate_icons.py exists in the workspace")
    sys.exit(1)

# Setup output directory
DESIGNER_DIR = ROOT / "assets" / "designer"
DESIGNER_DIR.mkdir(parents=True, exist_ok=True)


def find_all_svg_files() -> List[Dict[str, Any]]:
    """Find all SVG files in the assets directory and return as options for the designer"""
    svg_files = []

    # Search in assets/icons directory
    icons_dir = ROOT / "assets" / "icons"
    if icons_dir.exists():
        for svg_path in icons_dir.glob("**/*.svg"):
            relative_path = svg_path.relative_to(ROOT)
            mode = "unknown"
            finish = "unknown"
            size = "unknown"

            # Try to parse info from path
            path_parts = str(relative_path).split("/")
            if "icons" in path_parts and len(path_parts) > 2:
                idx = path_parts.index("icons")
                if idx + 1 < len(path_parts):
                    mode = path_parts[idx + 1]  # light or dark
                if idx + 2 < len(path_parts):
                    finish = path_parts[idx + 2]  # flat-orange, etc.
                if idx + 3 < len(path_parts):
                    # Try to extract size
                    size_match = re.search(r'(\d+)px', path_parts[idx + 3])
                    if size_match:
                        size = size_match.group(1) + "px"

            svg_files.append({
                "path": str(relative_path),
                "name": svg_path.name,
                "mode": mode,
                "finish": finish,
                "size": size
            })

    # Also search in assets/animated directory for already animated files
    animated_dir = ROOT / "assets" / "animated"
    if animated_dir.exists():
        for svg_path in animated_dir.glob("**/*.svg"):
            relative_path = svg_path.relative_to(ROOT)
            svg_files.append({
                "path": str(relative_path),
                "name": svg_path.name,
                "mode": "animated",
                "finish": "animated",
                "size": "unknown"
            })

    # Also search in assets/animated/glyphs for glyphs
    glyphs_dir = ROOT / "assets" / "animated" / "glyphs"
    if glyphs_dir.exists():
        for svg_path in glyphs_dir.glob("**/*.svg"):
            relative_path = svg_path.relative_to(ROOT)
            svg_files.append({
                "path": str(relative_path),
                "name": svg_path.name,
                "mode": "glyph",
                "finish": "animated",
                "size": "unknown"
            })

    return svg_files


def create_animation_designer() -> Path:
    """Create an interactive HTML animation designer"""
    designer_path = DESIGNER_DIR / "animation_designer.html"
    svg_files = find_all_svg_files()

    # Escape and stringify the JSON data for direct embedding in HTML
    svg_files_json = json.dumps(svg_files).replace("'", "\\'").replace('"', '\\"')
    animation_presets_json = json.dumps(
        ANIMATION_PRESETS).replace("'", "\\'").replace('"', '\\"')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrategyDECK Animation Designer</title>
    <style>
        :root {{
            --primary: #FF6A00;
            --primary-dark: #CC5500;
            --bg-dark: #1a1a1a;
            --bg-light: #f8f9fa;
            --text-dark: #333;
            --text-light: #f8f9fa;
            --border: #ddd;
            --panel-bg: #fff;
            --panel-bg-dark: #2a2a2a;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            color: var(--text-dark);
            background-color: var(--bg-light);
            transition: background-color 0.3s ease;
        }}
        
        body.dark-mode {{
            background-color: var(--bg-dark);
            color: var(--text-light);
        }}
        
        .container {{
            display: grid;
            grid-template-columns: 300px 1fr;
            height: 100vh;
        }}
        
        .sidebar {{
            background-color: var(--panel-bg);
            border-right: 1px solid var(--border);
            padding: 20px;
            overflow-y: auto;
            transition: background-color 0.3s ease;
        }}
        
        .dark-mode .sidebar {{
            background-color: var(--panel-bg-dark);
            border-right-color: #444;
        }}
        
        .preview-panel {{
            padding: 20px;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }}
        
        .preview-container {{
            flex: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            background-color: rgba(0, 0, 0, 0.03);
            border-radius: 8px;
            margin-bottom: 20px;
            min-height: 300px;
            transition: background-color 0.3s ease;
        }}
        
        .dark-mode .preview-container {{
            background-color: rgba(255, 255, 255, 0.05);
        }}
        
        .controls {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            background-color: var(--primary);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            transition: background-color 0.2s;
        }}
        
        .btn:hover {{
            background-color: var(--primary-dark);
        }}
        
        .btn-secondary {{
            background-color: #6c757d;
        }}
        
        .btn-secondary:hover {{
            background-color: #5a6268;
        }}
        
        h1, h2, h3 {{
            color: var(--primary);
        }}
        
        .dark-mode h1, .dark-mode h2, .dark-mode h3 {{
            color: var(--primary);
        }}
        
        .form-group {{
            margin-bottom: 15px;
        }}
        
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }}
        
        select, input, textarea {{
            width: 100%;
            padding: 8px;
            border: 1px solid var(--border);
            border-radius: 4px;
            background-color: white;
            color: var(--text-dark);
        }}
        
        .dark-mode select, .dark-mode input, .dark-mode textarea {{
            background-color: #3a3a3a;
            color: var(--text-light);
            border-color: #555;
        }}
        
        .animation-stack {{
            margin-top: 20px;
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.02);
            transition: background-color 0.3s ease;
        }}
        
        .dark-mode .animation-stack {{
            background-color: rgba(255, 255, 255, 0.05);
            border-color: #444;
        }}
        
        .animation-item {{
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;
            background-color: white;
            position: relative;
            transition: background-color 0.3s ease;
        }}
        
        .dark-mode .animation-item {{
            background-color: #3a3a3a;
            border-color: #555;
        }}
        
        .animation-item-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        
        .remove-animation {{
            background-color: #dc3545;
            color: white;
            border: none;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            position: absolute;
            top: 5px;
            right: 5px;
        }}
        
        .remove-animation:hover {{
            background-color: #bd2130;
        }}
        
        .toggle-switch {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }}
        
        .toggle-switch label {{
            margin-bottom: 0;
        }}
        
        .switch {{
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
        }}
        
        .switch input {{
            opacity: 0;
            width: 0;
            height: 0;
        }}
        
        .slider {{
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 24px;
        }}
        
        .slider:before {{
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }}
        
        input:checked + .slider {{
            background-color: var(--primary);
        }}
        
        input:checked + .slider:before {{
            transform: translateX(26px);
        }}
        
        .code-display {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 4px;
            font-family: monospace;
            overflow-x: auto;
            white-space: pre-wrap;
            margin-top: 20px;
            transition: background-color 0.3s ease;
        }}
        
        .dark-mode .code-display {{
            background-color: #2d2d2d;
        }}
        
        .color-picker-container {{
            display: flex;
            gap: 5px;
            margin-top: 5px;
        }}
        
        .color-picker {{
            height: 30px;
            width: 100%;
            padding: 0;
        }}
        
        .accordion {{
            margin-bottom: 10px;
        }}
        
        .accordion-header {{
            background-color: var(--primary);
            color: white;
            padding: 10px;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .accordion-content {{
            border: 1px solid var(--border);
            border-top: none;
            border-radius: 0 0 4px 4px;
            padding: 10px;
            display: none;
            background-color: white;
            transition: background-color 0.3s ease;
        }}
        
        .dark-mode .accordion-content {{
            background-color: #3a3a3a;
            border-color: #555;
        }}
        
        .show {{
            display: block;
        }}
        
        .svg-file-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }}
        
        .svg-file-item {{
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 5px;
            text-align: center;
            cursor: pointer;
            background-color: white;
            transition: transform 0.2s, background-color 0.3s ease;
            height: 100px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            overflow: hidden;
        }}
        
        .dark-mode .svg-file-item {{
            background-color: #3a3a3a;
            border-color: #555;
        }}
        
        .svg-file-item:hover {{
            transform: translateY(-3px);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .svg-file-item.selected {{
            border: 2px solid var(--primary);
        }}
        
        .svg-preview {{
            height: 60px;
            width: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .svg-preview svg {{
            max-width: 100%;
            max-height: 100%;
        }}
        
        .svg-name {{
            font-size: 10px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            width: 100%;
        }}
        
        .filter-controls {{
            margin-bottom: 15px;
            display: flex;
            gap: 10px;
        }}
        
        .tooltip {{
            position: relative;
            display: inline-block;
            margin-left: 5px;
        }}
        
        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
        }}
        
        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}
        
        .notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            display: none;
            z-index: 1000;
            transition: opacity 0.3s;
        }}
    </style>
</head>
<body>
    <div class="notification" id="notification">Saved successfully!</div>
    
    <div class="container">
        <div class="sidebar">
            <h2>Animation Designer</h2>
            
            <div class="toggle-switch">
                <label for="darkModeToggle">Dark Mode</label>
                <label class="switch">
                    <input type="checkbox" id="darkModeToggle">
                    <span class="slider"></span>
                </label>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion('file-selector')">
                    <span>1. Select SVG File</span>
                    <span>+</span>
                </div>
                <div class="accordion-content" id="file-selector">
                    <div class="filter-controls">
                        <select id="filterMode">
                            <option value="all">All Modes</option>
                            <option value="light">Light</option>
                            <option value="dark">Dark</option>
                            <option value="glyph">Glyphs</option>
                            <option value="animated">Animated</option>
                        </select>
                        <select id="filterFinish">
                            <option value="all">All Finishes</option>
                        </select>
                    </div>
                    <div class="svg-file-grid" id="svgFileGrid">
                        <!-- SVG files will be dynamically added here -->
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion('animation-builder')">
                    <span>2. Build Animation</span>
                    <span>+</span>
                </div>
                <div class="accordion-content" id="animation-builder">
                    <div class="form-group">
                        <label for="animationType">Animation Type</label>
                        <select id="animationType">
                            <option value="pulse">Pulse</option>
                            <option value="rotate">Rotate</option>
                            <option value="bounce">Bounce</option>
                            <option value="fade">Fade</option>
                            <option value="morph">Morph</option>
                            <option value="color-shift">Color Shift</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="targetElements">Target Elements</label>
                        <select id="targetElements">
                            <option value="foreground">Foreground</option>
                            <option value="background">Background</option>
                            <option value="all">All Elements</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="duration">Duration (ms or s)</label>
                        <input type="text" id="duration" value="2s">
                    </div>
                    
                    <div class="form-group color-shift-options" style="display: none;">
                        <label>Alternate Colors</label>
                        <div class="color-picker-container">
                            <input type="color" id="alternateColor1" class="color-picker" value="#FF6A00">
                            <input type="color" id="alternateColor2" class="color-picker" value="#005599">
                        </div>
                    </div>
                    
                    <button class="btn" id="addAnimation">Add Animation</button>
                    
                    <div class="animation-stack" id="animationStack">
                        <h3>Animation Stack</h3>
                        <div id="animationItems">
                            <!-- Animation items will be dynamically added here -->
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion('export-options')">
                    <span>3. Export Options</span>
                    <span>+</span>
                </div>
                <div class="accordion-content" id="export-options">
                    <div class="form-group">
                        <label for="outputFilename">Output Filename</label>
                        <input type="text" id="outputFilename" value="animated-icon.svg">
                    </div>
                    
                    <button class="btn" id="previewAnimation">Update Preview</button>
                    <button class="btn" id="exportAnimation">Export SVG</button>
                    <button class="btn btn-secondary" id="copyCode">Copy SVG Code</button>
                </div>
            </div>
            
            <div class="accordion">
                <div class="accordion-header" onclick="toggleAccordion('animation-code')">
                    <span>SVG Code</span>
                    <span>+</span>
                </div>
                <div class="accordion-content" id="animation-code">
                    <div class="code-display" id="svgCode">
                        <!-- SVG code will be displayed here -->
                    </div>
                </div>
            </div>
        </div>
        
        <div class="preview-panel">
            <h1>Animation Preview</h1>
            <div class="controls">
                <button class="btn" id="toggleAnimation">Pause Animation</button>
                <button class="btn" id="resetAnimation">Reset Animation</button>
                <button class="btn btn-secondary" id="zoomIn">Zoom In</button>
                <button class="btn btn-secondary" id="zoomOut">Zoom Out</button>
                <button class="btn btn-secondary" id="resetZoom">Reset Zoom</button>
            </div>
            
            <div class="preview-container" id="previewContainer">
                <!-- SVG preview will be displayed here -->
            </div>
        </div>
    </div>
    
    <script>
        // Initialize with SVG files and animation presets
        const svgFiles = JSON.parse("${svg_files_json}");
        const animationPresets = JSON.parse("${animation_presets_json}");
        
        let currentSvgPath = null;
        let currentSvgContent = null;
        let animationStack = [];
        let currentZoom = 1;
        
        // DOM elements
        const svgFileGrid = document.getElementById('svgFileGrid');
        const filterMode = document.getElementById('filterMode');
        const filterFinish = document.getElementById('filterFinish');
        const animationType = document.getElementById('animationType');
        const targetElements = document.getElementById('targetElements');
        const duration = document.getElementById('duration');
        const alternateColor1 = document.getElementById('alternateColor1');
        const alternateColor2 = document.getElementById('alternateColor2');
        const addAnimation = document.getElementById('addAnimation');
        const animationItems = document.getElementById('animationItems');
        const previewContainer = document.getElementById('previewContainer');
        const previewAnimation = document.getElementById('previewAnimation');
        const exportAnimation = document.getElementById('exportAnimation');
        const outputFilename = document.getElementById('outputFilename');
        const svgCode = document.getElementById('svgCode');
        const copyCode = document.getElementById('copyCode');
        const toggleAnimation = document.getElementById('toggleAnimation');
        const resetAnimation = document.getElementById('resetAnimation');
        const zoomIn = document.getElementById('zoomIn');
        const zoomOut = document.getElementById('zoomOut');
        const resetZoom = document.getElementById('resetZoom');
        const darkModeToggle = document.getElementById('darkModeToggle');
        const notification = document.getElementById('notification');
        
        // Populate unique finishes for the filter
        const uniqueFinishes = [...new Set(svgFiles.map(file => file.finish))];
        uniqueFinishes.sort().forEach(finish => {
            const option = document.createElement('option');
            option.value = finish;
            option.textContent = finish;
            filterFinish.appendChild(option);
        });
        
        // Initialize SVG file grid
        function updateSvgGrid() {
            svgFileGrid.innerHTML = '';
            
            const modeFilter = filterMode.value;
            const finishFilter = filterFinish.value;
            
            svgFiles
                .filter(file => {
                    return (modeFilter === 'all' || file.mode === modeFilter) &&
                           (finishFilter === 'all' || file.finish === finishFilter);
                })
                .forEach(file => {
                    const item = document.createElement('div');
                    item.className = 'svg-file-item';
                    item.dataset.path = file.path;
                    
                    const preview = document.createElement('div');
                    preview.className = 'svg-preview';
                    
                    const name = document.createElement('div');
                    name.className = 'svg-name';
                    name.textContent = file.name;
                    
                    item.appendChild(preview);
                    item.appendChild(name);
                    svgFileGrid.appendChild(item);
                    
                    // Load SVG preview
                    fetch(file.path)
                        .then(response => response.text())
                        .then(svgContent => {
                            preview.innerHTML = svgContent;
                            
                            // Scale SVG to fit preview area
                            const svg = preview.querySelector('svg');
                            if (svg) {
                                svg.style.width = '100%';
                                svg.style.height = '100%';
                            }
                        })
                        .catch(error => {
                            console.error('Error loading SVG:', error);
                            preview.textContent = 'Error';
                        });
                    
                    // Select SVG file
                    item.addEventListener('click', () => {
                        document.querySelectorAll('.svg-file-item').forEach(el => {
                            el.classList.remove('selected');
                        });
                        item.classList.add('selected');
                        currentSvgPath = file.path;
                        
                        // Update output filename with a default based on selected file
                        const baseName = file.name.replace('.svg', '');
                        outputFilename.value = `animated-${baseName}.svg`;
                        
                        // Load SVG content
                        fetch(file.path)
                            .then(response => response.text())
                            .then(svgContent => {
                                currentSvgContent = svgContent;
                                updatePreview();
                            })
                            .catch(error => {
                                console.error('Error loading SVG:', error);
                            });
                    });
                });
        }
        
        // Initialize filter change events
        filterMode.addEventListener('change', updateSvgGrid);
        filterFinish.addEventListener('change', updateSvgGrid);
        
        // Initialize animation type change event
        animationType.addEventListener('change', () => {
            const colorShiftOptions = document.querySelector('.color-shift-options');
            if (animationType.value === 'color-shift') {
                colorShiftOptions.style.display = 'block';
            } else {
                colorShiftOptions.style.display = 'none';
            }
        });
        
        // Add animation to stack
        addAnimation.addEventListener('click', () => {
            if (!currentSvgContent) {
                alert('Please select an SVG file first');
                return;
            }
            
            const animation = {
                type: animationType.value,
                target: targetElements.value,
                duration: duration.value
            };
            
            // Add color values for color-shift animation
            if (animation.type === 'color-shift') {
                animation.colors = [
                    alternateColor1.value,
                    alternateColor2.value
                ];
            }
            
            animationStack.push(animation);
            updateAnimationStack();
            updatePreview();
        });
        
        // Update animation stack UI
        function updateAnimationStack() {
            animationItems.innerHTML = '';
            
            if (animationStack.length === 0) {
                const emptyMessage = document.createElement('div');
                emptyMessage.textContent = 'No animations added yet';
                emptyMessage.style.fontStyle = 'italic';
                emptyMessage.style.color = '#999';
                emptyMessage.style.padding = '10px';
                animationItems.appendChild(emptyMessage);
                return;
            }
            
            animationStack.forEach((animation, index) => {
                const item = document.createElement('div');
                item.className = 'animation-item';
                
                const header = document.createElement('div');
                header.className = 'animation-item-header';
                
                const title = document.createElement('div');
                title.style.fontWeight = 'bold';
                title.textContent = animation.type.charAt(0).toUpperCase() + animation.type.slice(1);
                
                const removeButton = document.createElement('button');
                removeButton.className = 'remove-animation';
                removeButton.textContent = '×';
                removeButton.addEventListener('click', () => {
                    animationStack.splice(index, 1);
                    updateAnimationStack();
                    updatePreview();
                });
                
                header.appendChild(title);
                item.appendChild(header);
                item.appendChild(removeButton);
                
                const details = document.createElement('div');
                details.innerHTML = `
                    <div>Target: ${animation.target}</div>
                    <div>Duration: ${animation.duration}</div>
                    ${animation.colors ? `<div>Colors: ${animation.colors.join(', ')}</div>` : ''}
                `;
                item.appendChild(details);
                
                animationItems.appendChild(item);
            });
        }
        
        // Update preview with current SVG and animations
        function updatePreview() {
            if (!currentSvgContent) {
                return;
            }
            
            let animatedSvg = currentSvgContent;
            
            // Apply each animation in the stack
            animationStack.forEach(animation => {
                const targets = animation.target === 'all' ? ['all'] : [animation.target];
                const colors = animation.colors || [];
                
                // Apply animation to SVG
                animatedSvg = applyAnimationToSvg(
                    animatedSvg,
                    animation.type,
                    targets,
                    colors,
                    animation.duration
                );
            });
            
            // Update preview container
            previewContainer.innerHTML = animatedSvg;
            
            // Scale SVG in preview
            const svg = previewContainer.querySelector('svg');
            if (svg) {
                svg.style.width = '300px';
                svg.style.height = '300px';
                svg.style.transform = `scale(${currentZoom})`;
                svg.style.transformOrigin = 'center';
                svg.style.transition = 'transform 0.3s ease';
            }
            
            // Update code display
            svgCode.textContent = animatedSvg;
        }
        
        // Function to apply animation to SVG (simplified version)
        function applyAnimationToSvg(svgContent, animationType, targetElements, alternateColors, customDuration) {
            // This is a simplified version that would be replaced with actual animation logic
            // In a real implementation, this would call out to the animate_icons.py functions
            
            // For demo purposes, we'll just modify the SVG to indicate animation
            const parser = new DOMParser();
            const doc = parser.parseFromString(svgContent, 'image/svg+xml');
            const svg = doc.documentElement;
            
            // Create a unique animation ID
            const animationId = `anim-${Math.random().toString(36).substr(2, 9)}`;
            
            // Create style element for animation
            const style = document.createElement('style');
            
            // Generate appropriate CSS based on animation type
            let css = '';
            
            switch (animationType) {
                case 'pulse':
                    css = `
                        @keyframes ${animationId} {
                            0% { transform: scale(1); opacity: 1; }
                            50% { transform: scale(1.2); opacity: 0.8; }
                            100% { transform: scale(1); opacity: 1; }
                        }
                        .${animationId} {
                            animation: ${animationId} ${customDuration || '2s'} ease-in-out infinite;
                            transform-origin: center;
                        }
                    `;
                    break;
                    
                case 'rotate':
                    css = `
                        @keyframes ${animationId} {
                            from { transform: rotate(0deg); }
                            to { transform: rotate(360deg); }
                        }
                        .${animationId} {
                            animation: ${animationId} ${customDuration || '3s'} linear infinite;
                            transform-origin: center;
                        }
                    `;
                    break;
                    
                case 'bounce':
                    css = `
                        @keyframes ${animationId} {
                            0% { transform: translateY(0); }
                            50% { transform: translateY(-10px); }
                            100% { transform: translateY(0); }
                        }
                        .${animationId} {
                            animation: ${animationId} ${customDuration || '1s'} ease-in-out infinite;
                        }
                    `;
                    break;
                    
                case 'fade':
                    css = `
                        @keyframes ${animationId} {
                            0% { opacity: 1; }
                            50% { opacity: 0.3; }
                            100% { opacity: 1; }
                        }
                        .${animationId} {
                            animation: ${animationId} ${customDuration || '2.5s'} ease-in-out infinite;
                        }
                    `;
                    break;
                    
                case 'color-shift':
                    const color1 = alternateColors[0] || '#FF6A00';
                    const color2 = alternateColors[1] || '#005599';
                    css = `
                        @keyframes ${animationId} {
                            0% { fill: ${color1}; }
                            50% { fill: ${color2}; }
                            100% { fill: ${color1}; }
                        }
                        .${animationId} {
                            animation: ${animationId} ${customDuration || '4s'} linear infinite;
                        }
                    `;
                    break;
                    
                case 'morph':
                    css = `
                        @keyframes ${animationId} {
                            0% { d: path(''); }
                            50% { d: path(''); }
                            100% { d: path(''); }
                        }
                        .${animationId} {
                            animation: ${animationId} ${customDuration || '3s'} ease-in-out infinite;
                        }
                    `;
                    break;
            }
            
            style.textContent = css;
            svg.appendChild(style);
            
            // Apply animation class to target elements
            if (targetElements.includes('all')) {
                // Add to all shapes
                const shapes = svg.querySelectorAll('path, circle, rect, polygon');
                shapes.forEach(shape => {
                    shape.classList.add(animationId);
                });
            } else if (targetElements.includes('foreground')) {
                // Add to all except the background (usually the first rect)
                const shapes = svg.querySelectorAll('path, circle, polygon');
                shapes.forEach(shape => {
                    shape.classList.add(animationId);
                });
            } else if (targetElements.includes('background')) {
                // Add to just the background (usually the first rect)
                const background = svg.querySelector('rect');
                if (background) {
                    background.classList.add(animationId);
                }
            }
            
            // Serialize back to string
            return new XMLSerializer().serializeToString(doc);
        }
        
        // Preview button
        previewAnimation.addEventListener('click', updatePreview);
        
        // Export animation
        exportAnimation.addEventListener('click', () => {
            if (!currentSvgContent || animationStack.length === 0) {
                alert('Please select an SVG file and add at least one animation');
                return;
            }
            
            const filename = outputFilename.value;
            const animatedSvgContent = svgCode.textContent;
            
            // Create a download link
            const a = document.createElement('a');
            const blob = new Blob([animatedSvgContent], {type: 'image/svg+xml'});
            a.href = URL.createObjectURL(blob);
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            // Show notification
            notification.style.display = 'block';
            notification.textContent = `Saved ${filename} successfully!`;
            setTimeout(() => {
                notification.style.opacity = '0';
                setTimeout(() => {
                    notification.style.display = 'none';
                    notification.style.opacity = '1';
                }, 300);
            }, 2000);
        });
        
        // Copy SVG code
        copyCode.addEventListener('click', () => {
            const code = svgCode.textContent;
            navigator.clipboard.writeText(code).then(() => {
                // Show notification
                notification.style.display = 'block';
                notification.textContent = 'SVG code copied to clipboard!';
                setTimeout(() => {
                    notification.style.opacity = '0';
                    setTimeout(() => {
                        notification.style.display = 'none';
                        notification.style.opacity = '1';
                    }, 300);
                }, 2000);
            });
        });
        
        // Animation controls
        toggleAnimation.addEventListener('click', () => {
            const svg = previewContainer.querySelector('svg');
            if (!svg) return;
            
            const animatedElements = svg.querySelectorAll('[class*="-animation"], [class*="anim-"]');
            
            if (toggleAnimation.textContent === 'Pause Animation') {
                animatedElements.forEach(el => {
                    el.style.animationPlayState = 'paused';
                });
                toggleAnimation.textContent = 'Resume Animation';
            } else {
                animatedElements.forEach(el => {
                    el.style.animationPlayState = 'running';
                });
                toggleAnimation.textContent = 'Pause Animation';
            }
        });
        
        resetAnimation.addEventListener('click', () => {
            updatePreview();
        });
        
        // Zoom controls
        zoomIn.addEventListener('click', () => {
            currentZoom += 0.1;
            updateZoom();
        });
        
        zoomOut.addEventListener('click', () => {
            currentZoom = Math.max(0.1, currentZoom - 0.1);
            updateZoom();
        });
        
        resetZoom.addEventListener('click', () => {
            currentZoom = 1;
            updateZoom();
        });
        
        function updateZoom() {
            const svg = previewContainer.querySelector('svg');
            if (svg) {
                svg.style.transform = `scale(${currentZoom})`;
            }
        }
        
        // Accordion functionality
        function toggleAccordion(id) {
            const content = document.getElementById(id);
            content.classList.toggle('show');
            
            // Update the + or - icon
            const header = content.previousElementSibling;
            const icon = header.querySelector('span:last-child');
            icon.textContent = content.classList.contains('show') ? '-' : '+';
        }
        
        // Dark mode toggle
        darkModeToggle.addEventListener('change', () => {
            document.body.classList.toggle('dark-mode', darkModeToggle.checked);
        });
        
        // Initialize
        updateSvgGrid();
        updateAnimationStack();
        
        // Auto-open first accordion
        toggleAccordion('file-selector');
    </script>
</body>
</html>
"""

    # Write HTML file
    with open(designer_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return designer_path


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="StrategyDECK Animation Designer")

    parser.add_argument(
        "--open",
        action="store_true",
        help="Open designer in browser after creation"
    )

    args = parser.parse_args()

    # Create the animation designer
    designer_path = create_animation_designer()
    print(f"Created animation designer at: {designer_path}")

    # Open in browser if requested
    if args.open:
        try:
            webbrowser.open(f"file://{designer_path.absolute()}")
            print(f"Opened designer in browser")
        except Exception as e:
            print(f"Error opening designer in browser: {e}")
            print(f"You can manually open the file at: {designer_path.absolute()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
