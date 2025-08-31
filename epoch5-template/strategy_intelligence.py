from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass
import joblib
from sklearn.ensemble import RandomForestRegressor
import pickle
from pathlib import Path
import time

@dataclass
class TaskMetrics:
    task_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    success_rate: float
    complexity_score: float

class StrategyIntelligence:
    """Intelligence layer for optimizing task execution"""
    
    def __init__(self, model_dir: str = ".models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.task_history: List[TaskMetrics] = []
        self.performance_model = RandomForestRegressor()
        self.pattern_memory: Dict[str, List[float]] = {}
        self.resource_weights: Dict[str, float] = {}
        
    def analyze_task_pattern(self, task_metrics: List[TaskMetrics]) -> Dict[str, Any]:
        """Identify patterns in task execution"""
        patterns = {}
        for metric in task_metrics:
            if metric.task_name not in self.pattern_memory:
                self.pattern_memory[metric.task_name] = []
            
            # Calculate efficiency score
            efficiency = (metric.success_rate * 100) / (metric.execution_time + 1)
            self.pattern_memory[metric.task_name].append(efficiency)
            
            # Analyze trends
            history = self.pattern_memory[metric.task_name]
            patterns[metric.task_name] = {
                "trend": np.gradient(history).mean() if len(history) > 1 else 0,
                "volatility": np.std(history) if len(history) > 1 else 0,
                "avg_efficiency": np.mean(history)
            }
        
        return patterns
        
    def optimize_resource_allocation(self, 
                                   patterns: Dict[str, Any],
                                   available_resources: float) -> Dict[str, float]:
        """Optimize resource allocation based on task patterns"""
        total_efficiency = sum(p["avg_efficiency"] for p in patterns.values())
        
        # Calculate resource weights based on efficiency and trends
        weights = {}
        for task, pattern in patterns.items():
            base_weight = pattern["avg_efficiency"] / total_efficiency if total_efficiency else 1
            trend_factor = 1 + (pattern["trend"] * 0.1)  # Adjust for positive/negative trends
            volatility_factor = 1 - (pattern["volatility"] * 0.05)  # Reduce allocation for volatile tasks
            
            weights[task] = base_weight * trend_factor * volatility_factor
            
        # Normalize weights
        weight_sum = sum(weights.values())
        self.resource_weights = {
            task: (weight / weight_sum) * available_resources
            for task, weight in weights.items()
        }
        
        return self.resource_weights
        
    def train_performance_model(self, metrics: List[TaskMetrics]):
        """Train ML model for performance prediction"""
        if not metrics:
            return
            
        X = [[m.memory_usage, m.cpu_usage, m.complexity_score] for m in metrics]
        y = [m.execution_time for m in metrics]
        
        self.performance_model.fit(X, y)
        joblib.dump(self.performance_model, self.model_dir / "performance_model.joblib")
        
    def predict_performance(self, 
                          memory_usage: float, 
                          cpu_usage: float, 
                          complexity_score: float) -> float:
        """Predict task performance based on metrics"""
        return self.performance_model.predict([[memory_usage, cpu_usage, complexity_score]])[0]
        
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        for task_name, history in self.pattern_memory.items():
            if len(history) < 2:
                continue
                
            recent_efficiency = history[-1]
            avg_efficiency = np.mean(history)
            
            if recent_efficiency < avg_efficiency:
                recommendations.append({
                    "task_name": task_name,
                    "issue": "Efficiency Degradation",
                    "current_efficiency": recent_efficiency,
                    "average_efficiency": avg_efficiency,
                    "recommended_action": "Increase resource allocation",
                    "priority": "High" if (avg_efficiency - recent_efficiency) > 10 else "Medium"
                })
                
        return recommendations
