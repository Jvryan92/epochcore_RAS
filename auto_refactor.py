#!/usr/bin/env python3
"""
EpochCore RAS Automated Refactoring System
Implements static analysis and refactoring routines that recursively improve code
"""

import ast
import os
import re
import json
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AutoRefactor:
    """
    Automated refactoring system that analyzes code and applies safe improvements.
    Uses static analysis to identify refactoring opportunities.
    """
    
    def __init__(self):
        self.project_root = os.getcwd()
        self.python_files = []
        self.refactoring_rules = {
            "complexity_reduction": True,
            "code_duplication": True,
            "naming_conventions": True,
            "import_optimization": True,
            "docstring_improvements": True,
            "type_hint_additions": True,
            "performance_optimizations": True
        }
        
        # Track applied refactorings to avoid repeating
        self.applied_refactorings = []
        
        logger.info("Auto Refactor system initialized")
    
    def analyze_and_refactor(self) -> Dict[str, Any]:
        """
        Analyze code base and apply safe refactoring improvements.
        """
        logger.info("Starting automated code analysis and refactoring")
        
        try:
            # Discover Python files
            self._discover_python_files()
            
            # Analyze each file
            analysis_results = []
            for file_path in self.python_files:
                file_analysis = self._analyze_file(file_path)
                if file_analysis:
                    analysis_results.append(file_analysis)
            
            # Generate refactoring recommendations
            improvements = self._generate_refactoring_improvements(analysis_results)
            
            result = {
                "improvements_found": len(improvements) > 0,
                "improvements": improvements,
                "files_analyzed": len(self.python_files),
                "analysis_results": analysis_results,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Code analysis completed. Found {len(improvements)} refactoring opportunities across {len(self.python_files)} files")
            return result
            
        except Exception as e:
            logger.error(f"Error in automated refactoring: {str(e)}")
            return {
                "improvements_found": False,
                "improvements": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _discover_python_files(self):
        """Discover all Python files in the project."""
        self.python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip virtual environments and cache directories
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.python_files.append(file_path)
        
        logger.info(f"Discovered {len(self.python_files)} Python files")
    
    def _analyze_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Analyze a single Python file for refactoring opportunities."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                logger.warning(f"Syntax error in {file_path}: {e}")
                return None
            
            analysis = {
                "file_path": file_path,
                "relative_path": os.path.relpath(file_path, self.project_root),
                "issues": [],
                "metrics": {},
                "suggestions": []
            }
            
            # Analyze different aspects
            self._analyze_complexity(tree, analysis, content)
            self._analyze_imports(tree, analysis)
            self._analyze_naming(tree, analysis)
            self._analyze_docstrings(tree, analysis)
            self._analyze_duplication(content, analysis)
            self._analyze_performance(tree, analysis, content)
            
            return analysis if analysis["issues"] or analysis["suggestions"] else None
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return None
    
    def _analyze_complexity(self, tree: ast.AST, analysis: Dict[str, Any], content: str):
        """Analyze code complexity and suggest improvements."""
        class ComplexityAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.functions = []
                self.classes = []
                
            def visit_FunctionDef(self, node):
                # Count nested control flow statements
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > 10:
                    analysis["issues"].append({
                        "type": "high_complexity",
                        "line": node.lineno,
                        "function": node.name,
                        "complexity": complexity,
                        "message": f"Function '{node.name}' has high cyclomatic complexity ({complexity})"
                    })
                    
                    analysis["suggestions"].append({
                        "type": "complexity_reduction",
                        "line": node.lineno,
                        "function": node.name,
                        "suggestion": "Consider breaking this function into smaller functions"
                    })
                
                self.functions.append({"name": node.name, "complexity": complexity, "line": node.lineno})
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Count methods in class
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if len(methods) > 20:
                    analysis["issues"].append({
                        "type": "large_class",
                        "line": node.lineno,
                        "class": node.name,
                        "method_count": len(methods),
                        "message": f"Class '{node.name}' has many methods ({len(methods)})"
                    })
                
                self.classes.append({"name": node.name, "methods": len(methods), "line": node.lineno})
                self.generic_visit(node)
            
            def _calculate_cyclomatic_complexity(self, node):
                """Calculate cyclomatic complexity of a function."""
                complexity = 1  # Base complexity
                
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                        complexity += 1
                    elif isinstance(child, ast.BoolOp):
                        complexity += len(child.values) - 1
                    elif isinstance(child, ast.ExceptHandler):
                        complexity += 1
                
                return complexity
        
        analyzer = ComplexityAnalyzer()
        analyzer.visit(tree)
        
        analysis["metrics"]["function_count"] = len(analyzer.functions)
        analysis["metrics"]["class_count"] = len(analyzer.classes)
        analysis["metrics"]["average_complexity"] = (
            sum(f["complexity"] for f in analyzer.functions) / len(analyzer.functions) 
            if analyzer.functions else 0
        )
    
    def _analyze_imports(self, tree: ast.AST, analysis: Dict[str, Any]):
        """Analyze import statements for optimization opportunities."""
        imports = []
        unused_imports = []
        
        class ImportAnalyzer(ast.NodeVisitor):
            def __init__(self):
                self.imported_names = set()
                self.used_names = set()
                
            def visit_Import(self, node):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports.append({"type": "import", "name": name, "line": node.lineno})
                    self.imported_names.add(name)
            
            def visit_ImportFrom(self, node):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports.append({"type": "from_import", "name": name, "module": node.module, "line": node.lineno})
                    self.imported_names.add(name)
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    self.used_names.add(node.id)
                self.generic_visit(node)
        
        analyzer = ImportAnalyzer()
        analyzer.visit(tree)
        
        # Find unused imports (simplified check)
        for imp in imports:
            if imp["name"] not in analyzer.used_names and imp["name"] != "*":
                unused_imports.append(imp)
                analysis["issues"].append({
                    "type": "unused_import",
                    "line": imp["line"],
                    "name": imp["name"],
                    "message": f"Unused import: {imp['name']}"
                })
                
                analysis["suggestions"].append({
                    "type": "import_cleanup",
                    "line": imp["line"],
                    "suggestion": f"Remove unused import: {imp['name']}"
                })
        
        analysis["metrics"]["import_count"] = len(imports)
        analysis["metrics"]["unused_import_count"] = len(unused_imports)
    
    def _analyze_naming(self, tree: ast.AST, analysis: Dict[str, Any]):
        """Analyze naming conventions."""
        class NamingAnalyzer(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                # Check snake_case for functions
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('_'):
                    analysis["issues"].append({
                        "type": "naming_convention",
                        "line": node.lineno,
                        "name": node.name,
                        "message": f"Function '{node.name}' should use snake_case naming"
                    })
                    
                    analysis["suggestions"].append({
                        "type": "naming_fix",
                        "line": node.lineno,
                        "suggestion": f"Rename function '{node.name}' to follow snake_case convention"
                    })
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                # Check PascalCase for classes
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    analysis["issues"].append({
                        "type": "naming_convention",
                        "line": node.lineno,
                        "name": node.name,
                        "message": f"Class '{node.name}' should use PascalCase naming"
                    })
                    
                    analysis["suggestions"].append({
                        "type": "naming_fix",
                        "line": node.lineno,
                        "suggestion": f"Rename class '{node.name}' to follow PascalCase convention"
                    })
                
                self.generic_visit(node)
        
        NamingAnalyzer().visit(tree)
    
    def _analyze_docstrings(self, tree: ast.AST, analysis: Dict[str, Any]):
        """Analyze docstring coverage and quality."""
        missing_docstrings = []
        
        class DocstringAnalyzer(ast.NodeVisitor):
            def visit_FunctionDef(self, node):
                if not ast.get_docstring(node) and not node.name.startswith('_'):
                    missing_docstrings.append(node.name)
                    analysis["issues"].append({
                        "type": "missing_docstring",
                        "line": node.lineno,
                        "function": node.name,
                        "message": f"Function '{node.name}' lacks a docstring"
                    })
                    
                    analysis["suggestions"].append({
                        "type": "add_docstring",
                        "line": node.lineno,
                        "suggestion": f"Add docstring to function '{node.name}'"
                    })
                
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                if not ast.get_docstring(node):
                    analysis["issues"].append({
                        "type": "missing_docstring",
                        "line": node.lineno,
                        "class": node.name,
                        "message": f"Class '{node.name}' lacks a docstring"
                    })
                    
                    analysis["suggestions"].append({
                        "type": "add_docstring",
                        "line": node.lineno,
                        "suggestion": f"Add docstring to class '{node.name}'"
                    })
                
                self.generic_visit(node)
        
        DocstringAnalyzer().visit(tree)
        analysis["metrics"]["missing_docstrings"] = len(missing_docstrings)
    
    def _analyze_duplication(self, content: str, analysis: Dict[str, Any]):
        """Analyze code duplication (simplified approach)."""
        lines = content.split('\n')
        line_hashes = {}
        duplicated_lines = []
        
        for i, line in enumerate(lines, 1):
            # Skip empty lines and comments
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Simple hash of non-whitespace content
            line_hash = hash(stripped)
            
            if line_hash in line_hashes:
                if line_hashes[line_hash] not in duplicated_lines:
                    duplicated_lines.append(line_hashes[line_hash])
                duplicated_lines.append(i)
            else:
                line_hashes[line_hash] = i
        
        if len(duplicated_lines) > 2:
            analysis["issues"].append({
                "type": "code_duplication",
                "lines": duplicated_lines[:10],  # Show first 10
                "count": len(duplicated_lines),
                "message": f"Found {len(duplicated_lines)} potentially duplicated lines"
            })
            
            analysis["suggestions"].append({
                "type": "extract_common_code",
                "suggestion": "Consider extracting common code into functions or constants"
            })
        
        analysis["metrics"]["duplicated_lines"] = len(duplicated_lines)
    
    def _analyze_performance(self, tree: ast.AST, analysis: Dict[str, Any], content: str):
        """Analyze potential performance improvements."""
        class PerformanceAnalyzer(ast.NodeVisitor):
            def visit_ListComp(self, node):
                # Suggest generator expressions for large list comprehensions
                if len(ast.dump(node)) > 200:  # Rough complexity measure
                    analysis["suggestions"].append({
                        "type": "performance_optimization",
                        "line": node.lineno,
                        "suggestion": "Consider using generator expression for memory efficiency"
                    })
                self.generic_visit(node)
            
            def visit_For(self, node):
                # Check for range(len()) pattern
                if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
                    if node.iter.func.id == 'range' and len(node.iter.args) == 1:
                        if isinstance(node.iter.args[0], ast.Call) and isinstance(node.iter.args[0].func, ast.Name):
                            if node.iter.args[0].func.id == 'len':
                                analysis["suggestions"].append({
                                    "type": "performance_optimization",
                                    "line": node.lineno,
                                    "suggestion": "Consider using enumerate() instead of range(len())"
                                })
                self.generic_visit(node)
        
        PerformanceAnalyzer().visit(tree)
    
    def _generate_refactoring_improvements(self, analysis_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate improvement recommendations from analysis results."""
        improvements = []
        
        for file_analysis in analysis_results:
            file_path = file_analysis["relative_path"]
            
            # Group suggestions by type
            suggestion_groups = {}
            for suggestion in file_analysis["suggestions"]:
                suggestion_type = suggestion["type"]
                if suggestion_type not in suggestion_groups:
                    suggestion_groups[suggestion_type] = []
                suggestion_groups[suggestion_type].append(suggestion)
            
            # Generate improvements for each group
            for suggestion_type, suggestions in suggestion_groups.items():
                if len(suggestions) >= 1:  # Only include if we have at least 1 suggestion
                    improvements.append({
                        "type": "refactor",
                        "refactor_type": suggestion_type,
                        "file": file_path,
                        "description": self._get_refactor_description(suggestion_type, len(suggestions)),
                        "suggestions_count": len(suggestions),
                        "suggestions": suggestions[:5],  # Include up to 5 specific suggestions
                        "confidence": self._get_refactor_confidence(suggestion_type),
                        "expected_benefit": self._get_refactor_benefit(suggestion_type),
                        "auto_applicable": self._is_auto_applicable(suggestion_type)
                    })
        
        return improvements
    
    def _get_refactor_description(self, refactor_type: str, count: int) -> str:
        """Get description for refactoring type."""
        descriptions = {
            "complexity_reduction": f"Reduce code complexity in {count} function(s)",
            "import_cleanup": f"Remove {count} unused import(s)",
            "naming_fix": f"Fix naming conventions for {count} item(s)",
            "add_docstring": f"Add docstrings to {count} function(s)/class(es)",
            "extract_common_code": f"Extract {count} duplicated code section(s)",
            "performance_optimization": f"Apply {count} performance optimization(s)"
        }
        return descriptions.get(refactor_type, f"Apply {refactor_type} refactoring ({count} instances)")
    
    def _get_refactor_confidence(self, refactor_type: str) -> float:
        """Get confidence level for refactoring type."""
        confidence_levels = {
            "import_cleanup": 0.9,
            "add_docstring": 0.8,
            "naming_fix": 0.7,
            "performance_optimization": 0.6,
            "complexity_reduction": 0.5,
            "extract_common_code": 0.4
        }
        return confidence_levels.get(refactor_type, 0.5)
    
    def _get_refactor_benefit(self, refactor_type: str) -> str:
        """Get expected benefit description."""
        benefits = {
            "complexity_reduction": "Improved code maintainability and readability",
            "import_cleanup": "Reduced memory usage and faster import times",
            "naming_fix": "Better code readability and consistency",
            "add_docstring": "Improved code documentation and understanding",
            "extract_common_code": "Reduced code duplication and maintenance burden",
            "performance_optimization": "Better runtime performance and resource usage"
        }
        return benefits.get(refactor_type, "General code quality improvement")
    
    def _is_auto_applicable(self, refactor_type: str) -> bool:
        """Check if refactoring can be applied automatically."""
        auto_applicable = {
            "import_cleanup": True,
            "add_docstring": False,  # Requires human input
            "naming_fix": False,     # May break external references
            "performance_optimization": False,  # Needs careful review
            "complexity_reduction": False,      # Requires redesign
            "extract_common_code": False        # Needs human judgment
        }
        return auto_applicable.get(refactor_type, False)
    
    def apply_safe_refactorings(self, improvements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply only the safest automatic refactorings."""
        applied = []
        
        for improvement in improvements:
            if improvement.get("auto_applicable", False) and improvement["confidence"] > 0.8:
                try:
                    success = self._apply_refactoring(improvement)
                    if success:
                        applied.append(improvement)
                        self.applied_refactorings.append({
                            "improvement": improvement,
                            "timestamp": datetime.now().isoformat()
                        })
                except Exception as e:
                    logger.error(f"Error applying refactoring {improvement['refactor_type']}: {str(e)}")
        
        return {
            "applied_count": len(applied),
            "applied_refactorings": applied,
            "total_candidates": len(improvements)
        }
    
    def _apply_refactoring(self, improvement: Dict[str, Any]) -> bool:
        """Apply a specific refactoring improvement."""
        # For now, just log what would be applied
        # In a real implementation, this would make actual code changes
        logger.info(f"Would apply refactoring: {improvement['description']} to {improvement['file']}")
        return True


if __name__ == "__main__":
    # Test the auto refactor system
    refactor = AutoRefactor()
    result = refactor.analyze_and_refactor()
    print(json.dumps(result, indent=2, default=str))