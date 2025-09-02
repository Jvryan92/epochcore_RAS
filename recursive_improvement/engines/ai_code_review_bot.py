"""
AI Code Review Bot Engine - Recursive Autonomy Module
Self-evolving code review bot that learns from merged PRs and updates its review logic recursively
"""

from datetime import datetime
from typing import Dict, Any, List
import json
import logging
import os
import subprocess
import re

from ..base import RecursiveEngine, CompoundingAction


class AICodeReviewBotEngine(RecursiveEngine):
    """
    Self-evolving code review bot with recursive learning capabilities.
    Learns from merged PRs, updates review logic, and improves ML model recursively.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("ai_code_review_bot", config)
        self.review_history = []
        self.model_metrics = {}
        self.learned_patterns = {}
        self.review_rules = self._load_default_review_rules()
        
    def initialize(self) -> bool:
        """Initialize the AI code review bot engine."""
        try:
            self.logger.info("Initializing AI Code Review Bot Engine")
            
            # Set up compounding actions
            review_action = CompoundingAction(
                name="code_review_learning",
                action=self.execute_main_action,
                interval=0.1,  # Continuous (every PR)
                pre_action=self.execute_pre_action,
                pre_interval=0.25,  # Pre-scan at +0.25 interval
                metadata={"type": "code_review", "recursive": True}
            )
            
            self.add_compounding_action(review_action)
            
            # Initialize metrics tracking
            self.model_metrics = {
                "reviews_performed": 0,
                "patterns_learned": 0,
                "model_updates": 0,
                "accuracy_score": 0.0,
                "false_positives": 0,
                "false_negatives": 0
            }
            
            self.logger.info("AI Code Review Bot Engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI Code Review Bot: {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute main code review learning and model update."""
        try:
            self.logger.info("Executing AI code review learning cycle")
            
            # Analyze recent merged PRs for learning
            merged_prs = self._get_recent_merged_prs()
            learned_patterns = self._analyze_merged_prs(merged_prs)
            
            # Update review logic based on learning
            updated_rules = self._update_review_rules(learned_patterns)
            
            # Update ML model if significant patterns found
            model_updated = False
            if len(learned_patterns) > 5:  # Threshold for model update
                model_updated = self._update_ml_model(learned_patterns)
                
            # Apply reviews to current open PRs
            reviewed_prs = self._review_open_prs()
            
            # Update metrics
            self.model_metrics["reviews_performed"] += len(reviewed_prs)
            self.model_metrics["patterns_learned"] += len(learned_patterns)
            if model_updated:
                self.model_metrics["model_updates"] += 1
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "action": "code_review_learning",
                "merged_prs_analyzed": len(merged_prs),
                "patterns_learned": len(learned_patterns),
                "rules_updated": len(updated_rules),
                "model_updated": model_updated,
                "prs_reviewed": len(reviewed_prs),
                "metrics": self.model_metrics
            }
            
            self.review_history.append(result)
            self.logger.info(f"Code review cycle completed: {len(merged_prs)} PRs analyzed, {len(reviewed_prs)} PRs reviewed")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in code review learning cycle: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "code_review_learning",
                "error": str(e),
                "status": "failed"
            }
    
    def execute_pre_action(self) -> Dict[str, Any]:
        """Execute pre-action: scan for new PRs and prepare review context."""
        try:
            self.logger.info("Pre-scanning for new PRs and preparing review context")
            
            # Quick scan for new PRs
            new_prs = self._scan_new_prs()
            
            # Pre-load review context
            context_prepared = self._prepare_review_context(new_prs)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "pr_pre_scan",
                "new_prs_found": len(new_prs),
                "context_prepared": context_prepared,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"Error in pre-action scan: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "pr_pre_scan", 
                "error": str(e),
                "status": "failed"
            }
    
    def _load_default_review_rules(self) -> Dict[str, Any]:
        """Load default code review rules."""
        return {
            "security_patterns": [
                r"password\s*=",
                r"api_key\s*=", 
                r"secret\s*=",
                r"token\s*=",
                r"eval\(",
                r"exec\(",
                r"__import__"
            ],
            "quality_patterns": [
                r"# TODO",
                r"# FIXME", 
                r"# HACK",
                r"print\(",
                r"console\.log\(",
                r"debugger"
            ],
            "performance_patterns": [
                r"\.sleep\(",
                r"time\.sleep\(",
                r"while True:",
                r"for.*in.*range\(.*\):"
            ],
            "style_patterns": [
                r"^[ ]*[^ ].*[^ ][ ]*$",  # Trailing whitespace
                r"^.{120,}",  # Long lines
            ]
        }
    
    def _get_recent_merged_prs(self) -> List[Dict[str, Any]]:
        """Get recently merged PRs for learning analysis."""
        # Simulate GitHub API call - in real implementation would use GitHub API
        return [
            {
                "id": "pr_123",
                "title": "Fix security vulnerability in auth",
                "files_changed": ["auth.py", "middleware.py"],
                "review_comments": ["Good security fix", "LGTM"],
                "merged_at": "2024-01-15T10:30:00Z"
            },
            {
                "id": "pr_124", 
                "title": "Refactor database queries",
                "files_changed": ["models.py", "queries.py"],
                "review_comments": ["Performance improvement", "Clean code"],
                "merged_at": "2024-01-14T14:20:00Z"
            }
        ]
    
    def _analyze_merged_prs(self, merged_prs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze merged PRs to learn patterns."""
        patterns = {}
        
        for pr in merged_prs:
            # Extract patterns from successful reviews
            if "security" in pr["title"].lower():
                patterns["security_fixes"] = patterns.get("security_fixes", 0) + 1
            if "refactor" in pr["title"].lower():
                patterns["refactor_patterns"] = patterns.get("refactor_patterns", 0) + 1
            if "performance" in pr["title"].lower():
                patterns["performance_improvements"] = patterns.get("performance_improvements", 0) + 1
                
        return patterns
    
    def _update_review_rules(self, patterns: Dict[str, Any]) -> List[str]:
        """Update review rules based on learned patterns."""
        updated_rules = []
        
        # Add new security patterns if security fixes are common
        if patterns.get("security_fixes", 0) > 2:
            new_security_pattern = r"hardcoded.*credential"
            if new_security_pattern not in self.review_rules["security_patterns"]:
                self.review_rules["security_patterns"].append(new_security_pattern)
                updated_rules.append("security_pattern_added")
                
        # Add performance patterns if performance improvements are common  
        if patterns.get("performance_improvements", 0) > 1:
            new_perf_pattern = r"\.join\(\)"
            if new_perf_pattern not in self.review_rules["performance_patterns"]:
                self.review_rules["performance_patterns"].append(new_perf_pattern)
                updated_rules.append("performance_pattern_added")
                
        return updated_rules
    
    def _update_ml_model(self, patterns: Dict[str, Any]) -> bool:
        """Update ML model based on learned patterns."""
        try:
            # Simulate ML model update
            self.logger.info("Updating ML model with new patterns")
            
            # In real implementation, this would:
            # 1. Retrain model with new data
            # 2. Update feature weights
            # 3. Validate model performance
            # 4. Deploy updated model
            
            self.learned_patterns.update(patterns)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update ML model: {e}")
            return False
    
    def _scan_new_prs(self) -> List[Dict[str, Any]]:
        """Scan for new PRs requiring review."""
        # Simulate GitHub API call
        return [
            {
                "id": "pr_125",
                "title": "Add new authentication method", 
                "author": "developer1",
                "created_at": "2024-01-16T09:00:00Z",
                "status": "open"
            }
        ]
    
    def _prepare_review_context(self, prs: List[Dict[str, Any]]) -> bool:
        """Prepare review context for upcoming PRs."""
        try:
            # Pre-load context, analyze code changes, prepare review templates
            for pr in prs:
                context = {
                    "pr_id": pr["id"],
                    "title": pr["title"],
                    "risk_level": self._assess_risk_level(pr["title"]),
                    "review_template": self._generate_review_template(pr["title"])
                }
                # Store context for later use
                
            return True
        except Exception as e:
            self.logger.error(f"Failed to prepare review context: {e}")
            return False
    
    def _review_open_prs(self) -> List[Dict[str, Any]]:
        """Review open PRs using current rules and ML model."""
        reviewed_prs = []
        
        # Get open PRs
        open_prs = self._scan_new_prs()
        
        for pr in open_prs:
            review_result = self._perform_code_review(pr)
            reviewed_prs.append(review_result)
            
        return reviewed_prs
    
    def _perform_code_review(self, pr: Dict[str, Any]) -> Dict[str, Any]:
        """Perform automated code review on a PR."""
        try:
            # Simulate code review process
            review_comments = []
            risk_score = 0
            
            # Check against security patterns
            if "auth" in pr["title"].lower():
                review_comments.append("⚠️ Authentication changes detected - ensure security best practices")
                risk_score += 2
                
            # Check against quality patterns  
            if "fix" in pr["title"].lower():
                review_comments.append("✅ Bug fix - verify test coverage")
                risk_score += 1
                
            # Generate overall recommendation
            recommendation = "APPROVE" if risk_score < 3 else "REQUEST_CHANGES"
            
            return {
                "pr_id": pr["id"],
                "review_comments": review_comments,
                "risk_score": risk_score,
                "recommendation": recommendation,
                "reviewed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error reviewing PR {pr['id']}: {e}")
            return {
                "pr_id": pr["id"],
                "error": str(e),
                "recommendation": "MANUAL_REVIEW_REQUIRED"
            }
    
    def _assess_risk_level(self, title: str) -> str:
        """Assess risk level of a PR based on title."""
        high_risk_keywords = ["security", "auth", "password", "token", "admin"]
        medium_risk_keywords = ["database", "api", "config", "deploy"]
        
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in high_risk_keywords):
            return "HIGH"
        elif any(keyword in title_lower for keyword in medium_risk_keywords):
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_review_template(self, title: str) -> str:
        """Generate review template based on PR title."""
        risk_level = self._assess_risk_level(title)
        
        if risk_level == "HIGH":
            return "Security review template: Check for hardcoded secrets, validate input sanitization"
        elif risk_level == "MEDIUM":
            return "Standard review template: Check code quality, test coverage, performance"
        else:
            return "Basic review template: Check style, documentation, basic functionality"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the AI code review bot."""
        return {
            "name": self.name,
            "running": self.is_running,
            "metrics": self.model_metrics,
            "learned_patterns_count": len(self.learned_patterns),
            "review_rules_count": sum(len(rules) for rules in self.review_rules.values()),
            "last_execution": self.last_execution,
            "total_executions": len(self.execution_history)
        }