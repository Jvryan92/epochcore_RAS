"""
Recursive Scheduler - Manages timing and orchestration of recursive improvements
"""

import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging
import schedule

from .base import RecursiveEngine
from .logger import RecursiveLogger


class RecursiveScheduler:
    """Scheduler that manages recursive improvement engine execution."""
    
    def __init__(self, logger: RecursiveLogger):
        self.engines: Dict[str, RecursiveEngine] = {}
        self.logger_instance = logger
        self.logger = logging.getLogger("recursive.scheduler")
        self.is_running = False
        self.scheduler_thread = None
        
        # Schedule recurring tasks
        self._setup_schedules()
    
    def _setup_schedules(self):
        """Set up the basic scheduling framework."""
        # Weekly main cycles
        schedule.every().monday.at("02:00").do(self._execute_weekly_cycle)
        
        # Daily health checks
        schedule.every().day.at("01:00").do(self._daily_health_check)
        
        # Hourly metrics collection
        schedule.every().hour.do(self._collect_metrics)
    
    def register_engine(self, engine: RecursiveEngine):
        """Register a recursive engine for scheduling."""
        self.engines[engine.name] = engine
        self.logger.info(f"Registered engine: {engine.name}")
        
        # Start the engine
        if engine.start():
            self.logger.info(f"Engine {engine.name} started successfully")
        else:
            self.logger.error(f"Failed to start engine: {engine.name}")
    
    def start_scheduler(self):
        """Start the scheduler in a background thread."""
        if not self.is_running:
            self.is_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            self.logger.info("Recursive scheduler started")
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        # Stop all engines
        for engine in self.engines.values():
            engine.stop()
        
        self.logger.info("Recursive scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop."""
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Continue running even if there's an error
    
    def _execute_weekly_cycle(self):
        """Execute the weekly recursive improvement cycle."""
        self.logger.info("Starting weekly recursive improvement cycle")
        
        cycle_results = {
            "timestamp": datetime.now().isoformat(),
            "engines_executed": [],
            "total_actions": 0,
            "errors": []
        }
        
        # Execute all engines with compounding logic
        for engine_name, engine in self.engines.items():
            try:
                self.logger.info(f"Executing weekly cycle for {engine_name}")
                result = engine.execute_with_compounding()
                
                cycle_results["engines_executed"].append(engine_name)
                cycle_results["total_actions"] += len(result.get("actions_executed", []))
                
                # Log the execution
                self.logger_instance.log_action(
                    engine_name, 
                    "weekly_cycle", 
                    result,
                    {"cycle_type": "weekly", "scheduled": True}
                )
                
            except Exception as e:
                error_msg = f"Engine {engine_name} failed: {e}"
                cycle_results["errors"].append(error_msg)
                self.logger.error(error_msg)
        
        # Log overall cycle completion
        self.logger_instance.log_action(
            "scheduler",
            "weekly_cycle_complete",
            cycle_results,
            {"cycle_duration": "weekly", "compounding": True}
        )
        
        self.logger.info("Weekly recursive improvement cycle completed")
    
    def _daily_health_check(self):
        """Perform daily health check of all engines."""
        self.logger.info("Starting daily health check")
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "engines": {},
            "overall_health": "healthy"
        }
        
        for engine_name, engine in self.engines.items():
            engine_status = engine.get_status()
            health_report["engines"][engine_name] = engine_status
            
            # Check if engine is healthy
            if not engine_status["running"]:
                health_report["overall_health"] = "degraded"
                self.logger.warning(f"Engine {engine_name} is not running")
                
                # Try to restart the engine
                if engine.start():
                    self.logger.info(f"Successfully restarted engine {engine_name}")
                else:
                    self.logger.error(f"Failed to restart engine {engine_name}")
        
        # Log health check results
        self.logger_instance.log_action(
            "scheduler",
            "daily_health_check",
            health_report,
            {"check_type": "health", "automated": True}
        )
    
    def _collect_metrics(self):
        """Collect hourly metrics from all engines."""
        self.logger.debug("Collecting hourly metrics")
        
        for engine_name, engine in self.engines.items():
            try:
                status = engine.get_status()
                
                # Log key metrics
                self.logger_instance.log_metric(
                    f"{engine_name}_executions",
                    status["total_executions"],
                    engine_name,
                    {"metric_type": "execution_count"}
                )
                
                self.logger_instance.log_metric(
                    f"{engine_name}_running",
                    1 if status["running"] else 0,
                    engine_name,
                    {"metric_type": "health_status"}
                )
                
            except Exception as e:
                self.logger.error(f"Failed to collect metrics for {engine_name}: {e}")
    
    def execute_engine_now(self, engine_name: str) -> Dict[str, any]:
        """Manually trigger execution of a specific engine."""
        if engine_name not in self.engines:
            return {"error": f"Engine {engine_name} not found"}
        
        engine = self.engines[engine_name]
        result = engine.execute_with_compounding()
        
        self.logger_instance.log_action(
            engine_name,
            "manual_execution",
            result,
            {"triggered_by": "manual", "scheduler": True}
        )
        
        return result
    
    def get_scheduler_status(self) -> Dict[str, any]:
        """Get current scheduler status."""
        return {
            "running": self.is_running,
            "engines_registered": len(self.engines),
            "engines": {name: engine.get_status() for name, engine in self.engines.items()},
            "next_weekly_cycle": self._get_next_schedule_time("weekly"),
            "uptime": "active" if self.is_running else "stopped"
        }
    
    def _get_next_schedule_time(self, schedule_type: str) -> Optional[str]:
        """Get next scheduled execution time."""
        try:
            if schedule_type == "weekly":
                # Next Monday at 2 AM
                now = datetime.now()
                days_ahead = 0 - now.weekday()  # Monday is 0
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                next_monday = now + timedelta(days=days_ahead)
                next_execution = next_monday.replace(hour=2, minute=0, second=0, microsecond=0)
                return next_execution.isoformat()
        except Exception as e:
            self.logger.error(f"Failed to calculate next schedule time: {e}")
        
        return None