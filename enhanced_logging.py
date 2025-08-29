import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class EnhancedLogger:
    """
    Enhanced logging system with structured output and rotation
    """

    def __init__(self, name: str, log_dir: Path):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create log directory
        log_dir.mkdir(parents=True, exist_ok=True)

        # File handler with rotation
        log_file = log_dir / f"{name}.log"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Console handler
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        self.logger.addHandler(console)

    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log a structured event with metadata"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": data,
        }
        self.logger.info(json.dumps(event))
