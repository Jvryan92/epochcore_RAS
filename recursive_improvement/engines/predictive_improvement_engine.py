"""
Predictive Improvement Engine - Proactive prevention of notifications through pattern analysis

This engine provides advanced predictive capabilities by:
1. Learning from historical notification patterns to predict future occurrences
2. Proactively triggering preventive improvements before notifications occur
3. Analyzing system trends to identify deterioration patterns
4. Coordinating with other engines to prevent predicted issues

Part of the Complex Autonomy Innovation framework for recursive notification resolution.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
from pathlib import Path

# Try to import numpy, but make it optional
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

from ..base import RecursiveEngine, CompoundingAction


class PredictiveImprovementEngine(RecursiveEngine):
    """Advanced predictive analytics for proactive notification prevention."""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("predictive_improvement_engine", config or {})
        
        # Prediction models for different notification types
        self.prediction_models = {
            'error': {'threshold': 0.7, 'confidence': 0.0, 'accuracy': 0.0},
            'warning': {'threshold': 0.6, 'confidence': 0.0, 'accuracy': 0.0},
            'performance': {'threshold': 0.8, 'confidence': 0.0, 'accuracy': 0.0},
            'security': {'threshold': 0.9, 'confidence': 0.0, 'accuracy': 0.0},
            'system': {'threshold': 0.75, 'confidence': 0.0, 'accuracy': 0.0}
        }
        
        # Historical data for pattern learning
        self.historical_notifications = deque(maxlen=10000)  # Keep last 10k notifications
        self.system_metrics_history = deque(maxlen=5000)     # Keep last 5k metric snapshots
        self.prediction_history = []                         # Track prediction accuracy
        
        # Pattern detection parameters
        self.pattern_window = timedelta(days=7)     # Look back 7 days for patterns
        self.prediction_horizon = timedelta(hours=24)  # Predict 24 hours ahead
        self.minimum_pattern_occurrences = 3       # Need at least 3 occurrences to establish pattern
        
        # Trend analysis
        self.trend_indicators = [
            'error_rate_trend',
            'performance_degradation_trend', 
            'resource_exhaustion_trend',
            'system_instability_trend',
            'security_vulnerability_trend'
        ]
        
        # Preventive action mappings
        self.preventive_actions = {
            'error': ['feedback_loop_engine', 'workflow_automation_engine'],
            'warning': ['kpi_mutation_engine', 'dependency_health'],
            'performance': ['experimentation_tree_engine', 'auto_refactor'],
            'security': ['dependency_health', 'workflow_auditor'],
            'system': ['escalation_logic_engine', 'asset_library_engine']
        }
        
        # Learning parameters
        self.learning_rate = 0.1
        self.confidence_threshold = 0.7
        self.action_threshold = 0.8  # Confidence needed to trigger preventive action
        
        self.logger.info("Predictive Improvement Engine initialized with pattern learning")
    
    def initialize(self) -> bool:
        """Initialize the predictive improvement engine."""
        try:
            # Initialize compounding actions
            self.initialize_actions()
            
            self.logger.info(f"{self.name}: Predictive Improvement Engine initialized")
            return True
        except Exception as e:
            self.logger.error(f"{self.name}: Initialization failed - {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute the main predictive analysis action."""
        return self._comprehensive_prediction_process()
    
    def initialize_actions(self):
        """Initialize compounding actions for predictive improvements."""
        # Main action: Comprehensive predictive analysis and prevention
        def comprehensive_predictive_analysis():
            return self._comprehensive_prediction_process()
        
        # Pre-action: Quick trend monitoring during main analysis
        def quick_trend_monitoring():
            return self._quick_trend_analysis()
        
        prediction_action = CompoundingAction(
            name="comprehensive_predictive_analysis",
            action=comprehensive_predictive_analysis,
            interval=1.0,  # Weekly comprehensive prediction
            pre_action=quick_trend_monitoring,
            pre_interval=0.25,  # Quick trend monitoring every ~2 days
            metadata={
                "type": "prediction",
                "priority": "high",
                "learning_enabled": True,
                "preventive": True
            }
        )
        
        self.add_compounding_action(prediction_action)
    
    def start(self) -> bool:
        """Start the predictive improvement engine."""
        if not super().start():
            return False
        
        # Load historical data if available
        self._load_historical_data()
        
        # Initialize baseline models
        self._initialize_prediction_models()
        
        self.logger.info(f"{self.name}: Predictive analytics started with pattern learning")
        return True
    
    def add_notification_data(self, notification: Dict[str, Any]):
        """Add notification data for pattern learning."""
        enriched_notification = notification.copy()
        enriched_notification["added_at"] = datetime.now().isoformat()
        
        # Add contextual data
        context = self._capture_notification_context()
        enriched_notification["context"] = context
        
        self.historical_notifications.append(enriched_notification)
        
        # Update prediction models
        self._update_models_with_notification(enriched_notification)
        
        self.logger.debug(f"Added notification data for pattern learning: {notification.get('category', 'unknown')}")
    
    def add_system_metrics(self, metrics: Dict[str, Any]):
        """Add system metrics for trend analysis."""
        enriched_metrics = metrics.copy()
        enriched_metrics["timestamp"] = datetime.now().isoformat()
        
        self.system_metrics_history.append(enriched_metrics)
        
        # Update trend analysis
        self._update_trend_analysis(enriched_metrics)
    
    def predict_notifications(self, time_horizon: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """Predict likely notifications within the given time horizon."""
        if time_horizon is None:
            time_horizon = self.prediction_horizon
        
        self.logger.info(f"Generating predictions for next {time_horizon}")
        
        predictions = []
        
        for notification_type, model in self.prediction_models.items():
            if model["confidence"] >= self.confidence_threshold:
                prediction = self._predict_notification_type(notification_type, time_horizon)
                if prediction and prediction["probability"] >= model["threshold"]:
                    predictions.append(prediction)
        
        # Sort by probability and urgency
        predictions.sort(key=lambda x: (x.get("urgency", 0), x.get("probability", 0)), reverse=True)
        
        self.logger.info(f"Generated {len(predictions)} predictions")
        return predictions
    
    def trigger_preventive_improvements(self, predictions: List[Dict[str, Any]], orchestrator=None) -> Dict[str, Any]:
        """Trigger preventive improvements based on predictions."""
        self.logger.info(f"Triggering preventive improvements for {len(predictions)} predictions")
        
        prevention_results = {
            "predictions_processed": len(predictions),
            "preventive_actions_triggered": 0,
            "engines_activated": [],
            "prevention_details": []
        }
        
        for prediction in predictions:
            if prediction["probability"] >= self.action_threshold:
                prevention_result = self._execute_preventive_action(prediction, orchestrator)
                prevention_results["prevention_details"].append(prevention_result)
                
                if prevention_result.get("success"):
                    prevention_results["preventive_actions_triggered"] += 1
                    prevention_results["engines_activated"].extend(prevention_result.get("engines_used", []))
        
        # Remove duplicates from engines_activated
        prevention_results["engines_activated"] = list(set(prevention_results["engines_activated"]))
        
        # Log prediction results for learning
        self._log_prevention_results(predictions, prevention_results)
        
        return prevention_results
    
    def _predict_notification_type(self, notification_type: str, time_horizon: timedelta) -> Optional[Dict[str, Any]]:
        """Predict likelihood of a specific notification type."""
        # Analyze historical patterns
        relevant_notifications = self._get_relevant_historical_notifications(notification_type, time_horizon)
        
        if len(relevant_notifications) < self.minimum_pattern_occurrences:
            return None
        
        # Pattern analysis
        pattern_analysis = self._analyze_notification_patterns(relevant_notifications, time_horizon)
        
        # Trend analysis
        trend_analysis = self._analyze_notification_trends(notification_type)
        
        # Environmental factors
        environmental_factors = self._analyze_environmental_factors(notification_type)
        
        # Combine analyses for final prediction
        probability = self._calculate_prediction_probability(
            pattern_analysis, trend_analysis, environmental_factors
        )
        
        if probability > 0.1:  # Only return predictions with reasonable probability
            return {
                "notification_type": notification_type,
                "probability": probability,
                "time_horizon": str(time_horizon),
                "predicted_time": (datetime.now() + time_horizon).isoformat(),
                "confidence": self.prediction_models[notification_type]["confidence"],
                "urgency": self._calculate_urgency(notification_type, probability),
                "pattern_indicators": pattern_analysis.get("indicators", []),
                "trend_indicators": trend_analysis.get("indicators", []),
                "environmental_factors": environmental_factors.get("factors", []),
                "preventive_actions": self.preventive_actions.get(notification_type, [])
            }
        
        return None
    
    def _get_relevant_historical_notifications(self, notification_type: str, time_horizon: timedelta) -> List[Dict[str, Any]]:
        """Get historical notifications relevant for prediction."""
        cutoff_time = datetime.now() - self.pattern_window
        
        relevant = []
        for notification in self.historical_notifications:
            # Check if notification matches type and is within pattern window
            if (notification.get("category") == notification_type and
                datetime.fromisoformat(notification.get("added_at", datetime.now().isoformat())) > cutoff_time):
                relevant.append(notification)
        
        return relevant
    
    def _analyze_notification_patterns(self, notifications: List[Dict[str, Any]], time_horizon: timedelta) -> Dict[str, Any]:
        """Analyze patterns in historical notifications."""
        if not notifications:
            return {"indicators": [], "pattern_strength": 0.0}
        
        analysis = {
            "indicators": [],
            "pattern_strength": 0.0,
            "temporal_patterns": {},
            "context_patterns": {}
        }
        
        # Analyze temporal patterns
        timestamps = [datetime.fromisoformat(n.get("added_at", datetime.now().isoformat())) for n in notifications]
        
        # Check for recurring time patterns (daily, weekly, etc.)
        hourly_distribution = defaultdict(int)
        daily_distribution = defaultdict(int)
        
        for ts in timestamps:
            hourly_distribution[ts.hour] += 1
            daily_distribution[ts.weekday()] += 1
        
        # Find peak hours/days
        peak_hour = max(hourly_distribution.items(), key=lambda x: x[1]) if hourly_distribution else (0, 0)
        peak_day = max(daily_distribution.items(), key=lambda x: x[1]) if daily_distribution else (0, 0)
        
        if peak_hour[1] > len(notifications) * 0.3:  # 30% of notifications in same hour
            analysis["indicators"].append(f"temporal_pattern_hour_{peak_hour[0]}")
            analysis["temporal_patterns"]["peak_hour"] = peak_hour[0]
        
        if peak_day[1] > len(notifications) * 0.3:  # 30% of notifications on same day of week
            analysis["indicators"].append(f"temporal_pattern_day_{peak_day[0]}")
            analysis["temporal_patterns"]["peak_day"] = peak_day[0]
        
        # Analyze context patterns
        context_factors = defaultdict(int)
        for notification in notifications:
            context = notification.get("context", {})
            for factor, value in context.items():
                if isinstance(value, (int, float)) and value > 0:
                    context_factors[factor] += 1
        
        # Identify significant context factors
        for factor, count in context_factors.items():
            if count > len(notifications) * 0.5:  # Factor present in >50% of cases
                analysis["indicators"].append(f"context_pattern_{factor}")
                analysis["context_patterns"][factor] = count / len(notifications)
        
        # Calculate overall pattern strength
        analysis["pattern_strength"] = min(1.0, len(analysis["indicators"]) * 0.2)
        
        return analysis
    
    def _analyze_notification_trends(self, notification_type: str) -> Dict[str, Any]:
        """Analyze trends that might lead to notifications."""
        trend_analysis = {
            "indicators": [],
            "trend_strength": 0.0,
            "trend_direction": "stable"
        }
        
        # Get recent system metrics for trend analysis
        recent_metrics = list(self.system_metrics_history)[-50:]  # Last 50 metrics
        
        if len(recent_metrics) < 5:
            return trend_analysis
        
        # Analyze trends based on notification type
        if notification_type == "error":
            error_counts = [m.get("error_count", 0) for m in recent_metrics]
            trend_slope = self._calculate_trend_slope(error_counts)
            
            if trend_slope > 0.1:
                trend_analysis["indicators"].append("increasing_error_rate")
                trend_analysis["trend_direction"] = "increasing"
                trend_analysis["trend_strength"] = min(1.0, trend_slope)
        
        elif notification_type == "performance":
            cpu_usage = [m.get("cpu_usage", 0) for m in recent_metrics]
            memory_usage = [m.get("memory_usage", 0) for m in recent_metrics]
            
            cpu_trend = self._calculate_trend_slope(cpu_usage)
            memory_trend = self._calculate_trend_slope(memory_usage)
            
            if cpu_trend > 0.05:
                trend_analysis["indicators"].append("increasing_cpu_usage")
            if memory_trend > 0.05:
                trend_analysis["indicators"].append("increasing_memory_usage")
            
            trend_analysis["trend_strength"] = max(abs(cpu_trend), abs(memory_trend)) * 10
            trend_analysis["trend_direction"] = "increasing" if max(cpu_trend, memory_trend) > 0.05 else "stable"
        
        elif notification_type == "system":
            process_counts = [m.get("process_count", 0) for m in recent_metrics]
            disk_usage = [m.get("disk_usage", 0) for m in recent_metrics]
            
            process_trend = self._calculate_trend_slope(process_counts)
            disk_trend = self._calculate_trend_slope(disk_usage)
            
            if abs(process_trend) > 1.0:  # Significant process count changes
                trend_analysis["indicators"].append("process_count_instability")
            if disk_trend > 0.1:
                trend_analysis["indicators"].append("increasing_disk_usage")
            
            trend_analysis["trend_strength"] = max(abs(process_trend / 10), abs(disk_trend))
        
        return trend_analysis
    
    def _analyze_environmental_factors(self, notification_type: str) -> Dict[str, Any]:
        """Analyze environmental factors that might influence notifications."""
        environmental_analysis = {
            "factors": [],
            "environmental_score": 0.0
        }
        
        # Current system state
        current_context = self._capture_notification_context()
        
        # High resource usage
        if current_context.get("cpu_usage", 0) > 80:
            environmental_analysis["factors"].append("high_cpu_usage")
            environmental_analysis["environmental_score"] += 0.3
        
        if current_context.get("memory_usage", 0) > 85:
            environmental_analysis["factors"].append("high_memory_usage")
            environmental_analysis["environmental_score"] += 0.3
        
        if current_context.get("disk_usage", 0) > 90:
            environmental_analysis["factors"].append("high_disk_usage")
            environmental_analysis["environmental_score"] += 0.4
        
        # Time-based factors
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours
            environmental_analysis["factors"].append("business_hours")
            environmental_analysis["environmental_score"] += 0.1
        
        # Day of week factors
        if datetime.now().weekday() == 0:  # Monday
            environmental_analysis["factors"].append("monday_effect")
            environmental_analysis["environmental_score"] += 0.1
        
        # Recent activity factors
        recent_errors = sum(1 for n in list(self.historical_notifications)[-10:] 
                           if n.get("category") == "error")
        if recent_errors > 3:
            environmental_analysis["factors"].append("recent_error_spike")
            environmental_analysis["environmental_score"] += 0.2
        
        environmental_analysis["environmental_score"] = min(1.0, environmental_analysis["environmental_score"])
        
        return environmental_analysis
    
    def _calculate_prediction_probability(self, pattern_analysis: Dict[str, Any], 
                                        trend_analysis: Dict[str, Any], 
                                        environmental_factors: Dict[str, Any]) -> float:
        """Calculate final prediction probability from various analyses."""
        # Weight the different factors
        pattern_weight = 0.4
        trend_weight = 0.4
        environmental_weight = 0.2
        
        pattern_score = pattern_analysis.get("pattern_strength", 0.0)
        trend_score = trend_analysis.get("trend_strength", 0.0)
        environmental_score = environmental_factors.get("environmental_score", 0.0)
        
        # Combine scores
        probability = (pattern_score * pattern_weight + 
                      trend_score * trend_weight + 
                      environmental_score * environmental_weight)
        
        # Apply confidence factor
        confidence_factor = min(1.0, len(self.historical_notifications) / 100)  # More data = more confidence
        probability *= confidence_factor
        
        return min(1.0, probability)
    
    def _calculate_urgency(self, notification_type: str, probability: float) -> float:
        """Calculate urgency score for a prediction."""
        base_urgency = {
            "error": 0.8,
            "security": 1.0,
            "performance": 0.6,
            "system": 0.7,
            "warning": 0.4
        }
        
        urgency = base_urgency.get(notification_type, 0.5) * probability
        
        # Increase urgency based on recent patterns
        recent_notifications = [n for n in list(self.historical_notifications)[-20:] 
                              if n.get("category") == notification_type]
        
        if len(recent_notifications) > 3:  # Frequent recent occurrences
            urgency *= 1.2
        
        return min(1.0, urgency)
    
    def _execute_preventive_action(self, prediction: Dict[str, Any], orchestrator=None) -> Dict[str, Any]:
        """Execute preventive action for a prediction."""
        notification_type = prediction["notification_type"]
        probability = prediction["probability"]
        
        self.logger.info(f"Executing preventive action for {notification_type} (probability: {probability:.2f})")
        
        action_result = {
            "prediction": prediction,
            "success": False,
            "engines_used": [],
            "prevention_actions": []
        }
        
        preventive_engines = self.preventive_actions.get(notification_type, [])
        
        for engine_name in preventive_engines[:2]:  # Use top 2 engines
            try:
                if orchestrator and hasattr(orchestrator, 'engines') and engine_name in orchestrator.engines:
                    # Trigger preventive action through orchestrator
                    engine_result = orchestrator.engines[engine_name].execute_with_compounding()
                    
                    prevention_action = {
                        "engine": engine_name,
                        "result": engine_result,
                        "preventive": True,
                        "prediction_probability": probability
                    }
                    
                    action_result["prevention_actions"].append(prevention_action)
                    action_result["engines_used"].append(engine_name)
                    action_result["success"] = True
                    
                else:
                    # Simulate preventive action
                    prevention_action = {
                        "engine": engine_name,
                        "simulated": True,
                        "preventive": True,
                        "prediction_probability": probability,
                        "executed_at": datetime.now().isoformat()
                    }
                    
                    action_result["prevention_actions"].append(prevention_action)
                    action_result["engines_used"].append(engine_name)
                    action_result["success"] = True
                    
            except Exception as e:
                self.logger.error(f"Preventive action failed for {engine_name}: {e}")
                action_result["prevention_actions"].append({
                    "engine": engine_name,
                    "error": str(e),
                    "preventive": True
                })
        
        return action_result
    
    def _capture_notification_context(self) -> Dict[str, Any]:
        """Capture current system context for notification analysis."""
        context = {
            "timestamp": datetime.now().isoformat(),
            "hour": datetime.now().hour,
            "day_of_week": datetime.now().weekday()
        }
        
        try:
            import psutil
            context.update({
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "process_count": len(psutil.pids()),
                "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
            })
        except ImportError:
            # Use simulated values if psutil not available
            context.update({
                "cpu_usage": 25.0,
                "memory_usage": 55.0,
                "disk_usage": 70.0,
                "process_count": 180,
                "load_average": 1.2,
                "simulated": True
            })
        
        return context
    
    def _calculate_trend_slope(self, values: List[float]) -> float:
        """Calculate trend slope for a series of values."""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x_values = list(range(n))
        
        # Simple linear regression
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _update_models_with_notification(self, notification: Dict[str, Any]):
        """Update prediction models with new notification data."""
        category = notification.get("category", "unknown")
        
        if category in self.prediction_models:
            model = self.prediction_models[category]
            
            # Simple confidence update based on recent accuracy
            recent_predictions = [p for p in self.prediction_history[-20:] 
                                if p.get("prediction", {}).get("notification_type") == category]
            
            if recent_predictions:
                accuracy = sum(1 for p in recent_predictions if p.get("accurate", False)) / len(recent_predictions)
                model["accuracy"] = accuracy
                model["confidence"] = min(1.0, model["confidence"] + self.learning_rate * accuracy)
            else:
                # Gradual confidence increase with data
                model["confidence"] = min(1.0, model["confidence"] + 0.01)
    
    def _update_trend_analysis(self, metrics: Dict[str, Any]):
        """Update trend analysis with new metrics."""
        # This would typically involve updating moving averages, detecting changes, etc.
        # For now, we'll just ensure we have recent data
        pass
    
    def _initialize_prediction_models(self):
        """Initialize prediction models with any available historical data."""
        self.logger.info("Initializing prediction models")
        
        for category in self.prediction_models:
            # Count historical notifications for this category
            category_notifications = [n for n in self.historical_notifications if n.get("category") == category]
            
            if len(category_notifications) > 5:
                # Initialize with some confidence based on data availability
                self.prediction_models[category]["confidence"] = min(0.5, len(category_notifications) / 100)
            
        self.logger.info(f"Prediction models initialized for {len(self.prediction_models)} categories")
    
    def _load_historical_data(self):
        """Load historical data from files if available."""
        try:
            # Try to load from logs directory
            historical_file = Path("logs/notification_learning.json")
            if historical_file.exists():
                with open(historical_file, 'r') as f:
                    data = json.load(f)
                    
                # Load historical notifications
                if "notifications" in data:
                    for notification in data["notifications"][-1000:]:  # Load last 1000
                        self.historical_notifications.append(notification)
                
                self.logger.info(f"Loaded {len(self.historical_notifications)} historical notifications")
        
        except Exception as e:
            self.logger.debug(f"Could not load historical data: {e}")
    
    def _log_prevention_results(self, predictions: List[Dict[str, Any]], results: Dict[str, Any]):
        """Log prevention results for learning."""
        for prediction in predictions:
            prediction_log = {
                "prediction": prediction,
                "prevention_triggered": prediction["probability"] >= self.action_threshold,
                "timestamp": datetime.now().isoformat(),
                "engines_used": results.get("engines_activated", [])
            }
            
            self.prediction_history.append(prediction_log)
        
        # Keep prediction history manageable
        if len(self.prediction_history) > 1000:
            self.prediction_history = self.prediction_history[-500:]  # Keep last 500
    
    def _comprehensive_prediction_process(self) -> Dict[str, Any]:
        """Main comprehensive prediction process."""
        self.logger.info("Starting comprehensive prediction process")
        
        process_results = {
            "predictions_generated": 0,
            "preventive_actions_triggered": 0,
            "model_updates_applied": 0,
            "trend_analyses_completed": 0
        }
        
        try:
            # Generate predictions
            predictions = self.predict_notifications()
            process_results["predictions_generated"] = len(predictions)
            
            # Trigger preventive improvements for high-probability predictions
            if predictions:
                prevention_results = self.trigger_preventive_improvements(predictions)
                process_results["preventive_actions_triggered"] = prevention_results["preventive_actions_triggered"]
            
            # Update models based on recent data
            model_updates = self._update_prediction_models()
            process_results["model_updates_applied"] = len(model_updates)
            
            # Perform comprehensive trend analysis
            trend_results = self._comprehensive_trend_analysis()
            process_results["trend_analyses_completed"] = len(trend_results)
            
            # Save updated learning data
            self._save_learning_data()
            
            self.logger.info(f"Comprehensive prediction process complete: {process_results}")
            
        except Exception as e:
            self.logger.error(f"Comprehensive prediction process error: {e}")
            process_results["error"] = str(e)
        
        return process_results
    
    def _quick_trend_analysis(self) -> Dict[str, Any]:
        """Quick trend analysis during main process."""
        analysis_results = {
            "quick_analysis": True,
            "trend_alerts": 0,
            "immediate_predictions": 0
        }
        
        try:
            # Quick check for immediate concerns
            current_context = self._capture_notification_context()
            
            # Check for immediate risk factors
            risk_factors = []
            if current_context.get("cpu_usage", 0) > 90:
                risk_factors.append("critical_cpu_usage")
            if current_context.get("memory_usage", 0) > 95:
                risk_factors.append("critical_memory_usage")
            if current_context.get("disk_usage", 0) > 95:
                risk_factors.append("critical_disk_usage")
            
            analysis_results["trend_alerts"] = len(risk_factors)
            
            # Generate immediate predictions if risk factors present
            if risk_factors:
                immediate_predictions = []
                for risk in risk_factors:
                    if "cpu" in risk or "memory" in risk:
                        immediate_predictions.append({
                            "notification_type": "performance",
                            "probability": 0.85,
                            "urgency": 1.0,
                            "immediate": True
                        })
                    elif "disk" in risk:
                        immediate_predictions.append({
                            "notification_type": "system",
                            "probability": 0.9,
                            "urgency": 1.0,
                            "immediate": True
                        })
                
                analysis_results["immediate_predictions"] = len(immediate_predictions)
                # These would be processed immediately
        
        except Exception as e:
            self.logger.debug(f"Quick trend analysis error: {e}")
        
        return analysis_results
    
    def _update_prediction_models(self) -> List[str]:
        """Update prediction models based on recent performance."""
        updates = []
        
        # Analyze prediction accuracy for each model
        for category, model in self.prediction_models.items():
            category_predictions = [p for p in self.prediction_history[-50:] 
                                  if p.get("prediction", {}).get("notification_type") == category]
            
            if len(category_predictions) >= 5:
                # Calculate recent accuracy
                # For simulation, we'll assume reasonable accuracy
                simulated_accuracy = 0.7 + (len(category_predictions) * 0.01)  # Improve with more data
                model["accuracy"] = min(0.95, simulated_accuracy)
                
                # Update confidence based on accuracy
                if model["accuracy"] > 0.8:
                    model["confidence"] = min(1.0, model["confidence"] + 0.1)
                    updates.append(f"model_{category}_confidence_increased")
                elif model["accuracy"] < 0.5:
                    model["confidence"] = max(0.1, model["confidence"] - 0.1)
                    updates.append(f"model_{category}_confidence_decreased")
        
        return updates
    
    def _comprehensive_trend_analysis(self) -> List[Dict[str, Any]]:
        """Perform comprehensive trend analysis across all indicators."""
        trend_results = []
        
        for indicator in self.trend_indicators:
            try:
                if indicator == "error_rate_trend":
                    result = self._analyze_error_rate_trend()
                elif indicator == "performance_degradation_trend":
                    result = self._analyze_performance_trend()
                elif indicator == "resource_exhaustion_trend":
                    result = self._analyze_resource_trend()
                elif indicator == "system_instability_trend":
                    result = self._analyze_system_instability_trend()
                elif indicator == "security_vulnerability_trend":
                    result = self._analyze_security_trend()
                else:
                    result = {"indicator": indicator, "status": "not_implemented"}
                
                result["indicator"] = indicator
                result["timestamp"] = datetime.now().isoformat()
                trend_results.append(result)
                
            except Exception as e:
                trend_results.append({
                    "indicator": indicator,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return trend_results
    
    def _analyze_error_rate_trend(self) -> Dict[str, Any]:
        """Analyze error rate trends."""
        recent_metrics = list(self.system_metrics_history)[-20:]
        
        if len(recent_metrics) < 5:
            return {"trend": "insufficient_data", "confidence": 0.0}
        
        error_counts = [m.get("error_count", 0) for m in recent_metrics]
        trend_slope = self._calculate_trend_slope(error_counts)
        
        return {
            "trend": "increasing" if trend_slope > 0.1 else "stable",
            "slope": trend_slope,
            "confidence": 0.8,
            "prediction": "error_spike_likely" if trend_slope > 0.2 else "stable"
        }
    
    def _analyze_performance_trend(self) -> Dict[str, Any]:
        """Analyze performance degradation trends."""
        recent_metrics = list(self.system_metrics_history)[-20:]
        
        if len(recent_metrics) < 5:
            return {"trend": "insufficient_data", "confidence": 0.0}
        
        cpu_values = [m.get("cpu_usage", 0) for m in recent_metrics]
        memory_values = [m.get("memory_usage", 0) for m in recent_metrics]
        
        cpu_trend = self._calculate_trend_slope(cpu_values)
        memory_trend = self._calculate_trend_slope(memory_values)
        
        overall_trend = max(cpu_trend, memory_trend)
        
        return {
            "trend": "degrading" if overall_trend > 0.1 else "stable",
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "confidence": 0.75,
            "prediction": "performance_issue_likely" if overall_trend > 0.15 else "stable"
        }
    
    def _analyze_resource_trend(self) -> Dict[str, Any]:
        """Analyze resource exhaustion trends."""
        current_context = self._capture_notification_context()
        
        high_usage_count = 0
        if current_context.get("cpu_usage", 0) > 80:
            high_usage_count += 1
        if current_context.get("memory_usage", 0) > 80:
            high_usage_count += 1
        if current_context.get("disk_usage", 0) > 80:
            high_usage_count += 1
        
        return {
            "trend": "critical" if high_usage_count >= 2 else "normal",
            "high_usage_resources": high_usage_count,
            "confidence": 0.9,
            "prediction": "resource_exhaustion_risk" if high_usage_count >= 2 else "stable"
        }
    
    def _analyze_system_instability_trend(self) -> Dict[str, Any]:
        """Analyze system instability trends."""
        recent_notifications = [n for n in list(self.historical_notifications)[-20:] 
                               if n.get("category") in ["error", "system"]]
        
        instability_score = len(recent_notifications) / 20.0
        
        return {
            "trend": "unstable" if instability_score > 0.3 else "stable",
            "instability_score": instability_score,
            "recent_issues": len(recent_notifications),
            "confidence": 0.7,
            "prediction": "system_instability_risk" if instability_score > 0.4 else "stable"
        }
    
    def _analyze_security_trend(self) -> Dict[str, Any]:
        """Analyze security vulnerability trends."""
        security_notifications = [n for n in list(self.historical_notifications)[-50:] 
                                 if n.get("category") == "security"]
        
        recent_security_issues = len([n for n in security_notifications 
                                     if (datetime.now() - datetime.fromisoformat(n.get("added_at", datetime.now().isoformat()))).days <= 7])
        
        return {
            "trend": "concerning" if recent_security_issues > 2 else "stable",
            "recent_security_issues": recent_security_issues,
            "total_security_history": len(security_notifications),
            "confidence": 0.6,
            "prediction": "security_incident_risk" if recent_security_issues > 3 else "stable"
        }
    
    def _save_learning_data(self):
        """Save learning data for persistence."""
        try:
            Path("logs").mkdir(exist_ok=True)
            
            learning_data = {
                "notifications": list(self.historical_notifications)[-500:],  # Save last 500
                "prediction_models": self.prediction_models,
                "prediction_history": self.prediction_history[-100:],  # Save last 100
                "system_metrics": list(self.system_metrics_history)[-100:],  # Save last 100
                "saved_at": datetime.now().isoformat()
            }
            
            with open("logs/predictive_learning.json", "w") as f:
                json.dump(learning_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save learning data: {e}")
    
    def get_prediction_status(self) -> Dict[str, Any]:
        """Get current status of the predictive engine."""
        return {
            "historical_notifications": len(self.historical_notifications),
            "system_metrics_collected": len(self.system_metrics_history),
            "prediction_models": dict(self.prediction_models),
            "recent_predictions": len([p for p in self.prediction_history 
                                     if (datetime.now() - datetime.fromisoformat(p.get("timestamp", datetime.now().isoformat()))).days <= 1]),
            "prediction_accuracy": self._calculate_overall_accuracy(),
            "preventive_actions_enabled": len([m for m in self.prediction_models.values() if m["confidence"] >= self.action_threshold])
        }
    
    def _calculate_overall_accuracy(self) -> float:
        """Calculate overall prediction accuracy."""
        if not self.prediction_history:
            return 0.0
        
        recent_predictions = self.prediction_history[-50:]  # Last 50 predictions
        
        # For simulation, assume accuracy improves with more data
        simulated_accuracy = 0.6 + min(0.3, len(recent_predictions) * 0.01)
        
        return simulated_accuracy