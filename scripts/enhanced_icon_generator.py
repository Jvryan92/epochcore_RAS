#!/usr/bin/env python3
"""
Enhanced Icon Generator for StrategyDECK

This script extends the basic icon generation system with additional features:
- Batch processing with parallel execution
- Custom color palettes
- Additional output formats (WebP, AVIF)
- Optimization of SVG and PNG outputs
- Analytics on icon generation process
- CLI interface with rich output

Usage:
  python enhanced_icon_generator.py --mode batch --palette custom
  python enhanced_icon_generator.py --create-variant "dark,neon-blue,24,web"
  python enhanced_icon_generator.py --optimize-existing
"""

import argparse
import concurrent.futures
import csv
import json
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Add the scripts directory to the path to import generate_icons
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from generate_icons import (
        ASSETS,
        CSV_PATH,
        FINISH_COLORS,
        MASTERS,
        OUT,
        ROOT,
        TOKENS,
        bake_svg,
        maybe_export_png,
        pick_master,
    )
except ImportError:
    print("Error: Could not import from generate_icons.py")
    sys.exit(1)

# Enhanced color palettes
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
    },
    "gradient": {
        # These aren't real colors but placeholders for gradient processing
        "gradient-sunset": "gradient:#FF5E62,#FF9966",
        "gradient-ocean": "gradient:#2E3192,#1BFFFF",
        "gradient-forest": "gradient:#134E5E,#71B280",
        "gradient-berry": "gradient:#8A2387,#E94057,#F27121",
        "gradient-cosmic": "gradient:#000000,#434343",
    }
}

# Additional output formats
ADDITIONAL_FORMATS = ["webp", "avif"]

# Template tokens for SVG replacement
TEMPLATE_TOKENS = {
    "{{mode_bg}}": "background",
    "{{accent}}": "primary",
    "{{accent_secondary}}": "secondary",
    "{{text}}": "text"
}


@dataclass
class IconVariant:
    """Represents a single icon variant configuration"""
    mode: str
    finish: str
    size: int
    context: str
    filename: Optional[str] = None
    custom_colors: Dict[str, str] = None
    formats: List[str] = None

    def __post_init__(self):
        if self.custom_colors is None:
            self.custom_colors = {}
        if self.formats is None:
            self.formats = ["svg", "png"]
        if self.filename is None:
            self.filename = f"strategy_icon-{self.mode}-{self.finish}-{self.size}px.png"

    @property
    def base_filename(self) -> str:
        """Get the base filename without extension"""
        return Path(self.filename).stem

    @property
    def output_folder(self) -> Path:
        """Get the output folder for this variant"""
        return OUT / self.mode / self.finish / f"{self.size}px" / self.context


class IconGenerationStats:
    """Tracks statistics about the icon generation process"""

    def __init__(self):
        self.start_time = time.time()
        self.total_variants = 0
        self.successful_svgs = 0
        self.successful_pngs = 0
        self.successful_additional_formats = {fmt: 0 for fmt in ADDITIONAL_FORMATS}
        self.failed_variants = []
        self.processing_times = []

    def add_processing_time(self, duration: float):
        """Add a processing time measurement"""
        self.processing_times.append(duration)

    def record_success(self, variant: IconVariant, formats: List[str]):
        """Record successful generation of a variant"""
        self.total_variants += 1
        if "svg" in formats:
            self.successful_svgs += 1
        if "png" in formats:
            self.successful_pngs += 1
        for fmt in ADDITIONAL_FORMATS:
            if fmt in formats:
                self.successful_additional_formats[fmt] += 1

    def record_failure(self, variant: IconVariant, error: str):
        """Record a failed generation"""
        self.total_variants += 1
        self.failed_variants.append((variant, error))

    @property
    def elapsed_time(self) -> float:
        """Get total elapsed time"""
        return time.time() - self.start_time

    @property
    def average_processing_time(self) -> float:
        """Get average processing time per variant"""
        if not self.processing_times:
            return 0
        return sum(self.processing_times) / len(self.processing_times)

    def print_report(self):
        """Print a report of the generation statistics"""
        print("\n--- Icon Generation Report ---")
        print(f"Total variants processed: {self.total_variants}")
        print(f"Successful SVGs: {self.successful_svgs}")
        print(f"Successful PNGs: {self.successful_pngs}")

        for fmt, count in self.successful_additional_formats.items():
            if count > 0:
                print(f"Successful {fmt.upper()}: {count}")

        print(f"Failed variants: {len(self.failed_variants)}")
        print(f"Total time: {self.elapsed_time:.2f} seconds")
        print(f"Average time per variant: {self.average_processing_time:.4f} seconds")

        if self.failed_variants:
            print("\nFailed variants:")
            for variant, error in self.failed_variants:
                print(
                    f"  - {variant.mode}/{variant.finish}/{variant.size}px/{variant.context}: {error}")

        print("-----------------------------")


