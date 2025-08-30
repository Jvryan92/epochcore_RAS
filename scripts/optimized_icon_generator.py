#!/usr/bin/env python3
"""
Optimized Icon Generator for StrategyDECK

This script optimizes the StrategyDECK icon generation system with:
- Parallel processing for faster generation
- Improved PNG conversion with multiple fallback methods
- Better error handling and reporting
- Performance metrics and benchmarking
- Memory usage optimization for large batch operations
"""

import argparse
import concurrent.futures
import csv
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("icon_generator.log"),
    ],
)
logger = logging.getLogger("icon_generator")

# Add the scripts directory to the path
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MASTERS = ASSETS / "masters"
OUT = ASSETS / "icons"
CSV_PATH = ROOT / "strategy_icon_variant_matrix.csv"

# Core color token definitions (preserved from original)
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

# Finish colors (preserved from original)
FINISH_COLORS = {
    "flat-orange": TOKENS["brand_orange"],
    "matte-carbon": TOKENS["matte"],
    "satin-black": TOKENS["ink"],
    "burnt-orange": TOKENS["burnt_orange"],
    "copper-foil": TOKENS["copper"],
    "embossed-paper": TOKENS["embossed"],
}

# Check for Cairo/CairoSVG availability upfront
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False
    logger.warning("CairoSVG not available. PNG export may use fallback methods.")

# Try to import Pillow for image manipulation
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    logger.warning("Pillow not available. Some image operations will be limited.")


@dataclass
class GenerationMetrics:
    """Stores metrics about the icon generation process"""
    start_time: float = field(default_factory=time.time)
    svg_count: int = 0
    png_count: int = 0
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


def pick_master(size_px: int) -> Path:
    """Select the appropriate master SVG based on size"""
    return MASTERS / (
        "strategy_icon_micro.svg" if size_px <= 32 else "strategy_icon_standard.svg"
    )


def bake_svg(master_svg: str, mode: str, finish: str) -> str:
    """Apply color replacements to the master SVG"""
    bg = TOKENS["paper"] if mode == "light" else TOKENS["slate_950"]
    fg = FINISH_COLORS.get(finish, TOKENS["brand_orange"])

    # Apply color replacements
    svg = master_svg.replace("#FF6A00", bg)  # replace background rect
    svg = svg.replace("#FFFFFF", fg)  # replace icon shapes

    return svg


def export_png_with_cairosvg(svg_bytes: bytes, out_png: Path, size_px: int) -> bool:
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


def export_png_with_inkscape(svg_path: Path, out_png: Path, size_px: int) -> bool:
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


def export_png_with_imagemagick(svg_path: Path, out_png: Path, size_px: int) -> bool:
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


def export_png_with_rsvg(svg_path: Path, out_png: Path, size_px: int) -> bool:
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


