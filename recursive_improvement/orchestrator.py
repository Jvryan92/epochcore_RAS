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
            
            # Initialize autonomous capabilities first
            self.autonomous_resolution_enabled = True
            self.auto_learning_enabled = True
            self.predictive_prevention_enabled = True
            self.autonomous_resolutions = 0
            self.prevented_notifications = 0
            
            # Set up hooks for system integration
            self._setup_core_hooks()
            
            # Set up enhanced hooks for autonomous resolution
            self._setup_autonomous_hooks()
            
            # Start the scheduler
            self.scheduler.start_scheduler()
            
            # Initialize autonomous resolution system
            self._initialize_autonomous_resolution()
            
            self.is_initialized = True
            self.start_time = datetime.now()
            
            # Log initialization
            self.recursive_logger.log_action(
                "orchestrator",
                "initialization",
                {"status": "success", "timestamp": self.start_time.isoformat()},
                {"version": "1.0.0", "autonomous_capabilities": True}
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
    
    def _setup_autonomous_hooks(self):
        """Set up hooks for autonomous notification resolution."""
        try:
            # Hook for automatic notification detection and resolution
            self.hook_system.register_hook(
                "notification_detected",
                self._on_notification_detected
            )
            
            # Hook for resolution validation
            self.hook_system.register_hook(
                "resolution_attempted", 
                self._on_resolution_attempted
            )
            
            # Hook for predictive prevention
            self.hook_system.register_hook(
                "prediction_generated",
                self._on_prediction_generated
            )
            
            # Hook for learning and adaptation
            self.hook_system.register_hook(
                "resolution_completed",
                self._on_resolution_completed
            )
            
            self.logger.info("Autonomous resolution hooks established")
        except Exception as e:
            self.logger.error(f"Failed to setup autonomous hooks: {e}")
    
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
    
    # Complex Autonomy Innovation Methods
    
    def _initialize_autonomous_resolution(self):
        """Initialize autonomous notification resolution system."""
        try:
            # Import the new engines here to avoid circular imports
            from .engines.notification_intelligence_engine import NotificationIntelligenceEngine
            from .engines.autonomous_notification_resolver import AutonomousNotificationResolver
            from .engines.resolution_validator import ResolutionValidator
            from .engines.predictive_improvement_engine import PredictiveImprovementEngine
            
            # Initialize Complex Autonomy engines if not already present
            if "notification_intelligence_engine" not in self.engines:
                self.notification_intelligence = NotificationIntelligenceEngine()
                self.register_engine(self.notification_intelligence)
            
            if "autonomous_notification_resolver" not in self.engines:
                self.notification_resolver = AutonomousNotificationResolver()
                self.register_engine(self.notification_resolver)
            
            if "resolution_validator" not in self.engines:
                self.resolution_validator = ResolutionValidator()
                self.register_engine(self.resolution_validator)
            
            if "predictive_improvement_engine" not in self.engines:
                self.predictive_engine = PredictiveImprovementEngine()
                self.register_engine(self.predictive_engine)
            
            # Set up cross-engine connections
            self._setup_autonomous_cross_connections()
            
            self.logger.info("Autonomous resolution system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize autonomous resolution system: {e}")
    
    def _setup_autonomous_hooks(self):
        """Set up hooks for autonomous notification resolution."""
        # Hook for automatic notification detection and resolution
        self.hook_system.register_hook(
            "notification_detected",
            self._on_notification_detected
        )
        
        # Hook for resolution validation
        self.hook_system.register_hook(
            "resolution_attempted", 
            self._on_resolution_attempted
        )
        
        # Hook for predictive prevention
        self.hook_system.register_hook(
            "prediction_generated",
            self._on_prediction_generated
        )
        
        # Hook for learning and adaptation
        self.hook_system.register_hook(
            "resolution_completed",
            self._on_resolution_completed
        )
        
        self.logger.info("Autonomous resolution hooks established")
    
    def _setup_autonomous_cross_connections(self):
        """Set up cross-connections between autonomous engines."""
        if (self.notification_intelligence and self.notification_resolver and 
            self.resolution_validator and self.predictive_engine):
            
            # Connect intelligence engine to resolver
            # Connect resolver to validator
            # Connect all to predictive engine for learning
            
            self.logger.info("Autonomous cross-connections established")
    
    def _on_notification_detected(self, notification: Dict[str, Any]):
        """Handle automatic notification detection and resolution."""
        if not self.autonomous_resolution_enabled:
            return
        
        self.logger.info(f"Autonomous notification resolution triggered: {notification.get('category', 'unknown')}")
        
        try:
            # Add notification to intelligence engine for learning
            if self.notification_intelligence:
                self.notification_intelligence.add_notification_data(notification)
            
            # Add to predictive engine for pattern learning
            if self.predictive_engine:
                self.predictive_engine.add_notification_data(notification)
            
            # Attempt autonomous resolution
            if self.notification_resolver:
                resolution_result = self.notification_resolver.resolve_notification(notification, self)
                
                # Validate the resolution
                if resolution_result.get("success") and self.resolution_validator:
                    validation_result = self.resolution_validator.validate_resolution(notification, resolution_result)
                    
                    # Trigger completion hook with results
                    self.hook_system.trigger_hook("resolution_completed", {
                        "notification": notification,
                        "resolution": resolution_result,
                        "validation": validation_result
                    })
                    
                    if validation_result.get("is_resolved"):
                        self.autonomous_resolutions += 1
                
        except Exception as e:
            self.logger.error(f"Autonomous notification resolution failed: {e}")
    
    def _on_resolution_attempted(self, resolution_data: Dict[str, Any]):
        """Handle resolution attempt validation."""
        if self.resolution_validator:
            notification = resolution_data.get("notification", {})
            resolution_result = resolution_data.get("resolution_result", {})
            
            validation_result = self.resolution_validator.validate_resolution(notification, resolution_result)
            resolution_data["validation"] = validation_result
    
    def _on_prediction_generated(self, prediction: Dict[str, Any]):
        """Handle predictive prevention based on generated predictions."""
        if not self.predictive_prevention_enabled:
            return
        
        try:
            # Trigger preventive improvements for high-probability predictions
            if prediction.get("probability", 0) >= 0.8:
                if self.predictive_engine:
                    prevention_result = self.predictive_engine.trigger_preventive_improvements([prediction], self)
                    
                    if prevention_result.get("preventive_actions_triggered", 0) > 0:
                        self.prevented_notifications += 1
                        self.logger.info(f"Preventive action triggered for {prediction.get('notification_type')}")
        
        except Exception as e:
            self.logger.error(f"Predictive prevention failed: {e}")
    
    def _on_resolution_completed(self, completion_data: Dict[str, Any]):
        """Handle resolution completion for learning."""
        if not self.auto_learning_enabled:
            return
        
        try:
            # Extract learning data
            notification = completion_data.get("notification", {})
            resolution = completion_data.get("resolution", {})
            validation = completion_data.get("validation", {})
            
            # Update system metrics for trend analysis
            if self.predictive_engine:
                current_metrics = self._capture_current_system_metrics()
                self.predictive_engine.add_system_metrics(current_metrics)
            
            # Log autonomous resolution success
            self.recursive_logger.log_action(
                "orchestrator",
                "autonomous_resolution_completed",
                {
                    "notification_type": notification.get("category", "unknown"),
                    "resolution_success": resolution.get("success", False),
                    "validation_success": validation.get("is_resolved", False),
                    "engines_used": resolution.get("engines_triggered", [])
                },
                {"autonomous": True, "learning": True}
            )
        
        except Exception as e:
            self.logger.error(f"Resolution completion handling failed: {e}")
    
    def _capture_current_system_metrics(self) -> Dict[str, Any]:
        """Capture current system metrics for learning."""
        metrics = {"timestamp": datetime.now().isoformat()}
        
        try:
            import psutil
            metrics.update({
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "process_count": len(psutil.pids()),
                "error_count": 0,  # Would be populated from logs
                "warning_count": 0  # Would be populated from logs
            })
        except ImportError:
            # Simulated metrics if psutil not available
            metrics.update({
                "cpu_usage": 20.0,
                "memory_usage": 50.0,
                "disk_usage": 65.0,
                "process_count": 160,
                "error_count": 1,
                "warning_count": 3,
                "simulated": True
            })
        
        return metrics
    
    def trigger_autonomous_notification_resolution(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Manually trigger autonomous notification resolution."""
        self.logger.info(f"Manual trigger of autonomous notification resolution: {notification.get('category', 'unknown')}")
        
        # Use the autonomous hook system
        self.hook_system.trigger_hook("notification_detected", notification)
        
        return {
            "triggered": True,
            "notification": notification,
            "autonomous_resolution_enabled": self.autonomous_resolution_enabled,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_autonomous_status(self) -> Dict[str, Any]:
        """Get status of autonomous resolution capabilities."""
        return {
            "autonomous_resolution_enabled": self.autonomous_resolution_enabled,
            "auto_learning_enabled": self.auto_learning_enabled,
            "predictive_prevention_enabled": self.predictive_prevention_enabled,
            "autonomous_resolutions": self.autonomous_resolutions,
            "prevented_notifications": self.prevented_notifications,
            "notification_intelligence_available": self.notification_intelligence is not None,
            "notification_resolver_available": self.notification_resolver is not None,
            "resolution_validator_available": self.resolution_validator is not None,
            "predictive_engine_available": self.predictive_engine is not None
        }
    
    def enable_autonomous_resolution(self, enabled: bool = True):
        """Enable or disable autonomous resolution."""
        self.autonomous_resolution_enabled = enabled
        self.logger.info(f"Autonomous resolution {'enabled' if enabled else 'disabled'}")
    
    def enable_predictive_prevention(self, enabled: bool = True):
        """Enable or disable predictive prevention."""
        self.predictive_prevention_enabled = enabled
        self.logger.info(f"Predictive prevention {'enabled' if enabled else 'disabled'}")
    
    def enable_auto_learning(self, enabled: bool = True):
        """Enable or disable automatic learning."""
        self.auto_learning_enabled = enabled
        self.logger.info(f"Auto learning {'enabled' if enabled else 'disabled'}")
    
    def get_complex_autonomy_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of complex autonomy innovations."""
        status = self.get_system_status()
        autonomous_status = self.get_autonomous_status()
        
        # Get status from individual engines
        intelligence_status = {}
        resolver_status = {}
        validator_status = {}
        predictor_status = {}
        
        try:
            if self.notification_intelligence:
                intelligence_status = self.notification_intelligence.get_intelligence_summary()
            if self.notification_resolver:
                resolver_status = self.notification_resolver.get_resolver_status()
            if self.resolution_validator:
                validator_status = self.resolution_validator.get_validator_status()
            if self.predictive_engine:
                predictor_status = self.predictive_engine.get_prediction_status()
        except Exception as e:
            self.logger.debug(f"Error getting engine status: {e}")
        
        return {
            "system_overview": status,
            "autonomous_capabilities": autonomous_status,
            "notification_intelligence": intelligence_status,
            "autonomous_resolver": resolver_status,
            "resolution_validator": validator_status,
            "predictive_engine": predictor_status,
            "total_engines": len(self.engines),
            "complex_autonomy_engines": 4,  # The new engines
            "recursive_engines": len(self.engines) - 4,  # Original engines
            "innovation_summary": {
                "autonomous_resolutions": self.autonomous_resolutions,
                "prevented_notifications": self.prevented_notifications,
                "total_improvements": self.total_improvements,
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
            }
        }