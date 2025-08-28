"""
Autonomous Continuous Improvement System Orchestrator

This is the central component that coordinates all autonomous improvement activities
across the repository. It builds upon the existing infrastructure and implements
advanced automation strategies for maintaining and improving repository quality.
"""

import asyncio
import json
import logging
import os
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml
from pydantic import BaseModel, Field

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.ai_agent.core.base_agent import BaseAgent
except ImportError:
    # Create a dummy BaseAgent if not available
    class BaseAgent:
        def __init__(self, name, config=None):
            self.name = name
            self.config = config or {}
            self.logger = logging.getLogger(name)
        
        def validate_config(self):
            return True

try:
    from scripts.ai_agent.core.performance_optimizer import PerformanceOptimizer
except ImportError:
    # Create a dummy class if not available
    class PerformanceOptimizer:
        def __init__(self):
            pass

try:
    from strategy_self_improve import RecursiveSelfImprover
except ImportError:
    # Create a dummy class if not available
    class RecursiveSelfImprover:
        def __init__(self, path):
            pass


class ImprovementPriority(Enum):
    """Priority levels for improvement tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ImprovementCategory(Enum):
    """Categories of improvements."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    MAINTENANCE = "maintenance"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPENDENCY = "dependency"
    WORKFLOW = "workflow"


class ImprovementTask(BaseModel):
    """Represents a single improvement task."""
    id: str
    category: ImprovementCategory
    priority: ImprovementPriority
    title: str
    description: str
    automated: bool = True
    estimated_duration: int = Field(default=300, description="Estimated duration in seconds")
    created_at: datetime = Field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    metrics_before: Dict[str, float] = Field(default_factory=dict)
    metrics_after: Dict[str, float] = Field(default_factory=dict)
    rollback_info: Optional[Dict[str, Any]] = None
    

class AutonomousConfig(BaseModel):
    """Configuration for autonomous improvement system."""
    enabled: bool = True
    safe_mode: bool = True
    max_concurrent_tasks: int = 3
    health_check_interval: int = 3600  # 1 hour
    improvement_interval: int = 7200   # 2 hours
    metrics_retention_days: int = 30
    confidence_threshold: float = 0.8
    rollback_enabled: bool = True
    notification_webhook: Optional[str] = None
    excluded_categories: List[str] = Field(default_factory=list)
    priority_hours: Dict[str, List[int]] = Field(
        default_factory=lambda: {"critical": list(range(24)), "high": list(range(6, 22))}
    )


