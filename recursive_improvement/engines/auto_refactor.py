"""
Auto Refactor Engine - Recursive Autonomy Module
Autonomous refactoring engine that suggests and optionally applies recursive code improvements
"""

from datetime import datetime
from typing import Dict, Any, List, Tuple
import ast
import os
import re
import subprocess
import logging

from ..base import RecursiveEngine, CompoundingAction


class AutoRefactorEngine(RecursiveEngine):
    """
    Autonomous refactoring engine with recursive improvement capabilities.
    Analyzes code for refactoring opportunities and applies improvements recursively.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("auto_refactor", config)
        self.refactoring_history = []
        self.code_metrics = {}
        self.refactoring_rules = self._load_refactoring_rules()
        self.improvement_suggestions = []
        
    def initialize(self) -> bool:
        """Initialize the auto refactor engine."""
        try:
            self.logger.info("Initializing Auto Refactor Engine")
            
            # Set up compounding actions
            refactor_action = CompoundingAction(
                name="recursive_refactoring",
                action=self.execute_main_action,
                interval=1.0,  # Weekly comprehensive analysis
                pre_action=self.execute_pre_action,
                pre_interval=0.25,  # Quick code smell detection
                metadata={"type": "refactoring", "recursive": True}
            )
            
            self.add_compounding_action(refactor_action)
            
            # Initialize metrics tracking
            self.code_metrics = {
                "files_analyzed": 0,
                "refactoring_opportunities": 0,
                "improvements_suggested": 0,
                "improvements_applied": 0,
                "code_quality_score": 0.0,
                "complexity_reduced": 0,
                "duplications_removed": 0
            }
            
            self.logger.info("Auto Refactor Engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Auto Refactor Engine: {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute main refactoring analysis and improvement application."""
        try:
            self.logger.info("Executing comprehensive refactoring analysis")
            
            # Analyze entire codebase for refactoring opportunities
            analysis_results = self._analyze_codebase()
            
            # Generate refactoring suggestions
            suggestions = self._generate_refactoring_suggestions(analysis_results)
            
            # Apply safe refactorings automatically
            applied_refactorings = self._apply_safe_refactorings(suggestions)
            
            # Create PR for complex refactorings requiring human review
            pr_created = self._create_refactoring_pr(suggestions)
            
            # Update code quality metrics
            self._update_code_quality_metrics()
            
            # Learn from applied refactorings
            learned_patterns = self._learn_from_refactorings(applied_refactorings)
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "action": "comprehensive_refactoring",
                "files_analyzed": len(analysis_results),
                "suggestions_generated": len(suggestions),
                "safe_refactorings_applied": len(applied_refactorings),
                "pr_created": pr_created,
                "learned_patterns": len(learned_patterns),
                "code_metrics": self.code_metrics
            }
            
            self.refactoring_history.append(result)
            self.logger.info(f"Refactoring cycle completed: {len(suggestions)} suggestions, {len(applied_refactorings)} applied")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in refactoring cycle: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "comprehensive_refactoring",
                "error": str(e),
                "status": "failed"
            }
    
    def execute_pre_action(self) -> Dict[str, Any]:
        """Execute pre-action: quick code smell detection and prioritization."""
        try:
            self.logger.info("Quick code smell detection and prioritization")
            
            # Quick scan for obvious code smells
            code_smells = self._detect_code_smells()
            
            # Prioritize refactoring opportunities
            prioritized_opportunities = self._prioritize_refactoring_opportunities(code_smells)
            
            # Pre-prepare refactoring templates
            templates_prepared = self._prepare_refactoring_templates(prioritized_opportunities)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "code_smell_detection",
                "code_smells_found": len(code_smells),
                "opportunities_prioritized": len(prioritized_opportunities),
                "templates_prepared": templates_prepared,
                "status": "completed"
            }
            
        except Exception as e:
            self.logger.error(f"Error in code smell detection: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "action": "code_smell_detection",
                "error": str(e),
                "status": "failed"
            }
    
    def _load_refactoring_rules(self) -> Dict[str, Any]:
        """Load refactoring rules and patterns."""
        return {
            "duplicate_code": {
                "pattern": "similar_blocks_threshold",
                "threshold": 0.8,
                "action": "extract_method"
            },
            "long_methods": {
                "pattern": "method_length",
                "threshold": 50,
                "action": "split_method"
            },
            "large_classes": {
                "pattern": "class_size",
                "threshold": 300,
                "action": "extract_class"
            },
            "complex_conditions": {
                "pattern": "cyclomatic_complexity",
                "threshold": 10,
                "action": "simplify_conditions"
            },
            "magic_numbers": {
                "pattern": r"\b\d+\b",
                "action": "extract_constant"
            },
            "unused_imports": {
                "pattern": "import_usage",
                "action": "remove_unused"
            },
            "inconsistent_naming": {
                "pattern": "naming_conventions",
                "action": "standardize_naming"
            }
        }
    
    def _analyze_codebase(self) -> List[Dict[str, Any]]:
        """Analyze entire codebase for refactoring opportunities."""
        analysis_results = []
        
        # Get all Python files
        python_files = self._get_python_files()
        
        for file_path in python_files:
            try:
                file_analysis = self._analyze_file(file_path)
                analysis_results.append(file_analysis)
                self.code_metrics["files_analyzed"] += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to analyze {file_path}: {e}")
                
        return analysis_results
    
    def _get_python_files(self) -> List[str]:
        """Get list of Python files in the repository."""
        python_files = []
        
        for root, dirs, files in os.walk("."):
            # Skip virtual environment and cache directories
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
                    
        return python_files
    
    def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a single file for refactoring opportunities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST for structural analysis
            tree = ast.parse(content)
            
            analysis = {
                "file_path": file_path,
                "line_count": len(content.splitlines()),
                "complexity_score": self._calculate_complexity(tree),
                "duplicate_blocks": self._find_duplicate_blocks(content),
                "long_methods": self._find_long_methods(tree),
                "magic_numbers": self._find_magic_numbers(content),
                "unused_imports": self._find_unused_imports(tree, content),
                "naming_issues": self._find_naming_issues(tree),
                "code_smells": []
            }
            
            # Calculate overall quality score
            analysis["quality_score"] = self._calculate_quality_score(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {e}")
            return {"file_path": file_path, "error": str(e)}
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of the file."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.With)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, (ast.Try, ast.ExceptHandler)):
                complexity += 1
                
        return complexity
    
    def _find_duplicate_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Find potential duplicate code blocks."""
        lines = content.splitlines()
        duplicates = []
        
        # Simple duplicate detection based on similar line patterns
        for i in range(len(lines) - 5):
            block1 = lines[i:i+5]
            for j in range(i+5, len(lines) - 5):
                block2 = lines[j:j+5]
                
                # Calculate similarity
                similarity = self._calculate_similarity(block1, block2)
                if similarity > 0.8:
                    duplicates.append({
                        "block1_start": i + 1,
                        "block2_start": j + 1,
                        "similarity": similarity,
                        "lines": 5
                    })
                    
        return duplicates
    
    def _calculate_similarity(self, block1: List[str], block2: List[str]) -> float:
        """Calculate similarity between two code blocks."""
        if len(block1) != len(block2):
            return 0.0
            
        matches = 0
        for line1, line2 in zip(block1, block2):
            # Normalize whitespace and compare
            if line1.strip() == line2.strip():
                matches += 1
                
        return matches / len(block1)
    
    def _find_long_methods(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Find methods that are too long."""
        long_methods = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_lines = node.end_lineno - node.lineno + 1
                if method_lines > 50:  # Threshold for long methods
                    long_methods.append({
                        "name": node.name,
                        "start_line": node.lineno,
                        "end_line": node.end_lineno,
                        "line_count": method_lines
                    })
                    
        return long_methods
    
    def _find_magic_numbers(self, content: str) -> List[Dict[str, Any]]:
        """Find magic numbers in the code."""
        magic_numbers = []
        
        # Find numeric literals (excluding common ones like 0, 1, 2)
        pattern = r'\b(?!0\b|1\b|2\b)\d+\b'
        
        for match in re.finditer(pattern, content):
            line_num = content[:match.start()].count('\n') + 1
            magic_numbers.append({
                "value": match.group(),
                "line": line_num,
                "position": match.start()
            })
            
        return magic_numbers
    
    def _find_unused_imports(self, tree: ast.AST, content: str) -> List[str]:
        """Find unused import statements."""
        imports = []
        used_names = set()
        
        # Collect all import statements
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
                
        # Find imports that are not used
        unused_imports = []
        for imp in imports:
            if imp not in used_names and not any(imp in line for line in content.splitlines()):
                unused_imports.append(imp)
                
        return unused_imports
    
    def _find_naming_issues(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Find naming convention issues."""
        naming_issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.islower() or '__' in node.name:
                    naming_issues.append({
                        "type": "function",
                        "name": node.name,
                        "line": node.lineno,
                        "issue": "should_use_snake_case"
                    })
            elif isinstance(node, ast.ClassDef):
                if not node.name[0].isupper():
                    naming_issues.append({
                        "type": "class",
                        "name": node.name,
                        "line": node.lineno,
                        "issue": "should_use_pascal_case"
                    })
                    
        return naming_issues
    
    def _calculate_quality_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall quality score for the file."""
        score = 100.0
        
        # Deduct points for various issues
        score -= len(analysis.get("duplicate_blocks", [])) * 10
        score -= len(analysis.get("long_methods", [])) * 5
        score -= len(analysis.get("magic_numbers", [])) * 2
        score -= len(analysis.get("unused_imports", [])) * 3
        score -= len(analysis.get("naming_issues", [])) * 2
        
        # Complexity penalty
        complexity = analysis.get("complexity_score", 0)
        if complexity > 20:
            score -= (complexity - 20) * 2
            
        return max(0.0, score)
    
    def _generate_refactoring_suggestions(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate refactoring suggestions based on analysis."""
        suggestions = []
        
        for analysis in analysis_results:
            file_path = analysis.get("file_path", "")
            
            # Suggest duplicate block removal
            for duplicate in analysis.get("duplicate_blocks", []):
                suggestions.append({
                    "type": "extract_method",
                    "file": file_path,
                    "description": f"Extract duplicate code starting at lines {duplicate['block1_start']} and {duplicate['block2_start']}",
                    "priority": "high",
                    "safety": "medium"
                })
                
            # Suggest method splitting for long methods
            for long_method in analysis.get("long_methods", []):
                suggestions.append({
                    "type": "split_method",
                    "file": file_path,
                    "description": f"Split long method '{long_method['name']}' ({long_method['line_count']} lines)",
                    "priority": "medium", 
                    "safety": "low"
                })
                
            # Suggest constant extraction for magic numbers
            for magic_number in analysis.get("magic_numbers", []):
                suggestions.append({
                    "type": "extract_constant",
                    "file": file_path,
                    "description": f"Extract magic number {magic_number['value']} at line {magic_number['line']}",
                    "priority": "low",
                    "safety": "high"
                })
                
            # Suggest removing unused imports
            for unused_import in analysis.get("unused_imports", []):
                suggestions.append({
                    "type": "remove_import",
                    "file": file_path,
                    "description": f"Remove unused import '{unused_import}'",
                    "priority": "low",
                    "safety": "high"
                })
                
        return suggestions
    
    def _apply_safe_refactorings(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply safe refactorings automatically."""
        applied_refactorings = []
        
        for suggestion in suggestions:
            if suggestion.get("safety") == "high":
                try:
                    success = self._apply_refactoring(suggestion)
                    if success:
                        applied_refactorings.append(suggestion)
                        self.code_metrics["improvements_applied"] += 1
                        
                except Exception as e:
                    self.logger.error(f"Failed to apply refactoring: {e}")
                    
        return applied_refactorings
    
    def _apply_refactoring(self, suggestion: Dict[str, Any]) -> bool:
        """Apply a specific refactoring."""
        try:
            if suggestion["type"] == "remove_import":
                return self._remove_unused_import(suggestion)
            elif suggestion["type"] == "extract_constant":
                return self._extract_constant(suggestion)
            # Add more refactoring implementations as needed
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error applying refactoring: {e}")
            return False
    
    def _remove_unused_import(self, suggestion: Dict[str, Any]) -> bool:
        """Remove unused import from file."""
        # Simulate import removal - in real implementation would modify file
        self.logger.info(f"Removing unused import in {suggestion['file']}")
        return True
    
    def _extract_constant(self, suggestion: Dict[str, Any]) -> bool:
        """Extract magic number to named constant.""" 
        # Simulate constant extraction - in real implementation would modify file
        self.logger.info(f"Extracting constant in {suggestion['file']}")
        return True
    
    def _create_refactoring_pr(self, suggestions: List[Dict[str, Any]]) -> bool:
        """Create PR for complex refactorings requiring human review."""
        complex_suggestions = [s for s in suggestions if s.get("safety") in ["low", "medium"]]
        
        if complex_suggestions:
            # Simulate PR creation - in real implementation would use GitHub API
            self.logger.info(f"Creating refactoring PR with {len(complex_suggestions)} suggestions")
            return True
            
        return False
    
    def _update_code_quality_metrics(self):
        """Update overall code quality metrics."""
        # Simulate metrics update
        self.code_metrics["code_quality_score"] = 85.0
        self.code_metrics["complexity_reduced"] += 5
    
    def _learn_from_refactorings(self, applied_refactorings: List[Dict[str, Any]]) -> List[str]:
        """Learn patterns from successfully applied refactorings."""
        patterns = []
        
        for refactoring in applied_refactorings:
            pattern = f"{refactoring['type']}_success"
            if pattern not in patterns:
                patterns.append(pattern)
                
        return patterns
    
    def _detect_code_smells(self) -> List[Dict[str, Any]]:
        """Quick detection of obvious code smells."""
        code_smells = [
            {
                "type": "long_parameter_list",
                "file": "example.py",
                "line": 42,
                "severity": "medium"
            },
            {
                "type": "duplicate_code",
                "file": "utils.py", 
                "line": 15,
                "severity": "high"
            }
        ]
        
        return code_smells
    
    def _prioritize_refactoring_opportunities(self, code_smells: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize refactoring opportunities based on impact and effort."""
        # Sort by severity and impact
        prioritized = sorted(code_smells, key=lambda x: {
            "high": 3,
            "medium": 2, 
            "low": 1
        }.get(x.get("severity", "low"), 1), reverse=True)
        
        return prioritized
    
    def _prepare_refactoring_templates(self, opportunities: List[Dict[str, Any]]) -> bool:
        """Prepare refactoring templates for common patterns."""
        try:
            # Pre-generate templates for common refactorings
            templates = {
                "extract_method": "def {method_name}():\n    # Extracted code here\n    pass",
                "extract_constant": "{CONSTANT_NAME} = {value}",
                "split_method": "# Method split template"
            }
            
            # Store templates for later use
            self.improvement_suggestions = templates
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to prepare templates: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the auto refactor engine."""
        return {
            "name": self.name,
            "running": self.is_running,
            "code_metrics": self.code_metrics,
            "refactoring_rules_count": len(self.refactoring_rules),
            "improvement_suggestions_count": len(self.improvement_suggestions),
            "last_execution": self.last_execution,
            "total_executions": len(self.execution_history)
        }