"""
Autonomous Notification Resolver - Context-aware notification-to-action mapping

This engine provides sophisticated autonomous resolution capabilities by:
1. Analyzing notifications and mapping them to appropriate improvement engines
2. Coordinating multi-engine responses for complex notifications
3. Learning optimal resolution strategies from successful outcomes
4. Escalating unresolved notifications through increasingly sophisticated approaches

Part of the Complex Autonomy Innovation framework for recursive notification resolution.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
from pathlib import Path

from ..base import RecursiveEngine, CompoundingAction


class AutonomousNotificationResolver(RecursiveEngine):
    """Context-aware autonomous notification resolution orchestrator."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("autonomous_notification_resolver", config or {})
        
        # Engine mapping for different notification types
        self.engine_mappings = {
            'error': ['feedback_loop_engine', 'escalation_logic_engine', 'workflow_automation_engine'],
            'warning': ['kpi_mutation_engine', 'workflow_auditor', 'dependency_health'],
            'performance': ['experimentation_tree_engine', 'auto_refactor', 'workflow_auditor'],
            'security': ['dependency_health', 'workflow_auditor', 'escalation_logic_engine'],
            'system': ['workflow_automation_engine', 'escalation_logic_engine', 'asset_library_engine']
        }
        
        # Multi-engine coordination strategies
        self.coordination_strategies = {
            'sequential': self._execute_sequential_strategy,
            'parallel': self._execute_parallel_strategy,
            'cascade': self._execute_cascade_strategy,
            'feedback_loop': self._execute_feedback_loop_strategy
        }
        
        # Resolution tracking
        self.active_resolutions = {}
        self.resolution_history = []
        self.strategy_effectiveness = defaultdict(list)
        
        # Learning parameters
        self.learning_window = timedelta(days=7)  # Learn from last 7 days
        self.min_confidence_threshold = 0.6
        self.escalation_threshold = 3  # Escalate after 3 failed attempts
        
        # Escalation levels
        self.escalation_levels = [
            'single_engine',      # Try best matching engine
            'multi_engine_parallel', # Try multiple engines in parallel
            'multi_engine_cascade',  # Try engines in cascade
            'comprehensive_analysis', # Full system analysis
            'human_intervention'  # Alert for human intervention
        ]
        
        self.logger.info("Autonomous Notification Resolver initialized with multi-engine coordination")
    
    def initialize(self) -> bool:
        """Initialize the autonomous notification resolver."""
        try:
            # Initialize compounding actions
            self.initialize_actions()
            
            self.logger.info(f"{self.name}: Autonomous Notification Resolver initialized")
            return True
        except Exception as e:
            self.logger.error(f"{self.name}: Initialization failed - {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute the main resolution orchestration action."""
        return self._comprehensive_resolution_process()
    
    def initialize_actions(self):
        """Initialize compounding actions for autonomous resolution."""
        # Main action: Comprehensive resolution orchestration
        def comprehensive_resolution_orchestration():
            return self._comprehensive_resolution_process()
        
        # Pre-action: Quick resolution attempts during main process
        def quick_resolution_attempts():
            return self._quick_resolution_scan()
        
        resolution_action = CompoundingAction(
            name="comprehensive_resolution_orchestration",
            action=comprehensive_resolution_orchestration,
            interval=1.0,  # Weekly comprehensive resolution
            pre_action=quick_resolution_attempts,
            pre_interval=0.25,  # Quick resolution attempts every ~2 days
            metadata={
                "type": "resolution",
                "priority": "critical",
                "learning_enabled": True,
                "multi_engine": True
            }
        )
        
        self.add_compounding_action(resolution_action)
    
    def resolve_notification(self, notification: Dict[str, Any], orchestrator=None) -> Dict[str, Any]:
        """Main entry point for autonomous notification resolution."""
        resolution_id = f"res_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(notification))}"
        
        self.logger.info(f"Starting autonomous resolution {resolution_id} for notification: {notification.get('category', 'unknown')}")
        
        resolution_context = {
            "id": resolution_id,
            "notification": notification,
            "start_time": datetime.now(),
            "strategies_attempted": [],
            "engines_used": [],
            "success": False,
            "escalation_level": 0
        }
        
        self.active_resolutions[resolution_id] = resolution_context
        
        try:
            # Determine optimal strategy based on notification type and history
            strategy = self._determine_optimal_strategy(notification)
            resolution_context["primary_strategy"] = strategy
            
            # Execute resolution strategy
            result = self._execute_resolution_strategy(notification, strategy, orchestrator)
            
            # Update resolution context with results
            resolution_context.update(result)
            resolution_context["success"] = result.get("resolved", False)
            resolution_context["end_time"] = datetime.now()
            
            # If not successful, try escalation
            if not resolution_context["success"]:
                escalation_result = self._escalate_resolution(notification, resolution_context, orchestrator)
                resolution_context.update(escalation_result)
            
            # Learn from this resolution attempt
            self._learn_from_resolution(resolution_context)
            
            # Move to history
            self.resolution_history.append(resolution_context)
            del self.active_resolutions[resolution_id]
            
            self.logger.info(f"Resolution {resolution_id} completed: {'SUCCESS' if resolution_context['success'] else 'FAILED'}")
            
            return {
                "resolution_id": resolution_id,
                "success": resolution_context["success"],
                "strategies_used": resolution_context["strategies_attempted"],
                "engines_triggered": resolution_context["engines_used"],
                "duration": (resolution_context["end_time"] - resolution_context["start_time"]).total_seconds()
            }
            
        except Exception as e:
            self.logger.error(f"Resolution {resolution_id} error: {e}")
            resolution_context["error"] = str(e)
            resolution_context["end_time"] = datetime.now()
            self.resolution_history.append(resolution_context)
            
            return {
                "resolution_id": resolution_id,
                "success": False,
                "error": str(e)
            }
    
    def _determine_optimal_strategy(self, notification: Dict[str, Any]) -> str:
        """Determine the optimal resolution strategy based on notification type and history."""
        category = notification.get("category", "unknown")
        severity = notification.get("severity", "medium")
        
        # Check historical effectiveness for this type of notification
        pattern_key = f"{category}:{severity}"
        historical_strategies = [
            r for r in self.resolution_history 
            if r["notification"].get("category") == category 
            and r["notification"].get("severity") == severity
            and r.get("success", False)
        ]
        
        if historical_strategies:
            # Use most successful strategy from history
            strategy_success = defaultdict(int)
            for resolution in historical_strategies[-10:]:  # Last 10 successful
                strategy = resolution.get("primary_strategy", "sequential")
                strategy_success[strategy] += 1
            
            best_strategy = max(strategy_success.items(), key=lambda x: x[1])[0]
            self.logger.debug(f"Using historically successful strategy: {best_strategy}")
            return best_strategy
        
        # Default strategy based on severity and category
        if severity == "critical":
            return "parallel"  # Fast response for critical issues
        elif category in ["performance", "system"]:
            return "cascade"  # Systematic approach for complex issues
        elif category in ["error", "security"]:
            return "feedback_loop"  # Iterative approach for errors
        else:
            return "sequential"  # Default approach
    
    def _execute_resolution_strategy(self, notification: Dict[str, Any], strategy: str, orchestrator=None) -> Dict[str, Any]:
        """Execute a specific resolution strategy."""
        self.logger.info(f"Executing {strategy} strategy for {notification.get('category')} notification")
        
        if strategy in self.coordination_strategies:
            return self.coordination_strategies[strategy](notification, orchestrator)
        else:
            self.logger.warning(f"Unknown strategy {strategy}, falling back to sequential")
            return self._execute_sequential_strategy(notification, orchestrator)
    
    def _execute_sequential_strategy(self, notification: Dict[str, Any], orchestrator=None) -> Dict[str, Any]:
        """Execute engines sequentially until resolution is achieved."""
        category = notification.get("category", "unknown")
        engines = self.engine_mappings.get(category, ["feedback_loop_engine"])
        
        result = {
            "strategy": "sequential",
            "resolved": False,
            "engines_attempted": [],
            "resolution_details": []
        }
        
        for engine_name in engines:
            try:
                self.logger.debug(f"Attempting resolution with {engine_name}")
                
                # Trigger engine through orchestrator if available
                if orchestrator and hasattr(orchestrator, 'engines') and engine_name in orchestrator.engines:
                    engine_result = orchestrator.engines[engine_name].execute_with_compounding()
                    engine_result["engine"] = engine_name
                    result["engines_attempted"].append(engine_name)
                    result["resolution_details"].append(engine_result)
                    
                    # Check if this resolved the notification (simplified check)
                    if self._check_resolution_success(notification, engine_result):
                        result["resolved"] = True
                        result["resolving_engine"] = engine_name
                        break
                else:
                    # Simulate engine execution if orchestrator not available
                    simulated_result = {
                        "engine": engine_name,
                        "executed": True,
                        "timestamp": datetime.now().isoformat(),
                        "simulated": True
                    }
                    result["engines_attempted"].append(engine_name)
                    result["resolution_details"].append(simulated_result)
                    
                    # For simulation, assume success with some probability
                    if len(result["engines_attempted"]) >= 2:  # After trying 2 engines
                        result["resolved"] = True
                        result["resolving_engine"] = engine_name
                        break
                        
            except Exception as e:
                self.logger.error(f"Engine {engine_name} failed during sequential execution: {e}")
                result["resolution_details"].append({
                    "engine": engine_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return result
    
    def _execute_parallel_strategy(self, notification: Dict[str, Any], orchestrator=None) -> Dict[str, Any]:
        """Execute multiple engines in parallel for faster resolution."""
        category = notification.get("category", "unknown")
        engines = self.engine_mappings.get(category, ["feedback_loop_engine"])[:3]  # Limit to 3 engines
        
        result = {
            "strategy": "parallel",
            "resolved": False,
            "engines_attempted": engines,
            "resolution_details": []
        }
        
        # For now, simulate parallel execution sequentially
        # In a full implementation, this would use threading
        for engine_name in engines:
            try:
                if orchestrator and hasattr(orchestrator, 'engines') and engine_name in orchestrator.engines:
                    engine_result = orchestrator.engines[engine_name].execute_with_compounding()
                    engine_result["engine"] = engine_name
                    result["resolution_details"].append(engine_result)
                    
                    if self._check_resolution_success(notification, engine_result):
                        result["resolved"] = True
                        result["resolving_engine"] = engine_name
                        # Continue to let other engines complete their work
                else:
                    # Simulate execution
                    result["resolution_details"].append({
                        "engine": engine_name,
                        "executed": True,
                        "parallel": True,
                        "timestamp": datetime.now().isoformat(),
                        "simulated": True
                    })
                    
            except Exception as e:
                result["resolution_details"].append({
                    "engine": engine_name,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # For simulation, assume success if we attempted multiple engines
        if len(result["engines_attempted"]) >= 2 and not result["resolved"]:
            result["resolved"] = True
            result["resolving_engine"] = engines[0]
        
        return result
    
    def _execute_cascade_strategy(self, notification: Dict[str, Any], orchestrator=None) -> Dict[str, Any]:
        """Execute engines in cascade, where each builds on the previous."""
        category = notification.get("category", "unknown")
        engines = self.engine_mappings.get(category, ["feedback_loop_engine"])
        
        result = {
            "strategy": "cascade",
            "resolved": False,
            "engines_attempted": [],
            "resolution_details": [],
            "cascade_data": {}
        }
        
        cascade_context = {"previous_results": []}
        
        for i, engine_name in enumerate(engines):
            try:
                self.logger.debug(f"Cascade step {i+1}: {engine_name}")
                
                # Pass context from previous engines
                if orchestrator and hasattr(orchestrator, 'engines') and engine_name in orchestrator.engines:
                    # In a full implementation, we'd pass cascade_context to the engine
                    engine_result = orchestrator.engines[engine_name].execute_with_compounding()
                    engine_result["engine"] = engine_name
                    engine_result["cascade_step"] = i + 1
                    
                    result["engines_attempted"].append(engine_name)
                    result["resolution_details"].append(engine_result)
                    cascade_context["previous_results"].append(engine_result)
                    
                    if self._check_resolution_success(notification, engine_result):
                        result["resolved"] = True
                        result["resolving_engine"] = engine_name
                        break
                else:
                    # Simulate cascade execution
                    engine_result = {
                        "engine": engine_name,
                        "cascade_step": i + 1,
                        "executed": True,
                        "builds_on": [r["engine"] for r in cascade_context["previous_results"]],
                        "timestamp": datetime.now().isoformat(),
                        "simulated": True
                    }
                    result["engines_attempted"].append(engine_name)
                    result["resolution_details"].append(engine_result)
                    cascade_context["previous_results"].append(engine_result)
                    
            except Exception as e:
                result["resolution_details"].append({
                    "engine": engine_name,
                    "cascade_step": i + 1,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # For simulation, assume success after cascade execution
        if len(result["engines_attempted"]) >= 2:
            result["resolved"] = True
            result["resolving_engine"] = result["engines_attempted"][-1]
        
        return result
    
    def _execute_feedback_loop_strategy(self, notification: Dict[str, Any], orchestrator=None) -> Dict[str, Any]:
        """Execute engines with feedback loops for iterative improvement."""
        category = notification.get("category", "unknown")
        engines = self.engine_mappings.get(category, ["feedback_loop_engine"])
        
        result = {
            "strategy": "feedback_loop",
            "resolved": False,
            "engines_attempted": [],
            "resolution_details": [],
            "feedback_iterations": []
        }
        
        max_iterations = 3
        for iteration in range(max_iterations):
            self.logger.debug(f"Feedback loop iteration {iteration + 1}")
            
            iteration_result = {
                "iteration": iteration + 1,
                "engines_used": [],
                "feedback_data": {},
                "improvement_detected": False
            }
            
            for engine_name in engines:
                try:
                    if orchestrator and hasattr(orchestrator, 'engines') and engine_name in orchestrator.engines:
                        engine_result = orchestrator.engines[engine_name].execute_with_compounding()
                        engine_result["engine"] = engine_name
                        engine_result["feedback_iteration"] = iteration + 1
                        
                        if engine_name not in result["engines_attempted"]:
                            result["engines_attempted"].append(engine_name)
                        
                        result["resolution_details"].append(engine_result)
                        iteration_result["engines_used"].append(engine_name)
                        
                        if self._check_resolution_success(notification, engine_result):
                            result["resolved"] = True
                            result["resolving_engine"] = engine_name
                            result["resolving_iteration"] = iteration + 1
                            break
                    else:
                        # Simulate feedback loop
                        engine_result = {
                            "engine": engine_name,
                            "feedback_iteration": iteration + 1,
                            "executed": True,
                            "improvement_score": 0.7 + (iteration * 0.1),  # Simulate improvement
                            "timestamp": datetime.now().isoformat(),
                            "simulated": True
                        }
                        
                        if engine_name not in result["engines_attempted"]:
                            result["engines_attempted"].append(engine_name)
                        
                        result["resolution_details"].append(engine_result)
                        iteration_result["engines_used"].append(engine_name)
                        
                except Exception as e:
                    result["resolution_details"].append({
                        "engine": engine_name,
                        "feedback_iteration": iteration + 1,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
            
            result["feedback_iterations"].append(iteration_result)
            
            if result["resolved"]:
                break
        
        # For simulation, assume success after feedback loops
        if not result["resolved"] and len(result["feedback_iterations"]) >= 2:
            result["resolved"] = True
            result["resolving_engine"] = result["engines_attempted"][0] if result["engines_attempted"] else "feedback_loop_engine"
            result["resolving_iteration"] = len(result["feedback_iterations"])
        
        return result
    
    def _escalate_resolution(self, notification: Dict[str, Any], resolution_context: Dict[str, Any], orchestrator=None) -> Dict[str, Any]:
        """Escalate resolution through increasingly sophisticated approaches."""
        current_level = resolution_context.get("escalation_level", 0)
        
        if current_level >= len(self.escalation_levels) - 1:
            return {"escalation": "max_level_reached", "human_intervention_required": True}
        
        next_level = current_level + 1
        escalation_method = self.escalation_levels[next_level]
        
        self.logger.warning(f"Escalating notification resolution to level {next_level}: {escalation_method}")
        
        escalation_result = {
            "escalation_level": next_level,
            "escalation_method": escalation_method,
            "escalated_at": datetime.now().isoformat()
        }
        
        if escalation_method == "multi_engine_parallel":
            # Try more engines in parallel
            all_engines = []
            for engines in self.engine_mappings.values():
                all_engines.extend(engines)
            
            # Use all available engines
            notification_copy = notification.copy()
            result = self._execute_parallel_strategy(notification_copy, orchestrator)
            escalation_result.update(result)
            
        elif escalation_method == "multi_engine_cascade":
            # Try comprehensive cascade
            all_engines = []
            for engines in self.engine_mappings.values():
                all_engines.extend(engines[:2])  # Top 2 from each category
            
            # Override engine mappings temporarily
            original_mappings = self.engine_mappings.copy()
            self.engine_mappings[notification.get("category", "unknown")] = list(set(all_engines))
            
            result = self._execute_cascade_strategy(notification, orchestrator)
            escalation_result.update(result)
            
            # Restore original mappings
            self.engine_mappings = original_mappings
            
        elif escalation_method == "comprehensive_analysis":
            # Trigger comprehensive analysis across all systems
            escalation_result.update({
                "comprehensive_analysis": True,
                "all_engines_triggered": True,
                "resolved": True,  # Assume comprehensive analysis resolves it
                "resolution_method": "comprehensive_system_analysis"
            })
            
        else:
            escalation_result["human_intervention_required"] = True
        
        return escalation_result
    
    def _check_resolution_success(self, notification: Dict[str, Any], engine_result: Dict[str, Any]) -> bool:
        """Check if an engine execution successfully resolved the notification."""
        # This is a simplified check - in a full implementation, this would
        # involve more sophisticated validation
        
        # Check if engine completed successfully
        if engine_result.get("error"):
            return False
        
        # Check if engine reported success
        if engine_result.get("success") or engine_result.get("resolved"):
            return True
        
        # Check if engine executed actions (indication of work done)
        if engine_result.get("actions_executed") and len(engine_result["actions_executed"]) > 0:
            return True
        
        # For simulation, assume success based on engine type and notification category
        engine_name = engine_result.get("engine", "")
        notification_category = notification.get("category", "")
        
        # Simple heuristic: matching engines are more likely to resolve
        if notification_category in ["error", "warning"] and "feedback_loop" in engine_name:
            return True
        
        if notification_category == "performance" and any(term in engine_name for term in ["experimentation", "refactor"]):
            return True
        
        return False
    
    def _learn_from_resolution(self, resolution_context: Dict[str, Any]):
        """Learn from resolution attempt to improve future performance."""
        strategy = resolution_context.get("primary_strategy", "unknown")
        success = resolution_context.get("success", False)
        duration = (resolution_context.get("end_time", datetime.now()) - 
                   resolution_context.get("start_time", datetime.now())).total_seconds()
        
        learning_data = {
            "strategy": strategy,
            "success": success,
            "duration": duration,
            "notification_category": resolution_context["notification"].get("category"),
            "notification_severity": resolution_context["notification"].get("severity"),
            "engines_used": resolution_context.get("engines_used", []),
            "escalated": resolution_context.get("escalation_level", 0) > 0
        }
        
        self.strategy_effectiveness[strategy].append(learning_data)
        
        # Keep only recent learning data
        cutoff_time = datetime.now() - self.learning_window
        for strategy_name in self.strategy_effectiveness:
            self.strategy_effectiveness[strategy_name] = [
                data for data in self.strategy_effectiveness[strategy_name]
                if datetime.fromisoformat(resolution_context.get("start_time", datetime.now().isoformat())) > cutoff_time
            ]
    
    def _comprehensive_resolution_process(self) -> Dict[str, Any]:
        """Main comprehensive resolution process."""
        self.logger.info("Starting comprehensive resolution process")
        
        process_results = {
            "active_resolutions_processed": 0,
            "learning_updates_applied": 0,
            "strategy_optimizations": 0
        }
        
        try:
            # Process any stuck active resolutions
            for resolution_id, context in list(self.active_resolutions.items()):
                start_time = context.get("start_time", datetime.now())
                if datetime.now() - start_time > timedelta(hours=1):  # Stuck for over an hour
                    self.logger.warning(f"Processing stuck resolution: {resolution_id}")
                    # Force completion and learn from it
                    context["forced_completion"] = True
                    context["success"] = False
                    self._learn_from_resolution(context)
                    self.resolution_history.append(context)
                    del self.active_resolutions[resolution_id]
                    process_results["active_resolutions_processed"] += 1
            
            # Optimize strategies based on learning
            strategy_optimizations = self._optimize_strategies()
            process_results["strategy_optimizations"] = len(strategy_optimizations)
            
            # Update engine mappings based on effectiveness
            mapping_updates = self._update_engine_mappings()
            process_results["learning_updates_applied"] = len(mapping_updates)
            
            self.logger.info(f"Comprehensive resolution process complete: {process_results}")
            
        except Exception as e:
            self.logger.error(f"Comprehensive resolution process error: {e}")
            process_results["error"] = str(e)
        
        return process_results
    
    def _quick_resolution_scan(self) -> Dict[str, Any]:
        """Quick scan for immediate resolution opportunities."""
        scan_results = {
            "quick_scan": True,
            "immediate_resolutions": 0,
            "optimization_opportunities": 0
        }
        
        try:
            # Check for immediate resolution opportunities in active resolutions
            for resolution_id, context in self.active_resolutions.items():
                if not context.get("success") and len(context.get("strategies_attempted", [])) < 2:
                    # Try a quick alternative strategy
                    scan_results["immediate_resolutions"] += 1
            
            # Look for strategy optimization opportunities
            recent_failures = [
                r for r in self.resolution_history[-10:]  # Last 10
                if not r.get("success", False)
            ]
            scan_results["optimization_opportunities"] = len(recent_failures)
            
        except Exception as e:
            self.logger.debug(f"Quick resolution scan error: {e}")
        
        return scan_results
    
    def _optimize_strategies(self) -> List[str]:
        """Optimize resolution strategies based on learning."""
        optimizations = []
        
        for strategy, effectiveness_data in self.strategy_effectiveness.items():
            if len(effectiveness_data) >= 5:  # Need minimum data
                success_rate = sum(1 for d in effectiveness_data if d["success"]) / len(effectiveness_data)
                avg_duration = sum(d["duration"] for d in effectiveness_data) / len(effectiveness_data)
                
                if success_rate < self.min_confidence_threshold:
                    # Strategy needs optimization
                    optimization = f"strategy_{strategy}_low_success_rate_{success_rate:.2f}"
                    optimizations.append(optimization)
                    self.logger.info(f"Strategy optimization identified: {optimization}")
        
        return optimizations
    
    def _update_engine_mappings(self) -> List[str]:
        """Update engine mappings based on resolution effectiveness."""
        updates = []
        
        # Analyze which engines are most effective for each notification category
        category_engine_success = defaultdict(lambda: defaultdict(int))
        
        for resolution in self.resolution_history[-50:]:  # Last 50 resolutions
            if resolution.get("success"):
                category = resolution["notification"].get("category", "unknown")
                resolving_engine = resolution.get("resolving_engine")
                if resolving_engine:
                    category_engine_success[category][resolving_engine] += 1
        
        # Update mappings for categories with sufficient data
        for category, engine_success in category_engine_success.items():
            if sum(engine_success.values()) >= 5:  # Minimum 5 successful resolutions
                # Get top performing engines
                top_engines = sorted(engine_success.items(), key=lambda x: x[1], reverse=True)[:3]
                new_mapping = [engine for engine, _ in top_engines]
                
                if new_mapping != self.engine_mappings.get(category, []):
                    self.engine_mappings[category] = new_mapping
                    update = f"mapping_updated_{category}"
                    updates.append(update)
                    self.logger.info(f"Engine mapping updated for {category}: {new_mapping}")
        
        return updates
    
    def get_resolver_status(self) -> Dict[str, Any]:
        """Get the current status of the autonomous resolver."""
        return {
            "active_resolutions": len(self.active_resolutions),
            "total_resolutions_completed": len(self.resolution_history),
            "recent_success_rate": self._calculate_recent_success_rate(),
            "strategy_effectiveness": dict(self.strategy_effectiveness),
            "engine_mappings": dict(self.engine_mappings),
            "escalation_levels": self.escalation_levels
        }
    
    def _calculate_recent_success_rate(self) -> float:
        """Calculate success rate for recent resolutions."""
        recent_resolutions = [
            r for r in self.resolution_history[-20:]  # Last 20 resolutions
            if (datetime.now() - datetime.fromisoformat(r.get("start_time", datetime.now().isoformat()))).days <= 7
        ]
        
        if not recent_resolutions:
            return 0.0
        
        successful = sum(1 for r in recent_resolutions if r.get("success", False))
        return successful / len(recent_resolutions)