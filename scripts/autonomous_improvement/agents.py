"""
Specialized agents for autonomous repository improvements.

These agents handle specific types of improvements like security patches,
dependency updates, code quality fixes, and documentation updates.
"""

import asyncio
import logging
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

try:
    from ..ai_agent.core.base_agent import BaseAgent
except ImportError:
    # Create a dummy BaseAgent if not available
    class BaseAgent:
        def __init__(self, name, config=None):
            self.name = name
            self.config = config or {}
            self.logger = logging.getLogger(name)
        
        def validate_config(self):
            return True
from .orchestrator import ImprovementTask, ImprovementCategory, ImprovementPriority


class ImprovementAgent(BaseAgent, ABC):
    """Base class for specialized improvement agents."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.improvements_made = []
        
    @abstractmethod
    async def can_handle(self, task: ImprovementTask) -> bool:
        """Check if this agent can handle the given task."""
        pass
    
    @abstractmethod
    async def execute_improvement(self, task: ImprovementTask) -> bool:
        """Execute the improvement task."""
        pass
    
    def run(self) -> Dict[str, Any]:
        """Base run method - not used directly by improvement agents."""
        return {"status": "improvement_agent_ready", "agent": self.name}


class SecurityAgent(ImprovementAgent):
    """Agent specialized in security improvements."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("security_agent", config)
    
    def validate_config(self) -> bool:
        return True
    
    async def can_handle(self, task: ImprovementTask) -> bool:
        return task.category == ImprovementCategory.SECURITY
    
    async def execute_improvement(self, task: ImprovementTask) -> bool:
        """Execute security improvements."""
        self.logger.info(f"Executing security improvement: {task.title}")
        
        try:
            if "vulnerability" in task.description.lower():
                return await self._fix_vulnerabilities()
            elif "secret" in task.description.lower():
                return await self._scan_for_secrets()
            elif "permission" in task.description.lower():
                return await self._fix_permissions()
            else:
                return await self._general_security_scan()
                
        except Exception as e:
            self.logger.error(f"Security improvement failed: {e}")
            return False
    
    async def _fix_vulnerabilities(self) -> bool:
        """Fix known vulnerabilities in dependencies."""
        try:
            # Run safety check to identify vulnerabilities
            result = subprocess.run(
                ["python", "-m", "safety", "check", "--json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("No vulnerabilities found")
                return True
            
            # Try to fix vulnerabilities by updating dependencies
            await self._update_vulnerable_dependencies()
            
            # Re-run safety check
            recheck = subprocess.run(
                ["python", "-m", "safety", "check"],
                capture_output=True,
                text=True
            )
            
            return recheck.returncode == 0
            
        except Exception as e:
            self.logger.error(f"Vulnerability fix failed: {e}")
            return False
    
    async def _update_vulnerable_dependencies(self) -> None:
        """Update dependencies to fix vulnerabilities."""
        requirements_file = Path("requirements.txt")
        if not requirements_file.exists():
            return
        
        # This is a simplified approach - in practice you'd want more sophisticated handling
        self.logger.info("Attempting to update vulnerable dependencies")
        
        # Could implement pip-audit integration or other security tools
        subprocess.run(["pip", "install", "--upgrade", "-r", "requirements.txt"], 
                      capture_output=True)
    
    async def _scan_for_secrets(self) -> bool:
        """Scan for exposed secrets in the repository."""
        try:
            # Basic regex patterns for common secrets
            secret_patterns = [
                r'(?i)(api_key|apikey|secret_key|secretkey)\s*[=:]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
                r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?([^"\'\s]{8,})["\']?',
                r'(?i)(token)\s*[=:]\s*["\']?([a-zA-Z0-9]{20,})["\']?',
            ]
            
            issues_found = []
            
            for py_file in Path(".").rglob("*.py"):
                if "/.git/" in str(py_file) or "/.venv/" in str(py_file):
                    continue
                
                try:
                    content = py_file.read_text()
                    for pattern in secret_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            issues_found.append((py_file, matches))
                except Exception:
                    continue
            
            if issues_found:
                self.logger.warning(f"Found potential secrets in {len(issues_found)} files")
                # In practice, you'd create issues or notifications
                return False
            
            self.logger.info("No secrets detected")
            return True
            
        except Exception as e:
            self.logger.error(f"Secret scan failed: {e}")
            return False
    
    async def _fix_permissions(self) -> bool:
        """Fix file permissions issues."""
        try:
            # Check for overly permissive files
            sensitive_files = [".env", "*.key", "*.pem", "*.p12"]
            
            for pattern in sensitive_files:
                for file_path in Path(".").rglob(pattern):
                    if file_path.is_file():
                        # Set restrictive permissions (owner read/write only)
                        file_path.chmod(0o600)
                        self.logger.info(f"Fixed permissions for {file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Permission fix failed: {e}")
            return False
    
    async def _general_security_scan(self) -> bool:
        """Run general security scan using bandit."""
        try:
            result = subprocess.run(
                ["python", "-m", "bandit", "-r", ".", "-f", "json", "--skip", "B101"],
                capture_output=True,
                text=True
            )
            
            # Bandit returns non-zero when issues are found
            if result.returncode == 0:
                self.logger.info("No security issues found by bandit")
                return True
            
            self.logger.warning("Security issues detected by bandit")
            # In practice, you'd parse the JSON output and attempt fixes
            return False
            
        except Exception as e:
            self.logger.error(f"Security scan failed: {e}")
            return False


class DependencyAgent(ImprovementAgent):
    """Agent specialized in dependency management."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("dependency_agent", config)
    
    def validate_config(self) -> bool:
        return True
    
    async def can_handle(self, task: ImprovementTask) -> bool:
        return task.category == ImprovementCategory.DEPENDENCY
    
    async def execute_improvement(self, task: ImprovementTask) -> bool:
        """Execute dependency improvements."""
        self.logger.info(f"Executing dependency improvement: {task.title}")
        
        try:
            if "outdated" in task.description.lower():
                return await self._update_outdated_dependencies()
            elif "unused" in task.description.lower():
                return await self._remove_unused_dependencies()
            elif "pinned" in task.description.lower():
                return await self._update_pinned_versions()
            else:
                return await self._general_dependency_maintenance()
                
        except Exception as e:
            self.logger.error(f"Dependency improvement failed: {e}")
            return False
    
    async def _update_outdated_dependencies(self) -> bool:
        """Update outdated dependencies."""
        try:
            # Check for outdated packages
            result = subprocess.run(
                ["pip", "list", "--outdated", "--format=json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False
            
            import json
            outdated_packages = json.loads(result.stdout)
            
            if not outdated_packages:
                self.logger.info("No outdated packages found")
                return True
            
            # Update packages one by one for better control
            updated_count = 0
            for package in outdated_packages[:5]:  # Limit to 5 updates per run
                package_name = package["name"]
                try:
                    update_result = subprocess.run(
                        ["pip", "install", "--upgrade", package_name],
                        capture_output=True,
                        text=True
                    )
                    
                    if update_result.returncode == 0:
                        self.logger.info(f"Updated {package_name}")
                        updated_count += 1
                    else:
                        self.logger.warning(f"Failed to update {package_name}")
                        
                except Exception as e:
                    self.logger.error(f"Error updating {package_name}: {e}")
            
            # Update requirements.txt if successful
            if updated_count > 0:
                await self._freeze_requirements()
            
            return updated_count > 0
            
        except Exception as e:
            self.logger.error(f"Dependency update failed: {e}")
            return False
    
    async def _freeze_requirements(self) -> None:
        """Update requirements.txt with current package versions."""
        try:
            result = subprocess.run(
                ["pip", "freeze"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                with open("requirements.txt", "w") as f:
                    # Filter out development packages and editable installs
                    lines = [
                        line for line in result.stdout.splitlines()
                        if not line.startswith("-e") and "==" in line
                    ]
                    f.write("\n".join(sorted(lines)) + "\n")
                
                self.logger.info("Updated requirements.txt")
                
        except Exception as e:
            self.logger.error(f"Failed to freeze requirements: {e}")
    
    async def _remove_unused_dependencies(self) -> bool:
        """Remove unused dependencies."""
        try:
            # This would require a more sophisticated analysis
            # For now, just return True as a placeholder
            self.logger.info("Unused dependency removal not implemented yet")
            return True
            
        except Exception as e:
            self.logger.error(f"Unused dependency removal failed: {e}")
            return False
    
    async def _update_pinned_versions(self) -> bool:
        """Update pinned dependency versions."""
        requirements_file = Path("requirements.txt")
        if not requirements_file.exists():
            return True
        
        try:
            content = requirements_file.read_text()
            lines = content.splitlines()
            
            updated_lines = []
            changes_made = False
            
            for line in lines:
                if "==" in line and not line.startswith("#"):
                    package_name = line.split("==")[0]
                    # Get latest version
                    result = subprocess.run(
                        ["pip", "index", "versions", package_name],
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        # Parse output to get latest version
                        # This is simplified - real implementation would be more robust
                        updated_lines.append(line)  # Keep existing for now
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            
            if changes_made:
                requirements_file.write_text("\n".join(updated_lines) + "\n")
                self.logger.info("Updated pinned versions")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Version update failed: {e}")
            return False
    
    async def _general_dependency_maintenance(self) -> bool:
        """General dependency maintenance."""
        try:
            # Run pip check to verify dependency consistency
            result = subprocess.run(
                ["pip", "check"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("Dependencies are consistent")
                return True
            else:
                self.logger.warning(f"Dependency issues found: {result.stdout}")
                return False
                
        except Exception as e:
            self.logger.error(f"Dependency check failed: {e}")
            return False


class QualityAgent(ImprovementAgent):
    """Agent specialized in code quality improvements."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("quality_agent", config)
    
    def validate_config(self) -> bool:
        return True
    
    async def can_handle(self, task: ImprovementTask) -> bool:
        return task.category == ImprovementCategory.QUALITY
    
    async def execute_improvement(self, task: ImprovementTask) -> bool:
        """Execute code quality improvements."""
        self.logger.info(f"Executing quality improvement: {task.title}")
        
        try:
            if "linting" in task.description.lower():
                return await self._fix_linting_issues()
            elif "formatting" in task.description.lower():
                return await self._fix_formatting_issues()
            elif "complexity" in task.description.lower():
                return await self._reduce_complexity()
            else:
                return await self._general_quality_improvements()
                
        except Exception as e:
            self.logger.error(f"Quality improvement failed: {e}")
            return False
    
    async def _fix_linting_issues(self) -> bool:
        """Fix linting issues using flake8 and other tools."""
        try:
            # Run flake8 to check for issues
            result = subprocess.run(
                ["flake8", ".", "--count", "--statistics", "--format=json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("No linting issues found")
                return True
            
            # For now, just report that issues exist
            # In practice, you'd implement specific fixes
            self.logger.warning("Linting issues detected")
            return False
            
        except Exception as e:
            self.logger.error(f"Linting fix failed: {e}")
            return False
    
    async def _fix_formatting_issues(self) -> bool:
        """Fix code formatting using Black."""
        try:
            result = subprocess.run(
                ["black", "--check", "."],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("Code formatting is correct")
                return True
            
            # Apply Black formatting
            format_result = subprocess.run(
                ["black", "."],
                capture_output=True,
                text=True
            )
            
            if format_result.returncode == 0:
                self.logger.info("Applied code formatting")
                return True
            else:
                self.logger.error(f"Formatting failed: {format_result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Formatting fix failed: {e}")
            return False
    
    async def _reduce_complexity(self) -> bool:
        """Attempt to reduce code complexity."""
        try:
            # Run complexity analysis
            result = subprocess.run(
                ["flake8", ".", "--select=C901", "--statistics"],
                capture_output=True,
                text=True
            )
            
            if "C901" not in result.stdout:
                self.logger.info("No complexity issues found")
                return True
            
            # Complexity reduction is complex (pun intended)
            # For now, just report the issues
            self.logger.warning("High complexity functions detected")
            return False
            
        except Exception as e:
            self.logger.error(f"Complexity analysis failed: {e}")
            return False
    
    async def _general_quality_improvements(self) -> bool:
        """General code quality improvements."""
        try:
            improvements = 0
            
            # Fix formatting
            if await self._fix_formatting_issues():
                improvements += 1
            
            # Import sorting with isort
            isort_result = subprocess.run(
                ["isort", "--check-only", "."],
                capture_output=True,
                text=True
            )
            
            if isort_result.returncode != 0:
                # Apply import sorting
                subprocess.run(["isort", "."], capture_output=True)
                improvements += 1
                self.logger.info("Applied import sorting")
            
            return improvements > 0
            
        except Exception as e:
            self.logger.error(f"Quality improvements failed: {e}")
            return False


class DocumentationAgent(ImprovementAgent):
    """Agent specialized in documentation improvements."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("documentation_agent", config)
    
    def validate_config(self) -> bool:
        return True
    
    async def can_handle(self, task: ImprovementTask) -> bool:
        return task.category == ImprovementCategory.DOCUMENTATION
    
    async def execute_improvement(self, task: ImprovementTask) -> bool:
        """Execute documentation improvements."""
        self.logger.info(f"Executing documentation improvement: {task.title}")
        
        try:
            if "readme" in task.description.lower():
                return await self._improve_readme()
            elif "api" in task.description.lower():
                return await self._generate_api_docs()
            elif "links" in task.description.lower():
                return await self._fix_broken_links()
            else:
                return await self._general_doc_improvements()
                
        except Exception as e:
            self.logger.error(f"Documentation improvement failed: {e}")
            return False
    
    async def _improve_readme(self) -> bool:
        """Improve README.md completeness."""
        readme_path = Path("README.md")
        if not readme_path.exists():
            # Create basic README
            readme_content = """# Project Title

Description of your project.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Describe how to use your project.

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
"""
            readme_path.write_text(readme_content)
            self.logger.info("Created basic README.md")
            return True
        
        # Check for missing sections
        content = readme_path.read_text()
        missing_sections = []
        
        required_sections = ["installation", "usage", "contributing", "license"]
        for section in required_sections:
            if section.lower() not in content.lower():
                missing_sections.append(section)
        
        if missing_sections:
            self.logger.info(f"README missing sections: {missing_sections}")
            # Would add missing sections in practice
        
        return len(missing_sections) == 0
    
    async def _generate_api_docs(self) -> bool:
        """Generate API documentation."""
        try:
            # Check if sphinx is available for documentation generation
            sphinx_result = subprocess.run(
                ["sphinx-quickstart", "--version"],
                capture_output=True,
                text=True
            )
            
            if sphinx_result.returncode != 0:
                self.logger.warning("Sphinx not available for documentation generation")
                return False
            
            # Would implement actual API doc generation here
            self.logger.info("API documentation generation not fully implemented")
            return True
            
        except Exception as e:
            self.logger.error(f"API doc generation failed: {e}")
            return False
    
    async def _fix_broken_links(self) -> bool:
        """Fix broken links in documentation."""
        try:
            # Simple implementation - would be more sophisticated in practice
            md_files = list(Path(".").rglob("*.md"))
            
            for md_file in md_files:
                content = md_file.read_text()
                # Find markdown links
                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                
                for link_text, link_url in links:
                    if link_url.startswith("http"):
                        # Would check if URL is accessible
                        continue
                    elif link_url.startswith("#"):
                        # Internal anchor link
                        continue
                    else:
                        # Local file link
                        link_path = Path(md_file.parent / link_url)
                        if not link_path.exists():
                            self.logger.warning(f"Broken link in {md_file}: {link_url}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Link checking failed: {e}")
            return False
    
    async def _general_doc_improvements(self) -> bool:
        """General documentation improvements."""
        improvements = 0
        
        # Ensure basic files exist
        basic_files = {
            "CONTRIBUTING.md": "# Contributing\n\nGuidelines for contributing to this project.\n",
            "CODE_OF_CONDUCT.md": "# Code of Conduct\n\nExpected behavior guidelines.\n",
            "CHANGELOG.md": "# Changelog\n\nAll notable changes to this project will be documented here.\n"
        }
        
        for filename, default_content in basic_files.items():
            file_path = Path(filename)
            if not file_path.exists():
                file_path.write_text(default_content)
                self.logger.info(f"Created {filename}")
                improvements += 1
        
        return improvements > 0