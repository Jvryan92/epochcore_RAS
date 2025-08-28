#!/usr/bin/env python3
"""Tests for the StrategyAgent implementation."""

import pytest
from pathlib import Path
import sys

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ai_agent.agents.strategy_agent import StrategyAgent, TaskType
from ai_agent.core.base_agent import BaseAgent


class TestStrategyAgent:
    """Test cases for StrategyAgent functionality."""
    
    def test_initialization(self):
        """Test StrategyAgent initialization."""
        agent = StrategyAgent()
        assert agent.name == "strategy_agent"
        assert isinstance(agent.pattern_registry, dict)
        assert len(agent.pattern_registry) == 3  # fractal, adaptive, quantum
        
    def test_bulk_task_creation(self):
        """Test creating bulk tasks."""
        agent = StrategyAgent()
        bulk_task = agent.create_bulk_task("test_bulk", bulk_factor=10)
        
        assert bulk_task.name == "test_bulk_bulk_10x"
        assert bulk_task.task_type == TaskType.COMPOUND
        assert bulk_task.metadata["bulk_factor"] == 10
        assert len(bulk_task.patterns) == 1
        
    def test_bulk_task_execution(self):
        """Test executing bulk tasks with quantum pattern."""
        agent = StrategyAgent()
        bulk_task = agent.create_bulk_task("test_bulk", bulk_factor=5, pattern_type="quantum")
        results = agent.execute_task(bulk_task)
        
        # Verify we got multiple outputs
        assert isinstance(results, dict)
        assert results["status"] == "compound_processed"
        
        # Check meta result contains generated tasks
        meta_result = results["meta_result"]
        assert meta_result["status"] == "meta_processed"
        assert meta_result["generated_tasks"] > 0
        
    def test_bulk_task_state_tracking(self):
        """Test state tracking for bulk tasks."""
        agent = StrategyAgent()
        bulk_task = agent.create_bulk_task("test_state", bulk_factor=3)
        agent.execute_task(bulk_task)
        
        # Verify state history was tracked
        assert len(agent.state_history[bulk_task.id]) > 0
        state = agent.state_history[bulk_task.id][0]
        assert state["type"] == TaskType.COMPOUND.value
        assert state["patterns_available"] == 1

    def test_bulk_task_pattern_types(self):
        """Test bulk task creation with different pattern types."""
        agent = StrategyAgent()
        
        # Test each pattern type
        for pattern in ["quantum", "fractal", "adaptive"]:
            bulk_task = agent.create_bulk_task(
                f"test_{pattern}", 
                bulk_factor=2, 
                pattern_type=pattern
            )
            assert len(bulk_task.patterns) == 1
            assert bulk_task.patterns[0].pattern_type == pattern

    def test_large_bulk_factor(self):
        """Test creating tasks with large bulk factors."""
        agent = StrategyAgent()
        bulk_task = agent.create_bulk_task("test_large", bulk_factor=100)
        
        # Ensure it handles large numbers safely
        assert bulk_task.metadata["bulk_factor"] == 100
        assert bulk_task.metadata["max_depth"] == 5  # Verify depth limit is set
        
        # Execute and verify it doesn't hang or crash
        results = agent.execute_task(bulk_task)
        assert results is not None
        assert "status" in results


if __name__ == "__main__":
    pytest.main([__file__])
