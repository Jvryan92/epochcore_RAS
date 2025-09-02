"""
Base classes for the Recursive Improvement Framework

Provides foundation for all recursive, compounding autonomous improvement algorithms.
"""

import asyncio
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
import logging


@dataclass
class CompoundingAction:
    """Represents a recursive action that compounds with other actions."""
    
    name: str
    action: Callable
    interval: float  # Main interval (e.g., 1.0 for weekly)
    pre_action: Optional[Callable] = None
    pre_interval: float = 0.25  # Pre-action interval (default +0.25)
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RecursiveEngine(ABC):
    """Abstract base class for all recursive improvement engines."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"recursive.{name}")
        self.is_running = False
        self.actions: List[CompoundingAction] = []
        self.last_execution = {}
        self.execution_history = []
        
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the engine. Returns True if successful."""
        pass
    
    @abstractmethod
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute the main recursive action. Returns execution result."""
        pass
    
    def execute_pre_action(self) -> Dict[str, Any]:
        """Execute pre-action that runs before main action completes."""
        self.logger.info(f"{self.name}: Executing pre-action at +{0.25} interval")
        return {"status": "pre-action_completed", "engine": self.name}
    
    def add_compounding_action(self, action: CompoundingAction):
        """Add a compounding action to this engine."""
        self.actions.append(action)
        self.logger.info(f"{self.name}: Added compounding action '{action.name}'")
    
    def get_next_execution_time(self, base_interval: float = 1.0) -> datetime:
        """Calculate next execution time based on interval."""
        last_exec = self.last_execution.get('main', datetime.now())
        return last_exec + timedelta(weeks=base_interval)
    
    def should_execute(self, action_type: str = 'main') -> bool:
        """Check if action should execute based on scheduling."""
        if action_type not in self.last_execution:
            return True
            
        last_exec = self.last_execution[action_type]
        interval = 1.0 if action_type == 'main' else 0.25
        next_exec = last_exec + timedelta(weeks=interval)
        return datetime.now() >= next_exec
    
    def execute_with_compounding(self) -> Dict[str, Any]:
        """Execute action with compounding logic - pre-action overlaps main action."""
        if not self.is_running:
            return {"error": "Engine not running"}
        
        result = {
            "engine": self.name,
            "timestamp": datetime.now().isoformat(),
            "actions_executed": []
        }
        
        try:
            # Schedule pre-action to run during main action execution
            if self.should_execute('pre'):
                pre_thread = threading.Thread(
                    target=self._delayed_pre_action, 
                    args=(0.25,)
                )
                pre_thread.start()
            
            # Execute main action
            if self.should_execute('main'):
                main_result = self.execute_main_action()
                result["main_action"] = main_result
                result["actions_executed"].append("main")
                self.last_execution['main'] = datetime.now()
            
            # Wait for pre-action to complete if it was started
            if 'pre_thread' in locals():
                pre_thread.join(timeout=10)  # Don't wait forever
            
            self.execution_history.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"{self.name}: Execution error - {e}")
            result["error"] = str(e)
            return result
    
    def _delayed_pre_action(self, delay: float):
        """Execute pre-action with delay to create overlap."""
        time.sleep(delay)
        if self.should_execute('pre'):
            try:
                pre_result = self.execute_pre_action()
                self.last_execution['pre'] = datetime.now()
                self.logger.info(f"{self.name}: Pre-action completed with overlap")
            except Exception as e:
                self.logger.error(f"{self.name}: Pre-action error - {e}")
    
    def start(self) -> bool:
        """Start the recursive engine."""
        if self.initialize():
            self.is_running = True
            self.logger.info(f"{self.name}: Started successfully")
            return True
        return False
    
    def stop(self):
        """Stop the recursive engine."""
        self.is_running = False
        self.logger.info(f"{self.name}: Stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return {
            "name": self.name,
            "running": self.is_running,
            "last_execution": self.last_execution,
            "total_executions": len(self.execution_history),
            "actions_count": len(self.actions)
        }


class RecursiveHook:
    """Hook system for integrating recursive improvements into existing modules."""
    
    def __init__(self):
        self.hooks: Dict[str, List[Callable]] = {}
        self.logger = logging.getLogger("recursive.hooks")
    
    def register_hook(self, event: str, callback: Callable):
        """Register a hook for a specific event."""
        if event not in self.hooks:
            self.hooks[event] = []
        self.hooks[event].append(callback)
        self.logger.debug(f"Registered hook for event: {event}")
    
    def trigger_hook(self, event: str, *args, **kwargs):
        """Trigger all hooks for a specific event."""
        if event in self.hooks:
            results = []
            for hook in self.hooks[event]:
                try:
                    result = hook(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Hook error for {event}: {e}")
            return results
        return []