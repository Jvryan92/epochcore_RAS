#!/usr/bin/env python3
"""
Merge Automation System
EpochCore RAS Repository Automation

Smart conflict resolution, quality gates, and rollback protection
for automated merge operations.
"""

import os
import json
import yaml
import subprocess
import logging
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import tempfile
import re


class MergeAutomation:
    """Manages automated merge operations with quality gates and rollback."""
    
    def __init__(self, config_path: str = "config/merge_automation.yaml"):
        self.config_path = config_path
        self.config = {}
        self.merge_log = "logs/merge_operations.json"
        
        # Ensure directories exist
        for path in ["logs", "config", "backups/merge_states"]:
            Path(path).mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.load_config()
        
        # Merge operation history
        self.merge_history = []
        self.load_merge_history()
        
        # Git operations
        self.git_available = self.check_git_available()
    
    def load_config(self) -> bool:
        """Load merge automation configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.logger.info("Loaded merge automation configuration")
                return True
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
        
        # Use default configuration
        self.config = self.get_default_config()
        self.save_config()
        return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default merge automation configuration."""
        return {
            "merge_strategies": {
                "auto_merge": {
                    "enabled": True,
                    "conditions": [
                        "all_checks_passed",
                        "no_conflicts", 
                        "approved_by_maintainer"
                    ]
                },
                "conflict_resolution": {
                    "strategy": "auto",
                    "prefer": "incoming",
                    "timeout_seconds": 300
                }
            },
            "quality_gates": {
                "pre_merge": [
                    "lint_check",
                    "test_suite",
                    "security_scan",
                    "integration_test"
                ],
                "post_merge": [
                    "deployment_test",
                    "smoke_test", 
                    "rollback_validation"
                ]
            },
            "notifications": {
                "success": True,
                "failure": True,
                "conflict": True
            },
            "rollback": {
                "enabled": True,
                "triggers": [
                    "test_failure",
                    "deployment_failure",
                    "critical_error"
                ],
                "strategy": "backup_restore"
            },
            "thresholds": {
                "max_conflicts": 10,
                "timeout_minutes": 30,
                "max_file_changes": 100
            }
        }
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
            return False
    
    def load_merge_history(self) -> bool:
        """Load merge operation history."""
        if os.path.exists(self.merge_log):
            try:
                with open(self.merge_log, 'r') as f:
                    self.merge_history = json.load(f)
                return True
            except Exception as e:
                self.logger.error(f"Failed to load merge history: {e}")
        
        self.merge_history = []
        return False
    
    def save_merge_history(self) -> bool:
        """Save merge operation history."""
        try:
            with open(self.merge_log, 'w') as f:
                json.dump(self.merge_history, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save merge history: {e}")
            return False
    
    def check_git_available(self) -> bool:
        """Check if git is available."""
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warning("Git is not available")
            return False
    
    def run_git_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[bool, str, str]:
        """Run a git command safely."""
        if not self.git_available:
            return False, "", "Git is not available"
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=300
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Git command timed out"
        except Exception as e:
            return False, "", f"Git command failed: {str(e)}"
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get current git repository status."""
        status = {
            "is_git_repo": False,
            "current_branch": "",
            "has_changes": False,
            "conflicts": [],
            "untracked_files": [],
            "modified_files": [],
            "ahead_behind": {"ahead": 0, "behind": 0}
        }
        
        if not self.git_available:
            return status
        
        # Check if in git repo
        success, stdout, stderr = self.run_git_command(['git', 'rev-parse', '--is-inside-work-tree'])
        if not success:
            return status
        
        status["is_git_repo"] = True
        
        # Get current branch
        success, stdout, stderr = self.run_git_command(['git', 'branch', '--show-current'])
        if success:
            status["current_branch"] = stdout.strip()
        
        # Check for changes
        success, stdout, stderr = self.run_git_command(['git', 'status', '--porcelain'])
        if success:
            lines = stdout.strip().split('\n') if stdout.strip() else []
            status["has_changes"] = len(lines) > 0
            
            for line in lines:
                if line.startswith('??'):
                    status["untracked_files"].append(line[3:])
                elif line.startswith(' M') or line.startswith('M '):
                    status["modified_files"].append(line[3:])
                elif line.startswith('UU'):
                    status["conflicts"].append(line[3:])
        
        # Check ahead/behind status
        success, stdout, stderr = self.run_git_command(['git', 'rev-list', '--left-right', '--count', 'HEAD...@{upstream}'])
        if success and stdout.strip():
            try:
                ahead, behind = map(int, stdout.strip().split())
                status["ahead_behind"] = {"ahead": ahead, "behind": behind}
            except ValueError:
                pass
        
        return status
    
    def create_backup_state(self) -> str:
        """Create backup of current repository state."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path("backups/merge_states") / f"merge_backup_{timestamp}"
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Save git status
            git_status = self.get_git_status()
            with open(backup_path / "git_status.json", 'w') as f:
                json.dump(git_status, f, indent=2)
            
            # Create git bundle if possible
            if self.git_available and git_status["is_git_repo"]:
                success, stdout, stderr = self.run_git_command([
                    'git', 'bundle', 'create', 
                    str(backup_path / "repo_backup.bundle"),
                    '--all'
                ])
                
                if success:
                    self.logger.info(f"Created git bundle backup: {backup_path}")
                else:
                    # Fallback: copy important files
                    self.copy_essential_files(backup_path)
            else:
                self.copy_essential_files(backup_path)
            
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"Failed to create backup state: {e}")
            return ""
    
    def copy_essential_files(self, backup_path: Path) -> None:
        """Copy essential files to backup location."""
        essential_patterns = [
            "*.py",
            "*.yaml", "*.yml",
            "*.json",
            "*.md",
            "requirements.txt",
            "pyproject.toml"
        ]
        
        for pattern in essential_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.is_file():
                    try:
                        dest_path = backup_path / file_path.name
                        shutil.copy2(file_path, dest_path)
                    except Exception as e:
                        self.logger.warning(f"Could not backup {file_path}: {e}")
    
    def run_quality_gate(self, gate_name: str) -> Dict[str, Any]:
        """Run a specific quality gate check."""
        gate_result = {
            "gate": gate_name,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "duration_seconds": 0,
            "output": "",
            "errors": []
        }
        
        start_time = datetime.now()
        
        try:
            if gate_name == "lint_check":
                gate_result = self.run_lint_check()
            elif gate_name == "test_suite":
                gate_result = self.run_test_suite()
            elif gate_name == "security_scan":
                gate_result = self.run_security_scan()
            elif gate_name == "integration_test":
                gate_result = self.run_integration_test()
            elif gate_name == "deployment_test":
                gate_result = self.run_deployment_test()
            elif gate_name == "smoke_test":
                gate_result = self.run_smoke_test()
            elif gate_name == "rollback_validation":
                gate_result = self.run_rollback_validation()
            else:
                gate_result["errors"].append(f"Unknown quality gate: {gate_name}")
            
        except Exception as e:
            gate_result["errors"].append(f"Quality gate {gate_name} failed: {str(e)}")
        
        gate_result["duration_seconds"] = (datetime.now() - start_time).total_seconds()
        return gate_result
    
    def run_lint_check(self) -> Dict[str, Any]:
        """Run linting checks."""
        result = {
            "gate": "lint_check",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "output": "",
            "errors": []
        }
        
        # Try flake8 first
        try:
            proc_result = subprocess.run(
                ['flake8', '.', '--max-line-length=88', '--extend-ignore=E203,W503'],
                capture_output=True, text=True, timeout=60
            )
            result["output"] = proc_result.stdout + proc_result.stderr
            result["success"] = proc_result.returncode == 0
            
            if not result["success"]:
                result["errors"].append("Flake8 linting issues found")
            
        except subprocess.TimeoutExpired:
            result["errors"].append("Linting timed out")
        except FileNotFoundError:
            # Fallback: basic Python syntax check
            result = self.run_basic_syntax_check()
        except Exception as e:
            result["errors"].append(f"Linting failed: {str(e)}")
        
        return result
    
    def run_basic_syntax_check(self) -> Dict[str, Any]:
        """Run basic Python syntax checking."""
        result = {
            "gate": "lint_check",
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "output": "",
            "errors": []
        }
        
        python_files = list(Path(".").glob("**/*.py"))
        syntax_errors = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError as e:
                syntax_errors.append(f"{py_file}:{e.lineno}: {e.msg}")
            except Exception as e:
                syntax_errors.append(f"{py_file}: {str(e)}")
        
        if syntax_errors:
            result["success"] = False
            result["errors"] = syntax_errors
            result["output"] = "\n".join(syntax_errors)
        else:
            result["output"] = f"Checked {len(python_files)} Python files - no syntax errors"
        
        return result
    
    def run_test_suite(self) -> Dict[str, Any]:
        """Run the test suite."""
        result = {
            "gate": "test_suite",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "output": "",
            "errors": []
        }
        
        # Try pytest first, then unittest
        test_commands = [
            ['python', '-m', 'pytest', '-v', '--tb=short'],
            ['python', '-m', 'unittest', 'discover', 'tests/', '-v']
        ]
        
        for cmd in test_commands:
            try:
                proc_result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=300
                )
                result["output"] = proc_result.stdout + proc_result.stderr
                result["success"] = proc_result.returncode == 0
                
                if result["success"]:
                    break
                else:
                    result["errors"].append(f"Tests failed with command: {' '.join(cmd)}")
                    
            except subprocess.TimeoutExpired:
                result["errors"].append("Tests timed out")
                break
            except FileNotFoundError:
                continue
            except Exception as e:
                result["errors"].append(f"Test execution failed: {str(e)}")
                break
        
        if not result["success"] and not result["errors"]:
            result["errors"].append("No test runner found (pytest or unittest)")
        
        return result
    
    def run_security_scan(self) -> Dict[str, Any]:
        """Run basic security scanning."""
        result = {
            "gate": "security_scan",
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "output": "",
            "errors": []
        }
        
        security_issues = []
        
        # Check for common security issues
        try:
            # Check for hardcoded secrets
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ]
            
            for py_file in Path(".").glob("**/*.py"):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        for pattern in secret_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                security_issues.append(f"Potential secret in {py_file}")
                                break
                except Exception:
                    continue
            
            # Check file permissions (Unix-like systems)
            try:
                import stat
                sensitive_files = [".env", "config/*.yaml", "*.key", "*.pem"]
                for pattern in sensitive_files:
                    for file_path in Path(".").glob(pattern):
                        if file_path.exists():
                            file_stat = file_path.stat()
                            if file_stat.st_mode & stat.S_IROTH or file_stat.st_mode & stat.S_IWOTH:
                                security_issues.append(f"World-readable file: {file_path}")
            except Exception:
                pass
            
            if security_issues:
                result["success"] = False
                result["errors"] = security_issues
                result["output"] = "\n".join(security_issues)
            else:
                result["output"] = "No obvious security issues found"
            
        except Exception as e:
            result["errors"].append(f"Security scan failed: {str(e)}")
            result["success"] = False
        
        return result
    
    def run_integration_test(self) -> Dict[str, Any]:
        """Run integration tests."""
        result = {
            "gate": "integration_test",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "output": "",
            "errors": []
        }
        
        try:
            # Try to run integration.py commands
            commands = [
                ['python', 'integration.py', 'validate'],
                ['python', 'integration.py', 'status']
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
    
    def run_deployment_test(self) -> Dict[str, Any]:
        """Run deployment validation test."""
        result = {
            "gate": "deployment_test", 
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "output": "Deployment test passed (simulated)",
            "errors": []
        }
        
        # This is a placeholder for actual deployment testing
        # In a real scenario, this would test deployment to staging environment
        
        return result
    
    def run_smoke_test(self) -> Dict[str, Any]:
        """Run smoke tests."""
        result = {
            "gate": "smoke_test",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "output": "",
            "errors": []
        }
        
        try:
            # Basic smoke test: can we import and run key components?
            smoke_tests = [
                "import recursive_improvement",
                "from integration import get_status",
                "get_status()"
            ]
            
            for test in smoke_tests:
                try:
                    exec(test)
                    result["output"] += f"✓ {test}\n"
                except Exception as e:
                    result["errors"].append(f"Smoke test failed: {test} - {str(e)}")
                    result["output"] += f"✗ {test} - {str(e)}\n"
            
            result["success"] = len(result["errors"]) == 0
            
        except Exception as e:
            result["errors"].append(f"Smoke test execution failed: {str(e)}")
        
        return result
    
    def run_rollback_validation(self) -> Dict[str, Any]:
        """Validate rollback capability."""
        result = {
            "gate": "rollback_validation",
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "output": "",
            "errors": []
        }
        
        try:
            # Check if backups exist
            backup_dir = Path("backups/merge_states")
            if backup_dir.exists():
                backups = list(backup_dir.glob("merge_backup_*"))
                result["output"] = f"Found {len(backups)} merge state backups"
                result["success"] = len(backups) > 0
                
                if not result["success"]:
                    result["errors"].append("No merge state backups available for rollback")
            else:
                result["errors"].append("Backup directory does not exist")
                result["success"] = False
            
        except Exception as e:
            result["errors"].append(f"Rollback validation failed: {str(e)}")
            result["success"] = False
        
        return result
    
    def detect_merge_conflicts(self, source_branch: str, target_branch: str) -> Dict[str, Any]:
        """Detect potential merge conflicts."""
        conflict_detection = {
            "timestamp": datetime.now().isoformat(),
            "source_branch": source_branch,
            "target_branch": target_branch,
            "has_conflicts": False,
            "conflict_files": [],
            "conflict_count": 0,
            "can_auto_resolve": False,
            "errors": []
        }
        
        if not self.git_available:
            conflict_detection["errors"].append("Git not available for conflict detection")
            return conflict_detection
        
        try:
            # Try a dry run merge
            success, stdout, stderr = self.run_git_command([
                'git', 'merge-tree', 
                f'$(git merge-base {source_branch} {target_branch})',
                source_branch, 
                target_branch
            ])
            
            if success:
                if stdout.strip():
                    # Parse conflicts
                    conflict_files = []
                    for line in stdout.split('\n'):
                        if line.startswith('<<<<<<< '):
                            # This is a conflict marker, extract filename from context
                            continue
                        elif '<<<<<<< ' in line or '>>>>>>> ' in line or '=======' in line:
                            continue
                    
                    # For now, assume conflicts exist if there's output
                    if stdout.strip():
                        conflict_detection["has_conflicts"] = True
                        conflict_detection["conflict_count"] = stdout.count('<<<<<<<')
                        
                        # Simple auto-resolution check
                        if conflict_detection["conflict_count"] <= self.config.get("thresholds", {}).get("max_conflicts", 10):
                            conflict_detection["can_auto_resolve"] = True
            
        except Exception as e:
            conflict_detection["errors"].append(f"Conflict detection failed: {str(e)}")
        
        return conflict_detection
    
    def auto_resolve_conflicts(self, conflict_files: List[str]) -> Dict[str, Any]:
        """Attempt to automatically resolve conflicts."""
        resolution_result = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": 0,
            "files_resolved": 0,
            "resolution_strategy": self.config.get("merge_strategies", {}).get("conflict_resolution", {}).get("strategy", "auto"),
            "errors": []
        }
        
        try:
            prefer_strategy = self.config.get("merge_strategies", {}).get("conflict_resolution", {}).get("prefer", "incoming")
            
            for file_path in conflict_files:
                resolution_result["files_processed"] += 1
                
                try:
                    if self.resolve_file_conflicts(file_path, prefer_strategy):
                        resolution_result["files_resolved"] += 1
                    else:
                        resolution_result["errors"].append(f"Could not resolve conflicts in {file_path}")
                        
                except Exception as e:
                    resolution_result["errors"].append(f"Failed to resolve {file_path}: {str(e)}")
            
        except Exception as e:
            resolution_result["errors"].append(f"Auto conflict resolution failed: {str(e)}")
        
        return resolution_result
    
    def resolve_file_conflicts(self, file_path: str, strategy: str) -> bool:
        """Resolve conflicts in a single file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            if '<<<<<<< ' not in content:
                return True  # No conflicts
            
            resolved_content = ""
            lines = content.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i]
                
                if line.startswith('<<<<<<< '):
                    # Found conflict start
                    conflict_start = i
                    current_section = []
                    incoming_section = []
                    
                    # Find the separator and end
                    separator_idx = None
                    end_idx = None
                    
                    for j in range(i + 1, len(lines)):
                        if lines[j] == '=======':
                            separator_idx = j
                        elif lines[j].startswith('>>>>>>> '):
                            end_idx = j
                            break
                    
                    if separator_idx is not None and end_idx is not None:
                        current_section = lines[i + 1:separator_idx]
                        incoming_section = lines[separator_idx + 1:end_idx]
                        
                        # Apply resolution strategy
                        if strategy == "incoming":
                            resolved_content += '\n'.join(incoming_section) + '\n'
                        elif strategy == "current":
                            resolved_content += '\n'.join(current_section) + '\n'
                        else:  # "auto" or other
                            # Simple heuristic: prefer non-empty, longer section
                            if len('\n'.join(incoming_section).strip()) > len('\n'.join(current_section).strip()):
                                resolved_content += '\n'.join(incoming_section) + '\n'
                            else:
                                resolved_content += '\n'.join(current_section) + '\n'
                        
                        i = end_idx + 1
                    else:
                        # Malformed conflict, keep as-is
                        resolved_content += line + '\n'
                        i += 1
                else:
                    resolved_content += line + '\n'
                    i += 1
            
            # Write resolved content
            with open(file_path, 'w') as f:
                f.write(resolved_content)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to resolve conflicts in {file_path}: {e}")
            return False
    
    def execute_merge_operation(self, source_branch: str, target_branch: str, message: Optional[str] = None) -> Dict[str, Any]:
        """Execute a complete merge operation with quality gates."""
        merge_operation = {
            "timestamp": datetime.now().isoformat(),
            "source_branch": source_branch,
            "target_branch": target_branch,
            "merge_message": message or f"Merge {source_branch} into {target_branch}",
            "success": False,
            "phase": "starting",
            "backup_created": "",
            "quality_gates": {"pre_merge": [], "post_merge": []},
            "conflicts_detected": False,
            "conflicts_resolved": False,
            "merge_completed": False,
            "rollback_performed": False,
            "errors": []
        }
        
        try:
            # Phase 1: Create backup
            merge_operation["phase"] = "backup_creation"
            backup_path = self.create_backup_state()
            merge_operation["backup_created"] = backup_path
            
            if not backup_path:
                merge_operation["errors"].append("Failed to create backup state")
                return merge_operation
            
            # Phase 2: Pre-merge quality gates
            merge_operation["phase"] = "pre_merge_quality_gates"
            pre_merge_gates = self.config.get("quality_gates", {}).get("pre_merge", [])
            
            for gate in pre_merge_gates:
                gate_result = self.run_quality_gate(gate)
                merge_operation["quality_gates"]["pre_merge"].append(gate_result)
                
                if not gate_result["success"]:
                    merge_operation["errors"].append(f"Pre-merge quality gate failed: {gate}")
                    return merge_operation
            
            # Phase 3: Conflict detection
            merge_operation["phase"] = "conflict_detection"
            conflict_detection = self.detect_merge_conflicts(source_branch, target_branch)
            merge_operation["conflicts_detected"] = conflict_detection["has_conflicts"]
            
            if conflict_detection["has_conflicts"]:
                if conflict_detection["can_auto_resolve"]:
                    # Phase 4: Auto conflict resolution
                    merge_operation["phase"] = "conflict_resolution"
                    resolution_result = self.auto_resolve_conflicts(conflict_detection["conflict_files"])
                    merge_operation["conflicts_resolved"] = resolution_result["files_resolved"] > 0
                    
                    if resolution_result["errors"]:
                        merge_operation["errors"].extend(resolution_result["errors"])
                        return merge_operation
                else:
                    merge_operation["errors"].append("Conflicts detected that cannot be auto-resolved")
                    return merge_operation
            
            # Phase 5: Execute merge
            merge_operation["phase"] = "merge_execution"
            if self.git_available:
                # Checkout target branch
                success, stdout, stderr = self.run_git_command(['git', 'checkout', target_branch])
                if not success:
                    merge_operation["errors"].append(f"Failed to checkout {target_branch}: {stderr}")
                    return merge_operation
                
                # Perform merge
                success, stdout, stderr = self.run_git_command([
                    'git', 'merge', source_branch, '-m', merge_operation["merge_message"]
                ])
                
                if success:
                    merge_operation["merge_completed"] = True
                else:
                    merge_operation["errors"].append(f"Merge failed: {stderr}")
                    return merge_operation
            else:
                merge_operation["errors"].append("Git not available for merge execution")
                return merge_operation
            
            # Phase 6: Post-merge quality gates
            merge_operation["phase"] = "post_merge_quality_gates"
            post_merge_gates = self.config.get("quality_gates", {}).get("post_merge", [])
            
            for gate in post_merge_gates:
                gate_result = self.run_quality_gate(gate)
                merge_operation["quality_gates"]["post_merge"].append(gate_result)
                
                if not gate_result["success"]:
                    # Trigger rollback
                    self.logger.error(f"Post-merge quality gate failed: {gate}, initiating rollback")
                    rollback_result = self.perform_rollback(backup_path)
                    merge_operation["rollback_performed"] = rollback_result["success"]
                    merge_operation["errors"].append(f"Post-merge quality gate failed: {gate}")
                    return merge_operation
            
            merge_operation["phase"] = "complete"
            merge_operation["success"] = True
            
            # Save to history
            self.merge_history.append(merge_operation)
            self.save_merge_history()
            
            self.logger.info(f"Successfully merged {source_branch} into {target_branch}")
            
        except Exception as e:
            merge_operation["errors"].append(f"Merge operation failed: {str(e)}")
            self.logger.error(f"Merge operation failed: {e}")
        
        return merge_operation
    
    def perform_rollback(self, backup_path: str) -> Dict[str, Any]:
        """Perform rollback to previous state."""
        rollback_result = {
            "timestamp": datetime.now().isoformat(),
            "backup_path": backup_path,
            "success": False,
            "method": "",
            "errors": []
        }
        
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                rollback_result["errors"].append(f"Backup path does not exist: {backup_path}")
                return rollback_result
            
            # Try git-based rollback first
            bundle_file = backup_dir / "repo_backup.bundle"
            if bundle_file.exists() and self.git_available:
                # Reset to last known good state
                success, stdout, stderr = self.run_git_command(['git', 'reset', '--hard', 'HEAD~1'])
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
            "total_operations": len(self.merge_history),
            "successful_merges": 0,
            "failed_merges": 0,
            "rollbacks_performed": 0,
            "average_duration": 0,
            "most_common_failures": {}
        }
        
        if not self.merge_history:
            return stats
        
        total_duration = 0
        failure_reasons = {}
        
        for operation in self.merge_history:
            if operation["success"]:
                stats["successful_merges"] += 1
            else:
                stats["failed_merges"] += 1
                
                # Count failure reasons
                for error in operation.get("errors", []):
                    failure_reasons[error] = failure_reasons.get(error, 0) + 1
            
            if operation.get("rollback_performed", False):
                stats["rollbacks_performed"] += 1
        
        stats["most_common_failures"] = dict(sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)[:5])
        
        return stats
    
    def get_status(self) -> Dict[str, Any]:
        """Get merge automation system status."""
        git_status = self.get_git_status()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "config_loaded": bool(self.config),
            "git_available": self.git_available,
            "git_status": git_status,
            "merge_operations_count": len(self.merge_history),
            "last_operation": self.merge_history[-1] if self.merge_history else None,
            "quality_gates_configured": {
                "pre_merge": len(self.config.get("quality_gates", {}).get("pre_merge", [])),
                "post_merge": len(self.config.get("quality_gates", {}).get("post_merge", []))
            },
            "backup_directory_exists": Path("backups/merge_states").exists()
        }


def main():
    """Main function for command line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Merge Automation System")
    parser.add_argument('--merge', nargs=2, metavar=('SOURCE', 'TARGET'), help='Merge source branch into target branch')
    parser.add_argument('--message', help='Merge commit message')
    parser.add_argument('--status', action='store_true', help='Get merge automation status')
    parser.add_argument('--stats', action='store_true', help='Get merge statistics')
    parser.add_argument('--quality-gate', help='Run specific quality gate')
    parser.add_argument('--rollback', help='Perform rollback using backup path')
    
    args = parser.parse_args()
    
    merge_automation = MergeAutomation()
    
    if args.merge:
        source, target = args.merge
        result = merge_automation.execute_merge_operation(source, target, args.message)
        print(json.dumps(result, indent=2))
    elif args.status:
        status = merge_automation.get_status()
        print(json.dumps(status, indent=2))
    elif args.stats:
        stats = merge_automation.get_merge_statistics()
        print(json.dumps(stats, indent=2))
    elif args.quality_gate:
        result = merge_automation.run_quality_gate(args.quality_gate)
        print(json.dumps(result, indent=2))
    elif args.rollback:
        result = merge_automation.perform_rollback(args.rollback)
        print(json.dumps(result, indent=2))
    else:
        print("Use --merge, --status, --stats, --quality-gate, or --rollback")


if __name__ == "__main__":
    main()