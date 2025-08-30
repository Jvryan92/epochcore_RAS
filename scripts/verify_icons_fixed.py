#!/usr/bin/env python3
"""
StrategyDECK Icon Verification Tool

This script verifies the quality and consistency of generated icons:
- Checks SVG structure and validity
- Verifies color token usage
- Confirms PNG export quality
- Validates size dimensions
- Generates a quality report
"""

import argparse
import concurrent.futures
import csv
import json
import logging
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("icon_verifier")

# Base paths
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICONS_DIR = ASSETS / "icons"
REPORT_DIR = ROOT / "reports"

# Ensure report directory exists
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Check for dependencies
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning("Pillow is not installed. PNG validation will be limited.")


def find_svg_files() -> List[Path]:
    """Find all SVG files in the icons directory"""
    return list(ICONS_DIR.glob("**/*.svg"))


def find_png_files() -> List[Path]:
    """Find all PNG files in the icons directory"""
    return list(ICONS_DIR.glob("**/*.png"))


def find_webp_files() -> List[Path]:
    """Find all WebP files in the icons directory"""
    return list(ICONS_DIR.glob("**/*.webp"))


def verify_svg_structure(svg_path: Path) -> Dict:
    """Verify the structure of an SVG file"""
    result = {
        "path": str(svg_path),
        "filename": svg_path.name,
        "status": "pass",
        "issues": []
    }

    try:
        # Read SVG content
        svg_content = svg_path.read_text(encoding="utf-8")

        # Check for empty file
        if len(svg_content) < 10:
            result["status"] = "fail"
            result["issues"].append("SVG file is empty or too small")
            return result

        # Check for valid XML
        try:
            ET.fromstring(svg_content)
        except ET.ParseError as e:
            result["status"] = "fail"
            result["issues"].append(f"Invalid XML: {str(e)}")
            return result

        # Check for basic SVG elements
        if "<svg" not in svg_content:
            result["status"] = "fail"
            result["issues"].append("Missing SVG root element")

        # Check viewBox attribute
        if "viewBox" not in svg_content and "width" not in svg_content:
            result["status"] = "warning"
            result["issues"].append("Missing viewBox or width/height attributes")

        # Check for recommended elements
        if "<path" not in svg_content and "<circle" not in svg_content and "<rect" not in svg_content:
            result["status"] = "warning"
            result["issues"].append(
                "No standard SVG elements found (path, circle, rect)")

    except Exception as e:
        result["status"] = "error"
        result["issues"].append(f"Error verifying SVG: {str(e)}")

    return result


def verify_png_quality(png_path: Path) -> Dict:
    """Verify the quality of a PNG file"""
    result = {
        "path": str(png_path),
        "filename": png_path.name,
        "status": "pass",
        "issues": []
    }

    if not PILLOW_AVAILABLE:
        result["status"] = "skip"
        result["issues"].append("Pillow not available for PNG validation")
        return result

    try:
        # Open the image
        img = Image.open(png_path)

        # Check format
        if img.format != "PNG":
            result["status"] = "fail"
            result["issues"].append(f"Not a PNG image (format: {img.format})")

        # Check dimensions
        width, height = img.size
        if width != height:
            result["status"] = "warning"
            result["issues"].append(f"Non-square dimensions: {width}x{height}")

        # Check mode (should be RGBA for transparency support)
        if img.mode != "RGBA":
            result["status"] = "warning"
            result["issues"].append(f"Image mode is {img.mode}, recommended: RGBA")

        # Check file size
        file_size = png_path.stat().st_size
        if file_size > 50 * 1024:  # Larger than 50KB
            result["status"] = "warning"
            result["issues"].append(f"Large file size: {file_size / 1024:.1f} KB")

        # Extract size from path
        try:
            # Assuming path format like "icons/light/flat-orange/32px/web/icon.png"
            size_str = png_path.parts[-3]
            expected_size = int(size_str.replace("px", ""))

            if width != expected_size:
                result["status"] = "fail"
                result["issues"].append(
                    f"Size mismatch: Image is {width}px but should be {expected_size}px")
        except:
            # If we can't determine the expected size, skip this check
            pass

    except Exception as e:
        result["status"] = "error"
        result["issues"].append(f"Error verifying PNG: {str(e)}")

    return result


