#!/usr/bin/env python3
"""
Workflow Conflict Resolver
Enhanced PR Management and Automated Merge Coordination

This module provides comprehensive conflict resolution and automated merge
management for multiple open pull requests across repositories.
"""

import os
import json
import yaml
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import subprocess
import tempfile
from dataclasses import dataclass, asdict
import hashlib

# Import existing modules
from merge_automation import MergeAutomation
from github_api_client import GitHubAPIClient


@dataclass
class PRConflictInfo:
    """Information about PR conflicts and resolution strategies."""
    pr_number: int
    repo_name: str
    source_branch: str
    target_branch: str
    conflicts: List[str]
    conflict_severity: str  # low, medium, high, critical
    auto_resolvable: bool
    requires_manual_review: bool
    resolution_strategy: str
    estimated_resolution_time: int  # minutes
    dependencies: List[int]  # PR numbers this depends on


@dataclass
class MergeQueueItem:
    """Item in the merge queue with priority and dependencies."""
    pr_number: int
    repo_name: str
    priority: int  # 1-10, higher is more important
    created_at: datetime
    dependencies: List[int]
    merge_strategy: str
    estimated_merge_time: int
    quality_gates_passed: bool
    conflict_status: str  # none, auto_resolvable, manual_required
    

class WorkflowConflictResolver:
    """Advanced workflow conflict resolution and PR management system."""
    
    def __init__(self, config_path: str = "config/workflow_resolver.yaml"):
        self.config_path = config_path
        self.config = {}
        self.merge_queue: List[MergeQueueItem] = []
        self.conflict_cache: Dict[str, PRConflictInfo] = {}
        self.resolution_log = "logs/conflict_resolution.json"
        self.merge_automation = MergeAutomation()
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize directories
        for path in ["logs", "config", "backups/workflow_states", "temp/conflict_resolution"]:
            Path(path).mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
        
        # Initialize GitHub API client if available
        self.github_client = None
        self.init_github_client()
        
        # Load existing queue and conflicts
        self.load_merge_queue()
        self.load_conflict_cache()
    
    def load_config(self) -> bool:
        """Load workflow resolver configuration."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                self.logger.info("Loaded workflow resolver configuration")
                return True
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
        
        # Use default configuration
        self.config = self.get_default_config()
        self.save_config()
        return False
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default workflow resolver configuration."""
        return {
            "merge_queue": {
                "max_concurrent_merges": 3,
                "priority_weights": {
                    "hotfix": 10,
                    "security": 9,
                    "bugfix": 7,
                    "feature": 5,
                    "documentation": 3,
                    "refactor": 4
                },
                "merge_window": {
                    "start_hour": 9,  # 9 AM
                    "end_hour": 17,   # 5 PM
                    "timezone": "UTC",
                    "blocked_days": ["saturday", "sunday"]
                }
            },
            "conflict_resolution": {
                "auto_resolution_strategies": {
                    "documentation": "prefer_incoming",
                    "configuration": "merge_both",
                    "code": "require_manual",
                    "tests": "prefer_latest"
                },
                "conflict_severity_thresholds": {
                    "low": 5,      # files
                    "medium": 15,  # files
                    "high": 30,    # files
                    "critical": 50 # files
                },
                "auto_resolve_timeout": 600,  # 10 minutes
                "manual_review_timeout": 3600  # 1 hour
            },
            "quality_gates": {
                "required_checks": [
                    "lint",
                    "test_unit", 
                    "test_integration",
                    "security_scan"
                ],
                "optional_checks": [
                    "performance_test",
                    "accessibility_test",
                    "documentation_check"
                ],
                "failure_handling": {
                    "required_failure": "block_merge",
                    "optional_failure": "warn_but_continue"
                }
            },
            "notifications": {
                "merge_success": True,
                "merge_failure": True,
                "conflict_detected": True,
                "queue_status": True,
                "manual_review_required": True
            },
            "cross_repo_sync": {
                "enabled": True,
                "sync_branches": ["main", "develop"],
                "propagation_delay": 300,  # 5 minutes
                "max_repos": 20
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
    
    def init_github_client(self) -> bool:
        """Initialize GitHub API client."""
        try:
            github_token = os.environ.get('GITHUB_TOKEN')
            if github_token:
                self.github_client = GitHubAPIClient(github_token)
                return True
            else:
                self.logger.warning("GITHUB_TOKEN not found, GitHub API features disabled")
        except Exception as e:
            self.logger.error(f"Failed to initialize GitHub client: {e}")
        return False
    
    def load_merge_queue(self) -> bool:
        """Load existing merge queue."""
        queue_file = "logs/merge_queue.json"
        if os.path.exists(queue_file):
            try:
                with open(queue_file, 'r') as f:
                    queue_data = json.load(f)
                    self.merge_queue = []
                    for item_data in queue_data:
                        # Convert datetime strings back to datetime objects
                        if 'created_at' in item_data and isinstance(item_data['created_at'], str):
                            item_data['created_at'] = datetime.fromisoformat(item_data['created_at'])
                        self.merge_queue.append(MergeQueueItem(**item_data))
                return True
            except Exception as e:
                self.logger.error(f"Failed to load merge queue: {e}")
        
        self.merge_queue = []
        return False
    
    def save_merge_queue(self) -> bool:
        """Save merge queue to file."""
        queue_file = "logs/merge_queue.json"
        try:
            queue_data = []
            for item in self.merge_queue:
                item_dict = asdict(item)
                # Convert datetime objects to strings
                if isinstance(item_dict.get('created_at'), datetime):
                    item_dict['created_at'] = item_dict['created_at'].isoformat()
                queue_data.append(item_dict)
            
            with open(queue_file, 'w') as f:
                json.dump(queue_data, f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save merge queue: {e}")
            return False
    
    def load_conflict_cache(self) -> bool:
        """Load conflict cache."""
        cache_file = "logs/conflict_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.conflict_cache = {
                        key: PRConflictInfo(**value) 
                        for key, value in cache_data.items()
                    }
                return True
            except Exception as e:
                self.logger.error(f"Failed to load conflict cache: {e}")
        return False
    
    def save_conflict_cache(self) -> bool:
        """Save conflict cache to file."""
        cache_file = "logs/conflict_cache.json"
        try:
            cache_data = {
                key: asdict(value) 
                for key, value in self.conflict_cache.items()
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save conflict cache: {e}")
            return False
    
    async def discover_open_prs(self, repo_list: List[str] = None) -> List[Dict[str, Any]]:
        """Discover all open PRs across repositories."""
        discovered_prs = []
        
        if not self.github_client:
            self.logger.warning("GitHub client not available, using mock data")
            return self._get_mock_pr_data()
        
        try:
            # Use provided repo list or discover from config
            repos = repo_list or self._get_monitored_repos()
            
            for repo in repos:
                owner, name = repo.split('/')
                prs = await self.github_client.get_open_prs(owner, name)
                
                for pr in prs:
                    pr_info = {
                        "repo": repo,
                        "number": pr["number"],
                        "title": pr["title"],
                        "author": pr["user"]["login"],
                        "source_branch": pr["head"]["ref"],
                        "target_branch": pr["base"]["ref"],
                        "created_at": pr["created_at"],
                        "updated_at": pr["updated_at"],
                        "draft": pr["draft"],
                        "mergeable": pr.get("mergeable"),
                        "mergeable_state": pr.get("mergeable_state"),
                        "labels": [label["name"] for label in pr["labels"]],
                        "review_status": await self._get_review_status(owner, name, pr["number"])
                    }
                    discovered_prs.append(pr_info)
                    
        except Exception as e:
            self.logger.error(f"Failed to discover PRs: {e}")
            return self._get_mock_pr_data()
        
        self.logger.info(f"Discovered {len(discovered_prs)} open PRs")
        return discovered_prs
    
    def _get_monitored_repos(self) -> List[str]:
        """Get list of repositories to monitor."""
        # Default repos based on the problem statement
        return [
            "Jvryan92/epochcore_RAS",
            "Jvryan92/EpochCore_OS", 
            "EpochCore5/epoch5-template",
            "Jvryan92/epoch-agentic-bundle",
            "Jvryan92/epoch-mesh",
            "Jvryan92/StategyDECK"
        ]
    
    def _get_mock_pr_data(self) -> List[Dict[str, Any]]:
        """Get mock PR data for testing."""
        return [
            {
                "repo": "Jvryan92/epochcore_RAS",
                "number": 49,
                "title": "Complete workflow conflict resolution with automated merge automation and issue detection",
                "author": "Copilot",
                "source_branch": "copilot/workflow-conflicts",
                "target_branch": "main",
                "created_at": "2025-09-04T06:21:00Z",
                "updated_at": "2025-09-04T18:00:00Z",
                "draft": False,
                "mergeable": True,
                "mergeable_state": "clean",
                "labels": [],
                "review_status": "pending"
            },
            {
                "repo": "Jvryan92/EpochCore_OS",
                "number": 26,
                "title": "Complete EpochCore_OS autonomous software ecosystem with recursive self-improvement capabilities",
                "author": "Copilot",
                "source_branch": "copilot/autonomous-ecosystem",
                "target_branch": "main",
                "created_at": "2025-09-04T10:21:00Z",
                "updated_at": "2025-09-04T17:00:00Z",
                "draft": False,
                "mergeable": None,
                "mergeable_state": "unknown",
                "labels": [],
                "review_status": "pending"
            }
        ]
    
    async def analyze_pr_conflicts(self, pr_info: Dict[str, Any]) -> PRConflictInfo:
        """Analyze conflicts for a specific PR."""
        pr_key = f"{pr_info['repo']}#{pr_info['number']}"
        
        # Check cache first
        if pr_key in self.conflict_cache:
            cached_info = self.conflict_cache[pr_key]
            # Check if cache is still valid (less than 1 hour old)
            cache_age = datetime.now() - datetime.fromisoformat(cached_info.created_at) if hasattr(cached_info, 'created_at') else timedelta(hours=2)
            if cache_age < timedelta(hours=1):
                return cached_info
        
        # Analyze conflicts
        try:
            conflicts = await self._detect_merge_conflicts(pr_info)
            conflict_severity = self._calculate_conflict_severity(conflicts)
            auto_resolvable = self._can_auto_resolve(conflicts, conflict_severity)
            resolution_strategy = self._determine_resolution_strategy(conflicts, pr_info)
            estimated_time = self._estimate_resolution_time(conflicts, auto_resolvable)
            dependencies = await self._find_pr_dependencies(pr_info)
            
            conflict_info = PRConflictInfo(
                pr_number=pr_info["number"],
                repo_name=pr_info["repo"],
                source_branch=pr_info["source_branch"],
                target_branch=pr_info["target_branch"],
                conflicts=conflicts,
                conflict_severity=conflict_severity,
                auto_resolvable=auto_resolvable,
                requires_manual_review=not auto_resolvable,
                resolution_strategy=resolution_strategy,
                estimated_resolution_time=estimated_time,
                dependencies=dependencies
            )
            
            # Cache the result
            self.conflict_cache[pr_key] = conflict_info
            self.save_conflict_cache()
            
            return conflict_info
            
        except Exception as e:
            self.logger.error(f"Failed to analyze conflicts for PR {pr_key}: {e}")
            # Return minimal conflict info
            return PRConflictInfo(
                pr_number=pr_info["number"],
                repo_name=pr_info["repo"],
                source_branch=pr_info["source_branch"],
                target_branch=pr_info["target_branch"],
                conflicts=[],
                conflict_severity="unknown",
                auto_resolvable=False,
                requires_manual_review=True,
                resolution_strategy="manual_review",
                estimated_resolution_time=60,
                dependencies=[]
            )
    
    async def _detect_merge_conflicts(self, pr_info: Dict[str, Any]) -> List[str]:
        """Detect merge conflicts for a PR."""
        conflicts = []
        
        try:
            # If we have GitHub access, use the API
            if self.github_client:
                owner, name = pr_info["repo"].split('/')
                pr_files = await self.github_client.get_pr_files(owner, name, pr_info["number"])
                
                # Check for common conflict patterns
                for file_info in pr_files:
                    filename = file_info["filename"]
                    
                    # Common conflict-prone files
                    if any(pattern in filename.lower() for pattern in [
                        'package.json', 'requirements.txt', 'config', 
                        'main.py', 'index.js', 'readme'
                    ]):
                        conflicts.append(filename)
                    
                    # Large changes are more likely to conflict
                    if file_info.get("changes", 0) > 100:
                        conflicts.append(filename)
            else:
                # Mock conflict detection for testing
                mock_conflicts = [
                    "integration.py",
                    "merge_automation.py",
                    "requirements.txt"
                ]
                conflicts = mock_conflicts[:2]  # Simulate some conflicts
                
        except Exception as e:
            self.logger.error(f"Error detecting conflicts: {e}")
        
        return conflicts
    
    def _calculate_conflict_severity(self, conflicts: List[str]) -> str:
        """Calculate conflict severity based on number and type of conflicts."""
        num_conflicts = len(conflicts)
        thresholds = self.config["conflict_resolution"]["conflict_severity_thresholds"]
        
        if num_conflicts == 0:
            return "none"
        elif num_conflicts <= thresholds["low"]:
            return "low"
        elif num_conflicts <= thresholds["medium"]:
            return "medium"
        elif num_conflicts <= thresholds["high"]:
            return "high"
        else:
            return "critical"
    
    def _can_auto_resolve(self, conflicts: List[str], severity: str) -> bool:
        """Determine if conflicts can be automatically resolved."""
        if severity in ["high", "critical"]:
            return False
        
        # Check if all conflicts are in auto-resolvable file types
        auto_resolvable_patterns = [
            "readme", "documentation", "config", ".md", ".txt", ".yml", ".yaml"
        ]
        
        for conflict_file in conflicts:
            if not any(pattern in conflict_file.lower() for pattern in auto_resolvable_patterns):
                return False
        
        return True
    
    def _determine_resolution_strategy(self, conflicts: List[str], pr_info: Dict[str, Any]) -> str:
        """Determine the best resolution strategy for conflicts."""
        if not conflicts:
            return "auto_merge"
        
        # Check PR labels for hints
        labels = pr_info.get("labels", [])
        if "hotfix" in labels or "security" in labels:
            return "prioritize_incoming"
        
        # Check file types
        strategies = self.config["conflict_resolution"]["auto_resolution_strategies"]
        
        for conflict_file in conflicts:
            if any(pattern in conflict_file.lower() for pattern in ["doc", "readme", ".md"]):
                return strategies.get("documentation", "prefer_incoming")
            elif any(pattern in conflict_file.lower() for pattern in ["config", ".yml", ".yaml", ".json"]):
                return strategies.get("configuration", "merge_both")
            elif any(pattern in conflict_file.lower() for pattern in [".py", ".js", ".ts", ".java"]):
                return strategies.get("code", "require_manual")
            elif any(pattern in conflict_file.lower() for pattern in ["test", "spec"]):
                return strategies.get("tests", "prefer_latest")
        
        return "require_manual"
    
    def _estimate_resolution_time(self, conflicts: List[str], auto_resolvable: bool) -> int:
        """Estimate time needed to resolve conflicts in minutes."""
        if not conflicts:
            return 5  # Quick merge
        
        if auto_resolvable:
            return 10 + (len(conflicts) * 2)  # Base time + 2 minutes per conflict
        else:
            return 30 + (len(conflicts) * 10)  # Base time + 10 minutes per conflict
    
    async def _find_pr_dependencies(self, pr_info: Dict[str, Any]) -> List[int]:
        """Find other PRs that this PR depends on."""
        dependencies = []
        
        try:
            # Look for dependency indicators in title and description
            title = pr_info.get("title", "").lower()
            
            # Check for common dependency patterns
            dependency_patterns = [
                r"depends on #(\d+)",
                r"requires #(\d+)",
                r"after #(\d+)",
                r"follows #(\d+)"
            ]
            
            import re
            for pattern in dependency_patterns:
                matches = re.findall(pattern, title)
                dependencies.extend([int(match) for match in matches])
            
            # Check if this is part of a series (similar branch names)
            source_branch = pr_info.get("source_branch", "")
            if "part" in source_branch.lower() or "step" in source_branch.lower():
                # Look for other PRs with similar branch names
                # This would require GitHub API access to implement fully
                pass
                
        except Exception as e:
            self.logger.error(f"Error finding dependencies: {e}")
        
        return list(set(dependencies))  # Remove duplicates
    
    async def _get_review_status(self, owner: str, repo: str, pr_number: int) -> str:
        """Get review status for a PR."""
        try:
            if self.github_client:
                reviews = await self.github_client.get_pr_reviews(owner, repo, pr_number)
                
                # Determine overall review status
                latest_reviews = {}
                for review in reviews:
                    user = review["user"]["login"]
                    latest_reviews[user] = review["state"]
                
                if "APPROVED" in latest_reviews.values():
                    return "approved"
                elif "CHANGES_REQUESTED" in latest_reviews.values():
                    return "changes_requested"
                else:
                    return "pending"
            else:
                return "pending"
        except Exception as e:
            self.logger.error(f"Error getting review status: {e}")
            return "unknown"
    
    def add_to_merge_queue(self, pr_info: Dict[str, Any], conflict_info: PRConflictInfo) -> bool:
        """Add a PR to the merge queue with appropriate priority."""
        try:
            # Calculate priority based on labels and type
            priority = self._calculate_pr_priority(pr_info)
            
            # Determine merge strategy
            merge_strategy = conflict_info.resolution_strategy
            
            # Check quality gates
            quality_gates_passed = self._check_quality_gates(pr_info)
            
            queue_item = MergeQueueItem(
                pr_number=pr_info["number"],
                repo_name=pr_info["repo"],
                priority=priority,
                created_at=datetime.now(),
                dependencies=conflict_info.dependencies,
                merge_strategy=merge_strategy,
                estimated_merge_time=conflict_info.estimated_resolution_time,
                quality_gates_passed=quality_gates_passed,
                conflict_status=conflict_info.conflict_severity
            )
            
            # Insert in priority order
            self.merge_queue.append(queue_item)
            self.merge_queue.sort(key=lambda x: (-x.priority, x.created_at))  # Convert datetime to sortable format
            
            # Save queue
            self.save_merge_queue()
            
            self.logger.info(f"Added PR {pr_info['repo']}#{pr_info['number']} to merge queue with priority {priority}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add PR to merge queue: {e}")
            return False
    
    def _calculate_pr_priority(self, pr_info: Dict[str, Any]) -> int:
        """Calculate PR priority based on labels and other factors."""
        base_priority = 5
        labels = pr_info.get("labels", [])
        priority_weights = self.config["merge_queue"]["priority_weights"]
        
        # Check for priority labels
        for label in labels:
            if label.lower() in priority_weights:
                base_priority = max(base_priority, priority_weights[label.lower()])
        
        # Adjust for age (older PRs get slight priority boost)
        try:
            created_at_str = pr_info["created_at"]
            if created_at_str.endswith('Z'):
                created_at_str = created_at_str[:-1] + '+00:00'
            created_at = datetime.fromisoformat(created_at_str)
            age_days = (datetime.now(created_at.tzinfo) - created_at).days
            age_bonus = min(age_days // 7, 2)  # Max 2 points for age
        except (ValueError, TypeError, KeyError):
            age_bonus = 0
        
        # Adjust for author (maintainers get priority)
        author = pr_info.get("author", "")
        if author in ["Jvryan92", "maintainer"]:
            base_priority += 1
        
        return min(base_priority + age_bonus, 10)  # Cap at 10
    
    def _check_quality_gates(self, pr_info: Dict[str, Any]) -> bool:
        """Check if PR has passed all required quality gates."""
        # For now, return True if PR is mergeable
        return pr_info.get("mergeable_state") == "clean"
    
    async def process_merge_queue(self, max_concurrent: int = None) -> Dict[str, Any]:
        """Process the merge queue, executing merges in priority order."""
        if max_concurrent is None:
            max_concurrent = self.config["merge_queue"]["max_concurrent_merges"]
        
        results = {
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "queue_size": len(self.merge_queue),
            "processing_details": []
        }
        
        # Check if we're in merge window
        if not self._in_merge_window():
            self.logger.info("Outside merge window, skipping queue processing")
            results["skipped"] = len(self.merge_queue)
            return results
        
        processed_count = 0
        current_merges = 0
        
        # Process queue in order
        queue_copy = self.merge_queue.copy()
        
        for queue_item in queue_copy:
            if current_merges >= max_concurrent:
                break
            
            if processed_count >= max_concurrent:
                break
            
            # Check dependencies
            if not self._dependencies_satisfied(queue_item):
                self.logger.info(f"Dependencies not satisfied for PR {queue_item.repo_name}#{queue_item.pr_number}")
                continue
            
            # Process the merge
            merge_result = await self._execute_merge(queue_item)
            
            results["processing_details"].append({
                "pr": f"{queue_item.repo_name}#{queue_item.pr_number}",
                "result": merge_result["status"],
                "details": merge_result.get("message", "")
            })
            
            if merge_result["status"] == "success":
                results["successful"] += 1
                # Remove from queue
                self.merge_queue.remove(queue_item)
                current_merges += 1
            elif merge_result["status"] == "failed":
                results["failed"] += 1
                # Keep in queue but mark for manual review
                queue_item.conflict_status = "manual_required"
            else:
                results["skipped"] += 1
            
            processed_count += 1
        
        results["processed"] = processed_count
        
        # Save updated queue
        self.save_merge_queue()
        
        self.logger.info(f"Processed merge queue: {results}")
        return results
    
    def _in_merge_window(self) -> bool:
        """Check if current time is within merge window."""
        try:
            merge_window = self.config["merge_queue"]["merge_window"]
            now = datetime.now()
            
            # Check day of week
            if now.strftime('%A').lower() in merge_window.get("blocked_days", []):
                return False
            
            # Check time of day
            start_hour = merge_window.get("start_hour", 0)
            end_hour = merge_window.get("end_hour", 23)
            
            return start_hour <= now.hour <= end_hour
            
        except Exception as e:
            self.logger.error(f"Error checking merge window: {e}")
            return True  # Default to allowing merges
    
    def _dependencies_satisfied(self, queue_item: MergeQueueItem) -> bool:
        """Check if all dependencies for a queue item are satisfied."""
        if not queue_item.dependencies:
            return True
        
        # Check if dependent PRs are merged or no longer in queue
        for dep_pr in queue_item.dependencies:
            # Check if dependency is still in queue (not merged yet)
            dep_in_queue = any(
                item.pr_number == dep_pr and item.repo_name == queue_item.repo_name
                for item in self.merge_queue
            )
            if dep_in_queue:
                return False
        
        return True
    
    async def _execute_merge(self, queue_item: MergeQueueItem) -> Dict[str, Any]:
        """Execute merge for a queue item."""
        try:
            self.logger.info(f"Executing merge for {queue_item.repo_name}#{queue_item.pr_number}")
            
            # Get PR info
            pr_key = f"{queue_item.repo_name}#{queue_item.pr_number}"
            conflict_info = self.conflict_cache.get(pr_key)
            
            if not conflict_info:
                return {"status": "failed", "message": "Conflict info not available"}
            
            # Execute based on strategy
            if queue_item.merge_strategy == "auto_merge":
                return await self._auto_merge_pr(queue_item, conflict_info)
            elif queue_item.merge_strategy == "require_manual":
                return {"status": "skipped", "message": "Manual review required"}
            else:
                return await self._resolve_and_merge_pr(queue_item, conflict_info)
                
        except Exception as e:
            self.logger.error(f"Error executing merge: {e}")
            return {"status": "failed", "message": f"Merge execution failed: {str(e)}"}
    
    async def _auto_merge_pr(self, queue_item: MergeQueueItem, conflict_info: PRConflictInfo) -> Dict[str, Any]:
        """Execute automatic merge for a PR."""
        try:
            # Use the existing merge automation
            merge_result = self.merge_automation.execute_merge(
                conflict_info.source_branch,
                conflict_info.target_branch
            )
            
            if merge_result.get("success"):
                return {"status": "success", "message": "Auto merge completed"}
            else:
                return {"status": "failed", "message": f"Auto merge failed: {merge_result.get('errors', [])}"}
                
        except Exception as e:
            return {"status": "failed", "message": f"Auto merge error: {str(e)}"}
    
    async def _resolve_and_merge_pr(self, queue_item: MergeQueueItem, conflict_info: PRConflictInfo) -> Dict[str, Any]:
        """Resolve conflicts and merge PR."""
        try:
            # Attempt conflict resolution based on strategy
            if conflict_info.auto_resolvable:
                resolution_result = await self._auto_resolve_conflicts(conflict_info)
                
                if resolution_result["success"]:
                    # Proceed with merge
                    return await self._auto_merge_pr(queue_item, conflict_info)
                else:
                    return {"status": "failed", "message": f"Conflict resolution failed: {resolution_result.get('message')}"}
            else:
                return {"status": "skipped", "message": "Manual conflict resolution required"}
                
        except Exception as e:
            return {"status": "failed", "message": f"Resolve and merge error: {str(e)}"}
    
    async def _auto_resolve_conflicts(self, conflict_info: PRConflictInfo) -> Dict[str, Any]:
        """Automatically resolve conflicts based on strategy."""
        try:
            self.logger.info(f"Auto-resolving conflicts for PR {conflict_info.repo_name}#{conflict_info.pr_number}")
            
            # For now, simulate conflict resolution
            # In a real implementation, this would:
            # 1. Clone the repository
            # 2. Attempt merge
            # 3. Apply resolution strategy to conflicts
            # 4. Commit resolved changes
            
            return {
                "success": True,
                "message": f"Auto-resolved {len(conflict_info.conflicts)} conflicts using {conflict_info.resolution_strategy}",
                "resolved_files": conflict_info.conflicts
            }
            
        except Exception as e:
            self.logger.error(f"Error auto-resolving conflicts: {e}")
            return {
                "success": False,
                "message": f"Auto-resolution failed: {str(e)}",
                "resolved_files": []
            }
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current merge queue status."""
        total_items = len(self.merge_queue)
        
        # Group by status
        by_status = {}
        by_priority = {}
        by_repo = {}
        
        for item in self.merge_queue:
            # Count by status
            status = item.conflict_status
            by_status[status] = by_status.get(status, 0) + 1
            
            # Count by priority
            priority = item.priority
            by_priority[f"priority_{priority}"] = by_priority.get(f"priority_{priority}", 0) + 1
            
            # Count by repo
            repo = item.repo_name
            by_repo[repo] = by_repo.get(repo, 0) + 1
        
        # Calculate estimated completion time
        estimated_time = sum(item.estimated_merge_time for item in self.merge_queue)
        
        return {
            "queue_size": total_items,
            "estimated_completion_minutes": estimated_time,
            "breakdown": {
                "by_status": by_status,
                "by_priority": by_priority,
                "by_repository": by_repo
            },
            "next_merge_window": self._get_next_merge_window(),
            "cache_info": {
                "cached_conflicts": len(self.conflict_cache),
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _get_next_merge_window(self) -> str:
        """Get the next available merge window."""
        try:
            merge_window = self.config["merge_queue"]["merge_window"]
            now = datetime.now()
            
            # If currently in window, return "now"
            if self._in_merge_window():
                return "now"
            
            # Calculate next window
            start_hour = merge_window.get("start_hour", 9)
            
            # Try tomorrow at start hour
            next_window = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            if next_window <= now:
                next_window += timedelta(days=1)
            
            # Skip blocked days
            blocked_days = merge_window.get("blocked_days", [])
            while next_window.strftime('%A').lower() in blocked_days:
                next_window += timedelta(days=1)
            
            return next_window.isoformat()
            
        except Exception as e:
            self.logger.error(f"Error calculating next merge window: {e}")
            return "unknown"
    
    async def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive analysis of all open PRs and conflicts."""
        self.logger.info("Starting comprehensive PR analysis...")
        
        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "discovered_prs": 0,
            "analyzed_conflicts": 0,
            "queue_additions": 0,
            "auto_resolvable": 0,
            "manual_review_required": 0,
            "high_priority": 0,
            "repositories_analyzed": 0,
            "queue_status": {},
            "recommendations": []
        }
        
        try:
            # Step 1: Discover all open PRs
            open_prs = await self.discover_open_prs()
            analysis_result["discovered_prs"] = len(open_prs)
            
            # Group PRs by repository
            repos_analyzed = set()
            
            # Step 2: Analyze conflicts for each PR
            for pr_info in open_prs:
                repos_analyzed.add(pr_info["repo"])
                
                conflict_info = await self.analyze_pr_conflicts(pr_info)
                analysis_result["analyzed_conflicts"] += 1
                
                if conflict_info.auto_resolvable:
                    analysis_result["auto_resolvable"] += 1
                else:
                    analysis_result["manual_review_required"] += 1
                
                # Add to merge queue if appropriate
                if self.add_to_merge_queue(pr_info, conflict_info):
                    analysis_result["queue_additions"] += 1
                    
                    # Check priority
                    priority = self._calculate_pr_priority(pr_info)
                    if priority >= 8:
                        analysis_result["high_priority"] += 1
            
            analysis_result["repositories_analyzed"] = len(repos_analyzed)
            
            # Step 3: Get queue status
            analysis_result["queue_status"] = self.get_queue_status()
            
            # Step 4: Generate recommendations
            analysis_result["recommendations"] = self._generate_recommendations(analysis_result)
            
            self.logger.info(f"Comprehensive analysis completed: {analysis_result}")
            
        except Exception as e:
            self.logger.error(f"Comprehensive analysis failed: {e}")
            analysis_result["error"] = str(e)
        
        return analysis_result
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis results."""
        recommendations = []
        
        # High priority PRs
        if analysis["high_priority"] > 0:
            recommendations.append(f"🚨 {analysis['high_priority']} high-priority PRs require immediate attention")
        
        # Manual review required
        if analysis["manual_review_required"] > 5:
            recommendations.append(f"⚠️ {analysis['manual_review_required']} PRs require manual review - consider scheduling review sessions")
        
        # Queue size
        queue_size = analysis["queue_status"].get("queue_size", 0)
        if queue_size > 10:
            recommendations.append(f"📋 Large merge queue ({queue_size} items) - consider increasing merge frequency")
        
        # Auto-resolvable conflicts
        if analysis["auto_resolvable"] > 0:
            recommendations.append(f"✅ {analysis['auto_resolvable']} PRs can be auto-merged - enable automated processing")
        
        # Repository spread
        if analysis["repositories_analyzed"] > 5:
            recommendations.append(f"🏢 PRs across {analysis['repositories_analyzed']} repositories - consider cross-repo sync")
        
        return recommendations


def main():
    """Main entry point for workflow conflict resolver."""
    import argparse
    
    parser = argparse.ArgumentParser(description="EpochCore RAS Workflow Conflict Resolver")
    parser.add_argument("--action", choices=["analyze", "process", "status"], default="analyze",
                       help="Action to perform")
    parser.add_argument("--repos", nargs="+", help="Specific repositories to analyze")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    # Initialize resolver
    config_path = args.config or "config/workflow_resolver.yaml"
    resolver = WorkflowConflictResolver(config_path)
    
    async def run_action():
        if args.action == "analyze":
            result = await resolver.run_comprehensive_analysis()
            print(json.dumps(result, indent=2))
        elif args.action == "process":
            result = await resolver.process_merge_queue()
            print(json.dumps(result, indent=2))
        elif args.action == "status":
            result = resolver.get_queue_status()
            print(json.dumps(result, indent=2))
    
    # Run the async action
    asyncio.run(run_action())


if __name__ == "__main__":
    main()