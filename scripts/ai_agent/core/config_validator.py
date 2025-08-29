"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""Configuration validation system for AI agents."""

from typing import Any, Dict, List, Optional, Type
from dataclasses import dataclass
import re


@dataclass
class ConfigField:
    """Configuration field definition with validation rules."""

    name: str
    field_type: Type
    required: bool = True
    default: Any = None
    validator: Optional[callable] = None
    description: str = ""


class ConfigValidator:
    """Validates configuration dictionaries against defined schemas."""

    def __init__(self):
        """Initialize the configuration validator."""
        self._schemas: Dict[str, List[ConfigField]] = {}

    def register_schema(self, name: str, fields: List[ConfigField]) -> None:
        """Register a new configuration schema.

        Args:
            name: Schema identifier
            fields: List of configuration fields
        """
        self._schemas[name] = fields

    def validate(self, schema_name: str, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate a configuration against a schema.

        Args:
            schema_name: Name of the schema to validate against
            config: Configuration dictionary to validate

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        if schema_name not in self._schemas:
            return False, [f"Unknown schema: {schema_name}"]

        errors = []
        schema = self._schemas[schema_name]

        # Check required fields
        for field in schema:
            if field.required and field.name not in config:
                errors.append(f"Missing required field: {field.name}")
                continue

            value = config.get(field.name, field.default)

            # Type checking
            if value is not None and not isinstance(value, field.field_type):
                errors.append(
                    f"Field {field.name} must be of type {field.field_type.__name__}"
                )

            # Custom validation
            if field.validator and value is not None:
                try:
                    if not field.validator(value):
                        errors.append(
                            f"Validation failed for field {field.name}"
                        )
                except Exception as e:
                    errors.append(
                        f"Validation error for field {field.name}: {str(e)}"
                    )

        return len(errors) == 0, errors


# Common validators
def validate_positive_int(value: int) -> bool:
    """Validate that a value is a positive integer.

    Args:
        value: Value to validate

    Returns:
        True if value is positive
    """
    return isinstance(value, int) and value > 0


def validate_url(value: str) -> bool:
    """Validate that a value is a valid URL.

    Args:
        value: Value to validate

    Returns:
        True if value is a valid URL
    """
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain
        r"localhost|"  # localhost
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$", re.IGNORECASE
    )
    return bool(url_pattern.match(value))


def validate_path(value: str) -> bool:
    """Validate that a value is a valid file system path.

    Args:
        value: Value to validate

    Returns:
        True if value is a valid path
    """
    try:
        return bool(re.match(r"^[a-zA-Z0-9/_\-\.]+$", value))
    except TypeError:
        return False


def validate_percentage(value: float) -> bool:
    """Validate that a value is a percentage (0-100).

    Args:
        value: Value to validate

    Returns:
        True if value is a valid percentage
    """
    return isinstance(value, (int, float)) and 0 <= value <= 100


# Common schemas
AGENT_BASE_SCHEMA = [
    ConfigField(
        "name",
        str,
        True,
        None,
        lambda x: bool(x.strip()),
        "Agent name identifier"
    ),
    ConfigField(
        "enabled",
        bool,
        False,
        True,
        None,
        "Whether the agent is enabled"
    ),
    ConfigField(
        "log_level",
        str,
        False,
        "INFO",
        lambda x: x in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        "Logging level for the agent"
    ),
    ConfigField(
        "max_retries",
        int,
        False,
        3,
        validate_positive_int,
        "Maximum number of retry attempts"
    ),
    ConfigField(
        "timeout",
        int,
        False,
        300,
        validate_positive_int,
        "Operation timeout in seconds"
    )
]
