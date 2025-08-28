"""Enhanced logging system for AI agents with structured logging and advanced formatting."""

import sys
import json
import logging
import traceback
from typing import Any, Dict, Optional
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler


class StructuredLogFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def __init__(self, **kwargs):
        """Initialize the structured log formatter.

        Args:
            **kwargs: Additional fields to include in all log records
        """
        super().__init__()
        self.additional_fields = kwargs

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string.

        Args:
            record: The log record to format

        Returns:
            JSON formatted log string
        """
        # Base log data
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add location data
        log_data.update({
            "function": record.funcName,
            "line": record.lineno,
            "path": record.pathname,
        })

        # Add any exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add additional configured fields
        log_data.update(self.additional_fields)

        # Add any extra attributes from the record
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


def setup_logging(
    log_dir: Path,
    level: int = logging.INFO,
    max_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    add_console_handler: bool = True,
    **kwargs: Any
) -> None:
    """Set up enhanced logging configuration.

    Args:
        log_dir: Directory for log files
        level: Logging level
        max_size: Maximum size of each log file
        backup_count: Number of backup files to keep
        add_console_handler: Whether to add console output
        **kwargs: Additional fields for structured logging
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create base logger
    logger = logging.getLogger("strategy_ai_agent")
    logger.setLevel(level)
    
    # Remove any existing handlers
    logger.handlers = []

    # Create structured formatter
    formatter = StructuredLogFormatter(**kwargs)

    # File handler with rotation
    log_file = log_dir / "agent.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_size,
        backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Optional console handler
    if add_console_handler:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


class ContextLogger:
    """Context manager for temporary logging configuration."""

    def __init__(
        self,
        logger: logging.Logger,
        context: Dict[str, Any],
        level: Optional[int] = None
    ):
        """Initialize the context logger.

        Args:
            logger: Logger to modify
            context: Context data to add to logs
            level: Optional temporary logging level
        """
        self.logger = logger
        self.context = context
        self.level = level
        self.original_level = logger.level

    def __enter__(self) -> logging.Logger:
        """Enter the logging context.

        Returns:
            Modified logger
        """
        if self.level is not None:
            self.logger.setLevel(self.level)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the logging context."""
        if self.level is not None:
            self.logger.setLevel(self.original_level)
