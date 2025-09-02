#!/usr/bin/env python3
"""
EpochCore RAS Reinforcement Learning Agent
Implements RL agent that proposes and tests workflow/code changes based on feedback
"""

import numpy as np
import json
import random
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ReinforcementLearningAgent:
    """
    RL agent that learns from system feedback to propose workflow improvements.
    Uses a simple Q-learning approach to optimize workflow decisions.
    """
    
    def __init__(self):
        self.learning_rate = 0.1
        self.discount_factor = 0.9
        self.epsilon = 0.1  # exploration rate
        self.epsilon_decay = 0.995
        
        # State space: system metrics and conditions
        self.state_features = [
            "cpu_usage", "memory_usage", "active_agents", "dag_backlog", 
            "error_rate", "response_time", "throughput"
        ]
        
        # Action space: workflow modifications
        self.actions = [
            "increase_agent_workers",
            "decrease_agent_workers", 
            "optimize_dag_scheduling",
            "adjust_batch_sizes",
            "modify_timeout_values",
            "change_priority_weights",
            "enable_caching",
            "optimize_resource_allocation"
        ]
        
        # Q-table for state-action values
        self.q_table = {}
        self.experience_buffer = []
        self.max_buffer_size = 1000
        
        # Performance history for learning
        self.performance_history = []
        self.baseline_performance = None
        
        logger.info("Reinforcement Learning Agent initialized")
    
    def propose_improvements(self, system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze system metrics and propose workflow improvements using RL.
        """
        logger.info("RL Agent analyzing system metrics for improvements")
        
        try:
            # Convert metrics to state representation
            current_state = self._metrics_to_state(system_metrics)
            
            # Select action using epsilon-greedy policy
            action_idx = self._select_action(current_state)
            action = self.actions[action_idx]
            
            # Generate improvement based on action
            improvements = self._generate_improvement_from_action(action, system_metrics)
            
            # Store experience for learning
            self._store_experience(current_state, action_idx, system_metrics)
            
            # Update Q-table based on recent experiences
            self._update_q_table()
            
            # Decay exploration rate
            self.epsilon = max(0.01, self.epsilon * self.epsilon_decay)
            
            result = {
                "improvements_found": len(improvements) > 0,
                "improvements": improvements,
                "selected_action": action,
                "state": current_state,
                "exploration_rate": self.epsilon,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"RL Agent proposed {len(improvements)} improvements using action: {action}")
            return result
            
        except Exception as e:
            logger.error(f"Error in RL agent improvement proposal: {str(e)}")
            return {
                "improvements_found": False,
                "improvements": [],
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def learn_from_feedback(self, action: str, reward: float, new_metrics: Dict[str, Any]):
        """
        Learn from the results of applying a workflow change.
        """
        logger.info(f"RL Agent learning from feedback: action={action}, reward={reward}")
        
        try:
            # Find the most recent experience with this action
            action_idx = self.actions.index(action)
            
            for experience in reversed(self.experience_buffer):
                if experience["action"] == action_idx:
                    # Update the experience with the reward
                    experience["reward"] = reward
                    experience["next_state"] = self._metrics_to_state(new_metrics)
                    break
            
            # Update performance history
            self.performance_history.append({
                "action": action,
                "reward": reward,
                "timestamp": datetime.now().isoformat(),
                "metrics": new_metrics
            })
            
            # Update baseline performance if this is better
            if self.baseline_performance is None or reward > self.baseline_performance:
                self.baseline_performance = reward
                logger.info(f"New baseline performance: {reward}")
            
        except Exception as e:
            logger.error(f"Error learning from feedback: {str(e)}")
    
    def _metrics_to_state(self, metrics: Dict[str, Any]) -> str:
        """Convert system metrics to a discrete state representation."""
        try:
            # Extract numeric values from metrics
            cpu = metrics.get("cpu_percent", 50)
            memory = metrics.get("memory_percent", 50)
            errors = metrics.get("validation_errors", 0)
            
            # Discretize continuous values
            cpu_level = "low" if cpu < 30 else "medium" if cpu < 70 else "high"
            memory_level = "low" if memory < 40 else "medium" if memory < 80 else "high"
            error_level = "none" if errors == 0 else "low" if errors < 3 else "high"
            
            # Simulate other metrics based on available data
            # In a real implementation, these would come from actual system monitoring
            agent_load = "normal"  # Could be derived from system status
            dag_status = "normal"  # Could be derived from DAG execution times
            
            state = f"cpu:{cpu_level}_mem:{memory_level}_err:{error_level}_agents:{agent_load}_dags:{dag_status}"
            return state
            
        except Exception as e:
            logger.error(f"Error converting metrics to state: {str(e)}")
            return "cpu:medium_mem:medium_err:none_agents:normal_dags:normal"  # default state
    
    def _select_action(self, state: str) -> int:
        """Select action using epsilon-greedy policy."""
        if random.random() < self.epsilon:
            # Explore: random action
            return random.randint(0, len(self.actions) - 1)
        else:
            # Exploit: best known action for this state
            if state in self.q_table:
                q_values = self.q_table[state]
                return np.argmax(q_values)
            else:
                # Initialize Q-values for new state
                self.q_table[state] = np.zeros(len(self.actions))
                return random.randint(0, len(self.actions) - 1)
    
    def _store_experience(self, state: str, action: int, metrics: Dict[str, Any]):
        """Store experience in buffer for learning."""
        experience = {
            "state": state,
            "action": action,
            "reward": None,  # Will be set when feedback is received
            "next_state": None,  # Will be set when feedback is received
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        }
        
        self.experience_buffer.append(experience)
        
        # Trim buffer if too large
        if len(self.experience_buffer) > self.max_buffer_size:
            self.experience_buffer = self.experience_buffer[-self.max_buffer_size:]
    
    def _update_q_table(self):
        """Update Q-table using experiences with rewards."""
        updated_count = 0
        
        for experience in self.experience_buffer:
            if experience["reward"] is not None and experience["next_state"] is not None:
                state = experience["state"]
                action = experience["action"]
                reward = experience["reward"]
                next_state = experience["next_state"]
                
                # Initialize Q-values if needed
                if state not in self.q_table:
                    self.q_table[state] = np.zeros(len(self.actions))
                if next_state not in self.q_table:
                    self.q_table[next_state] = np.zeros(len(self.actions))
                
                # Q-learning update
                current_q = self.q_table[state][action]
                max_next_q = np.max(self.q_table[next_state])
                new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
                self.q_table[state][action] = new_q
                
                updated_count += 1
        
        if updated_count > 0:
            logger.info(f"Updated Q-table with {updated_count} experiences")
    
    def _generate_improvement_from_action(self, action: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific improvement recommendations based on the selected action."""
        improvements = []
        
        try:
            if action == "increase_agent_workers":
                improvements.append({
                    "type": "rl_workflow",
                    "workflow_change": "increase_agent_pool",
                    "description": "Increase agent worker pool size for better throughput",
                    "parameters": {"agent_pool_size": "+2"},
                    "expected_impact": "Improved parallel processing capability",
                    "confidence": 0.7,
                    "action": action
                })
            
            elif action == "decrease_agent_workers":
                improvements.append({
                    "type": "rl_workflow",
                    "workflow_change": "decrease_agent_pool",
                    "description": "Decrease agent worker pool size to reduce resource usage",
                    "parameters": {"agent_pool_size": "-1"},
                    "expected_impact": "Reduced resource consumption",
                    "confidence": 0.6,
                    "action": action
                })
            
            elif action == "optimize_dag_scheduling":
                improvements.append({
                    "type": "rl_workflow",
                    "workflow_change": "optimize_scheduling",
                    "description": "Optimize DAG task scheduling algorithm",
                    "parameters": {"scheduling_strategy": "priority_based"},
                    "expected_impact": "Better task prioritization and execution order",
                    "confidence": 0.8,
                    "action": action
                })
            
            elif action == "adjust_batch_sizes":
                batch_adjustment = "+1" if metrics.get("cpu_percent", 50) < 50 else "-1"
                improvements.append({
                    "type": "rl_workflow",
                    "workflow_change": "adjust_batching",
                    "description": f"Adjust processing batch sizes for optimal throughput",
                    "parameters": {"batch_size_adjustment": batch_adjustment},
                    "expected_impact": "Optimized I/O and processing efficiency",
                    "confidence": 0.75,
                    "action": action
                })
            
            elif action == "modify_timeout_values":
                improvements.append({
                    "type": "rl_workflow",
                    "workflow_change": "timeout_optimization",
                    "description": "Optimize timeout values based on observed performance",
                    "parameters": {"timeout_adjustment": "dynamic"},
                    "expected_impact": "Better balance between reliability and responsiveness",
                    "confidence": 0.65,
                    "action": action
                })
            
            elif action == "change_priority_weights":
                improvements.append({
                    "type": "rl_workflow",
                    "workflow_change": "priority_rebalancing",
                    "description": "Adjust task priority weights based on performance data",
                    "parameters": {"priority_rebalance": "cpu_optimized"},
                    "expected_impact": "Improved resource utilization",
                    "confidence": 0.7,
                    "action": action
                })
            
            elif action == "enable_caching":
                improvements.append({
                    "type": "rl_workflow",
                    "workflow_change": "enable_caching",
                    "description": "Enable intelligent caching for frequently accessed data",
                    "parameters": {"cache_strategy": "lru", "cache_size": "moderate"},
                    "expected_impact": "Reduced computation and I/O overhead",
                    "confidence": 0.8,
                    "action": action
                })
            
            elif action == "optimize_resource_allocation":
                improvements.append({
                    "type": "rl_workflow",
                    "workflow_change": "resource_optimization",
                    "description": "Optimize resource allocation based on current workload",
                    "parameters": {"allocation_strategy": "workload_adaptive"},
                    "expected_impact": "Better resource utilization and performance",
                    "confidence": 0.75,
                    "action": action
                })
            
        except Exception as e:
            logger.error(f"Error generating improvement for action {action}: {str(e)}")
        
        return improvements
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get statistics about the RL agent's learning progress."""
        return {
            "total_experiences": len(self.experience_buffer),
            "q_table_size": len(self.q_table),
            "exploration_rate": self.epsilon,
            "performance_history_size": len(self.performance_history),
            "baseline_performance": self.baseline_performance,
            "actions_available": len(self.actions),
            "recent_performance": self.performance_history[-10:] if self.performance_history else []
        }
    
    def calculate_reward(self, old_metrics: Dict[str, Any], new_metrics: Dict[str, Any]) -> float:
        """
        Calculate reward based on improvement in system metrics.
        Used when actual performance feedback is available.
        """
        try:
            reward = 0.0
            
            # CPU usage improvement (lower is better)
            cpu_old = old_metrics.get("cpu_percent", 50)
            cpu_new = new_metrics.get("cpu_percent", 50)
            cpu_improvement = (cpu_old - cpu_new) / 100.0  # Normalize
            reward += cpu_improvement * 2.0
            
            # Memory usage improvement (lower is better)
            mem_old = old_metrics.get("memory_percent", 50)
            mem_new = new_metrics.get("memory_percent", 50)
            mem_improvement = (mem_old - mem_new) / 100.0  # Normalize
            reward += mem_improvement * 1.5
            
            # Error reduction (fewer errors is better)
            errors_old = old_metrics.get("validation_errors", 0)
            errors_new = new_metrics.get("validation_errors", 0)
            error_improvement = errors_old - errors_new
            reward += error_improvement * 3.0  # Heavily weight error reduction
            
            # System status (operational is better)
            status_old = 1.0 if old_metrics.get("status") == "operational" else 0.0
            status_new = 1.0 if new_metrics.get("status") == "operational" else 0.0
            status_improvement = status_new - status_old
            reward += status_improvement * 5.0  # Heavily weight system stability
            
            # Normalize reward to [-5, 5] range
            reward = max(-5.0, min(5.0, reward))
            
            return reward
            
        except Exception as e:
            logger.error(f"Error calculating reward: {str(e)}")
            return 0.0


if __name__ == "__main__":
    # Test the RL agent
    agent = ReinforcementLearningAgent()
    
    # Simulate system metrics
    test_metrics = {
        "cpu_percent": 65,
        "memory_percent": 45,
        "validation_errors": 0,
        "status": "operational"
    }
    
    result = agent.propose_improvements(test_metrics)
    print(json.dumps(result, indent=2))