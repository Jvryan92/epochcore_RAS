"""
Recursive Logger - Advanced logging system for tracking all recursive improvements
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading


class RecursiveLogger:
    """Advanced logging system for recursive improvement tracking."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.general_log = self.log_dir / "recursive_improvements.log"
        self.metrics_log = self.log_dir / "metrics.json"
        self.actions_log = self.log_dir / "actions.json"
        
        self.metrics_data = []
        self.actions_data = []
        self._lock = threading.Lock()
        
        # Set up main logger
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.general_log),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger("recursive_logger")
    
    def log_action(self, engine_name: str, action_type: str, 
                   result: Dict[str, Any], metadata: Dict[str, Any] = None):
        """Log a recursive action execution."""
        with self._lock:
            action_entry = {
                "timestamp": datetime.now().isoformat(),
                "engine": engine_name,
                "action_type": action_type,
                "result": result,
                "metadata": metadata or {}
            }
            
            self.actions_data.append(action_entry)
            self._save_json_log(self.actions_log, self.actions_data)
            
            self.logger.info(f"Action logged: {engine_name}.{action_type}")
    
    def log_metric(self, metric_name: str, value: Any, 
                   engine_name: str = None, tags: Dict[str, str] = None):
        """Log a metric for tracking improvements."""
        with self._lock:
            metric_entry = {
                "timestamp": datetime.now().isoformat(),
                "metric": metric_name,
                "value": value,
                "engine": engine_name,
                "tags": tags or {}
            }
            
            self.metrics_data.append(metric_entry)
            self._save_json_log(self.metrics_log, self.metrics_data)
            
            self.logger.info(f"Metric logged: {metric_name} = {value}")
    
    def log_compounding_action(self, engine_name: str, main_action: str, 
                              pre_action: str, overlap_duration: float):
        """Log compounding action with overlap timing."""
        metadata = {
            "main_action": main_action,
            "pre_action": pre_action,
            "overlap_duration_seconds": overlap_duration,
            "compounding": True
        }
        
        self.log_action(engine_name, "compounding_execution", {
            "status": "completed",
            "actions": [main_action, pre_action]
        }, metadata)
    
    def get_engine_metrics(self, engine_name: str, 
                          hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent metrics for a specific engine."""
        cutoff = datetime.now().timestamp() - (hours * 3600)
        
        return [
            metric for metric in self.metrics_data
            if metric.get("engine") == engine_name and
            datetime.fromisoformat(metric["timestamp"]).timestamp() > cutoff
        ]
    
    def get_action_history(self, engine_name: str = None, 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent action history."""
        actions = self.actions_data[-limit:]
        if engine_name:
            actions = [a for a in actions if a.get("engine") == engine_name]
        return actions
    
    def get_improvement_summary(self) -> Dict[str, Any]:
        """Generate a summary of recursive improvements."""
        with self._lock:
            total_actions = len(self.actions_data)
            engines = set(action.get("engine") for action in self.actions_data)
            
            recent_actions = [
                action for action in self.actions_data
                if (datetime.now() - datetime.fromisoformat(action["timestamp"])).days <= 7
            ]
            
            return {
                "total_actions": total_actions,
                "active_engines": len(engines),
                "engines": list(engines),
                "recent_actions_7d": len(recent_actions),
                "last_activity": self.actions_data[-1]["timestamp"] if self.actions_data else None
            }
    
    def _save_json_log(self, filepath: Path, data: List[Dict[str, Any]]):
        """Save JSON data to log file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save {filepath}: {e}")
    
    def cleanup_old_logs(self, days: int = 30):
        """Remove log entries older than specified days."""
        cutoff = datetime.now().timestamp() - (days * 24 * 3600)
        
        with self._lock:
            self.metrics_data = [
                metric for metric in self.metrics_data
                if datetime.fromisoformat(metric["timestamp"]).timestamp() > cutoff
            ]
            
            self.actions_data = [
                action for action in self.actions_data
                if datetime.fromisoformat(action["timestamp"]).timestamp() > cutoff
            ]
            
            self._save_json_log(self.metrics_log, self.metrics_data)
            self._save_json_log(self.actions_log, self.actions_data)
            
            self.logger.info(f"Cleaned up logs older than {days} days")