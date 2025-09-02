#!/usr/bin/env python3
"""
EpochCore RAS ML Optimization System

Manages machine learning model optimization and performance enhancement.
Includes recursive improvement hooks for autonomous ML system enhancement.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
import random
from recursive_improvement import ImprovementStrategy, SubsystemHook, get_framework


class ModelType(Enum):
    """Types of ML models in the system."""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    NEURAL_NETWORK = "neural_network"
    ENSEMBLE = "ensemble"
    REINFORCEMENT = "reinforcement"


class ModelStatus(Enum):
    """Status of an ML model."""
    TRAINING = "training"
    READY = "ready"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"


class MLModel:
    """Represents a machine learning model."""
    
    def __init__(self, model_id: str, name: str, model_type: ModelType):
        self.id = model_id
        self.name = name
        self.type = model_type
        self.status = ModelStatus.TRAINING
        self.created_at = datetime.now()
        self.last_trained = None
        self.last_evaluated = None
        self.version = "1.0"
        
        # Performance metrics
        self.accuracy = 0.0
        self.precision = 0.0
        self.recall = 0.0
        self.f1_score = 0.0
        self.training_time = 0
        self.inference_time = 0.0  # ms per prediction
        
        # Resource usage
        self.memory_usage_mb = 0
        self.cpu_utilization = 0.0
        self.gpu_utilization = 0.0
        
        # Usage statistics
        self.prediction_count = 0
        self.deployment_uptime = 0  # hours
        self.error_rate = 0.0
        
    def to_dict(self) -> Dict:
        """Convert model to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "status": self.status.value,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "last_trained": self.last_trained.isoformat() if self.last_trained else None,
            "last_evaluated": self.last_evaluated.isoformat() if self.last_evaluated else None,
            "performance": {
                "accuracy": self.accuracy,
                "precision": self.precision,
                "recall": self.recall,
                "f1_score": self.f1_score,
                "training_time": self.training_time,
                "inference_time": self.inference_time
            },
            "resource_usage": {
                "memory_usage_mb": self.memory_usage_mb,
                "cpu_utilization": self.cpu_utilization,
                "gpu_utilization": self.gpu_utilization
            },
            "usage_stats": {
                "prediction_count": self.prediction_count,
                "deployment_uptime": self.deployment_uptime,
                "error_rate": self.error_rate
            }
        }


