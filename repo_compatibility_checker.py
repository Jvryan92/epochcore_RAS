#!/usr/bin/env python3
"""
Repository Compatibility Checker for EpochCore RAS

This module provides comprehensive compatibility analysis for repositories
before attempting EpochCore RAS propagation.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import yaml


@dataclass
class CompatibilityScore:
    """Data class to track compatibility scoring."""
    total_score: int = 0
    max_score: int = 100
    category_scores: Dict[str, int] = None
    critical_issues: List[str] = None
    warnings: List[str] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.category_scores is None:
            self.category_scores = {}
        if self.critical_issues is None:
            self.critical_issues = []
        if self.warnings is None:
            self.warnings = []
        if self.recommendations is None:
            self.recommendations = []
    
    @property
    def percentage(self) -> float:
        return (self.total_score / self.max_score) * 100 if self.max_score > 0 else 0
    
    @property
    def compatibility_level(self) -> str:
        if self.percentage >= 90:
            return "excellent"
        elif self.percentage >= 75:
            return "good"
        elif self.percentage >= 50:
            return "fair" 
        elif self.percentage >= 25:
            return "poor"
        else:
            return "incompatible"


class RepositoryCompatibilityChecker:
    """Main class for checking repository compatibility with EpochCore RAS."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.supported_languages = {
            "python": {"extensions": [".py"], "config_files": ["requirements.txt", "pyproject.toml", "setup.py"], "weight": 1.0},
            "javascript": {"extensions": [".js", ".jsx"], "config_files": ["package.json"], "weight": 0.8},
            "typescript": {"extensions": [".ts", ".tsx"], "config_files": ["package.json", "tsconfig.json"], "weight": 0.8},
            "java": {"extensions": [".java"], "config_files": ["pom.xml", "build.gradle"], "weight": 0.7},
            "go": {"extensions": [".go"], "config_files": ["go.mod"], "weight": 0.7},
            "rust": {"extensions": [".rs"], "config_files": ["Cargo.toml"], "weight": 0.6},
            "csharp": {"extensions": [".cs"], "config_files": ["*.csproj", "*.sln"], "weight": 0.6},
            "php": {"extensions": [".php"], "config_files": ["composer.json"], "weight": 0.5}
        }
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Default configuration
        return {
            "scoring_weights": {
                "git_repo": 10,
                "language_support": 25,
                "ci_cd": 15,
                "testing": 15,
                "documentation": 10,
                "dependencies": 10,
                "structure": 10,
                "security": 5
            },
            "minimum_compatibility": 50,
            "required_features": ["git_repo", "language_support"]
        }
    
    def check_repository(self, repo_path: str, remote_url: Optional[str] = None) -> CompatibilityScore:
        """Perform comprehensive compatibility check on repository."""
        repo_path = Path(repo_path).resolve()
        score = CompatibilityScore()
        
        # Check if repository exists
        if not repo_path.exists():
            score.critical_issues.append(f"Repository path {repo_path} does not exist")
            return score
            
        # Perform individual checks
        self._check_git_repository(repo_path, score)
        self._check_language_support(repo_path, score)
        self._check_ci_cd_systems(repo_path, score)
        self._check_testing_infrastructure(repo_path, score)
        self._check_documentation(repo_path, score)
        self._check_dependencies(repo_path, score)
        self._check_repository_structure(repo_path, score)
        self._check_security_setup(repo_path, score)
        
        # Check remote repository if URL provided
        if remote_url:
            self._check_remote_repository(remote_url, score)
            
        # Calculate final recommendations
        self._generate_recommendations(score)
        
        return score
    
    def _check_git_repository(self, repo_path: Path, score: CompatibilityScore):
        """Check Git repository status and configuration."""
        git_dir = repo_path / ".git"
        weight = self.config["scoring_weights"]["git_repo"]
        
        if not git_dir.exists():
            score.critical_issues.append("Not a Git repository")
            return
            
        score.category_scores["git_repo"] = weight
        score.total_score += weight
        
        # Check for remote repositories
        try:
            result = subprocess.run(
                ["git", "remote", "-v"], 
                cwd=repo_path, 
                capture_output=True, 
                text=True
            )
            if result.stdout.strip():
                score.recommendations.append("✅ Remote repository configured")
            else:
                score.warnings.append("⚠️  No remote repository configured")
        except Exception:
            score.warnings.append("⚠️  Unable to check Git remote configuration")
            
        # Check for uncommitted changes
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"], 
                cwd=repo_path, 
                capture_output=True, 
                text=True
            )
            if result.stdout.strip():
                score.warnings.append("⚠️  Repository has uncommitted changes")
        except Exception:
            pass
    
    def _check_language_support(self, repo_path: Path, score: CompatibilityScore):
        """Check programming language support and detect primary language."""
        weight = self.config["scoring_weights"]["language_support"]
        detected_languages = {}
        
        # Count files by language
        for lang, config in self.supported_languages.items():
            file_count = 0
            for ext in config["extensions"]:
                file_count += len(list(repo_path.rglob(f"*{ext}")))
            
            if file_count > 0:
                detected_languages[lang] = {
                    "file_count": file_count,
                    "weight": config["weight"]
                }
        
        if not detected_languages:
            score.critical_issues.append("No supported programming languages detected")
            return
            
        # Calculate score based on detected languages
        primary_lang = max(detected_languages.items(), key=lambda x: x[1]["file_count"])
        lang_score = int(weight * primary_lang[1]["weight"])
        
        score.category_scores["language_support"] = lang_score
        score.total_score += lang_score
        score.recommendations.append(f"✅ Primary language: {primary_lang[0]} ({primary_lang[1]['file_count']} files)")
        
        # Check for language-specific configuration files
        for lang in detected_languages:
            config_files = self.supported_languages[lang]["config_files"]
            for config_file in config_files:
                if list(repo_path.glob(config_file)):
                    score.recommendations.append(f"✅ Found {lang} configuration: {config_file}")
                    break
            else:
                score.warnings.append(f"⚠️  Missing {lang} configuration files")
    
    def _check_ci_cd_systems(self, repo_path: Path, score: CompatibilityScore):
        """Check for existing CI/CD systems and configurations."""
        weight = self.config["scoring_weights"]["ci_cd"]
        ci_systems = []
        
        ci_patterns = {
            "github_actions": ".github/workflows/",
            "gitlab_ci": ".gitlab-ci.yml",
            "jenkins": "Jenkinsfile",
            "circleci": ".circleci/config.yml",
            "travis": ".travis.yml",
            "azure_pipelines": "azure-pipelines.yml"
        }
        
        for system, pattern in ci_patterns.items():
            if (repo_path / pattern).exists():
                ci_systems.append(system)
                
        if ci_systems:
            score.category_scores["ci_cd"] = weight
            score.total_score += weight
            score.recommendations.append(f"✅ CI/CD systems found: {', '.join(ci_systems)}")
        else:
            score.warnings.append("⚠️  No CI/CD systems detected")
            
        # Check for workflow quality if GitHub Actions exists
        if "github_actions" in ci_systems:
            workflows_dir = repo_path / ".github" / "workflows"
            workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
            if len(workflow_files) > 0:
                score.recommendations.append(f"✅ {len(workflow_files)} GitHub Actions workflows found")
            else:
                score.warnings.append("⚠️  GitHub Actions directory exists but no workflows found")
    
    def _check_testing_infrastructure(self, repo_path: Path, score: CompatibilityScore):
        """Check for testing frameworks and test coverage."""
        weight = self.config["scoring_weights"]["testing"]
        testing_score = 0
        
        # Look for test directories
        test_dirs = ["tests/", "test/", "__tests__/", "spec/"]
        found_test_dirs = [d for d in test_dirs if (repo_path / d).exists()]
        
        if found_test_dirs:
            testing_score += weight // 2
            score.recommendations.append(f"✅ Test directories found: {', '.join(found_test_dirs)}")
        else:
            score.warnings.append("⚠️  No test directories found")
            
        # Look for test configuration files
        test_configs = {
            "pytest": ["pytest.ini", "pyproject.toml", "setup.cfg"],
            "jest": ["jest.config.js", "jest.config.json"],
            "mocha": [".mocharc.json", "mocha.opts"],
            "junit": ["pom.xml"],
            "go_test": ["go.mod"],
            "cargo_test": ["Cargo.toml"]
        }
        
        for framework, config_files in test_configs.items():
            for config_file in config_files:
                if (repo_path / config_file).exists():
                    testing_score += weight // 4
                    score.recommendations.append(f"✅ {framework} configuration found")
                    break
                    
        score.category_scores["testing"] = min(testing_score, weight)
        score.total_score += score.category_scores["testing"]
    
    def _check_documentation(self, repo_path: Path, score: CompatibilityScore):
        """Check for documentation files and quality."""
        weight = self.config["scoring_weights"]["documentation"]
        doc_score = 0
        
        # Check for README file
        readme_patterns = ["README.md", "README.rst", "README.txt", "readme.md"]
        for pattern in readme_patterns:
            if (repo_path / pattern).exists():
                doc_score += weight // 2
                score.recommendations.append(f"✅ README file found: {pattern}")
                break
        else:
            score.warnings.append("⚠️  No README file found")
            
        # Check for additional documentation
        doc_patterns = {
            "CONTRIBUTING": ["CONTRIBUTING.md", "CONTRIBUTING.rst"],
            "LICENSE": ["LICENSE", "LICENSE.md", "LICENSE.txt"],
            "CHANGELOG": ["CHANGELOG.md", "CHANGELOG.rst", "HISTORY.md"],
            "docs directory": ["docs/", "documentation/"]
        }
        
        for doc_type, patterns in doc_patterns.items():
            for pattern in patterns:
                if (repo_path / pattern).exists():
                    doc_score += weight // 8
                    score.recommendations.append(f"✅ {doc_type} found")
                    break
                    
        score.category_scores["documentation"] = min(doc_score, weight)
        score.total_score += score.category_scores["documentation"]
    
    def _check_dependencies(self, repo_path: Path, score: CompatibilityScore):
        """Check dependency management and security."""
        weight = self.config["scoring_weights"]["dependencies"]
        dep_score = 0
        
        dependency_files = [
            "requirements.txt", "package.json", "Pipfile", "poetry.lock",
            "go.mod", "Cargo.toml", "pom.xml", "build.gradle"
        ]
        
        found_deps = []
        for dep_file in dependency_files:
            if (repo_path / dep_file).exists():
                found_deps.append(dep_file)
                dep_score += weight // 3
                
        if found_deps:
            score.recommendations.append(f"✅ Dependency files found: {', '.join(found_deps)}")
        else:
            score.warnings.append("⚠️  No dependency management files found")
            
        # Check for security scanning
        security_files = [".github/dependabot.yml", ".snyk"]
        for sec_file in security_files:
            if (repo_path / sec_file).exists():
                dep_score += weight // 4
                score.recommendations.append(f"✅ Security scanning configured: {sec_file}")
                
        score.category_scores["dependencies"] = min(dep_score, weight)
        score.total_score += score.category_scores["dependencies"]
    
    def _check_repository_structure(self, repo_path: Path, score: CompatibilityScore):
        """Check repository structure and organization."""
        weight = self.config["scoring_weights"]["structure"]
        struct_score = 0
        
        # Check for common directories
        expected_dirs = {
            "src/": "Source code directory",
            "lib/": "Library directory", 
            "scripts/": "Scripts directory",
            "config/": "Configuration directory",
            "examples/": "Examples directory"
        }
        
        for dir_name, description in expected_dirs.items():
            if (repo_path / dir_name).exists():
                struct_score += weight // 10
                score.recommendations.append(f"✅ {description} found")
                
        # Check for configuration files
        config_files = [".gitignore", ".editorconfig", "Makefile"]
        for config_file in config_files:
            if (repo_path / config_file).exists():
                struct_score += weight // 10
                score.recommendations.append(f"✅ {config_file} found")
                
        score.category_scores["structure"] = min(struct_score, weight)
        score.total_score += score.category_scores["structure"]
    
    def _check_security_setup(self, repo_path: Path, score: CompatibilityScore):
        """Check security configurations and best practices."""
        weight = self.config["scoring_weights"]["security"]
        sec_score = 0
        
        # Check for security-related files
        security_files = {
            "SECURITY.md": "Security policy",
            ".github/CODEOWNERS": "Code owners file",
            ".github/SECURITY.md": "Security documentation"
        }
        
        for sec_file, description in security_files.items():
            if (repo_path / sec_file).exists():
                sec_score += weight // 3
                score.recommendations.append(f"✅ {description} found")
                
        score.category_scores["security"] = min(sec_score, weight)
        score.total_score += score.category_scores["security"]
    
    def _check_remote_repository(self, remote_url: str, score: CompatibilityScore):
        """Check remote repository features and settings."""
        # This would require GitHub API access for full implementation
        # For now, just validate URL format
        if remote_url.startswith(("https://github.com", "git@github.com")):
            score.recommendations.append("✅ GitHub repository detected")
        elif remote_url.startswith(("https://gitlab.com", "git@gitlab.com")):
            score.recommendations.append("✅ GitLab repository detected")
        else:
            score.warnings.append("⚠️  Unknown repository hosting service")
    
    def _generate_recommendations(self, score: CompatibilityScore):
        """Generate final recommendations based on compatibility score."""
        if score.compatibility_level == "excellent":
            score.recommendations.append("🎉 Repository is excellent for EpochCore RAS propagation")
        elif score.compatibility_level == "good":
            score.recommendations.append("✅ Repository is well-suited for EpochCore RAS propagation")
        elif score.compatibility_level == "fair":
            score.recommendations.append("⚠️  Repository needs some improvements before propagation")
        elif score.compatibility_level == "poor":
            score.recommendations.append("⛔ Repository requires significant improvements before propagation")
        else:
            score.recommendations.append("❌ Repository is not compatible with EpochCore RAS propagation")
            
        # Add specific recommendations based on missing features
        if not score.critical_issues:
            if score.category_scores.get("testing", 0) < 10:
                score.recommendations.append("💡 Consider adding automated tests")
            if score.category_scores.get("ci_cd", 0) < 10:
                score.recommendations.append("💡 Consider setting up CI/CD pipeline")
            if score.category_scores.get("documentation", 0) < 5:
                score.recommendations.append("💡 Consider improving documentation")


