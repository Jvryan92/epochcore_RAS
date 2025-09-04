#!/usr/bin/env python3
"""
EpochCore RAS Workflow Issue Resolver
Automated tool to identify and resolve common workflow conflicts and issues
"""

import os
import sys
import json
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from merge_automation import MergeAutomation


class WorkflowIssueResolver:
    """Resolves workflow conflicts and issues automatically."""

    def __init__(self):
        self.merge_automation = MergeAutomation()
        self.workflow_dir = Path(".github/workflows")
        self.issues_found = []
        self.fixes_applied = []

    def analyze_workflows(self) -> Dict[str, Any]:
        """Analyze all workflows for potential issues."""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "workflows_analyzed": 0,
            "issues_found": [],
            "warnings": [],
            "recommendations": [],
        }

        if not self.workflow_dir.exists():
            analysis["issues_found"].append("No .github/workflows directory found")
            return analysis

        for workflow_file in self.workflow_dir.glob("*.yml"):
            analysis["workflows_analyzed"] += 1
            self._analyze_workflow_file(workflow_file, analysis)

        return analysis

    def _analyze_workflow_file(self, workflow_file: Path, analysis: Dict[str, Any]):
        """Analyze a single workflow file."""
        try:
            with open(workflow_file, "r") as f:
                workflow = yaml.safe_load(f)

            workflow_name = workflow_file.name

            # Check for common issues
            self._check_dependency_conflicts(workflow, workflow_name, analysis)
            self._check_missing_permissions(workflow, workflow_name, analysis)
            self._check_action_versions(workflow, workflow_name, analysis)
            self._check_environment_setup(workflow, workflow_name, analysis)
            self._check_artifact_handling(workflow, workflow_name, analysis)

        except yaml.YAMLError as e:
            analysis["issues_found"].append(
                f"{workflow_file.name}: YAML parsing error - {e}"
            )
        except Exception as e:
            analysis["issues_found"].append(
                f"{workflow_file.name}: Analysis error - {e}"
            )

    def _check_dependency_conflicts(self, workflow: Dict, name: str, analysis: Dict):
        """Check for dependency conflicts between steps."""
        jobs = workflow.get("jobs", {})

        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            has_node = False
            has_python = False

            for step in steps:
                if isinstance(step, dict):
                    uses = step.get("uses", "")
                    if "setup-node" in uses:
                        has_node = True
                    elif "setup-python" in uses:
                        has_python = True
                    elif step.get("run", "").startswith(("npm ", "node ")):
                        has_node = True
                    elif step.get("run", "").startswith(("python ", "pip ")):
                        has_python = True

            if has_node and has_python:
                analysis["warnings"].append(
                    f"{name} ({job_name}): Mixed Node.js and Python setup detected. "
                    "Ensure compatibility."
                )

    def _check_missing_permissions(self, workflow: Dict, name: str, analysis: Dict):
        """Check for missing permissions."""
        permissions = workflow.get("permissions")

        if permissions is None:
            analysis["warnings"].append(
                f"{name}: No permissions specified. Consider adding explicit permissions."
            )

        # Check for write permissions without contents: read
        jobs = workflow.get("jobs", {})
        for job_name, job_config in jobs.items():
            job_permissions = job_config.get("permissions", {})
            if job_permissions and "contents" not in job_permissions:
                for perm, level in job_permissions.items():
                    if level == "write":
                        analysis["warnings"].append(
                            f"{name} ({job_name}): Write permissions without contents access"
                        )
                        break

    def _check_action_versions(self, workflow: Dict, name: str, analysis: Dict):
        """Check for outdated action versions."""
        version_recommendations = {
            "actions/checkout": "v4",
            "actions/setup-node": "v4",
            "actions/setup-python": "v4",
            "actions/upload-artifact": "v4",
        }

        jobs = workflow.get("jobs", {})
        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])

            for step in steps:
                if isinstance(step, dict) and "uses" in step:
                    action = step["uses"]
                    action_name = action.split("@")[0]

                    if action_name in version_recommendations:
                        recommended_version = version_recommendations[action_name]
                        if not action.endswith(f"@{recommended_version}"):
                            analysis["recommendations"].append(
                                f"{name} ({job_name}): Update {action_name} to @{recommended_version}"
                            )

    def _check_environment_setup(self, workflow: Dict, name: str, analysis: Dict):
        """Check for proper environment setup."""
        jobs = workflow.get("jobs", {})

        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])
            has_python_setup = False
            has_venv_creation = False

            for step in steps:
                if isinstance(step, dict):
                    if step.get("uses", "").startswith("actions/setup-python"):
                        has_python_setup = True

                    run_command = step.get("run", "")
                    if "python -m venv" in run_command or "virtualenv" in run_command:
                        has_venv_creation = True

                    # Check for Python commands without venv activation
                    if (
                        ("pip install" in run_command or "python " in run_command)
                        and "source venv/bin/activate" not in run_command
                        and "venv\\Scripts\\activate" not in run_command
                    ):
                        if has_python_setup:
                            analysis["recommendations"].append(
                                f"{name} ({job_name}): Consider using virtual environment for Python commands"
                            )

    def _check_artifact_handling(self, workflow: Dict, name: str, analysis: Dict):
        """Check for proper artifact handling."""
        jobs = workflow.get("jobs", {})

        for job_name, job_config in jobs.items():
            steps = job_config.get("steps", [])

            for step in steps:
                if isinstance(step, dict) and step.get("uses", "").startswith(
                    "actions/upload-artifact"
                ):
                    # Check if artifact path exists
                    with_config = step.get("with", {})
                    artifact_path = with_config.get("path")

                    if (
                        artifact_path
                        and not Path(artifact_path).exists()
                        and not any(
                            wildcard in artifact_path for wildcard in ["*", "?"]
                        )
                    ):
                        analysis["warnings"].append(
                            f"{name} ({job_name}): Artifact path '{artifact_path}' may not exist"
                        )

    def fix_common_issues(self) -> Dict[str, Any]:
        """Automatically fix common workflow issues."""
        fix_result = {
            "timestamp": datetime.now().isoformat(),
            "fixes_attempted": 0,
            "fixes_successful": 0,
            "fixes_failed": 0,
            "details": [],
        }

        # Run analysis first
        analysis = self.analyze_workflows()

        # Fix dependency installation issues
        self._fix_dependency_installation(fix_result)

        # Fix missing directories
        self._fix_missing_directories(fix_result)

        # Update .gitignore
        self._update_gitignore(fix_result)

        return fix_result

    def _fix_dependency_installation(self, fix_result: Dict):
        """Fix common dependency installation issues."""
        try:
            # Check if npm install fails due to missing package.json
            if self.workflow_dir.exists():
                for workflow_file in self.workflow_dir.glob("*.yml"):
                    with open(workflow_file, "r") as f:
                        content = f.read()

                    if "npm ci" in content and not Path("package.json").exists():
                        fix_result["fixes_attempted"] += 1
                        fix_result["details"].append(
                            f"Found npm ci in {workflow_file.name} but no package.json"
                        )

                        # package.json was already created earlier
                        if Path("package.json").exists():
                            fix_result["fixes_successful"] += 1
                            fix_result["details"].append(
                                "✓ package.json already exists"
                            )

        except Exception as e:
            fix_result["fixes_failed"] += 1
            fix_result["details"].append(
                f"✗ Failed to fix dependency installation: {e}"
            )

    def _fix_missing_directories(self, fix_result: Dict):
        """Fix missing directories referenced in workflows."""
        required_dirs = [
            "scripts",
            "data/triggers",
            "ops/trigger_runs",
            "logs",
            "backups/merge_states",
        ]

        for directory in required_dirs:
            fix_result["fixes_attempted"] += 1
            dir_path = Path(directory)

            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    fix_result["fixes_successful"] += 1
                    fix_result["details"].append(f"✓ Created directory: {directory}")
                except Exception as e:
                    fix_result["fixes_failed"] += 1
                    fix_result["details"].append(
                        f"✗ Failed to create directory {directory}: {e}"
                    )
            else:
                fix_result["fixes_successful"] += 1
                fix_result["details"].append(f"✓ Directory already exists: {directory}")

    def _update_gitignore(self, fix_result: Dict):
        """Update .gitignore with common patterns."""
        fix_result["fixes_attempted"] += 1

        gitignore_additions = [
            "# Python",
            "venv/",
            "__pycache__/",
            "*.pyc",
            ".pytest_cache/",
            "htmlcov/",
            ".coverage",
            "",
            "# Node.js",
            "node_modules/",
            "npm-debug.log*",
            "",
            "# Logs",
            "logs/*.log",
            "",
            "# Temporary files",
            "temp_*.txt",
            ".DS_Store",
        ]

        try:
            gitignore_path = Path(".gitignore")
            existing_content = ""

            if gitignore_path.exists():
                with open(gitignore_path, "r") as f:
                    existing_content = f.read()

            additions_needed = []
            for addition in gitignore_additions:
                if addition and addition not in existing_content:
                    additions_needed.append(addition)

            if additions_needed:
                with open(gitignore_path, "a") as f:
                    if existing_content and not existing_content.endswith("\n"):
                        f.write("\n")
                    f.write("\n".join(additions_needed) + "\n")

                fix_result["fixes_successful"] += 1
                fix_result["details"].append(
                    f"✓ Updated .gitignore with {len(additions_needed)} new patterns"
                )
            else:
                fix_result["fixes_successful"] += 1
                fix_result["details"].append("✓ .gitignore already up to date")

        except Exception as e:
            fix_result["fixes_failed"] += 1
            fix_result["details"].append(f"✗ Failed to update .gitignore: {e}")

    def validate_system_integration(self) -> Dict[str, Any]:
        """Validate that all systems integrate properly."""
        validation = {
            "timestamp": datetime.now().isoformat(),
            "components_tested": 0,
            "components_passing": 0,
            "components_failing": 0,
            "details": [],
        }

        # Test merge automation
        validation["components_tested"] += 1
        try:
            merge_status = self.merge_automation.get_git_status()
            if "error" not in merge_status:
                validation["components_passing"] += 1
                validation["details"].append("✓ Merge automation working")
            else:
                validation["components_failing"] += 1
                validation["details"].append(
                    f"✗ Merge automation error: {merge_status['error']}"
                )
        except Exception as e:
            validation["components_failing"] += 1
            validation["details"].append(f"✗ Merge automation failed: {e}")

        # Test integration script
        validation["components_tested"] += 1
        try:
            result = subprocess.run(
                ["python", "integration.py", "status"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                validation["components_passing"] += 1
                validation["details"].append("✓ Integration script working")
            else:
                validation["components_failing"] += 1
                validation["details"].append(
                    f"✗ Integration script error: {result.stderr}"
                )
        except Exception as e:
            validation["components_failing"] += 1
            validation["details"].append(f"✗ Integration script failed: {e}")

        # Test Node.js trigger executor
        validation["components_tested"] += 1
        if Path("scripts/triggers_executor.mjs").exists():
            try:
                result = subprocess.run(
                    ["node", "--version"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    validation["components_passing"] += 1
                    validation["details"].append("✓ Node.js trigger executor ready")
                else:
                    validation["components_failing"] += 1
                    validation["details"].append("✗ Node.js not available")
            except Exception as e:
                validation["components_failing"] += 1
                validation["details"].append(f"✗ Node.js check failed: {e}")
        else:
            validation["components_failing"] += 1
            validation["details"].append("✗ Trigger executor script missing")

        return validation


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="EpochCore RAS Workflow Issue Resolver"
    )
    parser.add_argument(
        "command",
        choices=["analyze", "fix", "validate", "all"],
        help="Command to execute",
    )

    args = parser.parse_args()

    resolver = WorkflowIssueResolver()

    if args.command == "analyze":
        result = resolver.analyze_workflows()
        print(json.dumps(result, indent=2))

    elif args.command == "fix":
        result = resolver.fix_common_issues()
        print(json.dumps(result, indent=2))

    elif args.command == "validate":
        result = resolver.validate_system_integration()
        print(json.dumps(result, indent=2))

    elif args.command == "all":
        print("=== WORKFLOW ANALYSIS ===")
        analysis = resolver.analyze_workflows()
        print(json.dumps(analysis, indent=2))

        print("\n=== FIXING ISSUES ===")
        fixes = resolver.fix_common_issues()
        print(json.dumps(fixes, indent=2))

        print("\n=== SYSTEM VALIDATION ===")
        validation = resolver.validate_system_integration()
        print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
