"""
Autonomous Issue Analyzer Engine
Automatically analyzes issues with recursive improvement and compounding intelligence.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import logging
import re

from ..base import RecursiveEngine, CompoundingAction


class AutonomousIssueAnalyzerEngine(RecursiveEngine):
    """
    Autonomous Issue Analyzer Engine that recursively analyzes issues,
    identifies patterns, and suggests improvements.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("autonomous_issue_analyzer", config)
        self.issue_database = []
        self.pattern_catalog = {}
        self.analysis_metrics = {}
        self.priority_queue = []
        
    def initialize(self) -> bool:
        """Initialize the issue analyzer engine."""
        try:
            self.logger.info("Initializing Autonomous Issue Analyzer Engine")
            
            # Set up compounding actions
            analysis_action = CompoundingAction(
                name="issue_analysis_cycle",
                action=self.execute_main_action,
                interval=1.0,  # Weekly
                pre_action=self.execute_pre_action,
                pre_interval=0.25,  # +0.25 interval
                metadata={"type": "analysis", "autonomous": True}
            )
            
            self.add_compounding_action(analysis_action)
            
            # Initialize analysis metrics
            self.analysis_metrics = {
                "issues_analyzed": 0,
                "patterns_identified": 0,
                "improvements_suggested": 0,
                "recursive_cycles": 0
            }
            
            self.logger.info("Autonomous Issue Analyzer Engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize issue analyzer: {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute main issue analysis with recursive improvement."""
        self.logger.info("Executing autonomous issue analysis")
        
        result = {
            "action": "issue_analysis",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        try:
            # Analyze existing issues
            issues_processed = self._analyze_issues()
            
            # Identify recursive patterns
            patterns_found = self._identify_patterns()
            
            # Generate improvement suggestions
            improvements = self._generate_improvements()
            
            # Update priority queue with compounding logic
            self._update_priority_queue()
            
            result.update({
                "issues_processed": issues_processed,
                "patterns_identified": patterns_found,
                "improvements_suggested": len(improvements),
                "priority_items": len(self.priority_queue)
            })
            
            # Update metrics with compounding
            self.analysis_metrics["issues_analyzed"] += issues_processed
            self.analysis_metrics["patterns_identified"] += patterns_found
            self.analysis_metrics["improvements_suggested"] += len(improvements)
            self.analysis_metrics["recursive_cycles"] += 1
            
            self.logger.info(f"Issue analysis complete: {issues_processed} issues processed")
            return result
            
        except Exception as e:
            self.logger.error(f"Issue analysis failed: {e}")
            result["error"] = str(e)
            return result
    
    def execute_pre_action(self) -> Dict[str, Any]:
        """Execute pre-analysis scanning with overlap."""
        self.logger.info("Executing pre-analysis issue scanning")
        
        try:
            # Pre-scan for new issues
            new_issues = self._scan_for_issues()
            
            # Pre-process priority adjustments
            self._pre_adjust_priorities()
            
            return {
                "status": "pre-analysis_completed",
                "engine": self.name,
                "new_issues_detected": len(new_issues),
                "pre_adjustments": True
            }
            
        except Exception as e:
            self.logger.error(f"Pre-analysis error: {e}")
            return {"status": "pre-analysis_error", "error": str(e)}
    
    def _analyze_issues(self) -> int:
        """Analyze issues with recursive logic."""
        # Simulate issue analysis
        mock_issues = [
            {"id": 1, "type": "performance", "severity": "high", "description": "Slow query execution"},
            {"id": 2, "type": "security", "severity": "critical", "description": "Authentication bypass"},
            {"id": 3, "type": "usability", "severity": "medium", "description": "Confusing UI flow"}
        ]
        
        processed = 0
        for issue in mock_issues:
            # Recursive analysis: break down complex issues
            if self._is_complex_issue(issue):
                sub_issues = self._decompose_issue(issue)
                self.issue_database.extend(sub_issues)
                processed += len(sub_issues)
            else:
                self.issue_database.append(issue)
                processed += 1
        
        return processed
    
    def _identify_patterns(self) -> int:
        """Identify recursive patterns in issues."""
        patterns_found = 0
        
        # Group issues by type and severity
        issue_groups = {}
        for issue in self.issue_database[-10:]:  # Recent issues
            key = f"{issue.get('type', 'unknown')}_{issue.get('severity', 'unknown')}"
            if key not in issue_groups:
                issue_groups[key] = []
            issue_groups[key].append(issue)
        
        # Identify patterns with compounding logic
        for group_key, issues in issue_groups.items():
            if len(issues) >= 2:  # Pattern threshold
                pattern = {
                    "type": group_key,
                    "frequency": len(issues),
                    "impact": self._calculate_pattern_impact(issues),
                    "recursive_depth": self._calculate_recursion_depth(issues)
                }
                self.pattern_catalog[group_key] = pattern
                patterns_found += 1
        
        return patterns_found
    
    def _generate_improvements(self) -> List[Dict[str, Any]]:
        """Generate recursive improvement suggestions."""
        improvements = []
        
        for pattern_key, pattern in self.pattern_catalog.items():
            improvement = {
                "pattern": pattern_key,
                "suggestion": self._create_improvement_suggestion(pattern),
                "priority": self._calculate_improvement_priority(pattern),
                "recursive_potential": pattern.get("recursive_depth", 1),
                "compounding_factor": min(pattern["frequency"] * 0.1, 2.0)
            }
            improvements.append(improvement)
        
        return improvements
    
    def _scan_for_issues(self) -> List[Dict[str, Any]]:
        """Pre-scan for new issues with autonomous detection."""
        # Simulate autonomous issue detection
        return [
            {"id": f"auto_{datetime.now().strftime('%H%M%S')}", "auto_detected": True, "type": "performance"}
        ]
    
    def _pre_adjust_priorities(self):
        """Pre-adjust priorities with compounding logic."""
        if self.priority_queue:
            # Compound priority adjustments based on frequency
            for item in self.priority_queue[-5:]:  # Recent items
                item["priority"] = min(item.get("priority", 1.0) * 1.1, 5.0)
    
    def _update_priority_queue(self):
        """Update priority queue with recursive compounding."""
        current_time = datetime.now()
        
        # Add new priority items based on patterns
        for pattern_key, pattern in self.pattern_catalog.items():
            priority_item = {
                "pattern": pattern_key,
                "priority": pattern["frequency"] * pattern.get("recursive_depth", 1),
                "timestamp": current_time.isoformat(),
                "compounding_cycles": 1
            }
            self.priority_queue.append(priority_item)
        
        # Keep queue manageable size with compounding logic
        if len(self.priority_queue) > 50:
            # Sort by priority and keep top items
            self.priority_queue = sorted(
                self.priority_queue, 
                key=lambda x: x["priority"], 
                reverse=True
            )[:50]
    
    def _is_complex_issue(self, issue: Dict[str, Any]) -> bool:
        """Determine if issue requires recursive decomposition."""
        description = issue.get("description", "")
        complexity_keywords = ["integration", "system-wide", "cascade", "multiple"]
        return any(keyword in description.lower() for keyword in complexity_keywords)
    
    def _decompose_issue(self, issue: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recursively decompose complex issues."""
        base_id = issue["id"]
        return [
            {**issue, "id": f"{base_id}_sub1", "description": f"Sub-issue 1 of {issue['description']}"},
            {**issue, "id": f"{base_id}_sub2", "description": f"Sub-issue 2 of {issue['description']}"}
        ]
    
    def _calculate_pattern_impact(self, issues: List[Dict[str, Any]]) -> float:
        """Calculate pattern impact with recursive scaling."""
        severity_weights = {"critical": 5.0, "high": 3.0, "medium": 2.0, "low": 1.0}
        total_impact = sum(severity_weights.get(issue.get("severity", "low"), 1.0) for issue in issues)
        return total_impact * (1.0 + len(issues) * 0.1)  # Compounding factor
    
    def _calculate_recursion_depth(self, issues: List[Dict[str, Any]]) -> int:
        """Calculate recursion depth for pattern analysis."""
        max_depth = 1
        for issue in issues:
            if "sub" in str(issue.get("id", "")):
                depth = str(issue["id"]).count("sub") + 1
                max_depth = max(max_depth, depth)
        return max_depth
    
    def _create_improvement_suggestion(self, pattern: Dict[str, Any]) -> str:
        """Create recursive improvement suggestion."""
        suggestions = {
            "performance": "Implement recursive performance optimization with compounding caching",
            "security": "Deploy layered security with recursive validation",
            "usability": "Create adaptive UI with compounding user feedback loops"
        }
        
        pattern_type = pattern["type"].split("_")[0] if "_" in pattern["type"] else "general"
        base_suggestion = suggestions.get(pattern_type, "Implement recursive improvement pattern")
        
        return f"{base_suggestion} (Recursive depth: {pattern.get('recursive_depth', 1)})"
    
    def _calculate_improvement_priority(self, pattern: Dict[str, Any]) -> float:
        """Calculate improvement priority with compounding logic."""
        base_priority = pattern["impact"] * pattern["frequency"]
        recursive_multiplier = 1.0 + (pattern.get("recursive_depth", 1) - 1) * 0.2
        return min(base_priority * recursive_multiplier, 10.0)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return {
            "name": self.name,
            "is_running": self.is_running,
            "metrics": self.analysis_metrics,
            "issue_database_size": len(self.issue_database),
            "patterns_tracked": len(self.pattern_catalog),
            "priority_queue_size": len(self.priority_queue),
            "last_execution": self.last_execution
        }