def generate_webp(svg_path: Path, output_path: Path, size_px: int) -> bool:
    """Generate WebP from SVG"""
    try:
        # First try with cairosvg + PIL
        import io

        import cairosvg
        from PIL import Image

        # Convert SVG to PNG in memory
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size_px,
            output_height=size_px
        )

        # Convert PNG to WebP
        image = Image.open(io.BytesIO(png_data))
        image.save(str(output_path), format="WEBP", quality=90)
        return True
    except Exception as e:
        print(f"WebP conversion failed: {e}")
        return False


def generate_avif(svg_path: Path, output_path: Path, size_px: int) -> bool:
    """Generate AVIF from SVG"""
    try:
        # Requires pillow-avif-plugin or similar
        import io

        import cairosvg
        from PIL import Image

        # Convert SVG to PNG in memory
        png_data = cairosvg.svg2png(
            url=str(svg_path),
            output_width=size_px,
            output_height=size_px
        )

        # Convert PNG to AVIF
        image = Image.open(io.BytesIO(png_data))
        image.save(str(output_path), format="AVIF", quality=90)
        return True
    except Exception as e:
        print(f"AVIF conversion failed: {e}")
        return False


def optimize_svg(svg_path: Path) -> bool:
    """Optimize SVG file size"""
    try:
        # Try with svgo if available
        import subprocess

        result = subprocess.run(
            ["svgo", str(svg_path), "--multipass"],
            capture_output=True,
            text=True
        )

        return result.returncode == 0
    except Exception as e:
        print(f"SVG optimization failed: {e}")
        return False


def optimize_png(png_path: Path) -> bool:
    """Optimize PNG file size"""
    try:
        # Try with pngquant if available
        import subprocess

        result = subprocess.run(
            ["pngquant", "--force", "--ext", ".png", "--quality=80-95", str(png_path)],
            capture_output=True,
            text=True
        )

        return result.returncode == 0
    except Exception as e:
        try:
            # Fallback to PIL
            from PIL import Image

            image = Image.open(png_path)
            image.save(png_path, optimize=True, quality=95)
            return True
        except Exception as e2:
            print(f"PNG optimization failed: {e}, {e2}")
            return False


