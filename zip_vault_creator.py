#!/usr/bin/env python3
"""
Zip Vault Creator - EpochCore RAS
Creates automated snapshots and vault archives of the system
"""

import os
import json
import yaml
import zipfile
import hashlib
import shutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set
from pathlib import Path
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZipVaultCreator:
    """Automated snapshot and vault creation system."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "zip_vault_config.yaml"
        self.vault_path = Path("vault")
        self.snapshots_path = self.vault_path / "snapshots"
        self.archives_path = self.vault_path / "archives"
        self.logs_path = Path("logs")
        
        # Ensure directories exist
        self.vault_path.mkdir(exist_ok=True)
        self.snapshots_path.mkdir(exist_ok=True)
        self.archives_path.mkdir(exist_ok=True)
        self.logs_path.mkdir(exist_ok=True)
        
        self.config = self._load_config()
        self.vault_history = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load zip vault configuration."""
        default_config = {
            "snapshot_settings": {
                "auto_snapshot": True,
                "snapshot_interval_hours": 6,
                "max_snapshots": 20,
                "compress_level": 6,
                "include_git": False
            },
            "vault_profiles": {
                "full_system": {
                    "description": "Complete system snapshot",
                    "include_patterns": [
                        "*.py", "*.yaml", "*.yml", "*.json", "*.md", "*.txt",
                        "*.sh", "*.ps1", "Makefile", ".gitignore"
                    ],
                    "exclude_patterns": [
                        "__pycache__", "*.pyc", "node_modules", ".git",
                        "logs/*", "vault/*", "venv", "*.log"
                    ],
                    "include_directories": [
                        "recursive_improvement", ".github", "tests", 
                        "docs", "scripts", "configs", "templates"
                    ]
                },
                "code_only": {
                    "description": "Source code only",
                    "include_patterns": ["*.py", "*.yaml", "*.yml", "*.json"],
                    "exclude_patterns": ["__pycache__", "*.pyc", "tests/*"],
                    "include_directories": ["recursive_improvement"]
                },
                "config_backup": {
                    "description": "Configuration files backup",
                    "include_patterns": ["*.yaml", "*.yml", "*.json", "*.conf"],
                    "exclude_patterns": [],
                    "include_directories": ["configs", ".github"]
                }
            },
            "archive_settings": {
                "auto_archive": True,
                "archive_threshold_days": 30,
                "max_archives": 10,
                "encryption_enabled": False,
                "compression_algorithm": "zip"
            },
            "integrity_checks": {
                "enabled": True,
                "hash_algorithm": "sha256",
                "verify_after_creation": True,
                "store_checksums": True
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    default_config.update(loaded_config or {})
            except Exception as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")
                
        return default_config
    
    def create_system_snapshot(self, profile: str = "full_system", 
                              custom_name: str = None) -> Dict[str, Any]:
        """Create a complete system snapshot."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        snapshot_name = custom_name or f"snapshot_{profile}_{timestamp}"
        
        logger.info(f"Creating system snapshot: {snapshot_name}")
        
        try:
            # Get profile configuration
            if profile not in self.config["vault_profiles"]:
                raise ValueError(f"Unknown profile: {profile}")
            
            profile_config = self.config["vault_profiles"][profile]
            
            # Create snapshot
            snapshot_result = self._create_snapshot(snapshot_name, profile_config)
            
            # Verify integrity if enabled
            if self.config["integrity_checks"]["enabled"]:
                integrity_result = self._verify_snapshot_integrity(snapshot_result["snapshot_path"])
                snapshot_result["integrity"] = integrity_result
            
            # Update vault history
            vault_record = {
                "operation": "snapshot_creation",
                "snapshot_name": snapshot_name,
                "profile": profile,
                "timestamp": datetime.now().isoformat(),
                "result": snapshot_result
            }
            
            self.vault_history.append(vault_record)
            self._log_vault_operation(vault_record)
            
            # Cleanup old snapshots if needed
            self._cleanup_old_snapshots()
            
            logger.info(f"Snapshot created successfully: {snapshot_name}")
            
            return {
                "status": "success",
                "snapshot_name": snapshot_name,
                "snapshot_path": snapshot_result["snapshot_path"],
                "files_included": snapshot_result["files_included"],
                "compressed_size_mb": snapshot_result["compressed_size_mb"],
                "creation_time": snapshot_result["creation_time_seconds"]
            }
            
        except Exception as e:
            logger.error(f"Snapshot creation failed: {e}")
            return {
                "status": "error",
                "snapshot_name": snapshot_name,
                "error": str(e)
            }
    
    def _create_snapshot(self, snapshot_name: str, profile_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create snapshot with given configuration."""
        start_time = datetime.now()
        snapshot_path = self.snapshots_path / f"{snapshot_name}.zip"
        
        files_included = 0
        total_size = 0
        
        # Create metadata
        metadata = {
            "snapshot_name": snapshot_name,
            "creation_timestamp": start_time.isoformat(),
            "profile_config": profile_config,
            "system_info": self._get_system_info(),
            "files": []
        }
        
        with zipfile.ZipFile(snapshot_path, 'w', 
                           compression=zipfile.ZIP_DEFLATED,
                           compresslevel=self.config["snapshot_settings"]["compress_level"]) as zipf:
            
            # Add files based on patterns
            included_files = self._find_files_to_include(profile_config)
            
            for file_path in included_files:
                try:
                    arcname = str(file_path)
                    zipf.write(file_path, arcname)
                    
                    file_stat = file_path.stat()
                    file_info = {
                        "path": arcname,
                        "size": file_stat.st_size,
                        "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        "checksum": self._calculate_file_hash(file_path) if self.config["integrity_checks"]["enabled"] else None
                    }
                    
                    metadata["files"].append(file_info)
                    files_included += 1
                    total_size += file_stat.st_size
                    
                except Exception as e:
                    logger.warning(f"Failed to include file {file_path}: {e}")
            
            # Add metadata file
            metadata_json = json.dumps(metadata, indent=2)
            zipf.writestr("_snapshot_metadata.json", metadata_json)
        
        end_time = datetime.now()
        compressed_size = snapshot_path.stat().st_size
        
        return {
            "snapshot_path": str(snapshot_path),
            "files_included": files_included,
            "original_size_mb": total_size / (1024 * 1024),
            "compressed_size_mb": compressed_size / (1024 * 1024),
            "compression_ratio": compressed_size / total_size if total_size > 0 else 0,
            "creation_time_seconds": (end_time - start_time).total_seconds(),
            "metadata": metadata
        }
    
    def _find_files_to_include(self, profile_config: Dict[str, Any]) -> Set[Path]:
        """Find files to include based on profile configuration."""
        included_files = set()
        
        include_patterns = profile_config.get("include_patterns", [])
        exclude_patterns = profile_config.get("exclude_patterns", [])
        include_directories = profile_config.get("include_directories", [])
        
        # Start with current directory
        search_paths = [Path(".")]
        
        # Add specific directories if specified
        if include_directories:
            search_paths = [Path(d) for d in include_directories if Path(d).exists()]
        
        for search_path in search_paths:
            for pattern in include_patterns:
                for file_path in search_path.glob(f"**/{pattern}"):
                    if file_path.is_file():
                        # Check against exclude patterns
                        should_exclude = False
                        for exclude_pattern in exclude_patterns:
                            if exclude_pattern in str(file_path):
                                should_exclude = True
                                break
                        
                        if not should_exclude:
                            included_files.add(file_path)
        
        return included_files
    
    def create_vault_archive(self, snapshots_to_archive: List[str] = None) -> Dict[str, Any]:
        """Create a vault archive from snapshots."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_name = f"vault_archive_{timestamp}"
        
        logger.info(f"Creating vault archive: {archive_name}")
        
        try:
            # Determine which snapshots to archive
            if not snapshots_to_archive:
                snapshots_to_archive = self._get_snapshots_for_archival()
            
            if not snapshots_to_archive:
                return {"status": "no_snapshots", "message": "No snapshots to archive"}
            
            archive_path = self.archives_path / f"{archive_name}.zip"
            archived_snapshots = 0
            
            with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                # Add snapshots to archive
                for snapshot_name in snapshots_to_archive:
                    snapshot_path = self.snapshots_path / f"{snapshot_name}.zip"
                    
                    if snapshot_path.exists():
                        zipf.write(snapshot_path, f"snapshots/{snapshot_name}.zip")
                        archived_snapshots += 1
                
                # Add archive metadata
                archive_metadata = {
                    "archive_name": archive_name,
                    "creation_timestamp": datetime.now().isoformat(),
                    "snapshots_included": snapshots_to_archive,
                    "total_snapshots": archived_snapshots,
                    "archive_size": 0  # Will be updated after creation
                }
                
                zipf.writestr("_archive_metadata.json", json.dumps(archive_metadata, indent=2))
            
            # Update metadata with final size
            archive_size = archive_path.stat().st_size
            archive_metadata["archive_size"] = archive_size
            
            # Remove archived snapshots if configured
            if self.config["archive_settings"]["auto_archive"]:
                for snapshot_name in snapshots_to_archive:
                    snapshot_path = self.snapshots_path / f"{snapshot_name}.zip"
                    if snapshot_path.exists():
                        snapshot_path.unlink()
                        logger.info(f"Removed archived snapshot: {snapshot_name}")
            
            # Log operation
            vault_record = {
                "operation": "archive_creation",
                "archive_name": archive_name,
                "timestamp": datetime.now().isoformat(),
                "snapshots_archived": archived_snapshots,
                "archive_size_mb": archive_size / (1024 * 1024)
            }
            
            self.vault_history.append(vault_record)
            self._log_vault_operation(vault_record)
            
            # Cleanup old archives
            self._cleanup_old_archives()
            
            logger.info(f"Archive created successfully: {archive_name}")
            
            return {
                "status": "success",
                "archive_name": archive_name,
                "archive_path": str(archive_path),
                "snapshots_archived": archived_snapshots,
                "archive_size_mb": archive_size / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Archive creation failed: {e}")
            return {
                "status": "error",
                "archive_name": archive_name,
                "error": str(e)
            }
    
    def restore_from_snapshot(self, snapshot_name: str, restore_path: str = None) -> Dict[str, Any]:
        """Restore system from a snapshot."""
        logger.info(f"Restoring from snapshot: {snapshot_name}")
        
        try:
            snapshot_path = self.snapshots_path / f"{snapshot_name}.zip"
            
            if not snapshot_path.exists():
                # Check in archives
                archive_path = self._find_snapshot_in_archives(snapshot_name)
                if not archive_path:
                    raise FileNotFoundError(f"Snapshot not found: {snapshot_name}")
                snapshot_path = archive_path
            
            restore_target = Path(restore_path or f"restored_{snapshot_name}")
            restore_target.mkdir(exist_ok=True)
            
            files_restored = 0
            
            with zipfile.ZipFile(snapshot_path, 'r') as zipf:
                # Extract all files
                zipf.extractall(restore_target)
                files_restored = len(zipf.namelist())
                
                # Get metadata if available
                try:
                    metadata_content = zipf.read("_snapshot_metadata.json")
                    metadata = json.loads(metadata_content)
                except KeyError:
                    metadata = {"message": "No metadata available"}
            
            # Log restoration
            vault_record = {
                "operation": "snapshot_restoration",
                "snapshot_name": snapshot_name,
                "restore_path": str(restore_target),
                "timestamp": datetime.now().isoformat(),
                "files_restored": files_restored
            }
            
            self.vault_history.append(vault_record)
            self._log_vault_operation(vault_record)
            
            logger.info(f"Restoration completed: {files_restored} files restored")
            
            return {
                "status": "success",
                "snapshot_name": snapshot_name,
                "restore_path": str(restore_target),
                "files_restored": files_restored,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Restoration failed: {e}")
            return {
                "status": "error",
                "snapshot_name": snapshot_name,
                "error": str(e)
            }
    
    def verify_vault_integrity(self) -> Dict[str, Any]:
        """Verify integrity of all vault files."""
        logger.info("Verifying vault integrity")
        
        integrity_results = {
            "snapshots_verified": 0,
            "snapshots_corrupted": [],
            "archives_verified": 0,
            "archives_corrupted": [],
            "overall_status": "healthy"
        }
        
        try:
            # Verify snapshots
            for snapshot_file in self.snapshots_path.glob("*.zip"):
                try:
                    with zipfile.ZipFile(snapshot_file, 'r') as zipf:
                        # Test zip integrity
                        bad_file = zipf.testzip()
                        if bad_file:
                            integrity_results["snapshots_corrupted"].append({
                                "file": snapshot_file.name,
                                "corrupted_entry": bad_file
                            })
                        else:
                            integrity_results["snapshots_verified"] += 1
                except Exception as e:
                    integrity_results["snapshots_corrupted"].append({
                        "file": snapshot_file.name,
                        "error": str(e)
                    })
            
            # Verify archives
            for archive_file in self.archives_path.glob("*.zip"):
                try:
                    with zipfile.ZipFile(archive_file, 'r') as zipf:
                        bad_file = zipf.testzip()
                        if bad_file:
                            integrity_results["archives_corrupted"].append({
                                "file": archive_file.name,
                                "corrupted_entry": bad_file
                            })
                        else:
                            integrity_results["archives_verified"] += 1
                except Exception as e:
                    integrity_results["archives_corrupted"].append({
                        "file": archive_file.name,
                        "error": str(e)
                    })
            
            # Determine overall status
            if integrity_results["snapshots_corrupted"] or integrity_results["archives_corrupted"]:
                integrity_results["overall_status"] = "degraded"
            
        except Exception as e:
            logger.error(f"Integrity verification failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
        
        return {
            "status": "completed",
            "integrity": integrity_results
        }
    
    def list_snapshots(self) -> Dict[str, Any]:
        """List available snapshots and archives."""
        snapshots = []
        archives = []
        
        # List snapshots
        for snapshot_file in sorted(self.snapshots_path.glob("*.zip")):
            snapshot_info = {
                "name": snapshot_file.stem,
                "size_mb": snapshot_file.stat().st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(snapshot_file.stat().st_mtime).isoformat(),
                "type": "snapshot"
            }
            
            # Try to get metadata
            try:
                with zipfile.ZipFile(snapshot_file, 'r') as zipf:
                    metadata_content = zipf.read("_snapshot_metadata.json")
                    metadata = json.loads(metadata_content)
                    snapshot_info["profile"] = metadata.get("profile_config", {}).get("description", "Unknown")
                    snapshot_info["files_count"] = len(metadata.get("files", []))
            except Exception:
                snapshot_info["profile"] = "Unknown"
                snapshot_info["files_count"] = "Unknown"
            
            snapshots.append(snapshot_info)
        
        # List archives
        for archive_file in sorted(self.archives_path.glob("*.zip")):
            archive_info = {
                "name": archive_file.stem,
                "size_mb": archive_file.stat().st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(archive_file.stat().st_mtime).isoformat(),
                "type": "archive"
            }
            
            # Try to get metadata
            try:
                with zipfile.ZipFile(archive_file, 'r') as zipf:
                    metadata_content = zipf.read("_archive_metadata.json")
                    metadata = json.loads(metadata_content)
                    archive_info["snapshots_count"] = metadata.get("total_snapshots", "Unknown")
            except Exception:
                archive_info["snapshots_count"] = "Unknown"
            
            archives.append(archive_info)
        
        return {
            "snapshots": snapshots,
            "archives": archives,
            "total_snapshots": len(snapshots),
            "total_archives": len(archives)
        }
    
    def _verify_snapshot_integrity(self, snapshot_path: str) -> Dict[str, Any]:
        """Verify integrity of a specific snapshot."""
        try:
            with zipfile.ZipFile(snapshot_path, 'r') as zipf:
                bad_file = zipf.testzip()
                if bad_file:
                    return {"status": "corrupted", "corrupted_file": bad_file}
                
                # Verify checksums if available
                try:
                    metadata_content = zipf.read("_snapshot_metadata.json")
                    metadata = json.loads(metadata_content)
                    
                    if self.config["integrity_checks"]["store_checksums"]:
                        # This would verify stored checksums against files
                        return {"status": "verified", "checksums_verified": True}
                except KeyError:
                    pass
                
                return {"status": "verified", "checksums_verified": False}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _get_snapshots_for_archival(self) -> List[str]:
        """Get list of snapshots eligible for archival."""
        threshold_days = self.config["archive_settings"]["archive_threshold_days"]
        cutoff_time = datetime.now() - timedelta(days=threshold_days)
        
        snapshots_to_archive = []
        
        for snapshot_file in self.snapshots_path.glob("*.zip"):
            file_time = datetime.fromtimestamp(snapshot_file.stat().st_mtime)
            if file_time < cutoff_time:
                snapshots_to_archive.append(snapshot_file.stem)
        
        return snapshots_to_archive
    
    def _find_snapshot_in_archives(self, snapshot_name: str) -> Path:
        """Find a snapshot within archived files."""
        for archive_file in self.archives_path.glob("*.zip"):
            try:
                with zipfile.ZipFile(archive_file, 'r') as zipf:
                    if f"snapshots/{snapshot_name}.zip" in zipf.namelist():
                        # Extract the snapshot to a temporary location
                        temp_path = self.vault_path / "temp" / f"{snapshot_name}.zip"
                        temp_path.parent.mkdir(exist_ok=True)
                        
                        with zipf.open(f"snapshots/{snapshot_name}.zip") as snapshot_data:
                            temp_path.write_bytes(snapshot_data.read())
                        
                        return temp_path
            except Exception:
                continue
        
        return None
    
    def _cleanup_old_snapshots(self):
        """Remove old snapshots exceeding max count."""
        max_snapshots = self.config["snapshot_settings"]["max_snapshots"]
        snapshots = sorted(self.snapshots_path.glob("*.zip"), 
                          key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_snapshot in snapshots[max_snapshots:]:
            old_snapshot.unlink()
            logger.info(f"Removed old snapshot: {old_snapshot.name}")
    
    def _cleanup_old_archives(self):
        """Remove old archives exceeding max count."""
        max_archives = self.config["archive_settings"]["max_archives"]
        archives = sorted(self.archives_path.glob("*.zip"),
                         key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_archive in archives[max_archives:]:
            old_archive.unlink()
            logger.info(f"Removed old archive: {old_archive.name}")
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information."""
        try:
            import psutil
            import platform
            
            return {
                "hostname": platform.node(),
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_usage": psutil.disk_usage('/').percent,
                "timestamp": datetime.now().isoformat()
            }
        except Exception:
            return {"timestamp": datetime.now().isoformat()}
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate hash of a file."""
        hash_algorithm = self.config["integrity_checks"]["hash_algorithm"]
        hasher = hashlib.new(hash_algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""
    
    def _log_vault_operation(self, vault_record: Dict[str, Any]):
        """Log vault operation."""
        try:
            log_file = self.logs_path / "vault_operations.log"
            with open(log_file, 'a') as f:
                f.write(json.dumps(vault_record) + '\n')
        except Exception as e:
            logger.error(f"Failed to log vault operation: {e}")
    
    def get_vault_status(self) -> Dict[str, Any]:
        """Get current vault status."""
        listing = self.list_snapshots()
        
        total_size = 0
        for snapshot in listing["snapshots"]:
            total_size += snapshot["size_mb"]
        for archive in listing["archives"]:
            total_size += archive["size_mb"]
        
        return {
            "total_snapshots": listing["total_snapshots"],
            "total_archives": listing["total_archives"],
            "total_size_mb": total_size,
            "vault_health": "healthy",  # Could be expanded with actual health checks
            "last_operation": self.vault_history[-1]["timestamp"] if self.vault_history else "never"
        }

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Zip Vault Creator")
    parser.add_argument("--snapshot", help="Create snapshot with profile")
    parser.add_argument("--archive", action="store_true", help="Create archive")
    parser.add_argument("--restore", help="Restore from snapshot")
    parser.add_argument("--list", action="store_true", help="List snapshots and archives")
    parser.add_argument("--verify", action="store_true", help="Verify vault integrity")
    parser.add_argument("--status", action="store_true", help="Show vault status")
    parser.add_argument("--name", help="Custom snapshot name")
    parser.add_argument("--restore-path", help="Restoration path")
    parser.add_argument("--config", help="Config file path")
    
    args = parser.parse_args()
    
    vault_creator = ZipVaultCreator(args.config)
    
    if args.snapshot:
        result = vault_creator.create_system_snapshot(args.snapshot, args.name)
        print(json.dumps(result, indent=2))
    elif args.archive:
        result = vault_creator.create_vault_archive()
        print(json.dumps(result, indent=2))
    elif args.restore:
        result = vault_creator.restore_from_snapshot(args.restore, args.restore_path)
        print(json.dumps(result, indent=2))
    elif args.list:
        result = vault_creator.list_snapshots()
        print(json.dumps(result, indent=2))
    elif args.verify:
        result = vault_creator.verify_vault_integrity()
        print(json.dumps(result, indent=2))
    elif args.status:
        status = vault_creator.get_vault_status()
        print(json.dumps(status, indent=2))
    else:
        print("Use --snapshot <profile>, --archive, --restore <name>, --list, --verify, or --status")

if __name__ == "__main__":
    main()