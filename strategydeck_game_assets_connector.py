#!/usr/bin/env python3
"""
StrategyDECK Game Assets Connector

This module provides functionality to sync StrategyDECK icons with game assets
and SaaS products. It serves as a bridge between the icon generation system
and the game/SaaS development pipelines.
"""

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GameAssetsConnector")

# Directory setup
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR
ASSETS_DIR = ROOT_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"
DIST_DIR = ROOT_DIR / "dist"
GAME_ASSETS_DIR = DIST_DIR / "game-assets"
SHARED_DIR = DIST_DIR / "shared"

# Configuration files
CONFIG_FILE = ROOT_DIR / "game_assets_sync_config.json"
EXPORT_FILE = DIST_DIR / "game-assets-export.json"


class GameAssetsConnector:
    """Connector between StrategyDECK icons and game/SaaS assets"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or CONFIG_FILE
        self.config = self._load_config()

        # Ensure directories exist
        GAME_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        SHARED_DIR.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()

    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        config = {
            "sync_targets": [],
            "shared_storage": {
                "type": "local",
                "path": str(SHARED_DIR)
            },
            "auto_sync": False,
            "sync_on_changes": True,
            "last_sync": None
        }

        # Save default config
        self._save_config(config)
        return config

    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def add_sync_target(self,
                        name: str,
                        path: str,
                        icon_types: List[str],
                        sizes: Optional[List[int]] = None,
                        contexts: Optional[List[str]] = None) -> bool:
        """
        Add a new sync target for game/SaaS assets

        Args:
            name: Name of the target (e.g., "unity-game", "web-dashboard")
            path: Path to the target directory
            icon_types: List of icon types to sync (e.g., ["svg", "png"])
            sizes: Optional list of sizes to sync (e.g., [16, 32])
            contexts: Optional list of contexts to sync (e.g., ["web", "game"])

        Returns:
            bool: Success status
        """
        try:
            target = {
                "name": name,
                "path": path,
                "icon_types": icon_types,
                "sizes": sizes or [],
                "contexts": contexts or [],
                "active": True,
                "last_sync": None
            }

            # Check if target already exists
            for i, existing in enumerate(self.config["sync_targets"]):
                if existing["name"] == name:
                    # Update existing target
                    self.config["sync_targets"][i] = target
                    self._save_config(self.config)
                    logger.info(f"Updated sync target: {name}")
                    return True

            # Add new target
            self.config["sync_targets"].append(target)
            self._save_config(self.config)
            logger.info(f"Added sync target: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add sync target: {e}")
            return False

    def remove_sync_target(self, name: str) -> bool:
        """Remove a sync target"""
        try:
            for i, target in enumerate(self.config["sync_targets"]):
                if target["name"] == name:
                    del self.config["sync_targets"][i]
                    self._save_config(self.config)
                    logger.info(f"Removed sync target: {name}")
                    return True

            logger.warning(f"Sync target not found: {name}")
            return False

        except Exception as e:
            logger.error(f"Failed to remove sync target: {e}")
            return False

    def sync_icons(self, target_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Sync icons to the specified target or all targets

        Args:
            target_name: Optional target name to sync, or None for all targets

        Returns:
            Dict with sync results
        """
        result = {
            "success": True,
            "synced_targets": [],
            "failed_targets": [],
            "synced_files": 0,
            "timestamp": datetime.now().isoformat()
        }

        try:
            # Get targets to sync
            targets = [t for t in self.config["sync_targets"] if t["active"]]
            if target_name:
                targets = [t for t in targets if t["name"] == target_name]
                if not targets:
                    result["success"] = False
                    result["error"] = f"Target not found or not active: {target_name}"
                    return result

            # Sync each target
            for target in targets:
                try:
                    synced_files = self._sync_target(target)
                    if synced_files >= 0:
                        target["last_sync"] = datetime.now().isoformat()
                        result["synced_targets"].append(target["name"])
                        result["synced_files"] += synced_files
                    else:
                        result["failed_targets"].append(target["name"])
                except Exception as e:
                    logger.error(f"Failed to sync target {target['name']}: {e}")
                    result["failed_targets"].append(target["name"])

            # Update last sync time
            self.config["last_sync"] = datetime.now().isoformat()
            self._save_config(self.config)

            # Update export file
            self._update_export_file(result)

            # Check overall success
            if result["failed_targets"]:
                result["success"] = False

            return result

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            result["success"] = False
            result["error"] = str(e)
            return result

    def _sync_target(self, target: Dict[str, Any]) -> int:
        """
        Sync icons to a specific target

        Args:
            target: Target configuration

        Returns:
            int: Number of synced files, or -1 on error
        """
        try:
            target_path = Path(target["path"])
            if not target_path.exists():
                target_path.mkdir(parents=True, exist_ok=True)

            synced_files = 0

            # Determine which icons to sync
            icon_types = target.get("icon_types", ["svg", "png"])
            sizes = target.get("sizes", [])
            contexts = target.get("contexts", [])

            # Find matching icons
            for icon_type in icon_types:
                pattern = f"**/*.{icon_type}"
                for icon_path in ICONS_DIR.glob(pattern):
                    try:
                        # Parse path components
                        parts = list(icon_path.parts)
                        icons_index = parts.index("icons")

                        # Extract components
                        mode = parts[icons_index + 1]
                        finish = parts[icons_index + 2]
                        size_part = parts[icons_index + 3]
                        size = int(size_part.replace("px", ""))
                        context = parts[icons_index + 4]

                        # Check if icon matches filters
                        if sizes and size not in sizes:
                            continue

                        if contexts and context not in contexts:
                            continue

                        # Determine output path
                        rel_path = icon_path.relative_to(ICONS_DIR)
                        out_path = target_path / rel_path

                        # Create output directory
                        out_path.parent.mkdir(parents=True, exist_ok=True)

                        # Copy icon file
                        shutil.copy2(icon_path, out_path)
                        synced_files += 1

                    except Exception as e:
                        logger.warning(f"Failed to sync icon {icon_path}: {e}")

            logger.info(f"Synced {synced_files} icons to {target['name']}")
            return synced_files

        except Exception as e:
            logger.error(f"Failed to sync target {target['name']}: {e}")
            return -1

    def _update_export_file(self, sync_result: Dict[str, Any]) -> None:
        """Update the export file with sync results"""
        try:
            export_data = {
                "last_sync": sync_result["timestamp"],
                "sync_targets": self.config["sync_targets"],
                "stats": {
                    "synced_files": sync_result["synced_files"],
                    "synced_targets": len(sync_result["synced_targets"]),
                    "failed_targets": len(sync_result["failed_targets"])
                }
            }

            with open(EXPORT_FILE, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to update export file: {e}")

    def update_shared_storage(self) -> bool:
        """Update shared storage with the latest icons"""
        try:
            shared_config = self.config.get("shared_storage", {})
            if shared_config.get("type") != "local":
                logger.warning("Only local shared storage is currently supported")
                return False

            shared_path = Path(shared_config.get("path", str(SHARED_DIR)))
            shared_path.mkdir(parents=True, exist_ok=True)

            # Clear existing files
            for item in shared_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

            # Copy all icons to shared storage
            icon_count = 0
            for ext in ["svg", "png"]:
                pattern = f"**/*.{ext}"
                for icon_path in ICONS_DIR.glob(pattern):
                    rel_path = icon_path.relative_to(ICONS_DIR)
                    out_path = shared_path / rel_path
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(icon_path, out_path)
                    icon_count += 1

            logger.info(f"Updated shared storage with {icon_count} icons")
            return True

        except Exception as e:
            logger.error(f"Failed to update shared storage: {e}")
            return False

    def list_available_icons(self) -> Dict[str, Any]:
        """Get a list of all available icons"""
        result = {
            "modes": set(),
            "finishes": set(),
            "sizes": set(),
            "contexts": set(),
            "formats": set(),
            "variants": [],
            "total_count": 0
        }

        try:
            for ext in ["svg", "png"]:
                pattern = f"**/*.{ext}"
                for icon_path in ICONS_DIR.glob(pattern):
                    try:
                        # Parse path components
                        parts = list(icon_path.parts)
                        icons_index = parts.index("icons")

                        # Extract components
                        mode = parts[icons_index + 1]
                        finish = parts[icons_index + 2]
                        size_part = parts[icons_index + 3]
                        size = int(size_part.replace("px", ""))
                        context = parts[icons_index + 4]
                        format_type = icon_path.suffix.lstrip(".")

                        # Update result sets
                        result["modes"].add(mode)
                        result["finishes"].add(finish)
                        result["sizes"].add(size)
                        result["contexts"].add(context)
                        result["formats"].add(format_type)

                        # Add variant info
                        variant = {
                            "mode": mode,
                            "finish": finish,
                            "size": size,
                            "context": context,
                            "path": str(icon_path)
                        }

                        if variant not in result["variants"]:
                            result["variants"].append(variant)

                        result["total_count"] += 1

                    except Exception as e:
                        logger.warning(f"Failed to parse icon {icon_path}: {e}")

            # Convert sets to sorted lists for JSON serialization
            result["modes"] = sorted(list(result["modes"]))
            result["finishes"] = sorted(list(result["finishes"]))
            result["sizes"] = sorted(list(result["sizes"]))
            result["contexts"] = sorted(list(result["contexts"]))
            result["formats"] = sorted(list(result["formats"]))

            return result

        except Exception as e:
            logger.error(f"Failed to list available icons: {e}")
            return {
                "error": str(e),
                "total_count": 0
            }


def main():
    """Command-line interface for the game assets connector"""
    parser = argparse.ArgumentParser(description="StrategyDECK Game Assets Connector")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List available icons
    list_parser = subparsers.add_parser("list", help="List available icons")

    # Add sync target
    add_parser = subparsers.add_parser("add-target", help="Add a sync target")
    add_parser.add_argument("name", help="Target name")
    add_parser.add_argument("path", help="Target path")
    add_parser.add_argument("--types", nargs="+", default=["svg", "png"],
                            help="Icon types to sync (e.g., svg png)")
    add_parser.add_argument("--sizes", nargs="+", type=int,
                            help="Icon sizes to sync (e.g., 16 32 48)")
    add_parser.add_argument("--contexts", nargs="+",
                            help="Icon contexts to sync (e.g., web game)")

    # Remove sync target
    remove_parser = subparsers.add_parser("remove-target", help="Remove a sync target")
    remove_parser.add_argument("name", help="Target name")

    # Sync icons
    sync_parser = subparsers.add_parser("sync", help="Sync icons to targets")
    sync_parser.add_argument("--target", help="Specific target to sync")

    # Update shared storage
    update_parser = subparsers.add_parser("update-shared", help="Update shared storage")

    args = parser.parse_args()

    connector = GameAssetsConnector()

    if args.command == "list":
        icons = connector.list_available_icons()
        print(f"Available icons ({icons['total_count']}):")
        print(f"  Modes: {', '.join(icons['modes'])}")
        print(f"  Finishes: {', '.join(icons['finishes'])}")
        print(f"  Sizes: {', '.join(map(str, icons['sizes']))}")
        print(f"  Contexts: {', '.join(icons['contexts'])}")
        print(f"  Formats: {', '.join(icons['formats'])}")

    elif args.command == "add-target":
        success = connector.add_sync_target(
            args.name,
            args.path,
            args.types,
            args.sizes,
            args.contexts
        )
        if success:
            print(f"Added sync target: {args.name}")
        else:
            print(f"Failed to add sync target: {args.name}")
            sys.exit(1)

    elif args.command == "remove-target":
        success = connector.remove_sync_target(args.name)
        if success:
            print(f"Removed sync target: {args.name}")
        else:
            print(f"Failed to remove sync target: {args.name}")
            sys.exit(1)

    elif args.command == "sync":
        result = connector.sync_icons(args.target)
        if result["success"]:
            print(
                f"Synced {result['synced_files']} icons to {len(result['synced_targets'])} targets")
        else:
            if "error" in result:
                print(f"Sync failed: {result['error']}")
            else:
                print(
                    f"Sync partially failed for targets: {', '.join(result['failed_targets'])}")
            sys.exit(1)

    elif args.command == "update-shared":
        success = connector.update_shared_storage()
        if success:
            print("Updated shared storage")
        else:
            print("Failed to update shared storage")
            sys.exit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
