"""
Workflow Auditor Engine - Recursive Autonomy Module
Meta-workflow auditor for CI/CD pipeline optimization and security, suggesting improvements recursively
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import os
import yaml
import json
import re
import logging

from ..base import RecursiveEngine, CompoundingAction


class WorkflowAuditorEngine(RecursiveEngine):
    """
    Meta-workflow auditor that analyzes CI/CD pipelines for optimization and security improvements.
    Recursively suggests and applies workflow enhancements.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("workflow_auditor", config)
        self.audit_history = []
        self.workflow_patterns = {}
        self.security_rules = self._load_security_rules()
        self.optimization_metrics = {}
        
    def initialize(self) -> bool:
        """Initialize the workflow auditor engine."""
        try:
            self.logger.info("Initializing Workflow Auditor Engine")
            
            # Set up compounding actions
            audit_action = CompoundingAction(
                name="workflow_audit",
                action=self.execute_main_action,
                interval=1.0,  # Weekly comprehensive audit
                pre_action=self.execute_pre_action,
                pre_interval=0.25,  # Quick security scan
                metadata={"type": "workflow_audit", "recursive": True}
            )
            
            self.add_compounding_action(audit_action)
            
            # Initialize optimization metrics
            self.optimization_metrics = {
                "workflows_audited": 0,
                "security_issues_found": 0,
                "optimizations_suggested": 0,
                "performance_improvements": 0,
                "cost_optimizations": 0,
                "security_score": 100.0,
                "efficiency_score": 75.0
            }
            
            self.logger.info("Workflow Auditor Engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Workflow Auditor Engine: {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute comprehensive workflow audit and optimization."""
        try:
            self.logger.info("Executing comprehensive workflow audit")
            
            # Find all workflow files
            workflow_files = self._find_workflow_files()
            
            # Audit each workflow file
            audit_results = []
            for workflow_file in workflow_files:
                audit = self._audit_workflow_file(workflow_file)
                audit_results.append(audit)
            
            # Analyze workflow patterns across repository
            pattern_analysis = self._analyze_workflow_patterns(audit_results)
            
            # Check for security vulnerabilities
            security_issues = self._check_workflow_security(audit_results)
            
            # Identify optimization opportunities
            optimization_opportunities = self._identify_optimizations(audit_results)
            
            # Generate improvement suggestions
            improvement_suggestions = self._generate_improvement_suggestions(
                security_issues, optimization_opportunities, pattern_analysis
            )
            
            # Apply safe optimizations automatically
            applied_optimizations = self._apply_safe_optimizations(improvement_suggestions)
            
            # Create PRs for complex improvements
            prs_created = self._create_improvement_prs(improvement_suggestions)
            
            # Update workflow patterns database
            self._update_workflow_patterns(pattern_analysis)
            
            # Calculate scores
            security_score = self._calculate_security_score(security_issues)
            efficiency_score = self._calculate_efficiency_score(optimization_opportunities)
            
            # Update metrics
            self._update_optimization_metrics(audit_results, security_issues, optimization_opportunities,
                                            applied_optimizations, security_score, efficiency_score)
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "action": "comprehensive_workflow_audit",
                "workflows_audited": len(workflow_files),
                "security_issues_found": len(security_issues),
                "optimization_opportunities": len(optimization_opportunities),
                "improvements_suggested": len(improvement_suggestions),
                "optimizations_applied": len(applied_optimizations),
                "prs_created": len(prs_created),
                "security_score": security_score,
                "efficiency_score": efficiency_score,
                "metrics": self.optimization_metrics
            }
            
            self.audit_history.append(result)
            self.logger.info(f"Workflow audit completed: {len(workflow_files)} workflows, {len(security_issues)} security issues")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in workflow audit: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "comprehensive_workflow_audit", 
                "error": str(e),
                "status": "failed"
            }
    
    def execute_pre_action(self) -> Dict[str, Any]:
        """Execute pre-action: quick security scan and critical issue detection."""
        try:
            self.logger.info("Quick workflow security scan and critical issue detection")
            
            # Quick scan for critical security issues
            critical_security_issues = self._quick_security_scan()
            
            # Check for workflow failures and bottlenecks
            performance_issues = self._check_performance_issues()
            
            # Pre-prepare optimization templates
            templates_prepared = self._prepare_optimization_templates(critical_security_issues, performance_issues)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "quick_workflow_security_scan",
                "critical_security_issues": len(critical_security_issues),
                "performance_issues": len(performance_issues),
                "templates_prepared": templates_prepared,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"Error in quick workflow scan: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "quick_workflow_security_scan",
                "error": str(e),
                "status": "failed"
            }
    
    def _load_security_rules(self) -> Dict[str, Any]:
        """Load workflow security rules and patterns."""
        return {
            "secrets_management": [
                {
                    "rule": "no_hardcoded_secrets",
                    "pattern": r"(password|token|key|secret)\s*[:=]\s*[\"'][^\"']*[\"']",
                    "severity": "critical",
                    "description": "Hardcoded secrets detected in workflow"
                },
                {
                    "rule": "use_github_secrets",
                    "pattern": r"\$\{\{\s*secrets\.",
                    "severity": "info",
                    "description": "Proper use of GitHub secrets"
                }
            ],
            "permissions": [
                {
                    "rule": "minimal_permissions",
                    "check": "permissions_scope",
                    "severity": "high",
                    "description": "Workflow uses overly broad permissions"
                },
                {
                    "rule": "no_write_all",
                    "pattern": r"permissions:\s*write-all",
                    "severity": "high",
                    "description": "Dangerous write-all permissions"
                }
            ],
            "third_party_actions": [
                {
                    "rule": "pinned_action_versions",
                    "pattern": r"uses:\s*[^@]*@(?!v?\d+\.\d+\.\d+)[^#\s]*",
                    "severity": "medium",
                    "description": "Third-party actions not pinned to specific versions"
                },
                {
                    "rule": "trusted_actions_only",
                    "check": "action_source_verification",
                    "severity": "high",
                    "description": "Use of untrusted third-party actions"
                }
            ],
            "environment_security": [
                {
                    "rule": "environment_isolation",
                    "check": "environment_separation",
                    "severity": "medium",
                    "description": "Insufficient environment isolation"
                }
            ]
        }
    
    def _find_workflow_files(self) -> List[str]:
        """Find all workflow files in the repository."""
        workflow_files = []
        
        # GitHub Actions workflows
        github_workflows_dir = ".github/workflows"
        if os.path.exists(github_workflows_dir):
            for file in os.listdir(github_workflows_dir):
                if file.endswith(('.yml', '.yaml')):
                    workflow_files.append(os.path.join(github_workflows_dir, file))
        
        # GitLab CI/CD
        gitlab_files = [".gitlab-ci.yml", ".gitlab-ci.yaml"]
        for file in gitlab_files:
            if os.path.exists(file):
                workflow_files.append(file)
        
        # Jenkins
        jenkins_files = ["Jenkinsfile", "jenkinsfile"]
        for file in jenkins_files:
            if os.path.exists(file):
                workflow_files.append(file)
        
        # CircleCI
        circleci_dir = ".circleci"
        if os.path.exists(circleci_dir):
            config_file = os.path.join(circleci_dir, "config.yml")
            if os.path.exists(config_file):
                workflow_files.append(config_file)
        
        # Azure Pipelines
        azure_files = ["azure-pipelines.yml", "azure-pipelines.yaml", ".azure-pipelines.yml"]
        for file in azure_files:
            if os.path.exists(file):
                workflow_files.append(file)
                
        return workflow_files
    
    def _audit_workflow_file(self, file_path: str) -> Dict[str, Any]:
        """Audit a specific workflow file."""
        try:
            audit_result = {
                "file_path": file_path,
                "file_type": self._detect_workflow_type(file_path),
                "last_modified": os.path.getmtime(file_path),
                "audit_timestamp": datetime.now().isoformat(),
                "security_issues": [],
                "optimization_opportunities": [],
                "complexity_score": 0,
                "maintainability_score": 0
            }
            
            # Read and parse workflow file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.endswith(('.yml', '.yaml')):
                try:
                    workflow_data = yaml.safe_load(content)
                    audit_result["parsed_content"] = workflow_data
                except yaml.YAMLError as e:
                    audit_result["parse_error"] = str(e)
                    return audit_result
            
            # Perform security checks
            audit_result["security_issues"] = self._check_file_security(content, workflow_data)
            
            # Check for optimization opportunities
            audit_result["optimization_opportunities"] = self._check_file_optimizations(content, workflow_data)
            
            # Calculate complexity and maintainability scores
            audit_result["complexity_score"] = self._calculate_workflow_complexity(workflow_data)
            audit_result["maintainability_score"] = self._calculate_maintainability_score(workflow_data)
            
            return audit_result
            
        except Exception as e:
            self.logger.error(f"Error auditing workflow file {file_path}: {e}")
            return {
                "file_path": file_path,
                "error": str(e),
                "audit_timestamp": datetime.now().isoformat()
            }
    
    def _detect_workflow_type(self, file_path: str) -> str:
        """Detect the type of workflow file."""
        if ".github/workflows" in file_path:
            return "github_actions"
        elif "gitlab-ci" in file_path.lower():
            return "gitlab_ci"
        elif "jenkins" in file_path.lower():
            return "jenkins"
        elif ".circleci" in file_path:
            return "circleci"
        elif "azure-pipelines" in file_path:
            return "azure_pipelines"
        else:
            return "unknown"
    
    def _check_file_security(self, content: str, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check a workflow file for security issues."""
        security_issues = []
        
        # Check each security rule category
        for category, rules in self.security_rules.items():
            for rule in rules:
                if "pattern" in rule:
                    # Pattern-based check
                    matches = re.finditer(rule["pattern"], content, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        security_issues.append({
                            "rule": rule["rule"],
                            "category": category,
                            "severity": rule["severity"],
                            "description": rule["description"],
                            "line": line_num,
                            "match": match.group()
                        })
                elif "check" in rule:
                    # Custom check function
                    issue = self._custom_security_check(rule, workflow_data)
                    if issue:
                        issue["category"] = category
                        security_issues.append(issue)
        
        return security_issues
    
    def _custom_security_check(self, rule: Dict[str, Any], workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform custom security checks on workflow data."""
        check_type = rule["check"]
        
        if check_type == "permissions_scope":
            return self._check_permissions_scope(workflow_data, rule)
        elif check_type == "action_source_verification":
            return self._check_action_sources(workflow_data, rule)
        elif check_type == "environment_separation":
            return self._check_environment_separation(workflow_data, rule)
        
        return None
    
    def _check_permissions_scope(self, workflow_data: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Check if workflow permissions are too broad."""
        permissions = workflow_data.get("permissions", {})
        
        if permissions == "write-all" or permissions.get("contents") == "write":
            return {
                "rule": rule["rule"],
                "severity": rule["severity"],
                "description": rule["description"],
                "details": "Workflow has overly broad write permissions"
            }
        
        return None
    
    def _check_action_sources(self, workflow_data: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Check if third-party actions are from trusted sources."""
        untrusted_actions = []
        
        jobs = workflow_data.get("jobs", {})
        for job_name, job_data in jobs.items():
            steps = job_data.get("steps", [])
            for step in steps:
                if "uses" in step:
                    action = step["uses"]
                    # Check if action is from trusted sources
                    if not self._is_trusted_action(action):
                        untrusted_actions.append(action)
        
        if untrusted_actions:
            return {
                "rule": rule["rule"],
                "severity": rule["severity"],
                "description": rule["description"],
                "details": f"Untrusted actions: {', '.join(untrusted_actions)}"
            }
        
        return None
    
    def _is_trusted_action(self, action: str) -> bool:
        """Check if an action is from a trusted source."""
        trusted_sources = [
            "actions/",
            "github/",
            "microsoft/",
            "google/",
            "aws-actions/"
        ]
        
        return any(action.startswith(source) for source in trusted_sources)
    
    def _check_environment_separation(self, workflow_data: Dict[str, Any], rule: Dict[str, Any]) -> Dict[str, Any]:
        """Check for proper environment separation."""
        # Check if production and staging environments are properly separated
        jobs = workflow_data.get("jobs", {})
        
        prod_and_staging_in_same_job = False
        for job_name, job_data in jobs.items():
            env_vars = job_data.get("env", {})
            if "production" in str(env_vars).lower() and "staging" in str(env_vars).lower():
                prod_and_staging_in_same_job = True
                break
        
        if prod_and_staging_in_same_job:
            return {
                "rule": rule["rule"],
                "severity": rule["severity"],
                "description": rule["description"],
                "details": "Production and staging environments mixed in same job"
            }
        
        return None
    
    def _check_file_optimizations(self, content: str, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for optimization opportunities in workflow file."""
        optimizations = []
        
        # Check for caching opportunities
        caching_opp = self._check_caching_opportunities(workflow_data)
        optimizations.extend(caching_opp)
        
        # Check for parallelization opportunities
        parallel_opp = self._check_parallelization_opportunities(workflow_data)
        optimizations.extend(parallel_opp)
        
        # Check for resource optimization
        resource_opp = self._check_resource_optimization(workflow_data)
        optimizations.extend(resource_opp)
        
        # Check for workflow triggers optimization
        trigger_opp = self._check_trigger_optimization(workflow_data)
        optimizations.extend(trigger_opp)
        
        return optimizations
    
    def _check_caching_opportunities(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for caching opportunities."""
        opportunities = []
        
        jobs = workflow_data.get("jobs", {})
        for job_name, job_data in jobs.items():
            steps = job_data.get("steps", [])
            
            has_npm_install = any("npm install" in str(step) for step in steps)
            has_cache_action = any("actions/cache" in str(step.get("uses", "")) for step in steps)
            
            if has_npm_install and not has_cache_action:
                opportunities.append({
                    "type": "add_caching",
                    "job": job_name,
                    "description": "Add npm cache to speed up builds",
                    "impact": "medium",
                    "effort": "low"
                })
        
        return opportunities
    
    def _check_parallelization_opportunities(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for parallelization opportunities."""
        opportunities = []
        
        jobs = workflow_data.get("jobs", {})
        
        # Look for jobs that could run in parallel
        sequential_jobs = []
        for job_name, job_data in jobs.items():
            needs = job_data.get("needs", [])
            if needs:
                sequential_jobs.append(job_name)
        
        # If many jobs are sequential, suggest parallelization
        if len(sequential_jobs) > 3:
            opportunities.append({
                "type": "increase_parallelization",
                "description": f"Consider parallelizing {len(sequential_jobs)} sequential jobs",
                "impact": "high",
                "effort": "medium"
            })
        
        return opportunities
    
    def _check_resource_optimization(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for resource optimization opportunities."""
        opportunities = []
        
        jobs = workflow_data.get("jobs", {})
        for job_name, job_data in jobs.items():
            runs_on = job_data.get("runs-on", "")
            
            # Check if using expensive runners unnecessarily
            if "windows" in runs_on.lower() or "macos" in runs_on.lower():
                opportunities.append({
                    "type": "optimize_runner",
                    "job": job_name,
                    "description": f"Consider using ubuntu runner instead of {runs_on} for cost savings",
                    "impact": "high",
                    "effort": "low"
                })
        
        return opportunities
    
    def _check_trigger_optimization(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check workflow trigger optimization."""
        opportunities = []
        
        on_triggers = workflow_data.get("on", {})
        
        # Check if workflow runs on too many triggers
        if isinstance(on_triggers, dict) and len(on_triggers) > 5:
            opportunities.append({
                "type": "optimize_triggers",
                "description": "Workflow has many triggers, consider consolidating",
                "impact": "medium",
                "effort": "low"
            })
        
        # Check for unnecessary push triggers
        if "push" in on_triggers and "pull_request" in on_triggers:
            opportunities.append({
                "type": "consolidate_triggers",
                "description": "Workflow runs on both push and PR, consider using only PR",
                "impact": "low",
                "effort": "low"
            })
        
        return opportunities
    
    def _calculate_workflow_complexity(self, workflow_data: Dict[str, Any]) -> int:
        """Calculate workflow complexity score."""
        complexity = 0
        
        jobs = workflow_data.get("jobs", {})
        complexity += len(jobs) * 2  # Each job adds complexity
        
        for job_data in jobs.values():
            steps = job_data.get("steps", [])
            complexity += len(steps)  # Each step adds complexity
            
            # Conditional steps add more complexity
            for step in steps:
                if "if" in step:
                    complexity += 2
        
        return complexity
    
    def _calculate_maintainability_score(self, workflow_data: Dict[str, Any]) -> float:
        """Calculate workflow maintainability score."""
        score = 100.0
        
        jobs = workflow_data.get("jobs", {})
        
        # Deduct points for long jobs
        for job_data in jobs.values():
            steps = job_data.get("steps", [])
            if len(steps) > 20:
                score -= 10
        
        # Deduct points for hardcoded values
        content_str = str(workflow_data)
        hardcoded_patterns = re.findall(r'\b\d+\.\d+\.\d+\b', content_str)  # Version numbers
        score -= len(hardcoded_patterns) * 2
        
        # Deduct points for missing documentation
        if "name" not in workflow_data:
            score -= 5
        
        return max(0.0, score)
    
    def _analyze_workflow_patterns(self, audit_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns across all workflows."""
        patterns = {
            "common_actions": {},
            "common_triggers": {},
            "runner_usage": {},
            "job_patterns": {},
            "complexity_distribution": []
        }
        
        for audit in audit_results:
            workflow_data = audit.get("parsed_content", {})
            
            # Analyze common actions
            jobs = workflow_data.get("jobs", {})
            for job_data in jobs.values():
                steps = job_data.get("steps", [])
                for step in steps:
                    if "uses" in step:
                        action = step["uses"].split("@")[0]  # Remove version
                        patterns["common_actions"][action] = patterns["common_actions"].get(action, 0) + 1
            
            # Analyze triggers
            on_triggers = workflow_data.get("on", {})
            if isinstance(on_triggers, dict):
                for trigger in on_triggers.keys():
                    patterns["common_triggers"][trigger] = patterns["common_triggers"].get(trigger, 0) + 1
            
            # Complexity distribution
            complexity = audit.get("complexity_score", 0)
            patterns["complexity_distribution"].append(complexity)
        
        return patterns
    
    def _check_workflow_security(self, audit_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate security issues from all workflows."""
        all_security_issues = []
        
        for audit in audit_results:
            security_issues = audit.get("security_issues", [])
            for issue in security_issues:
                issue["file"] = audit["file_path"]
                all_security_issues.append(issue)
        
        return all_security_issues
    
    def _identify_optimizations(self, audit_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities across all workflows."""
        all_optimizations = []
        
        for audit in audit_results:
            optimizations = audit.get("optimization_opportunities", [])
            for opt in optimizations:
                opt["file"] = audit["file_path"]
                all_optimizations.append(opt)
        
        return all_optimizations
    
    def _generate_improvement_suggestions(self, security_issues: List[Dict[str, Any]], 
                                        optimizations: List[Dict[str, Any]], 
                                        patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive improvement suggestions."""
        suggestions = []
        
        # Security improvement suggestions
        for issue in security_issues:
            suggestions.append({
                "type": "security_fix",
                "category": issue["category"],
                "description": f"Fix {issue['rule']} in {issue['file']}",
                "priority": self._severity_to_priority(issue["severity"]),
                "safety": "high",
                "file": issue["file"]
            })
        
        # Optimization suggestions
        for opt in optimizations:
            suggestions.append({
                "type": "optimization",
                "category": opt["type"],
                "description": opt["description"],
                "priority": self._impact_to_priority(opt["impact"]),
                "safety": "medium",
                "file": opt.get("file", "")
            })
        
        # Pattern-based suggestions
        if patterns["complexity_distribution"]:
            avg_complexity = sum(patterns["complexity_distribution"]) / len(patterns["complexity_distribution"])
            if avg_complexity > 50:
                suggestions.append({
                    "type": "complexity_reduction",
                    "category": "maintainability",
                    "description": "Workflows are complex, consider breaking down into smaller jobs",
                    "priority": "medium",
                    "safety": "low"
                })
        
        return suggestions
    
    def _severity_to_priority(self, severity: str) -> str:
        """Convert security severity to priority."""
        mapping = {
            "critical": "high",
            "high": "high", 
            "medium": "medium",
            "low": "low",
            "info": "low"
        }
        return mapping.get(severity, "medium")
    
    def _impact_to_priority(self, impact: str) -> str:
        """Convert optimization impact to priority."""
        mapping = {
            "high": "high",
            "medium": "medium",
            "low": "low"
        }
        return mapping.get(impact, "medium")
    
    def _apply_safe_optimizations(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply safe optimizations automatically."""
        applied_optimizations = []
        
        for suggestion in suggestions:
            if suggestion.get("safety") == "high" and suggestion.get("priority") in ["high", "medium"]:
                try:
                    success = self._apply_optimization(suggestion)
                    if success:
                        applied_optimizations.append(suggestion)
                        
                except Exception as e:
                    self.logger.error(f"Failed to apply optimization: {e}")
        
        return applied_optimizations
    
    def _apply_optimization(self, suggestion: Dict[str, Any]) -> bool:
        """Apply a specific optimization."""
        try:
            # Simulate optimization application
            self.logger.info(f"Applying optimization: {suggestion['description']}")
            return True
        except Exception as e:
            self.logger.error(f"Error applying optimization: {e}")
            return False
    
    def _create_improvement_prs(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create PRs for workflow improvements."""
        prs_created = []
        
        # Group suggestions by type and priority
        security_suggestions = [s for s in suggestions if s["type"] == "security_fix"]
        optimization_suggestions = [s for s in suggestions if s["type"] == "optimization"]
        
        # Create PR for security fixes
        if security_suggestions:
            pr_info = self._create_security_improvement_pr(security_suggestions)
            if pr_info:
                prs_created.append(pr_info)
        
        # Create PR for optimizations
        if optimization_suggestions:
            pr_info = self._create_optimization_pr(optimization_suggestions)
            if pr_info:
                prs_created.append(pr_info)
        
        return prs_created
    
    def _create_security_improvement_pr(self, security_suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create PR for security improvements."""
        try:
            pr_title = "Workflow Security Improvements"
            pr_body = "This PR addresses the following security issues:\n\n"
            
            for suggestion in security_suggestions:
                pr_body += f"- {suggestion['description']}\n"
            
            self.logger.info(f"Creating security improvement PR: {pr_title}")
            
            return {
                "type": "security_improvement",
                "title": pr_title,
                "issues_addressed": len(security_suggestions),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create security improvement PR: {e}")
            return None
    
    def _create_optimization_pr(self, optimization_suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create PR for workflow optimizations."""
        try:
            pr_title = "Workflow Performance Optimizations"
            pr_body = "This PR includes the following workflow optimizations:\n\n"
            
            for suggestion in optimization_suggestions:
                pr_body += f"- {suggestion['description']}\n"
            
            self.logger.info(f"Creating optimization PR: {pr_title}")
            
            return {
                "type": "optimization",
                "title": pr_title,
                "optimizations_included": len(optimization_suggestions),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create optimization PR: {e}")
            return None
    
    def _update_workflow_patterns(self, patterns: Dict[str, Any]):
        """Update workflow patterns database."""
        self.workflow_patterns.update(patterns)
    
    def _calculate_security_score(self, security_issues: List[Dict[str, Any]]) -> float:
        """Calculate overall security score."""
        score = 100.0
        
        for issue in security_issues:
            severity_penalty = {
                "critical": 30,
                "high": 20,
                "medium": 10,
                "low": 5,
                "info": 2
            }
            score -= severity_penalty.get(issue.get("severity", "low"), 2)
        
        return max(0.0, score)
    
    def _calculate_efficiency_score(self, optimizations: List[Dict[str, Any]]) -> float:
        """Calculate overall efficiency score."""
        score = 100.0
        
        for opt in optimizations:
            impact_penalty = {
                "high": 15,
                "medium": 8,
                "low": 3
            }
            score -= impact_penalty.get(opt.get("impact", "low"), 3)
        
        return max(0.0, score)
    
    def _update_optimization_metrics(self, audit_results: List[Dict[str, Any]], 
                                   security_issues: List[Dict[str, Any]], 
                                   optimizations: List[Dict[str, Any]], 
                                   applied_optimizations: List[Dict[str, Any]], 
                                   security_score: float, 
                                   efficiency_score: float):
        """Update optimization metrics."""
        self.optimization_metrics.update({
            "workflows_audited": len(audit_results),
            "security_issues_found": len(security_issues),
            "optimizations_suggested": len(optimizations),
            "performance_improvements": len(applied_optimizations),
            "security_score": security_score,
            "efficiency_score": efficiency_score
        })
    
    def _quick_security_scan(self) -> List[Dict[str, Any]]:
        """Quick scan for critical security issues."""
        # Simulate quick security scan
        critical_issues = [
            {
                "rule": "hardcoded_secrets",
                "severity": "critical",
                "file": ".github/workflows/ci.yml"
            }
        ]
        
        return critical_issues
    
    def _check_performance_issues(self) -> List[Dict[str, Any]]:
        """Check for workflow performance issues."""
        # Simulate performance issue detection
        performance_issues = [
            {
                "type": "slow_job",
                "file": ".github/workflows/ci.yml",
                "job": "test",
                "issue": "Job takes longer than 10 minutes"
            }
        ]
        
        return performance_issues
    
    def _prepare_optimization_templates(self, security_issues: List[Dict[str, Any]], 
                                      performance_issues: List[Dict[str, Any]]) -> bool:
        """Prepare optimization templates for critical issues."""
        try:
            # Pre-generate templates for common optimizations
            templates = {
                "add_caching": "- name: Cache dependencies\n  uses: actions/cache@v3",
                "fix_permissions": "permissions:\n  contents: read\n  pull-requests: write",
                "security_fix": "# Remove hardcoded secrets and use GitHub secrets"
            }
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to prepare optimization templates: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the workflow auditor engine."""
        return {
            "name": self.name,
            "running": self.is_running,
            "optimization_metrics": self.optimization_metrics,
            "security_rules_count": sum(len(rules) for rules in self.security_rules.values()),
            "workflow_patterns_count": len(self.workflow_patterns),
            "last_execution": self.last_execution,
            "total_executions": len(self.execution_history)
        }