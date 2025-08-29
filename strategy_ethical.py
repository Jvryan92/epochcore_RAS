from datetime import datetime
from pathlib import Path
import json
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import torch
import torch.nn as nn
from enum import Enum
from abc import ABC, abstractmethod
from ethical_reflection import EthicalReflectionEngine


class EthicalPrinciple(Enum):
    BENEFICENCE = "maximize_benefit"
    NONMALEFICENCE = "prevent_harm"
    AUTONOMY = "respect_autonomy"
    JUSTICE = "ensure_fairness"
    TRANSPARENCY = "maintain_transparency"
    ACCOUNTABILITY = "ensure_accountability"
    PRIVACY = "protect_privacy"
    SUSTAINABILITY = "environmental_responsibility"


@dataclass
class EthicalConstraint:
    principle: EthicalPrinciple
    threshold: float
    priority: int
    description: str


@dataclass
class EthicalAssessment:
    action_id: str
    principles_evaluated: List[EthicalPrinciple]
    scores: Dict[EthicalPrinciple, float]
    overall_score: float
    constraints_satisfied: bool
    reasoning: List[str]
    timestamp: datetime


@dataclass
class Impact:
    direct_effects: Dict[str, float]
    indirect_effects: Dict[str, float]
    long_term_effects: Dict[str, float]
    uncertainty: float
    reversibility: float
    stakeholders: List[str]


class ValueAlignmentModel(nn.Module):
    """Neural network for value alignment assessment"""

    def __init__(self, input_size: int, hidden_size: int = 128):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, len(EthicalPrinciple)),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return torch.sigmoid(self.network(x))


class AbstractEthicalStrategy(ABC):
    @abstractmethod
    def evaluate_action(self, context: Dict[str, Any]) -> float:
        pass


class UtilitarianStrategy(AbstractEthicalStrategy):
    def evaluate_action(self, context: Dict[str, Any]) -> float:
        benefits = sum(context.get("benefits", {}).values())
        harms = sum(context.get("harms", {}).values())
        return benefits - harms


class DeontologicalStrategy(AbstractEthicalStrategy):
    def evaluate_action(self, context: Dict[str, Any]) -> float:
        rules_followed = context.get("rules_followed", 0)
        rules_violated = context.get("rules_violated", 0)
        return 1.0 if rules_violated == 0 else 0.0


class VirtueEthicsStrategy(AbstractEthicalStrategy):
    def evaluate_action(self, context: Dict[str, Any]) -> float:
        virtues = context.get("virtues", {})
        return sum(virtues.values()) / len(virtues) if virtues else 0.0


