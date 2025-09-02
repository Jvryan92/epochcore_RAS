#!/usr/bin/env python3
"""
EpochCore RAS Agent Management System

Manages agent registry, capabilities, and performance optimization.
Includes recursive improvement hooks for autonomous agent enhancement.
"""

import random
import time
from datetime import datetime
from typing import Dict, List, Any
from recursive_improvement import ImprovementStrategy, SubsystemHook, get_framework


class Agent:
    """Represents an autonomous agent in the system."""
    
    def __init__(self, agent_id: str, skills: List[str], performance_score: float = 0.5):
        self.id = agent_id
        self.skills = skills
        self.performance_score = performance_score  # 0.0 to 1.0
        self.task_count = 0
        self.success_rate = 0.8
        self.last_active = datetime.now()
        self.learning_rate = 0.1
        
    def to_dict(self) -> Dict:
        """Convert agent to dictionary representation."""
        return {
            "id": self.id,
            "skills": self.skills,
            "performance_score": self.performance_score,
            "task_count": self.task_count,
            "success_rate": self.success_rate,
            "last_active": self.last_active.isoformat()
        }


class AgentRegistry:
    """Registry for managing agents and their capabilities."""
    
    def __init__(self):
        self.agents = {}
        self.skill_index = {}
        self.performance_history = []
        
        # Initialize with sample agents
        self._initialize_sample_agents()
        
    def _initialize_sample_agents(self):
        """Initialize with sample agents for demonstration."""
        sample_agents = [
            Agent("agent_001", ["python", "data_processing"], 0.85),
            Agent("agent_002", ["javascript", "frontend"], 0.75),
            Agent("agent_003", ["devops", "docker"], 0.90),
            Agent("agent_004", ["security", "audit"], 0.80),
            Agent("agent_005", ["database", "sql"], 0.88)
        ]
        
        for agent in sample_agents:
            self.register_agent(agent)
            
    def register_agent(self, agent: Agent) -> None:
        """Register a new agent."""
        self.agents[agent.id] = agent
        
        # Update skill index
        for skill in agent.skills:
            if skill not in self.skill_index:
                self.skill_index[skill] = []
            self.skill_index[skill].append(agent.id)
            
    def get_agent(self, agent_id: str) -> Agent:
        """Get agent by ID."""
        return self.agents.get(agent_id)
        
    def find_agents_by_skill(self, skill: str) -> List[Agent]:
        """Find agents with a specific skill."""
        agent_ids = self.skill_index.get(skill, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
        
    def get_system_state(self) -> Dict:
        """Get comprehensive system state."""
        total_agents = len(self.agents)
        active_agents = sum(1 for a in self.agents.values() 
                          if (datetime.now() - a.last_active).seconds < 3600)
        
        avg_performance = sum(a.performance_score for a in self.agents.values()) / total_agents if total_agents > 0 else 0
        avg_success_rate = sum(a.success_rate for a in self.agents.values()) / total_agents if total_agents > 0 else 0
        
        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "average_performance": avg_performance,
            "average_success_rate": avg_success_rate,
            "unique_skills": len(self.skill_index),
            "agents": {aid: agent.to_dict() for aid, agent in self.agents.items()},
            "skill_distribution": {skill: len(agents) for skill, agents in self.skill_index.items()},
            "timestamp": datetime.now().isoformat()
        }