def main():
    """CLI interface for repository compatibility checking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check repository compatibility with EpochCore RAS")
    parser.add_argument("repo_path", help="Path to repository to check")
    parser.add_argument("--remote-url", help="Remote repository URL for additional checks")
    parser.add_argument("--config", help="Path to custom configuration file")
    parser.add_argument("--output", choices=["json", "yaml", "text"], default="text", 
                       help="Output format")
    
    args = parser.parse_args()
    
    checker = RepositoryCompatibilityChecker(args.config)
    score = checker.check_repository(args.repo_path, args.remote_url)
    
    if args.output == "json":
        print(json.dumps(asdict(score), indent=2))
    elif args.output == "yaml":
        print(yaml.dump(asdict(score), default_flow_style=False))
    else:
        # Text output
        print(f"Repository Compatibility Analysis")
        print(f"================================")
        print(f"Repository: {args.repo_path}")
        print(f"Compatibility Score: {score.total_score}/{score.max_score} ({score.percentage:.1f}%)")
        print(f"Compatibility Level: {score.compatibility_level.upper()}")
        print()
        
        if score.critical_issues:
            print("Critical Issues:")
            for issue in score.critical_issues:
                print(f"  ❌ {issue}")
            print()
            
        if score.category_scores:
            print("Category Scores:")
            for category, cat_score in score.category_scores.items():
                print(f"  {category}: {cat_score}")
            print()
            
        if score.warnings:
            print("Warnings:")
            for warning in score.warnings:
                print(f"  {warning}")
            print()
            
        if score.recommendations:
            print("Recommendations:")
            for rec in score.recommendations:
                print(f"  {rec}")


if __name__ == "__main__":
    main()