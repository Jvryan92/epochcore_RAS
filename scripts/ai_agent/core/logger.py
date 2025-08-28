"""Logging configuration for the AI agent system."""

import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager
import traceback

# Global logger registry
_loggers: Dict[str, logging.Logger] = {}


class Logger:
    """A configurable logger for the AI agent system."""

    def __init__(self, name: str, log_file: str, level: int = logging.INFO):
        """Initialize the logger with a name and output file.

        Args:
            name: The name of the logger
            log_file: Path to the log file
            level: The logging level (default: INFO)
        """
        self.name = name
        self.log_file = log_file
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Always log debug messages to file
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setLevel(logging.DEBUG)

        # Stream handler follows user-specified level
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

        # Ensure debug messages get through
        self.logger.propagate = False

    def debug(self, msg, *args, **kwargs):
        """Log a debug message."""
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """Log an info message."""
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Log an error message."""
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """Log a critical message."""
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        """Log an exception message."""
        self.logger.exception(msg, *args, **kwargs)

    @contextmanager
    def log_context(self, context_name: str):
        """A context manager for logging scoped operations.

        Args:
            context_name: Name of the context/operation
        """
        self.info(f"Starting {context_name}")
        try:
            yield self
            self.info(f"Completed {context_name}")
        except Exception as e:
            error_msg = f"Error in {context_name}: {str(e)}\n{traceback.format_exc()}"
            self.error(error_msg)
            raise


# Global logger registry
_instances: Dict[str, Logger] = {}


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    console_output: bool = True,
) -> logging.Logger:
    """Setup logging configuration for the AI agent system.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console_output: Whether to output logs to console

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("strategy_ai_agent")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log all to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(
    name: str, log_file: str = "ai_agent.log", level: int = logging.INFO
) -> logging.Logger:
    """Get or create a logger instance.

    Args:
        name: The name of the logger
        log_file: Path to the log file (default: ai_agent.log)
        level: The logging level (default: INFO)

    Returns:
        The logger instance
    """
    global _instances
    if not _instances.get(name):
        _instances[name] = Logger(name, log_file, level)
    return _instances[name].logger