def verify_webp_quality(webp_path: Path) -> Dict:
    """Verify the quality of a WebP file"""
    result = {
        "path": str(webp_path),
        "filename": webp_path.name,
        "status": "pass",
        "issues": []
    }

    if not PILLOW_AVAILABLE:
        result["status"] = "skip"
        result["issues"].append("Pillow not available for WebP validation")
        return result

    try:
        # Open the image
        img = Image.open(webp_path)

        # Check format
        if img.format != "WEBP":
            result["status"] = "fail"
            result["issues"].append(f"Not a WebP image (format: {img.format})")

        # Check dimensions
        width, height = img.size
        if width != height:
            result["status"] = "warning"
            result["issues"].append(f"Non-square dimensions: {width}x{height}")

        # Extract size from path
        try:
            # Assuming path format like "icons/light/flat-orange/32px/web/icon.webp"
            size_str = webp_path.parts[-3]
            expected_size = int(size_str.replace("px", ""))

            if width != expected_size:
                result["status"] = "fail"
                result["issues"].append(
                    f"Size mismatch: Image is {width}px but should be {expected_size}px")
        except:
            # If we can't determine the expected size, skip this check
            pass

    except Exception as e:
        result["status"] = "error"
        result["issues"].append(f"Error verifying WebP: {str(e)}")

    return result


def verify_color_tokens(svg_path: Path, token_mapping: Dict[str, str]) -> Dict:
    """Verify color token usage in an SVG file"""
    result = {
        "path": str(svg_path),
        "filename": svg_path.name,
        "status": "pass",
        "issues": [],
        "colors_found": []
    }

    try:
        # Read SVG content
        svg_content = svg_path.read_text(encoding="utf-8")

        # Extract all hex colors
        import re
        color_pattern = r'#[0-9A-Fa-f]{3,6}'
        colors = re.findall(color_pattern, svg_content)

        # Normalize colors (to 6-digit hex)
        normalized_colors = []
        for color in colors:
            if len(color) == 4:  # 3-digit hex
                r, g, b = color[1], color[2], color[3]
                normalized = f"#{r}{r}{g}{g}{b}{b}".upper()
            else:
                normalized = color.upper()
            normalized_colors.append(normalized)

        # Get unique colors
        unique_colors = list(set(normalized_colors))
        result["colors_found"] = unique_colors

        # Check if colors are in our token mapping
        token_colors = [c.upper() for c in token_mapping.values()]
        unknown_colors = [c for c in unique_colors if c not in token_colors]

        if unknown_colors:
            result["status"] = "warning"
            result["issues"].append(
                f"Unknown colors found: {', '.join(unknown_colors)}")

    except Exception as e:
        result["status"] = "error"
        result["issues"].append(f"Error verifying color tokens: {str(e)}")

    return result


def verify_directory_structure() -> Dict:
    """Verify the structure of the icons directory"""
    result = {
        "status": "pass",
        "issues": [],
        "modes": [],
        "finishes": [],
        "sizes": [],
        "contexts": []
    }

    try:
        # Check if icons directory exists
        if not ICONS_DIR.exists():
            result["status"] = "fail"
            result["issues"].append(f"Icons directory {ICONS_DIR} does not exist")
            return result

        # Check for mode directories (light, dark)
        modes = [d.name for d in ICONS_DIR.iterdir() if d.is_dir()]
        result["modes"] = modes

        if "light" not in modes or "dark" not in modes:
            result["status"] = "warning"
            result["issues"].append(
                "Missing expected mode directories (light and/or dark)")

        # Check finishes, sizes, and contexts
        all_finishes = set()
        all_sizes = set()
        all_contexts = set()

        for mode_dir in ICONS_DIR.iterdir():
            if not mode_dir.is_dir():
                continue

            finishes = [d.name for d in mode_dir.iterdir() if d.is_dir()]
            all_finishes.update(finishes)

            for finish_dir in mode_dir.iterdir():
                if not finish_dir.is_dir():
                    continue

                sizes = [d.name for d in finish_dir.iterdir() if d.is_dir()]
                all_sizes.update(sizes)

                for size_dir in finish_dir.iterdir():
                    if not size_dir.is_dir():
                        continue

                    contexts = [d.name for d in size_dir.iterdir() if d.is_dir()]
                    all_contexts.update(contexts)

        result["finishes"] = list(all_finishes)
        result["sizes"] = list(all_sizes)
        result["contexts"] = list(all_contexts)

        # Check for size format (should be like "16px")
        invalid_sizes = [s for s in all_sizes if not (
            s.endswith("px") and s[:-2].isdigit())]
        if invalid_sizes:
            result["status"] = "warning"
            result["issues"].append(f"Invalid size format: {', '.join(invalid_sizes)}")

    except Exception as e:
        result["status"] = "error"
        result["issues"].append(f"Error verifying directory structure: {str(e)}")

    return result


