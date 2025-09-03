#!/usr/bin/env python3
"""
Cross-Repository Propagation Tool for EpochCore RAS

This tool automates the deployment of the EpochCore RAS recursive improvement
system across multiple repositories, handling different repository types and
ensuring compatibility.
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import yaml

class CrossRepoPropagator:
    """Main class for propagating EpochCore RAS across repositories."""
    
    def __init__(self, source_repo_path: str = "."):
        self.source_repo_path = Path(source_repo_path).resolve()
        self.propagation_config = self._load_propagation_config()
        self.supported_languages = {
            "python": {"files": ["requirements.txt", "pyproject.toml", "setup.py"], "extensions": [".py"], "primary": True},
            "javascript": {"files": ["package.json", "yarn.lock"], "extensions": [".js", ".jsx"], "primary": False},
            "typescript": {"files": ["package.json", "tsconfig.json"], "extensions": [".ts", ".tsx"], "primary": False},
            "java": {"files": ["pom.xml", "build.gradle"], "extensions": [".java"], "primary": False},
            "go": {"files": ["go.mod", "go.sum"], "extensions": [".go"], "primary": False},
            "rust": {"files": ["Cargo.toml"], "extensions": [".rs"], "primary": False}
        }
        
    def _load_propagation_config(self) -> Dict:
        """Load propagation configuration."""
        config_path = self.source_repo_path / "config" / "cross_repo_config.yml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Get default propagation configuration."""
        return {
            "core_files": [
                "recursive_improvement/",
                "integration.py",
                ".github/workflows/recursive-autonomy.yml",
                "config/",
                "templates/"
            ],
            "optional_files": [
                "dashboard.py",
                "tests/test_recursive_integration.py",
                "docs/ARCHITECTURE.md"
            ],
            "adaptation_rules": {
                "python": {
                    "dependency_file": "requirements.txt",
                    "test_command": "python -m pytest",
                    "setup_script": "setup_python.sh"
                },
                "javascript": {
                    "dependency_file": "package.json", 
                    "test_command": "npm test",
                    "setup_script": "setup_node.sh"
                }
            },
            "validation_checks": [
                "check_git_repo",
                "check_language_support",
                "check_existing_ci",
                "check_dependencies"
            ]
        }
    
    def analyze_target_repo(self, repo_path: str) -> Dict:
        """Analyze target repository to determine compatibility and requirements."""
        repo_path = Path(repo_path).resolve()
        analysis = {
            "path": str(repo_path),
            "exists": repo_path.exists(),
            "is_git_repo": False,
            "languages": [],
            "ci_systems": [],
            "existing_automation": [],
            "compatibility_score": 0,
            "recommendations": []
        }
        
        if not analysis["exists"]:
            analysis["recommendations"].append("Repository path does not exist")
            return analysis
            
        # Check if it's a Git repository
        git_dir = repo_path / ".git"
        if git_dir.exists():
            analysis["is_git_repo"] = True
            analysis["compatibility_score"] += 20
        else:
            analysis["recommendations"].append("Not a Git repository - initialize with 'git init'")
            
        # Detect programming languages
        analysis["languages"] = self._detect_languages(repo_path)
        if analysis["languages"]:
            analysis["compatibility_score"] += 30
            
        # Check for existing CI/CD systems
        analysis["ci_systems"] = self._detect_ci_systems(repo_path)
        if analysis["ci_systems"]:
            analysis["compatibility_score"] += 20
            
        # Check for existing automation
        analysis["existing_automation"] = self._detect_existing_automation(repo_path)
        if analysis["existing_automation"]:
            analysis["compatibility_score"] += 10
            
        # Final compatibility assessment
        if analysis["compatibility_score"] >= 70:
            analysis["recommendations"].append("✅ Repository is highly compatible for EpochCore RAS deployment")
        elif analysis["compatibility_score"] >= 40:
            analysis["recommendations"].append("⚠️  Repository is moderately compatible - some setup required")
        else:
            analysis["recommendations"].append("❌ Repository requires significant setup before deployment")
            
        return analysis
    
    def _detect_languages(self, repo_path: Path) -> List[str]:
        """Detect programming languages used in the repository."""
        languages = []
        
        for lang, config in self.supported_languages.items():
            # Check by configuration files
            for file_pattern in config["files"]:
                if list(repo_path.glob(f"**/{file_pattern}")):
                    languages.append(lang)
                    break
            
            # Check by file extensions
            if lang not in languages:
                for ext in config.get("extensions", []):
                    if list(repo_path.glob(f"**/*{ext}")):
                        languages.append(lang)
                        break
                    
        return languages
    
    def _detect_ci_systems(self, repo_path: Path) -> List[str]:
        """Detect existing CI/CD systems."""
        ci_systems = []
        
        # GitHub Actions
        if (repo_path / ".github" / "workflows").exists():
            ci_systems.append("github_actions")
            
        # GitLab CI
        if (repo_path / ".gitlab-ci.yml").exists():
            ci_systems.append("gitlab_ci")
            
        # Jenkins
        if (repo_path / "Jenkinsfile").exists():
            ci_systems.append("jenkins")
            
        # CircleCI
        if (repo_path / ".circleci").exists():
            ci_systems.append("circleci")
            
        return ci_systems
    
    def _detect_existing_automation(self, repo_path: Path) -> List[str]:
        """Detect existing automation tools."""
        automation = []
        
        # Check for common automation files
        automation_patterns = {
            "makefile": ["Makefile", "makefile"],
            "docker": ["Dockerfile", "docker-compose.yml"],
            "scripts": ["scripts/", "bin/"],
            "pre_commit": [".pre-commit-config.yaml"],
            "dependabot": [".github/dependabot.yml"]
        }
        
        for tool, patterns in automation_patterns.items():
            for pattern in patterns:
                if (repo_path / pattern).exists():
                    automation.append(tool)
                    break
                    
        return automation
    
    def propagate_to_repository(self, target_repo_path: str, 
                              modules: Optional[List[str]] = None,
                              dry_run: bool = False) -> Dict:
        """Propagate EpochCore RAS system to target repository."""
        
        target_path = Path(target_repo_path).resolve()
        
        # Analyze target repository first
        analysis = self.analyze_target_repo(target_path)
        
        if analysis["compatibility_score"] < 30:
            return {
                "success": False,
                "error": "Repository compatibility too low for automatic deployment",
                "analysis": analysis,
                "recommendations": analysis["recommendations"]
            }
        
        # Determine which modules to propagate
        if modules is None:
            modules = ["core", "workflows", "integration", "documentation"]
            
        propagation_result = {
            "success": True,
            "target_repo": str(target_path),
            "modules_propagated": [],
            "files_copied": [],
            "adaptations_made": [],
            "errors": [],
            "warnings": []
        }
        
        try:
            # Create backup if not dry run
            if not dry_run:
                backup_path = self._create_backup(target_path)
                propagation_result["backup_created"] = str(backup_path)
                
            # Propagate core recursive improvement system
            if "core" in modules:
                result = self._propagate_core_system(target_path, dry_run)
                propagation_result["modules_propagated"].append("core")
                propagation_result["files_copied"].extend(result.get("files_copied", []))
                
            # Propagate GitHub Actions workflows
            if "workflows" in modules:
                result = self._propagate_workflows(target_path, analysis, dry_run)
                propagation_result["modules_propagated"].append("workflows")
                propagation_result["files_copied"].extend(result.get("files_copied", []))
                propagation_result["adaptations_made"].extend(result.get("adaptations", []))
                
            # Propagate integration layer
            if "integration" in modules:
                result = self._propagate_integration(target_path, analysis, dry_run)
                propagation_result["modules_propagated"].append("integration")
                propagation_result["files_copied"].extend(result.get("files_copied", []))
                
            # Propagate documentation
            if "documentation" in modules:
                result = self._propagate_documentation(target_path, dry_run)
                propagation_result["modules_propagated"].append("documentation")
                propagation_result["files_copied"].extend(result.get("files_copied", []))
                
        except Exception as e:
            propagation_result["success"] = False
            propagation_result["error"] = str(e)
            
        return propagation_result
    
    def _create_backup(self, target_path: Path) -> Path:
        """Create backup of target repository before propagation."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = target_path.parent / f"{target_path.name}_backup_{timestamp}"
        
        # Copy only essential files to avoid large backups
        essential_patterns = [
            "*.md", "*.txt", "*.yml", "*.yaml", "*.json", 
            ".github/", "src/", "lib/", "tests/", "docs/"
        ]
        
        backup_dir.mkdir(exist_ok=True)
        
        for pattern in essential_patterns:
            for file_path in target_path.glob(pattern):
                if file_path.is_file():
                    relative_path = file_path.relative_to(target_path)
                    destination = backup_dir / relative_path
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, destination)
                elif file_path.is_dir() and not file_path.name.startswith('.'):
                    shutil.copytree(file_path, backup_dir / file_path.name, dirs_exist_ok=True)
                    
        return backup_dir
    
    def _propagate_core_system(self, target_path: Path, dry_run: bool) -> Dict:
        """Propagate core recursive improvement system."""
        result = {"files_copied": []}
        
        source_recursive = self.source_repo_path / "recursive_improvement"
        target_recursive = target_path / "recursive_improvement"
        
        if dry_run:
            print(f"[DRY RUN] Would copy {source_recursive} -> {target_recursive}")
        else:
            if source_recursive.exists():
                shutil.copytree(source_recursive, target_recursive, dirs_exist_ok=True)
                result["files_copied"].append("recursive_improvement/")
                
        return result
    
    def _propagate_workflows(self, target_path: Path, analysis: Dict, dry_run: bool) -> Dict:
        """Propagate GitHub Actions workflows with adaptations."""
        result = {"files_copied": [], "adaptations": []}
        
        if "github_actions" not in analysis["ci_systems"]:
            # Create .github/workflows directory
            workflows_dir = target_path / ".github" / "workflows"
            if dry_run:
                print(f"[DRY RUN] Would create {workflows_dir}")
            else:
                workflows_dir.mkdir(parents=True, exist_ok=True)
                
        # Copy and adapt recursive-autonomy workflow
        source_workflow = self.source_repo_path / ".github" / "workflows" / "recursive-autonomy.yml"
        target_workflow = target_path / ".github" / "workflows" / "recursive-autonomy.yml"
        
        if source_workflow.exists():
            if dry_run:
                print(f"[DRY RUN] Would copy and adapt {source_workflow} -> {target_workflow}")
            else:
                # Adapt workflow for target repository
                adapted_content = self._adapt_workflow_for_repo(source_workflow, analysis)
                target_workflow.write_text(adapted_content)
                result["files_copied"].append(".github/workflows/recursive-autonomy.yml")
                result["adaptations"].append("Adapted workflow for repository language and structure")
                
        return result
    
    def _adapt_workflow_for_repo(self, workflow_path: Path, analysis: Dict) -> str:
        """Adapt workflow content for target repository."""
        content = workflow_path.read_text()
        
        # Adapt based on detected languages
        if "javascript" in analysis["languages"] and "python" not in analysis["languages"]:
            # Replace Python setup with Node.js setup
            content = content.replace(
                "uses: actions/setup-python@v5",
                "uses: actions/setup-node@v4"
            )
            content = content.replace(
                "python-version: ${{ env.PYTHON_VERSION }}",
                "node-version: ${{ env.NODE_VERSION }}"
            )
            content = content.replace(
                "pip install -r requirements.txt",
                "npm install"
            )
            
        # Add repository-specific environment variables
        env_section = "env:\n  PYTHON_VERSION: '3.12'\n  NODE_VERSION: '18'"
        if "javascript" in analysis["languages"]:
            env_section += "\n  NPM_VERSION: 'latest'"
        if "java" in analysis["languages"]:
            env_section += "\n  JAVA_VERSION: '17'"
            
        return content
    
    def _propagate_integration(self, target_path: Path, analysis: Dict, dry_run: bool) -> Dict:
        """Propagate integration scripts."""
        result = {"files_copied": []}
        
        # Copy integration.py with adaptations
        source_integration = self.source_repo_path / "integration.py"
        target_integration = target_path / "integration.py"
        
        if source_integration.exists():
            if dry_run:
                print(f"[DRY RUN] Would copy {source_integration} -> {target_integration}")
            else:
                shutil.copy2(source_integration, target_integration)
                result["files_copied"].append("integration.py")
                
        return result
    
    def _propagate_documentation(self, target_path: Path, dry_run: bool) -> Dict:
        """Propagate documentation."""
        result = {"files_copied": []}
        
        # Create docs directory if it doesn't exist
        docs_dir = target_path / "docs"
        if dry_run:
            print(f"[DRY RUN] Would create/update {docs_dir}")
        else:
            docs_dir.mkdir(exist_ok=True)
            
            # Copy architecture documentation
            source_arch = self.source_repo_path / "docs" / "ARCHITECTURE.md"
            if source_arch.exists():
                target_arch = docs_dir / "EPOCHCORE_ARCHITECTURE.md"
                shutil.copy2(source_arch, target_arch)
                result["files_copied"].append("docs/EPOCHCORE_ARCHITECTURE.md")
                
        return result
    
    def validate_propagation(self, target_repo_path: str) -> Dict:
        """Validate successful propagation of EpochCore RAS system."""
        target_path = Path(target_repo_path).resolve()
        
        validation_result = {
            "success": True,
            "checks_passed": [],
            "checks_failed": [],
            "warnings": [],
            "overall_health": "unknown"
        }
        
        # Check 1: Core recursive improvement system
        recursive_dir = target_path / "recursive_improvement"
        if recursive_dir.exists() and (recursive_dir / "__init__.py").exists():
            validation_result["checks_passed"].append("✅ Recursive improvement system found")
        else:
            validation_result["checks_failed"].append("❌ Recursive improvement system missing")
            validation_result["success"] = False
            
        # Check 2: Integration script
        integration_file = target_path / "integration.py"
        if integration_file.exists():
            validation_result["checks_passed"].append("✅ Integration script found")
        else:
            validation_result["checks_failed"].append("❌ Integration script missing")
            validation_result["success"] = False
            
        # Check 3: GitHub Actions workflow
        workflow_file = target_path / ".github" / "workflows" / "recursive-autonomy.yml"
        if workflow_file.exists():
            validation_result["checks_passed"].append("✅ GitHub Actions workflow found")
        else:
            validation_result["checks_failed"].append("❌ GitHub Actions workflow missing")
            validation_result["warnings"].append("⚠️  Consider adding GitHub Actions workflow for automation")
            
        # Check 4: Try to run basic validation
        try:
            os.chdir(target_path)
            result = subprocess.run(
                [sys.executable, "integration.py", "validate"], 
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                validation_result["checks_passed"].append("✅ System validation successful")
            else:
                validation_result["checks_failed"].append(f"❌ System validation failed: {result.stderr}")
                validation_result["success"] = False
        except Exception as e:
            validation_result["warnings"].append(f"⚠️  Could not run system validation: {e}")
            
        # Calculate overall health
        total_checks = len(validation_result["checks_passed"]) + len(validation_result["checks_failed"])
        if total_checks > 0:
            success_rate = len(validation_result["checks_passed"]) / total_checks
            if success_rate >= 0.8:
                validation_result["overall_health"] = "excellent"
            elif success_rate >= 0.6:
                validation_result["overall_health"] = "good"
            elif success_rate >= 0.4:
                validation_result["overall_health"] = "fair"
            else:
                validation_result["overall_health"] = "poor"
                
        return validation_result
    
    def generate_propagation_report(self, results: List[Dict]) -> str:
        """Generate comprehensive propagation report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# EpochCore RAS Cross-Repository Propagation Report