class MLOptimizationManager:
    """Manager for ML model optimization and enhancement."""
    
    def __init__(self):
        self.models = {}
        self.training_queue = []
        self.optimization_history = []
        self.system_metrics = {
            "total_models": 0,
            "deployed_models": 0,
            "avg_accuracy": 0.0,
            "avg_inference_time": 0.0,
            "total_predictions": 0,
            "system_load": 0.0
        }
        
        # Initialize with sample models
        self._initialize_sample_models()
        
    def _initialize_sample_models(self):
        """Initialize with sample ML models for demonstration."""
        sample_models = [
            ("ml_001", "User Classification Model", ModelType.CLASSIFICATION),
            ("ml_002", "Revenue Prediction Model", ModelType.REGRESSION), 
            ("ml_003", "Content Clustering Model", ModelType.CLUSTERING),
            ("ml_004", "Recommendation Network", ModelType.NEURAL_NETWORK),
            ("ml_005", "Fraud Detection Ensemble", ModelType.ENSEMBLE)
        ]
        
        for model_id, name, model_type in sample_models:
            model = MLModel(model_id, name, model_type)
            
            # Simulate model training and performance
            model.status = random.choice([ModelStatus.READY, ModelStatus.DEPLOYED])
            model.last_trained = datetime.now() - timedelta(days=random.randint(1, 30))
            model.last_evaluated = datetime.now() - timedelta(days=random.randint(1, 7))
            
            # Generate realistic performance metrics
            base_accuracy = 0.70 + random.random() * 0.25  # 70-95%
            model.accuracy = base_accuracy
            model.precision = base_accuracy + random.uniform(-0.05, 0.05)
            model.recall = base_accuracy + random.uniform(-0.05, 0.05)
            model.f1_score = 2 * (model.precision * model.recall) / (model.precision + model.recall)
            
            model.training_time = random.randint(300, 3600)  # 5min to 1hr
            model.inference_time = random.uniform(1.0, 50.0)  # 1-50ms
            
            # Resource usage
            model.memory_usage_mb = random.randint(100, 2000)
            model.cpu_utilization = random.uniform(0.1, 0.8)
            model.gpu_utilization = random.uniform(0.0, 0.9) if random.random() > 0.3 else 0.0
            
            # Usage statistics
            if model.status == ModelStatus.DEPLOYED:
                model.prediction_count = random.randint(1000, 100000)
                model.deployment_uptime = random.randint(24, 720)  # 1-30 days
                model.error_rate = random.uniform(0.001, 0.05)  # 0.1-5%
                
            self.models[model.id] = model
            
        self._update_system_metrics()
        
    def _update_system_metrics(self):
        """Update system-wide metrics."""
        if not self.models:
            return
            
        deployed_models = [m for m in self.models.values() if m.status == ModelStatus.DEPLOYED]
        
        self.system_metrics.update({
            "total_models": len(self.models),
            "deployed_models": len(deployed_models),
            "avg_accuracy": sum(m.accuracy for m in self.models.values()) / len(self.models),
            "avg_inference_time": sum(m.inference_time for m in self.models.values()) / len(self.models),
            "total_predictions": sum(m.prediction_count for m in deployed_models),
            "system_load": sum(m.cpu_utilization for m in deployed_models) / max(len(deployed_models), 1)
        })
        
    def optimize_model_performance(self, model_id: str) -> Dict:
        """Optimize a specific model's performance."""
        if model_id not in self.models:
            return {"status": "error", "message": f"Model {model_id} not found"}
            
        model = self.models[model_id]
        old_performance = model.to_dict()["performance"].copy()
        
        # Simulate performance optimization
        improvement_factor = 1.05 + random.uniform(0, 0.1)  # 5-15% improvement
        
        # Improve accuracy metrics
        model.accuracy = min(0.99, model.accuracy * improvement_factor)
        model.precision = min(0.99, model.precision * improvement_factor)
        model.recall = min(0.99, model.recall * improvement_factor)
        model.f1_score = 2 * (model.precision * model.recall) / (model.precision + model.recall)
        
        # Optimize inference time
        model.inference_time = max(0.5, model.inference_time * 0.9)  # 10% faster
        
        # Update resource efficiency
        model.memory_usage_mb = max(50, int(model.memory_usage_mb * 0.95))  # 5% less memory
        model.cpu_utilization = max(0.05, model.cpu_utilization * 0.92)  # 8% less CPU
        
        model.last_evaluated = datetime.now()
        
        optimization_record = {
            "model_id": model_id,
            "timestamp": datetime.now().isoformat(),
            "old_performance": old_performance,
            "new_performance": model.to_dict()["performance"],
            "improvements": {
                "accuracy_gain": model.accuracy - old_performance["accuracy"],
                "inference_speedup": old_performance["inference_time"] - model.inference_time,
                "memory_reduction": old_performance.get("memory_usage_mb", 0) - model.memory_usage_mb
            }
        }
        
        self.optimization_history.append(optimization_record)
        self._update_system_metrics()
        
        return {
            "status": "success",
            "optimization": optimization_record
        }
        
    def retrain_underperforming_models(self) -> Dict:
        """Identify and retrain models with poor performance."""
        avg_accuracy = self.system_metrics["avg_accuracy"]
        underperforming = []
        
        for model in self.models.values():
            if (model.accuracy < avg_accuracy * 0.85 or  # 15% below average
                model.error_rate > 0.03 or  # >3% error rate
                (model.last_trained and 
                 (datetime.now() - model.last_trained).days > 60)):  # Not trained in 60 days
                underperforming.append(model)
                
        retraining_results = []
        for model in underperforming[:3]:  # Retrain up to 3 models
            old_accuracy = model.accuracy
            old_error_rate = model.error_rate
            
            # Simulate retraining
            model.accuracy = min(0.95, old_accuracy + random.uniform(0.02, 0.08))
            model.error_rate = max(0.001, old_error_rate * 0.5)
            model.last_trained = datetime.now()
            model.training_time = random.randint(300, 1800)
            
            retraining_results.append({
                "model_id": model.id,
                "old_accuracy": old_accuracy,
                "new_accuracy": model.accuracy,
                "old_error_rate": old_error_rate,
                "new_error_rate": model.error_rate,
                "training_time": model.training_time
            })
            
        self._update_system_metrics()
        
        return {
            "models_retrained": len(retraining_results),
            "results": retraining_results
        }
        
    def get_system_state(self) -> Dict:
        """Get comprehensive ML system state."""
        # Model distribution by type
        type_distribution = {}
        for model_type in ModelType:
            type_distribution[model_type.value] = sum(1 for m in self.models.values() 
                                                     if m.type == model_type)
            
        # Model distribution by status
        status_distribution = {}
        for status in ModelStatus:
            status_distribution[status.value] = sum(1 for m in self.models.values()
                                                   if m.status == status)
            
        # Performance distribution
        performance_stats = {
            "accuracy": {
                "min": min(m.accuracy for m in self.models.values()) if self.models else 0,
                "max": max(m.accuracy for m in self.models.values()) if self.models else 0,
                "avg": self.system_metrics["avg_accuracy"]
            },
            "inference_time": {
                "min": min(m.inference_time for m in self.models.values()) if self.models else 0,
                "max": max(m.inference_time for m in self.models.values()) if self.models else 0,
                "avg": self.system_metrics["avg_inference_time"]
            }
        }
        
        # Resource utilization
        total_memory = sum(m.memory_usage_mb for m in self.models.values())
        avg_cpu = sum(m.cpu_utilization for m in self.models.values()) / len(self.models) if self.models else 0
        avg_gpu = sum(m.gpu_utilization for m in self.models.values() if m.gpu_utilization > 0)
        gpu_models = sum(1 for m in self.models.values() if m.gpu_utilization > 0)
        avg_gpu = avg_gpu / gpu_models if gpu_models > 0 else 0
        
        return {
            "system_metrics": self.system_metrics,
            "type_distribution": type_distribution,
            "status_distribution": status_distribution,
            "performance_stats": performance_stats,
            "resource_utilization": {
                "total_memory_mb": total_memory,
                "avg_cpu_utilization": avg_cpu,
                "avg_gpu_utilization": avg_gpu,
                "gpu_enabled_models": gpu_models
            },
            "models": {mid: model.to_dict() for mid, model in self.models.items()},
            "recent_optimizations": self.optimization_history[-10:],
            "timestamp": datetime.now().isoformat()
        }


