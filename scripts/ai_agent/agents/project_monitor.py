"""Project Monitor Agent for tracking project status and generating reports."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Callable
import time

from ..core.base_agent import BaseAgent


class ProjectMonitorAgent(BaseAgent):
    """Monitor project files and directories for changes."""

    def __init__(
        self, name: str = "project_monitor", config: Dict[str, Any] | None = None
    ):
        """Initialize the project monitor.

        Args:
            name: Name of the monitor instance
            config: Configuration dictionary with:
                   - project_root: Root directory to monitor
                   - watch_patterns: List of glob patterns to watch
                   - ignore_patterns: List of glob patterns to ignore
                   - scan_interval: Interval between scans in seconds
        """
        super().__init__(name, config or {})
        self.project_root = self.config.get("project_root", ".")
        self.watch_patterns = self.config.get("watch_patterns", ["*"])
        self.ignore_patterns = self.config.get(
            "ignore_patterns", ["__pycache__", "*.pyc"]
        )
        self.scan_interval = self.config.get("scan_interval", 1.0)
        self._file_states = {}  # Tracks file modification times
        self._handlers = []  # Event handlers

    def validate_config(self) -> bool:
        """Validate the monitor configuration."""
        # Check types
        if (
            not isinstance(self.watch_patterns, list)
            or not isinstance(self.ignore_patterns, list)
            or not isinstance(self.scan_interval, (int, float))
        ):
            return False

        # Check project root exists
        try:
            path = Path(self.project_root)
            return path.exists() and path.is_dir()
        except:
            return False

    def add_event_handler(self, handler: Callable[[str, str], None]):
        """Add an event handler function.

        Args:
            handler: Function that takes (event_type, file_path)
        """
        self._handlers.append(handler)

    def is_valid_path(self, path: str) -> bool:
        """Check if a path should be monitored.

        Args:
            path: Relative path to check

        Returns:
            bool: True if path matches watch patterns and not ignore patterns
        """
        from fnmatch import fnmatch

        # Check ignore patterns first
        for pattern in self.ignore_patterns:
            if fnmatch(path, pattern):
                return False

        # Then check watch patterns
        for pattern in self.watch_patterns:
            if fnmatch(path, pattern):
                return True

        return False

    def scan_for_changes(self) -> Dict[str, set]:
        """Scan for file changes.

        Returns:
            Dict with sets of added, modified and deleted files
        """
        changes = {"added": set(), "modified": set(), "deleted": set()}

        current_files = {}

        # Walk through project directory
        for root, _, files in os.walk(self.project_root):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, self.project_root)

                if not self.is_valid_path(rel_path):
                    continue

                try:
                    mtime = os.path.getmtime(abs_path)
                    current_files[rel_path] = mtime

                    if rel_path not in self._file_states:
                        changes["added"].add(rel_path)
                    elif mtime > self._file_states[rel_path]:
                        changes["modified"].add(rel_path)
                except OSError:
                    continue

        # Check for deleted files
        for path in self._file_states:
            if path not in current_files:
                changes["deleted"].add(path)

        # Update state
        self._file_states = current_files

        # Notify handlers
        for event_type, paths in changes.items():
            for path in paths:
                for handler in self._handlers:
                    try:
                        handler(event_type, path)
                    except Exception:
                        # Log error but continue processing
                        continue

        return changes

    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Run the monitor continuously.

        Returns:
            Dict containing run status
        """
        try:
            while True:
                changes = self.scan_for_changes()
                if any(changes.values()):
                    self.logger.info(f"Detected changes: {changes}")
                time.sleep(self.scan_interval)
        except KeyboardInterrupt:
            return {"status": "stopped", "reason": "user interrupt"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def cleanup(self):
        """Clean up monitor resources."""
        self._file_states.clear()
        self._handlers.clear()


class ProjectMonitorAgent(BaseAgent):
    """Agent for monitoring project status and generating reports."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Project Monitor Agent.

        Args:
            config: Agent configuration
        """
        super().__init__("project_monitor", config)

    def validate_config(self) -> bool:
        """Validate agent configuration.

        Returns:
            True if configuration is valid
        """
        # No special configuration required for basic monitoring
        return True

    def run(self) -> Dict[str, Any]:
        """Run the project monitoring tasks.

        Returns:
            Project status report
        """
        project_root = self.get_project_root()

        # Collect project metrics
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_structure": self._analyze_project_structure(project_root),
            "workflow_status": self._check_workflow_files(project_root),
            "asset_status": self._check_assets(project_root),
            "test_coverage": self._analyze_test_coverage(project_root),
            "documentation": self._check_documentation(project_root),
        }

        # Save report if configured
        if self.config.get("save_report", True):
            self._save_report(report, project_root)

        return report

    def _analyze_project_structure(self, root: Path) -> Dict[str, Any]:
        """Analyze project structure and organization.

        Args:
            root: Project root path

        Returns:
            Project structure analysis
        """
        structure = {
            "total_files": 0,
            "python_files": 0,
            "test_files": 0,
            "doc_files": 0,
            "workflow_files": 0,
            "directories": [],
        }

        try:
            for path in root.rglob("*"):
                if path.is_file():
                    structure["total_files"] += 1

                    if path.suffix == ".py":
                        structure["python_files"] += 1
                    elif path.name.startswith("test_") or "test" in path.parts:
                        structure["test_files"] += 1
                    elif path.suffix in [".md", ".rst", ".txt"]:
                        structure["doc_files"] += 1
                    elif path.suffix in [".yml", ".yaml"] and ".github" in path.parts:
                        structure["workflow_files"] += 1
                elif path.is_dir() and not path.name.startswith("."):
                    structure["directories"].append(str(path.relative_to(root)))

        except Exception as e:
            self.logger.warning(f"Error analyzing project structure: {e}")

        return structure

    def _check_workflow_files(self, root: Path) -> Dict[str, Any]:
        """Check GitHub Actions workflow files.

        Args:
            root: Project root path

        Returns:
            Workflow status analysis
        """
        workflows_dir = root / ".github" / "workflows"
        status = {
            "workflows_exist": workflows_dir.exists(),
            "workflow_count": 0,
            "workflows": [],
        }

        if workflows_dir.exists():
            for workflow in workflows_dir.glob("*.yml"):
                status["workflow_count"] += 1
                status["workflows"].append(
                    {
                        "name": workflow.name,
                        "size": workflow.stat().st_size,
                        "modified": datetime.fromtimestamp(
                            workflow.stat().st_mtime
                        ).isoformat(),
                    }
                )

        return status

    def _check_assets(self, root: Path) -> Dict[str, Any]:
        """Check asset generation and organization.

        Args:
            root: Project root path

        Returns:
            Asset status analysis
        """
        assets_dir = root / "assets"
        status = {
            "assets_dir_exists": assets_dir.exists(),
            "masters_exist": False,
            "icons_generated": False,
            "csv_config_exists": False,
        }

        if assets_dir.exists():
            masters_dir = assets_dir / "masters"
            icons_dir = assets_dir / "icons"
            csv_config = root / "strategy_icon_variant_matrix.csv"

            status["masters_exist"] = masters_dir.exists() and any(
                masters_dir.glob("*.svg")
            )
            status["icons_generated"] = icons_dir.exists() and any(icons_dir.rglob("*"))
            status["csv_config_exists"] = csv_config.exists()

        return status

    def _analyze_test_coverage(self, root: Path) -> Dict[str, Any]:
        """Analyze test coverage and test files.

        Args:
            root: Project root path

        Returns:
            Test coverage analysis
        """
        tests_dir = root / "tests"
        scripts_dir = root / "scripts"

        coverage = {
            "tests_dir_exists": tests_dir.exists(),
            "test_files": 0,
            "script_files": 0,
            "coverage_ratio": 0.0,
        }

        if tests_dir.exists():
            coverage["test_files"] = len(list(tests_dir.glob("test_*.py")))

        if scripts_dir.exists():
            coverage["script_files"] = len(list(scripts_dir.glob("*.py")))

        if coverage["script_files"] > 0:
            coverage["coverage_ratio"] = (
                coverage["test_files"] / coverage["script_files"]
            )

        return coverage

    def _check_documentation(self, root: Path) -> Dict[str, Any]:
        """Check documentation completeness.

        Args:
            root: Project root path

        Returns:
            Documentation analysis
        """
        docs = {
            "readme_exists": (root / "README.md").exists(),
            "contributing_exists": (root / "CONTRIBUTING.md").exists(),
            "docs_dir_exists": (root / "docs").exists(),
            "doc_files": 0,
        }

        docs_dir = root / "docs"
        if docs_dir.exists():
            docs["doc_files"] = len(list(docs_dir.glob("*.md")))

        return docs

    def _save_report(self, report: Dict[str, Any], root: Path) -> None:
        """Save the project report to file.

        Args:
            report: Report data
            root: Project root path
        """
        try:
            reports_dir = root / "reports"
            reports_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"project_status_{timestamp}.json"

            with open(report_file, "w") as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"Project report saved to {report_file}")

        except Exception as e:
            self.logger.warning(f"Could not save report: {e}")
