#!/usr/bin/env python3
"""
StrategyDECK Unified Icon Generator

This script provides a unified approach to icon generation, supporting both
CSV-based and JSON-based configuration, with enhanced features like:
- Parallel processing
- Multiple export formats
- Configurable optimization
- Detailed reporting and metrics
- Automatic fallback for PNG generation
"""

import argparse
import concurrent.futures
import csv
import json
import logging
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("icon_generator.log"),
    ],
)
logger = logging.getLogger("unified_icon_generator")

# Base paths
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MASTERS = ASSETS / "masters"
OUT = ASSETS / "icons"
CSV_PATH = ROOT / "strategy_icon_variant_matrix.csv"
CONFIG_PATH = ROOT / "config" / "icon_config.json"

# Check for dependencies
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False
    logger.warning("CairoSVG not available. PNG export may use fallback methods.")

try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning("Pillow not available. Some image operations will be limited.")


@dataclass
class IconVariant:
    """Represents a single icon variant"""
    mode: str
    finish: str
    size: int
    context: str
    filename: Optional[str] = None
    formats: List[str] = field(default_factory=lambda: ["svg", "png"])
    optimize: bool = False
    high_dpi: bool = False

    def __post_init__(self):
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


@dataclass
class GenerationMetrics:
    """Stores metrics about the icon generation process"""
    start_time: float = field(default_factory=time.time)
    total_variants: int = 0
    successful_variants: int = 0
    svg_count: int = 0
    png_count: int = 0
    webp_count: int = 0
    other_formats_count: int = 0
    errors: List[str] = field(default_factory=list)
    processing_times: List[float] = field(default_factory=list)

    @property
    def total_time(self) -> float:
        """Get the total elapsed time"""
        return time.time() - self.start_time

    @property
    def average_time(self) -> float:
        """Get the average processing time per variant"""
        if not self.processing_times:
            return 0
        return sum(self.processing_times) / len(self.processing_times)


class ConfigManager:
    """Manages configuration for icon generation"""

    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = config_path
        self.config = self._load_config()
        self._setup_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            logger.warning(
                f"Config file {self.config_path} not found, using default configuration"
            )
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}

    def _setup_config(self):
        """Set up derived values and defaults"""
        # Set up tokens dictionary
        self.tokens = self.config.get("color_tokens", {})

        # Set up finish colors
        self.finish_colors = {}
        for finish, token in self.config.get("finish_colors", {}).items():
            self.finish_colors[finish] = self.tokens.get(
                token, "#FF6A00")  # Default to orange

        # Set up mode backgrounds
        self.mode_colors = {}
        for mode, colors in self.config.get("modes", {}).items():
            bg_token = colors.get("background")
            self.mode_colors[mode] = self.tokens.get(
                bg_token, "#FFFFFF")  # Default to white

    def get_master_path(self, size: int) -> Path:
        """Get the appropriate master SVG path based on size"""
        thresholds = self.config.get("size_thresholds", {"micro": 32, "standard": 256})

        if size <= thresholds.get("micro", 32):
            return MASTERS / "strategy_icon_micro.svg"
        elif size <= thresholds.get("standard", 256):
            return MASTERS / "strategy_icon_standard.svg"
        else:
            return MASTERS / "strategy_icon_standard.svg"  # Fallback to standard

    def get_color_for_mode(self, mode: str) -> str:
        """Get the background color for a mode"""
        return self.mode_colors.get(mode, "#FFFFFF")  # Default to white

    def get_color_for_finish(self, finish: str) -> str:
        """Get the color for a finish"""
        return self.finish_colors.get(finish, "#FF6A00")  # Default to orange

    def get_context_options(self, context: str) -> Dict:
        """Get options for a specific context"""
        contexts = self.config.get("contexts", {})
        return contexts.get(context, {"formats": ["svg", "png"], "optimize": False})

    def get_processing_options(self) -> Dict:
        """Get processing options"""
        return self.config.get("processing_options", {
            "parallel": True,
            "batch_size": 10,
            "optimize_svg": False,
            "optimize_png": False,
            "max_workers": 4
        })

    def get_custom_variants(self) -> List[Dict]:
        """Get custom variant definitions"""
        return self.config.get("custom_variants", [])

    def bake_svg(self, master_svg: str, mode: str, finish: str) -> str:
        """Apply color replacements to the master SVG"""
        bg = self.get_color_for_mode(mode)
        fg = self.get_color_for_finish(finish)

        # Apply color replacements
        svg = master_svg.replace("#FF6A00", bg)  # replace background rect
        svg = svg.replace("#FFFFFF", fg)  # replace icon shapes

        return svg