class ModelPerformanceOptimizationStrategy(ImprovementStrategy):
    """Strategy for optimizing ML model performance."""
    
    def get_name(self) -> str:
        return "ml_model_performance_optimization"
        
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze ML models and identify performance optimization opportunities."""
        opportunities = {
            "improvements_available": False,
            "underperforming_models": [],
            "resource_inefficiencies": [],
            "optimization_potential": 0.0
        }
        
        models_data = subsystem_state.get("models", {})
        performance_stats = subsystem_state.get("performance_stats", {})
        avg_accuracy = performance_stats.get("accuracy", {}).get("avg", 0.8)
        avg_inference_time = performance_stats.get("inference_time", {}).get("avg", 20.0)
        
        # Identify underperforming models
        for model_id, model_data in models_data.items():
            performance = model_data.get("performance", {})
            resource_usage = model_data.get("resource_usage", {})
            
            accuracy = performance.get("accuracy", 0.0)
            inference_time = performance.get("inference_time", 0.0)
            memory_usage = resource_usage.get("memory_usage_mb", 0)
            
            # Check for low accuracy
            if accuracy < avg_accuracy * 0.9:  # 10% below average
                opportunities["underperforming_models"].append({
                    "model_id": model_id,
                    "issue": "low_accuracy",
                    "current_accuracy": accuracy,
                    "target_accuracy": avg_accuracy,
                    "improvement_needed": avg_accuracy - accuracy
                })
                
            # Check for slow inference
            if inference_time > avg_inference_time * 1.5:  # 50% slower than average
                opportunities["underperforming_models"].append({
                    "model_id": model_id,
                    "issue": "slow_inference",
                    "current_inference_time": inference_time,
                    "target_inference_time": avg_inference_time,
                    "speedup_needed": inference_time - avg_inference_time
                })
                
            # Check for high resource usage
            if memory_usage > 1000:  # >1GB memory
                opportunities["resource_inefficiencies"].append({
                    "model_id": model_id,
                    "issue": "high_memory_usage",
                    "current_memory_mb": memory_usage,
                    "target_memory_mb": 800,
                    "reduction_needed": memory_usage - 800
                })
                
        if opportunities["underperforming_models"] or opportunities["resource_inefficiencies"]:
            opportunities["improvements_available"] = True
            opportunities["optimization_potential"] = (
                len(opportunities["underperforming_models"]) * 0.15 +
                len(opportunities["resource_inefficiencies"]) * 0.1
            )
            
        return opportunities
        
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute ML model performance improvements."""
        improved_state = subsystem_state.copy()
        improvements_made = []
        
        # Optimize underperforming models
        for underperformer in opportunities.get("underperforming_models", []):
            model_id = underperformer["model_id"]
            if model_id in improved_state["models"]:
                issue = underperformer["issue"]
                
                if issue == "low_accuracy":
                    old_accuracy = improved_state["models"][model_id]["performance"]["accuracy"]
                    improvement = min(0.1, underperformer["improvement_needed"])
                    new_accuracy = min(0.99, old_accuracy + improvement)
                    improved_state["models"][model_id]["performance"]["accuracy"] = new_accuracy
                    
                    improvements_made.append({
                        "type": "accuracy_improvement",
                        "model_id": model_id,
                        "old_accuracy": old_accuracy,
                        "new_accuracy": new_accuracy
                    })
                    
                elif issue == "slow_inference":
                    old_time = improved_state["models"][model_id]["performance"]["inference_time"]
                    speedup_factor = 0.8  # 20% faster
                    new_time = max(0.5, old_time * speedup_factor)
                    improved_state["models"][model_id]["performance"]["inference_time"] = new_time
                    
                    improvements_made.append({
                        "type": "inference_speedup",
                        "model_id": model_id,
                        "old_inference_time": old_time,
                        "new_inference_time": new_time
                    })
                    
        # Optimize resource usage
        for inefficiency in opportunities.get("resource_inefficiencies", []):
            model_id = inefficiency["model_id"]
            if model_id in improved_state["models"]:
                if inefficiency["issue"] == "high_memory_usage":
                    old_memory = improved_state["models"][model_id]["resource_usage"]["memory_usage_mb"]
                    reduction = min(200, inefficiency["reduction_needed"])
                    new_memory = max(50, old_memory - reduction)
                    improved_state["models"][model_id]["resource_usage"]["memory_usage_mb"] = new_memory
                    
                    improvements_made.append({
                        "type": "memory_optimization",
                        "model_id": model_id,
                        "old_memory_mb": old_memory,
                        "new_memory_mb": new_memory
                    })
                    
        # Recalculate system metrics
        if improvements_made:
            models = improved_state["models"].values()
            total_models = len(models)
            
            if total_models > 0:
                improved_state["system_metrics"]["avg_accuracy"] = sum(
                    m["performance"]["accuracy"] for m in models
                ) / total_models
                
                improved_state["system_metrics"]["avg_inference_time"] = sum(
                    m["performance"]["inference_time"] for m in models  
                ) / total_models
                
                # Update performance stats
                accuracies = [m["performance"]["accuracy"] for m in models]
                inference_times = [m["performance"]["inference_time"] for m in models]
                
                improved_state["performance_stats"]["accuracy"] = {
                    "min": min(accuracies),
                    "max": max(accuracies),
                    "avg": sum(accuracies) / len(accuracies)
                }
                
                improved_state["performance_stats"]["inference_time"] = {
                    "min": min(inference_times),
                    "max": max(inference_times), 
                    "avg": sum(inference_times) / len(inference_times)
                }
                
        improved_state["improvements_made"] = improvements_made
        improved_state["timestamp"] = datetime.now().isoformat()
        
        return improved_state


