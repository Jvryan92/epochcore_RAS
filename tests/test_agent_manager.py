#!/usr/bin/env python3
"""Unified block tests for the AgentManager class."""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch
import tempfile
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ai_agent.core.agent_manager import AgentManager
from ai_agent.core.base_agent import BaseAgent


class TestAgentManagerUnified:
    """Test cases for AgentManager using unified block testing."""
    
    def test_agent_registration_unified(self):
        """
        Unified block test for agent registration and management.
        Tests registration, deregistration, and agent lookup.
        """
        class TestAgent(BaseAgent):
            def validate_config(self) -> bool:
                return True
                
            def run(self, *args, **kwargs):
                return {"status": "ok"}

        # Block 1: Test agent registration and lookup
        manager = AgentManager()
        agent1 = TestAgent(name="agent1")
        agent2 = TestAgent(name="agent2")
        
        manager.register_agent(agent1)
        manager.register_agent(agent2)
        
        assert manager.get_agent("agent1") == agent1
        assert manager.get_agent("agent2") == agent2
        assert manager.get_agent("nonexistent") is None
        
        # Block 2: Test duplicate registration and deregistration
        agent3 = TestAgent(name="agent1")  # Same name as agent1
        with pytest.raises(ValueError):
            manager.register_agent(agent3)
            
        manager.deregister_agent("agent1")
        assert manager.get_agent("agent1") is None
        manager.register_agent(agent3)  # Should work now
        assert manager.get_agent("agent1") == agent3
        
        # Block 3: Test bulk operations
        agents = [TestAgent(name=f"bulk{i}") for i in range(5)]
        for agent in agents:
            manager.register_agent(agent)
            
        assert len(manager.get_all_agents()) == 7  # 5 bulk + agent2 + agent3
        manager.deregister_all_agents()
        assert len(manager.get_all_agents()) == 0

    def test_agent_lifecycle_management_unified(self):
        """
        Unified block test for agent lifecycle management.
        Tests starting, stopping, and monitoring agents.
        """
        class LifecycleTestAgent(BaseAgent):
            def __init__(self, name="test", config=None):
                super().__init__(name, config)
                self.started = False
                self.stopped = False
                
            def validate_config(self) -> bool:
                return True
                
            def run(self, *args, **kwargs):
                self.started = True
                if self.config.get('should_fail'):
                    raise ValueError("Test failure")
                return {"status": "running"}
                
            def cleanup(self):
                self.stopped = True

        # Block 1: Test agent start/stop
        manager = AgentManager()
        agent = LifecycleTestAgent(name="lifecycle")
        manager.register_agent(agent)
        
        result = manager.start_agent("lifecycle")
        assert result["status"] == "success"
        assert agent.started
        
        manager.stop_agent("lifecycle")
        assert agent.stopped
        
        # Block 2: Test bulk lifecycle operations
        agents = [LifecycleTestAgent(name=f"bulk{i}") for i in range(3)]
        for agent in agents:
            manager.register_agent(agent)
            
        results = manager.start_all_agents()
        assert all(result["status"] == "success" for result in results.values())
        assert all(agent.started for agent in agents)
        
        manager.stop_all_agents()
        assert all(agent.stopped for agent in agents)
        
        # Block 3: Test error handling
        error_agent = LifecycleTestAgent(name="error", config={"should_fail": True})
        manager.register_agent(error_agent)
        result = manager.start_agent("error")
        assert result["status"] == "error"
        assert "Test failure" in str(result["error"])
        assert error_agent.stopped  # Should clean up after error

    def test_agent_configuration_unified(self):
        """
        Unified block test for agent configuration management.
        Tests configuration loading, validation, and updates.
        """
        class ConfigTestAgent(BaseAgent):
            def validate_config(self) -> bool:
                return self.config.get('valid', True)
                
            def run(self, *args, **kwargs):
                return self.config

        # Block 1: Test configuration loading
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as config_file:
            config = {
                "agent1": {"valid": True, "param": "value1"},
                "agent2": {"valid": True, "param": "value2"}
            }
            json.dump(config, config_file)
            config_file.flush()
            
            manager = AgentManager()
            manager.load_config(config_file.name)
            
            agent1 = ConfigTestAgent(name="agent1")
            agent2 = ConfigTestAgent(name="agent2")
            
            manager.register_agent(agent1)
            manager.register_agent(agent2)
            
            assert agent1.config["param"] == "value1"
            assert agent2.config["param"] == "value2"
            
        # Block 2: Test configuration validation
        invalid_agent = ConfigTestAgent(name="invalid", config={"valid": False})
        manager.register_agent(invalid_agent)
        result = manager.start_agent("invalid")
        assert result["status"] == "error"
        assert "configuration validation failed" in result["error"].lower()
        
        # Block 3: Test configuration updates
        update_agent = ConfigTestAgent(name="update")
        manager.register_agent(update_agent)
        
        new_config = {"valid": True, "param": "updated"}
        manager.update_agent_config("update", new_config)
        assert update_agent.config == new_config
        
        result = manager.start_agent("update")
        assert result["status"] == "success"
        assert result["result"]["param"] == "updated"
