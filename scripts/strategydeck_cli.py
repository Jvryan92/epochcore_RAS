#!/usr/bin/env python3
"""
StrategyDECK Icon CLI

A unified command-line interface for the StrategyDECK icon generation system.
This tool brings together all the icon generation, customization, and export capabilities
into a single convenient CLI.

Usage:
  python strategydeck_cli.py generate --all
  python strategydeck_cli.py customize --palette neon
  python strategydeck_cli.py export --framework react --output ./react-icons
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# Try to import our modules
try:
    from generate_icons import main as generate_icons_main
except ImportError:
    generate_icons_main = None

try:
    from enhanced_icon_generator import main as enhanced_generator_main
except ImportError:
    enhanced_generator_main = None

try:
    from palette_manager import main as palette_manager_main
except ImportError:
    palette_manager_main = None

try:
    from icon_framework_exporter import main as framework_exporter_main
except ImportError:
    framework_exporter_main = None


class StrategyCLI:
    """Main CLI class for StrategyDECK tools"""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser"""
        parser = argparse.ArgumentParser(
            description="StrategyDECK Icon CLI - A unified tool for icon generation"
        )

        subparsers = parser.add_subparsers(dest="command", help="Command to run")

        # Generate command
        generate_parser = subparsers.add_parser("generate", help="Generate icons")
        generate_parser.add_argument(
            "--all", action="store_true", help="Generate all icons")
        generate_parser.add_argument(
            "--enhanced", action="store_true", help="Use enhanced generator")
        generate_parser.add_argument(
            "--modes", nargs="+", help="Modes to generate (light, dark)")
        generate_parser.add_argument(
            "--finishes", nargs="+", help="Finishes to generate")
        generate_parser.add_argument(
            "--sizes", nargs="+", type=int, help="Sizes to generate")
        generate_parser.add_argument(
            "--contexts", nargs="+", help="Contexts to generate")
        generate_parser.add_argument(
            "--optimize", action="store_true", help="Optimize output")
        generate_parser.add_argument(
            "--parallel", action="store_true", help="Process in parallel")

        # Customize command
        customize_parser = subparsers.add_parser(
            "customize", help="Customize icons and palettes")
        customize_subparsers = customize_parser.add_subparsers(
            dest="customize_command", help="Customization command")

        # Palette commands
        palette_parser = customize_subparsers.add_parser(
            "palette", help="Manage color palettes")
        palette_parser.add_argument(
            "--list", action="store_true", help="List all palettes")
        palette_parser.add_argument(
            "--create", metavar="NAME", help="Create a new palette")
        palette_parser.add_argument("--edit", metavar="NAME", help="Edit a palette")
        palette_parser.add_argument(
            "--preview", metavar="NAME", help="Preview a palette")
        palette_parser.add_argument("--export", metavar="NAME", help="Export a palette")
        palette_parser.add_argument("--format", choices=["css", "scss", "json", "python"],
                                    default="css", help="Export format")
        palette_parser.add_argument("--base-color", help="Base color for new palette")

        # Icon variant commands
        variant_parser = customize_subparsers.add_parser(
            "variant", help="Create custom icon variants")
        variant_parser.add_argument("--create", metavar="SPEC",
                                    help="Create variant (mode,finish,size,context)")
        variant_parser.add_argument("--palette", help="Use custom palette")

        # Debug commands
        debug_parser = customize_subparsers.add_parser("debug", help="Debug tools")
        debug_parser.add_argument("--bake", metavar="SVG",
                                  help="Debug SVG baking process")
        debug_parser.add_argument("--mode", choices=["light", "dark"], default="light")
        debug_parser.add_argument("--finish", default="flat-orange")
        debug_parser.add_argument("--gui", action="store_true",
                                  help="Launch GUI debugger")

        # Export command
        export_parser = subparsers.add_parser(
            "export", help="Export icons to frameworks")
        export_parser.add_argument("--framework", choices=[
            "react", "vue", "angular", "svelte", "vanilla-js", "web-components"
        ], required=True, help="Target framework")
        export_parser.add_argument("--output", required=True, help="Output directory")
        export_parser.add_argument(
            "--optimize", action="store_true", help="Optimize SVGs")
        export_parser.add_argument(
            "--sizes", type=int, nargs="+", help="Include only these sizes")
        export_parser.add_argument(
            "--modes", nargs="+", help="Include only these modes")
        export_parser.add_argument("--contexts", nargs="+",
                                   help="Include only these contexts")

        # Info command
        info_parser = subparsers.add_parser("info", help="Show system information")
        info_parser.add_argument("--dependencies", action="store_true",
                                 help="Check dependencies")
        info_parser.add_argument("--stats", action="store_true",
                                 help="Show icon statistics")

        return parser

    def run(self, args=None) -> int:
        """Run the CLI with the given arguments"""
        args = self.parser.parse_args(args)

        if not args.command:
            self.parser.print_help()
            return 1

        # Dispatch to appropriate command
        if args.command == "generate":
            return self._run_generate(args)
        elif args.command == "customize":
            return self._run_customize(args)
        elif args.command == "export":
            return self._run_export(args)
        elif args.command == "info":
            return self._run_info(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1

    def _run_generate(self, args) -> int:
        """Run icon generation"""
        if args.enhanced and enhanced_generator_main:
            # Use enhanced generator
            cli_args = []

            if args.all:
                cli_args.append("--csv")
            else:
                cli_args.append("--batch")

                if args.modes:
                    cli_args.append("--modes")
                    cli_args.extend(args.modes)

                if args.finishes:
                    cli_args.append("--finishes")
                    cli_args.extend(args.finishes)

                if args.sizes:
                    cli_args.append("--sizes")
                    cli_args.extend([str(s) for s in args.sizes])

                if args.contexts:
                    cli_args.append("--contexts")
                    cli_args.extend(args.contexts)

            if args.optimize:
                cli_args.append("--optimize")

            if args.parallel:
                cli_args.append("--parallel")

            # Convert to string list for subprocess
            cli_args = [str(arg) for arg in cli_args]

            # Use module directly
            try:
                sys.argv = [sys.argv[0]] + cli_args
                return enhanced_generator_main() or 0
            except Exception as e:
                print(f"Error running enhanced generator: {e}")
                return 1

        elif generate_icons_main:
            # Use standard generator
            try:
                return generate_icons_main() or 0
            except Exception as e:
                print(f"Error running icon generator: {e}")
                return 1
        else:
            # Fall back to subprocess
            try:
                script_path = SCRIPT_DIR / "generate_icons.py"
                result = subprocess.run([sys.executable, str(script_path)])
                return result.returncode
            except Exception as e:
                print(f"Error running icon generator: {e}")
                return 1

    def _run_customize(self, args) -> int:
        """Run customization tools"""
        if not args.customize_command:
            print("Please specify a customization command. Use --help for more information.")
            return 1

        if args.customize_command == "palette" and palette_manager_main:
            # Build argument list
            cli_args = []

            if args.list:
                cli_args.append("--list")
            elif args.create:
                cli_args.append("--create")
                cli_args.append(args.create)

                if args.base_color:
                    cli_args.append("--base-color")
                    cli_args.append(args.base_color)
            elif args.edit:
                cli_args.append("--edit")
                cli_args.append(args.edit)
            elif args.preview:
                cli_args.append("--preview")
                cli_args.append(args.preview)
            elif args.export:
                cli_args.append("--export")
                cli_args.append(args.export)
                cli_args.append("--format")
                cli_args.append(args.format)

            # Use module directly
            try:
                sys.argv = [sys.argv[0]] + cli_args
                return palette_manager_main() or 0
            except Exception as e:
                print(f"Error running palette manager: {e}")
                return 1

        elif args.customize_command == "variant" and enhanced_generator_main:
            # Build argument list for enhanced generator
            cli_args = []

            if args.create:
                cli_args.append("--create-variant")
                cli_args.append(args.create)

            if args.palette:
                cli_args.append("--palette")
                cli_args.append(args.palette)

            # Use module directly
            try:
                sys.argv = [sys.argv[0]] + cli_args
                return enhanced_generator_main() or 0
            except Exception as e:
                print(f"Error creating variant: {e}")
                return 1

        elif args.customize_command == "debug":
            # Debug tools
            try:
                script_path = ROOT / "debug_bake_svg.py"

                cmd = [sys.executable, str(script_path)]

                if args.bake:
                    cmd.append("--svg")
                    cmd.append(args.bake)
                    cmd.append("--mode")
                    cmd.append(args.mode)
                    cmd.append("--finish")
                    cmd.append(args.finish)

                if args.gui:
                    cmd.append("--gui")

                result = subprocess.run(cmd)
                return result.returncode
            except Exception as e:
                print(f"Error running debug tool: {e}")
                return 1

        else:
            print(f"Unknown customize command: {args.customize_command}")
            return 1

    def _run_export(self, args) -> int:
        """Run export tools"""
        if framework_exporter_main:
            # Build argument list
            cli_args = [
                "--framework", args.framework,
                "--output", args.output
            ]

            if args.optimize:
                cli_args.append("--optimize")

            if args.sizes:
                cli_args.append("--sizes")
                cli_args.extend([str(s) for s in args.sizes])

            if args.modes:
                cli_args.append("--modes")
                cli_args.extend(args.modes)

            if args.contexts:
                cli_args.append("--contexts")
                cli_args.extend(args.contexts)

            # Use module directly
            try:
                sys.argv = [sys.argv[0]] + cli_args
                return framework_exporter_main() or 0
            except Exception as e:
                print(f"Error running framework exporter: {e}")
                return 1
        else:
            # Fall back to subprocess
            try:
                script_path = SCRIPT_DIR / "icon_framework_exporter.py"

                cmd = [
                    sys.executable,
                    str(script_path),
                    "--framework", args.framework,
                    "--output", args.output
                ]

                if args.optimize:
                    cmd.append("--optimize")

                if args.sizes:
                    cmd.append("--sizes")
                    cmd.extend([str(s) for s in args.sizes])

                if args.modes:
                    cmd.append("--modes")
                    cmd.extend(args.modes)

                if args.contexts:
                    cmd.append("--contexts")
                    cmd.extend(args.contexts)

                result = subprocess.run(cmd)
                return result.returncode
            except Exception as e:
                print(f"Error running framework exporter: {e}")
                return 1

    def _run_info(self, args) -> int:
        """Run info commands"""
        if args.dependencies:
            return self._check_dependencies()
        elif args.stats:
            return self._show_stats()
        else:
            return self._show_system_info()

    def _check_dependencies(self) -> int:
        """Check dependencies and their versions"""
        dependencies = {
            "cairosvg": "SVG to PNG conversion",
            "pillow": "Image processing",
            "svglib": "SVG parsing",
            "reportlab": "PDF generation",
            "pytest": "Testing",
            "flake8": "Linting",
            "black": "Formatting"
        }

        print("StrategyDECK Icon System Dependencies")
        print("=" * 40)

        for package, description in dependencies.items():
            try:
                module = __import__(package)
                version = getattr(module, "__version__", "unknown")
                print(f"✓ {package}: v{version} - {description}")
            except ImportError:
                print(f"✗ {package}: Not installed - {description}")

        print("\nCore Components:")

        core_scripts = [
            ("generate_icons.py", "Basic icon generator"),
            ("enhanced_icon_generator.py", "Enhanced icon generator"),
            ("palette_manager.py", "Color palette manager"),
            ("icon_framework_exporter.py", "Framework exporter"),
            ("debug_bake_svg.py", "SVG debugging tool")
        ]

        for script, description in core_scripts:
            script_path = SCRIPT_DIR / script
            if script_path.exists():
                print(f"✓ {script}: Available - {description}")
            else:
                print(f"✗ {script}: Missing - {description}")

        return 0

    def _show_stats(self) -> int:
        """Show icon statistics"""
        if not OUT.exists():
            print("No icons found. Generate icons first.")
            return 1

        print("StrategyDECK Icon Statistics")
        print("=" * 40)

        # Count modes
        modes = set()
        for mode_dir in OUT.glob("*"):
            if mode_dir.is_dir():
                modes.add(mode_dir.name)

        print(f"Modes: {', '.join(modes)} ({len(modes)} total)")

        # Count finishes
        finishes = set()
        for mode_dir in OUT.glob("*"):
            if mode_dir.is_dir():
                for finish_dir in mode_dir.glob("*"):
                    if finish_dir.is_dir():
                        finishes.add(finish_dir.name)

        print(f"Finishes: {', '.join(finishes)} ({len(finishes)} total)")

        # Count sizes
        sizes = set()
        for size_dir in OUT.glob("*/*/*px"):
            if size_dir.is_dir():
                size = size_dir.name.replace("px", "")
                try:
                    sizes.add(int(size))
                except ValueError:
                    pass

        print(f"Sizes: {', '.join(str(s) for s in sorted(sizes))} ({len(sizes)} total)")

        # Count contexts
        contexts = set()
        for context_dir in OUT.glob("*/*/*px/*"):
            if context_dir.is_dir():
                contexts.add(context_dir.name)

        print(f"Contexts: {', '.join(contexts)} ({len(contexts)} total)")

        # Count files
        svg_count = len(list(OUT.glob("**/*.svg")))
        png_count = len(list(OUT.glob("**/*.png")))

        print(f"SVG files: {svg_count}")
        print(f"PNG files: {png_count}")
        print(f"Total files: {svg_count + png_count}")

        return 0

    def _show_system_info(self) -> int:
        """Show system information"""
        print("StrategyDECK Icon System Information")
        print("=" * 40)

        print(f"Root directory: {ROOT}")
        print(f"Scripts directory: {SCRIPT_DIR}")
        print(f"Output directory: {OUT}")
        print(f"Configuration matrix: {CSV_PATH}")

        # Python version
        print(f"Python version: {sys.version.split()[0]}")

        # Check for master SVGs
        masters_dir = ROOT / "assets" / "masters"
        master_files = list(masters_dir.glob("*.svg"))

        if master_files:
            print(f"Master SVGs: {', '.join(f.name for f in master_files)}")
        else:
            print("Master SVGs: None found")

        # Check for custom palettes
        config_dir = ROOT / "config"
        if config_dir.exists():
            palette_files = list(config_dir.glob("*_palette.json"))
            if palette_files:
                print(
                    f"Custom palettes: {', '.join(f.stem.replace('_palette', '') for f in palette_files)}")
            else:
                print("Custom palettes: None found")

        return 0


# Set up global variables if imported
try:
    from generate_icons import CSV_PATH, OUT, ROOT
except ImportError:
    ROOT = Path(__file__).resolve().parent.parent
    OUT = ROOT / "assets" / "icons"
    CSV_PATH = ROOT / "strategy_icon_variant_matrix.csv"


def main():
    """Main entry point"""
    cli = StrategyCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