class MLResourceOptimizationStrategy(ImprovementStrategy):
    """Strategy for optimizing ML resource utilization."""
    
    def get_name(self) -> str:
        return "ml_resource_optimization"
        
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze resource utilization and identify optimization opportunities."""
        opportunities = {
            "improvements_available": False,
            "resource_bottlenecks": [],
            "scaling_opportunities": [],
            "optimization_potential": 0.0
        }
        
        resource_util = subsystem_state.get("resource_utilization", {})
        system_metrics = subsystem_state.get("system_metrics", {})
        
        total_memory = resource_util.get("total_memory_mb", 0)
        avg_cpu = resource_util.get("avg_cpu_utilization", 0.0)
        system_load = system_metrics.get("system_load", 0.0)
        
        # Check for resource bottlenecks
        if total_memory > 8000:  # >8GB total memory usage
            opportunities["resource_bottlenecks"].append({
                "type": "high_memory_usage",
                "current_usage_mb": total_memory,
                "target_usage_mb": 6000,
                "reduction_needed": total_memory - 6000
            })
            
        if avg_cpu > 0.8:  # >80% CPU utilization
            opportunities["resource_bottlenecks"].append({
                "type": "high_cpu_utilization",
                "current_utilization": avg_cpu,
                "target_utilization": 0.6,
                "reduction_needed": avg_cpu - 0.6
            })
            
        if system_load > 0.7:  # >70% system load
            opportunities["scaling_opportunities"].append({
                "type": "system_overload",
                "current_load": system_load,
                "recommendation": "Scale horizontally or optimize models"
            })
            
        if opportunities["resource_bottlenecks"] or opportunities["scaling_opportunities"]:
            opportunities["improvements_available"] = True
            opportunities["optimization_potential"] = (
                len(opportunities["resource_bottlenecks"]) * 0.2 +
                len(opportunities["scaling_opportunities"]) * 0.15
            )
            
        return opportunities
        
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute resource optimization improvements."""
        improved_state = subsystem_state.copy()
        improvements_made = []
        
        # Address resource bottlenecks
        for bottleneck in opportunities.get("resource_bottlenecks", []):
            if bottleneck["type"] == "high_memory_usage":
                old_total = improved_state["resource_utilization"]["total_memory_mb"]
                reduction = min(1500, bottleneck["reduction_needed"])
                new_total = max(1000, old_total - reduction)
                improved_state["resource_utilization"]["total_memory_mb"] = new_total
                
                improvements_made.append({
                    "type": "memory_consolidation",
                    "old_total_memory_mb": old_total,
                    "new_total_memory_mb": new_total,
                    "memory_saved_mb": old_total - new_total
                })
                
            elif bottleneck["type"] == "high_cpu_utilization":
                old_cpu = improved_state["resource_utilization"]["avg_cpu_utilization"]
                reduction = min(0.2, bottleneck["reduction_needed"])
                new_cpu = max(0.1, old_cpu - reduction)
                improved_state["resource_utilization"]["avg_cpu_utilization"] = new_cpu
                
                improvements_made.append({
                    "type": "cpu_optimization", 
                    "old_cpu_utilization": old_cpu,
                    "new_cpu_utilization": new_cpu
                })
                
        # Handle scaling opportunities
        for scaling_opp in opportunities.get("scaling_opportunities", []):
            if scaling_opp["type"] == "system_overload":
                old_load = improved_state["system_metrics"]["system_load"]
                # Simulate load reduction through optimization
                new_load = max(0.3, old_load * 0.8)  # 20% load reduction
                improved_state["system_metrics"]["system_load"] = new_load
                
                improvements_made.append({
                    "type": "load_balancing",
                    "old_system_load": old_load,
                    "new_system_load": new_load
                })
                
        improved_state["improvements_made"] = improvements_made
        improved_state["timestamp"] = datetime.now().isoformat()
        
        return improved_state