def process_variant(variant: IconVariant, optimize: bool = False) -> Tuple[bool, List[str], Optional[str]]:
    """Process a single icon variant"""
    start_time = time.time()

    try:
        # Create output directory
        variant.output_folder.mkdir(parents=True, exist_ok=True)

        # Select master SVG
        master_path = pick_master(variant.size)
        if not master_path.exists():
            return False, [], f"Master not found: {master_path}"

        # Read master SVG
        master_svg = master_path.read_text(encoding="utf-8")

        # Apply custom colors if provided
        if variant.custom_colors:
            # This is a placeholder for custom color handling
            # In a real implementation, we'd use variant.custom_colors
            # to override the default colors used in bake_svg
            baked_svg = bake_svg(master_svg, variant.mode, variant.finish)
        else:
            baked_svg = bake_svg(master_svg, variant.mode, variant.finish)

        # Create output paths
        svg_path = variant.output_folder / f"{variant.base_filename}.svg"
        png_path = variant.output_folder / variant.filename

        # Additional format paths
        additional_paths = {
            fmt: variant.output_folder / f"{variant.base_filename}.{fmt}"
            for fmt in ADDITIONAL_FORMATS
            if fmt in variant.formats
        }

        # Write SVG file
        svg_path.write_text(baked_svg, encoding="utf-8")

        # Optimize SVG if requested
        if optimize and "svg" in variant.formats:
            optimize_svg(svg_path)

        # Generate and possibly optimize PNG
        successful_formats = ["svg"]
        if "png" in variant.formats:
            png_ok = maybe_export_png(
                baked_svg.encode("utf-8"), png_path, variant.size
            )
            if png_ok:
                successful_formats.append("png")

                # Optimize PNG if requested
                if optimize:
                    optimize_png(png_path)

        # Generate additional formats
        for fmt, path in additional_paths.items():
            if fmt == "webp":
                webp_ok = generate_webp(svg_path, path, variant.size)
                if webp_ok:
                    successful_formats.append("webp")
            elif fmt == "avif":
                avif_ok = generate_avif(svg_path, path, variant.size)
                if avif_ok:
                    successful_formats.append("avif")

        # Record processing time
        processing_time = time.time() - start_time

        return True, successful_formats, None
    except Exception as e:
        return False, [], str(e)


def load_variants_from_csv() -> List[IconVariant]:
    """Load icon variants from the CSV matrix file"""
    if not CSV_PATH.exists():
        print(f"[error] Missing CSV matrix at {CSV_PATH}")
        sys.exit(1)

    variants = []
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    for r in rows:
        variant = IconVariant(
            mode=r["Mode"],
            finish=r["Finish"],
            size=int(r["Size (px)"]),
            context=r["Context"],
            filename=r.get("Filename")
        )
        variants.append(variant)

    return variants


