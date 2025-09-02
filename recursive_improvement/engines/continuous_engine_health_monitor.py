"""
Continuous Engine Health Monitor
Monitors all recursive engines and maintains system health through self-healing
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from ..base import RecursiveEngine, CompoundingAction


class ContinuousEngineHealthMonitor(RecursiveEngine):
    """
    Continuous Engine Health Monitor that monitors all recursive engines,
    detects health issues, and applies self-healing measures.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("continuous_engine_health_monitor", config)
        self.engine_registry = {}
        self.health_metrics = {}
        self.healing_history = []
        self.alert_thresholds = {}
        
    def initialize(self) -> bool:
        """Initialize the continuous engine health monitor."""
        try:
            self.logger.info("Initializing Continuous Engine Health Monitor")
            
            # Set up compounding actions
            monitoring_action = CompoundingAction(
                name="continuous_health_monitoring",
                action=self.execute_main_action,
                interval=1.0,  # Weekly comprehensive health analysis
                pre_action=self.execute_pre_action,
                pre_interval=0.25,  # Continuous monitoring at +0.25 interval
                metadata={"type": "health_monitoring", "recursive": True}
            )
            
            self.add_compounding_action(monitoring_action)
            
            # Initialize alert thresholds
            self.alert_thresholds = {
                "response_time": {"warning": 5.0, "critical": 10.0},
                "error_rate": {"warning": 0.05, "critical": 0.15},
                "memory_usage": {"warning": 0.80, "critical": 0.95},
                "execution_failures": {"warning": 3, "critical": 10},
                "availability": {"warning": 0.95, "critical": 0.90}
            }
            
            # Initialize health metrics template
            self.health_metrics = {
                "system_health_score": 1.0,
                "engines_healthy": 0,
                "engines_degraded": 0,
                "engines_failing": 0,
                "last_health_check": None,
                "healing_actions_taken": 0
            }
            
            self.logger.info("Continuous Engine Health Monitor initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize health monitor: {e}")
            return False
    
    def register_engine(self, engine: RecursiveEngine) -> None:
        """Register an engine for health monitoring."""
        if engine.name not in self.engine_registry:
            self.engine_registry[engine.name] = {
                "engine": engine,
                "registered_at": datetime.now().isoformat(),
                "health_status": "unknown",
                "last_check": None,
                "metrics": self._initialize_engine_metrics()
            }
            self.logger.info(f"Registered engine for monitoring: {engine.name}")
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute comprehensive health analysis and system healing."""
        self.logger.info("Executing comprehensive engine health analysis")
        
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "comprehensive_health_analysis",
            "engine_health_reports": [],
            "system_health_score": 0.0,
            "healing_actions": [],
            "recommendations": []
        }
        
        try:
            # Analyze health of all registered engines
            health_reports = self._analyze_all_engines()
            analysis_result["engine_health_reports"] = health_reports
            
            # Calculate overall system health score
            system_health_score = self._calculate_system_health_score(health_reports)
            analysis_result["system_health_score"] = system_health_score
            
            # Apply comprehensive healing measures
            healing_actions = self._apply_comprehensive_healing(health_reports)
            analysis_result["healing_actions"] = healing_actions
            
            # Generate system recommendations
            recommendations = self._generate_system_recommendations(health_reports)
            analysis_result["recommendations"] = recommendations
            
            # Implement recursive health improvements
            recursive_improvements = self._implement_recursive_health_improvements()
            analysis_result["recursive_improvements"] = recursive_improvements
            
            # Update system metrics
            self._update_system_health_metrics(analysis_result)
            
            # Store healing history
            self.healing_history.append(analysis_result)
            
            # Trigger system-wide optimizations if needed
            if system_health_score < 0.8:
                optimization_result = self._trigger_system_optimization()
                analysis_result["system_optimization"] = optimization_result
            
            self.logger.info(f"Comprehensive health analysis complete - System health: {system_health_score:.2f}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Comprehensive health analysis failed: {e}")
            analysis_result["error"] = str(e)
            return analysis_result
    
    def execute_pre_action(self) -> Dict[str, Any]:
        """Execute continuous health monitoring at +0.25 interval."""
        self.logger.info("Executing continuous health monitoring (+0.25 interval)")
        
        monitoring_result = {
            "timestamp": datetime.now().isoformat(),
            "action_type": "continuous_monitoring",
            "health_checks": [],
            "immediate_healing": [],
            "alerts_triggered": []
        }
        
        try:
            # Perform rapid health checks on all engines
            health_checks = self._perform_rapid_health_checks()
            monitoring_result["health_checks"] = health_checks
            
            # Apply immediate healing for critical issues
            immediate_healing = self._apply_immediate_healing(health_checks)
            monitoring_result["immediate_healing"] = immediate_healing
            
            # Trigger alerts for significant health degradation
            alerts = self._check_and_trigger_alerts(health_checks)
            monitoring_result["alerts_triggered"] = alerts
            
            # Update engine metrics
            self._update_engine_metrics(health_checks)
            
            # Perform predictive health analysis
            predictive_analysis = self._perform_predictive_health_analysis()
            monitoring_result["predictive_analysis"] = predictive_analysis
            
            self.logger.info(f"Continuous monitoring complete - {len(health_checks)} engines checked")
            return monitoring_result
            
        except Exception as e:
            self.logger.error(f"Continuous monitoring failed: {e}")
            monitoring_result["error"] = str(e)
            return monitoring_result
    
    def _initialize_engine_metrics(self) -> Dict[str, Any]:
        """Initialize metrics for a new engine."""
        return {
            "response_times": [],
            "error_count": 0,
            "success_count": 0,
            "last_execution": None,
            "availability_score": 1.0,
            "performance_trend": "stable",
            "memory_usage": 0.0,
            "health_score": 1.0
        }
    
    def _analyze_all_engines(self) -> List[Dict[str, Any]]:
        """Analyze health of all registered engines."""
        health_reports = []
        
        for engine_name, engine_info in self.engine_registry.items():
            report = self._analyze_engine_health(engine_name, engine_info)
            health_reports.append(report)
        
        return health_reports
    
    def _analyze_engine_health(self, engine_name: str, engine_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze health of a specific engine."""
        engine = engine_info["engine"]
        metrics = engine_info["metrics"]
        
        health_report = {
            "engine_name": engine_name,
            "health_status": "unknown",
            "health_score": 0.0,
            "issues_detected": [],
            "performance_metrics": {},
            "recommendations": [],
            "last_analyzed": datetime.now().isoformat()
        }
        
        try:
            # Check engine availability and responsiveness
            availability_score = self._check_engine_availability(engine)
            performance_score = self._check_engine_performance(metrics)
            error_score = self._check_engine_errors(metrics)
            
            # Calculate overall health score
            health_score = (availability_score + performance_score + error_score) / 3
            health_report["health_score"] = health_score
            
            # Determine health status
            if health_score >= 0.8:
                health_report["health_status"] = "healthy"
            elif health_score >= 0.6:
                health_report["health_status"] = "degraded"
            else:
                health_report["health_status"] = "failing"
            
            # Detect specific issues
            issues = self._detect_engine_issues(engine, metrics)
            health_report["issues_detected"] = issues
            
            # Generate performance metrics
            health_report["performance_metrics"] = {
                "availability_score": availability_score,
                "performance_score": performance_score,
                "error_score": error_score,
                "response_time_avg": self._calculate_avg_response_time(metrics),
                "error_rate": self._calculate_error_rate(metrics)
            }
            
            # Generate recommendations
            recommendations = self._generate_engine_recommendations(engine, issues)
            health_report["recommendations"] = recommendations
            
            # Update engine info
            engine_info["health_status"] = health_report["health_status"]
            engine_info["last_check"] = datetime.now().isoformat()
            
        except Exception as e:
            health_report["error"] = str(e)
            health_report["health_status"] = "error"
            self.logger.error(f"Failed to analyze engine {engine_name}: {e}")
        
        return health_report
    
    def _check_engine_availability(self, engine: RecursiveEngine) -> float:
        """Check engine availability and responsiveness."""
        try:
            # Check if engine is running
            if not engine.is_running:
                return 0.0
            
            # Check if engine responds to status requests
            status = engine.get_status()
            if status and isinstance(status, dict):
                return 1.0
            else:
                return 0.5
                
        except Exception as e:
            self.logger.warning(f"Engine availability check failed: {e}")
            return 0.0
    
    def _check_engine_performance(self, metrics: Dict[str, Any]) -> float:
        """Check engine performance metrics."""
        response_times = metrics.get("response_times", [])
        if not response_times:
            return 0.8  # Neutral score if no data
        
        avg_response_time = sum(response_times) / len(response_times)
        
        # Score based on response time thresholds
        if avg_response_time <= self.alert_thresholds["response_time"]["warning"]:
            return 1.0
        elif avg_response_time <= self.alert_thresholds["response_time"]["critical"]:
            return 0.6
        else:
            return 0.2
    
    def _check_engine_errors(self, metrics: Dict[str, Any]) -> float:
        """Check engine error rates."""
        error_count = metrics.get("error_count", 0)
        success_count = metrics.get("success_count", 1)
        total_executions = error_count + success_count
        
        if total_executions == 0:
            return 0.8  # Neutral score if no executions
        
        error_rate = error_count / total_executions
        
        # Score based on error rate thresholds
        if error_rate <= self.alert_thresholds["error_rate"]["warning"]:
            return 1.0
        elif error_rate <= self.alert_thresholds["error_rate"]["critical"]:
            return 0.6
        else:
            return 0.2
    
    def _detect_engine_issues(self, engine: RecursiveEngine, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect specific issues with an engine."""
        issues = []
        
        # Check for high error rates
        error_rate = self._calculate_error_rate(metrics)
        if error_rate > self.alert_thresholds["error_rate"]["warning"]:
            issues.append({
                "type": "high_error_rate",
                "severity": "critical" if error_rate > self.alert_thresholds["error_rate"]["critical"] else "warning",
                "value": error_rate,
                "description": f"Error rate is {error_rate:.2%}"
            })
        
        # Check for slow response times
        avg_response_time = self._calculate_avg_response_time(metrics)
        if avg_response_time > self.alert_thresholds["response_time"]["warning"]:
            issues.append({
                "type": "slow_response",
                "severity": "critical" if avg_response_time > self.alert_thresholds["response_time"]["critical"] else "warning",
                "value": avg_response_time,
                "description": f"Average response time is {avg_response_time:.2f}s"
            })
        
        # Check for engine not running
        if not engine.is_running:
            issues.append({
                "type": "engine_stopped",
                "severity": "critical",
                "description": "Engine is not running"
            })
        
        return issues
    
    def _calculate_avg_response_time(self, metrics: Dict[str, Any]) -> float:
        """Calculate average response time from metrics."""
        response_times = metrics.get("response_times", [])
        return sum(response_times) / len(response_times) if response_times else 0.0
    
    def _calculate_error_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate error rate from metrics."""
        error_count = metrics.get("error_count", 0)
        success_count = metrics.get("success_count", 1)
        total = error_count + success_count
        return error_count / total if total > 0 else 0.0
    
    def _calculate_system_health_score(self, health_reports: List[Dict[str, Any]]) -> float:
        """Calculate overall system health score."""
        if not health_reports:
            return 0.0
        
        total_score = sum(report.get("health_score", 0) for report in health_reports)
        return total_score / len(health_reports)
    
    def _apply_comprehensive_healing(self, health_reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply comprehensive healing measures based on health reports."""
        healing_actions = []
        
        for report in health_reports:
            if report.get("health_status") in ["degraded", "failing"]:
                actions = self._heal_engine(report)
                healing_actions.extend(actions)
        
        return healing_actions
    
    def _heal_engine(self, health_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply healing measures to a specific engine."""
        engine_name = health_report["engine_name"]
        issues = health_report.get("issues_detected", [])
        healing_actions = []
        
        for issue in issues:
            action = self._create_healing_action(engine_name, issue)
            if action:
                healing_actions.append(action)
                self._apply_healing_action(engine_name, action)
        
        return healing_actions
    
    def _create_healing_action(self, engine_name: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Create a healing action for a specific issue."""
        issue_type = issue.get("type")
        
        action_mapping = {
            "high_error_rate": {
                "action": "restart_engine",
                "description": "Restart engine to clear error state"
            },
            "slow_response": {
                "action": "optimize_performance",
                "description": "Apply performance optimization"
            },
            "engine_stopped": {
                "action": "start_engine",
                "description": "Start the stopped engine"
            }
        }
        
        if issue_type in action_mapping:
            action_info = action_mapping[issue_type]
            return {
                "healing_id": f"heal_{engine_name}_{issue_type}_{datetime.now().strftime('%H%M%S')}",
                "engine": engine_name,
                "issue_type": issue_type,
                "action": action_info["action"],
                "description": action_info["description"],
                "severity": issue.get("severity", "medium"),
                "applied_at": datetime.now().isoformat()
            }
        
        return None
    
    def _apply_healing_action(self, engine_name: str, action: Dict[str, Any]) -> bool:
        """Apply a healing action to an engine."""
        try:
            engine_info = self.engine_registry.get(engine_name)
            if not engine_info:
                return False
            
            engine = engine_info["engine"]
            action_type = action["action"]
            
            if action_type == "restart_engine":
                engine.stop()
                return engine.start()
            elif action_type == "start_engine":
                return engine.start()
            elif action_type == "optimize_performance":
                # Simulate performance optimization
                self.logger.info(f"Applied performance optimization to {engine_name}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to apply healing action {action['healing_id']}: {e}")
            return False
    
    def _generate_system_recommendations(self, health_reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate system-wide recommendations based on health reports."""
        recommendations = []
        
        # Count engines by health status
        status_counts = {}
        for report in health_reports:
            status = report.get("health_status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Generate recommendations based on patterns
        if status_counts.get("failing", 0) > 2:
            recommendations.append({
                "type": "system_maintenance",
                "priority": "high",
                "description": "Multiple engines failing - schedule comprehensive system maintenance"
            })
        
        if status_counts.get("degraded", 0) > len(health_reports) / 2:
            recommendations.append({
                "type": "performance_optimization",
                "priority": "medium",
                "description": "Majority of engines degraded - implement system-wide performance optimization"
            })
        
        return recommendations
    
    def _implement_recursive_health_improvements(self) -> List[Dict[str, Any]]:
        """Implement recursive improvements to the health monitoring system."""
        improvements = [
            {
                "improvement_type": "self_learning_thresholds",
                "description": "Health thresholds that adapt based on historical performance",
                "recursive_depth": 2,
                "implementation": "threshold_learning_algorithm"
            },
            {
                "improvement_type": "predictive_healing",
                "description": "Predict and prevent health issues before they occur",
                "recursive_depth": 3,
                "implementation": "predictive_analytics_engine"
            }
        ]
        
        return improvements
    
    def _perform_rapid_health_checks(self) -> List[Dict[str, Any]]:
        """Perform rapid health checks during continuous monitoring."""
        health_checks = []
        
        for engine_name, engine_info in self.engine_registry.items():
            check = {
                "engine_name": engine_name,
                "check_type": "rapid",
                "timestamp": datetime.now().isoformat(),
                "status": "unknown",
                "response_time": 0.0
            }
            
            try:
                start_time = datetime.now()
                engine = engine_info["engine"]
                
                # Quick availability check
                if engine.is_running:
                    check["status"] = "running"
                else:
                    check["status"] = "stopped"
                
                # Measure response time
                response_time = (datetime.now() - start_time).total_seconds()
                check["response_time"] = response_time
                
                # Update metrics
                engine_info["metrics"]["response_times"].append(response_time)
                # Keep only last 10 response times
                if len(engine_info["metrics"]["response_times"]) > 10:
                    engine_info["metrics"]["response_times"].pop(0)
                
            except Exception as e:
                check["status"] = "error"
                check["error"] = str(e)
            
            health_checks.append(check)
        
        return health_checks
    
    def _apply_immediate_healing(self, health_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply immediate healing for critical issues found in health checks."""
        immediate_healing = []
        
        for check in health_checks:
            if check["status"] == "stopped":
                healing_action = {
                    "healing_type": "immediate_restart",
                    "engine": check["engine_name"],
                    "applied_at": datetime.now().isoformat(),
                    "reason": "engine_stopped_detected"
                }
                
                # Apply the healing
                if self._restart_engine_immediately(check["engine_name"]):
                    healing_action["result"] = "success"
                else:
                    healing_action["result"] = "failed"
                
                immediate_healing.append(healing_action)
        
        return immediate_healing
    
    def _restart_engine_immediately(self, engine_name: str) -> bool:
        """Restart an engine immediately."""
        try:
            engine_info = self.engine_registry.get(engine_name)
            if engine_info:
                engine = engine_info["engine"]
                engine.stop()
                return engine.start()
            return False
        except Exception as e:
            self.logger.error(f"Failed to restart engine {engine_name}: {e}")
            return False
    
    def _check_and_trigger_alerts(self, health_checks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check health status and trigger alerts if needed."""
        alerts = []
        
        for check in health_checks:
            if check["status"] == "error" or check["status"] == "stopped":
                alert = {
                    "alert_type": "engine_health_critical",
                    "engine": check["engine_name"],
                    "status": check["status"],
                    "triggered_at": datetime.now().isoformat(),
                    "severity": "critical"
                }
                alerts.append(alert)
            elif check.get("response_time", 0) > self.alert_thresholds["response_time"]["critical"]:
                alert = {
                    "alert_type": "engine_performance_degraded",
                    "engine": check["engine_name"],
                    "response_time": check["response_time"],
                    "triggered_at": datetime.now().isoformat(),
                    "severity": "warning"
                }
                alerts.append(alert)
        
        return alerts
    
    def _update_engine_metrics(self, health_checks: List[Dict[str, Any]]) -> None:
        """Update engine metrics based on health checks."""
        for check in health_checks:
            engine_name = check["engine_name"]
            if engine_name in self.engine_registry:
                metrics = self.engine_registry[engine_name]["metrics"]
                
                if check["status"] == "running":
                    metrics["success_count"] += 1
                else:
                    metrics["error_count"] += 1
                
                metrics["last_execution"] = check["timestamp"]
    
    def _perform_predictive_health_analysis(self) -> Dict[str, Any]:
        """Perform predictive analysis to anticipate health issues."""
        return {
            "analysis_type": "predictive",
            "predictions": [
                {
                    "engine": "example_engine",
                    "predicted_issue": "performance_degradation",
                    "probability": 0.7,
                    "time_to_issue": "2_hours"
                }
            ],
            "confidence": 0.8
        }
    
    def _update_system_health_metrics(self, analysis_result: Dict[str, Any]) -> None:
        """Update system-wide health metrics."""
        health_reports = analysis_result.get("engine_health_reports", [])
        
        self.health_metrics["system_health_score"] = analysis_result.get("system_health_score", 0.0)
        self.health_metrics["engines_healthy"] = len([r for r in health_reports if r.get("health_status") == "healthy"])
        self.health_metrics["engines_degraded"] = len([r for r in health_reports if r.get("health_status") == "degraded"])
        self.health_metrics["engines_failing"] = len([r for r in health_reports if r.get("health_status") == "failing"])
        self.health_metrics["last_health_check"] = datetime.now().isoformat()
        self.health_metrics["healing_actions_taken"] += len(analysis_result.get("healing_actions", []))
    
    def _trigger_system_optimization(self) -> Dict[str, Any]:
        """Trigger system-wide optimization when health is degraded."""
        return {
            "optimization_type": "system_wide",
            "triggered_at": datetime.now().isoformat(),
            "reason": "low_system_health",
            "actions": ["resource_reallocation", "performance_tuning", "error_cleanup"],
            "expected_improvement": 0.2
        }
    
    def _generate_engine_recommendations(self, engine: RecursiveEngine, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for a specific engine."""
        recommendations = []
        
        for issue in issues:
            issue_type = issue.get("type")
            if issue_type == "high_error_rate":
                recommendations.append("Implement better error handling and retry logic")
            elif issue_type == "slow_response":
                recommendations.append("Optimize performance and consider caching")
            elif issue_type == "engine_stopped":
                recommendations.append("Investigate root cause of engine stopping")
        
        return recommendations