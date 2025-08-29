"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/usr/bin/env python3
"""
EPOCHCORE RAS Universal Protection System
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
Applies comprehensive protection to all repository files
"""

from typing import Dict, List, Set, Tuple
from pathlib import Path
from datetime import datetime
import sys
import os
import logging
import json
import hashlib
import hmac

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniversalProtection:
    """Comprehensive protection system for all repository files."""

    def __init__(self):
        """Initialize protection system."""
        self.repo_root = Path(__file__).parent
        self.protected_files: Set[Path] = set()
        self.signature_map: Dict[str, str] = {}
        self.protection_manifest = self.repo_root / ".protection_manifest"

        # Protection metadata
        self.protection_info = {
            "copyright": {
                "owner": "John Ryan",
                "business": "EpochCore Business",
                "location": "Charlotte NC",
                "year": "2024",
                "contact": "jryan2k19@gmail.com",
                "rights": "All Rights Reserved"
            },
            "license": "Proprietary - All Rights Reserved",
            "timestamp": datetime.now().isoformat(),
            "protection_version": "2.0.0"
        }

        # Initialize subsystems
        self._initialize()

    def _initialize(self):
        """Initialize protection system."""
        # Load existing manifest if it exists
        if self.protection_manifest.exists():
            try:
                data = json.loads(self.protection_manifest.read_text())
                self.signature_map = data.get("signatures", {})
            except Exception as e:
                logger.error(f"Error loading manifest: {e}")

    def protect_repository(self):
        """Apply protection to all repository files."""
        logger.info("Starting repository protection...")

        # Get all files
        all_files = self._scan_repository()
        total = len(all_files)
        protected = 0

        # Process each file
        for file_path in all_files:
            try:
                if self._should_protect(file_path):
                    self._protect_file(file_path)
                    protected += 1
                    logger.info(f"Protected: {file_path} ({protected}/{total})")
            except Exception as e:
                logger.error(f"Error protecting {file_path}: {e}")

        # Save manifest
        self._save_manifest()
        logger.info(f"Protection complete. Protected {protected} files.")

    def _scan_repository(self) -> Set[Path]:
        """Scan repository for all files."""
        files = set()

        for file_path in self.repo_root.rglob("*"):
            if file_path.is_file() and not self._is_excluded(file_path):
                files.add(file_path)

        return files

    def _is_excluded(self, path: Path) -> bool:
        """Check if file should be excluded from protection."""
        excludes = {
            ".git", "__pycache__", ".pytest_cache", "*.pyc",
            ".DS_Store", ".protection_manifest"
        }

        # Check each part of the path
        parts = path.relative_to(self.repo_root).parts
        return any(p.startswith(".") or p in excludes for p in parts)

    def _should_protect(self, path: Path) -> bool:
        """Determine if file needs protection."""
        # Skip if already protected with latest version
        if str(path) in self.signature_map:
            return False

        # Always protect certain files
        critical_patterns = {
            "*.py", "*.sh", "*.md", "*.json", "*.jsonl",
            "*.txt", "*.yml", "*.yaml", "Dockerfile"
        }

        return any(
            path.match(pattern) for pattern in critical_patterns
        )

    def _protect_file(self, path: Path):
        """Apply protection to a single file."""
        # Read file content
        content = path.read_bytes()

        # Generate signature
        signature = self._generate_signature(content)

        # Add to signature map
        self.signature_map[str(path)] = {
            "signature": signature,
            "timestamp": datetime.now().isoformat(),
            "protection": self.protection_info.copy()
        }

        # If it's a text file, add protection header
        if path.suffix in {".py", ".sh", ".md", ".txt"}:
            self._add_protection_header(path)

    def _generate_signature(self, content: bytes) -> str:
        """Generate cryptographic signature for content."""
        return hashlib.sha256(content).hexdigest()

    def _add_protection_header(self, path: Path):
        """Add protection header to text files."""
        content = path.read_text()
        header = f'''"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

'''
        # Add header if not already present
        if not content.startswith('"""PROTECTED FILE'):
            path.write_text(header + content)

    def _save_manifest(self):
        """Save protection manifest."""
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(self.signature_map),
            "signatures": self.signature_map,
            "protection_info": self.protection_info
        }

        self.protection_manifest.write_text(
            json.dumps(manifest, indent=2)
        )

    def verify_repository(self) -> Tuple[bool, List[str]]:
        """Verify integrity of protected files."""
        violations = []

        for file_path, info in self.signature_map.items():
            path = Path(file_path)
            if path.exists():
                content = path.read_bytes()
                current_sig = self._generate_signature(content)
                if current_sig != info["signature"]:
                    violations.append(file_path)

        return len(violations) == 0, violations


if __name__ == "__main__":
    protector = UniversalProtection()
    protector.protect_repository()

    # Verify protection
    is_valid, violations = protector.verify_repository()
    if not is_valid:
        logger.warning("Protection violations found:")
        for v in violations:
            logger.warning(f" - {v}")
    else:
        logger.info("All files protected and verified!")