def load_custom_palette(palette_name: str) -> Dict[str, str]:
    """Load a custom color palette"""
    if palette_name in ENHANCED_PALETTES:
        return ENHANCED_PALETTES[palette_name]

    # Try to load from file
    palette_path = ROOT / "config" / f"{palette_name}_palette.json"
    if palette_path.exists():
        try:
            with open(palette_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading palette {palette_name}: {e}")

    return {}


def create_variant_matrix(options: Dict[str, List[str]]) -> List[IconVariant]:
    """Create a matrix of variants from option combinations"""
    variants = []

    # Default options if not provided
    options.setdefault("modes", ["light", "dark"])
    options.setdefault("finishes", list(FINISH_COLORS.keys()))
    options.setdefault("sizes", [16, 32, 48])
    options.setdefault("contexts", ["web"])
    options.setdefault("formats", ["svg", "png"])

    for mode in options["modes"]:
        for finish in options["finishes"]:
            for size in options["sizes"]:
                for context in options["contexts"]:
                    variant = IconVariant(
                        mode=mode,
                        finish=finish,
                        size=int(size),
                        context=context,
                        formats=options["formats"]
                    )
                    variants.append(variant)

    return variants


def process_template_variant(variant: IconVariant, optimize: bool = False) -> Tuple[bool, List[str], Optional[str]]:
    """Process a single icon variant using template-based token replacement

    This function extends the basic process_variant function to support more
    advanced token replacement in SVG templates. Instead of just replacing
    specific hex colors, it supports named token replacement like {{primary}},
    {{secondary}}, etc.

    The variant's custom_colors dictionary should contain the token values.
    """
    start_time = time.time()

    try:
        # Create output directory
        variant.output_folder.mkdir(parents=True, exist_ok=True)

        # Select master SVG
        master_path = pick_master(variant.size)
        if not master_path.exists():
            return False, [], f"Master not found: {master_path}"

        # Read master SVG
        master_svg = master_path.read_text(encoding="utf-8")

        # Apply token replacements if custom colors are provided
        if variant.custom_colors:
            # Replace tokens in the format {{token_name}}
            svg_content = master_svg
            for token_name, color_value in variant.custom_colors.items():
                svg_content = svg_content.replace(f"{{{{{token_name}}}}}", color_value)

            # Apply standard bake_svg for backward compatibility
            baked_svg = bake_svg(svg_content, variant.mode, variant.finish)
        else:
            # Fallback to standard processing
            baked_svg = bake_svg(master_svg, variant.mode, variant.finish)

        # Create output paths
        svg_path = variant.output_folder / f"{variant.base_filename}.svg"
        png_path = variant.output_folder / variant.filename

        # Additional format paths
        additional_paths = {
            fmt: variant.output_folder / f"{variant.base_filename}.{fmt}"
            for fmt in ADDITIONAL_FORMATS
            if fmt in variant.formats
        }

        # Write SVG file
        svg_path.write_text(baked_svg, encoding="utf-8")

        # Optimize SVG if requested
        if optimize and "svg" in variant.formats:
            optimize_svg(svg_path)

        # Generate and possibly optimize PNG
        successful_formats = ["svg"]
        if "png" in variant.formats:
            png_ok = maybe_export_png(
                baked_svg.encode("utf-8"), png_path, variant.size
            )
            if png_ok:
                successful_formats.append("png")

                # Optimize PNG if requested
                if optimize:
                    optimize_png(png_path)

        # Generate additional formats
        for fmt, path in additional_paths.items():
            if fmt == "webp":
                webp_ok = generate_webp(svg_path, path, variant.size)
                if webp_ok:
                    successful_formats.append("webp")
            elif fmt == "avif":
                avif_ok = generate_avif(svg_path, path, variant.size)
                if avif_ok:
                    successful_formats.append("avif")

        # Record processing time
        processing_time = time.time() - start_time

        return True, successful_formats, None
    except Exception as e:
        return False, [], str(e)


def batch_generate_icons(
    variants: List[IconVariant],
    parallel: bool = True,
    optimize: bool = False
) -> IconGenerationStats:
    """Generate multiple icon variants, optionally in parallel"""
    stats = IconGenerationStats()

    if parallel:
        # Process variants in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_variant = {
                executor.submit(process_variant, variant, optimize): variant
                for variant in variants
            }

            for future in concurrent.futures.as_completed(future_to_variant):
                variant = future_to_variant[future]
                success, formats, error = future.result()

                if success:
                    stats.record_success(variant, formats)
                    print(
                        f"✓ Generated {variant.mode}/{variant.finish}/{variant.size}px/{variant.context}")
                else:
                    stats.record_failure(variant, error)
                    print(
                        f"✗ Failed {variant.mode}/{variant.finish}/{variant.size}px/{variant.context}: {error}")
    else:
        # Process variants sequentially
        for variant in variants:
            start_time = time.time()
            success, formats, error = process_variant(variant, optimize)
            processing_time = time.time() - start_time
            stats.add_processing_time(processing_time)

            if success:
                stats.record_success(variant, formats)
                print(
                    f"✓ Generated {variant.mode}/{variant.finish}/{variant.size}px/{variant.context}")
            else:
                stats.record_failure(variant, error)
                print(
                    f"✗ Failed {variant.mode}/{variant.finish}/{variant.size}px/{variant.context}: {error}")

    return stats


def optimize_existing_icons() -> int:
    """Optimize all existing SVG and PNG files"""
    optimized = 0

    # Find all SVG files
    svg_files = list(OUT.glob("**/*.svg"))
    print(f"Found {len(svg_files)} SVG files to optimize")

    for svg_path in svg_files:
        if optimize_svg(svg_path):
            optimized += 1
            print(f"✓ Optimized {svg_path.relative_to(ROOT)}")
        else:
            print(f"✗ Failed to optimize {svg_path.relative_to(ROOT)}")

    # Find all PNG files
    png_files = list(OUT.glob("**/*.png"))
    print(f"Found {len(png_files)} PNG files to optimize")

    for png_path in png_files:
        if optimize_png(png_path):
            optimized += 1
            print(f"✓ Optimized {png_path.relative_to(ROOT)}")
        else:
            print(f"✗ Failed to optimize {png_path.relative_to(ROOT)}")

    return optimized


