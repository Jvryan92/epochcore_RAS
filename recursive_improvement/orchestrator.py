"""
Recursive Orchestrator - Central coordinator for all recursive improvement engines
"""

import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from .base import RecursiveEngine, RecursiveHook
from .logger import RecursiveLogger
from .scheduler import RecursiveScheduler


class RecursiveOrchestrator:
    """Central orchestrator that coordinates all recursive improvement engines."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger("recursive.orchestrator")
        
        # Core components
        self.recursive_logger = RecursiveLogger()
        self.scheduler = RecursiveScheduler(self.recursive_logger)
        self.hook_system = RecursiveHook()
        
        # State management
        self.engines: Dict[str, RecursiveEngine] = {}
        self.is_initialized = False
        self.start_time = None
        
        # Metrics
        self.total_improvements = 0
        self.active_engines = 0
        
    def initialize(self) -> bool:
        """Initialize the orchestrator and all core systems."""
        try:
            self.logger.info("Initializing Recursive Orchestrator")
            
            # Set up hooks for system integration
            self._setup_core_hooks()
            
            # Start the scheduler
            self.scheduler.start_scheduler()
            
            self.is_initialized = True
            self.start_time = datetime.now()
            
            # Log initialization
            self.recursive_logger.log_action(
                "orchestrator",
                "initialization",
                {"status": "success", "timestamp": self.start_time.isoformat()},
                {"version": "1.0.0"}
            )
            
            self.logger.info("Recursive Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            return False
    
    def register_engine(self, engine: RecursiveEngine) -> bool:
        """Register a recursive engine with the orchestrator."""
        try:
            if not isinstance(engine, RecursiveEngine):
                raise ValueError("Engine must inherit from RecursiveEngine")
            
            # Store the engine
            self.engines[engine.name] = engine
            
            # Register with scheduler
            self.scheduler.register_engine(engine)
            
            # Set up engine-specific hooks
            self._setup_engine_hooks(engine)
            
            self.active_engines += 1
            
            self.logger.info(f"Successfully registered engine: {engine.name}")
            
            # Log registration
            self.recursive_logger.log_action(
                "orchestrator",
                "engine_registration",
                {"engine_name": engine.name, "status": "success"},
                {"total_engines": len(self.engines)}
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register engine {engine.name}: {e}")
            return False
    
    def _setup_core_hooks(self):
        """Set up core system hooks."""
        # Hook for workflow execution
        self.hook_system.register_hook(
            "workflow_start",
            self._on_workflow_start
        )
        
        self.hook_system.register_hook(
            "workflow_complete",
            self._on_workflow_complete
        )
        
        # Hook for status changes
        self.hook_system.register_hook(
            "status_update",
            self._on_status_update
        )
        
        # Hook for system validation
        self.hook_system.register_hook(
            "system_validation",
            self._on_system_validation
        )
        
        self.logger.info("Core hooks established")
    
    def _setup_engine_hooks(self, engine: RecursiveEngine):
        """Set up hooks for a specific engine."""
        engine_hooks = {
            f"{engine.name}_action_complete": self._on_engine_action_complete,
            f"{engine.name}_error": self._on_engine_error,
            f"{engine.name}_improvement": self._on_engine_improvement
        }
        
        for event, callback in engine_hooks.items():
            self.hook_system.register_hook(event, callback)
    
    def trigger_recursive_improvement(self, context: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger recursive improvements based on context."""
        self.logger.info(f"Triggering recursive improvements for context: {context}")
        
        improvement_results = {
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "engines_triggered": [],
            "total_improvements": 0,
            "metadata": metadata or {}
        }
        
        # Trigger relevant engines based on context
        for engine_name, engine in self.engines.items():
            if self._should_trigger_engine(engine, context):
                try:
                    result = engine.execute_with_compounding()
                    improvement_results["engines_triggered"].append({
                        "engine": engine_name,
                        "result": result
                    })
                    
                    if result.get("actions_executed"):
                        improvement_results["total_improvements"] += len(result["actions_executed"])
                    
                except Exception as e:
                    self.logger.error(f"Engine {engine_name} failed during trigger: {e}")
        
        # Update global counter
        self.total_improvements += improvement_results["total_improvements"]
        
        # Log the trigger event
        self.recursive_logger.log_action(
            "orchestrator",
            "recursive_trigger",
            improvement_results,
            {"trigger_context": context, "compounding": True}
        )
        
        # Trigger hooks
        self.hook_system.trigger_hook("recursive_improvement_complete", improvement_results)
        
        return improvement_results
    
    def _should_trigger_engine(self, engine: RecursiveEngine, context: str) -> bool:
        """Determine if an engine should be triggered for a given context."""
        # Default logic - can be overridden per engine
        engine_contexts = {
            "workflow": ["feedback_loop", "workflow_automation", "experimentation"],
            "validation": ["escalation_logic", "kpi_mutation"],
            "content": ["content_stack", "asset_library", "playbook_generator"],
            "monitoring": ["debrief_bot", "cloning_agent"]
        }
        
        for context_group, engines in engine_contexts.items():
            if context_group in context.lower():
                return any(eng in engine.name.lower() for eng in engines)
        
        return True  # Default to trigger all engines
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "orchestrator": {
                "initialized": self.is_initialized,
                "uptime": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                "total_improvements": self.total_improvements,
                "active_engines": self.active_engines
            },
            "scheduler": self.scheduler.get_scheduler_status(),
            "engines": {
                name: engine.get_status() 
                for name, engine in self.engines.items()
            },
            "recent_activity": self.recursive_logger.get_improvement_summary()
        }
        
        return status
    
    def execute_engine(self, engine_name: str) -> Dict[str, Any]:
        """Manually execute a specific engine."""
        if engine_name not in self.engines:
            return {"error": f"Engine '{engine_name}' not found"}
        
        return self.scheduler.execute_engine_now(engine_name)
    
    def shutdown(self):
        """Gracefully shutdown the orchestrator."""
        self.logger.info("Shutting down Recursive Orchestrator")
        
        # Stop scheduler
        self.scheduler.stop_scheduler()
        
        # Stop all engines
        for engine in self.engines.values():
            engine.stop()
        
        # Log shutdown
        self.recursive_logger.log_action(
            "orchestrator",
            "shutdown",
            {
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                "total_improvements": self.total_improvements
            },
            {"graceful": True}
        )
        
        self.logger.info("Recursive Orchestrator shut down complete")
    
    # Hook callback methods
    def _on_workflow_start(self, *args, **kwargs):
        """Handle workflow start events."""
        self.trigger_recursive_improvement("workflow_start", kwargs)
    
    def _on_workflow_complete(self, *args, **kwargs):
        """Handle workflow completion events."""
        self.trigger_recursive_improvement("workflow_complete", kwargs)
    
    def _on_status_update(self, *args, **kwargs):
        """Handle status update events."""
        self.recursive_logger.log_metric(
            "system_status_update",
            kwargs.get("status", "unknown"),
            "orchestrator"
        )
    
    def _on_system_validation(self, *args, **kwargs):
        """Handle system validation events."""
        self.trigger_recursive_improvement("system_validation", kwargs)
    
    def _on_engine_action_complete(self, *args, **kwargs):
        """Handle engine action completion."""
        self.recursive_logger.log_metric(
            "engine_action_complete",
            1,
            kwargs.get("engine_name", "unknown")
        )
    
    def _on_engine_error(self, *args, **kwargs):
        """Handle engine errors."""
        self.recursive_logger.log_metric(
            "engine_error",
            1,
            kwargs.get("engine_name", "unknown"),
            {"error": kwargs.get("error", "unknown")}
        )
    
    def _on_engine_improvement(self, *args, **kwargs):
        """Handle engine improvements."""
        self.total_improvements += kwargs.get("improvement_count", 1)
        self.recursive_logger.log_metric(
            "total_system_improvements",
            self.total_improvements,
            "orchestrator"
        )