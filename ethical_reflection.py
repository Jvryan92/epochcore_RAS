"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""
Ethical Reflection Engine for advanced moral decision making.
"""

from dataclasses import dataclass
from typing import Dict, List, Any
from pathlib import Path
import json
from datetime import datetime
import numpy as np

class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

@dataclass
class ReflectionOutcome:
    """Outcome of ethical reflection"""
    lessons_learned: List[str]
    improvement_suggestions: List[str]
    confidence: float
    adaptation_metrics: Dict[str, float]

class EthicalReflectionEngine:
    """
    Advanced reflection engine for ethical decision making.
    Provides metacognitive capabilities to learn from past decisions.
    """
    
    def __init__(self, reflection_dir: str = ".ethical/reflection"):
        self.reflection_dir = Path(reflection_dir)
        self.reflection_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.reflection_dir / "reflection_history.json"
        self.insights_file = self.reflection_dir / "ethical_insights.json"
        
        # Initialize with empty state
        self.reflection_history = []
        self.ethical_insights = {
            "confidence_trend": 0.0,
            "most_effective_principles": [],
            "adaptation_metrics": {
                "current_rate": 0.0,
                "uncertainty_awareness": 0.0
            },
            "principle_effectiveness": {},
            "recent_lessons": []
        }
        
        # Save initial state if files don't exist
        if not self.history_file.exists():
            with open(self.history_file, 'w') as f:
                json.dump([], f, cls=NumpyJSONEncoder)
                
        if not self.insights_file.exists():
            with open(self.insights_file, 'w') as f:
                json.dump(self.ethical_insights, f, cls=NumpyJSONEncoder)
        
        # Now try to load any existing history
        self._load_history()
        
    def reflect_on_decision(self,
                          decision_id: str,
                          context: Dict[str, Any],
                          principles: List[str],
                          outcomes: Dict[str, Any]) -> ReflectionOutcome:
        """
        Reflect on a decision to extract lessons and insights.
        """
        # Analyze effectiveness of principles
        principle_performance = {
            p: outcomes["principle_scores"].get(p, 0.0)  
            for p in principles
        }
        
        # Generate lessons based on performance
        lessons = []
        for principle, score in principle_performance.items():
            if score > 0.8:
                lessons.append(f"Principle '{principle}' was highly effective")
            elif score < 0.4:
                lessons.append(f"Principle '{principle}' may need strengthening")
        
        # Calculate confidence based on outcomes
        confidence = self._calculate_confidence(outcomes)
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(
            principle_performance,
            outcomes["overall_score"],
            context
        )
        
        # Update adaptation metrics
        adaptation_metrics = self._update_adaptation_metrics(
            confidence,
            outcomes["overall_score"]
        )
        
        reflection = ReflectionOutcome(
            lessons_learned=lessons,
            improvement_suggestions=suggestions,
            confidence=confidence,
            adaptation_metrics=adaptation_metrics
        )
        
        # Store reflection
        self._store_reflection(decision_id, reflection, context, outcomes)
        
        return reflection
        
    def get_decision_support(self,
                           context: Dict[str, Any],
                           proposed_principles: List[str]) -> Dict[str, Any]:
        """Get decision support based on past reflections"""
        similar_cases = self._find_similar_cases(context)
        
        if not similar_cases:
            return {
                "confidence": 0.5,
                "suggested_principles": proposed_principles,
                "cautions": ["No similar cases found for reference"]
            }
            
        # Analyze principle effectiveness in similar cases
        principle_effectiveness = self._analyze_principle_effectiveness(
            similar_cases,
            proposed_principles
        )
        
        # Generate recommendations
        # Get confidence values safely with a default
        confidence_values = []
        for case in similar_cases:
            try:
                confidence_values.append(case.get("confidence", 0.5))
            except (TypeError, AttributeError):
                confidence_values.append(0.5)
                
        recommendations = {
            "confidence": float(np.mean(confidence_values)) if confidence_values else 0.5,
            "suggested_principles": [
                p for p, score in principle_effectiveness.items()
                if score > 0.7
            ],
            "cautions": [
                f"Principle '{p}' had mixed results in similar cases"
                for p, score in principle_effectiveness.items()
                if score < 0.4
            ]
        }
        
        return recommendations
        
    def get_ethical_insights(self) -> Dict[str, Any]:
        """Get aggregated ethical insights from reflection history"""
        return self.ethical_insights
        
    def _calculate_confidence(self, outcomes: Dict[str, Any]) -> float:
        """Calculate confidence based on decision outcomes"""
        # Average of overall score and principle alignment
        principle_scores = list(outcomes["principle_scores"].values())
        return (outcomes["overall_score"] + np.mean(principle_scores)) / 2
        
    def _generate_suggestions(self,
                            principle_performance: Dict[str, float],
                            overall_score: float,
                            context: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on performance"""
        suggestions = []
        
        # Suggest improvements for low-performing principles
        for principle, score in principle_performance.items():
            if score < 0.5:
                suggestions.append(
                    f"Consider strengthening '{principle}' in similar contexts"
                )
                
        # Overall performance suggestions
        if overall_score < 0.6:
            suggestions.append(
                "Review decision-making process for better ethical alignment"
            )
            
        return suggestions
        
    def _update_adaptation_metrics(self,
                                 confidence: float,
                                 overall_score: float) -> Dict[str, float]:
        """Update adaptation and learning metrics"""
        if not self.reflection_history:
            return {
                "current_rate": 0.5,
                "uncertainty_awareness": 0.5
            }
            
        # Calculate learning rate from recent decisions
        recent_scores = [r["outcomes"]["overall_score"]
                        for r in self.reflection_history[-5:]]
        learning_rate = np.mean(np.diff(recent_scores)) if len(recent_scores) > 1 else 0
        
        # Calculate uncertainty awareness
        uncertainty = abs(confidence - overall_score)
        
        return {
            "current_rate": max(0, min(1, 0.5 + learning_rate)),
            "uncertainty_awareness": 1 - uncertainty
        }
        
    def _store_reflection(self,
                         decision_id: str,
                         reflection: ReflectionOutcome,
                         context: Dict[str, Any],
                         outcomes: Dict[str, Any]):
        """Store reflection results"""
        reflection_data = {
            "decision_id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "outcomes": outcomes,
            "reflection": {
                "lessons_learned": reflection.lessons_learned,
                "improvement_suggestions": reflection.improvement_suggestions,
                "confidence": reflection.confidence,
                "adaptation_metrics": reflection.adaptation_metrics
            }
        }
        
        self.reflection_history.append(reflection_data)
        
        # Update insights
        self._update_insights(reflection_data)
        
        # Save to disk
        self._save_history()
        
    def _find_similar_cases(self,
                          context: Dict[str, Any],
                          threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Find similar cases from history"""
        similar_cases = []
        
        for case in self.reflection_history:
            similarity = self._calculate_similarity(context, case["context"])
            if similarity > threshold:
                similar_cases.append(case)
                
        return similar_cases
        
    def _calculate_similarity(self,
                            context1: Dict[str, Any],
                            context2: Dict[str, Any]) -> float:
        """Calculate similarity between two contexts"""
        # Simple key overlap for now
        keys1 = set(context1.keys())
        keys2 = set(context2.keys())
        
        if not keys1 or not keys2:
            return 0.0
            
        return len(keys1.intersection(keys2)) / len(keys1.union(keys2))
        
    def _analyze_principle_effectiveness(self,
                                      cases: List[Dict[str, Any]],
                                      principles: List[str]) -> Dict[str, float]:
        """Analyze how effective different principles were in similar cases"""
        effectiveness = {}
        
        for principle in principles:
            scores = []
            for case in cases:
                if principle in case["outcomes"]["principle_scores"]:
                    scores.append(case["outcomes"]["principle_scores"][principle])
                    
            effectiveness[principle] = np.mean(scores) if scores else 0.5
            
        return effectiveness
        
    def _update_insights(self, reflection_data: Dict[str, Any]):
        """Update ethical insights based on new reflection"""
        # Update confidence trend
        confidences = [r["reflection"]["confidence"]
                      for r in self.reflection_history[-10:]]
        self.ethical_insights["confidence_trend"] = (
            np.mean(np.diff(confidences))
            if len(confidences) > 1 else 0.0
        )
        
        # Update principle effectiveness
        outcomes = reflection_data["outcomes"]
        for principle, score in outcomes["principle_scores"].items():
            if principle not in self.ethical_insights["principle_effectiveness"]:
                self.ethical_insights["principle_effectiveness"][principle] = []
                
            scores = self.ethical_insights["principle_effectiveness"][principle]
            scores.append(score)
            # Keep only recent scores
            self.ethical_insights["principle_effectiveness"][principle] = scores[-10:]
            
        # Update most effective principles
        avg_effectiveness = {
            p: np.mean(scores)
            for p, scores in self.ethical_insights["principle_effectiveness"].items()
        }
        self.ethical_insights["most_effective_principles"] = sorted(
            avg_effectiveness.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        # Update recent lessons
        self.ethical_insights["recent_lessons"] = reflection_data["reflection"]["lessons_learned"]
        
        # Save insights
        with open(self.insights_file, 'w') as f:
            json.dump(self.ethical_insights, f, indent=2, cls=NumpyJSONEncoder)
            
    def _load_history(self):
        """Load reflection history from disk"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.reflection_history = json.load(f)
        except json.JSONDecodeError:
            self.reflection_history = []
            
        try:
            if self.insights_file.exists():
                with open(self.insights_file, 'r') as f:
                    self.ethical_insights = json.load(f)
        except json.JSONDecodeError:
            self.ethical_insights = {
                "confidence_trend": 0.0,
                "most_effective_principles": [],
                "adaptation_metrics": {
                    "current_rate": 0.0,
                    "uncertainty_awareness": 0.0
                },
                "principle_effectiveness": {},
                "recent_lessons": []
            }
                
    def _save_history(self):
        """Save reflection history to disk"""
        with open(self.history_file, 'w') as f:
            json.dump(self.reflection_history, f, indent=2, cls=NumpyJSONEncoder)