# Global ML optimization manager instance
_ml_manager = None


def get_ml_manager() -> MLOptimizationManager:
    """Get or create the global ML optimization manager."""
    global _ml_manager
    if _ml_manager is None:
        _ml_manager = MLOptimizationManager()
    return _ml_manager


def initialize_ml_optimization() -> SubsystemHook:
    """Initialize ML optimization with recursive improvement hooks."""
    manager = get_ml_manager()
    
    # Create improvement strategies
    strategies = [
        ModelPerformanceOptimizationStrategy(),
        MLResourceOptimizationStrategy()
    ]
    
    # Create subsystem hook
    hook = SubsystemHook(
        name="ml",
        get_state_func=manager.get_system_state,
        improvement_strategies=strategies
    )
    
    # Register with the framework
    framework = get_framework()
    framework.register_subsystem(hook)
    
    return hook


# Example usage functions
def improve_ml_system() -> Dict:
    """Manual trigger for ML system improvement."""
    framework = get_framework()
    return framework.run_manual_improvement("ml")


def get_ml_status() -> Dict:
    """Get current ML system status."""
    manager = get_ml_manager()
    return manager.get_system_state()


def optimize_specific_model(model_id: str) -> Dict:
    """Optimize a specific ML model."""
    manager = get_ml_manager()
    return manager.optimize_model_performance(model_id)


