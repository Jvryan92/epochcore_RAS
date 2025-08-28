#!/usr/bin/env python3
"""Unified block tests for the Logger class."""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, mock_open
import tempfile
import json
import logging
import os

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ai_agent.core.logger import Logger


class TestLoggerUnified:
    """Test cases for Logger using unified block testing."""
    
    def test_logger_initialization_unified(self):
        """
        Unified block test for logger initialization and configuration.
        Tests logger setup, log levels, and file handling.
        """
        # Block 1: Test basic initialization
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "test.log")
            logger = Logger("test_logger", log_file)
            
            assert logger.name == "test_logger"
            assert logger.log_file == log_file
            assert logger.logger.level == logging.INFO
            assert os.path.exists(log_file)
            
            # Test with different log level
            debug_logger = Logger("debug_logger", log_file, level=logging.DEBUG)
            assert debug_logger.logger.level == logging.DEBUG
            
        # Block 2: Test file handler configuration
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "handler_test.log")
            logger = Logger("handler_test", log_file)
            
            handlers = logger.logger.handlers
            assert len(handlers) == 2  # File and stream handlers
            
            file_handler = next(h for h in handlers if isinstance(h, logging.FileHandler))
            assert file_handler.baseFilename == log_file
            assert file_handler.mode == "a"  # Append mode
            
            stream_handler = next(h for h in handlers if isinstance(h, logging.StreamHandler))
            assert stream_handler is not None
            
        # Block 3: Test logging directory creation
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_log_file = os.path.join(temp_dir, "logs", "nested", "test.log")
            logger = Logger("nested_logger", nested_log_file)
            
            assert os.path.exists(os.path.dirname(nested_log_file))
            assert os.path.exists(nested_log_file)

    def test_logging_operations_unified(self):
        """
        Unified block test for logging operations.
        Tests different log levels, formatting, and message handling.
        """
        # Block 1: Test log level methods
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "operations.log")
            logger = Logger("ops_logger", log_file)
            
            test_messages = {
                "debug": "Debug message",
                "info": "Info message",
                "warning": "Warning message",
                "error": "Error message",
                "critical": "Critical message"
            }
            
            # Test each log level
            for level, message in test_messages.items():
                getattr(logger, level)(message)
                
            with open(log_file, 'r') as f:
                content = f.read()
                for message in test_messages.values():
                    assert message in content
                    
        # Block 2: Test message formatting
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "format.log")
            logger = Logger("format_logger", log_file)
            
            # Test string formatting
            logger.info("Test %s: %d", "number", 42)
            logger.error("Error code: %d, message: %s", 404, "Not Found")
            
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Test number: 42" in content
                assert "Error code: 404, message: Not Found" in content
                
        # Block 3: Test exception logging
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "exception.log")
            logger = Logger("exception_logger", log_file)
            
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                logger.exception("An error occurred")
                
            with open(log_file, 'r') as f:
                content = f.read()
                assert "An error occurred" in content
                assert "ValueError: Test exception" in content
                assert "Traceback" in content

    def test_logger_integration_unified(self):
        """
        Unified block test for logger integration features.
        Tests context managers, filters, and special handlers.
        """
        # Block 1: Test context handling
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "context.log")
            logger = Logger("context_logger", log_file)
            
            with logger.log_context("test_operation") as ctx:
                logger.info("Inside context")
                
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Starting test_operation" in content
                assert "Inside context" in content
                assert "Completed test_operation" in content
                
        # Block 2: Test error context
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "error_context.log")
            logger = Logger("error_context_logger", log_file)
            
            try:
                with logger.log_context("error_operation"):
                    raise ValueError("Test error")
            except ValueError:
                pass
                
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Starting error_operation" in content
                assert "Error in error_operation" in content
                assert "ValueError: Test error" in content
                
        # Block 3: Test custom formatters
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = os.path.join(temp_dir, "format.log")
            logger = Logger("format_logger", log_file)
            
            # Add custom formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            for handler in logger.logger.handlers:
                handler.setFormatter(formatter)
                
            logger.info("Custom formatted message")
            
            with open(log_file, 'r') as f:
                content = f.read()
                assert " - format_logger - INFO - Custom formatted message" in content
