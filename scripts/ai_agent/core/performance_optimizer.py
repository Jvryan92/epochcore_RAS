#!/usr/bin/env python3
"""Performance optimization module with cryptographic verification."""

import os
import json
import hashlib
import hmac
import datetime as dt
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict

from .base_agent import BaseAgent


@dataclass
class Optimization:
    """Record of an optimization attempt with cryptographic proof."""

    id: str
    timestamp: str
    component: str
    old_params: Dict[str, Any]


class PerformanceOptimizer(BaseAgent):
    """Automatically optimizes performance with cryptographic proof."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the performance optimizer.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__("performance_optimizer", config)

        self.optimizations: Dict[str, Optimization] = {}
        self.parameter_history: Dict[str, List[Dict]] = defaultdict(list)
        self.merkle_roots: List[str] = []
        self.current_metrics: Dict[str, float] = {}

        # Subscribe to relevant topics
        self.subscribe_to_topic("pricing_analysis")
        self.subscribe_to_topic("performance_check")
        self.subscribe_to_topic("system_health")

    def _get_recent_metrics(self) -> Dict[str, float]:
        """Get recent performance metrics."""
        metrics = {}
        for component, history in self.parameter_history.items():
            if history:
                latest = history[-1]
                if "metrics" in latest:
                    for key, value in latest["metrics"].items():
                        if isinstance(value, (int, float)):
                            metrics[key] = float(value)
        return metrics

    def _get_current_metrics(self) -> Dict[str, float]:
        """Get current system metrics."""
        return self.current_metrics.copy()

    def validate_config(self) -> bool:
        """Validate agent configuration."""
        # No specific config needed
        return True

    def run(self) -> Dict[str, Any]:
        """Run optimizer's main loop."""
        return {
            "status": "success",
            "optimizations": len(self.optimizations),
            "components": len(self.parameter_history),
        }

    def record_parameters(
        self, component: str, params: Dict[str, Any], metrics: Dict[str, float]
    ) -> None:
        """Record parameter settings and resulting metrics."""
        timestamp = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        self.parameter_history[component].append(
            {"timestamp": timestamp, "params": params.copy(), "metrics": metrics.copy()}
        )

        # Notify interested agents of significant metric changes
        if any(
            self._is_metric_significant(component, metric, value)
            for metric, value in metrics.items()
        ):
            self.send_message(
                recipient=None,  # Broadcast
                topic="performance_alert",
                data={
                    "component": component,
                    "metrics": metrics,
                    "timestamp": timestamp,
                    "severity": self._calculate_severity(metrics),
                },
                priority="high",
            )

    def _is_metric_significant(self, component: str, metric: str, value: float) -> bool:
        """Check if a metric change is significant."""
        if component not in self.parameter_history:
            return False

        history = self.parameter_history[component]
        if len(history) < 2:
            return False

        prev_value = history[-2]["metrics"].get(metric)
        if prev_value is None:
            return False

        # Define significance thresholds for different metrics
        thresholds = {
            "response_time": 0.2,  # 20% change
            "error_rate": 0.1,  # 10% change
            "cpu_usage": 0.15,  # 15% change
            "memory_usage": 0.15,  # 15% change
            "default": 0.25,  # 25% change for other metrics
        }

        threshold = thresholds.get(metric, thresholds["default"])
        percent_change = abs(value - prev_value) / prev_value

        return percent_change > threshold

    def _calculate_severity(self, metrics: Dict[str, float]) -> str:
        """Calculate alert severity based on metrics."""
        severity_score = 0

        # Weight different metrics
        weights = {
            "error_rate": 1.0,
            "response_time": 0.8,
            "cpu_usage": 0.6,
            "memory_usage": 0.6,
        }

        thresholds = {
            "error_rate": 0.05,  # 5% error rate
            "response_time": 1000,  # 1 second
            "cpu_usage": 0.8,  # 80% usage
            "memory_usage": 0.8,  # 80% usage
        }

        for metric, value in metrics.items():
            if metric in weights:
                threshold = thresholds.get(metric, float("inf"))
                if value > threshold:
                    severity_score += weights[metric]

        if severity_score >= 1.5:
            return "high"
        elif severity_score >= 0.8:
            return "medium"
        return "low"

    def _process_message(self, message: Dict[str, Any]) -> None:
        """Process incoming messages from other agents.

        Args:
            message: The message to process
        """
        topic = message["topic"]
        data = message["data"]

        if topic == "performance_check":
            # Handle requests for performance data on specific components
            products = data.get("high_volatility_products", [])
            if products:
                response_data = self._analyze_product_performance(products)
                self.send_message(
                    recipient=message["sender"],
                    topic="performance_data",
                    data=response_data,
                    priority="high",
                )

        elif topic == "pricing_analysis":
            # Monitor pricing analysis lifecycle
            action = data.get("action")
            if action == "start_analysis":
                # Begin monitoring system load
                self._start_load_monitoring()
            elif action == "complete":
                # Correlate system performance with pricing changes
                metrics = data.get("metrics", {})
                self._correlate_pricing_performance(metrics)

    def _analyze_product_performance(self, product_ids: List[str]) -> Dict[str, Any]:
        """Analyze performance metrics for specific products.

        Args:
            product_ids: List of product IDs to analyze

        Returns:
            Performance analysis data
        """
        analysis = {
            "timestamp": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "high_load_correlation": False,
            "performance_impact": {},
        }

        # Get recent performance metrics
        recent_metrics = self._get_recent_metrics()

        # Check for performance impact during price changes
        for product_id in product_ids:
            component = f"product_{product_id}"
            if component in self.parameter_history:
                history = self.parameter_history[component]
                if history and recent_metrics:
                    # Check if performance issues correlate with price changes
                    if (
                        recent_metrics.get("response_time", 0) > 800
                        or recent_metrics.get("error_rate", 0) > 0.02
                    ):
                        analysis["high_load_correlation"] = True
                        analysis["performance_impact"][product_id] = "high"

        return analysis

    def _start_load_monitoring(self) -> None:
        """Start monitoring system load during pricing analysis."""
        # Reset performance metrics with initial values
        self.record_parameters(
            "system",
            {},
            {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "response_time": 0.0,
                "error_rate": 0.0,
                "load_factor": 0.0,
            },
        )

    def _correlate_pricing_performance(self, pricing_metrics: Dict[str, Any]) -> None:
        """Correlate system performance with pricing changes.

        Args:
            pricing_metrics: Metrics from pricing analysis
        """
        # Get performance metrics during the pricing analysis
        current_metrics = self._get_current_metrics()

        # Check for correlations
        if current_metrics.get("cpu_usage", 0) > 0.7:
            self.send_message(
                recipient=None,  # Broadcast
                topic="system_health",
                data={
                    "health_score": 0.6,
                    "reason": "High CPU usage during pricing operations",
                    "recommendation": "Consider optimizing pricing calculation logic",
                },
                priority="high",
            )

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics summary with compounding recommendations."""
        metrics = {
            "timestamp": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "components": {},
            "overall": {
                "optimizations": len(self.optimizations),
                "components_tracked": len(self.parameter_history),
            },
            "recommendations": [],
        }

        # Track critical thresholds for recommendations
        critical_metrics = {
            "response_time": 1000,  # ms
            "error_rate": 0.05,  # 5%
            "memory_usage": 0.9,  # 90%
            "cpu_usage": 0.8,  # 80%
        }

        # Summarize per-component metrics
        for component, history in self.parameter_history.items():
            if not history:
                continue

            latest = history[-1]
            component_metrics = {
                "latest_metrics": latest["metrics"],
                "parameter_versions": len(history),
                "last_update": latest["timestamp"],
            }

            # Calculate improvement trends and check thresholds
            if len(history) > 1:
                first_metrics = history[0]["metrics"]
                for metric, value in latest["metrics"].items():
                    if metric in first_metrics:
                        pct_change = (
                            (value - first_metrics[metric])
                            / first_metrics[metric]
                            * 100
                        )
                        component_metrics[f"{metric}_improvement"] = pct_change

                        # Check thresholds for recommendations
                        if metric in critical_metrics:
                            threshold = critical_metrics[metric]
                            if value > threshold:
                                metrics["recommendations"].append(
                                    {
                                        "component": component,
                                        "metric": metric,
                                        "value": value,
                                        "threshold": threshold,
                                        "priority": "high",
                                        "suggestion": f"Optimize {component} {metric}",
                                    }
                                )

            metrics["components"][component] = component_metrics

        # Add compounding optimization recommendations
        metrics["recommendations"].extend(self._get_compound_recommendations())

        return metrics

    def _get_compound_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on cross-component analysis."""
        recommendations = []

        # Analyze correlated metrics across components
        for comp1, history1 in self.parameter_history.items():
            if not history1:
                continue

            metrics1 = history1[-1]["metrics"]

            for comp2, history2 in self.parameter_history.items():
                if comp1 == comp2 or not history2:
                    continue

                metrics2 = history2[-1]["metrics"]

                # Look for correlated issues
                if (
                    "response_time" in metrics1
                    and "response_time" in metrics2
                    and metrics1["response_time"] > 500
                    and metrics2["response_time"] > 500
                ):
                    recommendations.append(
                        {
                            "components": [comp1, comp2],
                            "metric": "response_time",
                            "priority": "high",
                            "suggestion": f"Review interaction between {comp1} and {comp2}",
                        }
                    )

                # Check resource contention
                if (
                    "cpu_usage" in metrics1
                    and "cpu_usage" in metrics2
                    and metrics1["cpu_usage"] > 0.7
                    and metrics2["cpu_usage"] > 0.7
                ):
                    recommendations.append(
                        {
                            "components": [comp1, comp2],
                            "metric": "cpu_usage",
                            "priority": "high",
                            "suggestion": "Resource contention detected",
                        }
                    )

        return recommendations

    def suggest_optimization(
        self,
        component: str,
        current_params: Dict[str, Any],
        target_metric: str,
        min_confidence: float = 0.1,
    ) -> Tuple[Dict[str, Any], float]:
        """Suggest parameter optimization based on history."""
        if component not in self.parameter_history:
            return (current_params, 0.0)

        history = self.parameter_history[component]
        if len(history) < 3:  # Need minimum history
            return (current_params, 0.0)

        # Analyze impact and optimize
        impacts = self._analyze_parameter_impacts(history, target_metric)
        best_params, confidence = self._generate_optimization(current_params, impacts)

        # If we found any improvement, return it regardless of confidence
        if confidence > 0.0:
            return (best_params, confidence)

        return (current_params, 0.0)

    def _analyze_parameter_impacts(
        self, history: List[Dict], metric: str
    ) -> Dict[str, Dict[str, float]]:
        """Analyze how parameters impact target metric."""
        impacts = defaultdict(lambda: defaultdict(list))

        # Group by parameter values
        for entry in history:
            metrics = entry.get("metrics", {})
            if metric not in metrics:
                continue

            params = entry.get("params", {})
            metric_value = float(metrics[metric])

            # Record impact for each parameter value
            for param, value in params.items():
                impacts[param][str(value)].append(metric_value)

        # Calculate average impact per value
        results = {}
        for param, values in impacts.items():
            value_impacts = {}
            for value, metric_values in values.items():
                if metric_values:  # Only if we have data
                    avg = sum(metric_values) / len(metric_values)
                    value_impacts[value] = avg
            if value_impacts:  # Only add parameter if it has impacts
                results[param] = value_impacts

        return results

    def _generate_optimization(
        self, current: Dict[str, Any], impacts: Dict[str, Dict[str, float]]
    ) -> Tuple[Dict[str, Any], float]:
        """Generate optimized parameters with confidence score."""
        if not impacts:
            return current, 0.0

        new_params = current.copy()
        improvements = []

        for param, values in impacts.items():
            if param not in current:
                continue

            # Find value with best impact (for latency, smaller is better)
            current_value = str(current[param])
            best_value = min(values.items(), key=lambda x: x[1])[
                0
            ]  # Use min for latency

            if best_value != current_value:
                try:
                    # Convert string value back to original type
                    typed_value = type(current[param])(best_value)
                    new_params[param] = typed_value

                    # For latency, calculate improvement as reduction percentage
                    current_impact = values.get(current_value, float("inf"))
                    best_impact = values[best_value]
                    if current_impact > best_impact:  # Only count improvements
                        improvement = (current_impact - best_impact) / current_impact
                        improvements.append(improvement)
                except (ValueError, TypeError):
                    continue

        if not improvements:
            return current, 0.0

        # Calculate confidence based on average improvement percentage
        confidence = sum(improvements) / len(improvements)  # Already in 0-1 range
        return new_params, confidence

    def apply_optimization(
        self,
        component: str,
        old_params: Dict,
        new_params: Dict,
        improvement: float,
        confidence: float,
    ) -> str:
        """
        Apply optimization with cryptographic proof.
        Returns optimization ID.
        """
        # Create optimization record
        opt_id = f"OPT-{hashlib.sha256(str(new_params).encode()).hexdigest()[:8]}"

        opt = Optimization(
            id=opt_id,
            timestamp=dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            component=component,
            old_params=old_params,
            new_params=new_params,
            improvement=improvement,
            confidence=confidence,
            proof_hash="",
        )

        # Create proof
        proof = {
            "optimization_id": opt_id,
            "component": component,
            "timestamp": opt.timestamp,
            "old_hash": hashlib.sha256(str(old_params).encode()).hexdigest(),
            "new_hash": hashlib.sha256(str(new_params).encode()).hexdigest(),
            "improvement": improvement,
            "confidence": confidence,
        }

        # Sign proof
        proof_bytes = json.dumps(proof, sort_keys=True).encode()
        proof["signature"] = hmac.new(
            self.mesh_key, proof_bytes, hashlib.sha256
        ).hexdigest()

        # Store proof
        proof_hash = hashlib.sha256(proof_bytes).hexdigest()
        path = os.path.join(self.cas_path, f"{proof_hash}.proof")
        with open(path, "w") as f:
            json.dump(proof, f, indent=2)

        # Update optimization record
        opt.proof_hash = proof_hash
        self.optimizations[opt_id] = opt
        self.merkle_roots.append(proof_hash)

        return opt_id

    def verify_optimization(self, opt_id: str) -> bool:
        """Verify cryptographic proof of optimization."""
        if opt_id not in self.optimizations:
            return False

        opt = self.optimizations[opt_id]

        # Load proof
        path = os.path.join(self.cas_path, f"{opt.proof_hash}.proof")
        if not os.path.exists(path):
            return False

        with open(path) as f:
            proof = json.load(f)

        # Verify signature
        proof_data = {k: v for k, v in proof.items() if k != "signature"}
        proof_bytes = json.dumps(proof_data, sort_keys=True).encode()

        expected_sig = hmac.new(self.mesh_key, proof_bytes, hashlib.sha256).hexdigest()

        return proof["signature"] == expected_sig

    def get_proof_root(self) -> str:
        """Get merkle root of all optimization proofs."""
        if not self.merkle_roots:
            return hashlib.sha256(b"").hexdigest()

        nodes = self.merkle_roots
        while len(nodes) > 1:
            pairs = [
                (nodes[i], nodes[i + 1] if i + 1 < len(nodes) else nodes[i])
                for i in range(0, len(nodes), 2)
            ]
            nodes = [
                hashlib.sha256(bytes.fromhex(a) + bytes.fromhex(b)).hexdigest()
                for a, b in pairs
            ]
        return nodes[0]
