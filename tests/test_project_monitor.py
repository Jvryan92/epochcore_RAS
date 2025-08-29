#!/usr/bin/env python3
"""Unified block tests for the ProjectMonitorAgent class."""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, mock_open
import tempfile
import json
import time
import os


class TestProjectMonitorUnified:
    """Test cases for ProjectMonitorAgent using unified block testing."""

    def setup_method(self):
        """Set up test fixtures."""
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
        from ai_agent.agents import ProjectMonitorAgent

        self.ProjectMonitorAgent = ProjectMonitorAgent

    def setup_method(self):
        """Set up test fixtures."""
        sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

    def test_monitor_initialization_unified(self):
        """
        Unified block test for project monitor initialization.
        Tests configuration, path setup, and validation.
        """
        # Block 1: Test basic initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "project_root": temp_dir,
                "watch_patterns": ["*.py", "*.json"],
                "ignore_patterns": ["__pycache__", "*.pyc"],
                "scan_interval": 1.0,
            }

            monitor = self.ProjectMonitorAgent(config=config)
            assert monitor.project_root == temp_dir
            assert set(monitor.watch_patterns) == set(config["watch_patterns"])
            assert set(monitor.ignore_patterns) == set(config["ignore_patterns"])
            assert monitor.scan_interval == 1.0

        # Block 2: Test configuration validation
        invalid_configs = [
            {},  # Empty config
            {"project_root": "/nonexistent"},  # Invalid path
            {"project_root": temp_dir, "watch_patterns": "*.py"},  # Invalid type
            {"project_root": temp_dir, "scan_interval": "1.0"},  # Invalid type
        ]

        for invalid_config in invalid_configs:
            with pytest.raises(ValueError):
                self.ProjectMonitorAgent(config=invalid_config)

        # Block 3: Test path normalization and validation
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "project_root": temp_dir,
                "watch_patterns": ["*.py"],
                "scan_interval": 1.0,
            }

            monitor = self.ProjectMonitorAgent(config=config)

            test_paths = ["test.py", "./test.py", "subdir/test.py"]

            for path in test_paths:
                full_path = os.path.join(temp_dir, path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write("test")

                assert monitor.is_valid_path(path)
                assert not monitor.is_valid_path(path + "c")  # .pyc should be ignored

    def test_file_monitoring_unified(self):
        """
        Unified block test for file monitoring operations.
        Tests file watching, change detection, and event handling.
        """
        # Block 1: Test file change detection
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "project_root": temp_dir,
                "watch_patterns": ["*.py"],
                "scan_interval": 0.1,
            }

            monitor = self.ProjectMonitorAgent(config=config)

            # Create initial files
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("initial content")

            # First scan to establish baseline
            changes = monitor.scan_for_changes()
            assert changes["added"] == {os.path.relpath(test_file, temp_dir)}
            assert not changes["modified"]
            assert not changes["deleted"]

            # Modify file
            time.sleep(0.1)  # Ensure modification time differs
            with open(test_file, "w") as f:
                f.write("modified content")

            changes = monitor.scan_for_changes()
            assert not changes["added"]
            assert changes["modified"] == {os.path.relpath(test_file, temp_dir)}
            assert not changes["deleted"]

            # Delete file
            os.remove(test_file)
            changes = monitor.scan_for_changes()
            assert not changes["added"]
            assert not changes["modified"]
            assert changes["deleted"] == {os.path.relpath(test_file, temp_dir)}

        # Block 2: Test pattern matching
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "project_root": temp_dir,
                "watch_patterns": ["*.py", "*.json"],
                "ignore_patterns": ["test_*.py", "*.pyc"],
            }

            monitor = self.ProjectMonitorAgent(config=config)

            test_files = {
                "module.py": True,
                "test_module.py": False,  # Should be ignored
                "config.json": True,
                "module.pyc": False,  # Should be ignored
                "data.txt": False,  # Not in watch patterns
            }

            for filename, should_watch in test_files.items():
                path = os.path.join(temp_dir, filename)
                with open(path, "w") as f:
                    f.write("content")

                assert monitor.is_valid_path(filename) == should_watch

        # Block 3: Test recursive monitoring
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "project_root": temp_dir,
                "watch_patterns": ["**/*.py"],
                "scan_interval": 0.1,
            }

            monitor = self.ProjectMonitorAgent(config=config)

            # Create nested directory structure
            test_files = [
                "top.py",
                "dir1/module1.py",
                "dir1/dir2/module2.py",
                "dir1/dir2/dir3/module3.py",
            ]

            for file_path in test_files:
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write("content")

            changes = monitor.scan_for_changes()
            assert changes["added"] == set(test_files)

            # Modify a deep nested file
            time.sleep(0.1)
            deep_file = os.path.join(temp_dir, "dir1/dir2/dir3/module3.py")
            with open(deep_file, "w") as f:
                f.write("modified")

            changes = monitor.scan_for_changes()
            assert not changes["added"]
            assert changes["modified"] == {"dir1/dir2/dir3/module3.py"}
            assert not changes["deleted"]

    def test_event_handling_unified(self):
        """
        Unified block test for event handling and callbacks.
        Tests event notification, filtering, and processing.
        """
        # Block 1: Test event callbacks
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "project_root": temp_dir,
                "watch_patterns": ["*.py"],
                "scan_interval": 0.1,
            }

            monitor = self.ProjectMonitorAgent(config=config)

            # Setup event tracking
            events = []

            def callback(event_type, file_path):
                events.append((event_type, file_path))

            monitor.add_event_handler(callback)

            # Test file operations
            test_file = "test.py"
            full_path = os.path.join(temp_dir, test_file)

            # Addition
            with open(full_path, "w") as f:
                f.write("content")
            monitor.scan_for_changes()

            # Modification
            time.sleep(0.1)
            with open(full_path, "w") as f:
                f.write("modified")
            monitor.scan_for_changes()

            # Deletion
            os.remove(full_path)
            monitor.scan_for_changes()

            assert events == [
                ("added", test_file),
                ("modified", test_file),
                ("deleted", test_file),
            ]

        # Block 2: Test multiple handlers
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "project_root": temp_dir,
                "watch_patterns": ["*.py"],
                "scan_interval": 0.1,
            }

            monitor = self.ProjectMonitorAgent(config=config)

            handler1_events = []
            handler2_events = []

            def handler1(event_type, file_path):
                handler1_events.append((event_type, file_path))

            def handler2(event_type, file_path):
                handler2_events.append((event_type, file_path))

            monitor.add_event_handler(handler1)
            monitor.add_event_handler(handler2)

            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("content")

            monitor.scan_for_changes()

            assert handler1_events == handler2_events
            assert len(handler1_events) == 1
            assert handler1_events[0] == ("added", "test.py")

        # Block 3: Test error handling in callbacks
        with tempfile.TemporaryDirectory() as temp_dir:
            config = {
                "project_root": temp_dir,
                "watch_patterns": ["*.py"],
                "scan_interval": 0.1,
            }

            monitor = self.ProjectMonitorAgent(config=config)

            def error_handler(event_type, file_path):
                raise ValueError("Test error")

            def normal_handler(event_type, file_path):
                normal_handler.called = True

            normal_handler.called = False

            monitor.add_event_handler(error_handler)
            monitor.add_event_handler(normal_handler)

            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("content")

            # Should continue processing handlers even if one fails
            monitor.scan_for_changes()
            assert normal_handler.called
