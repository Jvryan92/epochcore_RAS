#!/usr/bin/env python3
"""
EpochCore RAS Recursive Autonomous Improvement Framework

A unified framework for recursive autonomous improvement across all subsystems.
Supports both autonomous (scheduled/self-triggered) and manual triggers.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Any, Optional
from abc import ABC, abstractmethod
import yaml
import json


class ImprovementMetrics:
    """Tracks improvement metrics and performance data."""
    
    def __init__(self):
        self.improvements = []
        self.performance_history = {}
        self.last_improvement = None
        
    def record_improvement(self, subsystem: str, improvement_type: str, 
                         metrics_before: Dict, metrics_after: Dict, 
                         success: bool = True):
        """Record an improvement attempt and its results."""
        improvement = {
            "timestamp": datetime.now().isoformat(),
            "subsystem": subsystem,
            "improvement_type": improvement_type,
            "metrics_before": metrics_before,
            "metrics_after": metrics_after,
            "success": success,
            "impact": self._calculate_impact(metrics_before, metrics_after)
        }
        self.improvements.append(improvement)
        self.last_improvement = improvement
        
        # Update performance history
        if subsystem not in self.performance_history:
            self.performance_history[subsystem] = []
        self.performance_history[subsystem].append(improvement)
        
    def _calculate_impact(self, before: Dict, after: Dict) -> Dict:
        """Calculate the impact of an improvement."""
        impact = {}
        for key in before.keys():
            if key in after:
                if isinstance(before[key], (int, float)) and isinstance(after[key], (int, float)):
                    impact[key] = {
                        "change": after[key] - before[key],
                        "percent_change": ((after[key] - before[key]) / before[key] * 100) if before[key] != 0 else 0
                    }
        return impact
        
    def get_subsystem_performance(self, subsystem: str) -> Dict:
        """Get performance history for a specific subsystem."""
        return self.performance_history.get(subsystem, [])
        
    def get_recent_improvements(self, hours: int = 24) -> List:
        """Get improvements from the last N hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [imp for imp in self.improvements 
                if datetime.fromisoformat(imp["timestamp"]) > cutoff]


class ImprovementStrategy(ABC):
    """Abstract base class for improvement strategies."""
    
    @abstractmethod
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze subsystem state and identify improvement opportunities."""
        pass
        
    @abstractmethod
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute improvements and return new state."""
        pass
        
    @abstractmethod
    def get_name(self) -> str:
        """Return strategy name."""
        pass


