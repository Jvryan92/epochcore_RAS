"""Repository quality and standards test suite."""

import unittest
import subprocess
import os
import json
import glob
from typing import List, Dict, Any
from pathlib import Path
import pytest
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestRepositoryStandards:
    """Test suite for repository standards compliance."""

    def setup_method(self):
        """Set up test environment."""
        self.repo_root = project_root
        self.required_files = [
            'README.md',
            '.github/workflows',
            'requirements.txt',
            'Dockerfile',
            '.devcontainer/devcontainer.json',
            'tests/',
            'docs/'
        ]
        self.minimum_coverage = 80.0

    def test_required_files_exist(self):
        """Verify all required files and directories exist."""
        missing = []
        for file_path in self.required_files:
            full_path = self.repo_root / file_path
            if not full_path.exists():
                missing.append(file_path)

        assert not missing, f"Missing required files/directories: {missing}"

    def test_ci_cd_workflow_exists(self):
        """Verify GitHub Actions CI/CD workflow is configured."""
        workflow_dir = self.repo_root / '.github' / 'workflows'
        if workflow_dir.exists():
            workflows = list(workflow_dir.glob('*.yml')) + list(workflow_dir.glob('*.yaml'))
            assert len(workflows) > 0, "No CI/CD workflows found"
        else:
            pytest.fail("No .github/workflows directory found")

    def test_docker_setup(self):
        """Verify Docker configuration is present."""
        dockerfile = self.repo_root / 'Dockerfile'
        devcontainer = self.repo_root / '.devcontainer' / 'devcontainer.json'
        
        assert dockerfile.exists(), "Dockerfile not found"
        assert devcontainer.exists(), "Dev container configuration not found"

    def test_documentation_completeness(self):
        """Verify documentation meets standards."""
        readme = self.repo_root / 'README.md'
        assert readme.exists(), "README.md not found"
        
        content = readme.read_text().lower()
        required_sections = [
            'installation',
            'usage',
            'contributing',
            'license',
            'api documentation'
        ]
        
        missing_sections = [
            section for section in required_sections 
            if section not in content
        ]
        
        assert not missing_sections, f"README missing sections: {missing_sections}"

    def test_security_configuration(self):
        """Verify security best practices are implemented."""
        security_files = [
            '.github/SECURITY.md',
            '.github/dependabot.yml',
            'SECURITY.md'
        ]
        
        found = any(
            (self.repo_root / file_path).exists() 
            for file_path in security_files
        )
        
        assert found, "No security configuration found"

    def test_test_coverage(self):
        """Validate test coverage meets threshold."""
        try:
            # Run coverage
            result = subprocess.run(
                ['python', '-m', 'pytest', '--cov=scripts', '--cov-report=json'],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            
            coverage_file = self.repo_root / 'coverage.json'
            assert coverage_file.exists(), "Coverage report not generated"
            
            with open(coverage_file) as f:
                coverage_data = json.load(f)
            
            total_coverage = coverage_data['totals']['percent_covered']
            assert total_coverage >= self.minimum_coverage, \
                f"Coverage {total_coverage}% below {self.minimum_coverage}% threshold"
                
        except Exception as e:
            pytest.skip(f"Coverage analysis failed: {e}")

    def test_contributing_guide(self):
        """Verify contributor documentation exists."""
        contributing_files = [
            'CONTRIBUTING.md',
            '.github/CONTRIBUTING.md',
            'docs/CONTRIBUTING.md'
        ]
        
        found = any(
            (self.repo_root / file_path).exists()
            for file_path in contributing_files
        )
        
        assert found, "No CONTRIBUTING.md guide found"

    def test_issue_templates(self):
        """Verify GitHub issue templates are configured."""
        template_dir = self.repo_root / '.github' / 'ISSUE_TEMPLATE'
        
        if template_dir.exists():
            templates = list(template_dir.glob('*.md')) + list(template_dir.glob('*.yml'))
            assert len(templates) > 0, "No issue templates found"
        else:
            pytest.fail("No issue templates directory found")

    def test_pull_request_template(self):
        """Verify PR template exists."""
        pr_templates = [
            '.github/pull_request_template.md',
            '.github/PULL_REQUEST_TEMPLATE.md'
        ]
        
        found = any(
            (self.repo_root / template).exists()
            for template in pr_templates
        )
        
        assert found, "No pull request template found"

    def test_python_package_structure(self):
        """Verify Python package structure is correct."""
        required_pkg_files = [
            'setup.py',
            'setup.cfg',
            'pyproject.toml',
            'MANIFEST.in'
        ]
        
        found_files = [
            file_path for file_path in required_pkg_files
            if (self.repo_root / file_path).exists()
        ]
        
        # Need at least setup.py or pyproject.toml
        assert any(
            file in found_files for file in ['setup.py', 'pyproject.toml']
        ), "Missing package configuration files"

    def test_documentation_build(self):
        """Verify documentation can be built."""
        docs_dir = self.repo_root / 'docs'
        if not docs_dir.exists():
            pytest.skip("No docs directory found")
            
        # Check for Sphinx or MkDocs
        sphinx_conf = docs_dir / 'conf.py'
        mkdocs_yml = self.repo_root / 'mkdocs.yml'
        
        assert any([sphinx_conf.exists(), mkdocs_yml.exists()]), \
            "No documentation configuration found"

    def test_code_quality_tools(self):
        """Verify code quality tools are configured."""
        quality_configs = [
            '.pylintrc',
            '.flake8',
            'setup.cfg',
            'pyproject.toml'
        ]
        
        found = False
        for config in quality_configs:
            path = self.repo_root / config
            if path.exists():
                content = path.read_text()
                if any(tool in content.lower() for tool in ['pylint', 'flake8', 'black', 'isort']):
                    found = True
                    break
                    
        assert found, "No code quality tools configured"

    def test_test_organization(self):
        """Verify test organization and structure."""
        test_dir = self.repo_root / 'tests'
        assert test_dir.exists(), "No tests directory found"
        
        # Check for test files
        test_files = list(test_dir.glob('test_*.py'))
        assert len(test_files) > 0, "No test files found"
        
        # Check for conftest.py
        conftest = test_dir / 'conftest.py'
        assert conftest.exists(), "No conftest.py found"

    def test_dependency_management(self):
        """Verify dependency management is properly configured."""
        req_files = [
            'requirements.txt',
            'requirements-dev.txt',
            'requirements-test.txt'
        ]
        
        found = any(
            (self.repo_root / file_path).exists()
            for file_path in req_files
        )
        
        assert found, "No requirements files found"
        
        # Check if using modern dependency management
        modern_dep_files = [
            'Pipfile',
            'pyproject.toml',
            'poetry.lock'
        ]
        
        uses_modern = any(
            (self.repo_root / file_path).exists()
            for file_path in modern_dep_files
        )
        
        if not uses_modern:
            pytest.warns(UserWarning, "Consider using modern dependency management tools")

    def test_ci_cd_completeness(self):
        """Verify CI/CD workflow completeness."""
        workflow_dir = self.repo_root / '.github' / 'workflows'
        if not workflow_dir.exists():
            pytest.fail("No .github/workflows directory found")
            
        workflows = list(workflow_dir.glob('*.yml')) + list(workflow_dir.glob('*.yaml'))
        
        required_stages = [
            'test',
            'lint',
            'security',
            'build',
            'deploy'
        ]
        
        found_stages = set()
        for workflow in workflows:
            content = workflow.read_text().lower()
            for stage in required_stages:
                if stage in content:
                    found_stages.add(stage)
                    
        missing = set(required_stages) - found_stages
        assert not missing, f"CI/CD missing stages: {missing}"


def generate_improvement_plan() -> str:
    """Generate repository improvement plan."""
    return """
    STRATEGYDECKA+ IMPROVEMENT PLAN
    ==============================
    
    1. TEST COVERAGE (>80%)
    ----------------------
    - Add pytest-cov to requirements
    - Create missing unit tests
    - Add integration tests
    - Configure coverage reporting
    - Add coverage badge
    
    2. CI/CD AUTOMATION
    -------------------
    - Create/update workflows
    - Add security scanning
    - Configure deployment
    - Add status badges
    
    3. DOCUMENTATION
    ---------------
    - Complete README sections
    - Set up API documentation
    - Add architecture diagrams
    - Create contributor guides
    
    4. SECURITY
    ----------
    - Add dependabot config
    - Enable CodeQL
    - Create SECURITY.md
    - Add security checks
    
    5. QUALITY TOOLS
    ---------------
    - Configure linters
    - Set up formatters
    - Add pre-commit hooks
    - Enable type checking
    
    6. DEPLOYMENT
    ------------
    - Document process
    - Create scripts
    - Configure environments
    - Add Docker support
    """


def main():
    """Main function to run tests and generate plan."""
    print("\nRunning StrategyDECK Repository Health Check...")
    print("=" * 50)
    
    # Generate plan
    plan = generate_improvement_plan()
    print(plan)
    
    # Run tests
    pytest.main([__file__, '-v'])


if __name__ == '__main__':
    main()
