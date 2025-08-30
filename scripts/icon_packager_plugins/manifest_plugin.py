#!/usr/bin/env python3
"""
Manifest Plugin for Icon Packager

This plugin generates a manifest.json file that includes detailed information
about each icon in the package.
"""

import json
from pathlib import Path
from typing import Any, Dict


def process(temp_dir: Path, variants: Dict, options: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the icon files and generate a manifest.json file.

    Args:
        temp_dir: Temporary directory where files are being packaged
        variants: Dictionary of icon variants being packaged
        options: Plugin-specific options

    Returns:
        Dict with plugin results
    """
    manifest = {
        "icons": [],
        "variant_count": len(variants),
        "total_files": 0
    }

    # Process each variant
    for variant_name, variant in variants.items():
        for icon_file in variant.files:
            manifest["icons"].append({
                "path": str(icon_file.path),
                "mode": icon_file.mode,
                "finish": icon_file.finish,
                "size": icon_file.size,
                "context": icon_file.context,
                "format": icon_file.format,
                "variant": variant_name
            })

    manifest["total_files"] = len(manifest["icons"])

    # Write manifest file
    manifest_path = temp_dir / "manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return {
        "manifest_path": str(manifest_path),
        "icon_count": manifest["total_files"]
    }
