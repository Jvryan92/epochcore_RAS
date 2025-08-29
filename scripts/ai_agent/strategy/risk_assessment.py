"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""Risk tolerance assessment tools."""

from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging


class RiskFactor(Enum):
    """Risk assessment factors."""
    
    TIME_HORIZON = "time_horizon"
    INCOME_STABILITY = "income_stability"
    INVESTMENT_KNOWLEDGE = "investment_knowledge"
    LOSS_TOLERANCE = "loss_tolerance"
    INVESTMENT_GOALS = "investment_goals"


@dataclass
class RiskAssessmentQuestion:
    """Structure for risk assessment questions."""
    
    question: str
    factor: RiskFactor
    weight: float
    options: List[Dict[str, Any]]


class RiskAssessmentTool:
    """Tool for assessing investor risk tolerance."""

    def __init__(self, logger=None):
        """Initialize assessment tool."""
        self.logger = logger or logging.getLogger(__name__)
        self._initialize_questions()

    def _initialize_questions(self):
        """Initialize assessment questions."""
        self.questions = [
            RiskAssessmentQuestion(
                question="When do you expect to begin withdrawing money from your investment account?",
                factor=RiskFactor.TIME_HORIZON,
                weight=0.25,
                options=[
                    {"text": "Less than 3 years", "score": 1},
                    {"text": "3-5 years", "score": 2},
                    {"text": "6-10 years", "score": 3},
                    {"text": "11-20 years", "score": 4},
                    {"text": "More than 20 years", "score": 5}
                ]
            ),
            RiskAssessmentQuestion(
                question="How stable is your current and future income from sources such as salary, pension, etc.?",
                factor=RiskFactor.INCOME_STABILITY,
                weight=0.2,
                options=[
                    {"text": "Very unstable", "score": 1},
                    {"text": "Somewhat unstable", "score": 2},
                    {"text": "Moderately stable", "score": 3},
                    {"text": "Stable", "score": 4},
                    {"text": "Very stable", "score": 5}
                ]
            ),
            RiskAssessmentQuestion(
                question="How would you rate your level of investment knowledge?",
                factor=RiskFactor.INVESTMENT_KNOWLEDGE,
                weight=0.15,
                options=[
                    {"text": "None", "score": 1},
                    {"text": "Limited", "score": 2},
                    {"text": "Good", "score": 3},
                    {"text": "Extensive", "score": 4},
                    {"text": "Professional", "score": 5}
                ]
            ),
            RiskAssessmentQuestion(
                question="If your portfolio lost 20% of its value in a short period, what would you do?",
                factor=RiskFactor.LOSS_TOLERANCE,
                weight=0.25,
                options=[
                    {"text": "Sell all investments", "score": 1},
                    {"text": "Sell some investments", "score": 2},
                    {"text": "Hold and wait", "score": 3},
                    {"text": "Buy more opportunistically", "score": 4},
                    {"text": "Buy much more aggressively", "score": 5}
                ]
            ),
            RiskAssessmentQuestion(
                question="What is your primary investment goal?",
                factor=RiskFactor.INVESTMENT_GOALS,
                weight=0.15,
                options=[
                    {"text": "Preserve capital", "score": 1},
                    {"text": "Generate income", "score": 2},
                    {"text": "Balanced growth and income", "score": 3},
                    {"text": "Growth", "score": 4},
                    {"text": "Aggressive growth", "score": 5}
                ]
            )
        ]

    def assess_risk_tolerance(
        self,
        responses: Dict[int, int]
    ) -> Dict[str, Any]:
        """Assess risk tolerance based on questionnaire responses.
        
        Args:
            responses: Dictionary mapping question index to response index
            
        Returns:
            Dictionary containing risk assessment results
        """
        if not all(0 <= q < len(self.questions) for q in responses.keys()):
            raise ValueError("Invalid question index in responses")
            
        total_score = 0
        max_score = 0
        factor_scores = {factor: 0 for factor in RiskFactor}
        
        for q_idx, r_idx in responses.items():
            question = self.questions[q_idx]
            if not 0 <= r_idx < len(question.options):
                raise ValueError(
                    f"Invalid response index {r_idx} for question {q_idx}"
                )
                
            score = question.options[r_idx]["score"]
            weighted_score = score * question.weight
            total_score += weighted_score
            max_score += 5 * question.weight  # 5 is max score per question
            
            factor_scores[question.factor] = weighted_score

        # Calculate percentage score
        risk_score = (total_score / max_score) * 100

        # Determine risk tolerance level
        risk_level = self._determine_risk_level(risk_score)
        
        # Generate specific recommendations
        recommendations = self._generate_recommendations(
            risk_level,
            factor_scores
        )
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "factor_analysis": {
                factor.value: score 
                for factor, score in factor_scores.items()
            },
            "recommendations": recommendations,
            "suggested_allocation": self._get_suggested_allocation(risk_level)
        }

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk tolerance level from score."""
        if risk_score < 20:
            return "Very Conservative"
        elif risk_score < 40:
            return "Conservative"
        elif risk_score < 60:
            return "Moderate"
        elif risk_score < 80:
            return "Growth"
        else:
            return "Aggressive"

    def _get_suggested_allocation(self, risk_level: str) -> Dict[str, float]:
        """Get suggested asset allocation based on risk level."""
        allocations = {
            "Very Conservative": {
                "stocks": 0.20,
                "bonds": 0.60,
                "cash": 0.15,
                "alternatives": 0.05
            },
            "Conservative": {
                "stocks": 0.40,
                "bonds": 0.40,
                "cash": 0.15,
                "alternatives": 0.05
            },
            "Moderate": {
                "stocks": 0.60,
                "bonds": 0.25,
                "cash": 0.10,
                "alternatives": 0.05
            },
            "Growth": {
                "stocks": 0.75,
                "bonds": 0.15,
                "cash": 0.05,
                "alternatives": 0.05
            },
            "Aggressive": {
                "stocks": 0.85,
                "bonds": 0.05,
                "cash": 0.05,
                "alternatives": 0.05
            }
        }
        return allocations[risk_level]

    def _generate_recommendations(
        self,
        risk_level: str,
        factor_scores: Dict[RiskFactor, float]
    ) -> List[str]:
        """Generate personalized recommendations based on assessment."""
        recommendations = []
        
        # Time horizon recommendations
        time_score = factor_scores[RiskFactor.TIME_HORIZON]
        if time_score < 0.5:
            recommendations.append(
                "Consider more conservative investments due to shorter time horizon"
            )
        elif time_score > 0.8:
            recommendations.append(
                "Your long time horizon allows for more aggressive growth strategies"
            )
            
        # Income stability recommendations
        income_score = factor_scores[RiskFactor.INCOME_STABILITY]
        if income_score < 0.5:
            recommendations.append(
                "Maintain larger emergency fund due to income variability"
            )
            recommendations.append(
                "Consider more liquid investments"
            )
            
        # Investment knowledge recommendations
        knowledge_score = factor_scores[RiskFactor.INVESTMENT_KNOWLEDGE]
        if knowledge_score < 0.6:
            recommendations.append(
                "Consider educational resources to improve investment knowledge"
            )
            recommendations.append(
                "Start with simpler investment vehicles like index funds"
            )
            
        # Loss tolerance recommendations
        loss_score = factor_scores[RiskFactor.LOSS_TOLERANCE]
        if loss_score < 0.5:
            recommendations.append(
                "Consider portfolio insurance strategies"
            )
            recommendations.append(
                "Focus on lower volatility investments"
            )
            
        # Goal-based recommendations
        goal_score = factor_scores[RiskFactor.INVESTMENT_GOALS]
        if goal_score > 0.8:
            recommendations.append(
                "Consider growth-oriented strategies aligned with aggressive goals"
            )
        elif goal_score < 0.3:
            recommendations.append(
                "Focus on capital preservation and income generation"
            )
            
        return recommendations

    def get_questionnaire(self) -> List[Dict[str, Any]]:
        """Get full questionnaire structure.
        
        Returns:
            List of questions with options
        """
        return [
            {
                "index": i,
                "question": q.question,
                "factor": q.factor.value,
                "options": [
                    {
                        "index": j,
                        "text": opt["text"]
                    }
                    for j, opt in enumerate(q.options)
                ]
            }
            for i, q in enumerate(self.questions)
        ]
