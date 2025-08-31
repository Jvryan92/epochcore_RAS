#!/usr/bin/env python3
"""Tests for the StrategyDECK AI Agent System."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ai_agent.core.agent_manager import AgentManager
from ai_agent.core.base_agent import BaseAgent
from ai_agent.agents.project_monitor import ProjectMonitorAgent
from ai_agent.agents.asset_manager import AssetManagerAgent
from ai_agent.agents.workflow_optimizer import WorkflowOptimizerAgent


class MockAgent(BaseAgent):
    """Mock agent for testing base functionality."""
    
    def __init__(self, config=None, should_fail=False):
        super().__init__("test_agent", config)
        self.should_fail = should_fail
        self.run_called = False
    
    def validate_config(self):
        return not self.should_fail
    
    def run(self):
        self.run_called = True
        if self.should_fail:
            raise ValueError("Test failure")
        return {"test": "success"}


class TestBaseAgent:
    """Test cases for BaseAgent functionality."""
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agent = MockAgent({"key": "value"})
        assert agent.name == "test_agent"
        assert agent.config == {"key": "value"}
        assert not agent.is_running()
    
    def test_agent_start_success(self):
        """Test successful agent execution."""
        agent = MockAgent()
        result = agent.start()
        
        assert result["status"] == "success"
        assert result["agent"] == "test_agent"
        assert result["result"]["test"] == "success"
        assert agent.run_called
    
    def test_agent_start_failure(self):
        """Test agent execution with failure."""
        agent = MockAgent(should_fail=True)
        result = agent.start()
        
        assert result["status"] == "error"
        assert result["agent"] == "test_agent"
        # The agent fails at config validation, not during run
        assert "Invalid configuration" in result["error"]
    
    def test_agent_config_validation_failure(self):
        """Test agent with invalid configuration."""
        agent = MockAgent(should_fail=True)
        result = agent.start()
        
        assert result["status"] == "error"
        assert "Invalid configuration" in result["error"]
    
    def test_get_project_root(self):
        """Test project root detection."""
        agent = MockAgent()
        root = agent.get_project_root()
        
        # Should be a Path object pointing to project root
        assert isinstance(root, Path)
        assert root.exists()


class TestAgentManager:
    """Test cases for AgentManager functionality."""
    
    def test_manager_initialization_no_config(self):
        """Test manager initialization without config file."""
        manager = AgentManager()
        
        assert manager.config is not None
        assert "logging" in manager.config
        assert "agents" in manager.config
    
    def test_manager_initialization_with_config(self):
        """Test manager initialization with config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                "logging": {"level": "DEBUG"},
                "agents": {"test": {"enabled": True}}
            }
            json.dump(config, f)
            config_path = Path(f.name)
        
        try:
            manager = AgentManager(config_path)
            assert manager.config["logging"]["level"] == "DEBUG"
            assert manager.config["agents"]["test"]["enabled"] is True
        finally:
            config_path.unlink()
    
    def test_register_agent(self):
        """Test agent registration."""
        manager = AgentManager()
        agent = MockAgent()
        
        manager.register_agent(agent)
        assert "test_agent" in manager.agents
        assert manager.agents["test_agent"] is agent
    
    def test_run_agent_success(self):
        """Test running a registered agent."""
        manager = AgentManager()
        agent = MockAgent()
        manager.register_agent(agent)
        
        result = manager.run_agent("test_agent")
        assert result["status"] == "success"
        assert agent.run_called
    
    def test_run_agent_not_found(self):
        """Test running a non-existent agent."""
        manager = AgentManager()
        result = manager.run_agent("nonexistent")
        
        assert result["status"] == "error"
        assert "not found" in result["error"]
    
    def test_run_all_agents(self):
        """Test running all registered agents."""
        manager = AgentManager()
        agent1 = MockAgent()
        agent1.name = "agent1"
        agent2 = MockAgent()
        agent2.name = "agent2"
        
        manager.register_agent(agent1)
        manager.register_agent(agent2)
        
        results = manager.run_all_agents()
        assert len(results) == 2
        assert all(r["status"] == "success" for r in results)
    
    def test_list_agents(self):
        """Test listing registered agents."""
        manager = AgentManager()
        agent = MockAgent()
        manager.register_agent(agent)
        
        agents = manager.list_agents()
        assert "test_agent" in agents
    
    def test_get_agent_status(self):
        """Test getting agent running status."""
        manager = AgentManager()
        agent = MockAgent()
        manager.register_agent(agent)
        
        status = manager.get_agent_status()
        assert "test_agent" in status
        assert status["test_agent"] is False  # Not running


