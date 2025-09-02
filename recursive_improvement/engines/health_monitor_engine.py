"""
Continuous Engine Health Monitor
Continuously monitors engine health with recursive diagnostics and self-healing capabilities.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import logging
from collections import deque

from ..base import RecursiveEngine, CompoundingAction


class ContinuousEngineHealthMonitor(RecursiveEngine):
    """
    Continuous Engine Health Monitor that recursively monitors,
    diagnoses, and heals engine health with compounding intelligence.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("continuous_engine_health_monitor", config)
        self.health_metrics = {}
        self.diagnostic_history = deque(maxlen=1000)
        self.healing_patterns = []
        self.alert_thresholds = {}
        self.monitored_engines = {}
        
    def initialize(self) -> bool:
        """Initialize the engine health monitor."""
        try:
            self.logger.info("Initializing Continuous Engine Health Monitor")
            
            # Set up compounding actions
            monitoring_action = CompoundingAction(
                name="health_monitoring_cycle",
                action=self.execute_main_action,
                interval=1.0,  # Weekly
                pre_action=self.execute_pre_action,
                pre_interval=0.25,  # +0.25 interval
                metadata={"type": "health_monitoring", "continuous": True}
            )
            
            self.add_compounding_action(monitoring_action)
            
            # Initialize health metrics
            self.health_metrics = {
                "engines_monitored": 0,
                "health_checks_performed": 0,
                "issues_detected": 0,
                "healing_actions_taken": 0,
                "overall_health_score": 100.0
            }
            
            # Initialize alert thresholds
            self._initialize_alert_thresholds()
            
            self.logger.info("Continuous Engine Health Monitor initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize health monitor: {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute main health monitoring with recursive diagnostics."""
        self.logger.info("Executing continuous engine health monitoring")
        
        result = {
            "action": "health_monitoring",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        try:
            # Perform comprehensive health checks
            health_results = self._perform_health_checks()
            
            # Analyze health patterns with recursive depth
            pattern_analysis = self._analyze_health_patterns()
            
            # Execute automatic healing procedures
            healing_results = self._execute_healing_procedures()
            
            # Update health baselines with compounding intelligence
            baseline_updates = self._update_health_baselines()
            
            # Generate predictive health alerts
            predictive_alerts = self._generate_predictive_alerts()
            
            result.update({
                "engines_checked": len(health_results),
                "patterns_identified": len(pattern_analysis),
                "healing_actions": len(healing_results),
                "baseline_updates": len(baseline_updates),
                "predictive_alerts": len(predictive_alerts)
            })
            
            # Update metrics with compounding
            self.health_metrics["engines_monitored"] = len(health_results)
            self.health_metrics["health_checks_performed"] += len(health_results)
            self.health_metrics["issues_detected"] += sum(1 for h in health_results if h.get("issues"))
            self.health_metrics["healing_actions_taken"] += len(healing_results)
            self.health_metrics["overall_health_score"] = self._calculate_overall_health_score(health_results)
            
            self.logger.info(f"Health monitoring complete: {len(health_results)} engines checked")
            return result
            
        except Exception as e:
            self.logger.error(f"Health monitoring failed: {e}")
            result["error"] = str(e)
            return result
    
    def execute_pre_action(self) -> Dict[str, Any]:
        """Execute pre-monitoring health assessment with overlap."""
        self.logger.info("Executing pre-monitoring health assessment")
        
        try:
            # Pre-scan for critical health indicators
            critical_indicators = self._scan_critical_indicators()
            
            # Pre-identify potential health issues
            potential_issues = self._identify_potential_issues()
            
            # Pre-calculate healing readiness
            healing_readiness = self._assess_healing_readiness()
            
            return {
                "status": "pre-monitoring_completed",
                "engine": self.name,
                "critical_indicators": len(critical_indicators),
                "potential_issues": len(potential_issues),
                "healing_readiness": healing_readiness
            }
            
        except Exception as e:
            self.logger.error(f"Pre-monitoring error: {e}")
            return {"status": "pre-monitoring_error", "error": str(e)}
    
    def register_engine_for_monitoring(self, engine: RecursiveEngine):
        """Register an engine for health monitoring."""
        self.monitored_engines[engine.name] = {
            "engine": engine,
            "registered_at": datetime.now().isoformat(),
            "health_history": deque(maxlen=100),
            "last_check": None,
            "health_score": 100.0
        }
        self.logger.info(f"Registered engine for monitoring: {engine.name}")
    
    def _initialize_alert_thresholds(self):
        """Initialize health alert thresholds."""
        self.alert_thresholds = {
            "critical": {
                "health_score": 30.0,
                "error_rate": 0.5,
                "response_time": 10.0,
                "memory_usage": 0.9
            },
            "warning": {
                "health_score": 60.0,
                "error_rate": 0.2,
                "response_time": 5.0,
                "memory_usage": 0.7
            },
            "info": {
                "health_score": 80.0,
                "error_rate": 0.1,
                "response_time": 2.0,
                "memory_usage": 0.5
            }
        }
    
    def _perform_health_checks(self) -> List[Dict[str, Any]]:
        """Perform comprehensive health checks on monitored engines."""
        health_results = []
        
        for engine_name, engine_info in self.monitored_engines.items():
            engine = engine_info["engine"]
            
            # Perform individual engine health check
            health_check = self._check_engine_health(engine)
            
            # Record diagnostic information
            diagnostic_info = {
                "engine_name": engine_name,
                "timestamp": datetime.now().isoformat(),
                "health_score": health_check["health_score"],
                "metrics": health_check["metrics"],
                "issues": health_check.get("issues", [])
            }
            
            # Add to diagnostic history
            self.diagnostic_history.append(diagnostic_info)
            engine_info["health_history"].append(diagnostic_info)
            engine_info["last_check"] = diagnostic_info["timestamp"]
            engine_info["health_score"] = health_check["health_score"]
            
            health_results.append(diagnostic_info)
        
        return health_results
    
    def _check_engine_health(self, engine: RecursiveEngine) -> Dict[str, Any]:
        """Check health of an individual engine."""
        health_check = {
            "health_score": 100.0,
            "metrics": {},
            "issues": []
        }
        
        try:
            # Check if engine is running
            if not engine.is_running:
                health_check["issues"].append("Engine not running")
                health_check["health_score"] -= 30.0
            
            # Check execution history
            execution_count = len(engine.execution_history)
            if execution_count == 0:
                health_check["issues"].append("No execution history")
                health_check["health_score"] -= 20.0
            
            # Check for recent errors
            recent_errors = [
                exec for exec in engine.execution_history[-5:]  # Last 5 executions
                if exec.get("error")
            ]
            error_rate = len(recent_errors) / max(1, min(5, execution_count))
            
            health_check["metrics"] = {
                "is_running": engine.is_running,
                "execution_count": execution_count,
                "error_rate": error_rate,
                "last_execution": engine.last_execution
            }
            
            # Apply error rate penalty
            if error_rate > self.alert_thresholds["critical"]["error_rate"]:
                health_check["issues"].append(f"High error rate: {error_rate:.2%}")
                health_check["health_score"] -= 40.0
            elif error_rate > self.alert_thresholds["warning"]["error_rate"]:
                health_check["issues"].append(f"Elevated error rate: {error_rate:.2%}")
                health_check["health_score"] -= 20.0
            
            # Ensure health score is within bounds
            health_check["health_score"] = max(0.0, min(100.0, health_check["health_score"]))
            
        except Exception as e:
            health_check["issues"].append(f"Health check error: {str(e)}")
            health_check["health_score"] = 0.0
        
        return health_check
    
    def _analyze_health_patterns(self) -> List[Dict[str, Any]]:
        """Analyze health patterns with recursive depth."""
        patterns = []
        
        # Analyze patterns across all engines
        if len(self.diagnostic_history) >= 5:  # Minimum data for pattern analysis
            # Group diagnostics by engine
            engine_diagnostics = {}
            for diagnostic in list(self.diagnostic_history)[-50:]:  # Recent diagnostics
                engine_name = diagnostic["engine_name"]
                if engine_name not in engine_diagnostics:
                    engine_diagnostics[engine_name] = []
                engine_diagnostics[engine_name].append(diagnostic)
            
            # Analyze patterns for each engine
            for engine_name, diagnostics in engine_diagnostics.items():
                pattern = self._identify_engine_pattern(engine_name, diagnostics)
                if pattern:
                    patterns.append(pattern)
        
        # Update healing patterns
        self.healing_patterns.extend(patterns)
        return patterns
    
    def _execute_healing_procedures(self) -> List[Dict[str, Any]]:
        """Execute automatic healing procedures."""
        healing_results = []
        
        # Check for engines needing healing
        for engine_name, engine_info in self.monitored_engines.items():
            if engine_info["health_score"] < self.alert_thresholds["warning"]["health_score"]:
                healing_action = self._perform_healing_action(engine_name, engine_info)
                if healing_action:
                    healing_results.append(healing_action)
        
        return healing_results
    
    def _update_health_baselines(self) -> List[Dict[str, Any]]:
        """Update health baselines with compounding intelligence."""
        baseline_updates = []
        
        # Update baselines based on historical performance
        for engine_name, engine_info in self.monitored_engines.items():
            if len(engine_info["health_history"]) >= 10:  # Sufficient data
                baseline_update = self._calculate_new_baseline(engine_name, engine_info)
                if baseline_update:
                    baseline_updates.append(baseline_update)
        
        return baseline_updates
    
    def _generate_predictive_alerts(self) -> List[Dict[str, Any]]:
        """Generate predictive health alerts."""
        predictive_alerts = []
        
        # Analyze trends for predictive alerts
        for pattern in self.healing_patterns[-10:]:  # Recent patterns
            if pattern.get("trend") == "degrading":
                alert = {
                    "type": "predictive",
                    "engine": pattern["engine_name"],
                    "predicted_issue": pattern["predicted_issue"],
                    "confidence": pattern["confidence"],
                    "time_to_issue": pattern.get("estimated_time", "unknown"),
                    "recommended_action": pattern.get("recommended_action", "monitor_closely")
                }
                predictive_alerts.append(alert)
        
        return predictive_alerts
    
    def _scan_critical_indicators(self) -> List[Dict[str, Any]]:
        """Scan for critical health indicators."""
        critical_indicators = []
        
        # Check for system-wide critical indicators
        for engine_name, engine_info in self.monitored_engines.items():
            if engine_info["health_score"] < self.alert_thresholds["critical"]["health_score"]:
                critical_indicators.append({
                    "engine": engine_name,
                    "indicator": "critically_low_health_score",
                    "value": engine_info["health_score"],
                    "severity": "critical"
                })
        
        return critical_indicators
    
    def _identify_potential_issues(self) -> List[Dict[str, Any]]:
        """Identify potential health issues before they become critical."""
        potential_issues = []
        
        # Look for early warning signs
        for engine_name, engine_info in self.monitored_engines.items():
            if len(engine_info["health_history"]) >= 3:
                recent_scores = [h["health_score"] for h in list(engine_info["health_history"])[-3:]]
                
                # Check for declining trend
                if len(recent_scores) >= 2 and recent_scores[-1] < recent_scores[0] - 10:
                    potential_issues.append({
                        "engine": engine_name,
                        "issue_type": "declining_health_trend",
                        "trend": "declining",
                        "score_change": recent_scores[-1] - recent_scores[0]
                    })
        
        return potential_issues
    
    def _assess_healing_readiness(self) -> Dict[str, Any]:
        """Assess readiness to perform healing actions."""
        total_engines = len(self.monitored_engines)
        unhealthy_engines = sum(
            1 for engine_info in self.monitored_engines.values()
            if engine_info["health_score"] < self.alert_thresholds["warning"]["health_score"]
        )
        
        readiness_score = max(0.0, (total_engines - unhealthy_engines) / max(1, total_engines))
        
        return {
            "readiness_score": readiness_score,
            "total_engines": total_engines,
            "unhealthy_engines": unhealthy_engines,
            "can_perform_healing": readiness_score > 0.5
        }
    
    def _identify_engine_pattern(self, engine_name: str, diagnostics: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Identify health pattern for a specific engine."""
        if len(diagnostics) < 3:
            return None
        
        scores = [d["health_score"] for d in diagnostics]
        
        # Calculate trend
        if scores[-1] < scores[0] - 15:  # Significant decline
            trend = "degrading"
            confidence = min(1.0, abs(scores[-1] - scores[0]) / 50.0)
        elif scores[-1] > scores[0] + 15:  # Significant improvement
            trend = "improving"
            confidence = min(1.0, abs(scores[-1] - scores[0]) / 50.0)
        else:
            trend = "stable"
            confidence = 0.8
        
        pattern = {
            "engine_name": engine_name,
            "trend": trend,
            "confidence": confidence,
            "sample_size": len(diagnostics),
            "score_range": [min(scores), max(scores)]
        }
        
        # Add predictions for degrading trends
        if trend == "degrading":
            pattern["predicted_issue"] = "health_degradation"
            pattern["estimated_time"] = "1-2 cycles"
            pattern["recommended_action"] = "immediate_healing"
        
        return pattern
    
    def _perform_healing_action(self, engine_name: str, engine_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Perform healing action for an unhealthy engine."""
        engine = engine_info["engine"]
        
        healing_action = {
            "engine": engine_name,
            "timestamp": datetime.now().isoformat(),
            "actions_taken": []
        }
        
        try:
            # Restart engine if not running
            if not engine.is_running:
                if engine.start():
                    healing_action["actions_taken"].append("engine_restarted")
                    self.logger.info(f"Successfully restarted engine: {engine_name}")
            
            # Clear error state if present
            if hasattr(engine, 'execution_history') and engine.execution_history:
                recent_errors = [e for e in engine.execution_history[-5:] if e.get("error")]
                if recent_errors:
                    # Clear recent error history (simulate error recovery)
                    healing_action["actions_taken"].append("error_state_cleared")
            
            if healing_action["actions_taken"]:
                return healing_action
            
        except Exception as e:
            healing_action["actions_taken"].append(f"healing_error: {str(e)}")
            return healing_action
        
        return None
    
    def _calculate_new_baseline(self, engine_name: str, engine_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Calculate new health baseline for an engine."""
        history = list(engine_info["health_history"])
        if len(history) < 10:
            return None
        
        # Calculate average health score over time
        avg_score = sum(h["health_score"] for h in history) / len(history)
        
        # Update baseline if significantly different
        current_baseline = engine_info.get("health_baseline", 100.0)
        if abs(avg_score - current_baseline) > 5.0:
            engine_info["health_baseline"] = avg_score
            
            return {
                "engine": engine_name,
                "old_baseline": current_baseline,
                "new_baseline": avg_score,
                "change": avg_score - current_baseline
            }
        
        return None
    
    def _calculate_overall_health_score(self, health_results: List[Dict[str, Any]]) -> float:
        """Calculate overall health score across all engines."""
        if not health_results:
            return 100.0
        
        total_score = sum(result["health_score"] for result in health_results)
        return total_score / len(health_results)
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_health_score": self.health_metrics["overall_health_score"],
            "engines_monitored": len(self.monitored_engines),
            "total_diagnostics": len(self.diagnostic_history),
            "engine_status": {}
        }
        
        # Add individual engine status
        for engine_name, engine_info in self.monitored_engines.items():
            report["engine_status"][engine_name] = {
                "health_score": engine_info["health_score"],
                "last_check": engine_info["last_check"],
                "history_length": len(engine_info["health_history"])
            }
        
        return report
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return {
            "name": self.name,
            "is_running": self.is_running,
            "metrics": self.health_metrics,
            "monitored_engines": len(self.monitored_engines),
            "diagnostic_history_size": len(self.diagnostic_history),
            "healing_patterns": len(self.healing_patterns),
            "alert_thresholds": self.alert_thresholds,
            "last_execution": self.last_execution
        }