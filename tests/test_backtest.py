"""
Comprehensive backtesting suite for the StrategyDECK agent system.
Tests all components and their interactions under various scenarios.
"""

import pytest
import numpy as np
import torch
import networkx as nx
from datetime import datetime, timedelta
from pathlib import Path
from qiskit import QuantumCircuit

from strategydeck_agent import StrategyDeckAgent
from strategy_quantum import QuantumArchitecture
from strategy_cognitive import CognitiveState, CognitiveDecision
from strategy_temporal import TimeSeriesData, TemporalPrediction
from strategy_ethical import EthicalAssessment, Impact, EthicalPrinciple


class TestScenario:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.data = data
        self.results = {}


@pytest.fixture
def agent():
    """Create a fully enabled agent for testing"""
    return StrategyDeckAgent(
        name="BacktestAgent",
        enable_mesh=True,
        enable_quantum=True,
        enable_ethical=True,
        enable_cognitive=True,
        enable_temporal=True,
    )


@pytest.fixture
def time_series_data():
    """Generate synthetic time series data for testing"""
    timestamps = np.array([datetime.now() + timedelta(hours=i) for i in range(100)])
    values = np.sin(np.linspace(0, 4 * np.pi, 100)) + np.random.normal(0, 0.1, 100)
    return TimeSeriesData(
        timestamps=timestamps,
        values=values,
        features=["test_metric"],
        frequency="1H",
        metadata={"type": "synthetic"},
    )


def test_mesh_initialization(agent):
    """Test mesh network initialization and node connectivity"""
    assert agent.mesh is not None
    assert len(agent.mesh.nodes) >= 6

    # Verify all core nodes exist
    expected_nodes = {
        "intelligence",
        "resilience",
        "collaboration",
        "quantum",
        "ethical",
        "cognitive",
    }
    node_types = {node.node_type for node in agent.mesh.nodes.values()}
    assert expected_nodes.issubset(node_types)

    # Check node capabilities
    for node in agent.mesh.nodes.values():
        assert len(node.capabilities) > 0
        assert node.health_score > 0


def test_quantum_optimization(agent):
    """Test quantum optimization capabilities"""
    # Create a test optimization problem
    graph = nx.complete_graph(4)
    circuit = agent.quantum.create_optimization_circuit(graph)

    assert circuit is not None
    assert isinstance(circuit, QuantumCircuit)
    assert circuit.num_qubits >= 4

    # Test quantum state preparation
    circuit = agent.quantum.create_superposition_circuit(num_qubits=4)
    assert circuit is not None
    assert isinstance(circuit, QuantumCircuit)
    assert circuit.num_qubits == 4


def test_cognitive_processing(agent):
    """Test cognitive processing and decision making"""
    # Test emotional state update
    agent.cognitive.update_emotional_state(0.6, 0.4, 0.7)

    # Test input processing with shorter input
    state = agent.cognitive.process_input("Test", context={"priority": "high"})
    assert isinstance(state, CognitiveState)
    assert state.confidence_score > 0

    # Test decision making with simple options
    options = ["option1", "option2", "option3"]
    decision = agent.cognitive.make_decision(state, options=options)
    assert isinstance(decision, CognitiveDecision)
    assert decision.confidence > 0
    assert len(decision.reasoning_path) > 0


def test_temporal_forecasting(agent):
    """Test temporal forecasting and pattern recognition"""
    # Create simple time series with hourly frequency
    values = np.sin(np.linspace(0, 4 * np.pi, 256))

    # Reshape for transformer input (seq_len, batch_size, feature_dim)
    values = np.expand_dims(values, axis=(1, 2))  # Shape: (256, 1, 1)

    # Add time series data
    agent.temporal.add_time_series("test_series", values)

    # Generate forecast
    forecast = agent.temporal.forecast("test_series", horizon=10)
    assert isinstance(forecast, TemporalPrediction)
    assert len(forecast.predictions) == 10
    assert len(forecast.confidence_intervals) == 2  # Upper and lower bounds

    # Check forecast quality metrics
    assert isinstance(forecast.model_performance, dict)
    assert len(forecast.model_performance) > 0
    assert all(isinstance(v, float) for v in forecast.model_performance.values())


def test_ethical_assessment(agent):
    """Test ethical decision making and impact assessment"""
    # Create a test scenario
    context = {
        "action": "deploy_system_update",
        "affected_users": 1000,
        "estimated_benefit": 0.8,
        "potential_risks": 0.2,
    }

    # Register test stakeholders
    agent.ethical.register_stakeholder(
        "test_users", interests={"safety": 0.9, "privacy": 0.8}
    )

    # Get ethical assessment
    assessment = agent.ethical.assess_action(
        action_id="test_action", context=context, stakeholders=["test_users"]
    )

    assert isinstance(assessment, EthicalAssessment)
    assert len(assessment.principles_evaluated) > 0
    assert isinstance(assessment.overall_score, float)
    assert 0 <= assessment.overall_score <= 1

    # Test impact prediction with simpler context
    impact = agent.ethical.predict_impact(
        action_id="test_action", context={"risk": 0.2, "benefit": 0.8}
    )

    assert isinstance(impact, Impact)
    assert isinstance(impact.uncertainty, float)
    assert isinstance(impact.reversibility, float)
    assert 0 <= impact.uncertainty <= 1
    assert 0 <= impact.reversibility <= 1


def test_resilience_and_recovery(agent):
    """Test system resilience and recovery mechanisms"""
    # Get initial node states
    nodes = list(agent.mesh.nodes.keys())
    assert len(nodes) > 0

    # Test node health monitoring
    test_node = nodes[0]
    initial_health = agent.mesh.nodes[test_node].health_score
    assert initial_health > 0

    # Simulate degraded performance
    agent.mesh.nodes[test_node].update_health(0.3)
    assert agent.mesh.nodes[test_node].health_score < 0.5

    # Test recovery mechanism
    agent.mesh.nodes[test_node].update_health(0.9)
    assert agent.mesh.nodes[test_node].health_score > 0.8


def test_full_system_integration(agent):
    """Test full system integration and component interaction"""
    # 1. Test cognitive processing
    cognitive_result = agent.cognitive.process_input(
        "System test", context={"type": "integration_test"}
    )
    assert isinstance(cognitive_result, CognitiveState)
    assert cognitive_result.confidence_score > 0

    # 2. Add and test time series
    values = np.sin(np.linspace(0, 2 * np.pi, 256))
    values = np.expand_dims(values, axis=(1, 2))  # Shape: (256, 1, 1)
    agent.temporal.add_time_series("test_metric", values)
    assert isinstance(cognitive_result, CognitiveState)
    assert cognitive_result.confidence_score > 0

    # 2. Test temporal forecasting
    values = np.sin(np.linspace(0, 2 * np.pi, 256))
    values = np.expand_dims(values, axis=(1, 2))  # Shape: (256, 1, 1)
    agent.temporal.add_time_series("test_metric", values)
    forecast = agent.temporal.forecast("test_metric", horizon=5)
    assert isinstance(forecast, TemporalPrediction)
    assert len(forecast.predictions) == 5

    # 3. Test ethical decision making
    assessment = agent.ethical.assess_action(
        action_id="integration_test", context={"impact": "minimal", "risk": 0.1}
    )
    assert isinstance(assessment, EthicalAssessment)
    assert isinstance(assessment.overall_score, float)

    # 4. Verify mesh stability
    assert all(node.health_score > 0 for node in agent.mesh.nodes.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
