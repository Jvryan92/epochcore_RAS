"""Ethical strategy implementation for value-aligned decision making."""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
import numpy as np

from . import StrategyComponent
from ..core.config_validator import ConfigField


@dataclass
class EthicalPrinciple:
    """Container for ethical principle definition."""

    name: str
    description: str
    weight: float = 1.0
    constraints: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    metrics: Dict[str, float] = field(default_factory=dict)


class EthicalStrategy(StrategyComponent):
    """Implements ethical decision-making capabilities."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize ethical strategy component.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__("ethical", config)
        self.principles: Dict[str, EthicalPrinciple] = {}
        self._setup_validation()
        self._initialize_principles()

    def _setup_validation(self):
        """Set up ethics-specific configuration validation."""
        self._validator.register_schema(
            self.name,
            super()._validator._schemas.get(self.name, [])
            + [
                ConfigField(
                    "principles",
                    dict,
                    True,
                    None,
                    None,
                    "Dictionary of ethical principles to enforce",
                ),
                ConfigField(
                    "min_ethical_score",
                    float,
                    False,
                    0.7,
                    lambda x: 0 <= x <= 1,
                    "Minimum ethical score required for approval",
                ),
            ],
        )

    def _initialize_principles(self):
        """Initialize ethical principles from configuration."""
        principle_configs = self.config.get("principles", {})

        for name, config in principle_configs.items():
            self.principles[name] = EthicalPrinciple(
                name=name,
                description=config.get("description", ""),
                weight=config.get("weight", 1.0),
                constraints=config.get("constraints", []),
                dependencies=set(config.get("dependencies", [])),
            )

    def _execute(self) -> Dict[str, Any]:
        """Execute ethical evaluation.

        Returns:
            Dictionary containing evaluation results
        """
        # Validate principle dependencies
        self._validate_dependencies()

        # Calculate principle scores
        principle_scores = self._evaluate_principles()

        # Get overall ethical score
        total_score = self._calculate_total_score(principle_scores)

        # Check against minimum threshold
        min_score = self.config.get("min_ethical_score", 0.7)
        is_ethical = total_score >= min_score

        return {
            "is_ethical": is_ethical,
            "total_score": total_score,
            "principle_scores": principle_scores,
            "violations": self._get_violations(principle_scores),
        }

    def _validate_dependencies(self):
        """Validate that principle dependencies are satisfied."""
        for name, principle in self.principles.items():
            missing = principle.dependencies - set(self.principles.keys())
            if missing:
                raise ValueError(
                    f"Principle {name} has missing dependencies: {missing}"
                )

    def _evaluate_principles(self) -> Dict[str, float]:
        """Evaluate all ethical principles.

        Returns:
            Dictionary mapping principles to their scores
        """
        scores = {}

        for name, principle in self.principles.items():
            # Start with base score
            base_score = principle.metrics.get("base_score", 0.5)

            # Apply constraint penalties
            penalties = sum(
                principle.metrics.get(f"constraint_{c}", 0.1)
                for c in principle.constraints
            )

            # Calculate final score
            score = max(0.0, min(1.0, base_score - penalties))
            scores[name] = score * principle.weight

        return scores

    def _calculate_total_score(self, principle_scores: Dict[str, float]) -> float:
        """Calculate overall ethical score.

        Args:
            principle_scores: Dictionary of principle scores

        Returns:
            Total weighted score
        """
        if not principle_scores:
            return 0.0

        total_weight = sum(p.weight for p in self.principles.values())

        if total_weight == 0:
            return 0.0

        weighted_sum = sum(
            score * self.principles[name].weight
            for name, score in principle_scores.items()
        )

        return weighted_sum / total_weight

    def _get_violations(
        self, principle_scores: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify ethical violations.

        Args:
            principle_scores: Dictionary of principle scores

        Returns:
            List of violation details
        """
        violations = []
        min_score = self.config.get("min_ethical_score", 0.7)

        for name, score in principle_scores.items():
            if score < min_score:
                principle = self.principles[name]
                violations.append(
                    {
                        "principle": name,
                        "score": score,
                        "description": principle.description,
                        "constraints": principle.constraints,
                    }
                )

        return violations

    def add_principle(
        self,
        name: str,
        description: str,
        weight: float = 1.0,
        constraints: Optional[List[str]] = None,
        dependencies: Optional[Set[str]] = None,
    ):
        """Add a new ethical principle.

        Args:
            name: Principle identifier
            description: Principle description
            weight: Principle weight
            constraints: List of constraints
            dependencies: Set of dependent principles
        """
        self.principles[name] = EthicalPrinciple(
            name=name,
            description=description,
            weight=weight,
            constraints=constraints or [],
            dependencies=dependencies or set(),
        )

    def update_metrics(self, principle: str, metrics: Dict[str, float]):
        """Update metrics for a principle.

        Args:
            principle: Principle identifier
            metrics: New metric values
        """
        if principle in self.principles:
            self.principles[principle].metrics.update(metrics)

    def get_principle(self, name: str) -> Optional[EthicalPrinciple]:
        """Get a specific ethical principle.

        Args:
            name: Principle identifier

        Returns:
            EthicalPrinciple if found, None otherwise
        """
        return self.principles.get(name)