class SubsystemHook:
    """Hook for integrating subsystems with the improvement framework."""
    
    def __init__(self, name: str, get_state_func: Callable, 
                 improvement_strategies: List[ImprovementStrategy]):
        self.name = name
        self.get_state = get_state_func
        self.strategies = improvement_strategies
        self.enabled = True
        self.last_improvement = None
        
    def run_improvement_cycle(self) -> Dict:
        """Run a complete improvement cycle for this subsystem."""
        if not self.enabled:
            return {"status": "disabled", "subsystem": self.name}
            
        try:
            # Get current state
            current_state = self.get_state()
            
            # Run each strategy
            results = []
            final_state = current_state.copy()
            
            for strategy in self.strategies:
                # Analyze for opportunities
                opportunities = strategy.analyze(final_state)
                
                if opportunities.get("improvements_available", False):
                    # Execute improvements
                    improved_state = strategy.improve(final_state, opportunities)
                    
                    results.append({
                        "strategy": strategy.get_name(),
                        "opportunities": opportunities,
                        "before_state": final_state.copy(),
                        "after_state": improved_state,
                        "success": True
                    })
                    
                    final_state = improved_state
                else:
                    results.append({
                        "strategy": strategy.get_name(),
                        "opportunities": opportunities,
                        "before_state": final_state.copy(),
                        "after_state": final_state,
                        "success": True,
                        "note": "No improvements needed"
                    })
            
            self.last_improvement = datetime.now()
            
            return {
                "status": "success",
                "subsystem": self.name,
                "timestamp": datetime.now().isoformat(),
                "initial_state": current_state,
                "final_state": final_state,
                "improvements": results
            }
            
        except Exception as e:
            logging.error(f"Error during improvement cycle for {self.name}: {e}")
            return {
                "status": "error",
                "subsystem": self.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


class RecursiveImprovementFramework:
    """Main framework for recursive autonomous improvement."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.subsystem_hooks = {}
        self.metrics = ImprovementMetrics()
        self.autonomous_mode = False
        self.scheduler_thread = None
        self.logger = self._setup_logging()
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults."""
        default_config = {
            "autonomous": {
                "enabled": True,
                "interval_minutes": 60,
                "max_concurrent_improvements": 3
            },
            "logging": {
                "level": "INFO",
                "file": "recursive_improvement.log"
            },
            "subsystems": {
                "agents": {"enabled": True, "priority": 1},
                "dags": {"enabled": True, "priority": 2},
                "capsules": {"enabled": True, "priority": 3},
                "ethics": {"enabled": True, "priority": 1},
                "ml": {"enabled": True, "priority": 2}
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                # Merge with defaults
                default_config.update(loaded_config)
            except Exception as e:
                logging.warning(f"Could not load config from {config_path}: {e}")
                
        return default_config
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the framework."""
        logger = logging.getLogger("recursive_improvement")
        logger.setLevel(getattr(logging, self.config["logging"]["level"]))
        
        handler = logging.FileHandler(self.config["logging"]["file"])
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    def register_subsystem(self, hook: SubsystemHook) -> None:
        """Register a subsystem with the improvement framework."""
        self.subsystem_hooks[hook.name] = hook
        self.logger.info(f"Registered subsystem: {hook.name}")
        
    def unregister_subsystem(self, name: str) -> None:
        """Unregister a subsystem."""
        if name in self.subsystem_hooks:
            del self.subsystem_hooks[name]
            self.logger.info(f"Unregistered subsystem: {name}")
            
    def enable_subsystem(self, name: str) -> None:
        """Enable improvement for a subsystem."""
        if name in self.subsystem_hooks:
            self.subsystem_hooks[name].enabled = True
            self.logger.info(f"Enabled subsystem: {name}")
            
    def disable_subsystem(self, name: str) -> None:
        """Disable improvement for a subsystem."""
        if name in self.subsystem_hooks:
            self.subsystem_hooks[name].enabled = False
            self.logger.info(f"Disabled subsystem: {name}")
            
    def run_manual_improvement(self, subsystem_name: Optional[str] = None) -> Dict:
        """Manually trigger improvement cycle(s)."""
        if subsystem_name:
            # Run improvement for specific subsystem
            if subsystem_name not in self.subsystem_hooks:
                return {"status": "error", "message": f"Subsystem '{subsystem_name}' not registered"}
                
            hook = self.subsystem_hooks[subsystem_name]
            result = hook.run_improvement_cycle()
            
            # Record metrics
            if result["status"] == "success" and "improvements" in result:
                for improvement in result["improvements"]:
                    self.metrics.record_improvement(
                        subsystem_name,
                        improvement["strategy"],
                        improvement["before_state"],
                        improvement["after_state"],
                        improvement["success"]
                    )
                    
            return result
        else:
            # Run improvement for all enabled subsystems
            results = {}
            for name, hook in self.subsystem_hooks.items():
                if hook.enabled:
                    results[name] = self.run_manual_improvement(name)
                    
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "subsystem_results": results,
                "total_subsystems": len(results)
            }
            
    def start_autonomous_mode(self) -> None:
        """Start autonomous improvement scheduling."""
        if self.autonomous_mode:
            self.logger.warning("Autonomous mode already running")
            return
            
        if not self.config["autonomous"]["enabled"]:
            self.logger.warning("Autonomous mode disabled in configuration")
            return
            
        self.autonomous_mode = True
        self.scheduler_thread = threading.Thread(target=self._autonomous_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.logger.info("Started autonomous improvement mode")
        
    def stop_autonomous_mode(self) -> None:
        """Stop autonomous improvement scheduling."""
        self.autonomous_mode = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
            self.scheduler_thread = None
            
        self.logger.info("Stopped autonomous improvement mode")
        
    def _autonomous_scheduler(self) -> None:
        """Main autonomous scheduling loop."""
        interval = self.config["autonomous"]["interval_minutes"] * 60
        
        while self.autonomous_mode:
            try:
                self.logger.info("Running autonomous improvement cycle")
                result = self.run_manual_improvement()
                
                if result["status"] == "success":
                    success_count = sum(1 for r in result["subsystem_results"].values() 
                                      if r["status"] == "success")
                    self.logger.info(f"Autonomous cycle completed: {success_count} subsystems improved")
                else:
                    self.logger.error(f"Autonomous cycle failed: {result}")
                    
            except Exception as e:
                self.logger.error(f"Error in autonomous scheduler: {e}")
                
            # Sleep for the configured interval
            time.sleep(interval)
            
    def get_status(self) -> Dict:
        """Get comprehensive framework status."""
        return {
            "autonomous_mode": self.autonomous_mode,
            "registered_subsystems": {
                name: {
                    "enabled": hook.enabled,
                    "last_improvement": hook.last_improvement.isoformat() if hook.last_improvement else None,
                    "strategies": [s.get_name() for s in hook.strategies]
                }
                for name, hook in self.subsystem_hooks.items()
            },
            "recent_improvements": self.metrics.get_recent_improvements(24),
            "total_improvements": len(self.metrics.improvements),
            "configuration": self.config,
            "timestamp": datetime.now().isoformat()
        }
        
    def get_metrics(self) -> ImprovementMetrics:
        """Get metrics object for detailed analysis."""
        return self.metrics
        
    def export_metrics(self, filepath: str) -> None:
        """Export metrics to a file."""
        metrics_data = {
            "improvements": self.metrics.improvements,
            "performance_history": self.metrics.performance_history,
            "export_timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)
            
        self.logger.info(f"Metrics exported to {filepath}")


# Global framework instance
_framework_instance = None


def get_framework(config_path: Optional[str] = None) -> RecursiveImprovementFramework:
    """Get or create the global framework instance."""
    global _framework_instance
    if _framework_instance is None:
        _framework_instance = RecursiveImprovementFramework(config_path)
    return _framework_instance


def initialize_framework(config_path: Optional[str] = None) -> RecursiveImprovementFramework:
    """Initialize and return the framework instance."""
    return get_framework(config_path)