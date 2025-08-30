#!/usr/bin/env python3
"""
Icon Packaging System for StrategyDECK

This module provides functions for packaging StrategyDECK icons into
distributable formats (zip, tar.gz, folder) for use in various contexts.
It also supports plugin-based customization of the packaging process.
"""

import argparse
import csv
import importlib
import json
import logging
import os
import re
import shutil
import sys
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("IconPackager")

# Directory setup
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent
ASSETS_DIR = ROOT_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
DIST_DIR = ROOT_DIR / "dist"
PLUGINS_DIR = SCRIPT_DIR / "icon_packager_plugins"

# Load configuration
CONFIG_FILE = ROOT_DIR / "icon_packager_config.json"
DEFAULT_CONFIG = {
    "formats": ["svg", "png"],
    "variants": [],  # Empty means all variants
    "plugins": [],
    "output_dir": "dist",
    "metadata": {
        "name": "StrategyDECK Icons",
        "version": "1.0.0",
        "author": "StrategyDECK Team",
        "license": "Proprietary",
        "description": "StrategyDECK brand icons"
    }
}


@dataclass
class IconFile:
    """Represents an icon file"""
    path: Path
    mode: str
    finish: str
    size: int
    context: str
    format: str
    variant_name: str

    @staticmethod
    def from_path(path: Path) -> 'IconFile':
        """Create an IconFile from a path"""
        # Parse path structure: icons/mode/finish/size/context/filename.ext
        parts = list(path.parts)

        # Find the 'icons' directory in the path
        try:
            icons_index = parts.index('icons')
        except ValueError:
            raise ValueError(
                f"Invalid icon path structure: {path} (no 'icons' directory found)")

        # Check if we have enough parts after 'icons'
        if len(parts) - icons_index < 6:
            raise ValueError(
                f"Invalid icon path structure: {path} (not enough path components)")

        # Extract components
        mode = parts[icons_index + 1]
        finish = parts[icons_index + 2]
        size_part = parts[icons_index + 3]
        if not size_part.endswith('px'):
            raise ValueError(
                f"Invalid icon path structure: {path} (size must end with 'px')")

        size = int(size_part.replace("px", ""))
        context = parts[icons_index + 4]
        format = path.suffix.lstrip(".")
        variant_name = f"{mode}/{finish}/{size}px/{context}"

        return IconFile(
            path=path,
            mode=mode,
            finish=finish,
            size=size,
            context=context,
            format=format,
            variant_name=variant_name
        )

    def get_relative_path(self, base_dir: Path) -> Path:
        """Get the path relative to a base directory"""
        return self.path.relative_to(base_dir)

    def get_output_path(self, output_pattern: str) -> str:
        """Get the output path based on a pattern"""
        output = output_pattern
        output = output.replace("{mode}", self.mode)
        output = output.replace("{finish}", self.finish)
        output = output.replace("{size}", str(self.size))
        output = output.replace("{context}", self.context)
        output = output.replace("{format}", self.format)
        output = output.replace("{filename}", self.path.stem)
        output = output.replace("{ext}", self.path.suffix.lstrip("."))
        return output


@dataclass
class IconVariant:
    """Represents an icon variant"""
    name: str
    mode: str
    finish: str
    size: int
    context: str
    files: List[IconFile] = field(default_factory=list)

    @staticmethod
    def from_parts(mode: str, finish: str, size: int, context: str) -> 'IconVariant':
        """Create an IconVariant from parts"""
        return IconVariant(
            name=f"{mode}/{finish}/{size}px/{context}",
            mode=mode,
            finish=finish,
            size=size,
            context=context
        )


@dataclass
class PackageOptions:
    """Options for packaging icons"""
    output_format: str = "zip"
    output_path: Optional[str] = None
    include_formats: List[str] = field(default_factory=lambda: ["svg", "png"])
    variants: List[str] = field(default_factory=list)  # Empty means all variants
    flatten_output: bool = False
    include_metadata: bool = True
    plugin_options: Dict[str, Any] = field(default_factory=dict)
    output_pattern: str = "{mode}/{finish}/{size}px/{context}/{filename}.{ext}"


@dataclass
class PackageResult:
    """Result of a packaging operation"""
    success: bool
    output_path: Optional[Path]
    file_count: int
    variant_count: int
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    plugin_results: Dict[str, Any] = field(default_factory=dict)