class IconGenerator:
    """Handles the generation of icons based on variants"""

    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager

    def export_png_with_cairosvg(self, svg_bytes: bytes, out_png: Path, size_px: int) -> bool:
        """Export PNG using CairoSVG"""
        try:
            out_png.parent.mkdir(parents=True, exist_ok=True)
            cairosvg.svg2png(
                bytestring=svg_bytes,
                write_to=str(out_png),
                output_width=size_px,
                output_height=size_px,
            )
            return True
        except Exception as e:
            logger.debug(f"CairoSVG PNG export failed: {e}")
            return False

    def export_png_with_inkscape(self, svg_path: Path, out_png: Path, size_px: int) -> bool:
        """Export PNG using Inkscape CLI"""
        try:
            # Check if inkscape is available
            if shutil.which("inkscape") is None:
                return False

            out_png.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                "inkscape",
                "--export-filename", str(out_png),
                "-w", str(size_px),
                "-h", str(size_px),
                str(svg_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Inkscape PNG export failed: {e}")
            return False

    def export_png_with_imagemagick(self, svg_path: Path, out_png: Path, size_px: int) -> bool:
        """Export PNG using ImageMagick convert"""
        try:
            # Check if convert is available
            if shutil.which("convert") is None:
                return False

            out_png.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                "convert",
                "-background", "none",
                "-size", f"{size_px}x{size_px}",
                str(svg_path),
                "-resize", f"{size_px}x{size_px}",
                str(out_png)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"ImageMagick PNG export failed: {e}")
            return False

    def export_png_with_rsvg(self, svg_path: Path, out_png: Path, size_px: int) -> bool:
        """Export PNG using rsvg-convert"""
        try:
            # Check if rsvg-convert is available
            if shutil.which("rsvg-convert") is None:
                return False

            out_png.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                "rsvg-convert",
                "-w", str(size_px),
                "-h", str(size_px),
                "-o", str(out_png),
                str(svg_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"rsvg-convert PNG export failed: {e}")
            return False

    def export_webp(self, svg_path: Path, out_webp: Path, size_px: int) -> bool:
        """Export WebP format from SVG"""
        if not PILLOW_AVAILABLE:
            return False

        # First try to create a PNG in memory
        try:
            if CAIROSVG_AVAILABLE:
                # Use CairoSVG to convert SVG to PNG in memory
                import io
                png_data = cairosvg.svg2png(
                    url=str(svg_path),
                    output_width=size_px,
                    output_height=size_px
                )

                # Convert PNG to WebP using Pillow
                image = Image.open(io.BytesIO(png_data))
                image.save(str(out_webp), format="WEBP", quality=90)
                return True
            else:
                # Try creating a temporary PNG first
                tmp_png = Path(tempfile.mktemp(suffix=".png"))
                if self.maybe_export_png(svg_path.read_bytes(), tmp_png, size_px):
                    # Convert PNG to WebP
                    image = Image.open(tmp_png)
                    image.save(str(out_webp), format="WEBP", quality=90)
                    tmp_png.unlink(missing_ok=True)
                    return True
                tmp_png.unlink(missing_ok=True)
                return False
        except Exception as e:
            logger.debug(f"WebP export failed: {e}")
            return False

    def maybe_export_png(self, svg_bytes: bytes, out_png: Path, size_px: int) -> bool:
        """Try multiple methods to export SVG to PNG"""
        # First, ensure the output directory exists
        out_png.parent.mkdir(parents=True, exist_ok=True)

        # If CairoSVG is available, try it first (fastest method)
        if CAIROSVG_AVAILABLE:
            if self.export_png_with_cairosvg(svg_bytes, out_png, size_px):
                return True

        # If that fails, write the SVG to a temporary file and try other methods
        with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(svg_bytes)

        try:
            # Try conversion methods in order of preference
            conversion_methods = [
                (self.export_png_with_inkscape, "Inkscape"),
                (self.export_png_with_rsvg, "rsvg-convert"),
                (self.export_png_with_imagemagick, "ImageMagick")
            ]

            for method, name in conversion_methods:
                if method(tmp_path, out_png, size_px):
                    logger.debug(f"Successfully exported PNG using {name}")
                    return True

            # If all methods failed, log the error
            logger.error(f"All PNG export methods failed for {out_png}")
            return False
        finally:
            # Clean up the temporary file
            tmp_path.unlink(missing_ok=True)

    def optimize_svg(self, svg_path: Path) -> bool:
        """Optimize SVG file size"""
        try:
            # Try with svgo if available
            if shutil.which("svgo"):
                result = subprocess.run(
                    ["svgo", str(svg_path), "--multipass"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0

            # Fallback to basic optimization by re-parsing and serializing
            if CAIROSVG_AVAILABLE:
                from cairosvg.parser import Tree
                from cairosvg.surface import SVGSurface

                svg_content = svg_path.read_text(encoding="utf-8")
                tree = Tree(bytestring=svg_content.encode("utf-8"))
                surface = SVGSurface(tree, None)
                optimized_svg = surface.tostring(encoding="utf-8").decode("utf-8")

                svg_path.write_text(optimized_svg, encoding="utf-8")
                return True

            return False
        except Exception as e:
            logger.debug(f"SVG optimization failed: {e}")
            return False

    def optimize_png(self, png_path: Path) -> bool:
        """Optimize PNG file size"""
        try:
            # Try with pngquant if available
            if shutil.which("pngquant"):
                result = subprocess.run(
                    ["pngquant", "--force", "--ext", ".png",
                        "--quality=80-95", str(png_path)],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0

            # Fallback to PIL
            if PILLOW_AVAILABLE:
                image = Image.open(png_path)
                image.save(png_path, optimize=True, quality=95)
                return True

            return False
        except Exception as e:
            logger.debug(f"PNG optimization failed: {e}")
            return False

    def process_variant(self, variant: IconVariant, metrics: GenerationMetrics) -> Dict[str, Any]:
        """Process a single icon variant"""
        start_time = time.time()
        results = {"successful": False, "formats": []}

        try:
            # Create output directory
            variant.output_folder.mkdir(parents=True, exist_ok=True)

            # Select master SVG
            master_path = self.config.get_master_path(variant.size)
            if not master_path.exists():
                logger.error(f"Master SVG not found: {master_path}")
                metrics.errors.append(f"Missing master: {master_path}")
                return results

            # Read master SVG
            master_svg = master_path.read_text(encoding="utf-8")

            # Apply color replacements
            baked_svg = self.config.bake_svg(master_svg, variant.mode, variant.finish)

            # Create output paths
            svg_path = variant.output_folder / f"{variant.base_filename}.svg"
            png_path = variant.output_folder / variant.filename
            webp_path = variant.output_folder / f"{variant.base_filename}.webp"

            # Write SVG file if requested
            if "svg" in variant.formats:
                svg_path.write_text(baked_svg, encoding="utf-8")
                results["formats"].append("svg")

                # Optimize SVG if requested
                if variant.optimize:
                    self.optimize_svg(svg_path)

            # Generate PNG if requested
            if "png" in variant.formats:
                png_success = self.maybe_export_png(
                    baked_svg.encode("utf-8"), png_path, variant.size
                )

                if png_success:
                    results["formats"].append("png")

                    # Optimize PNG if requested
                    if variant.optimize:
                        self.optimize_png(png_path)

            # Generate WebP if requested
            if "webp" in variant.formats:
                if self.export_webp(svg_path, webp_path, variant.size):
                    results["formats"].append("webp")

            # Record processing time
            processing_time = time.time() - start_time
            metrics.processing_times.append(processing_time)

            results["successful"] = True
            return results
        except Exception as e:
            logger.error(
                f"Error processing variant {variant.mode}/{variant.finish}/{variant.size}: {e}")
            metrics.errors.append(f"Error: {str(e)}")
            return results

    def process_batch(self, variants: List[IconVariant], parallel: bool = True) -> GenerationMetrics:
        """Process a batch of icon variants"""
        metrics = GenerationMetrics()
        total = len(variants)

        logger.info(f"Processing {total} icon variants...")

        # Get processing options
        proc_options = self.config.get_processing_options()
        max_workers = proc_options.get("max_workers", 4)

        if parallel and total > 1:
            # Use process pool for CPU-bound tasks
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_variant = {
                    executor.submit(self.process_variant, variant, metrics): variant
                    for variant in variants
                }

                # Process results as they complete
                for i, future in enumerate(concurrent.futures.as_completed(future_to_variant), 1):
                    variant = future_to_variant[future]
                    result = future.result()

                    metrics.total_variants += 1
                    if result["successful"]:
                        metrics.successful_variants += 1

                        if "svg" in result["formats"]:
                            metrics.svg_count += 1
                        if "png" in result["formats"]:
                            metrics.png_count += 1
                        if "webp" in result["formats"]:
                            metrics.webp_count += 1

                    # Progress reporting
                    if i % max(1, total // 10) == 0 or i == total:
                        logger.info(f"Progress: {i}/{total} variants processed")
        else:
            # Process sequentially
            for i, variant in enumerate(variants, 1):
                result = self.process_variant(variant, metrics)

                metrics.total_variants += 1
                if result["successful"]:
                    metrics.successful_variants += 1

                    if "svg" in result["formats"]:
                        metrics.svg_count += 1
                    if "png" in result["formats"]:
                        metrics.png_count += 1
                    if "webp" in result["formats"]:
                        metrics.webp_count += 1

                # Progress reporting
                if i % max(1, total // 10) == 0 or i == total:
                    logger.info(f"Progress: {i}/{total} variants processed")

        return metrics


def load_csv_variants(csv_path: Path, config_manager: ConfigManager) -> List[IconVariant]:
    """Load variants from the CSV file"""
    if not csv_path.exists():
        logger.error(f"CSV matrix file not found: {csv_path}")
        sys.exit(1)

    variants = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))

        for row in rows:
            context = row["Context"]
            context_options = config_manager.get_context_options(context)

            variant = IconVariant(
                mode=row["Mode"],
                finish=row["Finish"],
                size=int(row["Size (px)"]),
                context=context,
                filename=row.get("Filename"),
                formats=context_options.get("formats", ["svg", "png"]),
                optimize=context_options.get("optimize", False),
                high_dpi=context_options.get("high_dpi", False)
            )
            variants.append(variant)

        return variants
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        sys.exit(1)


def load_json_variants(config_manager: ConfigManager) -> List[IconVariant]:
    """Load variants from the JSON configuration"""
    variants = []

    # Get custom variants from config
    custom_defs = config_manager.get_custom_variants()

    for variant_def in custom_defs:
        context = variant_def["context"]
        context_options = config_manager.get_context_options(context)

        variant = IconVariant(
            mode=variant_def["mode"],
            finish=variant_def["finish"],
            size=int(variant_def["size"]),
            context=context,
            filename=variant_def.get("filename"),
            formats=variant_def.get(
                "formats", context_options.get("formats", ["svg", "png"])),
            optimize=variant_def.get(
                "optimize", context_options.get("optimize", False)),
            high_dpi=variant_def.get("high_dpi", context_options.get("high_dpi", False))
        )
        variants.append(variant)

    return variants


def print_report(metrics: GenerationMetrics):
    """Print a performance report"""
    print("\n" + "=" * 60)
    print(" StrategyDECK Icon Generation Report ".center(60, "="))
    print("=" * 60)

    print(f"Total variants processed: {metrics.total_variants}")
    print(f"Successful variants: {metrics.successful_variants}")
    print(f"SVG files generated: {metrics.svg_count}")
    print(f"PNG files generated: {metrics.png_count}")
    print(f"WebP files generated: {metrics.webp_count}")
    print(f"Total time: {metrics.total_time:.2f} seconds")
    print(f"Average time per variant: {metrics.average_time:.4f} seconds")

    if metrics.errors:
        print(f"\nErrors encountered: {len(metrics.errors)}")
        for i, error in enumerate(metrics.errors[:5], 1):
            print(f"  {i}. {error}")

        if len(metrics.errors) > 5:
            print(f"  ... and {len(metrics.errors) - 5} more errors")

    print("\n" + "=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Unified Icon Generator for StrategyDECK"
    )
    parser.add_argument(
        "--source", choices=["csv", "json", "both"], default="both",
        help="Source for variant definitions"
    )
    parser.add_argument(
        "--csv", type=str,
        help="Custom CSV matrix file"
    )
    parser.add_argument(
        "--config", type=str,
        help="Custom JSON config file"
    )
    parser.add_argument(
        "--output", type=str,
        help="Custom output directory"
    )
    parser.add_argument(
        "--parallel", action="store_true", default=True,
        help="Process variants in parallel (default: True)"
    )
    parser.add_argument(
        "--sequential", action="store_true",
        help="Process variants sequentially"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logger.setLevel(logging.DEBUG)

    # Set custom output directory if specified
    if args.output:
        global OUT
        OUT = Path(args.output)

    # Set custom CSV file if specified
    csv_path = CSV_PATH
    if args.csv:
        csv_path = Path(args.csv)

    # Set custom config file if specified
    config_path = CONFIG_PATH
    if args.config:
        config_path = Path(args.config)

    # Create config manager
    config_manager = ConfigManager(config_path)

    # Create icon generator
    generator = IconGenerator(config_manager)

    # Load variants based on source
    variants = []

    if args.source in ["csv", "both"]:
        csv_variants = load_csv_variants(csv_path, config_manager)
        logger.info(f"Loaded {len(csv_variants)} variants from CSV")
        variants.extend(csv_variants)

    if args.source in ["json", "both"]:
        json_variants = load_json_variants(config_manager)
        logger.info(f"Loaded {len(json_variants)} variants from JSON config")
        variants.extend(json_variants)

    if not variants:
        logger.error("No variants loaded. Please check your configuration.")
        return 1

    # Determine parallel processing mode
    parallel = args.parallel and not args.sequential

    # Process the variants
    metrics = generator.process_batch(variants, parallel=parallel)

    # Print report
    print_report(metrics)

    # Return success status code
    if metrics.successful_variants == metrics.total_variants:
        logger.info("All variants generated successfully.")
        return 0
    else:
        logger.warning(
            f"{metrics.total_variants - metrics.successful_variants} variants failed to generate.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
