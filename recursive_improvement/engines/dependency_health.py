"""
Dependency Health Engine - Recursive Autonomy Module
Recursive dependency health check for outdated, vulnerable, or deprecated dependencies, opening PRs as needed
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import json
import subprocess
import re
import logging
import os

from ..base import RecursiveEngine, CompoundingAction


class DependencyHealthEngine(RecursiveEngine):
    """
    Recursive dependency health checker with autonomous PR creation.
    Monitors dependencies for security vulnerabilities, updates, and deprecations.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("dependency_health", config)
        self.dependency_history = []
        self.vulnerability_database = {}
        self.update_policies = self._load_update_policies()
        self.health_metrics = {}
        
    def initialize(self) -> bool:
        """Initialize the dependency health engine."""
        try:
            self.logger.info("Initializing Dependency Health Engine")
            
            # Set up compounding actions
            health_check_action = CompoundingAction(
                name="dependency_health_check",
                action=self.execute_main_action,
                interval=1.0,  # Weekly comprehensive check
                pre_action=self.execute_pre_action,
                pre_interval=0.25,  # Quick vulnerability scan
                metadata={"type": "dependency_health", "recursive": True}
            )
            
            self.add_compounding_action(health_check_action)
            
            # Initialize health metrics tracking
            self.health_metrics = {
                "dependencies_tracked": 0,
                "vulnerabilities_found": 0,
                "updates_available": 0,
                "security_updates_applied": 0,
                "prs_created": 0,
                "deprecated_dependencies": 0,
                "health_score": 100.0
            }
            
            self.logger.info("Dependency Health Engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Dependency Health Engine: {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute comprehensive dependency health check and updates."""
        try:
            self.logger.info("Executing comprehensive dependency health check")
            
            # Scan all dependency files
            dependency_files = self._find_dependency_files()
            
            # Analyze each dependency file
            analysis_results = []
            for dep_file in dependency_files:
                analysis = self._analyze_dependency_file(dep_file)
                analysis_results.append(analysis)
            
            # Check for vulnerabilities
            vulnerability_results = self._check_vulnerabilities(analysis_results)
            
            # Check for available updates
            update_results = self._check_available_updates(analysis_results)
            
            # Check for deprecated dependencies
            deprecation_results = self._check_deprecated_dependencies(analysis_results)
            
            # Apply automatic security updates
            security_updates = self._apply_security_updates(vulnerability_results)
            
            # Create PRs for non-critical updates
            prs_created = self._create_update_prs(update_results, deprecation_results)
            
            # Update vulnerability database
            self._update_vulnerability_database(vulnerability_results)
            
            # Calculate health score
            health_score = self._calculate_health_score(vulnerability_results, update_results, deprecation_results)
            
            # Update metrics
            self._update_health_metrics(analysis_results, vulnerability_results, update_results, 
                                      security_updates, prs_created, health_score)
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "action": "comprehensive_dependency_health_check",
                "dependency_files": len(dependency_files),
                "total_dependencies": sum(len(r.get("dependencies", [])) for r in analysis_results),
                "vulnerabilities_found": len(vulnerability_results),
                "updates_available": len(update_results),
                "security_updates_applied": len(security_updates),
                "prs_created": len(prs_created),
                "health_score": health_score,
                "metrics": self.health_metrics
            }
            
            self.dependency_history.append(result)
            self.logger.info(f"Dependency health check completed: {result['total_dependencies']} deps, {result['vulnerabilities_found']} vulnerabilities")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in dependency health check: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "comprehensive_dependency_health_check",
                "error": str(e),
                "status": "failed"
            }
    
    def execute_pre_action(self) -> Dict[str, Any]:
        """Execute pre-action: quick vulnerability scan and critical update detection."""
        try:
            self.logger.info("Quick vulnerability scan and critical update detection")
            
            # Quick scan for critical vulnerabilities
            critical_vulns = self._quick_vulnerability_scan()
            
            # Check for critical security updates
            critical_updates = self._check_critical_updates()
            
            # Pre-prepare update PRs for critical issues
            pr_templates_prepared = self._prepare_critical_update_templates(critical_vulns, critical_updates)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "quick_vulnerability_scan",
                "critical_vulnerabilities": len(critical_vulns),
                "critical_updates": len(critical_updates),
                "pr_templates_prepared": pr_templates_prepared,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"Error in quick vulnerability scan: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "quick_vulnerability_scan",
                "error": str(e),
                "status": "failed"
            }
    
    def _load_update_policies(self) -> Dict[str, Any]:
        """Load dependency update policies."""
        return {
            "security_updates": {
                "auto_apply": True,
                "create_pr": True,
                "severity_threshold": "medium"
            },
            "major_updates": {
                "auto_apply": False,
                "create_pr": True,
                "require_review": True
            },
            "minor_updates": {
                "auto_apply": True,
                "create_pr": True,
                "batch_updates": True
            },
            "patch_updates": {
                "auto_apply": True,
                "create_pr": False,
                "immediate": True
            },
            "deprecated_dependencies": {
                "auto_apply": False,
                "create_pr": True,
                "suggest_alternatives": True
            }
        }
    
    def _find_dependency_files(self) -> List[str]:
        """Find all dependency files in the repository."""
        dependency_files = []
        
        # Common dependency file patterns
        patterns = [
            "requirements.txt",
            "requirements-*.txt", 
            "pyproject.toml",
            "setup.py",
            "Pipfile",
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "Gemfile",
            "Gemfile.lock",
            "composer.json",
            "composer.lock",
            "go.mod",
            "go.sum"
        ]
        
        for root, dirs, files in os.walk("."):
            # Skip virtual environment and cache directories
            dirs[:] = [d for d in dirs if d not in ['venv', 'node_modules', '.git', '__pycache__']]
            
            for file in files:
                for pattern in patterns:
                    if file == pattern or (pattern.endswith("*") and file.startswith(pattern[:-1])):
                        dependency_files.append(os.path.join(root, file))
                        
        return dependency_files
    
    def _analyze_dependency_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a specific dependency file."""
        try:
            analysis = {
                "file_path": file_path,
                "file_type": self._detect_file_type(file_path),
                "dependencies": [],
                "last_modified": os.path.getmtime(file_path),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            if file_path.endswith("requirements.txt"):
                analysis["dependencies"] = self._parse_requirements_txt(file_path)
            elif file_path.endswith("package.json"):
                analysis["dependencies"] = self._parse_package_json(file_path)
            elif file_path.endswith("pyproject.toml"):
                analysis["dependencies"] = self._parse_pyproject_toml(file_path)
            # Add more parsers as needed
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing dependency file {file_path}: {e}")
            return {
                "file_path": file_path,
                "error": str(e),
                "analysis_timestamp": datetime.now().isoformat()
            }
    
    def _detect_file_type(self, file_path: str) -> str:
        """Detect the type of dependency file."""
        if file_path.endswith((".txt", "requirements")):
            return "pip"
        elif file_path.endswith((".json", "package")):
            return "npm"
        elif file_path.endswith(".toml"):
            return "python_toml"
        elif file_path.endswith(("Gemfile", ".gemspec")):
            return "ruby"
        elif file_path.endswith(("go.mod", "go.sum")):
            return "go"
        else:
            return "unknown"
    
    def _parse_requirements_txt(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse requirements.txt file."""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        dep_info = self._parse_requirement_line(line)
                        if dep_info:
                            dep_info["line_number"] = line_num
                            dependencies.append(dep_info)
                            
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            
        return dependencies
    
    def _parse_requirement_line(self, line: str) -> Dict[str, Any]:
        """Parse a single requirement line."""
        # Handle various requirement formats: package>=1.0.0, package==1.0.0, etc.
        match = re.match(r'^([a-zA-Z0-9_-]+)([><=!~]+)?([\d\.]+.*)?', line)
        
        if match:
            package_name = match.group(1)
            operator = match.group(2) or "=="
            version = match.group(3) or "latest"
            
            return {
                "name": package_name,
                "current_version": version,
                "version_operator": operator,
                "raw_line": line
            }
            
        return None
    
    def _parse_package_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse package.json file."""
        dependencies = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Parse dependencies and devDependencies
            for section in ["dependencies", "devDependencies", "peerDependencies"]:
                if section in data:
                    for name, version in data[section].items():
                        dependencies.append({
                            "name": name,
                            "current_version": version,
                            "section": section,
                            "raw_line": f'"{name}": "{version}"'
                        })
                        
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            
        return dependencies
    
    def _parse_pyproject_toml(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse pyproject.toml file."""
        dependencies = []
        
        try:
            # Simple TOML parsing for dependencies
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for [tool.poetry.dependencies] or similar sections
            dep_sections = re.findall(r'\[.*dependencies\](.*?)(?=\[|$)', content, re.DOTALL)
            
            for section in dep_sections:
                for line in section.split('\n'):
                    if '=' in line and not line.strip().startswith('#'):
                        match = re.match(r'([a-zA-Z0-9_-]+)\s*=\s*"([^"]+)"', line.strip())
                        if match:
                            dependencies.append({
                                "name": match.group(1),
                                "current_version": match.group(2),
                                "raw_line": line.strip()
                            })
                            
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            
        return dependencies
    
    def _check_vulnerabilities(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check dependencies for known vulnerabilities."""
        vulnerabilities = []
        
        for analysis in analysis_results:
            for dep in analysis.get("dependencies", []):
                # Simulate vulnerability check - in real implementation would use security databases
                vuln_check = self._check_dependency_vulnerability(dep["name"], dep.get("current_version"))
                if vuln_check:
                    vulnerabilities.append({
                        "package": dep["name"],
                        "current_version": dep.get("current_version"),
                        "vulnerability": vuln_check,
                        "file": analysis["file_path"],
                        "severity": vuln_check.get("severity", "unknown")
                    })
                    
        return vulnerabilities
    
    def _check_dependency_vulnerability(self, package_name: str, version: str) -> Dict[str, Any]:
        """Check a specific dependency for vulnerabilities."""
        # Simulate vulnerability database lookup
        known_vulnerabilities = {
            "requests": {
                "versions": ["<2.20.0"],
                "cve": "CVE-2018-18074",
                "severity": "high",
                "description": "Server Side Request Forgery vulnerability"
            },
            "django": {
                "versions": ["<3.0.0"],
                "cve": "CVE-2019-14232",
                "severity": "medium", 
                "description": "Potential SQL injection vulnerability"
            }
        }
        
        if package_name in known_vulnerabilities:
            vuln_info = known_vulnerabilities[package_name]
            # Simplified version check
            if version and any(v in version for v in vuln_info["versions"]):
                return vuln_info
                
        return None
    
    def _check_available_updates(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for available updates for dependencies."""
        updates = []
        
        for analysis in analysis_results:
            for dep in analysis.get("dependencies", []):
                update_info = self._check_package_updates(dep["name"], dep.get("current_version"))
                if update_info:
                    updates.append({
                        "package": dep["name"],
                        "current_version": dep.get("current_version"),
                        "latest_version": update_info.get("latest_version"),
                        "update_type": update_info.get("update_type"),
                        "file": analysis["file_path"],
                        "changelog": update_info.get("changelog", "")
                    })
                    
        return updates
    
    def _check_package_updates(self, package_name: str, current_version: str) -> Dict[str, Any]:
        """Check for updates to a specific package."""
        # Simulate package registry lookup
        package_updates = {
            "pyyaml": {
                "current": "6.0.1",
                "latest": "6.0.2",
                "update_type": "patch"
            },
            "requests": {
                "current": "2.28.0",
                "latest": "2.31.0",
                "update_type": "minor"
            }
        }
        
        if package_name in package_updates:
            update_info = package_updates[package_name]
            if current_version != update_info["latest"]:
                return {
                    "latest_version": update_info["latest"],
                    "update_type": update_info["update_type"],
                    "changelog": f"Updated from {current_version} to {update_info['latest']}"
                }
                
        return None
    
    def _check_deprecated_dependencies(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for deprecated dependencies."""
        deprecated = []
        
        # List of known deprecated packages
        deprecated_packages = {
            "flask-login": {
                "reason": "Security vulnerabilities",
                "alternative": "flask-principal",
                "deprecation_date": "2024-01-01"
            }
        }
        
        for analysis in analysis_results:
            for dep in analysis.get("dependencies", []):
                if dep["name"] in deprecated_packages:
                    dep_info = deprecated_packages[dep["name"]]
                    deprecated.append({
                        "package": dep["name"],
                        "current_version": dep.get("current_version"),
                        "reason": dep_info["reason"],
                        "alternative": dep_info["alternative"],
                        "file": analysis["file_path"]
                    })
                    
        return deprecated
    
    def _apply_security_updates(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply critical security updates automatically."""
        applied_updates = []
        
        for vuln in vulnerabilities:
            if vuln["severity"] in ["critical", "high"] and self.update_policies["security_updates"]["auto_apply"]:
                try:
                    success = self._apply_dependency_update(vuln["package"], "latest", vuln["file"])
                    if success:
                        applied_updates.append({
                            "package": vuln["package"],
                            "file": vuln["file"],
                            "reason": "security_vulnerability",
                            "cve": vuln["vulnerability"].get("cve", ""),
                            "applied_at": datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    self.logger.error(f"Failed to apply security update for {vuln['package']}: {e}")
                    
        return applied_updates
    
    def _apply_dependency_update(self, package: str, version: str, file_path: str) -> bool:
        """Apply a dependency update to a file."""
        try:
            # Simulate dependency update - in real implementation would modify files
            self.logger.info(f"Updating {package} to {version} in {file_path}")
            
            # For requirements.txt, would update the line
            # For package.json, would update the JSON
            # etc.
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating dependency: {e}")
            return False
    
    def _create_update_prs(self, updates: List[Dict[str, Any]], deprecated: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create PRs for non-critical updates and deprecation replacements."""
        prs_created = []
        
        # Group updates by type for batch PRs
        minor_updates = [u for u in updates if u.get("update_type") == "minor"]
        major_updates = [u for u in updates if u.get("update_type") == "major"]
        
        # Create PR for minor updates (batch)
        if minor_updates and self.update_policies["minor_updates"]["create_pr"]:
            pr_info = self._create_batch_update_pr(minor_updates, "minor")
            if pr_info:
                prs_created.append(pr_info)
        
        # Create individual PRs for major updates
        if self.update_policies["major_updates"]["create_pr"]:
            for update in major_updates:
                pr_info = self._create_individual_update_pr(update, "major")
                if pr_info:
                    prs_created.append(pr_info)
        
        # Create PRs for deprecated dependency replacements
        if deprecated and self.update_policies["deprecated_dependencies"]["create_pr"]:
            for dep in deprecated:
                pr_info = self._create_deprecation_replacement_pr(dep)
                if pr_info:
                    prs_created.append(pr_info)
                    
        return prs_created
    
    def _create_batch_update_pr(self, updates: List[Dict[str, Any]], update_type: str) -> Dict[str, Any]:
        """Create a PR for batch updates."""
        try:
            # Simulate PR creation - in real implementation would use GitHub API
            pr_title = f"Batch {update_type} dependency updates"
            pr_body = f"Updates {len(updates)} dependencies:\n"
            
            for update in updates:
                pr_body += f"- {update['package']}: {update['current_version']} → {update['latest_version']}\n"
            
            self.logger.info(f"Creating batch update PR: {pr_title}")
            
            return {
                "type": "batch_update",
                "title": pr_title,
                "updates_count": len(updates),
                "packages": [u["package"] for u in updates],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create batch update PR: {e}")
            return None
    
    def _create_individual_update_pr(self, update: Dict[str, Any], update_type: str) -> Dict[str, Any]:
        """Create PR for individual major update."""
        try:
            pr_title = f"Update {update['package']} from {update['current_version']} to {update['latest_version']}"
            pr_body = f"Major update for {update['package']}\n\nChangelog:\n{update.get('changelog', 'No changelog available')}"
            
            self.logger.info(f"Creating individual update PR: {pr_title}")
            
            return {
                "type": "individual_update",
                "title": pr_title,
                "package": update["package"],
                "update_type": update_type,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create individual update PR: {e}")
            return None
    
    def _create_deprecation_replacement_pr(self, deprecated: Dict[str, Any]) -> Dict[str, Any]:
        """Create PR for deprecated dependency replacement."""
        try:
            pr_title = f"Replace deprecated dependency {deprecated['package']} with {deprecated['alternative']}"
            pr_body = f"Replacing deprecated package {deprecated['package']}\n\nReason: {deprecated['reason']}\nRecommended alternative: {deprecated['alternative']}"
            
            self.logger.info(f"Creating deprecation replacement PR: {pr_title}")
            
            return {
                "type": "deprecation_replacement",
                "title": pr_title,
                "deprecated_package": deprecated["package"],
                "alternative": deprecated["alternative"],
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create deprecation replacement PR: {e}")
            return None
    
    def _update_vulnerability_database(self, vulnerabilities: List[Dict[str, Any]]):
        """Update local vulnerability database with new findings."""
        for vuln in vulnerabilities:
            package_name = vuln["package"]
            if package_name not in self.vulnerability_database:
                self.vulnerability_database[package_name] = []
                
            self.vulnerability_database[package_name].append({
                "found_at": datetime.now().isoformat(),
                "severity": vuln["severity"],
                "cve": vuln["vulnerability"].get("cve", ""),
                "description": vuln["vulnerability"].get("description", "")
            })
    
    def _calculate_health_score(self, vulnerabilities: List[Dict[str, Any]], 
                              updates: List[Dict[str, Any]], 
                              deprecated: List[Dict[str, Any]]) -> float:
        """Calculate overall dependency health score."""
        score = 100.0
        
        # Deduct points for vulnerabilities
        for vuln in vulnerabilities:
            severity_penalty = {
                "critical": 25,
                "high": 15,
                "medium": 8,
                "low": 3
            }
            score -= severity_penalty.get(vuln.get("severity", "low"), 3)
        
        # Deduct points for outdated dependencies
        score -= len(updates) * 2
        
        # Deduct points for deprecated dependencies
        score -= len(deprecated) * 10
        
        return max(0.0, score)
    
    def _update_health_metrics(self, analysis_results: List[Dict[str, Any]], 
                             vulnerabilities: List[Dict[str, Any]], 
                             updates: List[Dict[str, Any]], 
                             security_updates: List[Dict[str, Any]], 
                             prs_created: List[Dict[str, Any]], 
                             health_score: float):
        """Update health metrics."""
        total_deps = sum(len(r.get("dependencies", [])) for r in analysis_results)
        
        self.health_metrics.update({
            "dependencies_tracked": total_deps,
            "vulnerabilities_found": len(vulnerabilities),
            "updates_available": len(updates),
            "security_updates_applied": len(security_updates),
            "prs_created": len(prs_created),
            "health_score": health_score
        })
    
    def _quick_vulnerability_scan(self) -> List[Dict[str, Any]]:
        """Quick scan for critical vulnerabilities."""
        # Simulate quick vulnerability scan
        critical_vulns = [
            {
                "package": "requests",
                "severity": "critical",
                "cve": "CVE-2024-XXXX"
            }
        ]
        
        return critical_vulns
    
    def _check_critical_updates(self) -> List[Dict[str, Any]]:
        """Check for critical security updates."""
        # Simulate critical update check
        critical_updates = [
            {
                "package": "django",
                "current": "3.0.0",
                "latest": "3.2.15",
                "security_update": True
            }
        ]
        
        return critical_updates
    
    def _prepare_critical_update_templates(self, vulns: List[Dict[str, Any]], updates: List[Dict[str, Any]]) -> bool:
        """Prepare PR templates for critical issues."""
        try:
            # Pre-generate PR templates for critical issues
            templates = {
                "critical_security": "CRITICAL SECURITY UPDATE: {package}\n\nThis update addresses {cve}",
                "urgent_update": "URGENT UPDATE: {package}\n\nSecurity patches included"
            }
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to prepare critical update templates: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the dependency health engine."""
        return {
            "name": self.name,
            "running": self.is_running,
            "health_metrics": self.health_metrics,
            "vulnerability_db_size": len(self.vulnerability_database),
            "update_policies": self.update_policies,
            "last_execution": self.last_execution,
            "total_executions": len(self.execution_history)
        }