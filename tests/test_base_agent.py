#!/usr/bin/env python3
"""Unified block tests for the BaseAgent class."""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch
import tempfile
import json

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ai_agent.core.base_agent import BaseAgent


class TestBaseAgentUnified:
    """Test cases for BaseAgent using unified block testing."""

    def test_agent_lifecycle_unified(self):
        """
        Unified block test for agent lifecycle management.
        Tests initialization, validation, execution, and cleanup.
        """

        class TestAgent(BaseAgent):
            def __init__(self, name="test", config=None):
                super().__init__(name, config)
                self.setup_called = False
                self.cleanup_called = False

            def validate_config(self) -> bool:
                return self.config.get("valid", True)

            def run(self, *args, **kwargs):
                return {"status": "running"}

            def cleanup(self):
                self.cleanup_called = True

            def setup(self):
                self.setup_called = True

        # Block 1: Test initialization and configuration
        config = {"test": True, "valid": True}
        agent = TestAgent(config=config)
        assert agent.name == "test"
        assert agent.config == config
        assert not agent.is_running()
        assert agent.validate_config()

        # Block 2: Test execution flow with success
        result = agent.start()
        assert result["status"] == "success"
        assert "result" in result
        assert agent.setup_called
        assert not agent.is_running()

        # Block 3: Test error handling and cleanup
        with patch.object(TestAgent, "run") as mock_run:
            mock_run.side_effect = Exception("Test error")
            agent = TestAgent()
            result = agent.start()
            assert result["status"] == "error"
            assert "error" in result
            assert agent.cleanup_called

    def test_agent_state_management_unified(self):
        """
        Unified block test for agent state management.
        Tests state transitions, concurrency control, and error recovery.
        """

        class StateTestAgent(BaseAgent):
            def validate_config(self) -> bool:
                return True

            def run(self, *args, **kwargs):
                if self.config.get("should_fail"):
                    raise ValueError("Test failure")
                return {"state": "completed"}

        # Block 1: Test state transitions
        agent = StateTestAgent(name="state_test")
        assert not agent.is_running()

        with patch.object(StateTestAgent, "run") as mock_run:
            mock_run.return_value = {"state": "running"}
            agent.start()
            assert not agent.is_running()  # Should reset after completion

        # Block 2: Test concurrent execution prevention
        agent = StateTestAgent(name="concurrent_test")
        agent._running = True  # Simulate running state
        result = agent.start()
        assert result["status"] == "error"
        assert "already running" in result["error"].lower()

        # Block 3: Test state recovery after errors
        agent = StateTestAgent(name="error_test", config={"should_fail": True})
        assert not agent.is_running()
        result = agent.start()
        assert result["status"] == "error"
        assert not agent.is_running()  # Should reset after error

    def test_agent_configuration_unified(self):
        """
        Unified block test for agent configuration management.
        Tests config validation, inheritance, and overrides.
        """

        class ConfigTestAgent(BaseAgent):
            def validate_config(self) -> bool:
                required = ["api_key", "endpoint"]
                return all(key in self.config for key in required)

            def run(self, *args, **kwargs):
                return self.config

        # Block 1: Test configuration validation
        valid_config = {"api_key": "test_key", "endpoint": "http://test.com"}
        agent = ConfigTestAgent(name="config_test", config=valid_config)
        assert agent.validate_config()

        invalid_config = {"api_key": "test_key"}  # Missing endpoint
        agent = ConfigTestAgent(name="config_test_invalid", config=invalid_config)
        assert not agent.validate_config()

        # Block 2: Test configuration inheritance
        base_config = {
            "api_key": "base_key",
            "endpoint": "http://base.com",
            "timeout": 30,
        }

        override_config = {"api_key": "override_key", "custom": True}

        with patch.dict(base_config), patch.dict(override_config):
            agent = ConfigTestAgent(config={**base_config, **override_config})
            result = agent.start()
            assert result["result"]["api_key"] == "override_key"
            assert result["result"]["endpoint"] == "http://base.com"
            assert result["result"]["custom"] is True

        # Block 3: Test configuration type safety
        type_test_configs = [
            (
                {"api_key": 123, "endpoint": "http://test.com"},
                False,
            ),  # api_key should be string
            ({"api_key": "test", "endpoint": None}, False),  # endpoint should be string
            (
                {"api_key": "test", "endpoint": "http://test.com", "timeout": "30"},
                False,
            ),  # timeout should be int
            ({"api_key": "test", "endpoint": "http://test.com", "timeout": 30}, True),
        ]

        for config, should_validate in type_test_configs:
            agent = ConfigTestAgent(config=config)
            if should_validate:
                assert agent.validate_config()
            else:
                assert not agent.validate_config()