class PerformanceOptimizationStrategy(ImprovementStrategy):
    """Strategy for optimizing agent performance."""
    
    def get_name(self) -> str:
        return "performance_optimization"
        
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze agent performance and identify improvement opportunities."""
        agents_data = subsystem_state.get("agents", {})
        opportunities = {
            "improvements_available": False,
            "low_performers": [],
            "skill_gaps": [],
            "optimization_potential": 0.0
        }
        
        # Find low-performing agents
        avg_performance = subsystem_state.get("average_performance", 0.5)
        for agent_id, agent_data in agents_data.items():
            if agent_data["performance_score"] < avg_performance * 0.8:
                opportunities["low_performers"].append({
                    "agent_id": agent_id,
                    "current_score": agent_data["performance_score"],
                    "improvement_needed": avg_performance - agent_data["performance_score"]
                })
                
        # Identify skill gaps (skills with few agents)
        skill_dist = subsystem_state.get("skill_distribution", {})
        total_agents = subsystem_state.get("total_agents", 1)
        for skill, count in skill_dist.items():
            coverage_ratio = count / total_agents
            if coverage_ratio < 0.3:  # Less than 30% coverage
                opportunities["skill_gaps"].append({
                    "skill": skill,
                    "current_coverage": coverage_ratio,
                    "agents_needed": max(1, int(total_agents * 0.3 - count))
                })
                
        # Calculate optimization potential
        if opportunities["low_performers"] or opportunities["skill_gaps"]:
            opportunities["improvements_available"] = True
            opportunities["optimization_potential"] = len(opportunities["low_performers"]) * 0.1 + len(opportunities["skill_gaps"]) * 0.05
            
        return opportunities
        
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute performance improvements."""
        improved_state = subsystem_state.copy()
        improvements_made = []
        
        # Improve low performers
        for low_performer in opportunities.get("low_performers", []):
            agent_id = low_performer["agent_id"]
            if agent_id in improved_state["agents"]:
                # Simulate performance improvement through training
                old_score = improved_state["agents"][agent_id]["performance_score"]
                improvement = min(0.2, low_performer["improvement_needed"])
                improved_state["agents"][agent_id]["performance_score"] = min(1.0, old_score + improvement)
                
                improvements_made.append({
                    "type": "performance_boost",
                    "agent_id": agent_id,
                    "old_score": old_score,
                    "new_score": improved_state["agents"][agent_id]["performance_score"]
                })
                
        # Address skill gaps by training existing agents
        for skill_gap in opportunities.get("skill_gaps", []):
            skill = skill_gap["skill"]
            # Find agents that could learn this skill
            candidates = [aid for aid, agent in improved_state["agents"].items() 
                         if skill not in agent["skills"] and agent["performance_score"] > 0.7]
            
            if candidates:
                # Train top performer in the missing skill
                chosen_agent = max(candidates, 
                                 key=lambda aid: improved_state["agents"][aid]["performance_score"])
                improved_state["agents"][chosen_agent]["skills"].append(skill)
                
                improvements_made.append({
                    "type": "skill_addition",
                    "agent_id": chosen_agent,
                    "new_skill": skill
                })
                
        # Recalculate system metrics
        if improvements_made:
            agents = improved_state["agents"].values()
            improved_state["average_performance"] = sum(a["performance_score"] for a in agents) / len(agents)
            
            # Update skill distribution
            skill_dist = {}
            for agent in agents:
                for skill in agent["skills"]:
                    skill_dist[skill] = skill_dist.get(skill, 0) + 1
            improved_state["skill_distribution"] = skill_dist
            improved_state["unique_skills"] = len(skill_dist)
            
        improved_state["improvements_made"] = improvements_made
        improved_state["timestamp"] = datetime.now().isoformat()
        
        return improved_state


