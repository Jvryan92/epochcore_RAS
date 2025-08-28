"""Workflow Optimizer Agent for analyzing and improving project workflows."""

import yaml
from pathlib import Path
from typing import Dict, Any, List

from ..core.base_agent import BaseAgent


class WorkflowOptimizerAgent(BaseAgent):
    """Agent for analyzing and optimizing project workflows."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Workflow Optimizer Agent.

        Args:
            config: Agent configuration
        """
        super().__init__("workflow_optimizer", config)

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
            "optimization_suggestions": self._suggest_optimizations(
                project_root
            ),
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
                            analysis["actions_used"].add(
                                step["uses"].split("@")[0]
                            )

            except Exception as e:
                self.logger.warning(f"Error analyzing {workflow_file}: {e}")

        # Convert sets to lists for JSON serialization
        analysis["triggers"] = list(analysis["triggers"])
        analysis["jobs"] = list(analysis["jobs"])
        analysis["actions_used"] = list(analysis["actions_used"])

        return analysis

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
                "Create .github/workflows directory for CI/CD automation"
            )
            return suggestions

        workflow_files = list(workflows_dir.glob("*.yml"))

        if not workflow_files:
            suggestions.append("Add GitHub Actions workflows for automation")
            return suggestions

        # Analyze workflow patterns
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
            suggestions.append(
                "Add pull_request triggers for better CI integration"
            )

        if not has_ci:
            suggestions.append(
                "Consider adding a continuous integration workflow"
            )

        if not has_cd:
            suggestions.append("Consider adding a deployment workflow")

        if not has_caching:
            suggestions.append(
                "Add dependency caching to improve build performance"
            )

        # Check for security best practices
        if any("secrets." in wf.read_text() for wf in workflow_files):
            suggestions.append(
                "Review secret usage and consider using environments"
            )

        return suggestions

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
                practices["issues"].append(
                    f"Error reading {workflow_file.name}: {e}"
                )

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
                        performance["complexity_indicators"][
                            "matrix_builds"
                        ] += 1

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

        if (
            total_steps > total_jobs * 10
        ):  # More than 10 steps per job on average
            performance["optimization_opportunities"].append(
                "High step count detected - consider consolidating "
                "related steps"
            )

        return performance
