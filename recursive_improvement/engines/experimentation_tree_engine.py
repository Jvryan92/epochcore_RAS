"""
Engine 2: Autonomous Experimentation Tree Engine
Branch expansion with +0.25 interval pruning of underperforming branches
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import uuid

from ..base import RecursiveEngine, CompoundingAction


class ExperimentBranch:
    """Represents an experiment branch in the autonomous tree."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.config = config or {}
        self.created_at = datetime.now()
        self.last_updated = datetime.now()
        self.performance_score = 0.0
        self.children: List['ExperimentBranch'] = []
        self.parent: Optional['ExperimentBranch'] = None
        self.status = "active"  # active, pruned, completed
        self.metrics = {}
        
    def add_child(self, child: 'ExperimentBranch'):
        """Add a child branch."""
        child.parent = self
        self.children.append(child)
        
    def update_performance(self, score: float, metrics: Dict[str, Any] = None):
        """Update branch performance."""
        self.performance_score = score
        self.metrics.update(metrics or {})
        self.last_updated = datetime.now()
        
    def should_prune(self, threshold: float = 0.3) -> bool:
        """Determine if branch should be pruned."""
        return self.performance_score < threshold and len(self.children) == 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert branch to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "performance_score": self.performance_score,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "children_count": len(self.children),
            "metrics": self.metrics
        }