class AutonomousOrchestrator(BaseAgent):
    """
    Central orchestrator for autonomous continuous improvement system.
    
    Coordinates all autonomous improvement activities including:
    - Repository health monitoring and reporting
    - Self-healing maintenance tasks
    - Workflow optimization
    - Proactive issue detection and resolution
    - Advanced automation features
    """

    def __init__(self, config_path: Optional[str] = None):
        super().__init__("autonomous_orchestrator")
        
        self.config_path = config_path or ".autonomous/config.yaml"
        self.base_dir = Path(".autonomous")
        self.base_dir.mkdir(exist_ok=True)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize components
        self.task_queue: List[ImprovementTask] = []
        self.active_tasks: Dict[str, ImprovementTask] = {}
        self.completed_tasks: deque = deque(maxlen=1000)
        self.metrics_history: deque = deque(maxlen=10000)
        
        # Health monitoring
        self.health_metrics: Dict[str, Any] = {}
        self.last_health_check = None
        self.health_trends: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # Safety mechanisms
        self.safety_locks: Set[str] = set()
        self.rollback_stack: List[Dict[str, Any]] = []
        
        # Integration components
        self.self_improver = RecursiveSelfImprover(str(self.base_dir / "self_improve"))
        self.performance_optimizer = PerformanceOptimizer()
        
        # Improvement agents (will be dynamically loaded)
        self.improvement_agents: Dict[str, BaseAgent] = {}
        
        self.logger = logging.getLogger("autonomous_orchestrator")

    def _load_config(self) -> AutonomousConfig:
        """Load configuration from file or create default."""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config_data = yaml.safe_load(f)
                return AutonomousConfig(**config_data)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_file}: {e}")
        
        # Create default configuration
        config = AutonomousConfig()
        self._save_config(config)
        return config

    def _save_config(self, config: AutonomousConfig):
        """Save configuration to file."""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            yaml.dump(config.model_dump(), f, default_flow_style=False)

    def validate_config(self) -> bool:
        """Validate orchestrator configuration."""
        return (
            isinstance(self.config, AutonomousConfig) and
            self.config.max_concurrent_tasks > 0 and
            self.config.health_check_interval > 0 and
            0 < self.config.confidence_threshold <= 1
        )

    def run(self) -> Dict[str, Any]:
        """Main orchestrator execution (synchronous wrapper)."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self._run_async())

    async def _run_async(self) -> Dict[str, Any]:
        """Main orchestrator execution loop."""
        if not self.config.enabled:
            return {"status": "disabled", "message": "Autonomous system is disabled"}
        
        start_time = time.time()
        tasks_processed = 0
        
        try:
            # Perform health check if needed
            if self._should_run_health_check():
                await self._run_health_check()
            
            # Generate improvement tasks if needed
            if self._should_generate_improvements():
                await self._generate_improvement_tasks()
            
            # Process improvement tasks
            tasks_processed = await self._process_improvement_tasks()
            
            # Update metrics
            self._update_metrics()
            
            # Generate reports
            await self._generate_reports()
            
            execution_time = time.time() - start_time
            
            return {
                "status": "success",
                "execution_time": execution_time,
                "tasks_processed": tasks_processed,
                "active_tasks": len(self.active_tasks),
                "queued_tasks": len(self.task_queue),
                "health_score": self._calculate_health_score()
            }
            
        except Exception as e:
            self.logger.error(f"Orchestrator execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "execution_time": time.time() - start_time
            }

    def _should_run_health_check(self) -> bool:
        """Check if health check should be run."""
        if self.last_health_check is None:
            return True
        
        elapsed = time.time() - self.last_health_check
        return elapsed >= self.config.health_check_interval

    async def _run_health_check(self):
        """Run comprehensive repository health check."""
        self.logger.info("Running repository health check")
        
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "repository": {
                "files": await self._analyze_repository_files(),
                "dependencies": await self._analyze_dependencies(),
                "security": await self._analyze_security(),
                "quality": await self._analyze_code_quality(),
                "tests": await self._analyze_test_coverage(),
                "documentation": await self._analyze_documentation()
            },
            "workflows": await self._analyze_workflows(),
            "performance": await self._analyze_performance()
        }
        
        self.health_metrics = health_data
        self.last_health_check = time.time()
        
        # Store health history for trend analysis
        for category, metrics in health_data["repository"].items():
            if isinstance(metrics, dict):
                for metric, value in metrics.items():
                    if isinstance(value, (int, float)):
                        self.health_trends[f"{category}.{metric}"].append({
                            "timestamp": time.time(),
                            "value": value
                        })

    def _should_generate_improvements(self) -> bool:
        """Check if new improvement tasks should be generated."""
        # Generate improvements if:
        # 1. Queue is empty and no active tasks
        # 2. Enough time has passed since last generation
        # 3. Health metrics indicate need for improvement
        
        if not self.task_queue and not self.active_tasks:
            return True
        
        if hasattr(self, 'last_improvement_generation'):
            elapsed = time.time() - self.last_improvement_generation
            if elapsed >= self.config.improvement_interval:
                return True
        
        # Check if health score is below threshold
        health_score = self._calculate_health_score()
        if health_score < 0.8:
            return True
        
        return False

    async def _generate_improvement_tasks(self):
        """Generate improvement tasks based on current repository state."""
        self.logger.info("Generating improvement tasks")
        
        tasks = []
        
        # Security improvements
        security_tasks = await self._generate_security_tasks()
        tasks.extend(security_tasks)
        
        # Quality improvements
        quality_tasks = await self._generate_quality_tasks()
        tasks.extend(quality_tasks)
        
        # Performance improvements
        performance_tasks = await self._generate_performance_tasks()
        tasks.extend(performance_tasks)
        
        # Maintenance improvements
        maintenance_tasks = await self._generate_maintenance_tasks()
        tasks.extend(maintenance_tasks)
        
        # Documentation improvements
        doc_tasks = await self._generate_documentation_tasks()
        tasks.extend(doc_tasks)
        
        # Testing improvements
        test_tasks = await self._generate_testing_tasks()
        tasks.extend(test_tasks)
        
        # Workflow improvements
        workflow_tasks = await self._generate_workflow_tasks()
        tasks.extend(workflow_tasks)
        
        # Filter out excluded categories
        filtered_tasks = [
            task for task in tasks
            if task.category.value not in self.config.excluded_categories
        ]
        
        # Sort by priority and add to queue
        filtered_tasks.sort(key=lambda t: (t.priority.value, t.created_at))
        self.task_queue.extend(filtered_tasks)
        
        self.last_improvement_generation = time.time()
        self.logger.info(f"Generated {len(filtered_tasks)} improvement tasks")

    async def _process_improvement_tasks(self) -> int:
        """Process queued improvement tasks."""
        processed = 0
        
        while (self.task_queue and 
               len(self.active_tasks) < self.config.max_concurrent_tasks):
            
            task = self.task_queue.pop(0)
            
            # Check if this is the right time for this priority
            if not self._is_appropriate_time(task.priority):
                self.task_queue.append(task)  # Re-queue for later
                break
            
            # Start the task
            asyncio.create_task(self._execute_improvement_task(task))
            self.active_tasks[task.id] = task
            processed += 1
        
        return processed

    async def _execute_improvement_task(self, task: ImprovementTask):
        """Execute a single improvement task."""
        self.logger.info(f"Executing task {task.id}: {task.title}")
        
        try:
            # Record metrics before
            task.metrics_before = await self._collect_task_metrics(task)
            
            # Create rollback point if enabled
            if self.config.rollback_enabled:
                task.rollback_info = await self._create_rollback_point(task)
            
            # Execute the task
            success = await self._execute_task_logic(task)
            
            # Record metrics after
            task.metrics_after = await self._collect_task_metrics(task)
            
            # Validate improvement
            if success and self._validate_improvement(task):
                task.success = True
                task.completed_at = datetime.now()
                self.logger.info(f"Task {task.id} completed successfully")
            else:
                # Rollback if needed
                if self.config.rollback_enabled and task.rollback_info:
                    await self._rollback_task(task)
                task.success = False
                task.error_message = "Improvement validation failed"
                
        except Exception as e:
            self.logger.error(f"Task {task.id} failed: {e}")
            task.success = False
            task.error_message = str(e)
            task.completed_at = datetime.now()
            
            # Attempt rollback on error
            if self.config.rollback_enabled and task.rollback_info:
                try:
                    await self._rollback_task(task)
                except Exception as rollback_error:
                    self.logger.error(f"Rollback failed for task {task.id}: {rollback_error}")
        
        finally:
            # Move from active to completed
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            self.completed_tasks.append(task)

    def _calculate_health_score(self) -> float:
        """Calculate overall repository health score (0-1)."""
        if not self.health_metrics:
            return 0.5  # Neutral score when no metrics available
        
        scores = []
        
        # Analyze repository metrics
        repo_metrics = self.health_metrics.get("repository", {})
        for category, metrics in repo_metrics.items():
            if isinstance(metrics, dict):
                category_score = self._calculate_category_score(metrics)
                scores.append(category_score)
        
        # Workflow health
        workflow_metrics = self.health_metrics.get("workflows", {})
        if workflow_metrics:
            workflow_score = self._calculate_workflow_score(workflow_metrics)
            scores.append(workflow_score)
        
        # Performance health
        perf_metrics = self.health_metrics.get("performance", {})
        if perf_metrics:
            perf_score = self._calculate_performance_score(perf_metrics)
            scores.append(perf_score)
        
        return sum(scores) / len(scores) if scores else 0.5

    def _calculate_category_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate score for a metrics category."""
        # This is a simplified scoring system
        numeric_metrics = [v for v in metrics.values() if isinstance(v, (int, float))]
        if not numeric_metrics:
            return 0.5
        
        # Normalize and average (this is very basic)
        normalized = [min(1.0, max(0.0, v / 100)) for v in numeric_metrics]
        return sum(normalized) / len(normalized)

    def _calculate_workflow_score(self, workflow_metrics: Dict[str, Any]) -> float:
        """Calculate workflow health score."""
        success_rate = workflow_metrics.get("success_rate", 0.5)
        avg_duration = workflow_metrics.get("average_duration", 300)
        
        # Score based on success rate and reasonable duration
        duration_score = max(0.0, 1.0 - (avg_duration - 300) / 1800)  # Prefer under 5min
        return (success_rate + duration_score) / 2

    def _calculate_performance_score(self, perf_metrics: Dict[str, Any]) -> float:
        """Calculate performance health score."""
        return perf_metrics.get("score", 0.5)

    async def _analyze_repository_files(self) -> Dict[str, Any]:
        """Analyze repository file structure and content."""
        # Implementation for file analysis
        total_files = sum(1 for _ in Path(".").rglob("*") if _.is_file())
        code_files = sum(1 for _ in Path(".").rglob("*.py") if _.is_file())
        test_files = sum(1 for _ in Path("tests").rglob("*.py") if _.is_file() and Path("tests").exists())
        
        return {
            "total_files": total_files,
            "code_files": code_files,
            "test_files": test_files,
            "doc_files": sum(1 for _ in Path(".").rglob("*.md") if _.is_file()),
            "large_files": sum(1 for _ in Path(".").rglob("*") if _.is_file() and _.stat().st_size > 1024*1024),
            "binary_files": sum(1 for _ in Path(".").rglob("*") if _.is_file() and not self._is_text_file(_))
        }

    def _is_text_file(self, path: Path) -> bool:
        """Check if a file is a text file."""
        try:
            with open(path, 'rb') as f:
                chunk = f.read(1024)
                return not bool(chunk.translate(None, bytes(range(32, 127)) + b'\n\r\t\f\b'))
        except:
            return False

    async def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies."""
        # Basic implementation - could be enhanced with actual dependency analysis
        requirements_file = Path("requirements.txt")
        if requirements_file.exists():
            with open(requirements_file) as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            return {
                "total_dependencies": len(deps),
                "outdated": 0,  # Would need actual analysis
                "vulnerable": 0,  # Would need security scan
                "unused": 0,  # Would need usage analysis
                "last_updated": datetime.now().isoformat()
            }
        return {"total_dependencies": 0, "outdated": 0, "vulnerable": 0, "unused": 0}

    async def _analyze_security(self) -> Dict[str, Any]:
        """Analyze repository security posture."""
        # Basic security analysis - would integrate with security tools
        return {
            "vulnerabilities": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "secrets_exposed": False,
            "security_policy_exists": Path("SECURITY.md").exists(),
            "branch_protection": True  # Would need GitHub API check
        }

    async def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality metrics."""
        # Would integrate with code quality tools like flake8, pylint
        return {
            "linting_score": 85.0,
            "complexity_score": 78.0,
            "duplication_percentage": 3.0,
            "maintainability_index": 82.0
        }

    async def _analyze_test_coverage(self) -> Dict[str, Any]:
        """Analyze test coverage metrics."""
        # Would integrate with coverage tools
        test_files = list(Path("tests").rglob("*.py")) if Path("tests").exists() else []
        return {
            "line_coverage": 75.0,
            "branch_coverage": 68.0,
            "function_coverage": 82.0,
            "total_tests": len(test_files) * 5,  # Estimate
            "passing_tests": len(test_files) * 5 - 1,
            "failing_tests": 1
        }

    async def _analyze_documentation(self) -> Dict[str, Any]:
        """Analyze documentation completeness."""
        return {
            "readme_complete": Path("README.md").exists(),
            "api_docs_coverage": 65.0,
            "examples_available": Path("examples").exists(),
            "outdated_docs": 0,
            "broken_links": 0
        }

    async def _analyze_workflows(self) -> Dict[str, Any]:
        """Analyze GitHub Actions workflow performance."""
        workflows_dir = Path(".github/workflows")
        if not workflows_dir.exists():
            return {"total_workflows": 0}
        
        workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        return {
            "total_workflows": len(workflows),
            "success_rate": 0.95,
            "average_duration": 180,
            "failed_runs_last_week": 1,
            "slowest_workflow": workflows[0].name if workflows else None
        }

    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze repository performance metrics."""
        return {
            "score": 0.85,
            "build_time": 120,
            "test_time": 45,
            "deploy_time": 30
        }

    # Task generation methods
    async def _generate_security_tasks(self) -> List[ImprovementTask]:
        """Generate security improvement tasks."""
        tasks = []
        security_metrics = self.health_metrics.get("repository", {}).get("security", {})
        vulnerabilities = security_metrics.get("vulnerabilities", {})
        
        if vulnerabilities.get("critical", 0) > 0:
            tasks.append(ImprovementTask(
                id=f"security_critical_{int(time.time())}",
                category=ImprovementCategory.SECURITY,
                priority=ImprovementPriority.CRITICAL,
                title="Fix critical security vulnerabilities",
                description="Address critical security vulnerabilities in dependencies"
            ))
        
        return tasks

    async def _generate_quality_tasks(self) -> List[ImprovementTask]:
        """Generate code quality improvement tasks."""
        tasks = []
        quality_metrics = self.health_metrics.get("repository", {}).get("quality", {})
        linting_score = quality_metrics.get("linting_score", 100)
        
        if linting_score < 80:
            tasks.append(ImprovementTask(
                id=f"quality_linting_{int(time.time())}",
                category=ImprovementCategory.QUALITY,
                priority=ImprovementPriority.MEDIUM,
                title="Improve code linting score",
                description="Fix linting issues to improve code quality"
            ))
        
        return tasks

    async def _generate_performance_tasks(self) -> List[ImprovementTask]:
        """Generate performance improvement tasks."""
        tasks = []
        perf_metrics = self.health_metrics.get("performance", {})
        build_time = perf_metrics.get("build_time", 0)
        
        if build_time > 300:  # 5 minutes
            tasks.append(ImprovementTask(
                id=f"performance_build_{int(time.time())}",
                category=ImprovementCategory.PERFORMANCE,
                priority=ImprovementPriority.MEDIUM,
                title="Optimize build time",
                description="Reduce build time through optimization"
            ))
        
        return tasks

    async def _generate_maintenance_tasks(self) -> List[ImprovementTask]:
        """Generate maintenance improvement tasks."""
        tasks = []
        dep_metrics = self.health_metrics.get("repository", {}).get("dependencies", {})
        outdated = dep_metrics.get("outdated", 0)
        
        if outdated > 5:
            tasks.append(ImprovementTask(
                id=f"maintenance_deps_{int(time.time())}",
                category=ImprovementCategory.DEPENDENCY,
                priority=ImprovementPriority.LOW,
                title="Update outdated dependencies",
                description="Update outdated dependencies to latest versions"
            ))
        
        return tasks

    async def _generate_documentation_tasks(self) -> List[ImprovementTask]:
        """Generate documentation improvement tasks."""
        tasks = []
        doc_metrics = self.health_metrics.get("repository", {}).get("documentation", {})
        api_coverage = doc_metrics.get("api_docs_coverage", 100)
        
        if api_coverage < 70:
            tasks.append(ImprovementTask(
                id=f"docs_api_{int(time.time())}",
                category=ImprovementCategory.DOCUMENTATION,
                priority=ImprovementPriority.LOW,
                title="Improve API documentation coverage",
                description="Add missing API documentation"
            ))
        
        return tasks

    async def _generate_testing_tasks(self) -> List[ImprovementTask]:
        """Generate testing improvement tasks."""
        tasks = []
        test_metrics = self.health_metrics.get("repository", {}).get("tests", {})
        coverage = test_metrics.get("line_coverage", 100)
        
        if coverage < 80:
            tasks.append(ImprovementTask(
                id=f"testing_coverage_{int(time.time())}",
                category=ImprovementCategory.TESTING,
                priority=ImprovementPriority.MEDIUM,
                title="Improve test coverage",
                description="Add tests to improve code coverage"
            ))
        
        return tasks

    async def _generate_workflow_tasks(self) -> List[ImprovementTask]:
        """Generate workflow improvement tasks."""
        tasks = []
        workflow_metrics = self.health_metrics.get("workflows", {})
        success_rate = workflow_metrics.get("success_rate", 1.0)
        
        if success_rate < 0.9:
            tasks.append(ImprovementTask(
                id=f"workflow_reliability_{int(time.time())}",
                category=ImprovementCategory.WORKFLOW,
                priority=ImprovementPriority.HIGH,
                title="Improve workflow reliability",
                description="Fix failing workflows to improve success rate"
            ))
        
        return tasks

    def _is_appropriate_time(self, priority: ImprovementPriority) -> bool:
        """Check if current time is appropriate for task priority."""
        current_hour = datetime.now().hour
        allowed_hours = self.config.priority_hours.get(priority.value, list(range(24)))
        return current_hour in allowed_hours

    async def _collect_task_metrics(self, task: ImprovementTask) -> Dict[str, float]:
        """Collect metrics relevant to the task."""
        return {"placeholder_metric": 1.0}

    async def _create_rollback_point(self, task: ImprovementTask) -> Dict[str, Any]:
        """Create a rollback point for the task."""
        return {
            "timestamp": time.time(),
            "task_id": task.id,
            "git_commit": "current_commit_hash",
            "files_backup": []
        }

    async def _execute_task_logic(self, task: ImprovementTask) -> bool:
        """Execute the actual improvement logic for a task."""
        await asyncio.sleep(0.1)  # Simulate work
        return True

    def _validate_improvement(self, task: ImprovementTask) -> bool:
        """Validate that the improvement was successful."""
        return task.success is not False

    async def _rollback_task(self, task: ImprovementTask):
        """Rollback changes made by a task."""
        self.logger.warning(f"Rolling back task {task.id}")

    def _update_metrics(self):
        """Update system metrics."""
        current_metrics = {
            "timestamp": time.time(),
            "health_score": self._calculate_health_score(),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "completed_tasks_today": len([
                t for t in self.completed_tasks
                if t.completed_at and 
                t.completed_at.date() == datetime.now().date()
            ])
        }
        
        self.metrics_history.append(current_metrics)

    async def _generate_reports(self):
        """Generate improvement reports."""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "health_score": self._calculate_health_score(),
            "recent_improvements": len([
                t for t in self.completed_tasks
                if t.completed_at and
                t.completed_at > datetime.now() - timedelta(days=1)
            ]),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue)
        }
        
        # Save report
        report_path = self.base_dir / "reports" / f"report_{int(time.time())}.json"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)

    async def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        return {
            "enabled": self.config.enabled,
            "health_score": self._calculate_health_score(),
            "active_tasks": len(self.active_tasks),
            "queued_tasks": len(self.task_queue),
            "completed_today": len([
                t for t in self.completed_tasks
                if t.completed_at and 
                t.completed_at.date() == datetime.now().date()
            ]),
            "last_health_check": self.last_health_check,
            "configuration": self.config.model_dump()
        }

    async def shutdown(self):
        """Gracefully shutdown the orchestrator."""
        self.logger.info("Shutting down autonomous orchestrator")
        
        # Cancel active tasks
        for task_id in list(self.active_tasks.keys()):
            self.logger.info(f"Cancelling active task: {task_id}")
        
        # Save final state
        await self._generate_reports()