def create_variant_from_string(variant_str: str) -> Optional[IconVariant]:
    """Create a variant from a comma-separated string"""
    try:
        parts = variant_str.split(",")
        if len(parts) < 4:
            print("Error: Variant string must have at least 4 parts: mode,finish,size,context")
            return None

        mode, finish, size, context = parts[:4]
        filename = parts[4] if len(parts) > 4 else None

        return IconVariant(
            mode=mode,
            finish=finish,
            size=int(size),
            context=context,
            filename=filename
        )
    except Exception as e:
        print(f"Error parsing variant string: {e}")
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Enhanced Icon Generator for StrategyDECK")

    # Mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--csv", action="store_true",
                            help="Generate icons from CSV matrix (default)")
    mode_group.add_argument("--batch", action="store_true",
                            help="Generate icons in batch mode")
    mode_group.add_argument("--create-variant", metavar="MODE,FINISH,SIZE,CONTEXT[,FILENAME]",
                            help="Create a single variant from a string specification")
    mode_group.add_argument("--optimize-existing", action="store_true",
                            help="Optimize all existing SVG and PNG files")

    # Batch mode options
    parser.add_argument("--modes", nargs="+",
                        help="Icon modes to generate (for batch mode)")
    parser.add_argument("--finishes", nargs="+",
                        help="Icon finishes to generate (for batch mode)")
    parser.add_argument("--sizes", nargs="+", type=int,
                        help="Icon sizes to generate (for batch mode)")
    parser.add_argument("--contexts", nargs="+",
                        help="Icon contexts to generate (for batch mode)")

    # Format options
    parser.add_argument("--formats", nargs="+", choices=["svg", "png", "webp", "avif"],
                        default=["svg", "png"], help="Output formats to generate")

    # Palette options
    parser.add_argument("--palette", help="Custom color palette to use")

    # Processing options
    parser.add_argument("--parallel", action="store_true",
                        help="Process variants in parallel")
    parser.add_argument("--optimize", action="store_true", help="Optimize output files")
    parser.add_argument("--output-dir", help="Custom output directory")

    args = parser.parse_args()

    # Set custom output directory if specified
    if args.output_dir:
        global OUT
        OUT = Path(args.output_dir).resolve()
        OUT.mkdir(parents=True, exist_ok=True)

    # Handle optimize existing mode
    if args.optimize_existing:
        count = optimize_existing_icons()
        print(f"Optimized {count} files")
        return

    # Create variants list based on mode
    variants = []

    if args.create_variant:
        # Create a single variant
        variant = create_variant_from_string(args.create_variant)
        if variant:
            variant.formats = args.formats
            variants = [variant]
        else:
            sys.exit(1)
    elif args.batch:
        # Create variants from batch options
        options = {
            "modes": args.modes,
            "finishes": args.finishes,
            "sizes": args.sizes,
            "contexts": args.contexts,
            "formats": args.formats
        }
        # Filter out None values
        options = {k: v for k, v in options.items() if v is not None}
        variants = create_variant_matrix(options)
    else:
        # Default: load from CSV
        variants = load_variants_from_csv()
        # Update formats for all variants
        for variant in variants:
            variant.formats = args.formats

    # Apply custom palette if specified
    if args.palette:
        custom_colors = load_custom_palette(args.palette)
        if custom_colors:
            print(
                f"Loaded custom palette: {args.palette} with {len(custom_colors)} colors")
            # Apply to FINISH_COLORS (this will affect all variants)
            FINISH_COLORS.update(custom_colors)

    # Generate icons
    print(f"Generating {len(variants)} icon variants...")
    stats = batch_generate_icons(variants, args.parallel, args.optimize)

    # Print report
    stats.print_report()


if __name__ == "__main__":
    main()