def maybe_export_png(svg_bytes: bytes, out_png: Path, size_px: int) -> bool:
    """Try multiple methods to export SVG to PNG"""
    # First, ensure the output directory exists
    out_png.parent.mkdir(parents=True, exist_ok=True)

    # If CairoSVG is available, try it first (fastest method)
    if CAIROSVG_AVAILABLE:
        if export_png_with_cairosvg(svg_bytes, out_png, size_px):
            return True

    # If that fails, write the SVG to a temporary file and try other methods
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as tmp:
        tmp_path = Path(tmp.name)
        tmp.write(svg_bytes)

    try:
        # Try conversion methods in order of preference
        conversion_methods = [
            (export_png_with_inkscape, "Inkscape"),
            (export_png_with_rsvg, "rsvg-convert"),
            (export_png_with_imagemagick, "ImageMagick")
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


def process_variant(row: dict, metrics: GenerationMetrics) -> Tuple[bool, bool]:
    """Process a single icon variant"""
    start_time = time.time()

    try:
        mode = row["Mode"]
        finish = row["Finish"]
        size = int(row["Size (px)"])
        context = row["Context"]
        filename = row.get("Filename") or f"strategy_icon-{mode}-{finish}-{size}px.png"

        master_path = pick_master(size)
        if not master_path.exists():
            logger.error(f"Master SVG not found: {master_path}")
            metrics.errors.append(f"Missing master: {master_path}")
            return False, False

        master_svg = master_path.read_text(encoding="utf-8")
        baked_svg = bake_svg(master_svg, mode, finish)

        folder = OUT / mode / finish / f"{size}px" / context
        folder.mkdir(parents=True, exist_ok=True)

        svg_path = folder / (Path(filename).stem + ".svg")
        svg_path.write_text(baked_svg, encoding="utf-8")

        svg_success = True
        png_success = maybe_export_png(
            baked_svg.encode("utf-8"), folder / Path(filename).name, size
        )

        # Record processing time
        processing_time = time.time() - start_time
        metrics.processing_times.append(processing_time)

        return svg_success, png_success
    except Exception as e:
        logger.error(f"Error processing variant {row}: {e}")
        metrics.errors.append(f"Error: {str(e)}")
        return False, False


def process_batch(rows: List[dict], parallel: bool = True) -> GenerationMetrics:
    """Process a batch of icon variants"""
    metrics = GenerationMetrics()
    total = len(rows)

    logger.info(f"Processing {total} icon variants...")

    if parallel and total > 1:
        # Use process pool for CPU-bound tasks
        with concurrent.futures.ProcessPoolExecutor() as executor:
            futures = []
            batch_size = min(os.cpu_count() * 2, total)

            for i in range(0, total, batch_size):
                batch = rows[i:i+batch_size]
                for row in batch:
                    futures.append(executor.submit(process_variant, row, metrics))

            # Process results as they complete
            for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
                svg_success, png_success = future.result()

                if svg_success:
                    metrics.svg_count += 1
                if png_success:
                    metrics.png_count += 1

                # Progress reporting
                if i % max(1, total // 10) == 0 or i == total:
                    logger.info(f"Progress: {i}/{total} variants processed")
    else:
        # Process sequentially
        for i, row in enumerate(rows, 1):
            svg_success, png_success = process_variant(row, metrics)

            if svg_success:
                metrics.svg_count += 1
            if png_success:
                metrics.png_count += 1

            # Progress reporting
            if i % max(1, total // 10) == 0 or i == total:
                logger.info(f"Progress: {i}/{total} variants processed")

    return metrics


def load_csv_variants() -> List[dict]:
    """Load variants from the CSV file"""
    if not CSV_PATH.exists():
        logger.error(f"CSV matrix file not found: {CSV_PATH}")
        sys.exit(1)

    try:
        with open(CSV_PATH, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
        sys.exit(1)


def print_report(metrics: GenerationMetrics):
    """Print a performance report"""
    print("\n" + "=" * 60)
    print(" StrategyDECK Icon Generation Report ".center(60, "="))
    print("=" * 60)

    print(f"Total variants processed: {len(metrics.processing_times)}")
    print(f"SVG files generated: {metrics.svg_count}")
    print(f"PNG files generated: {metrics.png_count}")
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
        description="Optimized Icon Generator for StrategyDECK"
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
        "--output", type=str,
        help="Custom output directory"
    )
    parser.add_argument(
        "--csv", type=str,
        help="Custom CSV matrix file"
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
    if args.csv:
        global CSV_PATH
        CSV_PATH = Path(args.csv)

    # Determine parallel processing mode
    parallel = args.parallel and not args.sequential

    # Load variants from CSV
    variants = load_csv_variants()

    # Process the variants
    metrics = process_batch(variants, parallel=parallel)

    # Print report
    print_report(metrics)

    # Return success status code
    if metrics.svg_count == len(variants) and metrics.png_count == len(variants):
        logger.info("All variants generated successfully.")
        return 0
    else:
        logger.warning("Some variants failed to generate.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
