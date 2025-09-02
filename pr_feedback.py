#!/usr/bin/env python3
"""
EpochCore RAS PR Feedback Loop System
Implements recursive pull request feedback loops for continuous improvement
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PRFeedbackLoop:
    """
    PR feedback loop system that continuously analyzes code changes
    and suggests improvements until no further enhancements are detected.
    """
    
    def __init__(self):
        self.feedback_history = []
        self.improvement_suggestions = []
        self.feedback_patterns = {}
        self.max_feedback_cycles = 5
        
        # Initialize feedback analyzers
        self._setup_feedback_analyzers()
        
        logger.info("PR Feedback Loop system initialized")
    
    def process_feedback(self) -> Dict[str, Any]:
        """
        Process current state and generate improvement suggestions
        based on accumulated feedback patterns.
        """
        logger.info("Processing PR feedback and generating improvements")
        
        try:
            # Analyze current codebase state
            codebase_analysis = self._analyze_codebase()
            
            # Generate feedback based on analysis
            feedback_items = self._generate_feedback(codebase_analysis)
            
            # Create improvement suggestions from feedback
            improvements = self._feedback_to_improvements(feedback_items)
            
            # Update feedback history
            feedback_result = {
                "feedback_processed": len(feedback_items) > 0,
                "improvements": improvements,
                "feedback_items": feedback_items,
                "codebase_analysis": codebase_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            self.feedback_history.append(feedback_result)
            
            # Trim history to last 50 entries
            if len(self.feedback_history) > 50:
                self.feedback_history = self.feedback_history[-50:]
            
            logger.info(f"PR feedback processing completed: {len(improvements)} improvements generated")
            return feedback_result
            
        except Exception as e:
            logger.error(f"Error processing PR feedback: {str(e)}")
            return {
                "feedback_processed": False,
                "improvements": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def simulate_pr_review(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate a PR review process with feedback generation.
        In a real implementation, this would integrate with GitHub API.
        """
        logger.info("Simulating PR review process")
        
        try:
            review_comments = []
            suggestions = []
            
            # Analyze different aspects of the changes
            if "files_changed" in changes:
                for file_change in changes["files_changed"]:
                    file_feedback = self._review_file_changes(file_change)
                    review_comments.extend(file_feedback["comments"])
                    suggestions.extend(file_feedback["suggestions"])
            
            # Generate overall PR feedback
            overall_feedback = self._generate_overall_pr_feedback(changes, review_comments)
            
            review_result = {
                "review_completed": True,
                "comments": review_comments,
                "suggestions": suggestions,
                "overall_feedback": overall_feedback,
                "approval_status": self._determine_approval_status(review_comments),
                "timestamp": datetime.now().isoformat()
            }
            
            return review_result
            
        except Exception as e:
            logger.error(f"Error in PR review simulation: {str(e)}")
            return {
                "review_completed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _setup_feedback_analyzers(self):
        """Setup feedback analysis patterns and rules."""
        self.feedback_patterns = {
            "code_quality": {
                "patterns": [
                    r"def\s+[a-zA-Z_]\w*\([^)]*\):\s*$",  # Functions without docstrings
                    r"class\s+[a-zA-Z_]\w*.*:\s*$",       # Classes without docstrings
                    r"^\s*#\s*TODO",                       # TODO comments
                    r"^\s*#\s*FIXME",                      # FIXME comments
                    r"^\s*#\s*HACK",                       # HACK comments
                ],
                "weight": 1.0
            },
            "security": {
                "patterns": [
                    r"eval\(",                             # eval() usage
                    r"exec\(",                             # exec() usage
                    r"subprocess\.call\(",                 # subprocess without shell=False
                    r"os\.system\(",                       # os.system() usage
                    r"input\(",                            # input() without validation
                ],
                "weight": 2.0
            },
            "performance": {
                "patterns": [
                    r"for\s+\w+\s+in\s+range\(len\(",    # range(len()) anti-pattern
                    r"\.append\(\)\s*$",                   # list.append in loops
                    r"re\.compile\(",                      # regex compilation in loops
                    r"\+\s*=.*\+",                         # String concatenation in loops
                ],
                "weight": 1.5
            },
            "maintainability": {
                "patterns": [
                    r"def\s+\w+.*:\s*\n(\s*.*\n){20,}",   # Very long functions
                    r"if.*:\s*\n(\s*if.*:\s*\n){3,}",     # Deeply nested if statements
                    r"try:\s*\n(\s*.*\n)*?\s*except:",    # Broad exception handling
                ],
                "weight": 1.2
            }
        }
    
    def _analyze_codebase(self) -> Dict[str, Any]:
        """Analyze current codebase for feedback generation."""
        try:
            import os
            
            analysis = {
                "files_analyzed": 0,
                "total_lines": 0,
                "issues_found": [],
                "metrics": {},
                "patterns_detected": {}
            }
            
            # Analyze Python files
            for root, dirs, files in os.walk("."):
                # Skip virtual environments and cache directories
                dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        file_analysis = self._analyze_file_for_feedback(file_path)
                        
                        analysis["files_analyzed"] += 1
                        analysis["total_lines"] += file_analysis.get("line_count", 0)
                        analysis["issues_found"].extend(file_analysis.get("issues", []))
                        
                        # Merge pattern detections
                        for pattern_type, count in file_analysis.get("patterns", {}).items():
                            if pattern_type not in analysis["patterns_detected"]:
                                analysis["patterns_detected"][pattern_type] = 0
                            analysis["patterns_detected"][pattern_type] += count
            
            # Calculate metrics
            analysis["metrics"] = {
                "average_issues_per_file": (
                    len(analysis["issues_found"]) / analysis["files_analyzed"] 
                    if analysis["files_analyzed"] > 0 else 0
                ),
                "total_pattern_matches": sum(analysis["patterns_detected"].values())
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing codebase: {str(e)}")
            return {
                "files_analyzed": 0,
                "total_lines": 0,
                "issues_found": [],
                "error": str(e)
            }
    
    def _analyze_file_for_feedback(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for feedback patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            line_count = len(lines)
            
            file_analysis = {
                "file_path": file_path,
                "line_count": line_count,
                "issues": [],
                "patterns": {}
            }
            
            # Check each feedback pattern
            for pattern_category, pattern_config in self.feedback_patterns.items():
                pattern_matches = 0
                
                for pattern in pattern_config["patterns"]:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        file_analysis["issues"].append({
                            "type": pattern_category,
                            "pattern": pattern,
                            "line": line_num,
                            "message": self._get_pattern_message(pattern_category, pattern),
                            "weight": pattern_config["weight"]
                        })
                        
                        pattern_matches += 1
                
                file_analysis["patterns"][pattern_category] = pattern_matches
            
            return file_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return {"file_path": file_path, "issues": [], "patterns": {}}
    
    def _get_pattern_message(self, pattern_category: str, pattern: str) -> str:
        """Get human-readable message for a pattern match."""
        messages = {
            "code_quality": {
                r"def\s+[a-zA-Z_]\w*\([^)]*\):\s*$": "Function missing docstring",
                r"class\s+[a-zA-Z_]\w*.*:\s*$": "Class missing docstring", 
                r"^\s*#\s*TODO": "TODO comment should be addressed",
                r"^\s*#\s*FIXME": "FIXME comment should be addressed",
                r"^\s*#\s*HACK": "HACK comment indicates code smell"
            },
            "security": {
                r"eval\(": "Avoid using eval() - security risk",
                r"exec\(": "Avoid using exec() - security risk",
                r"subprocess\.call\(": "Use subprocess with shell=False for security",
                r"os\.system\(": "Avoid os.system() - use subprocess instead",
                r"input\(": "Validate input() for security"
            },
            "performance": {
                r"for\s+\w+\s+in\s+range\(len\(": "Use enumerate() instead of range(len())",
                r"\.append\(\)\s*$": "Consider list comprehension for better performance",
                r"re\.compile\(": "Compile regex outside of loops",
                r"\+\s*=.*\+": "Use join() for string concatenation in loops"
            },
            "maintainability": {
                r"def\s+\w+.*:\s*\n(\s*.*\n){20,}": "Function is too long - consider breaking it up",
                r"if.*:\s*\n(\s*if.*:\s*\n){3,}": "Deeply nested conditions - consider refactoring",
                r"try:\s*\n(\s*.*\n)*?\s*except:": "Avoid broad exception handling"
            }
        }
        
        category_messages = messages.get(pattern_category, {})
        return category_messages.get(pattern, f"Pattern detected: {pattern_category}")
    
    def _generate_feedback(self, codebase_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate feedback items from codebase analysis."""
        feedback_items = []
        
        issues = codebase_analysis.get("issues_found", [])
        
        # Group issues by type and priority
        issue_groups = {}
        for issue in issues:
            issue_type = issue["type"]
            if issue_type not in issue_groups:
                issue_groups[issue_type] = []
            issue_groups[issue_type].append(issue)
        
        # Generate feedback for each issue group
        for issue_type, type_issues in issue_groups.items():
            if len(type_issues) >= 1:  # Generate feedback if we have issues
                feedback_items.append({
                    "category": issue_type,
                    "priority": self._get_feedback_priority(issue_type),
                    "issue_count": len(type_issues),
                    "summary": self._generate_feedback_summary(issue_type, len(type_issues)),
                    "specific_issues": type_issues[:5],  # Show up to 5 specific examples
                    "recommendation": self._get_feedback_recommendation(issue_type)
                })
        
        # Sort by priority
        feedback_items.sort(key=lambda x: x["priority"], reverse=True)
        
        return feedback_items
    
    def _get_feedback_priority(self, issue_type: str) -> float:
        """Get priority score for feedback type."""
        priorities = {
            "security": 3.0,
            "maintainability": 2.0,
            "performance": 1.5,
            "code_quality": 1.0
        }
        return priorities.get(issue_type, 1.0)
    
    def _generate_feedback_summary(self, issue_type: str, count: int) -> str:
        """Generate summary message for feedback type."""
        summaries = {
            "security": f"Found {count} security-related issues that should be addressed",
            "maintainability": f"Found {count} maintainability issues that could make code harder to maintain",
            "performance": f"Found {count} performance issues that could affect system efficiency",
            "code_quality": f"Found {count} code quality issues that could improve readability"
        }
        return summaries.get(issue_type, f"Found {count} issues of type {issue_type}")
    
    def _get_feedback_recommendation(self, issue_type: str) -> str:
        """Get recommendation for feedback type."""
        recommendations = {
            "security": "Review and fix security vulnerabilities immediately. Use safer alternatives and validate all inputs.",
            "maintainability": "Refactor complex code into smaller, more manageable functions. Add proper documentation.",
            "performance": "Optimize performance bottlenecks. Use more efficient algorithms and data structures.",
            "code_quality": "Improve code quality by adding docstrings, following naming conventions, and addressing technical debt."
        }
        return recommendations.get(issue_type, "Address these issues to improve code quality")
    
    def _feedback_to_improvements(self, feedback_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert feedback items to improvement suggestions."""
        improvements = []
        
        for feedback in feedback_items:
            if feedback["issue_count"] > 0:
                improvements.append({
                    "type": "pr_feedback",
                    "suggestion": f"Address {feedback['category']} issues",
                    "category": feedback["category"],
                    "priority": feedback["priority"],
                    "description": feedback["summary"],
                    "recommendation": feedback["recommendation"],
                    "issue_count": feedback["issue_count"],
                    "specific_examples": feedback["specific_issues"],
                    "confidence": self._calculate_feedback_confidence(feedback),
                    "expected_impact": self._get_expected_impact(feedback["category"])
                })
        
        return improvements
    
    def _calculate_feedback_confidence(self, feedback: Dict[str, Any]) -> float:
        """Calculate confidence level for feedback."""
        # Higher confidence for more issues and higher priority categories
        base_confidence = 0.6
        
        # Boost confidence based on issue count
        issue_boost = min(0.3, feedback["issue_count"] * 0.05)
        
        # Boost confidence based on priority
        priority_boost = feedback["priority"] * 0.1
        
        return min(1.0, base_confidence + issue_boost + priority_boost)
    
    def _get_expected_impact(self, category: str) -> str:
        """Get expected impact of addressing feedback category."""
        impacts = {
            "security": "Significantly improved system security and reduced vulnerability risks",
            "maintainability": "Improved code maintainability and reduced technical debt",
            "performance": "Better system performance and resource utilization",
            "code_quality": "Enhanced code readability and developer productivity"
        }
        return impacts.get(category, "General code improvement")
    
    def _review_file_changes(self, file_change: Dict[str, Any]) -> Dict[str, Any]:
        """Review changes to a specific file."""
        comments = []
        suggestions = []
        
        file_path = file_change.get("filename", "unknown")
        changes = file_change.get("changes", [])
        
        # Analyze each change
        for change in changes:
            change_type = change.get("type", "unknown")  # added, deleted, modified
            line_content = change.get("content", "")
            line_number = change.get("line", 0)
            
            # Check for common issues in changes
            if change_type == "added":
                # Check new code for issues
                issues = self._check_line_for_issues(line_content)
                for issue in issues:
                    comments.append({
                        "file": file_path,
                        "line": line_number,
                        "type": "issue",
                        "message": issue["message"],
                        "category": issue["category"]
                    })
                    
                    suggestions.append({
                        "file": file_path,
                        "line": line_number,
                        "suggestion": issue["suggestion"],
                        "category": issue["category"]
                    })
        
        return {
            "comments": comments,
            "suggestions": suggestions
        }
    
    def _check_line_for_issues(self, line_content: str) -> List[Dict[str, Any]]:
        """Check a single line for common issues."""
        issues = []
        
        # Check against feedback patterns
        for pattern_category, pattern_config in self.feedback_patterns.items():
            for pattern in pattern_config["patterns"]:
                if re.search(pattern, line_content):
                    issues.append({
                        "category": pattern_category,
                        "message": self._get_pattern_message(pattern_category, pattern),
                        "suggestion": self._get_pattern_suggestion(pattern_category, pattern)
                    })
        
        return issues
    
    def _get_pattern_suggestion(self, pattern_category: str, pattern: str) -> str:
        """Get improvement suggestion for a pattern."""
        suggestions = {
            "code_quality": "Add proper documentation and follow coding standards",
            "security": "Use secure alternatives and validate inputs",
            "performance": "Optimize for better performance",
            "maintainability": "Refactor for better maintainability"
        }
        return suggestions.get(pattern_category, "Consider improvement")
    
    def _generate_overall_pr_feedback(self, changes: Dict[str, Any], comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall feedback for the PR."""
        total_files = len(changes.get("files_changed", []))
        total_comments = len(comments)
        
        # Categorize comments
        comment_categories = {}
        for comment in comments:
            category = comment.get("category", "other")
            comment_categories[category] = comment_categories.get(category, 0) + 1
        
        feedback = {
            "summary": f"Reviewed {total_files} files with {total_comments} comments",
            "comment_categories": comment_categories,
            "overall_quality": self._assess_overall_quality(comment_categories),
            "recommendations": self._generate_pr_recommendations(comment_categories)
        }
        
        return feedback
    
    def _assess_overall_quality(self, comment_categories: Dict[str, int]) -> str:
        """Assess overall quality of the PR."""
        total_issues = sum(comment_categories.values())
        
        if total_issues == 0:
            return "excellent"
        elif total_issues <= 3:
            return "good"
        elif total_issues <= 10:
            return "fair"
        else:
            return "needs_improvement"
    
    def _generate_pr_recommendations(self, comment_categories: Dict[str, int]) -> List[str]:
        """Generate recommendations for the PR."""
        recommendations = []
        
        for category, count in comment_categories.items():
            if count > 0:
                if category == "security":
                    recommendations.append(f"Address {count} security issue(s) before merging")
                elif category == "maintainability":
                    recommendations.append(f"Improve maintainability by addressing {count} issue(s)")
                elif category == "performance":
                    recommendations.append(f"Consider optimizing {count} performance issue(s)")
                elif category == "code_quality":
                    recommendations.append(f"Enhance code quality by fixing {count} issue(s)")
        
        if not recommendations:
            recommendations.append("Code looks good - no major issues found")
        
        return recommendations
    
    def _determine_approval_status(self, comments: List[Dict[str, Any]]) -> str:
        """Determine if PR should be approved based on comments."""
        security_issues = len([c for c in comments if c.get("category") == "security"])
        total_issues = len(comments)
        
        if security_issues > 0:
            return "changes_requested"  # Never approve with security issues
        elif total_issues > 10:
            return "changes_requested"  # Too many issues
        elif total_issues > 0:
            return "approved_with_suggestions"
        else:
            return "approved"
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get statistics about feedback processing."""
        total_feedback_cycles = len(self.feedback_history)
        total_improvements = sum(
            len(fb.get("improvements", [])) 
            for fb in self.feedback_history
        )
        
        # Count feedback categories
        category_counts = {}
        for feedback in self.feedback_history:
            for improvement in feedback.get("improvements", []):
                category = improvement.get("category", "unknown")
                category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_feedback_cycles": total_feedback_cycles,
            "total_improvements_suggested": total_improvements,
            "category_breakdown": category_counts,
            "average_improvements_per_cycle": (
                total_improvements / total_feedback_cycles 
                if total_feedback_cycles > 0 else 0
            ),
            "recent_feedback": self.feedback_history[-3:] if self.feedback_history else []
        }


if __name__ == "__main__":
    # Test the PR feedback system
    pr_feedback = PRFeedbackLoop()
    result = pr_feedback.process_feedback()
    print(json.dumps(result, indent=2, default=str))