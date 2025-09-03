#!/usr/bin/env python3
"""
Continuity Ritual Automation
EpochCore RAS Repository Automation

Scheduled maintenance rituals for system health, performance monitoring,
and automated maintenance tasks.
"""

import os
import json
import psutil
import shutil
import logging
import schedule
import time
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
import subprocess


class ContinuityRitual:
    """Manages automated maintenance rituals for system continuity."""
    
    def __init__(self, config_path: str = "config/continuity_ritual.yaml"):
        self.config_path = config_path
        self.config = {}
        self.ritual_log = "logs/ritual_execution.json"
        self.metrics_log = "logs/system_metrics.json"
        
        # Ensure directories exist
        for path in ["logs", "backups", "config"]:
            Path(path).mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.load_config()
        
        # Ritual execution history
        self.execution_history = []
        self.load_execution_history()
        
        # System metrics
        self.system_metrics = {
            "cpu_percent": 0,
            "memory_percent": 0,
            "disk_percent": 0,
            "network_io": {},
            "process_count": 0
        }
    
    def load_config(self) -> bool:
        """Load ritual configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.logger.info("Loaded ritual configuration")
                return True
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
        
        # Default configuration
        self.config = self.get_default_config()
        self.save_config()
        return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default ritual configuration."""
        return {
            "rituals": {
                "daily": {
                    "enabled": True,
                    "schedule": "0 2 * * *",
                    "tasks": [
                        "system_health_check",
                        "log_rotation",
                        "temp_cleanup",
                        "metrics_collection"
                    ]
                },
                "weekly": {
                    "enabled": True,
                    "schedule": "0 3 * * 1",
                    "tasks": [
                        "full_backup",
                        "dependency_update_check", 
                        "performance_analysis",
                        "security_scan"
                    ]
                },
                "monthly": {
                    "enabled": True,
                    "schedule": "0 4 1 * *",
                    "tasks": [
                        "archive_old_logs",
                        "cleanup_old_backups",
                        "system_optimization",
                        "comprehensive_audit"
                    ]
                }
            },
            "monitoring": {
                "resource_thresholds": {
                    "cpu_percent": 80,
                    "memory_percent": 85,
                    "disk_percent": 90
                }
            },
            "notifications": {
                "enabled": True,
                "channels": ["log", "file"]
            }
        }
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
    
    def load_execution_history(self) -> bool:
        """Load ritual execution history."""
        if os.path.exists(self.ritual_log):
            try:
                with open(self.ritual_log, 'r') as f:
                    self.execution_history = json.load(f)
                return True
            except Exception as e:
                self.logger.error(f"Failed to load execution history: {e}")
        
        self.execution_history = []
        return False
    
    def save_execution_history(self) -> bool:
        """Save ritual execution history."""
        try:
            with open(self.ritual_log, 'w') as f:
                json.dump(self.execution_history, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save execution history: {e}")
            return False
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network metrics
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # Process metrics
            process_count = len(psutil.pids())
            
            self.system_metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk_percent,
                "disk_free_gb": disk.free / (1024**3),
                "network_io": network_io,
                "process_count": process_count,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
            
            return self.system_metrics
        except Exception as e:
            self.logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def check_resource_thresholds(self) -> List[Dict[str, Any]]:
        """Check if system resources exceed thresholds."""
        warnings = []
        thresholds = self.config.get("monitoring", {}).get("resource_thresholds", {})
        
        metrics = self.collect_system_metrics()
        
        # Check CPU threshold
        if metrics.get("cpu_percent", 0) > thresholds.get("cpu_percent", 80):
            warnings.append({
                "type": "cpu_high",
                "current": metrics["cpu_percent"],
                "threshold": thresholds["cpu_percent"],
                "severity": "warning"
            })
        
        # Check memory threshold
        if metrics.get("memory_percent", 0) > thresholds.get("memory_percent", 85):
            warnings.append({
                "type": "memory_high",
                "current": metrics["memory_percent"],
                "threshold": thresholds["memory_percent"],
                "severity": "warning"
            })
        
        # Check disk threshold
        if metrics.get("disk_percent", 0) > thresholds.get("disk_percent", 90):
            warnings.append({
                "type": "disk_high",
                "current": metrics["disk_percent"],
                "threshold": thresholds["disk_percent"],
                "severity": "critical"
            })
        
        return warnings
    
    def system_health_check(self) -> Dict[str, Any]:
        """Perform system health check."""
        self.logger.info("Performing system health check")
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {},
            "warnings": [],
            "errors": []
        }
        
        try:
            # Collect metrics
            metrics = self.collect_system_metrics()
            health_report["metrics"] = metrics
            
            # Check resource thresholds
            warnings = self.check_resource_thresholds()
            health_report["warnings"] = warnings
            
            # Check disk space
            if metrics.get("disk_percent", 0) > 95:
                health_report["status"] = "critical"
                health_report["errors"].append("Disk space critically low")
            elif warnings:
                health_report["status"] = "warning"
            
            # Check essential processes
            essential_processes = self.check_essential_processes()
            health_report["checks"]["processes"] = essential_processes
            
            # Check log file sizes
            log_check = self.check_log_file_sizes()
            health_report["checks"]["logs"] = log_check
            
        except Exception as e:
            health_report["status"] = "error"
            health_report["errors"].append(f"Health check failed: {str(e)}")
        
        return health_report
    
    def check_essential_processes(self) -> Dict[str, Any]:
        """Check if essential processes are running."""
        essential_processes = {
            "python_processes": 0,
            "recursive_engines": 0,
            "details": []
        }
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    cmdline = ' '.join(proc_info['cmdline']) if proc_info['cmdline'] else ''
                    
                    if 'python' in proc_info['name'].lower():
                        essential_processes["python_processes"] += 1
                        
                    if any(keyword in cmdline.lower() for keyword in ['integration.py', 'recursive', 'epochcore']):
                        essential_processes["recursive_engines"] += 1
                        essential_processes["details"].append({
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "cmdline": cmdline[:100] + "..." if len(cmdline) > 100 else cmdline
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to check processes: {e}")
        
        return essential_processes
    
    def check_log_file_sizes(self) -> Dict[str, Any]:
        """Check log file sizes and rotation needs."""
        log_check = {
            "total_size_mb": 0,
            "large_files": [],
            "rotation_needed": False
        }
        
        logs_dir = Path("logs")
        if logs_dir.exists():
            try:
                for log_file in logs_dir.glob("*.log"):
                    file_size = log_file.stat().st_size
                    file_size_mb = file_size / (1024 * 1024)
                    log_check["total_size_mb"] += file_size_mb
                    
                    if file_size_mb > 50:  # 50MB threshold
                        log_check["large_files"].append({
                            "file": str(log_file),
                            "size_mb": round(file_size_mb, 2)
                        })
                        log_check["rotation_needed"] = True
                        
            except Exception as e:
                self.logger.error(f"Failed to check log files: {e}")
        
        return log_check
    
    def log_rotation(self) -> Dict[str, Any]:
        """Perform log rotation."""
        self.logger.info("Performing log rotation")
        
        rotation_result = {
            "timestamp": datetime.now().isoformat(),
            "files_rotated": 0,
            "space_freed_mb": 0,
            "errors": []
        }
        
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return rotation_result
        
        try:
            for log_file in logs_dir.glob("*.log"):
                file_size = log_file.stat().st_size
                file_size_mb = file_size / (1024 * 1024)
                
                if file_size_mb > 10:  # Rotate files larger than 10MB
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    rotated_name = f"{log_file.stem}_{timestamp}.log"
                    rotated_path = logs_dir / rotated_name
                    
                    try:
                        shutil.move(str(log_file), str(rotated_path))
                        
                        # Compress rotated file
                        subprocess.run(['gzip', str(rotated_path)], check=True)
                        
                        rotation_result["files_rotated"] += 1
                        rotation_result["space_freed_mb"] += file_size_mb
                        
                    except subprocess.CalledProcessError:
                        # If gzip fails, just move the file
                        rotation_result["files_rotated"] += 1
                        rotation_result["space_freed_mb"] += file_size_mb
                    except Exception as e:
                        rotation_result["errors"].append(f"Failed to rotate {log_file}: {str(e)}")
                        
        except Exception as e:
            rotation_result["errors"].append(f"Log rotation failed: {str(e)}")
        
        return rotation_result
    
    def temp_cleanup(self) -> Dict[str, Any]:
        """Clean up temporary files."""
        self.logger.info("Performing temporary file cleanup")
        
        cleanup_result = {
            "timestamp": datetime.now().isoformat(),
            "files_cleaned": 0,
            "space_freed_mb": 0,
            "errors": []
        }
        
        # Define cleanup patterns
        cleanup_patterns = [
            "**/__pycache__/**",
            "**/tmp/**",
            "**/*.tmp",
            "**/*.pyc",
            "**/temp/**",
            "**/.pytest_cache/**"
        ]
        
        try:
            for pattern in cleanup_patterns:
                for item in Path(".").glob(pattern):
                    if item.is_file():
                        try:
                            file_size = item.stat().st_size
                            item.unlink()
                            cleanup_result["files_cleaned"] += 1
                            cleanup_result["space_freed_mb"] += file_size / (1024 * 1024)
                        except Exception as e:
                            cleanup_result["errors"].append(f"Failed to delete {item}: {str(e)}")
                    elif item.is_dir() and not any(item.iterdir()):  # Empty directory
                        try:
                            item.rmdir()
                            cleanup_result["files_cleaned"] += 1
                        except Exception as e:
                            cleanup_result["errors"].append(f"Failed to remove directory {item}: {str(e)}")
                            
        except Exception as e:
            cleanup_result["errors"].append(f"Cleanup failed: {str(e)}")
        
        return cleanup_result
    
    def metrics_collection(self) -> Dict[str, Any]:
        """Collect and store system metrics."""
        self.logger.info("Collecting system metrics")
        
        metrics = self.collect_system_metrics()
        
        # Save to metrics log
        try:
            # Load existing metrics
            existing_metrics = []
            if os.path.exists(self.metrics_log):
                with open(self.metrics_log, 'r') as f:
                    existing_metrics = json.load(f)
            
            # Add new metrics
            existing_metrics.append(metrics)
            
            # Keep only last 1000 entries
            if len(existing_metrics) > 1000:
                existing_metrics = existing_metrics[-1000:]
            
            # Save updated metrics
            with open(self.metrics_log, 'w') as f:
                json.dump(existing_metrics, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics_collected": True,
            "metrics": metrics
        }
    
    def full_backup(self) -> Dict[str, Any]:
        """Create full system backup."""
        self.logger.info("Creating full system backup")
        
        backup_result = {
            "timestamp": datetime.now().isoformat(),
            "backup_created": False,
            "backup_path": "",
            "size_mb": 0,
            "errors": []
        }
        
        try:
            # Use the zip vault creator if available
            try:
                from zip_vault_creator import VaultCreator
                vault = VaultCreator()
                result = vault.create_snapshot("full_system")
                backup_result.update(result)
            except ImportError:
                # Fallback to simple backup
                backup_result = self.simple_backup()
                
        except Exception as e:
            backup_result["errors"].append(f"Backup failed: {str(e)}")
        
        return backup_result
    
    def simple_backup(self) -> Dict[str, Any]:
        """Simple backup without zip vault creator."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("backups") / f"system_backup_{timestamp}"
        
        backup_result = {
            "timestamp": datetime.now().isoformat(),
            "backup_created": False,
            "backup_path": str(backup_dir),
            "size_mb": 0,
            "errors": []
        }
        
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy essential directories
            essential_dirs = ["config", "data", "recursive_improvement", "tests"]
            essential_files = ["integration.py", "requirements.txt", "README.md"]
            
            total_size = 0
            
            for dir_name in essential_dirs:
                src_dir = Path(dir_name)
                if src_dir.exists():
                    dst_dir = backup_dir / dir_name
                    shutil.copytree(src_dir, dst_dir)
                    total_size += sum(f.stat().st_size for f in dst_dir.rglob('*') if f.is_file())
            
            for file_name in essential_files:
                src_file = Path(file_name)
                if src_file.exists():
                    dst_file = backup_dir / file_name
                    shutil.copy2(src_file, dst_file)
                    total_size += dst_file.stat().st_size
            
            backup_result["backup_created"] = True
            backup_result["size_mb"] = total_size / (1024 * 1024)
            
        except Exception as e:
            backup_result["errors"].append(f"Simple backup failed: {str(e)}")
        
        return backup_result
    
    def dependency_update_check(self) -> Dict[str, Any]:
        """Check for dependency updates."""
        self.logger.info("Checking for dependency updates")
        
        update_result = {
            "timestamp": datetime.now().isoformat(),
            "updates_available": False,
            "packages": [],
            "errors": []
        }
        
        try:
            # Check for pip updates
            result = subprocess.run(
                ['pip', 'list', '--outdated', '--format=json'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                outdated_packages = json.loads(result.stdout)
                if outdated_packages:
                    update_result["updates_available"] = True
                    update_result["packages"] = outdated_packages
                    
        except subprocess.TimeoutExpired:
            update_result["errors"].append("Dependency check timed out")
        except Exception as e:
            update_result["errors"].append(f"Dependency check failed: {str(e)}")
        
        return update_result
    
    def performance_analysis(self) -> Dict[str, Any]:
        """Analyze system performance."""
        self.logger.info("Analyzing system performance")
        
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "performance_score": 0,
            "bottlenecks": [],
            "recommendations": []
        }
        
        try:
            metrics = self.collect_system_metrics()
            
            # Calculate performance score (0-100)
            cpu_score = max(0, 100 - metrics.get("cpu_percent", 0))
            memory_score = max(0, 100 - metrics.get("memory_percent", 0))
            disk_score = max(0, 100 - metrics.get("disk_percent", 0))
            
            analysis_result["performance_score"] = (cpu_score + memory_score + disk_score) / 3
            
            # Identify bottlenecks
            if metrics.get("cpu_percent", 0) > 70:
                analysis_result["bottlenecks"].append("High CPU usage")
                analysis_result["recommendations"].append("Consider optimizing CPU-intensive tasks")
            
            if metrics.get("memory_percent", 0) > 80:
                analysis_result["bottlenecks"].append("High memory usage")
                analysis_result["recommendations"].append("Review memory usage and consider cleanup")
            
            if metrics.get("disk_percent", 0) > 85:
                analysis_result["bottlenecks"].append("High disk usage")
                analysis_result["recommendations"].append("Clean up old files and logs")
            
        except Exception as e:
            self.logger.error(f"Performance analysis failed: {e}")
        
        return analysis_result
    
    def security_scan(self) -> Dict[str, Any]:
        """Perform basic security scan."""
        self.logger.info("Performing security scan")
        
        scan_result = {
            "timestamp": datetime.now().isoformat(),
            "security_score": 100,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Check for common security issues
            
            # Check file permissions
            sensitive_files = [".env", "config/*.yaml", "config/*.yml"]
            for pattern in sensitive_files:
                for file_path in Path(".").glob(pattern):
                    if file_path.exists():
                        stat = file_path.stat()
                        if stat.st_mode & 0o077:  # World or group readable
                            scan_result["issues"].append(f"Sensitive file {file_path} has loose permissions")
                            scan_result["security_score"] -= 10
            
            # Check for secrets in config files
            config_files = list(Path("config").glob("*.yaml")) if Path("config").exists() else []
            for config_file in config_files:
                try:
                    with open(config_file, 'r') as f:
                        content = f.read().lower()
                        if any(keyword in content for keyword in ['password', 'secret', 'token', 'key']):
                            scan_result["recommendations"].append(f"Review {config_file} for hardcoded secrets")
                except:
                    pass
            
            # Add general recommendations
            scan_result["recommendations"].extend([
                "Regularly update dependencies",
                "Use strong authentication",
                "Enable audit logging",
                "Monitor system access"
            ])
            
        except Exception as e:
            self.logger.error(f"Security scan failed: {e}")
        
        return scan_result
    
    def archive_old_logs(self) -> Dict[str, Any]:
        """Archive old log files."""
        self.logger.info("Archiving old logs")
        
        archive_result = {
            "timestamp": datetime.now().isoformat(),
            "files_archived": 0,
            "space_freed_mb": 0,
            "errors": []
        }
        
        logs_dir = Path("logs")
        archive_dir = Path("backups/archived_logs")
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        if logs_dir.exists():
            try:
                cutoff_date = datetime.now() - timedelta(days=30)
                
                for log_file in logs_dir.glob("*.log*"):
                    if log_file.is_file():
                        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            try:
                                file_size = log_file.stat().st_size
                                archive_path = archive_dir / log_file.name
                                shutil.move(str(log_file), str(archive_path))
                                
                                archive_result["files_archived"] += 1
                                archive_result["space_freed_mb"] += file_size / (1024 * 1024)
                                
                            except Exception as e:
                                archive_result["errors"].append(f"Failed to archive {log_file}: {str(e)}")
                                
            except Exception as e:
                archive_result["errors"].append(f"Log archival failed: {str(e)}")
        
        return archive_result
    
    def cleanup_old_backups(self) -> Dict[str, Any]:
        """Clean up old backup files."""
        self.logger.info("Cleaning up old backups")
        
        cleanup_result = {
            "timestamp": datetime.now().isoformat(),
            "backups_cleaned": 0,
            "space_freed_mb": 0,
            "errors": []
        }
        
        backups_dir = Path("backups")
        if backups_dir.exists():
            try:
                cutoff_date = datetime.now() - timedelta(days=90)  # Keep backups for 90 days
                
                for backup_item in backups_dir.rglob("*"):
                    if backup_item.is_file():
                        file_time = datetime.fromtimestamp(backup_item.stat().st_mtime)
                        if file_time < cutoff_date:
                            try:
                                file_size = backup_item.stat().st_size
                                backup_item.unlink()
                                
                                cleanup_result["backups_cleaned"] += 1
                                cleanup_result["space_freed_mb"] += file_size / (1024 * 1024)
                                
                            except Exception as e:
                                cleanup_result["errors"].append(f"Failed to clean {backup_item}: {str(e)}")
                                
            except Exception as e:
                cleanup_result["errors"].append(f"Backup cleanup failed: {str(e)}")
        
        return cleanup_result
    
    def system_optimization(self) -> Dict[str, Any]:
        """Perform system optimization."""
        self.logger.info("Performing system optimization")
        
        optimization_result = {
            "timestamp": datetime.now().isoformat(),
            "optimizations_applied": 0,
            "improvements": [],
            "errors": []
        }
        
        try:
            # Optimize Python bytecode
            try:
                result = subprocess.run(['python', '-m', 'compileall', '.'], 
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    optimization_result["optimizations_applied"] += 1
                    optimization_result["improvements"].append("Compiled Python bytecode")
            except:
                pass
            
            # Clean up pip cache
            try:
                subprocess.run(['pip', 'cache', 'purge'], timeout=30)
                optimization_result["optimizations_applied"] += 1
                optimization_result["improvements"].append("Cleared pip cache")
            except:
                pass
            
            # System-specific optimizations could be added here
            
        except Exception as e:
            optimization_result["errors"].append(f"Optimization failed: {str(e)}")
        
        return optimization_result
    
    def comprehensive_audit(self) -> Dict[str, Any]:
        """Perform comprehensive system audit."""
        self.logger.info("Performing comprehensive audit")
        
        audit_result = {
            "timestamp": datetime.now().isoformat(),
            "health_check": {},
            "security_scan": {},
            "performance_analysis": {},
            "recommendations": []
        }
        
        try:
            # Run all audit components
            audit_result["health_check"] = self.system_health_check()
            audit_result["security_scan"] = self.security_scan()
            audit_result["performance_analysis"] = self.performance_analysis()
            
            # Generate comprehensive recommendations
            audit_result["recommendations"] = self.generate_audit_recommendations(audit_result)
            
        except Exception as e:
            self.logger.error(f"Comprehensive audit failed: {e}")
        
        return audit_result
    
    def generate_audit_recommendations(self, audit_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on audit data."""
        recommendations = []
        
        # Health check recommendations
        health = audit_data.get("health_check", {})
        if health.get("status") == "warning":
            recommendations.append("Address system resource warnings")
        elif health.get("status") == "critical":
            recommendations.append("URGENT: Address critical system issues")
        
        # Security recommendations
        security = audit_data.get("security_scan", {})
        if security.get("security_score", 100) < 80:
            recommendations.append("Improve security posture")
        
        # Performance recommendations
        performance = audit_data.get("performance_analysis", {})
        if performance.get("performance_score", 100) < 70:
            recommendations.append("Optimize system performance")
        
        # Add general recommendations
        recommendations.extend([
            "Schedule regular maintenance rituals",
            "Monitor system metrics continuously", 
            "Keep dependencies up to date",
            "Review and rotate logs regularly"
        ])
        
        return recommendations
    
    def execute_ritual(self, ritual_type: str) -> Dict[str, Any]:
        """Execute a specific ritual."""
        ritual_execution = {
            "timestamp": datetime.now().isoformat(),
            "ritual_type": ritual_type,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "success": False,
            "tasks_executed": [],
            "errors": []
        }
        
        try:
            ritual_config = self.config["rituals"].get(ritual_type, {})
            if not ritual_config.get("enabled", False):
                ritual_execution["errors"].append(f"Ritual {ritual_type} is not enabled")
                return ritual_execution
            
            tasks = ritual_config.get("tasks", [])
            
            for task in tasks:
                task_result = None
                
                try:
                    if hasattr(self, task):
                        self.logger.info(f"Executing task: {task}")
                        task_result = getattr(self, task)()
                        ritual_execution["tasks_executed"].append({
                            "task": task,
                            "success": True,
                            "result": task_result
                        })
                    else:
                        ritual_execution["errors"].append(f"Unknown task: {task}")
                        ritual_execution["tasks_executed"].append({
                            "task": task,
                            "success": False,
                            "error": f"Task not found: {task}"
                        })
                        
                except Exception as e:
                    error_msg = f"Task {task} failed: {str(e)}"
                    self.logger.error(error_msg)
                    ritual_execution["errors"].append(error_msg)
                    ritual_execution["tasks_executed"].append({
                        "task": task,
                        "success": False,
                        "error": error_msg
                    })
            
            ritual_execution["completed_at"] = datetime.now().isoformat()
            ritual_execution["success"] = len(ritual_execution["errors"]) == 0
            
            # Save to execution history
            self.execution_history.append(ritual_execution)
            self.save_execution_history()
            
        except Exception as e:
            ritual_execution["errors"].append(f"Ritual execution failed: {str(e)}")
        
        return ritual_execution
    
    def schedule_rituals(self) -> None:
        """Schedule all enabled rituals."""
        for ritual_type, ritual_config in self.config.get("rituals", {}).items():
            if ritual_config.get("enabled", False):
                schedule_str = ritual_config.get("schedule", "")
                if schedule_str:
                    # Note: This is a simplified scheduler
                    # In production, use a proper cron-like scheduler
                    self.logger.info(f"Would schedule {ritual_type} with: {schedule_str}")
    
    def run_continuous_monitoring(self, interval: int = 300) -> None:
        """Run continuous monitoring loop."""
        self.logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                # Collect metrics
                self.metrics_collection()
                
                # Check thresholds
                warnings = self.check_resource_thresholds()
                if warnings:
                    self.logger.warning(f"Resource threshold warnings: {warnings}")
                
                # Sleep until next interval
                time.sleep(interval)
                
            except KeyboardInterrupt:
                self.logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current ritual system status."""
        return {
            "timestamp": datetime.now().isoformat(),
            "config_loaded": bool(self.config),
            "rituals_configured": len(self.config.get("rituals", {})),
            "execution_history_count": len(self.execution_history),
            "last_execution": self.execution_history[-1] if self.execution_history else None,
            "current_metrics": self.system_metrics,
            "resource_warnings": self.check_resource_thresholds()
        }


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Continuity Ritual Automation")
    parser.add_argument('--ritual', choices=['daily', 'weekly', 'monthly'], help='Execute specific ritual')
    parser.add_argument('--status', action='store_true', help='Get ritual system status')
    parser.add_argument('--health', action='store_true', help='Perform health check')
    parser.add_argument('--monitor', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--interval', type=int, default=300, help='Monitoring interval in seconds')
    
    args = parser.parse_args()
    
    ritual = ContinuityRitual()
    
    if args.ritual:
        result = ritual.execute_ritual(args.ritual)
        print(json.dumps(result, indent=2))
    elif args.status:
        status = ritual.get_status()
        print(json.dumps(status, indent=2))
    elif args.health:
        health = ritual.system_health_check()
        print(json.dumps(health, indent=2))
    elif args.monitor:
        ritual.run_continuous_monitoring(args.interval)
    else:
        print("Use --ritual, --status, --health, or --monitor")


if __name__ == "__main__":
    main()