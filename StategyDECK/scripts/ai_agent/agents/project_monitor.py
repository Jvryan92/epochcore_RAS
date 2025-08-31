"""Project Monitor Agent for tracking project status and generating reports."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from ..core.base_agent import BaseAgent


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
                    elif (
                        path.suffix in [".yml", ".yaml"]
                        and ".github" in path.parts
                    ):
                        structure["workflow_files"] += 1
                elif path.is_dir() and not path.name.startswith("."):
                    structure["directories"].append(
                        str(path.relative_to(root))
                    )

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
            status["icons_generated"] = icons_dir.exists() and any(
                icons_dir.rglob("*")
            )
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
