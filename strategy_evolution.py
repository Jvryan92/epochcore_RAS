from typing import Dict, List, Any, Optional, Type, Callable
import numpy as np
from dataclasses import dataclass
import torch
import torch.nn as nn
from pathlib import Path
import json
import time
from datetime import datetime


@dataclass
class EvolutionMetric:
    capability_name: str
    performance_score: float
    adaptation_rate: float
    complexity: int
    timestamp: datetime


class EvolutionaryNetwork(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
        )

    def forward(self, x):
        return self.network(x)


class AutonomousEvolution:
    """
    Autonomous Evolution layer for self-improving agent capabilities
    """

    def __init__(self, evolution_dir: str = ".evolution"):
        self.evolution_dir = Path(evolution_dir)
        self.evolution_dir.mkdir(parents=True, exist_ok=True)

        self.capability_networks: Dict[str, EvolutionaryNetwork] = {}
        self.evolution_history: List[EvolutionMetric] = []
        self.adaptation_threshold = 0.75
        self.learning_rate = 0.01

    def initialize_capability(
        self,
        capability_name: str,
        input_size: int = 10,
        hidden_size: int = 20,
        output_size: int = 5,
    ):
        """Initialize a new evolutionary capability"""
        network = EvolutionaryNetwork(input_size, hidden_size, output_size)
        self.capability_networks[capability_name] = network

        # Record initial state
        self._record_evolution(
            capability_name,
            performance_score=0.5,  # Initial score
            adaptation_rate=0.1,  # Initial adaptation rate
        )

        return network

    def evolve_capability(
        self,
        capability_name: str,
        performance_data: torch.Tensor,
        target_data: torch.Tensor,
    ) -> Dict[str, float]:
        """Evolve a capability based on performance data"""
        if capability_name not in self.capability_networks:
            self.initialize_capability(capability_name)

        network = self.capability_networks[capability_name]
        optimizer = torch.optim.Adam(network.parameters(), lr=self.learning_rate)
        criterion = nn.MSELoss()

        # Training loop
        network.train()
        optimizer.zero_grad()

        output = network(performance_data)
        loss = criterion(output, target_data)
        loss.backward()
        optimizer.step()

        # Calculate adaptation metrics
        performance_score = 1.0 - loss.item()
        adaptation_rate = self._calculate_adaptation_rate(capability_name)

        self._record_evolution(
            capability_name,
            performance_score=performance_score,
            adaptation_rate=adaptation_rate,
        )

        return {
            "performance_score": performance_score,
            "adaptation_rate": adaptation_rate,
            "loss": loss.item(),
        }

    def synthesize_capability(self, source_capabilities: List[str]) -> Optional[str]:
        """Synthesize a new capability from existing ones"""
        if len(source_capabilities) < 2:
            return None

        networks = [
            self.capability_networks[cap]
            for cap in source_capabilities
            if cap in self.capability_networks
        ]

        if not networks:
            return None

        # Create new capability
        new_cap_name = f"synthetic_{int(time.time())}"
        new_network = self.initialize_capability(new_cap_name)

        # Transfer knowledge from source networks
        with torch.no_grad():
            for i, layer in enumerate(new_network.network):
                if isinstance(layer, nn.Linear):
                    # Average weights from source networks
                    avg_weight = torch.mean(
                        torch.stack(
                            [
                                list(net.network[i].parameters())[0].data
                                for net in networks
                            ]
                        ),
                        dim=0,
                    )
                    layer.weight.data = avg_weight

        return new_cap_name

    def get_evolution_metrics(self) -> Dict[str, Any]:
        """Get evolution performance metrics"""
        metrics = {}

        for cap_name in self.capability_networks:
            cap_history = [
                m for m in self.evolution_history if m.capability_name == cap_name
            ]

            if cap_history:
                recent_metrics = cap_history[-10:]  # Last 10 records
                metrics[cap_name] = {
                    "current_performance": recent_metrics[-1].performance_score,
                    "improvement_rate": self._calculate_improvement_rate(
                        recent_metrics
                    ),
                    "complexity": recent_metrics[-1].complexity,
                    "adaptation_stability": self._calculate_stability(recent_metrics),
                }

        return metrics

    def _record_evolution(
        self, capability_name: str, performance_score: float, adaptation_rate: float
    ):
        """Record evolution metrics"""
        metric = EvolutionMetric(
            capability_name=capability_name,
            performance_score=performance_score,
            adaptation_rate=adaptation_rate,
            complexity=self._calculate_complexity(capability_name),
            timestamp=datetime.now(),
        )

        self.evolution_history.append(metric)
        self._save_evolution_state()

    def _calculate_adaptation_rate(self, capability_name: str) -> float:
        """Calculate capability adaptation rate"""
        history = [
            m for m in self.evolution_history if m.capability_name == capability_name
        ]

        if len(history) < 2:
            return 0.1

        recent_scores = [m.performance_score for m in history[-5:]]
        return np.std(recent_scores) * 2  # Higher variance = higher adaptation

    def _calculate_complexity(self, capability_name: str) -> int:
        """Calculate capability complexity"""
        network = self.capability_networks[capability_name]
        return sum(p.numel() for p in network.parameters())

    def _calculate_improvement_rate(self, metrics: List[EvolutionMetric]) -> float:
        """Calculate rate of improvement"""
        if len(metrics) < 2:
            return 0.0

        scores = [m.performance_score for m in metrics]
        return (scores[-1] - scores[0]) / len(scores)

    def _calculate_stability(self, metrics: List[EvolutionMetric]) -> float:
        """Calculate adaptation stability"""
        adaptation_rates = [m.adaptation_rate for m in metrics]
        return 1.0 - np.std(adaptation_rates)  # Higher stability = lower variance

    def _save_evolution_state(self):
        """Save evolution state to disk"""
        state_file = self.evolution_dir / "evolution_state.json"
        state = {
            "history": [
                {
                    "capability": m.capability_name,
                    "performance": m.performance_score,
                    "adaptation_rate": m.adaptation_rate,
                    "complexity": m.complexity,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in self.evolution_history
            ],
            "last_updated": datetime.now().isoformat(),
        }

        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
