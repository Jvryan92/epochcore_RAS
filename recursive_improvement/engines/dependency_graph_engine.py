"""
Recursive Dependency Graph Updater Engine
Recursively updates and optimizes dependency graphs with compounding intelligence.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
import json
import logging
from collections import defaultdict, deque

from ..base import RecursiveEngine, CompoundingAction


class RecursiveDependencyGraphUpdater(RecursiveEngine):
    """
    Recursive Dependency Graph Updater that continuously analyzes,
    optimizes, and evolves dependency relationships with compounding improvements.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("recursive_dependency_graph_updater", config)
        self.dependency_graph = {}
        self.optimization_history = []
        self.cycle_detection_cache = {}
        self.performance_metrics = {}
        self.update_patterns = []
        
    def initialize(self) -> bool:
        """Initialize the dependency graph updater engine."""
        try:
            self.logger.info("Initializing Recursive Dependency Graph Updater Engine")
            
            # Set up compounding actions
            update_action = CompoundingAction(
                name="dependency_graph_optimization",
                action=self.execute_main_action,
                interval=1.0,  # Weekly
                pre_action=self.execute_pre_action,
                pre_interval=0.25,  # +0.25 interval
                metadata={"type": "dependency_optimization", "recursive": True}
            )
            
            self.add_compounding_action(update_action)
            
            # Initialize performance metrics
            self.performance_metrics = {
                "graphs_analyzed": 0,
                "cycles_detected": 0,
                "optimizations_applied": 0,
                "recursive_depth": 1,
                "update_cycles": 0
            }
            
            # Initialize basic dependency graph structure
            self._initialize_graph_structure()
            
            self.logger.info("Recursive Dependency Graph Updater Engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dependency graph updater: {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute main dependency graph optimization with recursive improvement."""
        self.logger.info("Executing recursive dependency graph update")
        
        result = {
            "action": "dependency_graph_optimization",
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        try:
            # Analyze current dependency structure
            analysis = self._analyze_dependency_structure()
            
            # Detect and resolve cycles recursively
            cycle_resolution = self._detect_and_resolve_cycles()
            
            # Optimize dependency paths with compounding
            path_optimization = self._optimize_dependency_paths()
            
            # Update graph with recursive improvements
            graph_updates = self._apply_recursive_updates()
            
            # Validate graph integrity with recursive checking
            validation = self._validate_graph_integrity()
            
            result.update({
                "nodes_analyzed": analysis["nodes_analyzed"],
                "cycles_resolved": len(cycle_resolution),
                "paths_optimized": len(path_optimization),
                "updates_applied": len(graph_updates),
                "integrity_score": validation["score"]
            })
            
            # Update metrics with compounding
            self.performance_metrics["graphs_analyzed"] += 1
            self.performance_metrics["cycles_detected"] += len(cycle_resolution)
            self.performance_metrics["optimizations_applied"] += len(graph_updates)
            self.performance_metrics["recursive_depth"] += 1
            self.performance_metrics["update_cycles"] += 1
            
            self.logger.info(f"Dependency graph optimization complete: {len(graph_updates)} updates applied")
            return result
            
        except Exception as e:
            self.logger.error(f"Dependency graph optimization failed: {e}")
            result["error"] = str(e)
            return result
    
    def execute_pre_action(self) -> Dict[str, Any]:
        """Execute pre-optimization analysis with overlap."""
        self.logger.info("Executing pre-optimization dependency analysis")
        
        try:
            # Pre-scan for new dependencies
            new_dependencies = self._scan_for_new_dependencies()
            
            # Pre-identify potential cycles
            potential_cycles = self._pre_identify_cycles()
            
            # Pre-calculate optimization candidates
            optimization_candidates = self._identify_optimization_candidates()
            
            return {
                "status": "pre-optimization_completed",
                "engine": self.name,
                "new_dependencies": len(new_dependencies),
                "potential_cycles": len(potential_cycles),
                "optimization_candidates": len(optimization_candidates)
            }
            
        except Exception as e:
            self.logger.error(f"Pre-optimization error: {e}")
            return {"status": "pre-optimization_error", "error": str(e)}
    
    def _initialize_graph_structure(self):
        """Initialize basic dependency graph structure."""
        # Create sample dependency graph
        self.dependency_graph = {
            "nodes": {
                "core_module": {"type": "core", "version": "1.0", "dependencies": []},
                "auth_module": {"type": "service", "version": "1.2", "dependencies": ["core_module"]},
                "api_module": {"type": "service", "version": "2.0", "dependencies": ["auth_module", "core_module"]},
                "ui_module": {"type": "frontend", "version": "3.1", "dependencies": ["api_module"]},
                "analytics_module": {"type": "service", "version": "1.5", "dependencies": ["api_module"]}
            },
            "edges": {},
            "metadata": {
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "optimization_level": 1
            }
        }
        
        # Build edge relationships
        self._rebuild_edge_relationships()
    
    def _analyze_dependency_structure(self) -> Dict[str, Any]:
        """Analyze current dependency structure with recursive depth."""
        nodes = self.dependency_graph.get("nodes", {})
        analysis = {
            "nodes_analyzed": len(nodes),
            "dependency_depth": {},
            "complexity_metrics": {},
            "bottleneck_nodes": []
        }
        
        # Calculate dependency depth for each node
        for node_id in nodes:
            depth = self._calculate_dependency_depth(node_id, set())
            analysis["dependency_depth"][node_id] = depth
        
        # Calculate complexity metrics
        analysis["complexity_metrics"] = {
            "max_depth": max(analysis["dependency_depth"].values()) if analysis["dependency_depth"] else 0,
            "avg_depth": sum(analysis["dependency_depth"].values()) / len(nodes) if nodes else 0,
            "total_edges": len(self.dependency_graph.get("edges", {}))
        }
        
        # Identify bottleneck nodes (nodes with many dependents)
        dependents_count = defaultdict(int)
        for node_id, node_data in nodes.items():
            for dep in node_data.get("dependencies", []):
                dependents_count[dep] += 1
        
        # Nodes with 3+ dependents are bottlenecks
        analysis["bottleneck_nodes"] = [
            node for node, count in dependents_count.items() if count >= 3
        ]
        
        return analysis
    
    def _detect_and_resolve_cycles(self) -> List[Dict[str, Any]]:
        """Detect and resolve dependency cycles with recursive resolution."""
        cycles_found = []
        nodes = self.dependency_graph.get("nodes", {})
        
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def dfs_cycle_detection(node_id: str, path: List[str]) -> List[str]:
            if node_id in rec_stack:
                # Found a cycle - return the cycle path
                cycle_start_idx = path.index(node_id)
                return path[cycle_start_idx:] + [node_id]
            
            if node_id in visited:
                return []
            
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            # Check dependencies
            for dep in nodes.get(node_id, {}).get("dependencies", []):
                cycle = dfs_cycle_detection(dep, path.copy())
                if cycle:
                    return cycle
            
            rec_stack.remove(node_id)
            return []
        
        # Check each node for cycles
        for node_id in nodes:
            if node_id not in visited:
                cycle = dfs_cycle_detection(node_id, [])
                if cycle:
                    cycle_info = {
                        "cycle_nodes": cycle,
                        "cycle_length": len(cycle) - 1,
                        "resolution_strategy": self._design_cycle_resolution(cycle),
                        "detected_at": datetime.now().isoformat()
                    }
                    cycles_found.append(cycle_info)
                    
                    # Apply resolution
                    self._apply_cycle_resolution(cycle_info)
        
        return cycles_found
    
    def _optimize_dependency_paths(self) -> List[Dict[str, Any]]:
        """Optimize dependency paths with recursive improvement."""
        optimizations = []
        nodes = self.dependency_graph.get("nodes", {})
        
        # Find longest dependency chains
        for node_id in nodes:
            chain_analysis = self._analyze_dependency_chain(node_id)
            
            if chain_analysis["chain_length"] > 3:  # Optimization threshold
                optimization = {
                    "node": node_id,
                    "original_chain_length": chain_analysis["chain_length"],
                    "optimization_type": "chain_reduction",
                    "potential_improvement": chain_analysis["chain_length"] - 2
                }
                
                # Apply optimization
                new_chain_length = self._apply_chain_optimization(node_id, chain_analysis)
                optimization["new_chain_length"] = new_chain_length
                optimization["actual_improvement"] = chain_analysis["chain_length"] - new_chain_length
                
                optimizations.append(optimization)
        
        return optimizations
    
    def _apply_recursive_updates(self) -> List[Dict[str, Any]]:
        """Apply recursive updates to the dependency graph."""
        updates = []
        
        # Update based on patterns identified in previous cycles
        for pattern in self.update_patterns[-5:]:  # Recent patterns
            update = self._apply_pattern_based_update(pattern)
            if update:
                updates.append(update)
        
        # Apply compounding improvements
        compounding_updates = self._apply_compounding_improvements()
        updates.extend(compounding_updates)
        
        # Update graph metadata
        self._update_graph_metadata(updates)
        
        return updates
    
    def _validate_graph_integrity(self) -> Dict[str, Any]:
        """Validate graph integrity with recursive checking."""
        validation = {
            "score": 0.0,
            "issues_found": [],
            "recursive_validation_depth": self.performance_metrics["recursive_depth"]
        }
        
        nodes = self.dependency_graph.get("nodes", {})
        
        # Check for orphaned nodes
        all_dependencies = set()
        for node_data in nodes.values():
            all_dependencies.update(node_data.get("dependencies", []))
        
        orphaned_nodes = [node for node in all_dependencies if node not in nodes]
        if orphaned_nodes:
            validation["issues_found"].append({
                "type": "orphaned_dependencies",
                "nodes": orphaned_nodes,
                "severity": "high"
            })
        
        # Check for self-dependencies
        self_dependent = [
            node_id for node_id, node_data in nodes.items()
            if node_id in node_data.get("dependencies", [])
        ]
        if self_dependent:
            validation["issues_found"].append({
                "type": "self_dependencies",
                "nodes": self_dependent,
                "severity": "medium"
            })
        
        # Calculate integrity score
        total_checks = 3  # Number of validation checks
        issues_weight = len(validation["issues_found"]) / total_checks if total_checks > 0 else 0
        validation["score"] = max(0.0, 1.0 - issues_weight) * 100
        
        return validation
    
    def _scan_for_new_dependencies(self) -> List[Dict[str, Any]]:
        """Scan for new dependencies to add to the graph."""
        # Simulate discovery of new dependencies
        new_deps = [
            {
                "node": f"new_module_{datetime.now().strftime('%H%M%S')}",
                "type": "service",
                "dependencies": ["core_module"],
                "discovered_via": "autonomous_scanning"
            }
        ]
        
        # Add new dependencies to graph
        for dep in new_deps:
            self.dependency_graph["nodes"][dep["node"]] = {
                "type": dep["type"],
                "version": "1.0",
                "dependencies": dep["dependencies"],
                "discovered_at": datetime.now().isoformat()
            }
        
        self._rebuild_edge_relationships()
        return new_deps
    
    def _pre_identify_cycles(self) -> List[List[str]]:
        """Pre-identify potential cycles before main analysis."""
        potential_cycles = []
        nodes = self.dependency_graph.get("nodes", {})
        
        # Check cache first
        cache_key = str(sorted(nodes.keys()))
        if cache_key in self.cycle_detection_cache:
            return self.cycle_detection_cache[cache_key]
        
        # Simple cycle detection for pre-analysis
        for node_id in nodes:
            visited = set()
            if self._has_potential_cycle(node_id, visited, []):
                potential_cycles.append([node_id])
        
        # Cache results
        self.cycle_detection_cache[cache_key] = potential_cycles
        return potential_cycles
    
    def _identify_optimization_candidates(self) -> List[Dict[str, Any]]:
        """Identify candidates for optimization."""
        candidates = []
        nodes = self.dependency_graph.get("nodes", {})
        
        # Find nodes with high dependency count
        for node_id, node_data in nodes.items():
            dep_count = len(node_data.get("dependencies", []))
            if dep_count > 2:  # Candidate threshold
                candidates.append({
                    "node": node_id,
                    "dependency_count": dep_count,
                    "optimization_potential": dep_count - 2
                })
        
        return candidates
    
    def _calculate_dependency_depth(self, node_id: str, visited: Set[str]) -> int:
        """Calculate recursive dependency depth for a node."""
        if node_id in visited:
            return 0  # Avoid infinite recursion
        
        visited.add(node_id)
        nodes = self.dependency_graph.get("nodes", {})
        
        if node_id not in nodes:
            return 0
        
        dependencies = nodes[node_id].get("dependencies", [])
        if not dependencies:
            return 1
        
        max_depth = 0
        for dep in dependencies:
            depth = self._calculate_dependency_depth(dep, visited.copy())
            max_depth = max(max_depth, depth)
        
        return max_depth + 1
    
    def _design_cycle_resolution(self, cycle: List[str]) -> List[str]:
        """Design resolution strategy for dependency cycle."""
        strategies = []
        
        if len(cycle) <= 3:
            strategies.append("remove_weakest_dependency")
        else:
            strategies.extend(["introduce_interface_layer", "split_cyclic_component"])
        
        strategies.append("add_dependency_injection")
        return strategies
    
    def _apply_cycle_resolution(self, cycle_info: Dict[str, Any]):
        """Apply cycle resolution to the graph."""
        cycle_nodes = cycle_info["cycle_nodes"]
        strategy = cycle_info["resolution_strategy"][0]  # Use first strategy
        
        if strategy == "remove_weakest_dependency":
            # Remove the last dependency in the cycle
            if len(cycle_nodes) >= 2:
                from_node = cycle_nodes[-2]
                to_node = cycle_nodes[-1]
                
                nodes = self.dependency_graph.get("nodes", {})
                if from_node in nodes:
                    deps = nodes[from_node].get("dependencies", [])
                    if to_node in deps:
                        deps.remove(to_node)
                        self.logger.info(f"Removed cyclic dependency: {from_node} -> {to_node}")
        
        # Rebuild edges after modification
        self._rebuild_edge_relationships()
    
    def _analyze_dependency_chain(self, node_id: str) -> Dict[str, Any]:
        """Analyze the dependency chain for a node."""
        chain = []
        visited = set()
        
        def build_chain(current_node: str):
            if current_node in visited:
                return
            
            visited.add(current_node)
            chain.append(current_node)
            
            nodes = self.dependency_graph.get("nodes", {})
            if current_node in nodes:
                for dep in nodes[current_node].get("dependencies", []):
                    build_chain(dep)
        
        build_chain(node_id)
        
        return {
            "chain_length": len(chain),
            "chain_nodes": chain,
            "complexity_score": len(chain) * len(visited)
        }
    
    def _apply_chain_optimization(self, node_id: str, chain_analysis: Dict[str, Any]) -> int:
        """Apply optimization to reduce dependency chain length."""
        nodes = self.dependency_graph.get("nodes", {})
        
        if node_id not in nodes:
            return chain_analysis["chain_length"]
        
        # Simple optimization: remove redundant intermediate dependencies
        deps = nodes[node_id].get("dependencies", [])
        if len(deps) > 2:
            # Keep only the most critical dependencies
            optimized_deps = deps[:2]  # Keep first two
            nodes[node_id]["dependencies"] = optimized_deps
            
            self._rebuild_edge_relationships()
            
            # Recalculate chain length
            new_analysis = self._analyze_dependency_chain(node_id)
            return new_analysis["chain_length"]
        
        return chain_analysis["chain_length"]
    
    def _apply_pattern_based_update(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply updates based on identified patterns."""
        pattern_type = pattern.get("type", "unknown")
        
        if pattern_type == "high_dependency_count":
            # Reduce dependencies for high-dependency nodes
            node_id = pattern.get("node_id")
            if node_id:
                nodes = self.dependency_graph.get("nodes", {})
                if node_id in nodes:
                    deps = nodes[node_id].get("dependencies", [])
                    if len(deps) > 3:
                        # Reduce to 3 dependencies
                        nodes[node_id]["dependencies"] = deps[:3]
                        return {
                            "type": "dependency_reduction",
                            "node": node_id,
                            "old_count": len(deps),
                            "new_count": 3
                        }
        
        return None
    
    def _apply_compounding_improvements(self) -> List[Dict[str, Any]]:
        """Apply improvements that compound over time."""
        improvements = []
        
        # Increase optimization level with each cycle
        current_level = self.dependency_graph["metadata"]["optimization_level"]
        new_level = min(current_level + 1, 10)  # Cap at level 10
        
        self.dependency_graph["metadata"]["optimization_level"] = new_level
        
        improvements.append({
            "type": "optimization_level_increase",
            "old_level": current_level,
            "new_level": new_level,
            "compounding_factor": new_level / max(1, current_level)
        })
        
        return improvements
    
    def _update_graph_metadata(self, updates: List[Dict[str, Any]]):
        """Update graph metadata with recent changes."""
        self.dependency_graph["metadata"].update({
            "last_updated": datetime.now().isoformat(),
            "updates_applied": len(updates),
            "recursive_depth": self.performance_metrics["recursive_depth"]
        })
    
    def _rebuild_edge_relationships(self):
        """Rebuild edge relationships from node dependencies."""
        edges = {}
        nodes = self.dependency_graph.get("nodes", {})
        
        for node_id, node_data in nodes.items():
            for dep in node_data.get("dependencies", []):
                edge_id = f"{node_id}->{dep}"
                edges[edge_id] = {
                    "from": node_id,
                    "to": dep,
                    "type": "dependency",
                    "weight": 1.0
                }
        
        self.dependency_graph["edges"] = edges
    
    def _has_potential_cycle(self, node_id: str, visited: Set[str], path: List[str]) -> bool:
        """Check if node has potential for creating cycles."""
        if node_id in visited:
            return True
        
        visited.add(node_id)
        path.append(node_id)
        
        nodes = self.dependency_graph.get("nodes", {})
        if node_id in nodes:
            for dep in nodes[node_id].get("dependencies", []):
                if dep in path:  # Immediate cycle
                    return True
                if self._has_potential_cycle(dep, visited.copy(), path.copy()):
                    return True
        
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current engine status."""
        return {
            "name": self.name,
            "is_running": self.is_running,
            "metrics": self.performance_metrics,
            "graph_nodes": len(self.dependency_graph.get("nodes", {})),
            "graph_edges": len(self.dependency_graph.get("edges", {})),
            "optimization_history": len(self.optimization_history),
            "update_patterns": len(self.update_patterns),
            "last_execution": self.last_execution
        }