class IconPackager:
    """Main icon packaging system"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path or CONFIG_FILE)
        self.plugins: Dict[str, Callable] = {}

        # Ensure output directory exists
        self.output_dir = Path(self.config.get("output_dir", "dist"))
        if not self.output_dir.is_absolute():
            self.output_dir = ROOT_DIR / self.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load plugins
        self._load_plugins()

    def _load_config(self, config_path: Path) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                logger.warning("Using default configuration")

        return DEFAULT_CONFIG

    def _load_plugins(self):
        """Load packaging plugins"""
        plugins_to_load = self.config.get("plugins", [])

        # Add plugins directory to path
        if not PLUGINS_DIR.exists():
            PLUGINS_DIR.mkdir(parents=True, exist_ok=True)

        sys.path.insert(0, str(PLUGINS_DIR))

        # Load each plugin
        for plugin_name in plugins_to_load:
            try:
                module_name = f"{plugin_name}_plugin"
                plugin_module = importlib.import_module(module_name)

                if hasattr(plugin_module, "process"):
                    self.plugins[plugin_name] = plugin_module.process
                    logger.info(f"Loaded plugin: {plugin_name}")
                else:
                    logger.warning(f"Plugin {plugin_name} has no 'process' function")
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {e}")

    def discover_icons(self, formats: List[str] = None) -> Dict[str, IconVariant]:
        """Discover all available icon variants"""
        formats = formats or ["svg", "png"]
        variants: Dict[str, IconVariant] = {}

        # Iterate through icon directory structure
        for format_name in formats:
            pattern = f"**/*.{format_name}"
            for icon_path in ICONS_DIR.glob(pattern):
                try:
                    icon_file = IconFile.from_path(icon_path)
                    variant_name = icon_file.variant_name

                    if variant_name not in variants:
                        variants[variant_name] = IconVariant(
                            name=variant_name,
                            mode=icon_file.mode,
                            finish=icon_file.finish,
                            size=icon_file.size,
                            context=icon_file.context
                        )

                    variants[variant_name].files.append(icon_file)
                except ValueError as e:
                    logger.warning(f"Skipping invalid icon: {icon_path} - {e}")

        return variants

    def filter_variants(self,
                        variants: Dict[str, IconVariant],
                        include_variants: List[str] = None) -> Dict[str, IconVariant]:
        """Filter variants based on include list"""
        if not include_variants:
            return variants

        filtered_variants = {}

        for pattern in include_variants:
            # Convert glob pattern to regex
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            regex = re.compile(f"^{regex_pattern}$")

            # Find matching variants
            for variant_name, variant in variants.items():
                if regex.match(variant_name):
                    filtered_variants[variant_name] = variant

        return filtered_variants

    def create_package(self, options: PackageOptions) -> PackageResult:
        """Create a package of icon variants"""
        try:
            # Set default output path if not specified
            if not options.output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                options.output_path = str(
                    self.output_dir / f"strategy_icons_{timestamp}.{options.output_format}")

            # Discover icons
            all_variants = self.discover_icons(options.include_formats)
            logger.info(f"Discovered {len(all_variants)} icon variants")

            # Filter variants if specified
            if options.variants:
                variants = self.filter_variants(all_variants, options.variants)
                logger.info(f"Filtered to {len(variants)} variants")
            else:
                variants = all_variants

            if not variants:
                return PackageResult(
                    success=False,
                    output_path=None,
                    file_count=0,
                    variant_count=0,
                    error="No matching variants found"
                )

            # Create temporary directory for packaging
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                file_count = 0

                # Process each variant
                for variant_name, variant in variants.items():
                    for icon_file in variant.files:
                        # Determine output path
                        if options.flatten_output:
                            rel_path = f"{icon_file.path.stem}.{icon_file.format}"
                        else:
                            rel_path = icon_file.get_output_path(options.output_pattern)

                        output_file = temp_path / rel_path
                        output_file.parent.mkdir(parents=True, exist_ok=True)

                        # Copy file
                        shutil.copy2(icon_file.path, output_file)
                        file_count += 1

                # Create metadata file if requested
                if options.include_metadata:
                    metadata = self.config.get("metadata", {}).copy()
                    metadata.update({
                        "variants": list(variants.keys()),
                        "formats": options.include_formats,
                        "file_count": file_count,
                        "created_at": datetime.now().isoformat()
                    })

                    with open(temp_path / "metadata.json", "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2)

                # Run plugins
                plugin_results = {}
                for plugin_name, plugin_func in self.plugins.items():
                    try:
                        plugin_options = options.plugin_options.get(plugin_name, {})
                        plugin_result = plugin_func(temp_path, variants, plugin_options)
                        plugin_results[plugin_name] = plugin_result
                        logger.info(f"Plugin {plugin_name} executed successfully")
                    except Exception as e:
                        logger.error(f"Plugin {plugin_name} failed: {e}")
                        plugin_results[plugin_name] = {"error": str(e)}

                # Create output package
                output_path = Path(options.output_path)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                if options.output_format == "zip":
                    self._create_zip_package(temp_path, output_path)
                elif options.output_format == "tar.gz":
                    self._create_tar_package(temp_path, output_path)
                elif options.output_format == "folder":
                    self._create_folder_package(temp_path, output_path)
                else:
                    return PackageResult(
                        success=False,
                        output_path=None,
                        file_count=file_count,
                        variant_count=len(variants),
                        error=f"Unsupported output format: {options.output_format}"
                    )

                logger.info(f"Package created successfully: {output_path}")
                return PackageResult(
                    success=True,
                    output_path=output_path,
                    file_count=file_count,
                    variant_count=len(variants),
                    plugin_results=plugin_results
                )
        except Exception as e:
            logger.error(f"Package creation failed: {e}")
            return PackageResult(
                success=False,
                output_path=None,
                file_count=0,
                variant_count=0,
                error=str(e)
            )

    def _create_zip_package(self, source_dir: Path, output_path: Path):
        """Create a ZIP package"""
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    zipf.write(
                        file_path,
                        arcname=file_path.relative_to(source_dir)
                    )

    def _create_tar_package(self, source_dir: Path, output_path: Path):
        """Create a TAR.GZ package"""
        with tarfile.open(output_path, "w:gz") as tarf:
            tarf.add(
                source_dir,
                arcname="."
            )

    def _create_folder_package(self, source_dir: Path, output_path: Path):
        """Create a folder package"""
        if output_path.exists():
            shutil.rmtree(output_path)

        shutil.copytree(source_dir, output_path)


def create_icon_package(
    output_format: str = "zip",
    output_path: Optional[str] = None,
    include_formats: List[str] = None,
    variants: List[str] = None,
    flatten_output: bool = False,
    include_metadata: bool = True,
    plugin_options: Dict[str, Any] = None,
    output_pattern: str = "{mode}/{finish}/{size}px/{context}/{filename}.{ext}"
) -> PackageResult:
    """
    Create a package of StrategyDECK icons.

    Args:
        output_format: The format of the output package ("zip", "tar.gz", or "folder")
        output_path: The path where the package will be saved
        include_formats: The file formats to include (e.g., ["svg", "png"])
        variants: List of variant patterns to include (empty means all variants)
        flatten_output: Whether to flatten the directory structure in the output
        include_metadata: Whether to include metadata.json in the package
        plugin_options: Options for packaging plugins
        output_pattern: Pattern for output file paths

    Returns:
        PackageResult: The result of the packaging operation
    """
    packager = IconPackager()

    options = PackageOptions(
        output_format=output_format,
        output_path=output_path,
        include_formats=include_formats or ["svg", "png"],
        variants=variants or [],
        flatten_output=flatten_output,
        include_metadata=include_metadata,
        plugin_options=plugin_options or {},
        output_pattern=output_pattern
    )

    return packager.create_package(options)


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(description="Package StrategyDECK icons")
    parser.add_argument("--format", choices=["zip", "tar.gz", "folder"], default="zip",
                        help="Output package format")
    parser.add_argument("--output", help="Output path")
    parser.add_argument("--formats", nargs="+", default=["svg", "png"],
                        help="File formats to include")
    parser.add_argument("--variants", nargs="+",
                        help="Variant patterns to include (e.g., 'light/*/16px/*')")
    parser.add_argument("--flatten", action="store_true",
                        help="Flatten directory structure in output")
    parser.add_argument("--no-metadata", action="store_true",
                        help="Don't include metadata.json")
    parser.add_argument("--pattern",
                        default="{mode}/{finish}/{size}px/{context}/{filename}.{ext}",
                        help="Pattern for output file paths")
    parser.add_argument("--list", action="store_true",
                        help="List available variants instead of creating a package")
    parser.add_argument("--package-all", action="store_true",
                        help="Package all available variants")

    args = parser.parse_args()

    packager = IconPackager()

    if args.list:
        # List available variants
        variants = packager.discover_icons(args.formats)
        print(f"Available variants ({len(variants)}):")

        for variant_name, variant in sorted(variants.items()):
            file_count = len(variant.files)
            formats = ", ".join(sorted(set(f.format for f in variant.files)))
            print(f"  {variant_name} ({file_count} files, formats: {formats})")

        return

    # Create package
    if args.package_all:
        # Get all available variants and package them all
        variants = packager.discover_icons(args.formats)
        variant_list = list(variants.keys())

        if not variant_list:
            print("No variants found to package")
            sys.exit(1)

        # Set output path if not specified
        if not args.output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output = f"dist/strategy_icons_all_{timestamp}.{args.format}"

        print(f"Packaging all {len(variant_list)} variants...")
    else:
        variant_list = args.variants

    result = create_icon_package(
        output_format=args.format,
        output_path=args.output,
        include_formats=args.formats,
        variants=variant_list,
        flatten_output=args.flatten,
        include_metadata=not args.no_metadata,
        output_pattern=args.pattern
    )

    if result.success:
        print(f"Package created successfully: {result.output_path}")
        print(
            f"Included {result.file_count} files from {result.variant_count} variants")
    else:
        print(f"Package creation failed: {result.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
