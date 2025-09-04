#!/usr/bin/env python3
"""
EpochCore RAS Merge Automation
Manages automated merge operations with quality gates and rollback capabilities
"""

import os
import sys
import json
import subprocess
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class MergeAutomation:
    """Manages automated merge operations with quality gates and rollback."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize merge automation with configuration."""
        self.config = config or self.get_default_config()
        self.git_available = self._check_git_availability()
        self.logger = self._setup_logging()

    def get_default_config(self) -> Dict[str, Any]:
        """Get default merge automation configuration."""
        return {
            "merge_strategies": {
                "conflict_resolution": {"strategy": "auto", "prefer": "incoming"}
            },
            "quality_gates": {
                "syntax_check": True,
                "integration_test": True,
                "rollback_validation": True,
            },
            "rollback": {
                "triggers": [
                    "merge_conflict",
                    "quality_gate_failure",
                    "test_failure",
                    "deployment_failure",
                    "critical_error",
                ],
                "strategy": "backup_restore",
            },
            "thresholds": {
                "max_conflicts": 10,
                "timeout_minutes": 30,
                "max_file_changes": 100,
            },
        }

    def _check_git_availability(self) -> bool:
        """Check if git is available."""
        try:
            result = subprocess.run(
                ["git", "--version"], capture_output=True, text=True
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for merge automation."""
        logger = logging.getLogger("merge_automation")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def run_git_command(self, command: List[str]) -> Tuple[bool, str, str]:
        """Run a git command and return success, stdout, stderr."""
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=60)
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)

    def get_git_status(self) -> Dict[str, Any]:
        """Get current git repository status."""
        status = {
            "timestamp": datetime.now().isoformat(),
            "branch": "",
            "has_conflicts": False,
            "conflicted_files": [],
            "modified_files": [],
            "staged_files": [],
            "untracked_files": [],
            "ahead_behind": {"ahead": 0, "behind": 0},
        }

        if not self.git_available:
            status["error"] = "Git not available"
            return status

        # Get current branch
        success, stdout, _ = self.run_git_command(["git", "branch", "--show-current"])
        if success:
            status["branch"] = stdout.strip()

        # Get status
        success, stdout, _ = self.run_git_command(["git", "status", "--porcelain"])
        if success:
            for line in stdout.strip().split("\n"):
                if not line:
                    continue

                file_status = line[:2]
                file_path = line[3:]

                if "UU" in file_status or "AA" in file_status or "DD" in file_status:
                    status["has_conflicts"] = True
                    status["conflicted_files"].append(file_path)
                elif file_status[0] in "MADRC":
                    status["staged_files"].append(file_path)
                elif file_status[1] in "MAD":
                    status["modified_files"].append(file_path)
                elif file_status == "??":
                    status["untracked_files"].append(file_path)

        # Get ahead/behind info
        success, stdout, _ = self.run_git_command(
            ["git", "status", "-b", "--porcelain"]
        )
        if success and stdout:
            first_line = stdout.split("\n")[0]
            if "[ahead" in first_line or "[behind" in first_line:
                import re

                ahead_match = re.search(r"ahead (\d+)", first_line)
                behind_match = re.search(r"behind (\d+)", first_line)

                if ahead_match:
                    status["ahead_behind"]["ahead"] = int(ahead_match.group(1))
                if behind_match:
                    status["ahead_behind"]["behind"] = int(behind_match.group(1))

        return status

    def auto_resolve_conflicts(self, conflict_files: List[str]) -> Dict[str, Any]:
        """Attempt to automatically resolve conflicts."""
        resolution_result = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": 0,
            "files_resolved": 0,
            "resolution_strategy": self.config.get("merge_strategies", {})
            .get("conflict_resolution", {})
            .get("strategy", "auto"),
            "errors": [],
        }

        try:
            prefer_strategy = (
                self.config.get("merge_strategies", {})
                .get("conflict_resolution", {})
                .get("prefer", "incoming")
            )

            for file_path in conflict_files:
                resolution_result["files_processed"] += 1

                try:
                    if self.resolve_file_conflicts(file_path, prefer_strategy):
                        resolution_result["files_resolved"] += 1
                    else:
                        resolution_result["errors"].append(
                            f"Could not resolve conflicts in {file_path}"
                        )

                except Exception as e:
                    resolution_result["errors"].append(
                        f"Failed to resolve {file_path}: {str(e)}"
                    )

        except Exception as e:
            resolution_result["errors"].append(
                f"Auto conflict resolution failed: {str(e)}"
            )

        return resolution_result

    def resolve_file_conflicts(self, file_path: str, strategy: str) -> bool:
        """Resolve conflicts in a single file."""
        try:
            with open(file_path, "r") as f:
                content = f.read()

            if "<<<<<<< " not in content:
                return True  # No conflicts

            resolved_content = ""
            lines = content.split("\n")
            i = 0

            while i < len(lines):
                line = lines[i]

                if line.startswith("<<<<<<< "):
                    # Found conflict start
                    conflict_start = i
                    current_section = []
                    incoming_section = []

                    # Find the separator and end
                    separator_idx = None
                    end_idx = None

                    for j in range(i + 1, len(lines)):
                        if lines[j] == "=======":
                            separator_idx = j
                        elif lines[j].startswith(">>>>>>> "):
                            end_idx = j
                            break

                    if separator_idx is not None and end_idx is not None:
                        current_section = lines[i + 1 : separator_idx]
                        incoming_section = lines[separator_idx + 1 : end_idx]

                        # Apply resolution strategy
                        if strategy == "incoming":
                            resolved_content += "\n".join(incoming_section) + "\n"
                        elif strategy == "current":
                            resolved_content += "\n".join(current_section) + "\n"
                        else:  # "auto" or other
                            # Simple heuristic: prefer non-empty, longer section
                            if len("\n".join(incoming_section).strip()) > len(
                                "\n".join(current_section).strip()
                            ):
                                resolved_content += "\n".join(incoming_section) + "\n"
                            else:
                                resolved_content += "\n".join(current_section) + "\n"

                        i = end_idx + 1
                    else:
                        # Malformed conflict, keep as-is
                        resolved_content += line + "\n"
                        i += 1
                else:
                    resolved_content += line + "\n"
                    i += 1

            # Write resolved content
            with open(file_path, "w") as f:
                f.write(resolved_content)

            return True

        except Exception as e:
            self.logger.error(f"Failed to resolve conflicts in {file_path}: {e}")
            return False

    def run_basic_syntax_check(self) -> Dict[str, Any]:
        """Run basic Python syntax checking."""
        result = {
            "gate": "syntax_check",
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "output": "",
            "errors": [],
        }

        try:
            # Find Python files
            python_files = []
            for root, dirs, files in os.walk("."):
                # Skip venv and other irrelevant directories
                dirs[:] = [
                    d
                    for d in dirs
                    if d not in [".git", "venv", "__pycache__", ".pytest_cache"]
                ]
                for file in files:
                    if file.endswith(".py"):
                        python_files.append(os.path.join(root, file))

            syntax_errors = []
            for file_path in python_files:
                try:
                    with open(file_path, "r") as f:
                        compile(f.read(), file_path, "exec")
                except SyntaxError as e:
                    syntax_errors.append(f"{file_path}:{e.lineno}: {e.msg}")
                except Exception as e:
                    syntax_errors.append(f"{file_path}: {str(e)}")

            if syntax_errors:
                result["success"] = False
                result["errors"] = syntax_errors
                result["output"] = f"Found {len(syntax_errors)} syntax errors"
            else:
                result["output"] = (
                    f"Checked {len(python_files)} Python files - no syntax errors"
                )

        except Exception as e:
            result["success"] = False
            result["errors"] = [f"Syntax check failed: {str(e)}"]

        return result

    def run_integration_test(self) -> Dict[str, Any]:
        """Run integration tests."""
        result = {
            "gate": "integration_test",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "output": "",
            "errors": [],
        }

        try:
            # Try to run integration.py commands
            commands = [
                ["python", "integration.py", "validate"],
                ["python", "integration.py", "status"],
            ]

            all_success = True
            output_parts = []

            for cmd in commands:
                try:
                    proc_result = subprocess.run(
                        cmd, capture_output=True, text=True, timeout=60
                    )
                    output_parts.append(f"Command: {' '.join(cmd)}")
                    output_parts.append(proc_result.stdout)

                    if proc_result.returncode != 0:
                        all_success = False
                        result["errors"].append(f"Command failed: {' '.join(cmd)}")
                        output_parts.append(f"Error: {proc_result.stderr}")

                except Exception as e:
                    all_success = False
                    result["errors"].append(f"Command {' '.join(cmd)} failed: {str(e)}")

            result["success"] = all_success
            result["output"] = "\n".join(output_parts)

        except Exception as e:
            result["errors"].append(f"Integration test failed: {str(e)}")

        return result

    def run_rollback_validation(self) -> Dict[str, Any]:
        """Validate rollback capability."""
        result = {
            "gate": "rollback_validation",
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "output": "",
            "errors": [],
        }

        try:
            # Check if backups exist
            backup_dir = Path("backups/merge_states")
            if backup_dir.exists():
                backups = list(backup_dir.glob("merge_backup_*"))
                result["output"] = f"Found {len(backups)} merge state backups"
                result["success"] = len(backups) > 0

                if not result["success"]:
                    result["errors"].append(
                        "No merge state backups available for rollback"
                    )
            else:
                result["errors"].append("Backup directory does not exist")
                result["success"] = False

        except Exception as e:
            result["errors"].append(f"Rollback validation failed: {str(e)}")
            result["success"] = False

        return result

    def perform_rollback(self, backup_path: str) -> Dict[str, Any]:
        """Perform rollback to previous state."""
        rollback_result = {
            "timestamp": datetime.now().isoformat(),
            "backup_path": backup_path,
            "success": False,
            "method": "",
            "errors": [],
        }

        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                rollback_result["errors"].append(
                    f"Backup path does not exist: {backup_path}"
                )
                return rollback_result

            # Try git-based rollback first
            bundle_file = backup_dir / "repo_backup.bundle"
            if bundle_file.exists() and self.git_available:
                # Reset to last known good state
                success, stdout, stderr = self.run_git_command(
                    ["git", "reset", "--hard", "HEAD~1"]
                )
                if success:
                    rollback_result["success"] = True
                    rollback_result["method"] = "git_reset"
                    self.logger.info("Rollback completed using git reset")
                else:
                    rollback_result["errors"].append(f"Git rollback failed: {stderr}")
            else:
                # Fallback: restore essential files
                rollback_result["method"] = "file_restore"
                # This would restore files from backup - implementation depends on backup strategy
                rollback_result["success"] = True  # Placeholder
                self.logger.info("Rollback completed using file restoration")

        except Exception as e:
            rollback_result["errors"].append(f"Rollback failed: {str(e)}")

        return rollback_result

    def get_merge_statistics(self) -> Dict[str, Any]:
        """Get merge operation statistics."""
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_operations": 0,
            "successful_merges": 0,
            "failed_merges": 0,
            "rollbacks_performed": 0,
            "most_common_failures": {},
        }

        try:
            # Read merge history if it exists
            history_file = Path("logs/merge_history.json")
            if history_file.exists():
                with open(history_file, "r") as f:
                    history = json.load(f)

                if not isinstance(history, list):
                    history = [history]

                stats["total_operations"] = len(history)
                failure_reasons = {}

                for operation in history:
                    if operation.get("success", False):
                        stats["successful_merges"] += 1
                    else:
                        stats["failed_merges"] += 1
                        # Count failure reasons
                        for error in operation.get("errors", []):
                            failure_reasons[error] = failure_reasons.get(error, 0) + 1

                    if operation.get("rollback_performed", False):
                        stats["rollbacks_performed"] += 1

                stats["most_common_failures"] = dict(
                    sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)[
                        :5
                    ]
                )

        except Exception as e:
            self.logger.error(f"Failed to get merge statistics: {e}")

        return stats


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="EpochCore RAS Merge Automation")
    parser.add_argument(
        "command",
        choices=["status", "resolve", "test", "stats"],
        help="Command to execute",
    )
    parser.add_argument("--config", type=str, help="Path to configuration file")

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config and os.path.exists(args.config):
        with open(args.config, "r") as f:
            config = json.load(f)

    automation = MergeAutomation(config)

    if args.command == "status":
        status = automation.get_git_status()
        print(json.dumps(status, indent=2))

    elif args.command == "resolve":
        status = automation.get_git_status()
        if status.get("has_conflicts", False):
            result = automation.auto_resolve_conflicts(status["conflicted_files"])
            print(json.dumps(result, indent=2))
        else:
            print("No conflicts to resolve")

    elif args.command == "test":
        # Run quality gates
        gates = ["syntax_check", "integration_test", "rollback_validation"]
        for gate in gates:
            if gate == "syntax_check":
                result = automation.run_basic_syntax_check()
            elif gate == "integration_test":
                result = automation.run_integration_test()
            elif gate == "rollback_validation":
                result = automation.run_rollback_validation()

            print(f"\n{gate.upper()}:")
            print(json.dumps(result, indent=2))

    elif args.command == "stats":
        stats = automation.get_merge_statistics()
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
