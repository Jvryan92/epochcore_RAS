#!/usr/bin/env python3
"""
StrategyDECK Icon Generation Report Tool

This script provides comprehensive reporting on the icon generation system,
including statistics, validation, and quality checks of generated assets.
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Add the scripts directory to the path
SCRIPT_DIR = Path(__file__).resolve().parent / "scripts"
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Create report output directory
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# Asset directories
ASSETS_DIR = ROOT / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
MASTERS_DIR = ASSETS_DIR / "masters"

# CSV variant matrix
VARIANT_MATRIX = ROOT / "strategy_icon_variant_matrix.csv"

# ANSI colors for terminal output


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_section(title):
    """Print a section header"""
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.END}")
    print(f"{Colors.HEADER} {title.center(58)} {Colors.END}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.END}")


def print_subsection(title):
    """Print a subsection header"""
    print(f"\n{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BLUE}{'-' * len(title)}{Colors.END}")


def has_cairosvg():
    """Check if CairoSVG is installed"""
    try:
        import cairosvg
        return True
    except ImportError:
        return False


def read_variant_matrix() -> List[Dict]:
    """Read the variant matrix CSV file"""
    if not VARIANT_MATRIX.exists():
        print(f"{Colors.RED}Error: Variant matrix file not found at {VARIANT_MATRIX}{Colors.END}")
        return []

    variants = []
    try:
        with open(VARIANT_MATRIX, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                variants.append(row)
        return variants
    except Exception as e:
        print(f"{Colors.RED}Error reading variant matrix: {e}{Colors.END}")
        return []


def scan_generated_icons() -> Tuple[Dict, Dict]:
    """Scan the icons directory and count SVG and PNG files"""
    if not ICONS_DIR.exists():
        print(f"{Colors.YELLOW}Warning: Icons directory not found at {ICONS_DIR}{Colors.END}")
        return {}, {}

    # Structure: {mode: {finish: {size: {context: count}}}}
    svg_counts = {}
    png_counts = {}

    # Walk through the icons directory
    for mode_dir in ICONS_DIR.iterdir():
        if not mode_dir.is_dir():
            continue

        mode = mode_dir.name
        svg_counts[mode] = {}
        png_counts[mode] = {}

        for finish_dir in mode_dir.iterdir():
            if not finish_dir.is_dir():
                continue

            finish = finish_dir.name
            svg_counts[mode][finish] = {}
            png_counts[mode][finish] = {}

            for size_dir in finish_dir.iterdir():
                if not size_dir.is_dir():
                    continue

                size = size_dir.name
                svg_counts[mode][finish][size] = {}
                png_counts[mode][finish][size] = {}

                for context_dir in size_dir.iterdir():
                    if not context_dir.is_dir():
                        continue

                    context = context_dir.name

                    # Count SVG files
                    svg_files = list(context_dir.glob("*.svg"))
                    svg_counts[mode][finish][size][context] = len(svg_files)

                    # Count PNG files
                    png_files = list(context_dir.glob("*.png"))
                    png_counts[mode][finish][size][context] = len(png_files)

    return svg_counts, png_counts


def validate_icons(svg_counts: Dict, png_counts: Dict, variants: List[Dict]) -> Dict:
    """Validate that all expected icons have been generated"""
    validation = {
        "expected_variants": len(variants),
        "found_svg_variants": 0,
        "found_png_variants": 0,
        "missing_svg_variants": [],
        "missing_png_variants": [],
        "has_cairosvg": has_cairosvg(),
    }

    # Check each expected variant
    for variant in variants:
        mode = variant.get("mode", "").strip()
        finish = variant.get("finish", "").strip()
        size = variant.get("size", "").strip() + "px"
        context = variant.get("context", "").strip()

        # Check SVG
        try:
            if svg_counts.get(mode, {}).get(finish, {}).get(size, {}).get(context, 0) > 0:
                validation["found_svg_variants"] += 1
            else:
                validation["missing_svg_variants"].append({
                    "mode": mode,
                    "finish": finish,
                    "size": size,
                    "context": context
                })
        except Exception as e:
            print(
                f"{Colors.RED}Error validating SVG variant {mode}/{finish}/{size}/{context}: {e}{Colors.END}")

        # Check PNG
        try:
            if png_counts.get(mode, {}).get(finish, {}).get(size, {}).get(context, 0) > 0:
                validation["found_png_variants"] += 1
            else:
                validation["missing_png_variants"].append({
                    "mode": mode,
                    "finish": finish,
                    "size": size,
                    "context": context
                })
        except Exception as e:
            print(
                f"{Colors.RED}Error validating PNG variant {mode}/{finish}/{size}/{context}: {e}{Colors.END}")

    return validation


def check_svg_quality(svg_files: List[Path]) -> Dict:
    """Check the quality of SVG files"""
    quality_report = {
        "total_files": len(svg_files),
        "valid_files": 0,
        "invalid_files": 0,
        "empty_files": 0,
        "missing_viewbox": 0,
        "issues": []
    }

    for svg_file in svg_files:
        try:
            # Check file size
            if svg_file.stat().st_size == 0:
                quality_report["empty_files"] += 1
                quality_report["issues"].append({
                    "file": str(svg_file),
                    "issue": "Empty file"
                })
                continue

            # Read file content
            with open(svg_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for basic SVG structure
            if not content.startswith('<svg') and not '<svg' in content:
                quality_report["invalid_files"] += 1
                quality_report["issues"].append({
                    "file": str(svg_file),
                    "issue": "Missing SVG tag"
                })
                continue

            # Check for viewBox
            if 'viewBox' not in content:
                quality_report["missing_viewbox"] += 1
                quality_report["issues"].append({
                    "file": str(svg_file),
                    "issue": "Missing viewBox attribute"
                })

            # File is valid if we get here
            quality_report["valid_files"] += 1

        except Exception as e:
            quality_report["invalid_files"] += 1
            quality_report["issues"].append({
                "file": str(svg_file),
                "issue": f"Error: {str(e)}"
            })

    return quality_report


def check_png_quality(png_files: List[Path]) -> Dict:
    """Check the quality of PNG files"""
    quality_report = {
        "total_files": len(png_files),
        "valid_files": 0,
        "invalid_files": 0,
        "empty_files": 0,
        "issues": []
    }

    # Try to import PIL
    try:
        from PIL import Image
        has_pil = True
    except ImportError:
        has_pil = False
        quality_report["issues"].append({
            "file": "N/A",
            "issue": "PIL not installed, cannot check PNG dimensions"
        })

    for png_file in png_files:
        try:
            # Check file size
            if png_file.stat().st_size == 0:
                quality_report["empty_files"] += 1
                quality_report["issues"].append({
                    "file": str(png_file),
                    "issue": "Empty file"
                })
                continue

            # Check PNG header
            with open(png_file, 'rb') as f:
                header = f.read(8)

            if header != b'\x89PNG\r\n\x1a\n':
                quality_report["invalid_files"] += 1
                quality_report["issues"].append({
                    "file": str(png_file),
                    "issue": "Invalid PNG header"
                })
                continue

            # Check dimensions with PIL if available
            if has_pil:
                try:
                    with Image.open(png_file) as img:
                        width, height = img.size

                        # Check if dimensions match expected size
                        size_match = re.search(r'/(\d+)px/', str(png_file))
                        if size_match:
                            expected_size = int(size_match.group(1))
                            if width != expected_size or height != expected_size:
                                quality_report["issues"].append({
                                    "file": str(png_file),
                                    "issue": f"Size mismatch: expected {expected_size}x{expected_size}, got {width}x{height}"
                                })
                except Exception as e:
                    quality_report["invalid_files"] += 1
                    quality_report["issues"].append({
                        "file": str(png_file),
                        "issue": f"Error opening with PIL: {str(e)}"
                    })
                    continue

            # File is valid if we get here
            quality_report["valid_files"] += 1

        except Exception as e:
            quality_report["invalid_files"] += 1
            quality_report["issues"].append({
                "file": str(png_file),
                "issue": f"Error: {str(e)}"
            })

    return quality_report


def check_master_files() -> Dict:
    """Check the master SVG files"""
    master_report = {
        "micro_exists": False,
        "standard_exists": False,
        "micro_size": 0,
        "standard_size": 0,
        "issues": []
    }

    # Check micro master
    micro_master = MASTERS_DIR / "strategy_icon_micro.svg"
    if micro_master.exists():
        master_report["micro_exists"] = True
        master_report["micro_size"] = micro_master.stat().st_size

        # Check content
        try:
            with open(micro_master, 'r', encoding='utf-8') as f:
                content = f.read()

            if '#FF6A00' not in content:
                master_report["issues"].append({
                    "file": str(micro_master),
                    "issue": "Missing #FF6A00 background color"
                })

            if '#FFFFFF' not in content:
                master_report["issues"].append({
                    "file": str(micro_master),
                    "issue": "Missing #FFFFFF foreground color"
                })
        except Exception as e:
            master_report["issues"].append({
                "file": str(micro_master),
                "issue": f"Error reading: {str(e)}"
            })
    else:
        master_report["issues"].append({
            "file": str(micro_master),
            "issue": "File does not exist"
        })

    # Check standard master
    standard_master = MASTERS_DIR / "strategy_icon_standard.svg"
    if standard_master.exists():
        master_report["standard_exists"] = True
        master_report["standard_size"] = standard_master.stat().st_size

        # Check content
        try:
            with open(standard_master, 'r', encoding='utf-8') as f:
                content = f.read()

            if '#FF6A00' not in content:
                master_report["issues"].append({
                    "file": str(standard_master),
                    "issue": "Missing #FF6A00 background color"
                })

            if '#FFFFFF' not in content:
                master_report["issues"].append({
                    "file": str(standard_master),
                    "issue": "Missing #FFFFFF foreground color"
                })
        except Exception as e:
            master_report["issues"].append({
                "file": str(standard_master),
                "issue": f"Error reading: {str(e)}"
            })
    else:
        master_report["issues"].append({
            "file": str(standard_master),
            "issue": "File does not exist"
        })

    return master_report


def check_endless_glyph_system() -> Dict:
    """Check the endless glyph system if it exists"""
    glyph_report = {
        "exists": False,
        "theme_count": 0,
        "themes": [],
        "issues": []
    }

    # Check if endless_glyph_generator.py exists
    glyph_script = SCRIPT_DIR / "endless_glyph_generator.py"
    if not glyph_script.exists():
        return glyph_report

    glyph_report["exists"] = True

    # Try to import
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        import endless_glyph_generator

        # Look for themes
        themes = []
        for attr in dir(endless_glyph_generator):
            if attr.endswith('_THEME') and isinstance(getattr(endless_glyph_generator, attr), dict):
                theme_name = attr.replace('_THEME', '').lower()
                themes.append(theme_name)

        glyph_report["theme_count"] = len(themes)
        glyph_report["themes"] = themes

        # Check for required functions
        required_functions = ["generate_glyph", "process_glyph_variant"]
        for func in required_functions:
            if not hasattr(endless_glyph_generator, func):
                glyph_report["issues"].append({
                    "issue": f"Missing required function: {func}"
                })

    except Exception as e:
        glyph_report["issues"].append({
            "issue": f"Error importing endless_glyph_generator: {str(e)}"
        })

    return glyph_report


def generate_report(args):
    """Generate the comprehensive report"""
    print_section("StrategyDECK Icon Generation Report")
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Read variant matrix
    print_subsection("Reading Variant Matrix")
    variants = read_variant_matrix()
    if variants:
        print(f"{Colors.GREEN}Found {len(variants)} variants in the matrix{Colors.END}")
    else:
        print(f"{Colors.RED}No variants found in the matrix{Colors.END}")

    # Scan generated icons
    print_subsection("Scanning Generated Icons")
    svg_counts, png_counts = scan_generated_icons()

    # Count totals
    svg_total = sum(sum(sum(sum(count for count in contexts.values())
                            for contexts in sizes.values())
                        for sizes in finishes.values())
                    for finishes in svg_counts.values())

    png_total = sum(sum(sum(sum(count for count in contexts.values())
                            for contexts in sizes.values())
                        for sizes in finishes.values())
                    for finishes in png_counts.values())

    print(f"{Colors.GREEN}Found {svg_total} SVG files{Colors.END}")
    print(f"{Colors.GREEN}Found {png_total} PNG files{Colors.END}")

    # Validate icons
    print_subsection("Validating Icons")
    validation = validate_icons(svg_counts, png_counts, variants)

    print(f"Expected variants: {validation['expected_variants']}")
    print(f"Found SVG variants: {validation['found_svg_variants']}")
    print(f"Found PNG variants: {validation['found_png_variants']}")

    # Report missing variants
    if validation["missing_svg_variants"]:
        print(
            f"\n{Colors.YELLOW}Missing SVG variants: {len(validation['missing_svg_variants'])}{Colors.END}")
        if args.verbose and validation["missing_svg_variants"]:
            for variant in validation["missing_svg_variants"][:5]:  # Show only first 5
                print(
                    f"  - {variant['mode']}/{variant['finish']}/{variant['size']}/{variant['context']}")
            if len(validation["missing_svg_variants"]) > 5:
                print(f"  ... and {len(validation['missing_svg_variants']) - 5} more")

    if validation["missing_png_variants"]:
        print(
            f"\n{Colors.YELLOW}Missing PNG variants: {len(validation['missing_png_variants'])}{Colors.END}")
        if not validation["has_cairosvg"]:
            print(
                f"{Colors.YELLOW}Note: CairoSVG is not installed, which is required for PNG generation{Colors.END}")
        if args.verbose and validation["missing_png_variants"]:
            for variant in validation["missing_png_variants"][:5]:  # Show only first 5
                print(
                    f"  - {variant['mode']}/{variant['finish']}/{variant['size']}/{variant['context']}")
            if len(validation["missing_png_variants"]) > 5:
                print(f"  ... and {len(validation['missing_png_variants']) - 5} more")

    # Check master files
    print_subsection("Checking Master Files")
    master_report = check_master_files()

    if master_report["micro_exists"]:
        print(
            f"{Colors.GREEN}Micro master exists: {master_report['micro_size']} bytes{Colors.END}")
    else:
        print(f"{Colors.RED}Micro master does not exist{Colors.END}")

    if master_report["standard_exists"]:
        print(
            f"{Colors.GREEN}Standard master exists: {master_report['standard_size']} bytes{Colors.END}")
    else:
        print(f"{Colors.RED}Standard master does not exist{Colors.END}")

    if master_report["issues"]:
        print(
            f"\n{Colors.YELLOW}Master file issues: {len(master_report['issues'])}{Colors.END}")
        if args.verbose:
            for issue in master_report["issues"]:
                print(f"  - {issue['file']}: {issue['issue']}")

    # Check quality of SVG files
    if args.quality and svg_total > 0:
        print_subsection("Checking SVG Quality")

        # Sample some SVG files
        svg_files = list(ICONS_DIR.glob("**/*.svg"))
        sample_size = min(100, len(svg_files))  # Check at most 100 files
        sample = svg_files[:sample_size]

        svg_quality = check_svg_quality(sample)

        print(f"Total files checked: {svg_quality['total_files']}")
        print(f"Valid files: {svg_quality['valid_files']}")
        print(f"Invalid files: {svg_quality['invalid_files']}")
        print(f"Empty files: {svg_quality['empty_files']}")
        print(f"Missing viewBox: {svg_quality['missing_viewbox']}")

        if svg_quality["issues"]:
            print(
                f"\n{Colors.YELLOW}SVG quality issues: {len(svg_quality['issues'])}{Colors.END}")
            if args.verbose:
                for issue in svg_quality["issues"][:5]:  # Show only first 5
                    print(f"  - {issue['file']}: {issue['issue']}")
                if len(svg_quality["issues"]) > 5:
                    print(f"  ... and {len(svg_quality['issues']) - 5} more")

    # Check quality of PNG files
    if args.quality and png_total > 0:
        print_subsection("Checking PNG Quality")

        # Sample some PNG files
        png_files = list(ICONS_DIR.glob("**/*.png"))
        sample_size = min(100, len(png_files))  # Check at most 100 files
        sample = png_files[:sample_size]

        png_quality = check_png_quality(sample)

        print(f"Total files checked: {png_quality['total_files']}")
        print(f"Valid files: {png_quality['valid_files']}")
        print(f"Invalid files: {png_quality['invalid_files']}")
        print(f"Empty files: {png_quality['empty_files']}")

        if png_quality["issues"]:
            print(
                f"\n{Colors.YELLOW}PNG quality issues: {len(png_quality['issues'])}{Colors.END}")
            if args.verbose:
                for issue in png_quality["issues"][:5]:  # Show only first 5
                    print(f"  - {issue['file']}: {issue['issue']}")
                if len(png_quality["issues"]) > 5:
                    print(f"  ... and {len(png_quality['issues']) - 5} more")

    # Check for endless glyph system
    print_subsection("Checking Endless Glyph System")
    glyph_report = check_endless_glyph_system()

    if glyph_report["exists"]:
        print(f"{Colors.GREEN}Endless Glyph System found{Colors.END}")
        print(f"Themes: {len(glyph_report['themes'])}")
        if args.verbose:
            print(f"Available themes: {', '.join(glyph_report['themes'])}")
    else:
        print(f"{Colors.YELLOW}Endless Glyph System not found{Colors.END}")

    if glyph_report["issues"]:
        print(
            f"\n{Colors.YELLOW}Glyph system issues: {len(glyph_report['issues'])}{Colors.END}")
        if args.verbose:
            for issue in glyph_report["issues"]:
                print(f"  - {issue['issue']}")

    # Save report to file
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = REPORT_DIR / f"icon_report_{timestamp}.json"

    # Collect all report data
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "variants": {
            "total": len(variants),
            "examples": variants[:5] if variants else []
        },
        "counts": {
            "svg_total": svg_total,
            "png_total": png_total,
            "svg_variants": validation["found_svg_variants"],
            "png_variants": validation["found_png_variants"],
            "missing_svg": len(validation["missing_svg_variants"]),
            "missing_png": len(validation["missing_png_variants"])
        },
        "validation": validation,
        "master_files": master_report,
        "endless_glyph": glyph_report
    }

    # Add quality data if collected
    if args.quality:
        if svg_total > 0:
            report_data["svg_quality"] = svg_quality
        if png_total > 0:
            report_data["png_quality"] = png_quality

    # Save as JSON
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        print(f"\n{Colors.GREEN}Report saved to {output_path}{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}Error saving report: {e}{Colors.END}")

    # Print summary
    print_section("Report Summary")

    if svg_total == 0:
        print(f"{Colors.RED}No SVG files found. Icon generation may have failed.{Colors.END}")
    elif validation["found_svg_variants"] < validation["expected_variants"]:
        print(
            f"{Colors.YELLOW}Some SVG variants are missing. Run with --verbose for details.{Colors.END}")
    else:
        print(f"{Colors.GREEN}All expected SVG variants were generated successfully.{Colors.END}")

    if not validation["has_cairosvg"]:
        print(f"{Colors.YELLOW}CairoSVG is not installed, PNG generation is disabled.{Colors.END}")
        print(f"{Colors.YELLOW}To enable PNG generation, run: pip install cairosvg{Colors.END}")
    elif png_total == 0:
        print(f"{Colors.RED}No PNG files found. PNG conversion may have failed.{Colors.END}")
        print(
            f"{Colors.YELLOW}Run debug_png_conversion.py to diagnose PNG conversion issues.{Colors.END}")
    elif validation["found_png_variants"] < validation["expected_variants"]:
        print(
            f"{Colors.YELLOW}Some PNG variants are missing. Run with --verbose for details.{Colors.END}")
    else:
        print(f"{Colors.GREEN}All expected PNG variants were generated successfully.{Colors.END}")

    # Display potential solutions for issues
    if (validation["found_svg_variants"] < validation["expected_variants"] or
            (validation["has_cairosvg"] and validation["found_png_variants"] < validation["expected_variants"])):
        print("\nSuggested Solutions:")
        print(
            f"1. Run the clean rebuild script: {Colors.BOLD}./clean_rebuild_assets.sh{Colors.END}")
        print(f"2. Check master SVG files for correct color tokens")
        print(f"3. Validate the variant matrix CSV file")
        if validation["has_cairosvg"] and validation["found_png_variants"] < validation["expected_variants"]:
            print(
                f"4. Debug PNG conversion: {Colors.BOLD}python debug_png_conversion.py --report{Colors.END}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate report on StrategyDECK icon generation")
    parser.add_argument(
        "--output", help="Output file path for the report (JSON format)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show detailed information")
    parser.add_argument("--quality", action="store_true",
                        help="Check quality of generated files")
    parser.add_argument("--html", action="store_true",
                        help="Generate HTML report (not implemented yet)")

    args = parser.parse_args()

    try:
        generate_report(args)
        return 0
    except Exception as e:
        print(f"{Colors.RED}Error generating report: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
