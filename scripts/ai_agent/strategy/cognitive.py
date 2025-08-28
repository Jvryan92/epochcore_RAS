"""Cognitive strategy implementation for advanced decision making."""

from typing import Dict, Any, List, Optional
import numpy as np
from dataclasses import dataclass, field

from . import StrategyComponent
from ..core.config_validator import ConfigField, validate_percentage


@dataclass
class CognitiveState:
    """Container for cognitive processing state."""

    confidence: float = 0.0
    uncertainty: float = 1.0
    context_weight: float = 0.5
    historical_decisions: List[Dict[str, Any]] = field(default_factory=list)
    active_contexts: List[str] = field(default_factory=list)
    decision_weights: Dict[str, float] = field(default_factory=dict)


class CognitiveStrategy(StrategyComponent):
    """Implements cognitive decision-making capabilities."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize cognitive strategy component.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__("cognitive", config)
        self.state = CognitiveState()
        self._setup_validation()

    def _setup_validation(self):
        """Set up cognitive-specific configuration validation."""
        self._validator.register_schema(
            self.name,
            super()._validator._schemas.get(self.name, []) + [
                ConfigField(
                    "confidence_threshold",
                    float,
                    False,
                    0.7,
                    validate_percentage,
                    "Minimum confidence threshold for decisions"
                ),
                ConfigField(
                    "max_uncertainty",
                    float,
                    False,
                    0.3,
                    validate_percentage,
                    "Maximum acceptable uncertainty"
                ),
                ConfigField(
                    "context_decay",
                    float,
                    False,
                    0.1,
                    lambda x: 0 <= x <= 1,
                    "Rate at which context influence decays"
                )
            ]
        )

    def _execute(self) -> Dict[str, Any]:
        """Execute cognitive processing.

        Returns:
            Dictionary containing processing results
        """
        # Update state based on configuration
        self._update_state()

        # Process active contexts
        context_influence = self._process_contexts()

        # Make decision incorporating context
        decision = self._make_decision(context_influence)

        # Update historical records
        self._update_history(decision)

        return {
            "decision": decision,
            "confidence": self.state.confidence,
            "uncertainty": self.state.uncertainty,
            "active_contexts": self.state.active_contexts,
            "context_influence": context_influence
        }

    def _update_state(self):
        """Update internal state based on configuration and history."""
        # Decay uncertainty over time
        self.state.uncertainty *= (1 - self.config.get("context_decay", 0.1))
        self.state.uncertainty = max(0.1, min(1.0, self.state.uncertainty))

        # Update confidence based on successful decisions
        if self.state.historical_decisions:
            recent_success = np.mean([
                d.get("success", False) 
                for d in self.state.historical_decisions[-5:]
            ])
            self.state.confidence = (
                0.7 * self.state.confidence + 0.3 * recent_success
            )

    def _process_contexts(self) -> Dict[str, float]:
        """Process active contexts and their influence.

        Returns:
            Dictionary mapping contexts to their influence values
        """
        context_weights = {}
        total_weight = 0

        for context in self.state.active_contexts:
            # Calculate temporal decay
            age = len(self.state.historical_decisions)
            decay = np.exp(-self.config.get("context_decay", 0.1) * age)
            
            # Get base weight from state
            base_weight = self.state.decision_weights.get(context, 0.5)
            
            # Combine with decay
            weight = base_weight * decay
            context_weights[context] = weight
            total_weight += weight

        # Normalize weights
        if total_weight > 0:
            return {
                k: v/total_weight 
                for k, v in context_weights.items()
            }
        return context_weights

    def _make_decision(
        self,
        context_influence: Dict[str, float]
    ) -> Dict[str, Any]:
        """Make a decision incorporating context influence.

        Args:
            context_influence: Dictionary of context influence weights

        Returns:
            Dictionary containing decision details
        """
        # Calculate overall confidence
        confidence = self.state.confidence * (1 - self.state.uncertainty)

        # Check if we meet the confidence threshold
        threshold = self.config.get("confidence_threshold", 0.7)
        can_decide = confidence >= threshold

        # Incorporate context influence
        strongest_context = max(
            context_influence.items(),
            key=lambda x: x[1],
            default=("none", 0.0)
        )

        return {
            "can_decide": can_decide,
            "confidence": confidence,
            "uncertainty": self.state.uncertainty,
            "dominant_context": strongest_context[0],
            "context_strength": strongest_context[1]
        }

    def _update_history(self, decision: Dict[str, Any]):
        """Update decision history.

        Args:
            decision: Decision data to record
        """
        self.state.historical_decisions.append(decision)
        
        # Keep only last 100 decisions
        if len(self.state.historical_decisions) > 100:
            self.state.historical_decisions = (
                self.state.historical_decisions[-100:]
            )

    def add_context(self, context: str, weight: float = 0.5):
        """Add a new context to consider in decision making.

        Args:
            context: Context identifier
            weight: Initial context weight
        """
        if context not in self.state.active_contexts:
            self.state.active_contexts.append(context)
            self.state.decision_weights[context] = weight

    def remove_context(self, context: str):
        """Remove a context from consideration.

        Args:
            context: Context to remove
        """
        if context in self.state.active_contexts:
            self.state.active_contexts.remove(context)
            self.state.decision_weights.pop(context, None)

    def adjust_confidence(self, adjustment: float):
        """Adjust the confidence level.

        Args:
            adjustment: Amount to adjust confidence by
        """
        self.state.confidence = max(0.0, min(1.0, 
            self.state.confidence + adjustment
        ))

    def set_uncertainty(self, uncertainty: float):
        """Set the uncertainty level.

        Args:
            uncertainty: New uncertainty value
        """
        self.state.uncertainty = max(0.0, min(1.0, uncertainty))