Generated: {timestamp}

## Summary
- Repositories analyzed: {len(results)}
- Successful propagations: {sum(1 for r in results if r.get('success', False))}
- Failed propagations: {sum(1 for r in results if not r.get('success', False))}

## Detailed Results
"""
        
        for i, result in enumerate(results, 1):
            status = "✅ SUCCESS" if result.get("success", False) else "❌ FAILED"
            report += f"\n### Repository {i}: {result.get('target_repo', 'Unknown')}\n"
            report += f"**Status**: {status}\n\n"
            
            if result.get("success"):
                report += f"**Modules Propagated**: {', '.join(result.get('modules_propagated', []))}\n"
                report += f"**Files Copied**: {len(result.get('files_copied', []))}\n"
                if result.get("adaptations_made"):
                    report += f"**Adaptations Made**: {len(result['adaptations_made'])}\n"
                if result.get("backup_created"):
                    report += f"**Backup Created**: {result['backup_created']}\n"
            else:
                report += f"**Error**: {result.get('error', 'Unknown error')}\n"
                if result.get("recommendations"):
                    report += "**Recommendations**:\n"
                    for rec in result["recommendations"]:
                        report += f"- {rec}\n"
                        
        return report


def main():
    """Main CLI interface for cross-repository propagation."""
    parser = argparse.ArgumentParser(
        description="EpochCore RAS Cross-Repository Propagation Tool"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze target repository compatibility")
    analyze_parser.add_argument("repo_path", help="Path to target repository")
    
    # Propagate command
    propagate_parser = subparsers.add_parser("propagate", help="Propagate EpochCore RAS to repository")
    propagate_parser.add_argument("repo_path", help="Path to target repository")
    propagate_parser.add_argument("--modules", nargs="+", 
                                help="Modules to propagate (core, workflows, integration, documentation)")
    propagate_parser.add_argument("--dry-run", action="store_true", 
                                help="Show what would be done without making changes")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate propagated system")
    validate_parser.add_argument("repo_path", help="Path to target repository")
    
    # Batch propagate command
    batch_parser = subparsers.add_parser("batch", help="Propagate to multiple repositories")
    batch_parser.add_argument("config_file", help="JSON/YAML file with repository list")
    batch_parser.add_argument("--dry-run", action="store_true")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    propagator = CrossRepoPropagator()
    
    if args.command == "analyze":
        analysis = propagator.analyze_target_repo(args.repo_path)
        print(json.dumps(analysis, indent=2))
        
    elif args.command == "propagate":
        result = propagator.propagate_to_repository(
            args.repo_path, 
            args.modules,
            args.dry_run
        )
        print(json.dumps(result, indent=2))
        
    elif args.command == "validate":
        validation = propagator.validate_propagation(args.repo_path)
        print(json.dumps(validation, indent=2))
        
    elif args.command == "batch":
        with open(args.config_file) as f:
            if args.config_file.endswith('.yml') or args.config_file.endswith('.yaml'):
                config = yaml.safe_load(f)
            else:
                config = json.load(f)
                
        results = []
        for repo_path in config.get("repositories", []):
            result = propagator.propagate_to_repository(
                repo_path, 
                config.get("modules"),
                args.dry_run
            )
            results.append(result)
            
        # Generate and save report
        report = propagator.generate_propagation_report(results)
        report_file = f"propagation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
            
        print(f"Batch propagation completed. Report saved to: {report_file}")
        
    return 0


if __name__ == "__main__":
    sys.exit(main())