class CapacityPlanningStrategy(ImprovementStrategy):
    """Strategy for optimizing agent capacity and allocation."""
    
    def get_name(self) -> str:
        return "capacity_planning"
        
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze capacity needs and allocation efficiency."""
        opportunities = {
            "improvements_available": False,
            "capacity_issues": [],
            "allocation_inefficiencies": [],
            "scaling_recommendations": []
        }
        
        total_agents = subsystem_state.get("total_agents", 0)
        active_agents = subsystem_state.get("active_agents", 0)
        
        # Check utilization rate
        utilization_rate = active_agents / total_agents if total_agents > 0 else 0
        
        if utilization_rate > 0.9:
            opportunities["capacity_issues"].append({
                "type": "overutilization",
                "utilization_rate": utilization_rate,
                "recommendation": "Add more agents"
            })
            opportunities["improvements_available"] = True
            
        elif utilization_rate < 0.5:
            opportunities["capacity_issues"].append({
                "type": "underutilization", 
                "utilization_rate": utilization_rate,
                "recommendation": "Optimize agent allocation or reduce capacity"
            })
            opportunities["improvements_available"] = True
            
        return opportunities
        
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute capacity improvements."""
        improved_state = subsystem_state.copy()
        improvements_made = []
        
        for issue in opportunities.get("capacity_issues", []):
            if issue["type"] == "overutilization":
                # Simulate adding new agents
                new_agent_count = min(2, max(1, int(improved_state["total_agents"] * 0.1)))
                improved_state["total_agents"] += new_agent_count
                improved_state["active_agents"] = min(improved_state["active_agents"] + new_agent_count, 
                                                    improved_state["total_agents"])
                
                improvements_made.append({
                    "type": "capacity_increase",
                    "agents_added": new_agent_count,
                    "new_total": improved_state["total_agents"]
                })
                
        improved_state["improvements_made"] = improvements_made
        improved_state["timestamp"] = datetime.now().isoformat()
        
        return improved_state


# Global registry instance
_agent_registry = None


def get_agent_registry() -> AgentRegistry:
    """Get or create the global agent registry."""
    global _agent_registry
    if _agent_registry is None:
        _agent_registry = AgentRegistry()
    return _agent_registry


def initialize_agent_management() -> SubsystemHook:
    """Initialize agent management with recursive improvement hooks."""
    registry = get_agent_registry()
    
    # Create improvement strategies
    strategies = [
        PerformanceOptimizationStrategy(),
        CapacityPlanningStrategy()
    ]
    
    # Create subsystem hook
    hook = SubsystemHook(
        name="agents",
        get_state_func=registry.get_system_state,
        improvement_strategies=strategies
    )
    
    # Register with the framework
    framework = get_framework()
    framework.register_subsystem(hook)
    
    return hook


# Example usage and integration functions
def improve_agent_performance(agent_id: str = None) -> Dict:
    """Manual trigger for agent performance improvement."""
    framework = get_framework()
    return framework.run_manual_improvement("agents")


def get_agent_status() -> Dict:
    """Get current agent system status."""
    registry = get_agent_registry()
    return registry.get_system_state()


if __name__ == "__main__":
    # Demo the agent management system
    print("🤖 EpochCore RAS Agent Management Demo")
    print("=" * 50)
    
    # Initialize
    hook = initialize_agent_management()
    registry = get_agent_registry()
    
    print("\n📊 Initial Agent Status:")
    status = get_agent_status()
    print(f"  Total Agents: {status['total_agents']}")
    print(f"  Active Agents: {status['active_agents']}")
    print(f"  Average Performance: {status['average_performance']:.2f}")
    print(f"  Unique Skills: {status['unique_skills']}")
    
    print("\n🔧 Running Improvement Cycle...")
    improvement_result = improve_agent_performance()
    
    print(f"\n✅ Improvement Result: {improvement_result['status']}")
    if improvement_result['status'] == 'success':
        for improvement in improvement_result['improvements']:
            print(f"  Strategy: {improvement['strategy']}")
            if 'improvements_made' in improvement['after_state']:
                for imp in improvement['after_state']['improvements_made']:
                    print(f"    - {imp}")
    
    print("\n📊 Final Agent Status:")
    final_status = get_agent_status()
    print(f"  Total Agents: {final_status['total_agents']}")
    print(f"  Active Agents: {final_status['active_agents']}")
    print(f"  Average Performance: {final_status['average_performance']:.2f}")
    print(f"  Unique Skills: {final_status['unique_skills']}")