if __name__ == "__main__":
    # Demo the ML optimization system
    print("🤖 EpochCore RAS ML Optimization Demo")
    print("=" * 50)
    
    # Initialize
    hook = initialize_ml_optimization()
    manager = get_ml_manager()
    
    print("\n📊 Initial ML Status:")
    status = get_ml_status()
    print(f"  Total Models: {status['system_metrics']['total_models']}")
    print(f"  Deployed Models: {status['system_metrics']['deployed_models']}")
    print(f"  Average Accuracy: {status['system_metrics']['avg_accuracy']:.1%}")
    print(f"  Average Inference Time: {status['system_metrics']['avg_inference_time']:.1f}ms")
    print(f"  System Load: {status['system_metrics']['system_load']:.1%}")
    
    print("\n🔧 Running Improvement Cycle...")
    improvement_result = improve_ml_system()
    
    print(f"\n✅ Improvement Result: {improvement_result['status']}")
    if improvement_result['status'] == 'success':
        for improvement in improvement_result['improvements']:
            print(f"  Strategy: {improvement['strategy']}")
            if 'improvements_made' in improvement['after_state']:
                for imp in improvement['after_state']['improvements_made']:
                    print(f"    - {imp}")
    
    print("\n📊 Final ML Status:")
    final_status = get_ml_status()
    print(f"  Total Models: {final_status['system_metrics']['total_models']}")
    print(f"  Deployed Models: {final_status['system_metrics']['deployed_models']}")
    print(f"  Average Accuracy: {final_status['system_metrics']['avg_accuracy']:.1%}")
    print(f"  Average Inference Time: {final_status['system_metrics']['avg_inference_time']:.1f}ms")
    print(f"  System Load: {final_status['system_metrics']['system_load']:.1%}")