class EthicalEngine:
    """
    Advanced ethical decision-making engine with value alignment,
    impact assessment, and moral constraint satisfaction.

    Features:
    - Multi-framework ethical evaluation
    - Impact prediction and assessment
    - Value alignment verification
    - Constraint satisfaction
    - Transparent reasoning
    """

    def __init__(self, ethical_dir: str = ".ethical"):
        self.ethical_dir = Path(ethical_dir)
        self.ethical_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.value_model = ValueAlignmentModel(input_size=64)
        self.constraints: List[EthicalConstraint] = []
        self.assessments: List[EthicalAssessment] = []

        # Initialize reflection engine
        self.reflection = EthicalReflectionEngine(str(self.ethical_dir / "reflection"))

        # Ethical strategies
        self.strategies = {
            "utilitarian": UtilitarianStrategy(),
            "deontological": DeontologicalStrategy(),
            "virtue": VirtueEthicsStrategy(),
        }

        # Impact tracking
        self.impact_history: Dict[str, Impact] = {}
        self.stakeholder_registry: Dict[str, Dict[str, Any]] = {}

        # Initialize baseline constraints
        self._initialize_baseline_constraints()

    def assess_action(
        self,
        action_id: str,
        context: Dict[str, Any],
        stakeholders: Optional[List[str]] = None,
    ) -> EthicalAssessment:
        """Perform comprehensive ethical assessment of an action"""
        # Prepare feature vector
        features = self._encode_context(context)

        # Get value alignment scores
        with torch.no_grad():
            principle_scores = self.value_model(features).numpy()

        # Evaluate using different ethical frameworks
        framework_scores = {
            framework: strategy.evaluate_action(context)
            for framework, strategy in self.strategies.items()
        }

        # Calculate overall score with weighted combination
        overall_score = (
            0.4 * np.mean(principle_scores)  # Value alignment
            + 0.3 * framework_scores["utilitarian"]  # Utility
            + 0.2 * framework_scores["deontological"]  # Rules
            + 0.1 * framework_scores["virtue"]  # Character
        )

        # Check constraint satisfaction
        constraints_satisfied = self._check_constraints(principle_scores)

        # Generate reasoning
        reasoning = self._generate_reasoning(
            principle_scores, framework_scores, constraints_satisfied
        )

        assessment = EthicalAssessment(
            action_id=action_id,
            principles_evaluated=list(EthicalPrinciple),
            scores={p: s for p, s in zip(EthicalPrinciple, principle_scores)},
            overall_score=float(overall_score),
            constraints_satisfied=constraints_satisfied,
            reasoning=reasoning,
            timestamp=datetime.now(),
        )

        # Reflect on the decision
        reflection = self.reflection.reflect_on_decision(
            decision_id=action_id,
            context=context,
            principles=[p.value for p in EthicalPrinciple],
            outcomes={
                "overall_score": overall_score,
                "framework_scores": framework_scores,
                "principle_scores": {
                    p.value: s for p, s in zip(EthicalPrinciple, principle_scores)
                },
            },
        )

        # Get decision support for future similar cases
        decision_support = self.reflection.get_decision_support(
            context=context, proposed_principles=[p.value for p in EthicalPrinciple]
        )

        # Add reflection insights to reasoning
        reasoning.extend(
            [f"Reflection: {lesson}" for lesson in reflection.lessons_learned[:2]]
        )
        reasoning.extend(
            [
                f"Improvement: {suggestion}"
                for suggestion in reflection.improvement_suggestions[:2]
            ]
        )

        self.assessments.append(assessment)
        return assessment

    def predict_impact(
        self, action_id: str, context: Dict[str, Any], time_horizon: str = "long_term"
    ) -> Impact:
        """Predict and assess the impact of an action"""
        # Analyze direct effects
        direct_effects = self._analyze_direct_effects(context)

        # Model indirect effects through stakeholder network
        indirect_effects = self._model_indirect_effects(
            direct_effects, context.get("stakeholders", [])
        )

        # Project long-term consequences
        long_term_effects = self._project_long_term_effects(
            direct_effects, indirect_effects, time_horizon
        )

        # Calculate uncertainty and reversibility
        uncertainty = self._calculate_uncertainty(
            direct_effects, indirect_effects, long_term_effects
        )

        reversibility = self._assess_reversibility(
            direct_effects, indirect_effects, long_term_effects
        )

        impact = Impact(
            direct_effects=direct_effects,
            indirect_effects=indirect_effects,
            long_term_effects=long_term_effects,
            uncertainty=uncertainty,
            reversibility=reversibility,
            stakeholders=list(self.stakeholder_registry.keys()),
        )

        self.impact_history[action_id] = impact
        return impact

    def add_constraint(self, constraint: EthicalConstraint):
        """Add an ethical constraint to the system"""
        self.constraints.append(constraint)
        self._save_constraints()

    def register_stakeholder(
        self,
        stakeholder_id: str,
        interests: Dict[str, float],
        impact_sensitivity: float = 1.0,
    ):
        """Register a stakeholder and their interests"""
        self.stakeholder_registry[stakeholder_id] = {
            "interests": interests,
            "impact_sensitivity": impact_sensitivity,
            "registered_at": datetime.now().isoformat(),
        }

    def get_ethical_metrics(self) -> Dict[str, Any]:
        """Get metrics about ethical processing including reflection insights"""
        if not self.assessments:
            return {"status": "No assessments performed"}

        recent_assessments = self.assessments[-10:]

        # Get base metrics
        metrics = {
            "average_score": np.mean([a.overall_score for a in recent_assessments]),
            "constraint_satisfaction_rate": np.mean(
                [1 if a.constraints_satisfied else 0 for a in recent_assessments]
            ),
            "principle_performance": {
                p.value: np.mean([a.scores[p] for a in recent_assessments])
                for p in EthicalPrinciple
            },
            "impact_metrics": {
                "average_uncertainty": np.mean(
                    [i.uncertainty for i in self.impact_history.values()]
                ),
                "average_reversibility": np.mean(
                    [i.reversibility for i in self.impact_history.values()]
                ),
            },
            "stakeholders": len(self.stakeholder_registry),
        }

        # Add reflection insights
        reflection_insights = self.reflection.get_ethical_insights()
        metrics.update(
            {
                "metacognitive_metrics": {
                    "confidence_trend": reflection_insights["confidence_trend"],
                    "top_principles": reflection_insights["most_effective_principles"],
                    "adaptation_rate": reflection_insights["adaptation_metrics"][
                        "current_rate"
                    ],
                    "uncertainty_awareness": reflection_insights["adaptation_metrics"][
                        "uncertainty_awareness"
                    ],
                },
                "learning_progress": {
                    "principle_effectiveness": reflection_insights[
                        "principle_effectiveness"
                    ],
                    "recent_lessons": reflection_insights["recent_lessons"],
                },
            }
        )

        return metrics

    def _initialize_baseline_constraints(self):
        """Initialize basic ethical constraints"""
        baseline_constraints = [
            EthicalConstraint(
                principle=EthicalPrinciple.NONMALEFICENCE,
                threshold=0.7,
                priority=1,
                description="Prevent significant harm to any stakeholder",
            ),
            EthicalConstraint(
                principle=EthicalPrinciple.PRIVACY,
                threshold=0.8,
                priority=2,
                description="Ensure data privacy and protection",
            ),
            EthicalConstraint(
                principle=EthicalPrinciple.TRANSPARENCY,
                threshold=0.6,
                priority=3,
                description="Maintain transparency in decision-making",
            ),
        ]

        self.constraints.extend(baseline_constraints)
        self._save_constraints()

    def _encode_context(self, context: Dict[str, Any]) -> torch.Tensor:
        """Encode context for value alignment assessment"""
        # Implement context encoding logic
        # This is a simplified version
        return torch.randn(64)  # Placeholder

    def _check_constraints(self, principle_scores: np.ndarray) -> bool:
        """Check if all ethical constraints are satisfied"""
        for constraint in self.constraints:
            principle_idx = list(EthicalPrinciple).index(constraint.principle)
            if principle_scores[principle_idx] < constraint.threshold:
                return False
        return True

    def _generate_reasoning(
        self,
        principle_scores: np.ndarray,
        framework_scores: Dict[str, float],
        constraints_satisfied: bool,
    ) -> List[str]:
        """Generate explanatory reasoning for the ethical assessment"""
        reasoning = []

        # Add principle-based reasoning
        for principle, score in zip(EthicalPrinciple, principle_scores):
            if score > 0.8:
                reasoning.append(f"Strong alignment with {principle.value}")
            elif score < 0.4:
                reasoning.append(f"Potential conflict with {principle.value}")

        # Add framework-based reasoning
        for framework, score in framework_scores.items():
            reasoning.append(f"{framework.capitalize()} analysis: {score:.2f}")

        # Add constraint satisfaction
        if constraints_satisfied:
            reasoning.append("All ethical constraints satisfied")
        else:
            reasoning.append("Some ethical constraints not met")

        return reasoning

    def _save_constraints(self):
        """Save ethical constraints to disk"""
        constraints_file = self.ethical_dir / "constraints.json"
        with open(constraints_file, "w") as f:
            json.dump(
                [
                    {
                        "principle": c.principle.value,
                        "threshold": c.threshold,
                        "priority": c.priority,
                        "description": c.description,
                    }
                    for c in self.constraints
                ],
                f,
                indent=2,
            )

    def _analyze_direct_effects(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Analyze immediate effects of an action"""
        effects = {}
        for key, value in context.items():
            if isinstance(value, (int, float)):
                effects[key] = float(value)
            elif isinstance(value, bool):
                effects[key] = 1.0 if value else 0.0
        return effects

    def _model_indirect_effects(
        self, direct_effects: Dict[str, float], stakeholders: List[str]
    ) -> Dict[str, float]:
        """Model indirect effects through stakeholder network"""
        indirect_effects = {}
        for effect, magnitude in direct_effects.items():
            for stakeholder in stakeholders:
                if stakeholder in self.stakeholder_registry:
                    sensitivity = self.stakeholder_registry[stakeholder][
                        "impact_sensitivity"
                    ]
                    indirect_effects[f"{effect}_{stakeholder}"] = (
                        magnitude * sensitivity
                    )
        return indirect_effects

    def _project_long_term_effects(
        self,
        direct_effects: Dict[str, float],
        indirect_effects: Dict[str, float],
        time_horizon: str,
    ) -> Dict[str, float]:
        """Project long-term effects based on current impact"""
        decay_factor = 0.8 if time_horizon == "long_term" else 0.5

        long_term = {}
        # Combine and decay effects over time
        all_effects = {**direct_effects, **indirect_effects}
        for effect, magnitude in all_effects.items():
            long_term[f"long_term_{effect}"] = magnitude * decay_factor

        return long_term

    def _calculate_uncertainty(
        self,
        direct_effects: Dict[str, float],
        indirect_effects: Dict[str, float],
        long_term_effects: Dict[str, float],
    ) -> float:
        """Calculate uncertainty in impact prediction"""
        # Uncertainty increases with effect chain length and magnitude
        direct_uncertainty = (
            np.std(list(direct_effects.values())) if direct_effects else 0
        )
        indirect_uncertainty = (
            np.std(list(indirect_effects.values())) if indirect_effects else 0
        )
        long_term_uncertainty = (
            np.std(list(long_term_effects.values())) if long_term_effects else 0
        )

        # Weight uncertainties by their temporal distance
        return (
            0.2 * direct_uncertainty
            + 0.3 * indirect_uncertainty
            + 0.5 * long_term_uncertainty
        )

    def _assess_reversibility(
        self,
        direct_effects: Dict[str, float],
        indirect_effects: Dict[str, float],
        long_term_effects: Dict[str, float],
    ) -> float:
        """Assess the reversibility of predicted impacts"""
        # Higher magnitude and longer-term effects are less reversible
        total_magnitude = (
            sum(map(abs, direct_effects.values()))
            + sum(map(abs, indirect_effects.values()))
            + sum(map(abs, long_term_effects.values()))
        )

        # Reversibility decreases exponentially with magnitude
        return np.exp(-0.1 * total_magnitude)
