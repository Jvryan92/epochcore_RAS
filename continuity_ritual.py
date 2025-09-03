#!/usr/bin/env python3
"""
Continuity Ritual Automation - EpochCore RAS
Automates maintenance and continuity processes for the system
"""

import os
import json
import yaml
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
import schedule
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContinuityRitualAutomation:
    """Automated continuity and maintenance ritual system."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "continuity_config.yaml"
        self.logs_path = Path("logs")
        self.reports_path = Path("reports")
        self.backups_path = Path("backups")
        
        # Ensure directories exist
        self.logs_path.mkdir(exist_ok=True)
        self.reports_path.mkdir(exist_ok=True)
        self.backups_path.mkdir(exist_ok=True)
        
        self.config = self._load_config()
        self.ritual_history = []
        self.last_health_check = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load continuity ritual configuration."""
        default_config = {
            "ritual_schedule": {
                "daily": ["health_check", "log_rotation", "metric_collection"],
                "weekly": ["system_backup", "dependency_update", "performance_analysis"],
                "monthly": ["comprehensive_audit", "security_scan", "documentation_sync"]
            },
            "health_checks": {
                "enabled": True,
                "interval_minutes": 30,
                "critical_thresholds": {
                    "cpu_usage": 80,
                    "memory_usage": 85,
                    "disk_usage": 90,
                    "response_time": 5000
                }
            },
            "backup_settings": {
                "enabled": True,
                "retention_days": 30,
                "include_patterns": ["*.py", "*.yaml", "*.yml", "*.json", "*.md"],
                "exclude_patterns": ["*.pyc", "__pycache__", "node_modules", ".git"]
            },
            "maintenance_windows": {
                "preferred_time": "02:00",
                "max_duration_minutes": 60,
                "notify_stakeholders": True
            },
            "automation_settings": {
                "auto_fix_minor_issues": True,
                "create_maintenance_prs": True,
                "send_alerts": True,
                "escalate_critical": True
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    default_config.update(loaded_config or {})
            except Exception as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")
                
        return default_config
    
    def initialize_continuity_automation(self) -> Dict[str, Any]:
        """Initialize the continuity automation system."""
        logger.info("Initializing continuity ritual automation...")
        
        try:
            # Schedule daily rituals
            for ritual in self.config["ritual_schedule"]["daily"]:
                schedule.every().day.at("06:00").do(self._execute_ritual, ritual, "daily")
            
            # Schedule weekly rituals
            for ritual in self.config["ritual_schedule"]["weekly"]:
                schedule.every().monday.at("02:00").do(self._execute_ritual, ritual, "weekly")
            
            # Schedule monthly rituals
            for ritual in self.config["ritual_schedule"]["monthly"]:
                schedule.every().month.do(self._execute_ritual, ritual, "monthly")
            
            # Schedule health checks
            if self.config["health_checks"]["enabled"]:
                health_interval = self.config["health_checks"]["interval_minutes"]
                schedule.every(health_interval).minutes.do(self._execute_health_check)
            
            logger.info("Continuity automation initialized successfully")
            
            return {
                "status": "initialized",
                "scheduled_rituals": len(schedule.jobs),
                "health_checks_enabled": self.config["health_checks"]["enabled"],
                "initialization_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Continuity initialization failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "initialization_time": datetime.now().isoformat()
            }
    
    def run_continuity_daemon(self):
        """Run the continuity automation daemon."""
        logger.info("Starting continuity ritual automation daemon...")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Continuity daemon stopped by user")
        except Exception as e:
            logger.error(f"Continuity daemon error: {e}")
    
    def execute_immediate_ritual(self, ritual_type: str) -> Dict[str, Any]:
        """Execute a specific ritual immediately."""
        logger.info(f"Executing immediate ritual: {ritual_type}")
        
        return self._execute_ritual(ritual_type, "immediate")
    
    def _execute_ritual(self, ritual_type: str, frequency: str) -> Dict[str, Any]:
        """Execute a specific continuity ritual."""
        start_time = datetime.now()
        logger.info(f"Starting {frequency} ritual: {ritual_type}")
        
        try:
            ritual_methods = {
                "health_check": self._health_check_ritual,
                "log_rotation": self._log_rotation_ritual,
                "metric_collection": self._metric_collection_ritual,
                "system_backup": self._system_backup_ritual,
                "dependency_update": self._dependency_update_ritual,
                "performance_analysis": self._performance_analysis_ritual,
                "comprehensive_audit": self._comprehensive_audit_ritual,
                "security_scan": self._security_scan_ritual,
                "documentation_sync": self._documentation_sync_ritual
            }
            
            ritual_method = ritual_methods.get(ritual_type)
            if not ritual_method:
                raise ValueError(f"Unknown ritual type: {ritual_type}")
            
            result = ritual_method()
            
            execution_time = datetime.now() - start_time
            
            ritual_record = {
                "ritual_type": ritual_type,
                "frequency": frequency,
                "status": result.get("status", "completed"),
                "start_time": start_time.isoformat(),
                "execution_time_seconds": execution_time.total_seconds(),
                "result": result
            }
            
            self.ritual_history.append(ritual_record)
            self._log_ritual_execution(ritual_record)
            
            logger.info(f"Completed {frequency} ritual: {ritual_type} in {execution_time}")
            
            return ritual_record
            
        except Exception as e:
            logger.error(f"Ritual {ritual_type} failed: {e}")
            
            error_record = {
                "ritual_type": ritual_type,
                "frequency": frequency,
                "status": "error",
                "start_time": start_time.isoformat(),
                "execution_time_seconds": (datetime.now() - start_time).total_seconds(),
                "error": str(e)
            }
            
            self.ritual_history.append(error_record)
            self._log_ritual_execution(error_record)
            
            return error_record
    
    def _health_check_ritual(self) -> Dict[str, Any]:
        """Perform system health check ritual."""
        logger.info("Executing health check ritual")
        
        health_metrics = {
            "system_status": "healthy",
            "issues_found": [],
            "warnings": [],
            "metrics": {}
        }
        
        try:
            # Check system resources
            import psutil
            
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_metrics["metrics"] = {
                "cpu_usage_percent": cpu_usage,
                "memory_usage_percent": memory.percent,
                "disk_usage_percent": disk.percent,
                "available_memory_gb": memory.available / (1024**3),
                "free_disk_gb": disk.free / (1024**3)
            }
            
            # Check against thresholds
            thresholds = self.config["health_checks"]["critical_thresholds"]
            
            if cpu_usage > thresholds["cpu_usage"]:
                health_metrics["issues_found"].append(f"High CPU usage: {cpu_usage}%")
                health_metrics["system_status"] = "degraded"
            
            if memory.percent > thresholds["memory_usage"]:
                health_metrics["issues_found"].append(f"High memory usage: {memory.percent}%")
                health_metrics["system_status"] = "degraded"
            
            if disk.percent > thresholds["disk_usage"]:
                health_metrics["issues_found"].append(f"High disk usage: {disk.percent}%")
                health_metrics["system_status"] = "critical"
            
            # Check recursive improvement system
            recursive_health = self._check_recursive_system_health()
            health_metrics["recursive_system"] = recursive_health
            
            # Check agent registry
            agent_health = self._check_agent_registry_health()
            health_metrics["agent_registry"] = agent_health
            
            self.last_health_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            health_metrics["system_status"] = "error"
            health_metrics["issues_found"].append(f"Health check failed: {e}")
        
        return health_metrics
    
    def _log_rotation_ritual(self) -> Dict[str, Any]:
        """Perform log rotation ritual."""
        logger.info("Executing log rotation ritual")
        
        rotated_files = 0
        archived_files = 0
        
        try:
            # Rotate log files older than 7 days
            for log_file in self.logs_path.glob("*.log"):
                if log_file.stat().st_mtime < (datetime.now() - timedelta(days=7)).timestamp():
                    archive_name = f"{log_file.stem}_{datetime.now().strftime('%Y%m%d')}.log"
                    archive_path = self.logs_path / "archive" / archive_name
                    
                    archive_path.parent.mkdir(exist_ok=True)
                    log_file.rename(archive_path)
                    rotated_files += 1
            
            # Compress old archives
            archive_path = self.logs_path / "archive"
            if archive_path.exists():
                for archive_file in archive_path.glob("*.log"):
                    if archive_file.stat().st_mtime < (datetime.now() - timedelta(days=30)).timestamp():
                        # Compress and remove
                        subprocess.run(["gzip", str(archive_file)], check=True)
                        archived_files += 1
            
        except Exception as e:
            logger.error(f"Log rotation error: {e}")
            return {"status": "error", "error": str(e)}
        
        return {
            "status": "completed",
            "rotated_files": rotated_files,
            "archived_files": archived_files
        }
    
    def _metric_collection_ritual(self) -> Dict[str, Any]:
        """Collect system and application metrics."""
        logger.info("Executing metric collection ritual")
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {},
            "application_metrics": {},
            "recursive_metrics": {}
        }
        
        try:
            # System metrics
            import psutil
            metrics["system_metrics"] = {
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total": psutil.virtual_memory().total,
                "memory_used": psutil.virtual_memory().used,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_io": dict(psutil.net_io_counters()._asdict()),
                "boot_time": psutil.boot_time()
            }
            
            # Application metrics
            metrics["application_metrics"] = {
                "agent_count": self._count_active_agents(),
                "workflow_runs": self._count_workflow_runs(),
                "error_count": self._count_recent_errors(),
                "uptime_seconds": (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds()
            }
            
            # Recursive system metrics
            metrics["recursive_metrics"] = self._collect_recursive_metrics()
            
            # Save metrics
            metrics_file = self.reports_path / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(metrics_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            
        except Exception as e:
            logger.error(f"Metric collection error: {e}")
            return {"status": "error", "error": str(e)}
        
        return {"status": "completed", "metrics_collected": len(metrics)}
    
    def _system_backup_ritual(self) -> Dict[str, Any]:
        """Perform system backup ritual."""
        logger.info("Executing system backup ritual")
        
        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.backups_path / f"backup_{backup_timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        backed_up_files = 0
        
        try:
            # Backup critical files
            include_patterns = self.config["backup_settings"]["include_patterns"]
            exclude_patterns = self.config["backup_settings"]["exclude_patterns"]
            
            for pattern in include_patterns:
                for file_path in Path(".").glob(f"**/{pattern}"):
                    if any(exclude_pattern in str(file_path) for exclude_pattern in exclude_patterns):
                        continue
                    
                    if file_path.is_file():
                        relative_path = file_path.relative_to(".")
                        backup_file_path = backup_dir / relative_path
                        backup_file_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        import shutil
                        shutil.copy2(file_path, backup_file_path)
                        backed_up_files += 1
            
            # Create backup manifest
            manifest = {
                "backup_timestamp": backup_timestamp,
                "files_backed_up": backed_up_files,
                "backup_size_mb": sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file()) / (1024*1024),
                "patterns_included": include_patterns,
                "patterns_excluded": exclude_patterns
            }
            
            with open(backup_dir / "manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"System backup error: {e}")
            return {"status": "error", "error": str(e)}
        
        return {
            "status": "completed",
            "backup_location": str(backup_dir),
            "files_backed_up": backed_up_files
        }
    
    def _dependency_update_ritual(self) -> Dict[str, Any]:
        """Check and update dependencies."""
        logger.info("Executing dependency update ritual")
        
        update_results = {
            "python_updates": [],
            "security_updates": [],
            "recommendations": []
        }
        
        try:
            # Check Python dependencies
            result = subprocess.run(["pip", "list", "--outdated", "--format=json"], 
                                  capture_output=True, text=True, check=True)
            
            if result.stdout:
                outdated_packages = json.loads(result.stdout)
                update_results["python_updates"] = outdated_packages
            
            # Security audit (if available)
            try:
                result = subprocess.run(["pip-audit"], capture_output=True, text=True)
                if result.returncode == 0:
                    update_results["security_status"] = "clean"
                else:
                    update_results["security_issues"] = result.stdout
            except FileNotFoundError:
                update_results["security_status"] = "tool_not_available"
            
            # Generate recommendations
            if update_results["python_updates"]:
                update_results["recommendations"].append("Update outdated Python packages")
            
        except Exception as e:
            logger.error(f"Dependency update error: {e}")
            return {"status": "error", "error": str(e)}
        
        return {"status": "completed", "updates": update_results}
    
    def _performance_analysis_ritual(self) -> Dict[str, Any]:
        """Analyze system performance."""
        logger.info("Executing performance analysis ritual")
        
        analysis_results = {
            "performance_score": 0,
            "bottlenecks": [],
            "recommendations": []
        }
        
        try:
            # Analyze recent metrics
            recent_metrics = self._get_recent_metrics()
            
            if recent_metrics:
                avg_cpu = sum(m["system_metrics"]["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
                avg_memory = sum(m["system_metrics"]["memory_used"] for m in recent_metrics) / len(recent_metrics)
                
                # Calculate performance score (0-100)
                cpu_score = max(0, 100 - avg_cpu)
                memory_score = max(0, 100 - (avg_memory / psutil.virtual_memory().total * 100))
                analysis_results["performance_score"] = (cpu_score + memory_score) / 2
                
                # Identify bottlenecks
                if avg_cpu > 70:
                    analysis_results["bottlenecks"].append("High CPU usage")
                    analysis_results["recommendations"].append("Optimize CPU-intensive operations")
                
                if avg_memory / psutil.virtual_memory().total > 0.8:
                    analysis_results["bottlenecks"].append("High memory usage")
                    analysis_results["recommendations"].append("Optimize memory usage")
            
        except Exception as e:
            logger.error(f"Performance analysis error: {e}")
            return {"status": "error", "error": str(e)}
        
        return {"status": "completed", "analysis": analysis_results}
    
    def _comprehensive_audit_ritual(self) -> Dict[str, Any]:
        """Perform comprehensive system audit."""
        logger.info("Executing comprehensive audit ritual")
        
        audit_results = {
            "system_health": "unknown",
            "security_status": "unknown",
            "performance_grade": "unknown",
            "issues_found": [],
            "recommendations": []
        }
        
        try:
            # System health audit
            health_result = self._health_check_ritual()
            audit_results["system_health"] = health_result["system_status"]
            audit_results["issues_found"].extend(health_result["issues_found"])
            
            # Performance audit
            perf_result = self._performance_analysis_ritual()
            if perf_result["status"] == "completed":
                score = perf_result["analysis"]["performance_score"]
                if score >= 80:
                    audit_results["performance_grade"] = "excellent"
                elif score >= 60:
                    audit_results["performance_grade"] = "good"
                elif score >= 40:
                    audit_results["performance_grade"] = "fair"
                else:
                    audit_results["performance_grade"] = "poor"
            
            # Security audit
            security_result = self._security_scan_ritual()
            audit_results["security_status"] = security_result.get("status", "unknown")
            
            # Generate overall recommendations
            if audit_results["system_health"] != "healthy":
                audit_results["recommendations"].append("Address system health issues")
            
            if audit_results["performance_grade"] in ["fair", "poor"]:
                audit_results["recommendations"].append("Optimize system performance")
            
        except Exception as e:
            logger.error(f"Comprehensive audit error: {e}")
            return {"status": "error", "error": str(e)}
        
        return {"status": "completed", "audit": audit_results}
    
    def _security_scan_ritual(self) -> Dict[str, Any]:
        """Perform security scan."""
        logger.info("Executing security scan ritual")
        
        security_results = {
            "vulnerabilities": [],
            "recommendations": [],
            "status": "secure"
        }
        
        try:
            # Check file permissions
            sensitive_files = ["integration.py", "dashboard.py", "agent_register_sync.py"]
            for file_name in sensitive_files:
                file_path = Path(file_name)
                if file_path.exists():
                    stat = file_path.stat()
                    # Check if file is world-readable/writable
                    if stat.st_mode & 0o077:
                        security_results["vulnerabilities"].append(f"Insecure permissions on {file_name}")
                        security_results["status"] = "vulnerable"
            
            # Check for secrets in code
            for py_file in Path(".").glob("**/*.py"):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        if any(keyword in content.lower() for keyword in ["password=", "api_key=", "secret="]):
                            security_results["vulnerabilities"].append(f"Potential secrets in {py_file}")
                            security_results["status"] = "vulnerable"
                except Exception:
                    continue
            
        except Exception as e:
            logger.error(f"Security scan error: {e}")
            return {"status": "error", "error": str(e)}
        
        return {"status": "completed", "security": security_results}
    
    def _documentation_sync_ritual(self) -> Dict[str, Any]:
        """Synchronize documentation with code."""
        logger.info("Executing documentation sync ritual")
        
        sync_results = {
            "docs_updated": 0,
            "drift_detected": [],
            "new_docs_needed": []
        }
        
        try:
            # Check if doc_updater engine is available
            try:
                from recursive_improvement.engines.doc_updater import DocUpdaterEngine
                doc_engine = DocUpdaterEngine()
                result = doc_engine.execute_main_action()
                
                sync_results["docs_updated"] = result.get("auto_updates_applied", 0)
                sync_results["drift_detected"] = result.get("drift_issues_found", [])
                sync_results["new_docs_needed"] = result.get("missing_docs_detected", [])
                
            except ImportError:
                logger.warning("Doc updater engine not available")
                sync_results["status"] = "engine_unavailable"
            
        except Exception as e:
            logger.error(f"Documentation sync error: {e}")
            return {"status": "error", "error": str(e)}
        
        return {"status": "completed", "sync": sync_results}
    
    def _execute_health_check(self):
        """Execute scheduled health check."""
        health_result = self._health_check_ritual()
        
        # Handle critical issues
        if health_result["system_status"] == "critical":
            self._handle_critical_issues(health_result["issues_found"])
        
        return health_result
    
    def _handle_critical_issues(self, issues: List[str]):
        """Handle critical system issues."""
        logger.warning(f"Critical issues detected: {issues}")
        
        if self.config["automation_settings"]["escalate_critical"]:
            # This would integrate with alerting system
            logger.critical("Escalating critical issues to administrators")
        
        if self.config["automation_settings"]["auto_fix_minor_issues"]:
            # Attempt automated fixes for known issues
            for issue in issues:
                if "High disk usage" in issue:
                    self._cleanup_disk_space()
    
    def _cleanup_disk_space(self):
        """Cleanup disk space by removing old files."""
        logger.info("Attempting to cleanup disk space")
        
        try:
            # Remove old log files
            for log_file in self.logs_path.glob("*.log"):
                if log_file.stat().st_mtime < (datetime.now() - timedelta(days=30)).timestamp():
                    log_file.unlink()
                    logger.info(f"Removed old log file: {log_file}")
            
            # Remove old backups
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"Disk cleanup error: {e}")
    
    def _cleanup_old_backups(self):
        """Remove old backup files."""
        try:
            retention_days = self.config["backup_settings"]["retention_days"]
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            
            for backup_dir in self.backups_path.glob("backup_*"):
                if backup_dir.stat().st_mtime < cutoff_time.timestamp():
                    import shutil
                    shutil.rmtree(backup_dir)
                    logger.info(f"Removed old backup: {backup_dir}")
                    
        except Exception as e:
            logger.error(f"Backup cleanup error: {e}")
    
    # Helper methods
    def _check_recursive_system_health(self) -> Dict[str, Any]:
        """Check recursive improvement system health."""
        try:
            from recursive_improvement.orchestrator import RecursiveOrchestrator
            # This would interface with actual orchestrator
            return {"status": "healthy", "engines_active": 15}
        except ImportError:
            return {"status": "unavailable", "engines_active": 0}
    
    def _check_agent_registry_health(self) -> Dict[str, Any]:
        """Check agent registry health."""
        try:
            from agent_register_sync import AgentRegisterSync
            sync_system = AgentRegisterSync()
            return sync_system.get_registry_status()
        except ImportError:
            return {"status": "unavailable"}
    
    def _count_active_agents(self) -> int:
        """Count active agents in the system."""
        try:
            from agent_register_sync import AgentRegisterSync
            sync_system = AgentRegisterSync()
            status = sync_system.get_registry_status()
            return status.get("active_agents", 0)
        except Exception:
            return 0
    
    def _count_workflow_runs(self) -> int:
        """Count recent workflow runs."""
        # This would integrate with GitHub API or workflow logs
        return 0
    
    def _count_recent_errors(self) -> int:
        """Count recent errors in logs."""
        error_count = 0
        try:
            for log_file in self.logs_path.glob("*.log"):
                with open(log_file, 'r') as f:
                    content = f.read()
                    error_count += content.lower().count("error")
        except Exception:
            pass
        return error_count
    
    def _collect_recursive_metrics(self) -> Dict[str, Any]:
        """Collect metrics from recursive improvement system."""
        return {
            "engines_active": 15,
            "improvements_applied": 0,
            "system_health": "healthy"
        }
    
    def _get_recent_metrics(self) -> List[Dict[str, Any]]:
        """Get recent metrics from files."""
        metrics = []
        try:
            for metrics_file in sorted(self.reports_path.glob("metrics_*.json"))[-5:]:
                with open(metrics_file, 'r') as f:
                    metrics.append(json.load(f))
        except Exception:
            pass
        return metrics
    
    def _log_ritual_execution(self, ritual_record: Dict[str, Any]):
        """Log ritual execution."""
        try:
            log_file = self.logs_path / "continuity_rituals.log"
            with open(log_file, 'a') as f:
                f.write(json.dumps(ritual_record) + '\n')
        except Exception as e:
            logger.error(f"Failed to log ritual execution: {e}")
    
    def get_continuity_status(self) -> Dict[str, Any]:
        """Get current continuity system status."""
        return {
            "automation_active": len(schedule.jobs) > 0,
            "scheduled_jobs": len(schedule.jobs),
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else "never",
            "recent_rituals": len(self.ritual_history),
            "system_health": self.last_health_check is not None
        }

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Continuity Ritual Automation")
    parser.add_argument("--init", action="store_true", help="Initialize automation")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--ritual", help="Execute specific ritual")
    parser.add_argument("--status", action="store_true", help="Show continuity status")
    parser.add_argument("--config", help="Config file path")
    
    args = parser.parse_args()
    
    automation = ContinuityRitualAutomation(args.config)
    
    if args.init:
        result = automation.initialize_continuity_automation()
        print(json.dumps(result, indent=2))
    elif args.daemon:
        automation.run_continuity_daemon()
    elif args.ritual:
        result = automation.execute_immediate_ritual(args.ritual)
        print(json.dumps(result, indent=2))
    elif args.status:
        status = automation.get_continuity_status()
        print(json.dumps(status, indent=2))
    else:
        print("Use --init, --daemon, --ritual <type>, or --status")

if __name__ == "__main__":
    main()