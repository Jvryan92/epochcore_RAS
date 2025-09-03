#!/usr/bin/env python3
"""
Merge Automation - EpochCore RAS
Python-based robust merge logic for integrating changes into main branch
"""

import os
import json
import yaml
import subprocess
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MergeAutomation:
    """Automated merge system with robust conflict resolution."""
    
    def __init__(self, config_path: str = None, repo_path: str = "."):
        self.repo_path = Path(repo_path).resolve()
        self.config_path = config_path or "merge_config.yaml"
        self.logs_path = self.repo_path / "logs"
        self.backup_path = self.repo_path / "merge_backups"
        
        # Ensure directories exist
        self.logs_path.mkdir(exist_ok=True)
        self.backup_path.mkdir(exist_ok=True)
        
        self.config = self._load_config()
        self.merge_history = []
        
    def _load_config(self) -> Dict[str, Any]:
        """Load merge automation configuration."""
        default_config = {
            "merge_settings": {
                "auto_merge_enabled": True,
                "conflict_resolution_strategy": "smart",
                "backup_before_merge": True,
                "run_tests_before_merge": True,
                "create_merge_pr": True
            },
            "branch_settings": {
                "main_branch": "main",
                "development_branch": "develop",
                "feature_prefix": "feature/",
                "hotfix_prefix": "hotfix/",
                "protected_branches": ["main", "master", "production"]
            },
            "conflict_resolution": {
                "auto_resolve_simple": True,
                "prefer_incoming_for": ["*.md", "*.txt", "*.json"],
                "prefer_current_for": ["*.py", "*.yaml", "*.yml"],
                "manual_review_required": ["integration.py", "requirements.txt"],
                "merge_tools": ["git", "diff3"]
            },
            "quality_gates": {
                "run_linting": True,
                "run_unit_tests": True,
                "run_integration_tests": True,
                "security_scan": True,
                "performance_check": False
            },
            "notification_settings": {
                "notify_on_success": True,
                "notify_on_failure": True,
                "notify_on_conflicts": True,
                "webhook_url": None
            }
        }
        
        config_file = self.repo_path / self.config_path
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    default_config.update(loaded_config or {})
            except Exception as e:
                logger.warning(f"Error loading config: {e}. Using defaults.")
                
        return default_config
    
    def execute_automated_merge(self, source_branch: str, 
                              target_branch: str = None,
                              merge_strategy: str = None) -> Dict[str, Any]:
        """Execute automated merge with conflict resolution."""
        target_branch = target_branch or self.config["branch_settings"]["main_branch"]
        merge_strategy = merge_strategy or self.config["conflict_resolution_strategy"]
        
        logger.info(f"Starting automated merge: {source_branch} -> {target_branch}")
        
        merge_session = {
            "session_id": f"merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "source_branch": source_branch,
            "target_branch": target_branch,
            "strategy": merge_strategy,
            "start_time": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        try:
            # Pre-merge validation
            validation_result = self._pre_merge_validation(source_branch, target_branch)
            merge_session["pre_validation"] = validation_result
            
            if not validation_result["passed"]:
                merge_session["status"] = "failed"
                merge_session["error"] = "Pre-merge validation failed"
                return merge_session
            
            # Create backup if configured
            if self.config["merge_settings"]["backup_before_merge"]:
                backup_result = self._create_merge_backup(target_branch)
                merge_session["backup"] = backup_result
            
            # Execute merge
            merge_result = self._execute_merge_operation(source_branch, target_branch, merge_strategy)
            merge_session["merge_operation"] = merge_result
            
            if merge_result["status"] == "conflicts":
                # Handle conflicts
                conflict_resolution = self._resolve_conflicts(merge_result["conflicts"])
                merge_session["conflict_resolution"] = conflict_resolution
                
                if conflict_resolution["status"] != "resolved":
                    merge_session["status"] = "conflicts_unresolved"
                    return merge_session
            
            # Post-merge validation
            if merge_result["status"] in ["success", "conflicts_resolved"]:
                post_validation = self._post_merge_validation()
                merge_session["post_validation"] = post_validation
                
                if not post_validation["passed"]:
                    # Rollback if validation fails
                    rollback_result = self._rollback_merge(merge_session)
                    merge_session["rollback"] = rollback_result
                    merge_session["status"] = "rollback_completed"
                    return merge_session
            
            # Finalize merge
            finalization_result = self._finalize_merge(merge_session)
            merge_session["finalization"] = finalization_result
            merge_session["status"] = "completed"
            
            # Log merge operation
            self._log_merge_operation(merge_session)
            
            logger.info(f"Merge completed successfully: {source_branch} -> {target_branch}")
            
        except Exception as e:
            logger.error(f"Merge failed: {e}")
            merge_session["status"] = "error"
            merge_session["error"] = str(e)
            
            # Attempt rollback on error
            try:
                rollback_result = self._rollback_merge(merge_session)
                merge_session["rollback"] = rollback_result
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")
                merge_session["rollback_error"] = str(rollback_error)
        
        finally:
            merge_session["end_time"] = datetime.now().isoformat()
            self.merge_history.append(merge_session)
        
        return merge_session
    
    def _pre_merge_validation(self, source_branch: str, target_branch: str) -> Dict[str, Any]:
        """Validate conditions before merge."""
        logger.info("Running pre-merge validation")
        
        validation_result = {
            "passed": True,
            "checks": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check if branches exist
            source_exists = self._branch_exists(source_branch)
            target_exists = self._branch_exists(target_branch)
            
            validation_result["checks"]["source_branch_exists"] = source_exists
            validation_result["checks"]["target_branch_exists"] = target_exists
            
            if not source_exists:
                validation_result["errors"].append(f"Source branch does not exist: {source_branch}")
                validation_result["passed"] = False
            
            if not target_exists:
                validation_result["errors"].append(f"Target branch does not exist: {target_branch}")
                validation_result["passed"] = False
            
            # Check if target branch is protected
            if target_branch in self.config["branch_settings"]["protected_branches"]:
                validation_result["checks"]["target_protected"] = True
                validation_result["warnings"].append(f"Target branch is protected: {target_branch}")
            
            # Check for uncommitted changes
            uncommitted_changes = self._has_uncommitted_changes()
            validation_result["checks"]["clean_working_directory"] = not uncommitted_changes
            
            if uncommitted_changes:
                validation_result["errors"].append("Working directory has uncommitted changes")
                validation_result["passed"] = False
            
            # Check if source is ahead of target
            if source_exists and target_exists:
                commits_ahead = self._get_commits_ahead(source_branch, target_branch)
                validation_result["checks"]["commits_ahead"] = commits_ahead
                
                if commits_ahead == 0:
                    validation_result["warnings"].append("Source branch has no new commits")
            
            # Run quality gates if enabled
            if self.config["merge_settings"]["run_tests_before_merge"]:
                quality_result = self._run_quality_gates()
                validation_result["quality_gates"] = quality_result
                
                if not quality_result["passed"]:
                    validation_result["passed"] = False
                    validation_result["errors"].append("Quality gates failed")
            
        except Exception as e:
            logger.error(f"Pre-merge validation error: {e}")
            validation_result["passed"] = False
            validation_result["errors"].append(f"Validation error: {e}")
        
        return validation_result
    
    def _execute_merge_operation(self, source_branch: str, target_branch: str, 
                                strategy: str) -> Dict[str, Any]:
        """Execute the actual merge operation."""
        logger.info(f"Executing merge operation with strategy: {strategy}")
        
        merge_result = {
            "status": "unknown",
            "conflicts": [],
            "merged_files": [],
            "command_output": ""
        }
        
        try:
            # Ensure we're on the target branch
            self._run_git_command(["checkout", target_branch])
            
            # Pull latest changes
            self._run_git_command(["pull", "origin", target_branch])
            
            # Attempt merge
            merge_command = ["merge", source_branch]
            
            if strategy == "no-ff":
                merge_command.append("--no-ff")
            elif strategy == "squash":
                merge_command.append("--squash")
            elif strategy == "ff-only":
                merge_command.append("--ff-only")
            
            try:
                result = self._run_git_command(merge_command)
                merge_result["command_output"] = result
                merge_result["status"] = "success"
                
                # Get list of merged files
                merged_files = self._get_merged_files(source_branch, target_branch)
                merge_result["merged_files"] = merged_files
                
            except subprocess.CalledProcessError as e:
                if "conflict" in e.stderr.lower() or "merge conflict" in e.stderr.lower():
                    # Handle merge conflicts
                    conflicts = self._detect_conflicts()
                    merge_result["conflicts"] = conflicts
                    merge_result["status"] = "conflicts"
                    merge_result["command_output"] = e.stderr
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"Merge operation failed: {e}")
            merge_result["status"] = "error"
            merge_result["error"] = str(e)
        
        return merge_result
    
    def _resolve_conflicts(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve merge conflicts using configured strategy."""
        logger.info(f"Resolving {len(conflicts)} conflicts")
        
        resolution_result = {
            "status": "unknown",
            "resolved_conflicts": [],
            "unresolved_conflicts": [],
            "resolution_summary": {}
        }
        
        try:
            for conflict in conflicts:
                file_path = conflict["file"]
                conflict_type = conflict["type"]
                
                # Check if file requires manual review
                if self._requires_manual_review(file_path):
                    resolution_result["unresolved_conflicts"].append(conflict)
                    continue
                
                # Apply resolution strategy
                resolution_strategy = self._determine_resolution_strategy(file_path, conflict_type)
                
                if resolution_strategy == "prefer_incoming":
                    resolved = self._resolve_prefer_incoming(file_path)
                elif resolution_strategy == "prefer_current":
                    resolved = self._resolve_prefer_current(file_path)
                elif resolution_strategy == "smart_merge":
                    resolved = self._resolve_smart_merge(file_path, conflict)
                else:
                    resolved = False
                
                if resolved:
                    resolution_result["resolved_conflicts"].append({
                        "file": file_path,
                        "strategy": resolution_strategy,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Stage resolved file
                    self._run_git_command(["add", file_path])
                else:
                    resolution_result["unresolved_conflicts"].append(conflict)
            
            # Update status based on resolution results
            if len(resolution_result["unresolved_conflicts"]) == 0:
                resolution_result["status"] = "resolved"
                
                # Complete the merge
                self._run_git_command(["commit", "--no-edit"])
                
            elif len(resolution_result["resolved_conflicts"]) > 0:
                resolution_result["status"] = "partially_resolved"
            else:
                resolution_result["status"] = "unresolved"
            
            resolution_result["resolution_summary"] = {
                "total_conflicts": len(conflicts),
                "resolved": len(resolution_result["resolved_conflicts"]),
                "unresolved": len(resolution_result["unresolved_conflicts"])
            }
            
        except Exception as e:
            logger.error(f"Conflict resolution failed: {e}")
            resolution_result["status"] = "error"
            resolution_result["error"] = str(e)
        
        return resolution_result
    
    def _post_merge_validation(self) -> Dict[str, Any]:
        """Validate system after merge."""
        logger.info("Running post-merge validation")
        
        validation_result = {
            "passed": True,
            "checks": {},
            "errors": []
        }
        
        try:
            # Run quality gates
            if self.config["quality_gates"]["run_unit_tests"]:
                test_result = self._run_unit_tests()
                validation_result["checks"]["unit_tests"] = test_result
                
                if not test_result["passed"]:
                    validation_result["passed"] = False
                    validation_result["errors"].append("Unit tests failed")
            
            if self.config["quality_gates"]["run_linting"]:
                lint_result = self._run_linting()
                validation_result["checks"]["linting"] = lint_result
                
                if not lint_result["passed"]:
                    validation_result["passed"] = False
                    validation_result["errors"].append("Linting failed")
            
            if self.config["quality_gates"]["run_integration_tests"]:
                integration_result = self._run_integration_tests()
                validation_result["checks"]["integration_tests"] = integration_result
                
                if not integration_result["passed"]:
                    validation_result["passed"] = False
                    validation_result["errors"].append("Integration tests failed")
            
            # Check system integrity
            integrity_result = self._check_system_integrity()
            validation_result["checks"]["system_integrity"] = integrity_result
            
            if not integrity_result["passed"]:
                validation_result["passed"] = False
                validation_result["errors"].append("System integrity check failed")
            
        except Exception as e:
            logger.error(f"Post-merge validation error: {e}")
            validation_result["passed"] = False
            validation_result["errors"].append(f"Validation error: {e}")
        
        return validation_result
    
    def _finalize_merge(self, merge_session: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the merge operation."""
        logger.info("Finalizing merge operation")
        
        finalization_result = {
            "status": "completed",
            "actions_taken": []
        }
        
        try:
            target_branch = merge_session["target_branch"]
            
            # Push changes to remote
            self._run_git_command(["push", "origin", target_branch])
            finalization_result["actions_taken"].append("pushed_to_remote")
            
            # Create merge tag if configured
            if self.config["merge_settings"].get("create_merge_tags", False):
                tag_name = f"merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self._run_git_command(["tag", tag_name])
                self._run_git_command(["push", "origin", tag_name])
                finalization_result["actions_taken"].append(f"created_tag_{tag_name}")
            
            # Send notifications
            if self.config["notification_settings"]["notify_on_success"]:
                self._send_notification("merge_success", merge_session)
                finalization_result["actions_taken"].append("sent_success_notification")
            
            # Clean up backup if merge was successful
            if "backup" in merge_session and merge_session["backup"]["status"] == "created":
                # Keep backup for a short time, then clean up
                finalization_result["actions_taken"].append("backup_retained")
            
        except Exception as e:
            logger.error(f"Merge finalization error: {e}")
            finalization_result["status"] = "error"
            finalization_result["error"] = str(e)
        
        return finalization_result
    
    def _rollback_merge(self, merge_session: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback merge operation."""
        logger.info("Rolling back merge operation")
        
        rollback_result = {
            "status": "completed",
            "actions_taken": []
        }
        
        try:
            # Abort merge if in progress
            try:
                self._run_git_command(["merge", "--abort"])
                rollback_result["actions_taken"].append("aborted_merge")
            except subprocess.CalledProcessError:
                pass  # No merge in progress
            
            # Reset to previous state if backup exists
            if "backup" in merge_session and merge_session["backup"]["status"] == "created":
                backup_commit = merge_session["backup"]["commit_hash"]
                self._run_git_command(["reset", "--hard", backup_commit])
                rollback_result["actions_taken"].append("reset_to_backup")
            
            # Send failure notification
            if self.config["notification_settings"]["notify_on_failure"]:
                self._send_notification("merge_failure", merge_session)
                rollback_result["actions_taken"].append("sent_failure_notification")
            
        except Exception as e:
            logger.error(f"Rollback error: {e}")
            rollback_result["status"] = "error"
            rollback_result["error"] = str(e)
        
        return rollback_result
    
    # Helper methods
    def _branch_exists(self, branch_name: str) -> bool:
        """Check if branch exists."""
        try:
            self._run_git_command(["rev-parse", "--verify", f"refs/heads/{branch_name}"])
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _has_uncommitted_changes(self) -> bool:
        """Check for uncommitted changes."""
        try:
            result = self._run_git_command(["status", "--porcelain"])
            return len(result.strip()) > 0
        except Exception:
            return True  # Assume there are changes if we can't check
    
    def _get_commits_ahead(self, source_branch: str, target_branch: str) -> int:
        """Get number of commits source is ahead of target."""
        try:
            result = self._run_git_command(["rev-list", "--count", f"{target_branch}..{source_branch}"])
            return int(result.strip())
        except Exception:
            return 0
    
    def _run_quality_gates(self) -> Dict[str, Any]:
        """Run quality gate checks."""
        quality_result = {
            "passed": True,
            "checks": {}
        }
        
        try:
            if self.config["quality_gates"]["run_linting"]:
                lint_result = self._run_linting()
                quality_result["checks"]["linting"] = lint_result
                if not lint_result["passed"]:
                    quality_result["passed"] = False
            
            if self.config["quality_gates"]["run_unit_tests"]:
                test_result = self._run_unit_tests()
                quality_result["checks"]["unit_tests"] = test_result
                if not test_result["passed"]:
                    quality_result["passed"] = False
            
        except Exception as e:
            logger.error(f"Quality gates error: {e}")
            quality_result["passed"] = False
            quality_result["error"] = str(e)
        
        return quality_result
    
    def _run_linting(self) -> Dict[str, Any]:
        """Run linting checks."""
        try:
            result = subprocess.run(["flake8", "."], 
                                  capture_output=True, text=True, timeout=300)
            
            return {
                "passed": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    def _run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests."""
        try:
            result = subprocess.run(["python", "-m", "unittest", "discover", "tests/", "-v"], 
                                  capture_output=True, text=True, timeout=600)
            
            return {
                "passed": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        try:
            # Run integration.py validate
            result = subprocess.run(["python", "integration.py", "validate"], 
                                  capture_output=True, text=True, timeout=300)
            
            return {
                "passed": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr
            }
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    def _check_system_integrity(self) -> Dict[str, Any]:
        """Check system integrity after merge."""
        integrity_checks = {
            "passed": True,
            "checks": {}
        }
        
        try:
            # Check if critical files exist
            critical_files = ["integration.py", "requirements.txt", "README.md"]
            
            for file_name in critical_files:
                file_path = self.repo_path / file_name
                exists = file_path.exists()
                integrity_checks["checks"][f"{file_name}_exists"] = exists
                
                if not exists:
                    integrity_checks["passed"] = False
            
            # Check if agent_register_sync.py can be imported
            try:
                import agent_register_sync
                integrity_checks["checks"]["agent_sync_importable"] = True
            except ImportError:
                integrity_checks["checks"]["agent_sync_importable"] = False
                integrity_checks["passed"] = False
            
        except Exception as e:
            integrity_checks["passed"] = False
            integrity_checks["error"] = str(e)
        
        return integrity_checks
    
    def _create_merge_backup(self, branch_name: str) -> Dict[str, Any]:
        """Create backup before merge."""
        try:
            # Get current commit hash
            commit_hash = self._run_git_command(["rev-parse", "HEAD"]).strip()
            
            # Create backup tag
            backup_tag = f"backup_{branch_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self._run_git_command(["tag", backup_tag])
            
            return {
                "status": "created",
                "commit_hash": commit_hash,
                "backup_tag": backup_tag
            }
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect merge conflicts."""
        conflicts = []
        
        try:
            # Get list of conflicted files
            result = self._run_git_command(["diff", "--name-only", "--diff-filter=U"])
            conflicted_files = result.strip().split('\n') if result.strip() else []
            
            for file_path in conflicted_files:
                if file_path:  # Skip empty lines
                    conflict_info = {
                        "file": file_path,
                        "type": "content_conflict",
                        "detected_at": datetime.now().isoformat()
                    }
                    conflicts.append(conflict_info)
            
        except Exception as e:
            logger.error(f"Conflict detection failed: {e}")
        
        return conflicts
    
    def _requires_manual_review(self, file_path: str) -> bool:
        """Check if file requires manual review."""
        manual_review_files = self.config["conflict_resolution"]["manual_review_required"]
        
        for pattern in manual_review_files:
            if pattern in file_path:
                return True
        
        return False
    
    def _determine_resolution_strategy(self, file_path: str, conflict_type: str) -> str:
        """Determine resolution strategy for a conflict."""
        # Check prefer_incoming patterns
        for pattern in self.config["conflict_resolution"]["prefer_incoming_for"]:
            if file_path.endswith(pattern.replace("*", "")):
                return "prefer_incoming"
        
        # Check prefer_current patterns
        for pattern in self.config["conflict_resolution"]["prefer_current_for"]:
            if file_path.endswith(pattern.replace("*", "")):
                return "prefer_current"
        
        # Default to smart merge if auto resolution is enabled
        if self.config["conflict_resolution"]["auto_resolve_simple"]:
            return "smart_merge"
        
        return "manual"
    
    def _resolve_prefer_incoming(self, file_path: str) -> bool:
        """Resolve conflict by preferring incoming changes."""
        try:
            self._run_git_command(["checkout", "--theirs", file_path])
            return True
        except Exception as e:
            logger.error(f"Failed to resolve {file_path} with prefer_incoming: {e}")
            return False
    
    def _resolve_prefer_current(self, file_path: str) -> bool:
        """Resolve conflict by preferring current changes."""
        try:
            self._run_git_command(["checkout", "--ours", file_path])
            return True
        except Exception as e:
            logger.error(f"Failed to resolve {file_path} with prefer_current: {e}")
            return False
    
    def _resolve_smart_merge(self, file_path: str, conflict: Dict[str, Any]) -> bool:
        """Attempt smart merge resolution."""
        try:
            # This is a simplified smart merge - in practice, this would be more sophisticated
            # For now, we'll try to use git's merge tools
            merge_tools = self.config["conflict_resolution"]["merge_tools"]
            
            if "diff3" in merge_tools:
                # Use diff3 style merge
                self._run_git_command(["config", "merge.conflictstyle", "diff3"])
            
            # For simple cases, prefer incoming by default
            return self._resolve_prefer_incoming(file_path)
            
        except Exception as e:
            logger.error(f"Smart merge failed for {file_path}: {e}")
            return False
    
    def _get_merged_files(self, source_branch: str, target_branch: str) -> List[str]:
        """Get list of files that were merged."""
        try:
            result = self._run_git_command([
                "diff", "--name-only", 
                f"{target_branch}@{{1}}", target_branch
            ])
            return result.strip().split('\n') if result.strip() else []
        except Exception:
            return []
    
    def _run_git_command(self, command: List[str]) -> str:
        """Run git command and return output."""
        full_command = ["git"] + command
        
        result = subprocess.run(
            full_command,
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            error_msg = f"Git command failed: {' '.join(full_command)}\nError: {result.stderr}"
            raise subprocess.CalledProcessError(result.returncode, full_command, result.stderr)
        
        return result.stdout
    
    def _send_notification(self, notification_type: str, merge_session: Dict[str, Any]):
        """Send notification about merge operation."""
        try:
            webhook_url = self.config["notification_settings"].get("webhook_url")
            if webhook_url:
                # This would send actual notifications
                logger.info(f"Would send {notification_type} notification")
            else:
                logger.info(f"Notification: {notification_type} - {merge_session['session_id']}")
        except Exception as e:
            logger.error(f"Notification failed: {e}")
    
    def _log_merge_operation(self, merge_session: Dict[str, Any]):
        """Log merge operation."""
        try:
            log_file = self.logs_path / "merge_operations.log"
            with open(log_file, 'a') as f:
                f.write(json.dumps(merge_session, indent=2, default=str) + '\n\n')
        except Exception as e:
            logger.error(f"Failed to log merge operation: {e}")
    
    def get_merge_status(self) -> Dict[str, Any]:
        """Get current merge system status."""
        return {
            "merge_automation_enabled": self.config["merge_settings"]["auto_merge_enabled"],
            "total_merges": len(self.merge_history),
            "successful_merges": len([m for m in self.merge_history if m["status"] == "completed"]),
            "failed_merges": len([m for m in self.merge_history if m["status"] in ["error", "conflicts_unresolved"]]),
            "last_merge": self.merge_history[-1]["start_time"] if self.merge_history else "never"
        }

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Merge Automation System")
    parser.add_argument("--merge", nargs=2, metavar=("SOURCE", "TARGET"), 
                       help="Execute merge from source to target branch")
    parser.add_argument("--strategy", choices=["merge", "no-ff", "squash", "ff-only"],
                       default="merge", help="Merge strategy")
    parser.add_argument("--status", action="store_true", help="Show merge system status")
    parser.add_argument("--config", help="Config file path")
    parser.add_argument("--repo-path", default=".", help="Repository path")
    
    args = parser.parse_args()
    
    merge_automation = MergeAutomation(args.config, args.repo_path)
    
    if args.merge:
        source_branch, target_branch = args.merge
        result = merge_automation.execute_automated_merge(source_branch, target_branch, args.strategy)
        print(json.dumps(result, indent=2, default=str))
    elif args.status:
        status = merge_automation.get_merge_status()
        print(json.dumps(status, indent=2))
    else:
        print("Use --merge SOURCE TARGET to execute merge or --status to check system status")

if __name__ == "__main__":
    main()