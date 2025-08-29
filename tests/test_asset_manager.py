#!/usr/bin/env python3
"""Unified block tests for the AssetManager class."""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, mock_open
import tempfile
import json
import shutil
import os

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ai_agent.agents.asset_manager import AssetManagerAgent as AssetManager


class TestAssetManagerUnified:
    """Test cases for AssetManager using unified block testing."""

    def test_asset_initialization_unified(self):
        """
        Unified block test for asset manager initialization and configuration.
        Tests setup, path management, and configuration validation.
        """
        # Block 1: Test basic initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "asset_root": temp_dir,
                "asset_types": ["images", "icons", "documents"],
                "allowed_extensions": [".png", ".jpg", ".svg", ".pdf"],
            }

            manager = AssetManager(config=config)
            assert manager.asset_root == temp_dir
            assert all(
                os.path.exists(os.path.join(temp_dir, t)) for t in config["asset_types"]
            )
            assert manager.allowed_extensions == set(config["allowed_extensions"])

        # Block 2: Test configuration validation
        invalid_configs = [
            {"asset_types": ["images"]},  # Missing asset_root
            {"asset_root": "/tmp"},  # Missing asset_types
            {"asset_root": "/tmp", "asset_types": "not_a_list"},  # Invalid type
            {
                "asset_root": "/nonexistent/path",
                "asset_types": ["images"],
            },  # Invalid path
        ]

        for invalid_config in invalid_configs:
            with pytest.raises((ValueError, OSError)):
                AssetManager(config=invalid_config)

        # Block 3: Test path normalization
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "asset_root": temp_dir,
                "asset_types": ["images"],
                "allowed_extensions": [".png"],
            }

            manager = AssetManager(config=config)
            test_paths = [
                "images/test.png",
                "./images/test.png",
                "../{}/images/test.png".format(os.path.basename(temp_dir)),
            ]

            for path in test_paths:
                normalized = manager.normalize_path(path)
                assert os.path.normpath(normalized) == os.path.normpath(
                    os.path.join(temp_dir, "images", "test.png")
                )

    def test_asset_operations_unified(self):
        """
        Unified block test for asset operations.
        Tests file operations, validation, and error handling.
        """
        # Block 1: Test asset addition and retrieval
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "asset_root": temp_dir,
                "asset_types": ["images", "documents"],
                "allowed_extensions": [".txt", ".png"],
            }

            manager = AssetManager(config=config)

            # Create test files
            test_files = {
                "images/test.png": b"PNG content",
                "documents/test.txt": b"Text content",
            }

            for path, content in test_files.items():
                full_path = os.path.join(temp_dir, path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "wb") as f:
                    f.write(content)

            # Test retrieval
            for path in test_files:
                assert manager.asset_exists(path)
                content = manager.get_asset(path)
                assert content == test_files[path]

        # Block 2: Test validation and error handling
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "asset_root": temp_dir,
                "asset_types": ["images"],
                "allowed_extensions": [".png"],
            }

            manager = AssetManager(config=config)

            invalid_cases = [
                "images/test.jpg",  # Invalid extension
                "videos/test.png",  # Invalid asset type
                "../outside/test.png",  # Path traversal attempt
                "images/../../../etc/passwd",  # Path traversal attempt
            ]

            for invalid_path in invalid_cases:
                with pytest.raises(ValueError):
                    manager.validate_asset_path(invalid_path)

        # Block 3: Test asset modification and removal
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "asset_root": temp_dir,
                "asset_types": ["images"],
                "allowed_extensions": [".png"],
            }

            manager = AssetManager(config=config)
            test_path = "images/test.png"
            full_path = os.path.join(temp_dir, test_path)

            # Test addition
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "wb") as f:
                f.write(b"Original content")

            # Test modification
            manager.update_asset(test_path, b"Updated content")
            assert manager.get_asset(test_path) == b"Updated content"

            # Test removal
            manager.remove_asset(test_path)
            assert not manager.asset_exists(test_path)
            assert not os.path.exists(full_path)

    def test_asset_batch_operations_unified(self):
        """
        Unified block test for batch asset operations.
        Tests bulk operations, transactions, and consistency.
        """
        # Block 1: Test bulk asset addition
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "asset_root": temp_dir,
                "asset_types": ["images", "documents"],
                "allowed_extensions": [".png", ".txt"],
            }

            manager = AssetManager(config=config)

            test_assets = {
                "images/test1.png": b"PNG 1",
                "images/test2.png": b"PNG 2",
                "documents/test.txt": b"Text content",
            }

            # Add all assets
            for path, content in test_assets.items():
                full_path = os.path.join(temp_dir, path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                manager.add_asset(path, content)

            # Verify all assets
            for path, content in test_assets.items():
                assert manager.asset_exists(path)
                assert manager.get_asset(path) == content

        # Block 2: Test asset listing and filtering
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "asset_root": temp_dir,
                "asset_types": ["images", "documents"],
                "allowed_extensions": [".png", ".txt"],
            }

            manager = AssetManager(config=config)

            # Create test directory structure
            test_files = [
                "images/test1.png",
                "images/test2.png",
                "images/subfolder/test3.png",
                "documents/test1.txt",
                "documents/test2.txt",
            ]

            for file_path in test_files:
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "wb") as f:
                    f.write(b"content")

            # Test listing
            all_assets = manager.list_assets()
            assert len(all_assets) == len(test_files)

            png_assets = manager.list_assets(extension=".png")
            assert len(png_assets) == 3

            image_assets = manager.list_assets(asset_type="images")
            assert len(image_assets) == 3

        # Block 3: Test batch removal and cleanup
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "asset_root": temp_dir,
                "asset_types": ["images", "documents"],
                "allowed_extensions": [".png", ".txt"],
            }

            manager = AssetManager(config=config)

            # Create test files
            test_files = {
                "images/test1.png": b"PNG 1",
                "images/test2.png": b"PNG 2",
                "documents/test.txt": b"Text",
            }

            for path, content in test_files.items():
                full_path = os.path.join(temp_dir, path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                manager.add_asset(path, content)

            # Test batch removal
            manager.remove_assets(["images/test1.png", "documents/test.txt"])
            remaining = manager.list_assets()
            assert len(remaining) == 1
            assert "images/test2.png" in remaining

            # Test cleanup
            manager.cleanup()
            assert not os.path.exists(os.path.join(temp_dir, "images/test2.png"))
