"""Asset Manager Agent for automating icon generation and asset management."""

import csv
from pathlib import Path
from typing import Dict, Any, List

from ..core.base_agent import BaseAgent


class AssetManagerAgent(BaseAgent):
    """Agent for managing and automating asset generation tasks."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the Asset Manager Agent.

        Args:
            config: Agent configuration
        """
        super().__init__("asset_manager", config)

    def validate_config(self) -> bool:
        """Validate agent configuration.

        Returns:
            True if configuration is valid
        """
        # Check if icon generation script exists
        project_root = self.get_project_root()
        script_path = project_root / "scripts" / "generate_icons.py"
        return script_path.exists()

    def run(self) -> Dict[str, Any]:
        """Run asset management tasks.

        Returns:
            Asset management results
        """
        project_root = self.get_project_root()

        results = {
            "asset_validation": self._validate_assets(project_root),
            "generation_status": self._check_generation_status(project_root),
            "optimization_suggestions": self._suggest_optimizations(
                project_root
            ),
        }

        # Auto-generate assets if configured
        if self.config.get("auto_generate", False):
            results["generation_result"] = self._generate_assets(project_root)

        return results

    def _validate_assets(self, root: Path) -> Dict[str, Any]:
        """Validate asset files and structure.

        Args:
            root: Project root path

        Returns:
            Asset validation results
        """
        validation = {
            "masters_valid": False,
            "csv_config_valid": False,
            "output_structure_exists": False,
            "issues": [],
        }

        # Check master files
        masters_dir = root / "assets" / "masters"
        if not masters_dir.exists():
            validation["issues"].append("Masters directory does not exist")
        else:
            svg_files = list(masters_dir.glob("*.svg"))
            if not svg_files:
                validation["issues"].append("No SVG master files found")
            else:
                validation["masters_valid"] = True
                self.logger.info(f"Found {len(svg_files)} master SVG files")

        # Check CSV configuration
        csv_config = root / "strategy_icon_variant_matrix.csv"
        if not csv_config.exists():
            validation["issues"].append("CSV configuration file missing")
        else:
            try:
                with open(csv_config, "r") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    if rows:
                        validation["csv_config_valid"] = True
                        self.logger.info(
                            f"CSV config has {len(rows)} variants"
                        )
            except Exception as e:
                validation["issues"].append(f"CSV config error: {e}")

        # Check output structure
        icons_dir = root / "assets" / "icons"
        if icons_dir.exists():
            validation["output_structure_exists"] = True

        return validation

    def _check_generation_status(self, root: Path) -> Dict[str, Any]:
        """Check current asset generation status.

        Args:
            root: Project root path

        Returns:
            Generation status information
        """
        status = {
            "icons_exist": False,
            "total_variants": 0,
            "svg_count": 0,
            "png_count": 0,
            "last_generation": None,
        }

        icons_dir = root / "assets" / "icons"
        if icons_dir.exists():
            status["icons_exist"] = True

            # Count generated files
            svg_files = list(icons_dir.rglob("*.svg"))
            png_files = list(icons_dir.rglob("*.png"))

            status["svg_count"] = len(svg_files)
            status["png_count"] = len(png_files)
            status["total_variants"] = len(svg_files)  # SVGs are primary

            # Find most recent modification
            if svg_files:
                most_recent = max(svg_files, key=lambda p: p.stat().st_mtime)
                status["last_generation"] = most_recent.stat().st_mtime

        return status

    def _suggest_optimizations(self, root: Path) -> List[str]:
        """Suggest asset management optimizations.

        Args:
            root: Project root path

        Returns:
            List of optimization suggestions
        """
        suggestions = []

        # Check for missing PNG exports
        icons_dir = root / "assets" / "icons"
        if icons_dir.exists():
            svg_count = len(list(icons_dir.rglob("*.svg")))
            png_count = len(list(icons_dir.rglob("*.png")))

            if svg_count > 0 and png_count == 0:
                suggestions.append(
                    "Consider installing cairosvg for PNG export capability"
                )
            elif png_count < svg_count:
                suggestions.append(
                    f"Only {png_count}/{svg_count} SVGs have PNG exports"
                )

        # Check CSV configuration completeness
        csv_config = root / "strategy_icon_variant_matrix.csv"
        if csv_config.exists():
            try:
                with open(csv_config, "r") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)

                    # Check for common sizes
                    sizes = [int(r.get("Size (px)", 0)) for r in rows]
                    common_sizes = [16, 32, 48, 64, 128, 256]
                    missing_sizes = [s for s in common_sizes if s not in sizes]

                    if missing_sizes:
                        suggestions.append(
                            f"Consider adding common icon sizes: "
                            f"{missing_sizes}"
                        )

            except Exception as e:
                suggestions.append(f"CSV validation error: {e}")

        # Check for asset organization
        if not (root / "assets" / "icons").exists():
            suggestions.append(
                "Run icon generation to create organized asset structure"
            )

        return suggestions

    def _generate_assets(self, root: Path) -> Dict[str, Any]:
        """Generate assets using the icon generation script.

        Args:
            root: Project root path

        Returns:
            Generation results
        """
        import subprocess
        import sys

        script_path = root / "scripts" / "generate_icons.py"

        try:
            self.logger.info("Running icon generation script")
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Generation script timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
