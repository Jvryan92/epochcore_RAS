#!/usr/bin/env python3
"""
StrategyDECK Icon Generator Benchmark Tool

This script benchmarks and compares the performance of different icon generation
implementations to identify the most efficient approach.
"""

import argparse
import csv
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Configuration
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
MASTERS = ASSETS / "masters"
ORIGINAL_SCRIPT = ROOT / "scripts" / "generate_icons.py"
OPTIMIZED_SCRIPT = ROOT / "scripts" / "unified_icon_generator.py"
ENHANCED_SCRIPT = ROOT / "scripts" / "enhanced_icon_generator.py"
CSV_PATH = ROOT / "strategy_icon_variant_matrix.csv"

# Test configurations
TEST_CONFIGS = {
    "small": 5,     # First 5 variants
    "medium": 10,   # First 10 variants
    "large": -1,    # All variants
}


def count_generated_files():
    """Count the number of generated SVG and PNG files"""
    svg_count = sum(1 for _ in ASSETS.glob("icons/**/*.svg"))
    png_count = sum(1 for _ in ASSETS.glob("icons/**/*.png"))
    return svg_count, png_count


def clean_output_directory():
    """Clean the output directory"""
    icons_dir = ASSETS / "icons"
    if icons_dir.exists():
        shutil.rmtree(icons_dir)
        icons_dir.mkdir(parents=True, exist_ok=True)


def count_variants():
    """Count the number of variants in the CSV file"""
    if not CSV_PATH.exists():
        print(f"Error: CSV file {CSV_PATH} not found")
        sys.exit(1)

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        return len(list(csv.DictReader(f)))