class TestProjectMonitorAgent:
    """Test cases for ProjectMonitorAgent."""
    
    def test_initialization(self):
        """Test ProjectMonitorAgent initialization."""
        agent = ProjectMonitorAgent()
        assert agent.name == "project_monitor"
    
    def test_validate_config(self):
        """Test configuration validation."""
        agent = ProjectMonitorAgent()
        assert agent.validate_config() is True
    
    def test_run_basic(self):
        """Test basic run functionality."""
        agent = ProjectMonitorAgent({"save_report": False})
        result = agent.run()
        
        # Should return a report structure
        assert "timestamp" in result
        assert "project_structure" in result
        assert "workflow_status" in result
        assert "asset_status" in result


class TestAssetManagerAgent:
    """Test cases for AssetManagerAgent."""
    
    def test_initialization(self):
        """Test AssetManagerAgent initialization."""
        agent = AssetManagerAgent()
        assert agent.name == "asset_manager"
    
    def test_validate_config(self):
        """Test configuration validation."""
        agent = AssetManagerAgent()
        # Should validate based on whether generate_icons.py exists
        result = agent.validate_config()
        assert isinstance(result, bool)
    
    @patch('subprocess.run')
    def test_generate_assets_success(self, mock_run):
        """Test successful asset generation."""
        mock_run.return_value = Mock(returncode=0, stdout="Success", stderr="")
        
        agent = AssetManagerAgent()
        result = agent._generate_assets(agent.get_project_root())
        
        assert result["success"] is True
        assert result["returncode"] == 0
    
    @patch('subprocess.run')
    def test_generate_assets_failure(self, mock_run):
        """Test failed asset generation."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error")
        
        agent = AssetManagerAgent()
        result = agent._generate_assets(agent.get_project_root())
        
        assert result["success"] is False
        assert result["returncode"] == 1


class TestWorkflowOptimizerAgent:
    """Test cases for WorkflowOptimizerAgent."""
    
    def test_initialization(self):
        """Test WorkflowOptimizerAgent initialization."""
        agent = WorkflowOptimizerAgent()
        assert agent.name == "workflow_optimizer"
    
    def test_validate_config(self):
        """Test configuration validation."""
        agent = WorkflowOptimizerAgent()
        # Should validate based on whether .github/workflows exists
        result = agent.validate_config()
        assert isinstance(result, bool)
    
    def test_run_basic(self):
        """Test basic run functionality."""
        agent = WorkflowOptimizerAgent()
        result = agent.run()
        
        # Should return analysis structure
        assert "workflow_analysis" in result
        assert "optimization_suggestions" in result
        assert "best_practices" in result
        assert "performance_insights" in result


class TestAgentIntegration:
    """Integration tests for the complete agent system."""
    
    def test_full_system_execution(self):
        """Test running the complete agent system."""
        manager = AgentManager()
        
        # Register all agents
        agents = [
            ProjectMonitorAgent({"save_report": False}),
            AssetManagerAgent({"auto_generate": False}),
            WorkflowOptimizerAgent()
        ]
        
        for agent in agents:
            manager.register_agent(agent)
        
        # Run all agents
        results = manager.run_all_agents()
        
        assert len(results) == 3
        # At least one should succeed (project_monitor should always work)
        assert any(r["status"] == "success" for r in results)
    
    def test_agent_error_isolation(self):
        """Test that agent failures don't affect others."""
        manager = AgentManager()
        
        # Mix of good and bad agents
        good_agent = MockAgent()
        good_agent.name = "good_agent"
        bad_agent = MockAgent(should_fail=True)
        bad_agent.name = "bad_agent"
        
        manager.register_agent(good_agent)
        manager.register_agent(bad_agent)
        
        results = manager.run_all_agents()
        
        # Should have results for both agents
        assert len(results) == 2
        
        # Good agent should succeed, bad agent should fail
        statuses = {r["agent"]: r["status"] for r in results}
        assert statuses["good_agent"] == "success"
        assert statuses["bad_agent"] == "error"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])