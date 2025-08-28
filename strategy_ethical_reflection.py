from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import torch
import torch.nn as nn
from pathlib import Path
import json
from enum import Enum

@dataclass
class ReflectionEntry:
    """Record of ethical decision reflection"""
    decision_id: str
    timestamp: datetime
    context: Dict[str, Any]
    principles_applied: List[str]
    outcome_assessment: Dict[str, float]
    lessons_learned: List[str]
    improvement_suggestions: List[str]

@dataclass
class MetacognitiveState:
    """Current state of ethical metacognition"""
    confidence: float  # 0-1 scale of decision-making confidence
    uncertainty_awareness: float  # 0-1 scale of known unknowns
    principle_weights: Dict[str, float]  # Learned importance of different principles
    adaptation_rate: float  # Rate of incorporating new insights

class EthicalReflectionEngine:
    """
    Metacognitive engine for reflecting on and improving ethical decision-making.
    
    Features:
    - Decision outcome tracking
    - Principle effectiveness analysis
    - Stakeholder impact learning
    - Adaptive moral framework
    - Continuous ethical improvement
    """
    
    def __init__(self, reflection_dir: str = ".reflection"):
        self.reflection_dir = Path(reflection_dir)
        self.reflection_dir.mkdir(parents=True, exist_ok=True)
        
        self.history: List[ReflectionEntry] = []
        self.metacognitive_state = MetacognitiveState(
            confidence=0.5,  # Start with moderate confidence
            uncertainty_awareness=0.7,  # High initial uncertainty awareness
            principle_weights={},  # Will be learned from experience
            adaptation_rate=0.1  # Conservative learning rate
        )
        
        # Initialize learning components
        self.principle_effectiveness = {}
        self.stakeholder_impact_memory = {}
        self.decision_patterns = {}
        
        # Load previous reflections if available
        self._load_history()
        
    def reflect_on_decision(self,
                          decision_id: str,
                          context: Dict[str, Any],
                          principles: List[str],
                          outcomes: Dict[str, float]) -> ReflectionEntry:
        """
        Reflect on an ethical decision and its outcomes
        """
        # Analyze decision effectiveness
        effectiveness = self._analyze_effectiveness(principles, outcomes)
        
        # Update principle weights based on outcomes
        self._update_principle_weights(principles, effectiveness)
        
        # Identify patterns and trends
        patterns = self._identify_decision_patterns(context, principles, outcomes)
        
        # Generate insights and lessons
        lessons = self._generate_lessons(context, principles, outcomes, patterns)
        
        # Create improvement suggestions
        improvements = self._suggest_improvements(lessons, patterns)
        
        # Update metacognitive state
        self._update_metacognitive_state(effectiveness, patterns)
        
        reflection = ReflectionEntry(
            decision_id=decision_id,
            timestamp=datetime.now(),
            context=context,
            principles_applied=principles,
            outcome_assessment={
                "effectiveness": effectiveness,
                "confidence": self.metacognitive_state.confidence,
                "adaptability": self.metacognitive_state.adaptation_rate
            },
            lessons_learned=lessons,
            improvement_suggestions=improvements
        )
        
        self.history.append(reflection)
        self._save_reflection(reflection)
        
        return reflection
        
    def get_ethical_insights(self) -> Dict[str, Any]:
        """
        Get accumulated ethical insights and learning
        """
        if not self.history:
            return {"status": "No reflection history available"}
            
        recent_reflections = self.history[-10:]
        
        return {
            "principle_effectiveness": self.principle_effectiveness,
            "confidence_trend": self._analyze_confidence_trend(),
            "most_effective_principles": self._get_top_principles(5),
            "recent_lessons": [r.lessons_learned for r in recent_reflections],
            "adaptation_metrics": {
                "current_rate": self.metacognitive_state.adaptation_rate,
                "uncertainty_awareness": self.metacognitive_state.uncertainty_awareness,
                "principle_weights": self.metacognitive_state.principle_weights
            }
        }
        
    def get_decision_support(self,
                           context: Dict[str, Any],
                           proposed_principles: List[str]) -> Dict[str, Any]:
        """
        Provide decision support based on learned insights
        """
        similar_cases = self._find_similar_cases(context)
        effective_principles = self._get_effective_principles(context)
        
        return {
            "recommended_principles": effective_principles,
            "confidence_score": self._calculate_confidence(context, proposed_principles),
            "similar_cases": [
                {
                    "decision_id": case.decision_id,
                    "effectiveness": case.outcome_assessment["effectiveness"],
                    "key_lessons": case.lessons_learned[:2]
                }
                for case in similar_cases[:3]
            ],
            "suggested_considerations": self._generate_considerations(
                context,
                similar_cases
            )
        }
        
    def _analyze_effectiveness(self,
                             principles: List[str],
                             outcomes: Dict[str, float]) -> float:
        """Analyze the effectiveness of applied principles"""
        weighted_outcomes = []
        
        for principle in principles:
            weight = self.metacognitive_state.principle_weights.get(principle, 0.5)
            relevant_outcomes = [
                v for k, v in outcomes.items()
                if k.startswith(principle.lower())
            ]
            if relevant_outcomes:
                weighted_outcomes.append(
                    weight * sum(relevant_outcomes) / len(relevant_outcomes)
                )
                
        return sum(weighted_outcomes) / len(weighted_outcomes) if weighted_outcomes else 0.5
        
    def _update_principle_weights(self,
                                principles: List[str],
                                effectiveness: float):
        """Update weights of ethical principles based on outcomes"""
        for principle in principles:
            current_weight = self.metacognitive_state.principle_weights.get(principle, 0.5)
            update = self.metacognitive_state.adaptation_rate * (effectiveness - current_weight)
            self.metacognitive_state.principle_weights[principle] = current_weight + update
            
    def _identify_decision_patterns(self,
                                  context: Dict[str, Any],
                                  principles: List[str],
                                  outcomes: Dict[str, float]) -> Dict[str, Any]:
        """Identify patterns in ethical decision-making"""
        pattern_key = frozenset(principles)
        
        if pattern_key not in self.decision_patterns:
            self.decision_patterns[pattern_key] = {
                "count": 0,
                "total_effectiveness": 0,
                "contexts": []
            }
            
        pattern = self.decision_patterns[pattern_key]
        pattern["count"] += 1
        pattern["total_effectiveness"] += sum(outcomes.values()) / len(outcomes)
        pattern["contexts"].append(context)
        
        return {
            "frequency": pattern["count"],
            "avg_effectiveness": pattern["total_effectiveness"] / pattern["count"],
            "context_similarity": self._calculate_context_similarity(
                context,
                pattern["contexts"][-2] if len(pattern["contexts"]) > 1 else None
            )
        }
        
    def _generate_lessons(self,
                         context: Dict[str, Any],
                         principles: List[str],
                         outcomes: Dict[str, float],
                         patterns: Dict[str, Any]) -> List[str]:
        """Generate lessons learned from the decision"""
        lessons = []
        
        # Effectiveness-based lessons
        if patterns["avg_effectiveness"] > 0.7:
            lessons.append(
                f"Principle combination {', '.join(principles)} is consistently effective"
            )
        elif patterns["avg_effectiveness"] < 0.3:
            lessons.append(
                f"Principle combination {', '.join(principles)} may need refinement"
            )
            
        # Context-based lessons
        if patterns["context_similarity"] > 0.8:
            lessons.append(
                "Similar contexts lead to consistent ethical considerations"
            )
        elif patterns["context_similarity"] < 0.2:
            lessons.append(
                "Ethical principles show flexibility across different contexts"
            )
            
        return lessons
        
    def _suggest_improvements(self,
                            lessons: List[str],
                            patterns: Dict[str, Any]) -> List[str]:
        """Generate suggestions for improving ethical decision-making"""
        improvements = []
        
        if patterns["avg_effectiveness"] < 0.5:
            improvements.append(
                "Consider incorporating additional ethical principles"
            )
            
        if patterns["context_similarity"] < 0.3:
            improvements.append(
                "Develop more context-specific ethical guidelines"
            )
            
        # Add adaptive learning rate suggestion
        current_rate = self.metacognitive_state.adaptation_rate
        if current_rate < 0.05:
            improvements.append(
                "Consider increasing adaptation rate to learn from experiences faster"
            )
        elif current_rate > 0.3:
            improvements.append(
                "Consider reducing adaptation rate to maintain stability"
            )
            
        return improvements
        
    def _update_metacognitive_state(self,
                                  effectiveness: float,
                                  patterns: Dict[str, Any]):
        """Update the metacognitive state based on reflection"""
        # Update confidence based on effectiveness and pattern recognition
        confidence_update = 0.1 * (effectiveness - self.metacognitive_state.confidence)
        self.metacognitive_state.confidence = min(
            1.0,
            max(0.0, self.metacognitive_state.confidence + confidence_update)
        )
        
        # Update uncertainty awareness based on pattern recognition
        if patterns["context_similarity"] < 0.3:
            self.metacognitive_state.uncertainty_awareness = min(
                1.0,
                self.metacognitive_state.uncertainty_awareness + 0.1
            )
        else:
            self.metacognitive_state.uncertainty_awareness = max(
                0.0,
                self.metacognitive_state.uncertainty_awareness - 0.05
            )
            
        # Adjust adaptation rate based on learning progress
        if len(self.history) > 10:
            recent_effectiveness = np.mean([
                r.outcome_assessment["effectiveness"]
                for r in self.history[-10:]
            ])
            if recent_effectiveness > 0.7:
                self.metacognitive_state.adaptation_rate *= 0.9  # Reduce learning rate
            elif recent_effectiveness < 0.3:
                self.metacognitive_state.adaptation_rate *= 1.1  # Increase learning rate
                
    def _find_similar_cases(self,
                           context: Dict[str, Any],
                           threshold: float = 0.7) -> List[ReflectionEntry]:
        """Find similar historical cases"""
        similar_cases = []
        
        for entry in reversed(self.history):  # Most recent first
            similarity = self._calculate_context_similarity(context, entry.context)
            if similarity >= threshold:
                similar_cases.append(entry)
                
        return similar_cases
        
    def _get_effective_principles(self,
                                context: Dict[str, Any]) -> List[str]:
        """Get historically effective principles for similar contexts"""
        principles = []
        weights = []
        
        for principle, weight in self.metacognitive_state.principle_weights.items():
            relevant_cases = [
                entry for entry in self.history
                if principle in entry.principles_applied
            ]
            if relevant_cases:
                avg_effectiveness = np.mean([
                    entry.outcome_assessment["effectiveness"]
                    for entry in relevant_cases
                ])
                principles.append(principle)
                weights.append(weight * avg_effectiveness)
                
        # Return top principles by weighted effectiveness
        sorted_principles = [
            p for _, p in sorted(zip(weights, principles), reverse=True)
        ]
        return sorted_principles[:5]  # Top 5 principles
        
    def _calculate_confidence(self,
                            context: Dict[str, Any],
                            principles: List[str]) -> float:
        """Calculate confidence in a proposed decision"""
        similar_cases = self._find_similar_cases(context)
        
        if not similar_cases:
            return 0.5  # Moderate confidence with no similar cases
            
        # Calculate confidence based on:
        # 1. Principle effectiveness in similar cases
        # 2. Current metacognitive state
        # 3. Pattern recognition strength
        principle_confidence = np.mean([
            self.metacognitive_state.principle_weights.get(p, 0.5)
            for p in principles
        ])
        
        pattern_confidence = self._calculate_pattern_confidence(
            principles,
            similar_cases
        )
        
        return 0.4 * principle_confidence + \
               0.3 * self.metacognitive_state.confidence + \
               0.3 * pattern_confidence
               
    def _calculate_context_similarity(self,
                                    context1: Dict[str, Any],
                                    context2: Optional[Dict[str, Any]]) -> float:
        """Calculate similarity between two contexts"""
        if not context2:
            return 0.0
            
        shared_keys = set(context1.keys()) & set(context2.keys())
        if not shared_keys:
            return 0.0
            
        similarities = []
        for key in shared_keys:
            if isinstance(context1[key], (int, float)) and \
               isinstance(context2[key], (int, float)):
                # Numerical comparison
                max_val = max(abs(context1[key]), abs(context2[key]))
                if max_val == 0:
                    similarities.append(1.0)
                else:
                    similarities.append(
                        1.0 - abs(context1[key] - context2[key]) / max_val
                    )
            else:
                # String/boolean comparison
                similarities.append(1.0 if context1[key] == context2[key] else 0.0)
                
        return sum(similarities) / len(similarities)
        
    def _calculate_pattern_confidence(self,
                                    principles: List[str],
                                    similar_cases: List[ReflectionEntry]) -> float:
        """Calculate confidence based on pattern recognition"""
        if not similar_cases:
            return 0.5
            
        # Calculate how often these principles were successful in similar cases
        principle_set = set(principles)
        successful_applications = sum(
            1 for case in similar_cases
            if set(case.principles_applied) == principle_set and
            case.outcome_assessment["effectiveness"] > 0.7
        )
        
        return successful_applications / len(similar_cases)
        
    def _analyze_confidence_trend(self) -> Dict[str, float]:
        """Analyze trend in decision-making confidence"""
        if len(self.history) < 2:
            return {"trend": 0.0, "volatility": 0.0}
            
        confidences = [
            entry.outcome_assessment["confidence"]
            for entry in self.history
        ]
        
        trend = (confidences[-1] - confidences[0]) / len(confidences)
        volatility = np.std(confidences)
        
        return {
            "trend": float(trend),
            "volatility": float(volatility)
        }
        
    def _get_top_principles(self, n: int = 5) -> List[Tuple[str, float]]:
        """Get top-n most effective principles"""
        sorted_principles = sorted(
            self.metacognitive_state.principle_weights.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_principles[:n]
        
    def _save_reflection(self, reflection: ReflectionEntry):
        """Save reflection entry to disk"""
        reflection_path = self.reflection_dir / f"reflection_{reflection.decision_id}.json"
        with open(reflection_path, 'w') as f:
            json.dump(
                {
                    "decision_id": reflection.decision_id,
                    "timestamp": reflection.timestamp.isoformat(),
                    "context": reflection.context,
                    "principles_applied": reflection.principles_applied,
                    "outcome_assessment": reflection.outcome_assessment,
                    "lessons_learned": reflection.lessons_learned,
                    "improvement_suggestions": reflection.improvement_suggestions
                },
                f,
                indent=2
            )
            
    def _load_history(self):
        """Load reflection history from disk"""
        if not self.reflection_dir.exists():
            return
            
        for reflection_file in self.reflection_dir.glob("reflection_*.json"):
            try:
                with open(reflection_file, 'r') as f:
                    data = json.load(f)
                    reflection = ReflectionEntry(
                        decision_id=data["decision_id"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        context=data["context"],
                        principles_applied=data["principles_applied"],
                        outcome_assessment=data["outcome_assessment"],
                        lessons_learned=data["lessons_learned"],
                        improvement_suggestions=data["improvement_suggestions"]
                    )
                    self.history.append(reflection)
            except Exception as e:
                print(f"Error loading reflection {reflection_file}: {e}")
                continue
