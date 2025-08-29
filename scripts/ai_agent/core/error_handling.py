"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""Enhanced error handling utilities for agents."""

from typing import Any, Callable, Dict, Optional, Type, Union, TypeVar
from functools import wraps
import asyncio
import time
import logging
import traceback

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

def safe_operation(max_retries: int = 3,
                   retry_delay: float = 1.0,
                   max_delay: float = 10.0,
                   default_value: Any = None,
                   log_errors: bool = True) -> Callable[[F], F]:
    """Decorator for safe operation with retries and error handling.
    
    Args:
        max_retries: Maximum number of retries
        retry_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries
        default_value: Value to return on failure
        log_errors: Whether to log errors
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            delay = retry_delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        if log_errors:
                            logging.error(
                                f"Operation failed after {max_retries} retries: {str(e)}",
                                exc_info=True
                            )
                        return default_value
                        
                    delay = min(delay * 2, max_delay)
                    time.sleep(delay)
                    
        return wrapper  # type: ignore
    return decorator

def with_retry(max_retries: int = 3, 
               retry_delay: float = 1.0,
               max_delay: float = 10.0,
               exceptions: Optional[Union[Type[Exception], tuple[Type[Exception], ...]]] = None) -> Callable[[F], F]:
    """Decorator to retry a function on failure.
    
    Args:
        max_retries: Maximum number of retries
        retry_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries
        exceptions: Exception types to catch and retry
    """
    if exceptions is None:
        exceptions = RetryableError
        
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            retries = 0
            delay = retry_delay
            
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if not isinstance(e, exceptions):  # type: ignore
                        raise
                    retries += 1
                    if retries > max_retries:
                        raise
                        
                    # Exponential backoff with jitter
                    delay = min(delay * 2, max_delay)
                    jitter = delay * 0.1 * (2 * asyncio.get_event_loop().time() % 1 - 1)
                    time.sleep(delay + jitter)
                    
        return wrapper  # type: ignore
    return decorator


class RetryableError(Exception):
    """Error that can be retried."""
    pass


class AgentError(Exception):
    """Base class for agent errors."""
    
    def __init__(self, message: str,
                 error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        """Initialize the agent error.

        Args:
            message: Error message
            error_code: Optional error code
            details: Additional error details
        """
        super().__init__(message)
        self.error_code = error_code or "AGENT_ERROR"
        self.details = details or {}
        self.timestamp = time.time()


class ConfigurationError(AgentError):
    """Raised when there is a configuration-related error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the configuration error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(
            message,
            "CONFIG_ERROR",
            details
        )


class ExecutionError(AgentError):
    """Raised when there is an error during agent execution."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the execution error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(
            message,
            "EXECUTION_ERROR",
            details
        )


class ValidationError(AgentError):
    """Raised when there is a validation error."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize the validation error.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(
            message,
            "VALIDATION_ERROR",
            details
        )


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator for retrying operations that may fail.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    continue

            raise ExecutionError(
                f"Operation failed after {max_attempts} attempts",
                {
                    "last_error": str(last_exception),
                    "last_error_type": type(last_exception).__name__,
                    "attempts": max_attempts
                }
            )
        return wrapper
    return decorator


def log_errors(logger: logging.Logger):
    """Decorator for logging errors that occur in a function.

    Args:
        logger: Logger instance to use for error logging

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    extra={
                        "error_type": type(e).__name__,
                        "traceback": traceback.format_exc()
                    }
                )
                raise
        return wrapper
    return decorator


def safe_execute(logger: logging.Logger, default_value: Any = None):
    """Decorator for safely executing functions with error handling.

    Args:
        logger: Logger instance to use for error logging
        default_value: Value to return if execution fails

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"Error in {func.__name__}, using default value: {str(e)}",
                    extra={
                        "error_type": type(e).__name__,
                        "default_value": default_value
                    }
                )
                return default_value
        return wrapper
    return decorator
