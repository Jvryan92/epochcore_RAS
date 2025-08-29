"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""Performance and resource optimization agent for the StrategyDECK system."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
import statistics
from ..core.base_agent import BaseAgent


class OptimizerAgent(BaseAgent):
    """Optimizer Agent for performance monitoring and resource optimization."""

    def __init__(self, name: str = "optimizer", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.performance_metrics = defaultdict(list)
        self.resource_usage = defaultdict(list)
        self.optimization_targets = {
            'latency': {'threshold': 300, 'weight': 0.4},
            'cpu_usage': {'threshold': 80, 'weight': 0.3},
            'memory_usage': {'threshold': 75, 'weight': 0.3}
        }
        
        # Subscribe to performance-related topics
        self.subscribe_to_topic('performance.metrics')
        self.subscribe_to_topic('resource.usage')
        self.subscribe_to_topic('optimization.request')
        self.subscribe_to_topic('system.health')

    def validate_config(self) -> bool:
        """Validate agent configuration."""
        required = ['monitoring_interval', 'optimization_threshold', 'target_slo']
        return all(key in self.config for key in required)

    def run(self) -> Dict[str, Any]:
        """Execute performance monitoring and optimization."""
        results = {
            'optimization_status': 'nominal',
            'performance_summary': {},
            'resource_status': {},
            'recommendations': []
        }

        try:
            # Collect performance metrics
            self._collect_performance_metrics()

            # Analyze resource usage
            resource_analysis = self._analyze_resource_usage()
            results['resource_status'] = resource_analysis

            # Generate performance summary
            perf_summary = self._generate_performance_summary()
            results['performance_summary'] = perf_summary

            # Check for optimization opportunities
            optimizations = self._identify_optimizations()
            results['recommendations'].extend(optimizations)

            # Process optimization requests
            opt_requests = self.get_messages('optimization.request')
            if opt_requests:
                for request in opt_requests:
                    recommendation = self._handle_optimization_request(request)
                    results['recommendations'].append(recommendation)

            # Broadcast system health if critical
            if self._should_broadcast_health(perf_summary):
                self._broadcast_health_status(perf_summary)

            return results

        except Exception as e:
            self.logger.error(f"Performance optimization failed: {str(e)}")
            results['optimization_status'] = 'error'
            results['error'] = str(e)
            return results

    def _collect_performance_metrics(self) -> None:
        """Collect and process performance metrics from various sources."""
        perf_messages = self.get_messages('performance.metrics')
        for msg in perf_messages:
            metrics = msg.get('data', {})
            for metric_name, value in metrics.items():
                self.performance_metrics[metric_name].append({
                    'value': value,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                # Trim old metrics
                max_history = self.config.get('metrics_history', 1000)
                if len(self.performance_metrics[metric_name]) > max_history:
                    self.performance_metrics[metric_name] = \
                        self.performance_metrics[metric_name][-max_history:]

    def _analyze_resource_usage(self) -> Dict[str, Any]:
        """Analyze current resource usage patterns."""
        analysis = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'resources': {},
            'anomalies': []
        }

        resource_msgs = self.get_messages('resource.usage')
        for msg in resource_msgs:
            resource_data = msg.get('data', {})
            for resource, usage in resource_data.items():
                self.resource_usage[resource].append({
                    'value': usage,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
                
                # Detect anomalies
                anomaly = self._detect_resource_anomaly(resource)
                if anomaly:
                    analysis['anomalies'].append(anomaly)
                
                # Calculate resource metrics
                recent_usage = [
                    u['value'] for u in self.resource_usage[resource][-10:]
                ]
                if recent_usage:
                    analysis['resources'][resource] = {
                        'current': recent_usage[-1],
                        'average': statistics.mean(recent_usage),
                        'peak': max(recent_usage),
                        'trend': self._calculate_trend(recent_usage)
                    }

        return analysis

    def _generate_performance_summary(self) -> Dict[str, Any]:
        """Generate a summary of current performance metrics."""
        summary = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': {},
            'slo_status': 'meeting',
            'critical_paths': []
        }

        for metric, values in self.performance_metrics.items():
            if not values:
                continue
                
            recent_values = [v['value'] for v in values[-10:]]
            metric_summary = {
                'current': recent_values[-1],
                'avg': statistics.mean(recent_values),
                'p95': self._calculate_percentile(recent_values, 95),
                'trend': self._calculate_trend(recent_values)
            }
            
            # Check SLO
            target_slo = self.config.get('target_slo', {}).get(metric)
            if target_slo and metric_summary['p95'] > target_slo:
                summary['slo_status'] = 'breaching'
                summary['critical_paths'].append(metric)
                
            summary['metrics'][metric] = metric_summary

        return summary

    def _identify_optimizations(self) -> List[Dict[str, Any]]:
        """Identify potential optimization opportunities."""
        recommendations = []
        
        # Check each optimization target
        for target, config in self.optimization_targets.items():
            if target not in self.performance_metrics:
                continue
                
            recent_metrics = [
                m['value'] for m in self.performance_metrics[target][-10:]
            ]
            if not recent_metrics:
                continue
                
            current = recent_metrics[-1]
            threshold = config['threshold']
            
            if current > threshold:
                recommendations.append({
                    'target': target,
                    'priority': 'high',
                    'current_value': current,
                    'threshold': threshold,
                    'suggestion': self._get_optimization_suggestion(target, current)
                })
                
        return recommendations

    def _handle_optimization_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process an optimization request."""
        request_data = request.get('data', {})
        target = request_data.get('target')
        constraint = request_data.get('constraint')
        
        recommendation = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'target': target,
            'status': 'processed'
        }

        try:
            if target in self.performance_metrics:
                current_value = self.performance_metrics[target][-1]['value']
                recommendation.update({
                    'current_value': current_value,
                    'optimization': self._get_optimization_suggestion(
                        target, current_value, constraint
                    )
                })
            else:
                recommendation['status'] = 'invalid_target'
                
        except Exception as e:
            recommendation['status'] = 'error'
            recommendation['error'] = str(e)
            
        return recommendation

    def _get_optimization_suggestion(
        self, 
        target: str, 
        current_value: float,
        constraint: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate an optimization suggestion for a specific target."""
        suggestion = {
            'type': 'optimization',
            'target': target,
            'actions': []
        }

        if target == 'latency':
            if current_value > 300:  # High latency
                suggestion['actions'].extend([
                    {'action': 'increase_cache_size', 'impact': 'medium'},
                    {'action': 'optimize_db_queries', 'impact': 'high'},
                    {'action': 'enable_compression', 'impact': 'medium'}
                ])
                
        elif target == 'cpu_usage':
            if current_value > 80:  # High CPU
                suggestion['actions'].extend([
                    {'action': 'scale_horizontally', 'impact': 'high'},
                    {'action': 'enable_request_throttling', 'impact': 'medium'},
                    {'action': 'optimize_compute_intensive_operations', 'impact': 'high'}
                ])
                
        elif target == 'memory_usage':
            if current_value > 75:  # High memory
                suggestion['actions'].extend([
                    {'action': 'increase_memory_limit', 'impact': 'high'},
                    {'action': 'implement_memory_caching', 'impact': 'medium'},
                    {'action': 'optimize_memory_intensive_operations', 'impact': 'high'}
                ])

        # Apply constraints if provided
        if constraint:
            suggestion['actions'] = [
                action for action in suggestion['actions']
                if self._validate_constraint(action, constraint)
            ]

        return suggestion

    def _validate_constraint(
        self, 
        action: Dict[str, str], 
        constraint: Dict[str, Any]
    ) -> bool:
        """Validate if an optimization action meets given constraints."""
        if 'max_impact' in constraint:
            impact_levels = {'low': 1, 'medium': 2, 'high': 3}
            action_impact = impact_levels.get(action['impact'], 0)
            max_impact = impact_levels.get(constraint['max_impact'], 0)
            return action_impact <= max_impact
            
        return True

    def _detect_resource_anomaly(self, resource: str) -> Optional[Dict[str, Any]]:
        """Detect anomalies in resource usage patterns."""
        if len(self.resource_usage[resource]) < 10:
            return None

        recent_usage = [
            u['value'] for u in self.resource_usage[resource][-10:]
        ]
        avg = statistics.mean(recent_usage)
        stdev = statistics.stdev(recent_usage) if len(recent_usage) > 1 else 0

        current = recent_usage[-1]
        if abs(current - avg) > 2 * stdev:  # Simple z-score anomaly detection
            return {
                'resource': resource,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'value': current,
                'average': avg,
                'deviation': abs(current - avg)
            }

        return None

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values."""
        if len(values) < 2:
            return 'stable'
            
        changes = [b - a for a, b in zip(values[:-1], values[1:])]
        avg_change = statistics.mean(changes)
        
        if abs(avg_change) < 0.05:  # Small change threshold
            return 'stable'
        return 'increasing' if avg_change > 0 else 'decreasing'

    def _calculate_percentile(
        self, 
        values: List[float], 
        percentile: float
    ) -> float:
        """Calculate a percentile value from a list of numbers."""
        sorted_values = sorted(values)
        index = (len(sorted_values) - 1) * percentile / 100
        floor = int(index)
        
        if floor == index:
            return sorted_values[floor]
            
        ceil = floor + 1
        floor_val = sorted_values[floor] * (ceil - index)
        ceil_val = sorted_values[ceil] * (index - floor)
        return floor_val + ceil_val

    def _should_broadcast_health(self, summary: Dict[str, Any]) -> bool:
        """Determine if health status should be broadcast."""
        return (
            summary.get('slo_status') == 'breaching' or
            len(summary.get('critical_paths', [])) > 0
        )

    def _broadcast_health_status(self, summary: Dict[str, Any]) -> None:
        """Broadcast system health status to interested agents."""
        health_status = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': summary['slo_status'],
            'critical_paths': summary.get('critical_paths', []),
            'metrics': summary.get('metrics', {})
        }
        
        self.send_message(
            None,
            'system.health',
            health_status,
            priority='high'
        )
