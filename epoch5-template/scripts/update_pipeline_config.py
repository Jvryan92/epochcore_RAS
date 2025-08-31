"""
Update pipeline configuration based on optimization analysis
"""
import yaml
import json
from typing import Dict, Any
from pathlib import Path

class PipelineConfigOptimizer:
    def __init__(self):
        self.workflow_file = Path(".github/workflows/epoch5-pipeline.yml")
        self.metrics_file = Path(".github/pipeline_metrics.json")
        self.optimization_file = Path(".github/optimization_history.json")
        
    def update_pipeline_config(self):
        """Update pipeline configuration with optimizations"""
        # Load current configuration
        with open(self.workflow_file, 'r') as f:
            config = yaml.safe_load(f)
            
        # Load metrics and optimizations
        metrics = self._load_metrics()
        optimizations = self._load_latest_optimizations()
        
        # Apply optimizations
        config = self._apply_job_parallelization(config, optimizations)
        config = self._apply_caching_strategy(config, optimizations)
        config = self._apply_resource_allocation(config, optimizations)
        config = self._apply_test_distribution(config, optimizations)
        config = self._apply_conditional_execution(config, optimizations)
        
        # Save updated configuration
        with open(self.workflow_file, 'w') as f:
            yaml.dump(config, f, sort_keys=False)
            
    def _load_metrics(self) -> Dict[str, Any]:
        """Load pipeline metrics"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {}
        
    def _load_latest_optimizations(self) -> Dict[str, Any]:
        """Load latest optimization suggestions"""
        if self.optimization_file.exists():
            with open(self.optimization_file, 'r') as f:
                history = json.load(f)
                if history:
                    return history[-1]["optimizations"]
        return {}
        
    def _apply_job_parallelization(self,
                                 config: Dict[str, Any],
                                 optimizations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply job parallelization optimizations"""
        parallel_jobs = optimizations.get("job_parallelization", {}).get("parallel_jobs", [])
        matrix_configs = optimizations.get("job_parallelization", {}).get("matrix_configs", {})
        
        for job_name in parallel_jobs:
            if job_name in config["jobs"]:
                # Add strategy matrix
                config["jobs"][job_name]["strategy"] = {
                    "fail-fast": false,
                    "matrix": {
                        "parallel": [1, 2, 3, 4]
                    }
                }
                
        for job_name, matrix_config in matrix_configs.items():
            if job_name in config["jobs"]:
                config["jobs"][job_name]["strategy"] = {
                    "fail-fast": false,
                    "max-parallel": matrix_config["max-parallel"],
                    "matrix": {
                        "split": matrix_config["split"]
                    }
                }
                
        return config
        
    def _apply_caching_strategy(self,
                              config: Dict[str, Any],
                              optimizations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply caching optimizations"""
        cache_updates = optimizations.get("cache_strategy", {})
        
        for job_name in cache_updates.get("improve_caching", []):
            if job_name in config["jobs"]:
                job = config["jobs"][job_name]
                
                # Update cache keys
                if job_name in cache_updates.get("cache_keys", {}):
                    cache_steps = [
                        step for step in job.get("steps", [])
                        if step.get("uses", "").startswith("actions/cache")
                    ]
                    
                    for step in cache_steps:
                        step["with"]["key"] = cache_updates["cache_keys"][job_name][0]
                        step["with"]["restore-keys"] = cache_updates["cache_keys"][job_name][1:]
                        
        return config
        
    def _apply_resource_allocation(self,
                                 config: Dict[str, Any],
                                 optimizations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply resource allocation optimizations"""
        resource_updates = optimizations.get("resource_allocation", {})
        
        for job_name, resource_class in resource_updates.get("resource_classes", {}).items():
            if job_name in config["jobs"]:
                if resource_class == "large":
                    config["jobs"][job_name]["runs-on"] = "ubuntu-latest-16-core"
                elif resource_class == "small":
                    config["jobs"][job_name]["runs-on"] = "ubuntu-latest-2-core"
                    
        return config
        
    def _apply_test_distribution(self,
                               config: Dict[str, Any],
                               optimizations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply test distribution optimizations"""
        test_updates = optimizations.get("test_distribution", {})
        
        for job_name, retry_config in test_updates.get("retry_config", {}).items():
            if job_name in config["jobs"]:
                job = config["jobs"][job_name]
                
                # Add test retry logic
                test_steps = [
                    step for step in job.get("steps", [])
                    if "test" in step.get("name", "").lower()
                ]
                
                for step in test_steps:
                    step["continue-on-error"] = True
                    step["id"] = f"{step.get('name', 'test')}_first_try"
                    
                    # Add retry step
                    retry_step = dict(step)
                    retry_step["if"] = f"failure() && steps.{step['id']}.outcome == 'failure'"
                    retry_step["id"] = f"{step['id']}_retry"
                    job["steps"].append(retry_step)
                    
        return config
        
    def _apply_conditional_execution(self,
                                   config: Dict[str, Any],
                                   optimizations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply conditional execution optimizations"""
        conditional_updates = optimizations.get("conditional_execution", {})
        
        for job_name, conditions in conditional_updates.get("conditional_config", {}).items():
            if job_name in config["jobs"]:
                job = config["jobs"][job_name]
                
                # Add path and branch conditions
                if "paths" in conditions:
                    if "on" not in config:
                        config["on"] = {}
                    if "push" not in config["on"]:
                        config["on"]["push"] = {}
                    config["on"]["push"]["paths"] = conditions["paths"]
                    
                if "branches" in conditions:
                    if "on" not in config:
                        config["on"] = {}
                    if "push" not in config["on"]:
                        config["on"]["push"] = {}
                    config["on"]["push"]["branches"] = conditions["branches"]
                    
        return config

def main():
    optimizer = PipelineConfigOptimizer()
    optimizer.update_pipeline_config()
    print("Pipeline configuration updated successfully")

if __name__ == "__main__":
    main()
