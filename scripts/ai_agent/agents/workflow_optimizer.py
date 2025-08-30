"""Workflow Optimizer Agent for analyzing and improving project workflows."""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
import copy
import traceback

from ..core.base_agent import BaseAgent


class WorkflowOptimizerAgent(BaseAgent):
    """Analyzes and optimizes workflow configurations."""

    def __init__(self, config: Dict[str, Any] | None = None):
        """Initialize the workflow optimizer agent.

        Args:
            config: Agent configuration
        """
        super().__init__("workflow_optimizer", config)
        self._workflows = {}
        self._metrics = {}

    def analyze_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze workflow structure and performance.

        Args:
            workflow_data: Dictionary containing workflow tasks and dependencies

        Returns:
            Dict containing analysis results
        """
        tasks = workflow_data.get("tasks", [])

        # Calculate metrics
        total_duration = sum(task.get("duration", 0) for task in tasks)
        critical_path = self._find_critical_path(tasks)
        bottlenecks = self._identify_bottlenecks(tasks)

        return {
            "total_duration": total_duration,
            "critical_path": critical_path,
            "bottlenecks": bottlenecks,
        }

    def analyze_resource_usage(self, workflow_data: Dict[str, Any]) -> Dict[str, int]:
        """Analyze resource utilization across tasks.

        Args:
            workflow_data: Dictionary containing workflow tasks and resources

        Returns:
            Dict mapping resources to their total usage duration
        """
        resources = {}
        for task in workflow_data.get("tasks", []):
            duration = task.get("duration", 0)
            for resource in task.get("resources", []):
                resources[resource] = resources.get(resource, 0) + duration
        return resources

    def optimize_parallel_execution(
        self, workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize workflow for parallel execution.

        Args:
            workflow_data: Dictionary containing workflow tasks

        Returns:
            Dict containing optimization results
        """
        tasks = workflow_data.get("tasks", [])
        parallel_groups = self._group_parallel_tasks(tasks)

        total_duration = sum(
            max(task.get("duration", 0) for task in group) for group in parallel_groups
        )

        return {
            "total_duration": total_duration,  # Use the parallel duration as total
            "parallel_duration": total_duration,
            "parallel_groups": parallel_groups,
            "sequential_duration": sum(task.get("duration", 0) for task in tasks),
        }

    def optimize_resource_allocation(
        self, workflow_data: Dict[str, Any], constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize resource allocation within constraints.

        Args:
            workflow_data: Dictionary containing workflow tasks
            constraints: Resource constraints to consider

        Returns:
            Dict containing allocation results including allocations and utilization metrics
        """
        tasks = workflow_data.get("tasks", [])
        allocations = self._allocate_resources(tasks, constraints)

        return {
            "allocations": allocations,
            "metrics": {
                "total_tasks": len(tasks),
                "resource_requests": len(
                    set(r for t in tasks for r in t.get("resources", []))
                ),
            },
            "feasible": self._validate_allocations(tasks, constraints),
            "constraints": constraints,
        }

        return {
            "allocations": allocations,
            "feasible": self._check_allocation_feasibility(allocations, constraints),
        }

    def _find_critical_path(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Find the critical path through tasks.

        Args:
            tasks: List of task dictionaries

        Returns:
            List of task IDs in critical path
        """
        # Build dependency graph
        graph = {task["id"]: task["dependencies"] for task in tasks}

        # Calculate earliest start times
        earliest_times = {}
        for task in tasks:
            earliest_times[task["id"]] = task.get("duration", 0)
            for dep in task.get("dependencies", []):
                if dep in earliest_times:
                    earliest_times[task["id"]] = max(
                        earliest_times[task["id"]],
                        earliest_times[dep] + task.get("duration", 0),
                    )

        # Find critical path
        critical_path = []
        # Get key with maximum value using type-safe key function
        current = max(earliest_times.keys(), key=lambda k: earliest_times[k])
        while current:
            critical_path.append(current)
            deps = graph[current]
            current = max(deps, key=lambda d: earliest_times[d]) if deps else None

        return list(reversed(critical_path))

    def _identify_bottlenecks(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Identify bottleneck tasks.

        Args:
            tasks: List of task dictionaries

        Returns:
            List of task IDs causing bottlenecks
        """
        avg_duration = (
            sum(task.get("duration", 0) for task in tasks) / len(tasks) if tasks else 0
        )
        return [
            task["id"] for task in tasks if task.get("duration", 0) > avg_duration * 1.5
        ]

    def _calculate_success_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate workflow success rate.

        Args:
            metrics: Dictionary containing workflow metrics

        Returns:
            Success rate as a float between 0 and 1
        """
        completed = metrics.get("completed_tasks", 0)
        failed = metrics.get("failed_tasks", 0)
        total = completed + failed
        return completed / total if total > 0 else 0.0

    def get_optimization_suggestions(self, workflow_data: Dict[str, Any]) -> List[str]:
        """Generate optimization suggestions.

        Args:
            workflow_data: Dictionary containing workflow configuration

        Returns:
            List of optimization suggestions
        """
        suggestions = []
        analysis = self.analyze_workflow(workflow_data)
        resource_usage = self.analyze_resource_usage(workflow_data)

        # Check for long duration
        if analysis["total_duration"] > 300:  # 5 minutes
            suggestions.append("Consider splitting long-running tasks")

        # Check for bottlenecks
        if analysis["bottlenecks"]:
            suggestions.append("Optimize or parallelize bottleneck tasks")

        # Check dependency chains
        if len(analysis["critical_path"]) > 5:
            suggestions.append(
                "Long dependency chain detected - consider restructuring"
            )

        # Check resource optimization opportunities
        if any(usage > 60 for usage in resource_usage.values()):  # Over 1 minute
            suggestions.append(
                "Resource usage is high - consider resource optimization and scaling"
            )

        # Always suggest resource optimization for tasks with multiple resources
        multi_resource_tasks = [
            t for t in workflow_data.get("tasks", []) if len(t.get("resources", [])) > 1
        ]
        if multi_resource_tasks:
            suggestions.append(
                "Consider optimizing resource allocation for tasks using multiple resources"
            )

        # Check for parallel execution opportunities
        independent_tasks = [
            t for t in workflow_data.get("tasks", []) if not t.get("dependencies")
        ]
        if len(independent_tasks) > 1:
            suggestions.append(
                "Multiple independent tasks detected - consider parallel execution"
            )

        return suggestions

    def monitor_task_execution(
        self, task_id: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Monitor execution of a specific task.

        Args:
            task_id: Task identifier
            task_data: Task configuration data

        Returns:
            Dictionary containing monitoring statistics
        """
        planned_duration = task_data.get("duration", 0)
        actual_duration = task_data.get("actual_duration", 0)
        deviation = actual_duration - planned_duration

        return {
            "planned_duration": planned_duration,
            "actual_duration": actual_duration,
            "deviation": deviation,
            "within_expected": abs(deviation)
            <= planned_duration * 0.2,  # 20% tolerance
        }

    def adapt_workflow(
        self, workflow_data: Dict[str, Any], execution_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Adapt workflow based on execution history.

        Args:
            workflow_data: Current workflow configuration
            execution_history: List of previous execution results

        Returns:
            Updated workflow configuration
        """
        adapted = copy.deepcopy(workflow_data)
        tasks = adapted.get("tasks", [])

        for task in tasks:
            task_history = [h for h in execution_history if h["task_id"] == task["id"]]
            if task_history:
                avg_duration = sum(h["actual"] for h in task_history) / len(
                    task_history
                )
                confidence = min(
                    1.0, len(task_history) / 5
                )  # More history = higher confidence
                task["duration"] = int(avg_duration)
                task["confidence_factor"] = confidence

        adapted["adaptation_reason"] = "Duration estimates updated based on history"
        return adapted

    def generate_workflow_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow performance report.

        Args:
            metrics: Dictionary containing workflow metrics

        Returns:
            Dictionary containing report details
        """
        metrics["success_rate"] = self._calculate_success_rate(metrics)
        return {
            "summary": {
                "tasks_completed": metrics["completed_tasks"],
                "tasks_failed": metrics["failed_tasks"],
                "success_rate": metrics["success_rate"],
                "total_duration": metrics["total_duration"],
            },
            "resource_usage": metrics["resource_usage"],
            "recommendations": self._generate_recommendations(metrics),
        }

    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations.

        Args:
            metrics: Dictionary containing workflow metrics

        Returns:
            List of recommendations
        """
        recommendations = []
        success_rate = metrics["success_rate"]
        resource_usage = metrics.get("resource_usage", {})

        if success_rate < 0.9:
            recommendations.append("Consider improving task reliability")

        for resource, usage in resource_usage.items():
            if usage > 80:
                recommendations.append(
                    f"High {resource} utilization - consider scaling"
                )

        return recommendations

    def _validate_allocations(
        self, tasks: List[Dict[str, Any]], constraints: Dict[str, Any]
    ) -> bool:
        """Validate resource allocations against constraints."""
        # For now, a simple validation that assumes if we could allocate, it's valid
        return all(
            all(resource in constraints for resource in task.get("resources", []))
            for task in tasks
        )

    def optimize_cost(
        self, workflow_data: Dict[str, Any], cost_factors: Dict[str, float]
    ) -> Dict[str, Any]:
        """Optimize workflow for cost efficiency.

        Args:
            workflow_data: Dictionary containing workflow tasks
            cost_factors: Cost multipliers for different resources

        Returns:
            Dict containing cost optimization results
        """
        tasks = workflow_data.get("tasks", [])
        resource_usage = self.analyze_resource_usage(workflow_data)
        total_duration_hours = sum(task.get("duration", 0) for task in tasks) / 3600.0

        # Initialize all resources
        resources = {"cpu", "memory", "io"}

        # Print input state
        print(f"Resource usage: {resource_usage}")
        print(f"Cost factors: {cost_factors}")

        # Initialize required resources
        required_resources = ["cpu", "memory", "io"]

        # Initialize normalized usage and cost breakdown with all required resources
        normalized_usage = {resource: 0.0 for resource in required_resources}
        cost_breakdown = {resource: 0.0 for resource in required_resources}

        # Convert durations to hours/GB and calculate costs
        cost_mapping = {"cpu": "cpu_hour", "memory": "memory_gb_hour", "io": "io_gb"}

        for resource in required_resources:
            # Get and normalize usage
            duration = resource_usage.get(resource, 0)
            if resource in ["cpu", "memory"]:
                normalized_usage[resource] = duration / 3600.0  # Convert to hours
            else:
                normalized_usage[resource] = duration / (1024 * 1024)  # Convert to GB

            # Calculate cost using normalized usage
            cost_factor_key = cost_mapping[resource]
            cost_factor = cost_factors.get(cost_factor_key, 0.0)
            cost_breakdown[resource] = normalized_usage[resource] * cost_factor

        # Print output state
        print(f"Normalized usage: {normalized_usage}")
        print(f"Cost breakdown: {cost_breakdown}")

        total_cost = sum(cost_breakdown.values())

        return {
            "total_cost": total_cost,
            "cost_breakdown": cost_breakdown,
            "duration_hours": total_duration_hours,
            "resource_usage": normalized_usage,
            "suggestions": self._generate_cost_suggestions(tasks),
        }

    def validate_config(self) -> bool:
        """Validate agent configuration.

        Returns:
            bool: True if config is valid
        """
        try:
            assert isinstance(self.config, dict)
            assert "log_level" in self.config
            return True
        except Exception as e:
            self.logger.error(f"Invalid config: {e}")
            return False

    def run(self) -> Dict[str, Any]:
        """Run workflow optimization.

        Returns:
            Optimization results
        """
        try:
            workflow_file = self.config["workflow_file"]
            with open(workflow_file, "r") as f:
                workflow_data = yaml.safe_load(f)

            analysis = self.analyze_workflow(workflow_data)
            resource_usage = self.analyze_resource_usage(workflow_data)
            suggestions = self.get_optimization_suggestions(workflow_data)

            return {
                "status": "success",
                "analysis": analysis,
                "resource_usage": resource_usage,
                "suggestions": suggestions,
            }
        except Exception as e:
            self.logger.error(
                f"Workflow optimization failed: {str(e)}\n{traceback.format_exc()}"
            )
            return {"status": "error", "error": str(e)}

    def monitor_task_execution(
        self, task_id: str, task_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Monitor execution metrics for a task.

        Args:
            task_id: Task identifier
            task_data: Task configuration data

        Returns:
            Dict containing monitoring results
        """
        import time

        start_time = time.time()
        duration = task_data.get("duration", 0)

        # Simulate or monitor task execution
        time.sleep(0.1)  # Minimal simulation

        actual_duration = time.time() - start_time
        deviation = actual_duration - duration

        return {
            "task_id": task_id,
            "planned_duration": duration,
            "actual_duration": actual_duration,
            "deviation": deviation,
            "within_expected": abs(deviation) <= duration * 0.1,  # 10% tolerance
        }

    def adapt_workflow(
        self, workflow_data: Dict[str, Any], execution_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Adapt workflow based on execution history.

        Args:
            workflow_data: Current workflow configuration
            execution_history: List of past execution metrics

        Returns:
            Dict containing adapted workflow configuration
        """
        adapted = copy.deepcopy(workflow_data)
        tasks = adapted.get("tasks", [])

        for task in tasks:
            task_history = [h for h in execution_history if h["task_id"] == task["id"]]

            if task_history:
                avg_duration = sum(h["actual"] for h in task_history) / len(
                    task_history
                )
                task["duration"] = avg_duration
                task["confidence_factor"] = self._calculate_confidence(task_history)

        return {
            "tasks": tasks,
            "adaptation_reason": "Duration estimates updated based on history",
        }

    def generate_workflow_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive workflow performance report.

        Args:
            metrics: Collected workflow metrics

        Returns:
            Dict containing report data
        """
        total = metrics["completed_tasks"] + metrics["failed_tasks"]
        success_rate = round(metrics["completed_tasks"] / total, 1) if total > 0 else 0

        return {
            "success_rate": success_rate,
            "efficiency_metrics": {
                "throughput": metrics["completed_tasks"] / metrics["total_duration"],
                "average_task_duration": metrics["total_duration"] / total,
            },
            "resource_utilization": {
                resource: usage / metrics["total_duration"] * 100
                for resource, usage in metrics["resource_usage"].items()
            },
            "recommendations": self._generate_recommendations(metrics),
        }

    def _find_critical_path(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Find the critical path through the workflow."""
        # Simplified implementation - returns longest chain
        task_map = {task["id"]: task for task in tasks}
        paths = []

        for task in tasks:
            if not task.get("dependencies"):
                path = self._trace_path(task["id"], task_map)
                paths.append(path)

        return max(paths, key=lambda p: sum(task_map[t]["duration"] for t in p))

    def _trace_path(self, start: str, task_map: Dict[str, Dict]) -> List[str]:
        """Trace a path from a starting task through its dependencies."""
        path = [start]
        current = task_map[start]

        while True:
            next_tasks = [
                t for t in task_map.values() if start in t.get("dependencies", [])
            ]

            if not next_tasks:
                break

            next_task = max(next_tasks, key=lambda t: t["duration"])
            path.append(next_task["id"])
            current = next_task
            start = next_task["id"]

        return path

    def _identify_bottlenecks(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Identify workflow bottlenecks."""
        # Simple implementation - identify tasks with longest duration
        if not tasks:
            return []

        max_duration = max(task.get("duration", 0) for task in tasks)
        return [task["id"] for task in tasks if task.get("duration", 0) == max_duration]

    def _group_parallel_tasks(self, tasks: List[Dict[str, Any]]) -> List[List[Dict]]:
        """Group tasks that can be executed in parallel."""
        # Simple implementation - group by dependency level
        groups = []
        remaining = tasks.copy()

        while remaining:
            group = [
                task
                for task in remaining
                if all(
                    dep not in [t["id"] for t in remaining]
                    for dep in task.get("dependencies", [])
                )
            ]

            if not group:
                break

            groups.append(group)
            remaining = [t for t in remaining if t not in group]

        return groups

    def _allocate_resources(
        self, tasks: List[Dict[str, Any]], constraints: Dict[str, Any]
    ) -> Dict[str, Dict]:
        """Allocate resources to tasks within constraints."""
        allocations = {}

        for task in tasks:
            task_allocation = {}
            for resource in task.get("resources", []):
                if resource in constraints:
                    # Handle numeric constraints
                    if isinstance(constraints[resource], (int, float)):
                        request = task.get("resource_request", {}).get(resource, 1)
                        task_allocation[resource] = min(
                            float(request), float(constraints[resource])
                        )
                    else:
                        # For string-based constraints (like "4GB", "100MB/s"), assign the constraint
                        task_allocation[resource] = constraints[resource]
            allocations[task["id"]] = task_allocation

        return allocations

    def _check_allocation_feasibility(
        self, allocations: Dict[str, Dict], constraints: Dict[str, Any]
    ) -> bool:
        """Check if resource allocation is feasible."""
        resource_usage = {}

        for task_allocation in allocations.values():
            for resource, amount in task_allocation.items():
                resource_usage[resource] = resource_usage.get(resource, 0) + amount

        return all(
            resource_usage.get(resource, 0) <= constraint
            for resource, constraint in constraints.items()
        )

    def _generate_cost_suggestions(self, tasks: List[Dict[str, Any]]) -> List[str]:
        """Generate cost optimization suggestions."""
        suggestions = []

        # Example suggestions based on task properties
        resource_heavy_tasks = [
            task["id"] for task in tasks if len(task.get("resources", [])) > 1
        ]

        if resource_heavy_tasks:
            suggestions.append(
                f"Consider optimizing resource usage in tasks: {', '.join(resource_heavy_tasks)}"
            )

        # Check for tasks with high duration
        long_tasks = [
            task["id"]
            for task in tasks
            if task.get("duration", 0) > 60  # Over 1 minute
        ]

        if long_tasks:
            suggestions.append(
                f"Consider breaking down long-running tasks: {', '.join(long_tasks)}"
            )

        return suggestions

    def _calculate_confidence(self, history: List[Dict[str, Any]]) -> float:
        """Calculate confidence factor from execution history."""
        if not history:
            return 0.0

        deviations = [abs(h["actual"] - h["planned"]) for h in history]
        avg_deviation = sum(deviations) / len(deviations)
        max_duration = max(h["actual"] for h in history)

        return 1.0 - (avg_deviation / max_duration if max_duration > 0 else 0.0)

    def _generate_recommendations(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []

        # Calculate success rate
        total_tasks = metrics["completed_tasks"] + metrics["failed_tasks"]
        success_rate = (
            metrics["completed_tasks"] / total_tasks if total_tasks > 0 else 0
        )

        if success_rate < 0.9:
            recommendations.append("Consider improving task reliability")

        for resource, usage in metrics["resource_usage"].items():
            if usage / metrics["total_duration"] > 0.8:
                recommendations.append(
                    f"High {resource} utilization - consider scaling"
                )

        return recommendations

    def validate_config(self) -> bool:
        """Validate agent configuration.

        Returns:
            True if configuration is valid
        """
        # Check if workflows directory exists
        project_root = self.get_project_root()
        workflows_dir = project_root / ".github" / "workflows"
        return workflows_dir.exists()

    def run(self) -> Dict[str, Any]:
        """Run workflow optimization analysis.

        Returns:
            Workflow optimization results
        """
        project_root = self.get_project_root()

        results = {
            "workflow_analysis": self._analyze_workflows(project_root),
            "optimization_suggestions": self._suggest_optimizations(project_root),
            "best_practices": self._check_best_practices(project_root),
            "performance_insights": self._analyze_performance(project_root),
        }

        return results

    def _analyze_workflows(self, root: Path) -> Dict[str, Any]:
        """Analyze existing GitHub Actions workflows.

        Args:
            root: Project root path

        Returns:
            Workflow analysis results
        """
        workflows_dir = root / ".github" / "workflows"
        analysis = {
            "total_workflows": 0,
            "workflows": {},
            "triggers": set(),
            "jobs": set(),
            "actions_used": set(),
        }

        if not workflows_dir.exists():
            return analysis

        for workflow_file in workflows_dir.glob("*.yml"):
            try:
                with open(workflow_file, "r") as f:
                    workflow = yaml.safe_load(f)

                analysis["total_workflows"] += 1
                workflow_name = workflow_file.stem

                workflow_info = {
                    "name": workflow.get("name", workflow_name),
                    "triggers": list(workflow.get("on", {}).keys()),
                    "jobs": list(workflow.get("jobs", {}).keys()),
                    "file_size": workflow_file.stat().st_size,
                }

                analysis["workflows"][workflow_name] = workflow_info
                analysis["triggers"].update(workflow_info["triggers"])
                analysis["jobs"].update(workflow_info["jobs"])

                # Extract actions used
                for job in workflow.get("jobs", {}).values():
                    for step in job.get("steps", []):
                        if "uses" in step:
                            analysis["actions_used"].add(step["uses"].split("@")[0])

            except Exception as e:
                self.logger.warning(f"Error analyzing {workflow_file}: {e}")

        # Convert sets to lists for JSON serialization
        analysis["triggers"] = list(analysis["triggers"])
        analysis["jobs"] = list(analysis["jobs"])
        analysis["actions_used"] = list(analysis["actions_used"])

        return analysis

    def _check_best_practices(self, root: Path) -> Dict[str, Any]:
        """Check adherence to GitHub Actions best practices.

        Args:
            root: Project root path

        Returns:
            Best practices compliance report
        """
        practices = {
            "using_specific_action_versions": False,
            "has_timeout_limits": False,
            "uses_environments": False,
            "has_manual_triggers": False,
            "follows_naming_conventions": True,
            "issues": [],
        }

        workflows_dir = root / ".github" / "workflows"
        if not workflows_dir.exists():
            return practices

        for workflow_file in workflows_dir.glob("*.yml"):
            try:
                workflow_content = workflow_file.read_text()

                # Check for specific action versions (not @main or @master)
                if "@v" in workflow_content or "@sha" in workflow_content:
                    practices["using_specific_action_versions"] = True

                # Check for timeout settings
                if "timeout-minutes" in workflow_content:
                    practices["has_timeout_limits"] = True

                # Check for manual triggers
                if "workflow_dispatch" in workflow_content:
                    practices["has_manual_triggers"] = True

                # Check for environment usage
                if "environment:" in workflow_content:
                    practices["uses_environments"] = True

                # Check naming conventions
                with open(workflow_file, "r") as f:
                    workflow = yaml.safe_load(f)
                    name = workflow.get("name", "")
                    if not name or name.islower():
                        practices["follows_naming_conventions"] = False
                        practices["issues"].append(
                            f"{workflow_file.name}: Workflow name should "
                            f"follow proper capitalization"
                        )

            except Exception as e:
                practices["issues"].append(f"Error reading {workflow_file.name}: {e}")

        return practices

    def _analyze_performance(self, root: Path) -> Dict[str, Any]:
        """Analyze workflow performance characteristics.

        Args:
            root: Project root path

        Returns:
            Performance analysis results
        """
        performance = {
            "total_workflow_files": 0,
            "average_file_size": 0,
            "complexity_indicators": {
                "total_jobs": 0,
                "total_steps": 0,
                "matrix_builds": 0,
                "conditional_steps": 0,
            },
            "optimization_opportunities": [],
        }

        workflows_dir = root / ".github" / "workflows"
        if not workflows_dir.exists():
            return performance

        workflow_files = list(workflows_dir.glob("*.yml"))
        performance["total_workflow_files"] = len(workflow_files)

        if not workflow_files:
            return performance

        total_size = 0
        total_jobs = 0
        total_steps = 0

        for workflow_file in workflow_files:
            try:
                file_size = workflow_file.stat().st_size
                total_size += file_size

                with open(workflow_file, "r") as f:
                    workflow = yaml.safe_load(f)

                jobs = workflow.get("jobs", {})
                total_jobs += len(jobs)

                for job in jobs.values():
                    steps = job.get("steps", [])
                    total_steps += len(steps)

                    # Check for matrix builds
                    if "strategy" in job and "matrix" in job["strategy"]:
                        performance["complexity_indicators"]["matrix_builds"] += 1

                    # Check for conditional steps
                    for step in steps:
                        if "if" in step:
                            performance["complexity_indicators"][
                                "conditional_steps"
                            ] += 1

            except Exception as e:
                self.logger.warning(f"Error analyzing {workflow_file}: {e}")

        performance["average_file_size"] = total_size // len(workflow_files)
        performance["complexity_indicators"]["total_jobs"] = total_jobs
        performance["complexity_indicators"]["total_steps"] = total_steps

        # Generate optimization opportunities
        if performance["average_file_size"] > 5000:  # 5KB threshold
            performance["optimization_opportunities"].append(
                "Large workflow files detected - consider splitting "
                "complex workflows"
            )

        if total_steps > total_jobs * 10:  # More than 10 steps per job on average
            performance["optimization_opportunities"].append(
                "High step count detected - consider consolidating " "related steps"
            )

        return performance

    def _suggest_optimizations(self, root: Path) -> List[str]:
        """Suggest workflow optimizations.

        Args:
            root: Project root path

        Returns:
            List of optimization suggestions
        """
        suggestions = []
        workflows_dir = root / ".github" / "workflows"
        if not workflows_dir.exists():
            suggestions.append(
                "No GitHub Actions workflows found - consider adding automation"
            )
            return suggestions

        workflow_files = list(workflows_dir.glob("*.yml"))

        all_triggers = set()
        has_ci = False
        has_cd = False
        has_caching = False

        for workflow_file in workflow_files:
            try:
                with open(workflow_file, "r") as f:
                    workflow = yaml.safe_load(f)

                triggers = workflow.get("on", {})
                all_triggers.update(triggers.keys())

                # Check for CI/CD patterns
                name = workflow.get("name", "").lower()
                if any(term in name for term in ["ci", "test", "build"]):
                    has_ci = True
                if any(term in name for term in ["cd", "deploy", "release"]):
                    has_cd = True

                # Check for caching
                workflow_content = workflow_file.read_text()
                if "cache" in workflow_content.lower():
                    has_caching = True

            except Exception as e:
                self.logger.warning(f"Error analyzing {workflow_file}: {e}")

        # Generate suggestions based on analysis
        if "pull_request" not in all_triggers:
            suggestions.append("Add pull_request triggers for better CI integration")

        if not has_ci:
            suggestions.append("Consider adding a continuous integration workflow")

        if not has_cd:
            suggestions.append("Consider adding a deployment workflow")

        if not has_caching:
            suggestions.append("Add dependency caching to improve build performance")

        # Check for security best practices
        if any("secrets." in wf.read_text() for wf in workflow_files):
            suggestions.append("Review secret usage and consider using environments")

        return suggestions

        workflow_files = list(workflows_dir.glob("*.yml"))

        if not workflow_files:
            suggestions.append("Add GitHub Actions workflows for automation")
            return suggestions

        # Analyze workflow patterns
