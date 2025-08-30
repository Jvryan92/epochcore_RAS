"""Test suite for high-skill agents."""

import pytest
from datetime import datetime, timezone
from typing import Dict, Any

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.ai_agent.core.agent_manager import AgentManager
from scripts.ai_agent.agents.sentinel_agent import SentinelAgent
from scripts.ai_agent.agents.optimizer_agent import OptimizerAgent
from scripts.ai_agent.agents.synth_agent import SynthAgent
from scripts.ai_agent.agents.high_skill_agents import register_high_skill_agents


@pytest.fixture
def agent_manager():
    """Create an agent manager instance for testing."""
    return AgentManager()


@pytest.fixture
def sentinel_agent():
    """Create a Sentinel agent instance for testing."""
    config = {
        "mesh_secret": "test_secret",
        "compliance_level": "high",
        "audit_interval": 60,
    }
    return SentinelAgent(config=config)


@pytest.fixture
def optimizer_agent():
    """Create an Optimizer agent instance for testing."""
    config = {
        "monitoring_interval": 30,
        "optimization_threshold": 0.75,
        "target_slo": {"latency": 300, "cpu_usage": 80, "memory_usage": 75},
    }
    return OptimizerAgent(config=config)


@pytest.fixture
def synth_agent():
    """Create a Synth agent instance for testing."""
    config = {
        "forecast_horizon": 30,
        "confidence_threshold": 0.8,
        "update_interval": 60,
    }
    return SynthAgent(config=config)


def test_sentinel_agent_initialization(sentinel_agent):
    """Test Sentinel agent initialization."""
    assert sentinel_agent.name == "sentinel"
    assert sentinel_agent.config["mesh_secret"] == "test_secret"
    assert sentinel_agent.config["compliance_level"] == "high"
    assert not sentinel_agent._is_running


def test_optimizer_agent_initialization(optimizer_agent):
    """Test Optimizer agent initialization."""
    assert optimizer_agent.name == "optimizer"
    assert optimizer_agent.config["monitoring_interval"] == 30
    assert optimizer_agent.config["optimization_threshold"] == 0.75
    assert not optimizer_agent._is_running


def test_synth_agent_initialization(synth_agent):
    """Test Synth agent initialization."""
    assert synth_agent.name == "synth"
    assert synth_agent.config["forecast_horizon"] == 30
    assert synth_agent.config["confidence_threshold"] == 0.8
    assert not synth_agent._is_running


def test_sentinel_agent_validation(sentinel_agent):
    """Test Sentinel agent config validation."""
    assert sentinel_agent.validate_config()

    # Test invalid config
    sentinel_agent.config = {}
    assert not sentinel_agent.validate_config()


def test_optimizer_agent_validation(optimizer_agent):
    """Test Optimizer agent config validation."""
    assert optimizer_agent.validate_config()

    # Test invalid config
    optimizer_agent.config = {}
    assert not optimizer_agent.validate_config()


def test_synth_agent_validation(synth_agent):
    """Test Synth agent config validation."""
    assert synth_agent.validate_config()

    # Test invalid config
    synth_agent.config = {}
    assert not synth_agent.validate_config()


def test_agent_registration(agent_manager):
    """Test registering high-skill agents."""
    config = {
        "mesh_secret": "test_secret",
        "compliance_level": "high",
        "monitoring_interval": 30,
        "forecast_horizon": 30,
    }

    register_high_skill_agents(agent_manager, config)

    assert "sentinel" in agent_manager.agents
    assert "optimizer" in agent_manager.agents
    assert "synth" in agent_manager.agents


def test_agent_connections(agent_manager):
    """Test agent connections and topic subscriptions."""
    config = {
        "mesh_secret": "test_secret",
        "compliance_level": "high",
        "monitoring_interval": 30,
        "forecast_horizon": 30,
    }

    register_high_skill_agents(agent_manager, config)

    sentinel = agent_manager.agents["sentinel"]
    optimizer = agent_manager.agents["optimizer"]
    synth = agent_manager.agents["synth"]

    # Check connections
    assert "optimizer" in sentinel._connected_agents
    assert "synth" in sentinel._connected_agents
    assert "sentinel" in optimizer._connected_agents
    assert "synth" in optimizer._connected_agents
    assert "sentinel" in synth._connected_agents
    assert "optimizer" in synth._connected_agents


def test_agent_message_passing(sentinel_agent, optimizer_agent):
    """Test message passing between agents."""
    # Connect agents
    sentinel_agent.connect_to_agent(optimizer_agent)
    optimizer_agent.connect_to_agent(sentinel_agent)

    # Send test message
    test_data = {"alert_type": "test_alert", "severity": "high"}

    sentinel_agent.send_message(
        "optimizer", "security.alert", test_data, priority="high"
    )

    # Check received message
    messages = optimizer_agent.get_messages("security.alert")
    assert len(messages) == 1
    assert messages[0]["data"] == test_data
    assert messages[0]["priority"] == "high"


def test_compound_features(agent_manager):
    """Test compound feature registration and decisions."""
    config = {
        "mesh_secret": "test_secret",
        "compliance_level": "high",
        "monitoring_interval": 30,
        "forecast_horizon": 30,
    }

    register_high_skill_agents(agent_manager, config)

    # Check compound features
    assert "security_performance" in agent_manager.compound_decisions
    assert "market_security" in agent_manager.compound_decisions
    assert "performance_market" in agent_manager.compound_decisions
    assert "full_system_status" in agent_manager.compound_decisions


def test_sentinel_security_monitoring(sentinel_agent):
    """Test Sentinel agent security monitoring."""
    result = sentinel_agent.run()

    assert "security_status" in result
    assert "integrity_checks" in result
    assert "compliance_status" in result


def test_optimizer_performance_monitoring(optimizer_agent):
    """Test Optimizer agent performance monitoring."""
    result = optimizer_agent.run()

    assert "optimization_status" in result
    assert "performance_summary" in result
    assert "recommendations" in result


def test_synth_market_analysis(synth_agent):
    """Test Synth agent market analysis."""
    result = synth_agent.run()

    assert "synthesis_status" in result
    assert "market_insights" in result
    assert "forecasts" in result


def test_agent_error_handling(sentinel_agent):
    """Test agent error handling."""
    # Force an error by removing required config
    sentinel_agent.config = {}

    result = sentinel_agent.run()
    assert result["security_status"] == "error"
    assert "error" in result
