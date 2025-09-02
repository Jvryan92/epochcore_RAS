"""
EpochCore RAS Recursive Improvement Framework

This module provides the core infrastructure for implementing recursive,
compounding autonomous improvement algorithms across the entire system.
"""

from .base import RecursiveEngine, CompoundingAction
from .orchestrator import RecursiveOrchestrator
from .logger import RecursiveLogger
from .scheduler import RecursiveScheduler

__all__ = [
    'RecursiveEngine',
    'CompoundingAction',
    'RecursiveOrchestrator',
    'RecursiveLogger',
    'RecursiveScheduler'
]

__version__ = '1.0.0'