class AutonomousExperimentationTreeEngine(RecursiveEngine):
    """
    Autonomous Experimentation Tree Engine that expands experiment branches
    and prunes underperforming branches in parallel at +0.25 intervals.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("experimentation_tree_engine", config)
        self.experiment_tree: Optional[ExperimentBranch] = None
        self.active_branches: List[ExperimentBranch] = []
        self.pruned_branches: List[ExperimentBranch] = []
        self.expansion_queue: List[Dict[str, Any]] = []
        
    def initialize(self) -> bool:
        """Initialize the experimentation tree engine."""
        try:
            self.logger.info("Initializing Autonomous Experimentation Tree Engine")
            
            # Create root experiment branch
            self.experiment_tree = ExperimentBranch(
                "root_experiment",
                {"type": "root", "auto_expand": True}
            )
            self.active_branches.append(self.experiment_tree)
            
            # Set up compounding actions
            expansion_action = CompoundingAction(
                name="branch_expansion",
                action=self.execute_main_action,
                interval=1.0,  # Weekly expansion
                pre_action=self.execute_pre_action,
                pre_interval=0.25,  # +0.25 interval pruning
                metadata={"type": "experimentation", "recursive": True}
            )
            
            self.add_compounding_action(expansion_action)
            
            # Initialize with baseline experiments
            self._create_baseline_experiments()
            
            self.logger.info("Autonomous Experimentation Tree Engine initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize experimentation tree engine: {e}")
            return False
    
    def execute_main_action(self) -> Dict[str, Any]:
        """Execute the main branch expansion action."""
        self.logger.info("Executing autonomous experiment branch expansion")
        
        expansion_result = {
            "timestamp": datetime.now().isoformat(),
            "action_type": "branch_expansion",
            "branches_created": [],
            "experiments_launched": [],
            "total_active_branches": len(self.active_branches)
        }
        
        try:
            # Analyze current tree performance
            tree_analysis = self._analyze_tree_performance()
            expansion_result["tree_analysis"] = tree_analysis
            
            # Identify expansion opportunities
            opportunities = self._identify_expansion_opportunities()
            expansion_result["opportunities"] = opportunities
            
            # Create new experiment branches
            new_branches = self._create_experiment_branches(opportunities)
            expansion_result["branches_created"] = [b.to_dict() for b in new_branches]
            
            # Launch experiments on new branches
            launched_experiments = self._launch_experiments(new_branches)
            expansion_result["experiments_launched"] = launched_experiments
            
            # Update expansion queue for next cycle
            self._update_expansion_queue()
            
            self.logger.info(f"Branch expansion completed - {len(new_branches)} new branches created")
            return expansion_result
            
        except Exception as e:
            self.logger.error(f"Branch expansion failed: {e}")
            expansion_result["error"] = str(e)
            return expansion_result
    
    def execute_pre_action(self) -> Dict[str, Any]:
        """Execute pre-action pruning at +0.25 interval."""
        self.logger.info("Executing parallel branch pruning (+0.25 interval)")
        
        pruning_result = {
            "timestamp": datetime.now().isoformat(),
            "action_type": "parallel_pruning",
            "branches_evaluated": 0,
            "branches_pruned": [],
            "pruning_criteria": {}
        }
        
        try:
            # Evaluate all active branches for pruning
            pruning_candidates = []
            for branch in self.active_branches:
                if self._evaluate_branch_for_pruning(branch):
                    pruning_candidates.append(branch)
            
            pruning_result["branches_evaluated"] = len(self.active_branches)
            pruning_result["pruning_candidates"] = len(pruning_candidates)
            
            # Prune underperforming branches
            pruned = self._prune_branches(pruning_candidates)
            pruning_result["branches_pruned"] = [b.to_dict() for b in pruned]
            
            # Update pruning criteria based on results
            updated_criteria = self._update_pruning_criteria(pruned)
            pruning_result["pruning_criteria"] = updated_criteria
            
            # Optimize remaining branches
            optimized = self._optimize_remaining_branches()
            pruning_result["optimizations_applied"] = optimized
            
            self.logger.info(f"Parallel pruning completed - {len(pruned)} branches pruned")
            return pruning_result
            
        except Exception as e:
            self.logger.error(f"Parallel pruning failed: {e}")
            pruning_result["error"] = str(e)
            return pruning_result
    
    def _analyze_tree_performance(self) -> Dict[str, Any]:
        """Analyze overall tree performance."""
        if not self.active_branches:
            return {"status": "no_active_branches"}
        
        total_score = sum(b.performance_score for b in self.active_branches)
        avg_score = total_score / len(self.active_branches)
        
        best_branch = max(self.active_branches, key=lambda b: b.performance_score)
        worst_branch = min(self.active_branches, key=lambda b: b.performance_score)
        
        analysis = {
            "total_branches": len(self.active_branches),
            "average_performance": avg_score,
            "best_performer": best_branch.to_dict(),
            "worst_performer": worst_branch.to_dict(),
            "pruned_total": len(self.pruned_branches),
            "tree_health": "healthy" if avg_score > 0.6 else "needs_optimization"
        }
        
        return analysis
    
    def _identify_expansion_opportunities(self) -> List[Dict[str, Any]]:
        """Identify opportunities for branch expansion."""
        opportunities = []
        
        # Look for high-performing branches that can be expanded
        for branch in self.active_branches:
            if branch.performance_score > 0.7:
                opportunities.append({
                    "type": "high_performer_expansion",
                    "parent_branch": branch.id,
                    "reason": "Strong performance indicates expansion potential",
                    "priority": "high"
                })
        
        # Look for gaps in experiment coverage
        if len(self.active_branches) < 10:  # Max branches limit
            opportunities.append({
                "type": "coverage_gap",
                "parent_branch": self.experiment_tree.id if self.experiment_tree else None,
                "reason": "Insufficient experiment coverage",
                "priority": "medium"
            })
        
        # Generate random exploration opportunities
        opportunities.append({
            "type": "random_exploration",
            "parent_branch": None,
            "reason": "Autonomous exploration of new experiment spaces",
            "priority": "low"
        })
        
        return opportunities
    
    def _create_experiment_branches(self, opportunities: List[Dict[str, Any]]) -> List[ExperimentBranch]:
        """Create new experiment branches based on opportunities."""
        new_branches = []
        
        for i, opportunity in enumerate(opportunities):
            branch_name = f"experiment_{opportunity['type']}_{i}"
            branch_config = {
                "opportunity": opportunity,
                "auto_generated": True,
                "expansion_timestamp": datetime.now().isoformat()
            }
            
            new_branch = ExperimentBranch(branch_name, branch_config)
            
            # Find parent branch if specified
            if opportunity.get("parent_branch"):
                parent = self._find_branch_by_id(opportunity["parent_branch"])
                if parent:
                    parent.add_child(new_branch)
            
            new_branches.append(new_branch)
            self.active_branches.append(new_branch)
        
        return new_branches
    
    def _launch_experiments(self, branches: List[ExperimentBranch]) -> List[Dict[str, Any]]:
        """Launch experiments on new branches."""
        launched = []
        
        for branch in branches:
            experiment = {
                "branch_id": branch.id,
                "experiment_type": "autonomous_optimization",
                "parameters": self._generate_experiment_parameters(branch),
                "launched_at": datetime.now().isoformat(),
                "expected_duration": "1_week"
            }
            
            # Simulate experiment launch
            self._simulate_experiment_launch(branch, experiment)
            launched.append(experiment)
        
        return launched
    
    def _generate_experiment_parameters(self, branch: ExperimentBranch) -> Dict[str, Any]:
        """Generate experiment parameters for a branch."""
        base_params = {
            "optimization_target": "performance_improvement",
            "learning_rate": 0.01,
            "batch_size": 32,
            "exploration_factor": 0.1
        }
        
        # Customize based on branch type
        if "high_performer" in branch.name:
            base_params["exploration_factor"] = 0.05  # Less exploration for proven branches
        elif "random_exploration" in branch.name:
            base_params["exploration_factor"] = 0.2   # More exploration for new areas
        
        return base_params
    
    def _simulate_experiment_launch(self, branch: ExperimentBranch, experiment: Dict[str, Any]):
        """Simulate launching an experiment on a branch."""
        # Simulate initial performance based on experiment type
        initial_score = 0.5  # Base score
        
        if "high_performer" in branch.name:
            initial_score = 0.7  # Start higher for proven approaches
        elif "random_exploration" in branch.name:
            initial_score = 0.3  # Start lower for exploration
        
        branch.update_performance(initial_score, {
            "experiment_started": True,
            "launch_timestamp": experiment["launched_at"]
        })
    
    def _evaluate_branch_for_pruning(self, branch: ExperimentBranch) -> bool:
        """Evaluate if a branch should be pruned."""
        # Don't prune root branch
        if branch == self.experiment_tree:
            return False
        
        # Don't prune recently created branches
        age = datetime.now() - branch.created_at
        if age < timedelta(days=1):
            return False
        
        # Prune based on performance threshold
        return branch.should_prune(threshold=0.4)
    
    def _prune_branches(self, candidates: List[ExperimentBranch]) -> List[ExperimentBranch]:
        """Prune underperforming branches."""
        pruned = []
        
        for branch in candidates:
            branch.status = "pruned"
            self.active_branches.remove(branch)
            self.pruned_branches.append(branch)
            pruned.append(branch)
            
            self.logger.info(f"Pruned branch {branch.name} (score: {branch.performance_score})")
        
        return pruned
    
    def _update_pruning_criteria(self, pruned: List[ExperimentBranch]) -> Dict[str, Any]:
        """Update pruning criteria based on pruned branches."""
        if not pruned:
            return {"status": "no_updates"}
        
        avg_pruned_score = sum(b.performance_score for b in pruned) / len(pruned)
        
        updated_criteria = {
            "pruned_count": len(pruned),
            "avg_pruned_score": avg_pruned_score,
            "new_threshold": max(0.3, avg_pruned_score - 0.1),  # Lower threshold slightly
            "criteria_updated": True
        }
        
        return updated_criteria
    
    def _optimize_remaining_branches(self) -> List[Dict[str, Any]]:
        """Optimize remaining branches after pruning."""
        optimizations = []
        
        for branch in self.active_branches:
            if branch.performance_score < 0.6:  # Could be improved
                optimization = {
                    "branch_id": branch.id,
                    "current_score": branch.performance_score,
                    "optimization_type": "performance_boost",
                    "applied_at": datetime.now().isoformat()
                }
                
                # Simulate optimization boost
                branch.update_performance(
                    min(1.0, branch.performance_score + 0.1),
                    {"optimization_applied": True}
                )
                
                optimization["new_score"] = branch.performance_score
                optimizations.append(optimization)
        
        return optimizations
    
    def _find_branch_by_id(self, branch_id: str) -> Optional[ExperimentBranch]:
        """Find a branch by its ID."""
        for branch in self.active_branches:
            if branch.id == branch_id:
                return branch
        return None
    
    def _create_baseline_experiments(self):
        """Create initial baseline experiments."""
        baseline_configs = [
            {"name": "performance_optimization", "focus": "system_performance"},
            {"name": "user_experience", "focus": "ux_improvement"},
            {"name": "scalability_test", "focus": "load_handling"}
        ]
        
        for config in baseline_configs:
            branch = ExperimentBranch(config["name"], config)
            self.experiment_tree.add_child(branch)
            self.active_branches.append(branch)
            
            # Simulate initial performance
            branch.update_performance(0.6, {"baseline": True})
    
    def _update_expansion_queue(self):
        """Update the expansion queue for next cycle."""
        # Clear old queue and add new expansion ideas
        self.expansion_queue.clear()
        
        # Add expansion ideas based on current tree state
        for branch in self.active_branches:
            if branch.performance_score > 0.8:
                self.expansion_queue.append({
                    "parent_branch": branch.id,
                    "expansion_type": "high_performer_derivative",
                    "priority": 1
                })
    
    def get_tree_status(self) -> Dict[str, Any]:
        """Get current tree status."""
        return {
            "active_branches": len(self.active_branches),
            "pruned_branches": len(self.pruned_branches), 
            "expansion_queue_size": len(self.expansion_queue),
            "tree_depth": self._calculate_tree_depth(),
            "overall_performance": self._calculate_overall_performance()
        }
    
    def _calculate_tree_depth(self) -> int:
        """Calculate maximum depth of the experiment tree."""
        def get_depth(branch, current_depth=0):
            if not branch.children:
                return current_depth
            return max(get_depth(child, current_depth + 1) for child in branch.children)
        
        return get_depth(self.experiment_tree) if self.experiment_tree else 0
    
    def _calculate_overall_performance(self) -> float:
        """Calculate overall tree performance."""
        if not self.active_branches:
            return 0.0
        
        total_score = sum(b.performance_score for b in self.active_branches)
        return total_score / len(self.active_branches)