def load_color_tokens() -> Dict[str, str]:
    """Load color tokens from configuration file"""
    tokens = {
        "paper": "#FFFFFF",
        "slate_950": "#060607",
        "brand_orange": "#FF6A00",
        "ink": "#000000",
        "copper": "#B87333",
        "burnt_orange": "#CC5500",
        "matte": "#333333",
        "embossed": "#F5F5F5"
    }

    # Try to load from config file if it exists
    config_path = ROOT / "config" / "icon_config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                if "color_tokens" in config:
                    tokens.update(config["color_tokens"])
        except Exception as e:
            logger.warning(f"Error loading color tokens from config: {e}")

    return tokens


def generate_report(results: Dict) -> str:
    """Generate a detailed HTML report"""
    svg_results = results["svg_results"]
    png_results = results["png_results"]
    webp_results = results["webp_results"]
    color_results = results["color_results"]
    structure_result = results["structure_result"]

    # Calculate statistics
    svg_count = len(svg_results)
    svg_pass = sum(1 for r in svg_results if r["status"] == "pass")
    svg_warn = sum(1 for r in svg_results if r["status"] == "warning")
    svg_fail = sum(1 for r in svg_results if r["status"] == "fail")
    svg_error = sum(1 for r in svg_results if r["status"] == "error")

    png_count = len(png_results)
    png_pass = sum(1 for r in png_results if r["status"] == "pass")
    png_warn = sum(1 for r in png_results if r["status"] == "warning")
    png_fail = sum(1 for r in png_results if r["status"] == "fail")
    png_error = sum(1 for r in png_results if r["status"] == "error")

    webp_count = len(webp_results)
    webp_pass = sum(1 for r in webp_results if r["status"] == "pass")
    webp_warn = sum(1 for r in webp_results if r["status"] == "warning")
    webp_fail = sum(1 for r in webp_results if r["status"] == "fail")
    webp_error = sum(1 for r in webp_results if r["status"] == "error")

    # Create HTML header and CSS
    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StrategyDECK Icon Verification Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        h1, h2, h3 {{
            color: #FF6A00;
        }}
        
        .summary {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            grid-gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        
        .stat-title {{
            font-weight: bold;
            margin-bottom: 10px;
            color: #FF6A00;
        }}
        
        .structure-section {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}
        
        .pass {{
            color: #28a745;
        }}
        
        .warning {{
            color: #ffc107;
        }}
        
        .fail {{
            color: #dc3545;
        }}
        
        .error {{
            color: #6c757d;
        }}
        
        .issue-list {{
            margin: 0;
            padding-left: 20px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .badge-pass {{
            background-color: #d4edda;
            color: #28a745;
        }}
        
        .badge-warning {{
            background-color: #fff3cd;
            color: #856404;
        }}
        
        .badge-fail {{
            background-color: #f8d7da;
            color: #721c24;
        }}
        
        .badge-error {{
            background-color: #f8f9fa;
            color: #6c757d;
        }}
        
        .color-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
            grid-gap: 10px;
            margin-top: 10px;
        }}
        
        .color-item {{
            text-align: center;
        }}
        
        .color-box {{
            width: 100%;
            height: 30px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <h1>StrategyDECK Icon Verification Report</h1>
    <p>Generated on {results["timestamp"]}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-title">SVG Files</div>
                <div>Total: {svg_count}</div>
                <div class="pass">Pass: {svg_pass}</div>
                <div class="warning">Warning: {svg_warn}</div>
                <div class="fail">Fail: {svg_fail}</div>
                <div class="error">Error: {svg_error}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-title">PNG Files</div>
                <div>Total: {png_count}</div>
                <div class="pass">Pass: {png_pass}</div>
                <div class="warning">Warning: {png_warn}</div>
                <div class="fail">Fail: {png_fail}</div>
                <div class="error">Error: {png_error}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-title">WebP Files</div>
                <div>Total: {webp_count}</div>
                <div class="pass">Pass: {webp_pass}</div>
                <div class="warning">Warning: {webp_warn}</div>
                <div class="fail">Fail: {webp_fail}</div>
                <div class="error">Error: {webp_error}</div>
            </div>
        </div>
    </div>
    
    <div class="structure-section">
        <h2>Directory Structure</h2>
        <div>Status: <span class="{structure_result["status"]}">{structure_result["status"].upper()}</span></div>
        
        <h3>Modes</h3>
        <div>Found: {", ".join(structure_result["modes"])}</div>
        
        <h3>Finishes</h3>
        <div>Found: {", ".join(structure_result["finishes"])}</div>
        
        <h3>Sizes</h3>
        <div>Found: {", ".join(structure_result["sizes"])}</div>
        
        <h3>Contexts</h3>
        <div>Found: {", ".join(structure_result["contexts"])}</div>
        
        <h3>Issues</h3>
        <ul class="issue-list">""")

    # Add structure issues
    if structure_result["issues"]:
        for issue in structure_result["issues"]:
            html_parts.append(f"<li>{issue}</li>")
    else:
        html_parts.append("<li>No issues found</li>")

    html_parts.append("""
        </ul>
    </div>
    
    <h2>SVG Verification</h2>
    <table>
        <tr>
            <th>Filename</th>
            <th>Status</th>
            <th>Issues</th>
        </tr>""")

    # Add SVG results
    for i, r in enumerate(svg_results[:20]):
        html_parts.append(f"""
        <tr>
            <td>{r["filename"]}</td>
            <td><span class="badge badge-{r["status"]}">{r["status"]}</span></td>
            <td>
                <ul class="issue-list">""")

        if r["issues"]:
            for issue in r["issues"]:
                html_parts.append(f"<li>{issue}</li>")
        else:
            html_parts.append("<li>No issues</li>")

        html_parts.append("""
                </ul>
            </td>
        </tr>""")

    # Add "more files" row if needed
    if len(svg_results) > 20:
        html_parts.append(f"""
        <tr><td colspan='3'>... and {len(svg_results) - 20} more files</td></tr>""")

    html_parts.append("""
    </table>
    
    <h2>PNG Verification</h2>
    <table>
        <tr>
            <th>Filename</th>
            <th>Status</th>
            <th>Issues</th>
        </tr>""")

    # Add PNG results
    for i, r in enumerate(png_results[:20]):
        html_parts.append(f"""
        <tr>
            <td>{r["filename"]}</td>
            <td><span class="badge badge-{r["status"]}">{r["status"]}</span></td>
            <td>
                <ul class="issue-list">""")

        if r["issues"]:
            for issue in r["issues"]:
                html_parts.append(f"<li>{issue}</li>")
        else:
            html_parts.append("<li>No issues</li>")

        html_parts.append("""
                </ul>
            </td>
        </tr>""")

    # Add "more files" row if needed
    if len(png_results) > 20:
        html_parts.append(f"""
        <tr><td colspan='3'>... and {len(png_results) - 20} more files</td></tr>""")

    html_parts.append("""
    </table>
    
    <h2>Color Token Usage</h2>
    <table>
        <tr>
            <th>Filename</th>
            <th>Status</th>
            <th>Colors Found</th>
            <th>Issues</th>
        </tr>""")

    # Add color results
    for i, r in enumerate(color_results[:20]):
        html_parts.append(f"""
        <tr>
            <td>{r["filename"]}</td>
            <td><span class="badge badge-{r["status"]}">{r["status"]}</span></td>
            <td>
                <div class="color-grid">""")

        # Add color boxes (limited to 8)
        for color in r["colors_found"][:8]:
            html_parts.append(
                f'<div class="color-item"><div class="color-box" style="background-color: {color}"></div><div>{color}</div></div>')

        # Add "more colors" indication if needed
        if len(r["colors_found"]) > 8:
            html_parts.append(f"<div>...and {len(r['colors_found']) - 8} more</div>")

        html_parts.append("""
                </div>
            </td>
            <td>
                <ul class="issue-list">""")

        if r["issues"]:
            for issue in r["issues"]:
                html_parts.append(f"<li>{issue}</li>")
        else:
            html_parts.append("<li>No issues</li>")

        html_parts.append("""
                </ul>
            </td>
        </tr>""")

    # Add "more files" row if needed
    if len(color_results) > 20:
        html_parts.append(f"""
        <tr><td colspan='4'>... and {len(color_results) - 20} more files</td></tr>""")

    html_parts.append("""
    </table>
    
    <script>
        // Add expandable sections
        document.addEventListener('DOMContentLoaded', function() {
            const tables = document.querySelectorAll('table');
            tables.forEach(table => {
                if (table.rows.length > 10) {
                    // Add show/hide toggle
                    const container = table.parentNode;
                    const toggle = document.createElement('button');
                    toggle.textContent = 'Show All Rows';
                    toggle.style.marginBottom = '10px';
                    toggle.style.padding = '5px 10px';
                    toggle.style.background = '#f8f9fa';
                    toggle.style.border = '1px solid #ddd';
                    toggle.style.borderRadius = '4px';
                    toggle.style.cursor = 'pointer';
                    
                    container.insertBefore(toggle, table);
                    
                    // Hide rows beyond the first 5
                    for (let i = 6; i < table.rows.length - 1; i++) {
                        table.rows[i].style.display = 'none';
                    }
                    
                    // Toggle visibility
                    toggle.addEventListener('click', function() {
                        const isHidden = table.rows[6].style.display === 'none';
                        
                        for (let i = 6; i < table.rows.length - 1; i++) {
                            table.rows[i].style.display = isHidden ? '' : 'none';
                        }
                        
                        toggle.textContent = isHidden ? 'Show Fewer Rows' : 'Show All Rows';
                    });
                }
            });
        });
    </script>
</body>
</html>""")

    return "".join(html_parts)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="StrategyDECK Icon Verification Tool")

    parser.add_argument("--svg-only", action="store_true", help="Only verify SVG files")
    parser.add_argument("--png-only", action="store_true", help="Only verify PNG files")
    parser.add_argument("--color-only", action="store_true",
                        help="Only verify color tokens")
    parser.add_argument("--report", type=str, help="Output HTML report filename")
    parser.add_argument("--json", type=str, help="Output JSON report filename")

    args = parser.parse_args()

    # Load color tokens
    token_mapping = load_color_tokens()
    logger.info(f"Loaded {len(token_mapping)} color tokens")

    # Find files
    svg_files = find_svg_files() if not args.png_only else []
    png_files = find_png_files() if not args.svg_only and not args.color_only else []
    webp_files = find_webp_files() if not args.svg_only and not args.color_only else []

    logger.info(
        f"Found {len(svg_files)} SVG files, {len(png_files)} PNG files, and {len(webp_files)} WebP files")

    # Verify directory structure
    structure_result = verify_directory_structure()

    # Verify SVG files
    svg_results = []
    if svg_files:
        logger.info("Verifying SVG files...")
        for svg_file in svg_files:
            result = verify_svg_structure(svg_file)
            svg_results.append(result)

    # Verify PNG files
    png_results = []
    if png_files:
        logger.info("Verifying PNG files...")
        for png_file in png_files:
            result = verify_png_quality(png_file)
            png_results.append(result)

    # Verify WebP files
    webp_results = []
    if webp_files:
        logger.info("Verifying WebP files...")
        for webp_file in webp_files:
            result = verify_webp_quality(webp_file)
            webp_results.append(result)

    # Verify color tokens
    color_results = []
    if svg_files and not args.png_only:
        logger.info("Verifying color tokens...")
        for svg_file in svg_files:
            result = verify_color_tokens(svg_file, token_mapping)
            color_results.append(result)

    # Print summary
    svg_pass = sum(1 for r in svg_results if r["status"] == "pass")
    svg_warn = sum(1 for r in svg_results if r["status"] == "warning")
    svg_fail = sum(1 for r in svg_results if r["status"] == "fail")
    svg_error = sum(1 for r in svg_results if r["status"] == "error")

    png_pass = sum(1 for r in png_results if r["status"] == "pass")
    png_warn = sum(1 for r in png_results if r["status"] == "warning")
    png_fail = sum(1 for r in png_results if r["status"] == "fail")
    png_error = sum(1 for r in png_results if r["status"] == "error")

    webp_pass = sum(1 for r in webp_results if r["status"] == "pass")
    webp_warn = sum(1 for r in webp_results if r["status"] == "warning")
    webp_fail = sum(1 for r in webp_results if r["status"] == "fail")
    webp_error = sum(1 for r in webp_results if r["status"] == "error")

    print("\n" + "=" * 60)
    print(" StrategyDECK Icon Verification Summary ".center(60, "="))
    print("=" * 60)

    print(f"SVG Files: {len(svg_results)} total")
    print(
        f"  Pass: {svg_pass}, Warning: {svg_warn}, Fail: {svg_fail}, Error: {svg_error}")

    print(f"PNG Files: {len(png_results)} total")
    print(
        f"  Pass: {png_pass}, Warning: {png_warn}, Fail: {png_fail}, Error: {png_error}")

    print(f"WebP Files: {len(webp_results)} total")
    print(
        f"  Pass: {webp_pass}, Warning: {webp_warn}, Fail: {webp_fail}, Error: {webp_error}")

    # Show directory structure information
    print("\nDirectory Structure:")
    print(f"  Status: {structure_result['status'].upper()}")
    print(f"  Modes: {', '.join(structure_result['modes'])}")
    print(f"  Finishes: {len(structure_result['finishes'])} unique")
    print(f"  Sizes: {', '.join(structure_result['sizes'])}")
    print(f"  Contexts: {', '.join(structure_result['contexts'])}")

    if structure_result["issues"]:
        print("\nStructure Issues:")
        for issue in structure_result["issues"]:
            print(f"  - {issue}")

    # Prepare results for report
    import datetime
    results = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "svg_results": svg_results,
        "png_results": png_results,
        "webp_results": webp_results,
        "color_results": color_results,
        "structure_result": structure_result
    }

    # Generate report if requested
    if args.report:
        report_path = args.report
        if not report_path.endswith(".html"):
            report_path += ".html"

        logger.info(f"Generating HTML report: {report_path}")
        html_report = generate_report(results)

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_report)
            print(f"\nHTML report saved to: {report_path}")
        except Exception as e:
            logger.error(f"Error writing HTML report: {e}")

    # Generate JSON report if requested
    if args.json:
        json_path = args.json
        if not json_path.endswith(".json"):
            json_path += ".json"

        logger.info(f"Generating JSON report: {json_path}")

        # Clean up results for JSON serialization
        json_results = {
            "timestamp": results["timestamp"],
            "svg_verification": {
                "total": len(svg_results),
                "pass": svg_pass,
                "warning": svg_warn,
                "fail": svg_fail,
                "error": svg_error,
                "details": svg_results
            },
            "png_verification": {
                "total": len(png_results),
                "pass": png_pass,
                "warning": png_warn,
                "fail": png_fail,
                "error": png_error,
                "details": png_results
            },
            "webp_verification": {
                "total": len(webp_results),
                "pass": webp_pass,
                "warning": webp_warn,
                "fail": webp_fail,
                "error": webp_error,
                "details": webp_results
            },
            "color_verification": {
                "total": len(color_results),
                "details": color_results
            },
            "directory_structure": structure_result
        }

        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(json_results, f, indent=2)
            print(f"\nJSON report saved to: {json_path}")
        except Exception as e:
            logger.error(f"Error writing JSON report: {e}")

    # Return status code
    if svg_fail > 0 or png_fail > 0 or webp_fail > 0 or structure_result["status"] == "fail":
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
