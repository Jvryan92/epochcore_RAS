#!/usr/bin/env python3
"""
Zip Vault Creator
EpochCore RAS Repository Automation

Multi-profile snapshot system with integrity verification,
compression optimization, and archive management.
"""

import os
import json
import yaml
import zipfile
import hashlib
import logging
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import glob
import zlib


class VaultCreator:
    """Creates and manages zip vault snapshots with multiple profiles."""
    
    def __init__(self, config_path: str = "config/vault_settings.yaml"):
        self.config_path = config_path
        self.config = {}
        self.vault_dir = Path("backups/snapshots")
        self.manifest_dir = Path("backups/manifests")
        
        # Ensure directories exist
        for path in [self.vault_dir, self.manifest_dir, Path("config")]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.load_config()
        
        # Archive management
        self.archive_registry = {}
        self.load_archive_registry()
    
    def load_config(self) -> bool:
        """Load vault configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.logger.info("Loaded vault configuration")
                return True
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
        
        # Use default configuration
        self.config = self.get_default_config()
        self.save_config()
        return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default vault configuration."""
        return {
            "profiles": {
                "full_system": {
                    "description": "Complete system snapshot",
                    "include": [
                        "**/*.py",
                        "**/*.yaml",
                        "**/*.yml", 
                        "**/*.json",
                        "**/*.md",
                        "config/**",
                        "data/**",
                        "docs/**"
                    ],
                    "exclude": [
                        "**/__pycache__/**",
                        "**/node_modules/**",
                        "**/.git/**",
                        "**/venv/**",
                        "logs/**",
                        "backups/snapshots/**"
                    ]
                },
                "code_only": {
                    "description": "Code and configuration only",
                    "include": [
                        "**/*.py",
                        "**/*.yaml",
                        "**/*.yml",
                        "config/**"
                    ],
                    "exclude": [
                        "**/__pycache__/**",
                        "logs/**",
                        "backups/**"
                    ]
                },
                "config_only": {
                    "description": "Configuration files only",
                    "include": [
                        "config/**",
                        "*.yaml",
                        "*.yml",
                        "requirements.txt",
                        "pyproject.toml"
                    ],
                    "exclude": []
                }
            },
            "vault": {
                "compression_level": 6,
                "integrity_check": True,
                "encryption": False,
                "retention_days": 90
            },
            "schedule": {
                "full_system": "0 1 * * *",
                "code_only": "0 */6 * * *",
                "config_only": "0 */3 * * *"
            }
        }
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
    
    def load_archive_registry(self) -> bool:
        """Load archive registry."""
        registry_path = self.manifest_dir / "archive_registry.json"
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    self.archive_registry = json.load(f)
                return True
            except Exception as e:
                self.logger.error(f"Failed to load archive registry: {e}")
        
        self.archive_registry = {
            "archives": {},
            "metadata": {
                "total_archives": 0,
                "total_size_mb": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
        return False
    
    def save_archive_registry(self) -> bool:
        """Save archive registry."""
        registry_path = self.manifest_dir / "archive_registry.json"
        try:
            self.archive_registry["metadata"]["last_updated"] = datetime.now().isoformat()
            with open(registry_path, 'w') as f:
                json.dump(self.archive_registry, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save archive registry: {e}")
            return False
    
    def get_files_for_profile(self, profile_name: str) -> Set[Path]:
        """Get list of files matching profile criteria."""
        profile = self.config.get("profiles", {}).get(profile_name, {})
        if not profile:
            self.logger.error(f"Profile {profile_name} not found")
            return set()
        
        include_patterns = profile.get("include", [])
        exclude_patterns = profile.get("exclude", [])
        
        # Get included files
        included_files = set()
        for pattern in include_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file():
                    included_files.add(file_path.resolve())
        
        # Remove excluded files
        excluded_files = set()
        for pattern in exclude_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file():
                    excluded_files.add(file_path.resolve())
        
        final_files = included_files - excluded_files
        
        # Filter out files that don't exist or are not accessible
        accessible_files = set()
        for file_path in final_files:
            try:
                if file_path.exists() and os.access(file_path, os.R_OK):
                    accessible_files.add(file_path)
            except (OSError, PermissionError):
                self.logger.warning(f"Cannot access file: {file_path}")
        
        return accessible_files
    
    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def create_manifest(self, files: Set[Path], profile_name: str) -> Dict[str, Any]:
        """Create a manifest for the snapshot."""
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "profile": profile_name,
            "profile_description": self.config["profiles"][profile_name].get("description", ""),
            "total_files": len(files),
            "files": {},
            "checksums": {},
            "statistics": {
                "total_size_bytes": 0,
                "total_size_mb": 0,
                "file_types": {},
                "largest_file": {"name": "", "size": 0},
                "smallest_file": {"name": "", "size": float('inf')}
            }
        }
        
        for file_path in files:
            try:
                stat = file_path.stat()
                relative_path = str(file_path.relative_to(Path.cwd()))
                
                # Calculate checksum
                checksum = self.calculate_file_checksum(file_path)
                
                # File info
                file_info = {
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "checksum": checksum
                }
                
                manifest["files"][relative_path] = file_info
                manifest["checksums"][relative_path] = checksum
                
                # Update statistics
                manifest["statistics"]["total_size_bytes"] += stat.st_size
                
                # File type statistics
                file_ext = file_path.suffix.lower() or "no_extension"
                manifest["statistics"]["file_types"][file_ext] = manifest["statistics"]["file_types"].get(file_ext, 0) + 1
                
                # Largest/smallest file tracking
                if stat.st_size > manifest["statistics"]["largest_file"]["size"]:
                    manifest["statistics"]["largest_file"] = {"name": relative_path, "size": stat.st_size}
                
                if stat.st_size < manifest["statistics"]["smallest_file"]["size"]:
                    manifest["statistics"]["smallest_file"] = {"name": relative_path, "size": stat.st_size}
                
            except Exception as e:
                self.logger.error(f"Failed to process file {file_path}: {e}")
        
        # Convert bytes to MB
        manifest["statistics"]["total_size_mb"] = manifest["statistics"]["total_size_bytes"] / (1024 * 1024)
        
        # Fix smallest file if no files were processed
        if manifest["statistics"]["smallest_file"]["size"] == float('inf'):
            manifest["statistics"]["smallest_file"] = {"name": "", "size": 0}
        
        return manifest
    
    def create_zip_archive(self, files: Set[Path], archive_path: Path, compression_level: int = 6) -> Dict[str, Any]:
        """Create zip archive with specified compression."""
        archive_result = {
            "success": False,
            "archive_path": str(archive_path),
            "files_added": 0,
            "uncompressed_size": 0,
            "compressed_size": 0,
            "compression_ratio": 0.0,
            "errors": []
        }
        
        try:
            # Ensure parent directory exists
            archive_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Map compression level to zipfile constant
            compression_map = {
                0: zipfile.ZIP_STORED,
                1: zipfile.ZIP_DEFLATED,
                6: zipfile.ZIP_DEFLATED,
                9: zipfile.ZIP_DEFLATED
            }
            
            compression_type = compression_map.get(compression_level, zipfile.ZIP_DEFLATED)
            
            with zipfile.ZipFile(archive_path, 'w', compression=compression_type, compresslevel=compression_level) as zf:
                for file_path in files:
                    try:
                        relative_path = str(file_path.relative_to(Path.cwd()))
                        
                        # Add file to archive
                        zf.write(file_path, relative_path)
                        
                        # Update statistics
                        archive_result["files_added"] += 1
                        archive_result["uncompressed_size"] += file_path.stat().st_size
                        
                    except Exception as e:
                        error_msg = f"Failed to add {file_path} to archive: {str(e)}"
                        archive_result["errors"].append(error_msg)
                        self.logger.error(error_msg)
            
            # Get compressed size
            if archive_path.exists():
                archive_result["compressed_size"] = archive_path.stat().st_size
                
                # Calculate compression ratio
                if archive_result["uncompressed_size"] > 0:
                    archive_result["compression_ratio"] = (
                        1.0 - (archive_result["compressed_size"] / archive_result["uncompressed_size"])
                    ) * 100
                
                archive_result["success"] = True
            
        except Exception as e:
            error_msg = f"Failed to create archive: {str(e)}"
            archive_result["errors"].append(error_msg)
            self.logger.error(error_msg)
        
        return archive_result
    
    def verify_archive_integrity(self, archive_path: Path, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Verify archive integrity against manifest."""
        verification_result = {
            "success": False,
            "archive_valid": False,
            "files_verified": 0,
            "checksum_matches": 0,
            "errors": []
        }
        
        try:
            if not archive_path.exists():
                verification_result["errors"].append("Archive file not found")
                return verification_result
            
            with zipfile.ZipFile(archive_path, 'r') as zf:
                # Test archive integrity
                try:
                    zf.testzip()
                    verification_result["archive_valid"] = True
                except Exception as e:
                    verification_result["errors"].append(f"Archive integrity check failed: {str(e)}")
                    return verification_result
                
                # Verify files and checksums
                for file_path, file_info in manifest["files"].items():
                    try:
                        # Check if file exists in archive
                        if file_path in zf.namelist():
                            verification_result["files_verified"] += 1
                            
                            # Extract and verify checksum
                            with zf.open(file_path) as archived_file:
                                content = archived_file.read()
                                calculated_checksum = hashlib.sha256(content).hexdigest()
                                
                                if calculated_checksum == file_info["checksum"]:
                                    verification_result["checksum_matches"] += 1
                                else:
                                    verification_result["errors"].append(f"Checksum mismatch for {file_path}")
                        else:
                            verification_result["errors"].append(f"File {file_path} not found in archive")
                            
                    except Exception as e:
                        verification_result["errors"].append(f"Failed to verify {file_path}: {str(e)}")
                
                # Overall success check
                verification_result["success"] = (
                    verification_result["archive_valid"] and
                    verification_result["files_verified"] == len(manifest["files"]) and
                    verification_result["checksum_matches"] == len(manifest["files"]) and
                    len(verification_result["errors"]) == 0
                )
                
        except Exception as e:
            verification_result["errors"].append(f"Integrity verification failed: {str(e)}")
        
        return verification_result
    
    def create_snapshot(self, profile_name: str) -> Dict[str, Any]:
        """Create a complete snapshot for the specified profile."""
        snapshot_result = {
            "timestamp": datetime.now().isoformat(),
            "profile": profile_name,
            "success": False,
            "phase": "starting",
            "archive_path": "",
            "manifest_path": "",
            "files_included": 0,
            "archive_size_mb": 0,
            "compression_ratio": 0.0,
            "integrity_verified": False,
            "errors": []
        }
        
        try:
            # Phase 1: Validate profile
            snapshot_result["phase"] = "validation"
            if profile_name not in self.config.get("profiles", {}):
                snapshot_result["errors"].append(f"Profile {profile_name} not found")
                return snapshot_result
            
            # Phase 2: Get files for profile
            snapshot_result["phase"] = "file_discovery"
            files = self.get_files_for_profile(profile_name)
            snapshot_result["files_included"] = len(files)
            
            if not files:
                snapshot_result["errors"].append("No files found for profile")
                return snapshot_result
            
            # Phase 3: Create manifest
            snapshot_result["phase"] = "manifest_creation"
            manifest = self.create_manifest(files, profile_name)
            
            # Generate archive filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_filename = f"{profile_name}_{timestamp}.zip"
            archive_path = self.vault_dir / archive_filename
            snapshot_result["archive_path"] = str(archive_path)
            
            # Generate manifest filename
            manifest_filename = f"{profile_name}_{timestamp}_manifest.json"
            manifest_path = self.manifest_dir / manifest_filename
            snapshot_result["manifest_path"] = str(manifest_path)
            
            # Phase 4: Create archive
            snapshot_result["phase"] = "archive_creation"
            compression_level = self.config.get("vault", {}).get("compression_level", 6)
            archive_result = self.create_zip_archive(files, archive_path, compression_level)
            
            if not archive_result["success"]:
                snapshot_result["errors"].extend(archive_result["errors"])
                return snapshot_result
            
            snapshot_result["archive_size_mb"] = archive_result["compressed_size"] / (1024 * 1024)
            snapshot_result["compression_ratio"] = archive_result["compression_ratio"]
            
            # Phase 5: Save manifest
            snapshot_result["phase"] = "manifest_saving"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Phase 6: Verify integrity (if enabled)
            snapshot_result["phase"] = "integrity_verification"
            if self.config.get("vault", {}).get("integrity_check", True):
                verification_result = self.verify_archive_integrity(archive_path, manifest)
                snapshot_result["integrity_verified"] = verification_result["success"]
                
                if not verification_result["success"]:
                    snapshot_result["errors"].extend(verification_result["errors"])
                    return snapshot_result
            else:
                snapshot_result["integrity_verified"] = True
            
            # Phase 7: Update registry
            snapshot_result["phase"] = "registry_update"
            archive_info = {
                "profile": profile_name,
                "created_at": snapshot_result["timestamp"],
                "archive_path": str(archive_path),
                "manifest_path": str(manifest_path),
                "size_mb": snapshot_result["archive_size_mb"],
                "files_count": snapshot_result["files_included"],
                "compression_ratio": snapshot_result["compression_ratio"],
                "integrity_verified": snapshot_result["integrity_verified"]
            }
            
            archive_id = f"{profile_name}_{timestamp}"
            self.archive_registry["archives"][archive_id] = archive_info
            self.archive_registry["metadata"]["total_archives"] = len(self.archive_registry["archives"])
            self.archive_registry["metadata"]["total_size_mb"] = sum(
                archive["size_mb"] for archive in self.archive_registry["archives"].values()
            )
            
            self.save_archive_registry()
            
            snapshot_result["phase"] = "complete"
            snapshot_result["success"] = True
            
            self.logger.info(f"Successfully created snapshot {archive_id}")
            
        except Exception as e:
            snapshot_result["errors"].append(f"Snapshot creation failed: {str(e)}")
            self.logger.error(f"Snapshot creation failed: {e}")
        
        return snapshot_result
    
    def list_snapshots(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """List all snapshots, optionally filtered by profile."""
        snapshot_list = {
            "timestamp": datetime.now().isoformat(),
            "total_snapshots": 0,
            "total_size_mb": 0,
            "snapshots": [],
            "profiles": {}
        }
        
        for archive_id, archive_info in self.archive_registry["archives"].items():
            if profile is None or archive_info["profile"] == profile:
                snapshot_list["snapshots"].append({
                    "id": archive_id,
                    "profile": archive_info["profile"],
                    "created_at": archive_info["created_at"],
                    "size_mb": archive_info["size_mb"],
                    "files_count": archive_info["files_count"],
                    "compression_ratio": archive_info["compression_ratio"],
                    "exists": Path(archive_info["archive_path"]).exists()
                })
                
                # Profile statistics
                prof = archive_info["profile"]
                if prof not in snapshot_list["profiles"]:
                    snapshot_list["profiles"][prof] = {"count": 0, "total_size_mb": 0}
                
                snapshot_list["profiles"][prof]["count"] += 1
                snapshot_list["profiles"][prof]["total_size_mb"] += archive_info["size_mb"]
        
        snapshot_list["total_snapshots"] = len(snapshot_list["snapshots"])
        snapshot_list["total_size_mb"] = sum(s["size_mb"] for s in snapshot_list["snapshots"])
        
        return snapshot_list
    
    def cleanup_old_snapshots(self, retention_days: Optional[int] = None) -> Dict[str, Any]:
        """Clean up snapshots older than retention period."""
        if retention_days is None:
            retention_days = self.config.get("vault", {}).get("retention_days", 90)
        
        cleanup_result = {
            "timestamp": datetime.now().isoformat(),
            "retention_days": retention_days,
            "snapshots_removed": 0,
            "space_freed_mb": 0,
            "errors": []
        }
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        archives_to_remove = []
        
        try:
            for archive_id, archive_info in self.archive_registry["archives"].items():
                created_at = datetime.fromisoformat(archive_info["created_at"])
                
                if created_at < cutoff_date:
                    archives_to_remove.append(archive_id)
            
            # Remove old archives
            for archive_id in archives_to_remove:
                try:
                    archive_info = self.archive_registry["archives"][archive_id]
                    
                    # Remove archive file
                    archive_path = Path(archive_info["archive_path"])
                    if archive_path.exists():
                        archive_path.unlink()
                        cleanup_result["space_freed_mb"] += archive_info["size_mb"]
                    
                    # Remove manifest file
                    manifest_path = Path(archive_info["manifest_path"])
                    if manifest_path.exists():
                        manifest_path.unlink()
                    
                    # Remove from registry
                    del self.archive_registry["archives"][archive_id]
                    cleanup_result["snapshots_removed"] += 1
                    
                    self.logger.info(f"Removed old snapshot: {archive_id}")
                    
                except Exception as e:
                    error_msg = f"Failed to remove {archive_id}: {str(e)}"
                    cleanup_result["errors"].append(error_msg)
                    self.logger.error(error_msg)
            
            # Update registry
            if archives_to_remove:
                self.save_archive_registry()
            
        except Exception as e:
            cleanup_result["errors"].append(f"Cleanup failed: {str(e)}")
        
        return cleanup_result
    
    def restore_snapshot(self, archive_id: str, restore_path: Optional[Path] = None) -> Dict[str, Any]:
        """Restore a snapshot to specified path."""
        if restore_path is None:
            restore_path = Path("restored_snapshots") / archive_id
        
        restore_result = {
            "timestamp": datetime.now().isoformat(),
            "archive_id": archive_id,
            "restore_path": str(restore_path),
            "success": False,
            "files_restored": 0,
            "errors": []
        }
        
        try:
            if archive_id not in self.archive_registry["archives"]:
                restore_result["errors"].append(f"Archive {archive_id} not found in registry")
                return restore_result
            
            archive_info = self.archive_registry["archives"][archive_id]
            archive_path = Path(archive_info["archive_path"])
            
            if not archive_path.exists():
                restore_result["errors"].append(f"Archive file not found: {archive_path}")
                return restore_result
            
            # Create restore directory
            restore_path.mkdir(parents=True, exist_ok=True)
            
            # Extract archive
            with zipfile.ZipFile(archive_path, 'r') as zf:
                zf.extractall(restore_path)
                restore_result["files_restored"] = len(zf.namelist())
            
            restore_result["success"] = True
            self.logger.info(f"Successfully restored snapshot {archive_id} to {restore_path}")
            
        except Exception as e:
            restore_result["errors"].append(f"Restore failed: {str(e)}")
            self.logger.error(f"Restore failed: {e}")
        
        return restore_result
    
    def get_status(self) -> Dict[str, Any]:
        """Get vault system status."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "config_loaded": bool(self.config),
            "profiles_available": len(self.config.get("profiles", {})),
            "total_archives": len(self.archive_registry["archives"]),
            "total_size_mb": self.archive_registry["metadata"].get("total_size_mb", 0),
            "vault_directory": str(self.vault_dir),
            "vault_directory_exists": self.vault_dir.exists(),
            "manifest_directory": str(self.manifest_dir),
            "manifest_directory_exists": self.manifest_dir.exists()
        }
        
        # Profile details
        status["profiles"] = {}
        for profile_name, profile_config in self.config.get("profiles", {}).items():
            files = self.get_files_for_profile(profile_name)
            status["profiles"][profile_name] = {
                "description": profile_config.get("description", ""),
                "files_count": len(files),
                "include_patterns": len(profile_config.get("include", [])),
                "exclude_patterns": len(profile_config.get("exclude", []))
            }
        
        return status


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Zip Vault Creator")
    parser.add_argument('--create', help='Create snapshot for profile')
    parser.add_argument('--list', action='store_true', help='List all snapshots')
    parser.add_argument('--profile', help='Filter snapshots by profile')
    parser.add_argument('--cleanup', action='store_true', help='Cleanup old snapshots')
    parser.add_argument('--restore', help='Restore snapshot by ID')
    parser.add_argument('--restore-path', help='Path to restore snapshot to')
    parser.add_argument('--status', action='store_true', help='Get vault status')
    
    args = parser.parse_args()
    
    vault = VaultCreator()
    
    if args.create:
        result = vault.create_snapshot(args.create)
        print(json.dumps(result, indent=2))
    elif args.list:
        result = vault.list_snapshots(args.profile)
        print(json.dumps(result, indent=2))
    elif args.cleanup:
        result = vault.cleanup_old_snapshots()
        print(json.dumps(result, indent=2))
    elif args.restore:
        restore_path = Path(args.restore_path) if args.restore_path else None
        result = vault.restore_snapshot(args.restore, restore_path)
        print(json.dumps(result, indent=2))
    elif args.status:
        status = vault.get_status()
        print(json.dumps(status, indent=2))
    else:
        print("Use --create, --list, --cleanup, --restore, or --status")


if __name__ == "__main__":
    main()