def run_benchmark(script_path, test_size):
    """Run a benchmark for a specific script and test size"""
    # Clean output directory
    clean_output_directory()

    # Prepare variant count
    total_variants = count_variants()
    if test_size > 0:
        print(f"Running benchmark with {test_size}/{total_variants} variants...")
        # Create temporary CSV with limited variants
        temp_csv = ROOT / "temp_benchmark.csv"
        with open(CSV_PATH, "r", encoding="utf-8") as src, open(temp_csv, "w", encoding="utf-8") as dest:
            reader = csv.reader(src)
            writer = csv.writer(dest)

            # Write header
            header = next(reader)
            writer.writerow(header)

            # Write limited rows
            for i, row in enumerate(reader):
                if i < test_size:
                    writer.writerow(row)
                else:
                    break

        csv_arg = f"--csv={temp_csv}"
    else:
        print(f"Running benchmark with all {total_variants} variants...")
        csv_arg = ""

    # Run the script and time it
    start_time = time.time()

    if "unified_icon_generator" in script_path.name or "enhanced_icon_generator" in script_path.name:
        cmd = [sys.executable, str(script_path), csv_arg]
    else:
        cmd = [sys.executable, str(script_path)]

    if csv_arg:
        cmd = [part for part in cmd if part]  # Remove empty parts

    print(f"Running command: {' '.join(str(c) for c in cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    end_time = time.time()
    elapsed = end_time - start_time

    # Count generated files
    svg_count, png_count = count_generated_files()

    # Cleanup temp file if created
    if test_size > 0:
        temp_csv.unlink(missing_ok=True)

    return {
        "script": script_path.name,
        "time": elapsed,
        "exit_code": result.returncode,
        "svg_count": svg_count,
        "png_count": png_count,
        "output": result.stdout,
        "error": result.stderr
    }


def print_benchmark_results(results):
    """Print benchmark results in a table format"""
    print("\n" + "=" * 80)
    print(" StrategyDECK Icon Generator Benchmark Results ".center(80, "="))
    print("=" * 80)

    print(f"{'Script':<25} {'Test Size':<10} {'Time (s)':<10} {'SVG Count':<10} {'PNG Count':<10} {'Status':<10}")
    print("-" * 80)

    for test_name, test_results in results.items():
        for result in test_results:
            script = result["script"]
            time_taken = f"{result['time']:.2f}"
            svg_count = result["svg_count"]
            png_count = result["png_count"]
            status = "Success" if result["exit_code"] == 0 else "Failed"

            print(
                f"{script:<25} {test_name:<10} {time_taken:<10} {svg_count:<10} {png_count:<10} {status:<10}")

    print("=" * 80)

    # Print detailed comparisons
    print("\nPerformance Comparison:")
    for test_name, test_results in results.items():
        if len(test_results) < 2:
            continue

        original = next(
            (r for r in test_results if "generate_icons.py" in r["script"]), None)
        optimized = next(
            (r for r in test_results if "unified_icon_generator.py" in r["script"]), None)
        enhanced = next(
            (r for r in test_results if "enhanced_icon_generator.py" in r["script"]), None)

        # Compare original vs optimized
        if original and optimized:
            speedup = original["time"] / optimized["time"] if optimized["time"] > 0 else float('inf')
            print(f"  {test_name}: Unified version is {speedup:.2f}x faster than original")

            # Compare file generation
            if original["svg_count"] == optimized["svg_count"]:
                print(f"  {test_name}: Both versions generated {original['svg_count']} SVG files")
            else:
                print(
                    f"  {test_name}: SVG diff: Original={original['svg_count']}, Unified={optimized['svg_count']}")

            if original["png_count"] == optimized["png_count"]:
                print(f"  {test_name}: Both versions generated {original['png_count']} PNG files")
            else:
                print(
                    f"  {test_name}: PNG diff: Original={original['png_count']}, Unified={optimized['png_count']}")

        # Compare original vs enhanced
        if original and enhanced:
            speedup = original["time"] / enhanced["time"] if enhanced["time"] > 0 else float('inf')
            print(f"  {test_name}: Enhanced version is {speedup:.2f}x faster than original")

            # Compare file generation
            if original["svg_count"] == enhanced["svg_count"]:
                print(f"  {test_name}: Both versions generated {original['svg_count']} SVG files")
            else:
                print(
                    f"  {test_name}: SVG diff: Original={original['svg_count']}, Enhanced={enhanced['svg_count']}")

            if original["png_count"] == enhanced["png_count"]:
                print(f"  {test_name}: Both versions generated {original['png_count']} PNG files")
            else:
                print(
                    f"  {test_name}: PNG diff: Original={original['png_count']}, Enhanced={enhanced['png_count']}")

        # Compare optimized vs enhanced
        if optimized and enhanced:
            speedup = optimized["time"] / enhanced["time"] if enhanced["time"] > 0 else float('inf')
            print(f"  {test_name}: Enhanced version is {speedup:.2f}x faster than unified")

            # Compare file generation
            if optimized["svg_count"] == enhanced["svg_count"]:
                print(f"  {test_name}: Both versions generated {optimized['svg_count']} SVG files")
            else:
                print(
                    f"  {test_name}: SVG diff: Unified={optimized['svg_count']}, Enhanced={enhanced['svg_count']}")

            if optimized["png_count"] == enhanced["png_count"]:
                print(f"  {test_name}: Both versions generated {optimized['png_count']} PNG files")
            else:
                print(
                    f"  {test_name}: PNG diff: Unified={optimized['png_count']}, Enhanced={enhanced['png_count']}")

        print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Benchmark StrategyDECK icon generation implementations"
    )
    parser.add_argument(
        "--test-size", choices=["small", "medium", "large"], default="small",
        help="Size of the benchmark test to run"
    )
    parser.add_argument(
        "--skip-original", action="store_true",
        help="Skip benchmarking the original implementation"
    )
    parser.add_argument(
        "--skip-optimized", action="store_true",
        help="Skip benchmarking the optimized implementation"
    )
    parser.add_argument(
        "--skip-enhanced", action="store_true",
        help="Skip benchmarking the enhanced implementation"
    )

    args = parser.parse_args()

    # Check if scripts exist
    if not ORIGINAL_SCRIPT.exists() and not args.skip_original:
        print(f"Error: Original script {ORIGINAL_SCRIPT} not found")
        sys.exit(1)

    if not OPTIMIZED_SCRIPT.exists() and not args.skip_optimized:
        print(f"Error: Optimized script {OPTIMIZED_SCRIPT} not found")
        sys.exit(1)
        
    if not ENHANCED_SCRIPT.exists() and not args.skip_enhanced:
        print(f"Error: Enhanced script {ENHANCED_SCRIPT} not found")
        sys.exit(1)

    # Determine test size
    test_size = TEST_CONFIGS[args.test_size]

    # Run benchmarks
    results = {args.test_size: []}

    if not args.skip_original:
        print(f"\nBenchmarking original implementation ({ORIGINAL_SCRIPT.name})...")
        result = run_benchmark(ORIGINAL_SCRIPT, test_size)
        results[args.test_size].append(result)

        print(f"Original implementation took {result['time']:.2f} seconds")
        print(
            f"Generated {result['svg_count']} SVG files and {result['png_count']} PNG files")

    if not args.skip_optimized:
        print(f"\nBenchmarking optimized implementation ({OPTIMIZED_SCRIPT.name})...")
        result = run_benchmark(OPTIMIZED_SCRIPT, test_size)
        results[args.test_size].append(result)

        print(f"Optimized implementation took {result['time']:.2f} seconds")
        print(
            f"Generated {result['svg_count']} SVG files and {result['png_count']} PNG files")
            
    if not args.skip_enhanced:
        print(f"\nBenchmarking enhanced implementation ({ENHANCED_SCRIPT.name})...")
        result = run_benchmark(ENHANCED_SCRIPT, test_size)
        results[args.test_size].append(result)

        print(f"Enhanced implementation took {result['time']:.2f} seconds")
        print(
            f"Generated {result['svg_count']} SVG files and {result['png_count']} PNG files")

    # Print results
    print_benchmark_results(results)


if __name__ == "__main__":
    main()
