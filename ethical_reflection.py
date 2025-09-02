#!/usr/bin/env python3
"""
EpochCore RAS Ethical Reflection System

Manages ethical decision-making, policy compliance, and moral reasoning.
Includes recursive improvement hooks for autonomous ethical enhancement.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from recursive_improvement import ImprovementStrategy, SubsystemHook, get_framework


class EthicalPrinciple(Enum):
    """Core ethical principles for the system."""
    AUTONOMY = "autonomy"
    BENEFICENCE = "beneficence"
    NON_MALEFICENCE = "non_maleficence"
    JUSTICE = "justice"
    TRANSPARENCY = "transparency"
    ACCOUNTABILITY = "accountability"
    PRIVACY = "privacy"
    FAIRNESS = "fairness"


class DecisionLevel(Enum):
    """Levels of ethical decision complexity."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EthicalDilemma:
    """Represents an ethical dilemma requiring evaluation."""
    dilemma_id: str
    description: str
    stakeholders: List[str]
    principles_involved: List[EthicalPrinciple]
    decision_level: DecisionLevel
    context: Dict[str, Any]
    timestamp: datetime
    resolution: Optional[str] = None
    justification: Optional[str] = None
    confidence_score: float = 0.0
    

class EthicalRule:
    """Represents an ethical rule or policy."""
    
    def __init__(self, rule_id: str, name: str, principle: EthicalPrinciple,
                 condition: str, action: str, priority: int = 1):
        self.id = rule_id
        self.name = name
        self.principle = principle
        self.condition = condition
        self.action = action
        self.priority = priority
        self.created_at = datetime.now()
        self.last_applied = None
        self.application_count = 0
        self.success_rate = 1.0
        self.enabled = True
        
    def to_dict(self) -> Dict:
        """Convert rule to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "principle": self.principle.value,
            "condition": self.condition,
            "action": self.action,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "last_applied": self.last_applied.isoformat() if self.last_applied else None,
            "application_count": self.application_count,
            "success_rate": self.success_rate,
            "enabled": self.enabled
        }


class EthicalReflectionEngine:
    """Core engine for ethical reasoning and decision-making."""
    
    def __init__(self):
        self.rules = {}
        self.dilemmas = []
        self.decisions_history = []
        self.ethical_metrics = {
            "total_decisions": 0,
            "ethical_violations": 0,
            "stakeholder_satisfaction": 0.8,
            "transparency_score": 0.75,
            "accountability_score": 0.85
        }
        
        # Initialize with sample ethical rules
        self._initialize_ethical_rules()
        
    def _initialize_ethical_rules(self):
        """Initialize with sample ethical rules."""
        sample_rules = [
            EthicalRule("rule_001", "Privacy Protection", EthicalPrinciple.PRIVACY,
                       "data contains personal information", 
                       "apply anonymization and access controls", 3),
            EthicalRule("rule_002", "Transparent Decision Making", EthicalPrinciple.TRANSPARENCY,
                       "decision affects user outcomes",
                       "provide clear explanation and rationale", 2),
            EthicalRule("rule_003", "Harm Prevention", EthicalPrinciple.NON_MALEFICENCE,
                       "action could cause harm to individuals",
                       "require additional safety checks and approval", 4),
            EthicalRule("rule_004", "Fair Resource Allocation", EthicalPrinciple.JUSTICE,
                       "resource allocation decision needed",
                       "ensure equitable distribution based on need", 2),
            EthicalRule("rule_005", "User Autonomy", EthicalPrinciple.AUTONOMY,
                       "decision affects user choice or control",
                       "preserve user agency and provide opt-out mechanisms", 3),
            EthicalRule("rule_006", "Accountability Tracking", EthicalPrinciple.ACCOUNTABILITY,
                       "automated decision made",
                       "log decision rationale and enable audit trail", 2)
        ]
        
        for rule in sample_rules:
            self.rules[rule.id] = rule
            # Simulate some usage history
            rule.application_count = abs(hash(rule.id)) % 50
            rule.success_rate = 0.8 + (abs(hash(rule.id)) % 20) / 100.0
            if rule.application_count > 0:
                rule.last_applied = datetime.now() - timedelta(days=abs(hash(rule.id)) % 30)
                
    def evaluate_ethical_scenario(self, scenario: Dict) -> Dict:
        """Evaluate an ethical scenario and provide recommendations."""
        scenario_id = scenario.get("id", f"scenario_{len(self.decisions_history)}")
        
        # Identify applicable rules
        applicable_rules = []
        for rule in self.rules.values():
            if rule.enabled and self._rule_applies_to_scenario(rule, scenario):
                applicable_rules.append(rule)
                
        # Sort by priority
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        # Generate ethical assessment
        assessment = {
            "scenario_id": scenario_id,
            "ethical_concerns": self._identify_ethical_concerns(scenario),
            "applicable_rules": [r.id for r in applicable_rules],
            "recommendations": [r.action for r in applicable_rules[:3]],  # Top 3
            "risk_level": self._assess_risk_level(scenario),
            "stakeholder_impact": self._assess_stakeholder_impact(scenario),
            "confidence_score": min(1.0, len(applicable_rules) * 0.2),
            "timestamp": datetime.now().isoformat()
        }
        
        # Update metrics
        self.ethical_metrics["total_decisions"] += 1
        for rule in applicable_rules:
            rule.application_count += 1
            rule.last_applied = datetime.now()
            
        self.decisions_history.append(assessment)
        
        return assessment
        
    def _rule_applies_to_scenario(self, rule: EthicalRule, scenario: Dict) -> bool:
        """Determine if a rule applies to a given scenario."""
        # Simple keyword matching for demo purposes
        scenario_text = str(scenario).lower()
        condition_keywords = rule.condition.lower().split()
        
        return any(keyword in scenario_text for keyword in condition_keywords)
        
    def _identify_ethical_concerns(self, scenario: Dict) -> List[str]:
        """Identify potential ethical concerns in a scenario."""
        concerns = []
        scenario_text = str(scenario).lower()
        
        concern_keywords = {
            "privacy": ["personal", "data", "information", "identity"],
            "fairness": ["bias", "discrimination", "unfair", "unequal"],
            "transparency": ["hidden", "opaque", "unclear", "black box"],
            "harm": ["damage", "hurt", "negative", "harmful", "risk"],
            "autonomy": ["control", "choice", "freedom", "consent"]
        }
        
        for concern, keywords in concern_keywords.items():
            if any(keyword in scenario_text for keyword in keywords):
                concerns.append(concern)
                
        return concerns
        
    def _assess_risk_level(self, scenario: Dict) -> str:
        """Assess the ethical risk level of a scenario."""
        risk_factors = 0
        scenario_text = str(scenario).lower()
        
        high_risk_terms = ["critical", "irreversible", "widespread", "vulnerable", "children"]
        medium_risk_terms = ["significant", "important", "affects many", "long-term"]
        
        if any(term in scenario_text for term in high_risk_terms):
            risk_factors += 3
        elif any(term in scenario_text for term in medium_risk_terms):
            risk_factors += 2
        else:
            risk_factors += 1
            
        if risk_factors >= 3:
            return "high"
        elif risk_factors >= 2:
            return "medium"
        else:
            return "low"
            
    def _assess_stakeholder_impact(self, scenario: Dict) -> Dict:
        """Assess impact on different stakeholders."""
        return {
            "users": "medium",
            "organization": "low", 
            "society": "low",
            "future_generations": "low"
        }
        
    def add_ethical_rule(self, rule: EthicalRule) -> None:
        """Add a new ethical rule."""
        self.rules[rule.id] = rule
        
    def update_rule_performance(self, rule_id: str, successful: bool) -> None:
        """Update the performance metrics of a rule."""
        if rule_id in self.rules:
            rule = self.rules[rule_id]
            # Simple moving average update
            old_rate = rule.success_rate
            rule.success_rate = (old_rate * 0.9) + (0.1 if successful else 0.0)
            
    def get_system_state(self) -> Dict:
        """Get comprehensive ethical system state."""
        total_rules = len(self.rules)
        active_rules = sum(1 for r in self.rules.values() if r.enabled)
        
        # Calculate principle coverage
        principle_coverage = {}
        for principle in EthicalPrinciple:
            principle_coverage[principle.value] = sum(1 for r in self.rules.values() 
                                                    if r.principle == principle and r.enabled)
            
        # Calculate recent performance
        recent_decisions = self.decisions_history[-50:] if self.decisions_history else []
        avg_confidence = sum(d["confidence_score"] for d in recent_decisions) / len(recent_decisions) if recent_decisions else 0
        
        # Rule performance analysis
        rule_performance = {}
        for rule_id, rule in self.rules.items():
            rule_performance[rule_id] = {
                "success_rate": rule.success_rate,
                "application_count": rule.application_count,
                "last_applied": rule.last_applied.isoformat() if rule.last_applied else None,
                "priority": rule.priority
            }
            
        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "principle_coverage": principle_coverage,
            "ethical_metrics": self.ethical_metrics.copy(),
            "recent_decision_confidence": avg_confidence,
            "total_decisions": len(self.decisions_history),
            "rules": {rid: rule.to_dict() for rid, rule in self.rules.items()},
            "rule_performance": rule_performance,
            "recent_decisions": recent_decisions[-10:],  # Last 10 decisions
            "timestamp": datetime.now().isoformat()
        }


class EthicalPolicyOptimizationStrategy(ImprovementStrategy):
    """Strategy for optimizing ethical policies and rules."""
    
    def get_name(self) -> str:
        return "ethical_policy_optimization"
        
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze ethical policies and identify improvement opportunities."""
        opportunities = {
            "improvements_available": False,
            "underperforming_rules": [],
            "coverage_gaps": [],
            "policy_conflicts": [],
            "optimization_potential": 0.0
        }
        
        rules_data = subsystem_state.get("rules", {})
        principle_coverage = subsystem_state.get("principle_coverage", {})
        rule_performance = subsystem_state.get("rule_performance", {})
        
        # Identify underperforming rules
        for rule_id, performance in rule_performance.items():
            success_rate = performance.get("success_rate", 1.0)
            application_count = performance.get("application_count", 0)
            
            if success_rate < 0.8 and application_count > 5:
                opportunities["underperforming_rules"].append({
                    "rule_id": rule_id,
                    "success_rate": success_rate,
                    "application_count": application_count,
                    "improvement_needed": 0.9 - success_rate
                })
                
        # Identify coverage gaps
        for principle, count in principle_coverage.items():
            if count == 0:
                opportunities["coverage_gaps"].append({
                    "principle": principle,
                    "current_coverage": count,
                    "recommended_rules": 2
                })
            elif count == 1:
                opportunities["coverage_gaps"].append({
                    "principle": principle, 
                    "current_coverage": count,
                    "recommended_rules": 1,
                    "reason": "Single point of failure"
                })
                
        # Check for potential policy conflicts
        rule_priorities = {}
        for rule_id, rule_data in rules_data.items():
            priority = rule_data.get("priority", 1)
            principle = rule_data.get("principle", "unknown")
            
            if priority in rule_priorities:
                rule_priorities[priority].append((rule_id, principle))
            else:
                rule_priorities[priority] = [(rule_id, principle)]
                
        for priority, rules_list in rule_priorities.items():
            if len(rules_list) > 2 and priority >= 3:  # High priority conflicts
                opportunities["policy_conflicts"].append({
                    "priority_level": priority,
                    "conflicting_rules": [r[0] for r in rules_list],
                    "principles_involved": list(set(r[1] for r in rules_list))
                })
                
        if (opportunities["underperforming_rules"] or 
            opportunities["coverage_gaps"] or 
            opportunities["policy_conflicts"]):
            opportunities["improvements_available"] = True
            opportunities["optimization_potential"] = (
                len(opportunities["underperforming_rules"]) * 0.15 +
                len(opportunities["coverage_gaps"]) * 0.2 +
                len(opportunities["policy_conflicts"]) * 0.1
            )
            
        return opportunities
        
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute ethical policy improvements."""
        improved_state = subsystem_state.copy()
        improvements_made = []
        
        # Improve underperforming rules
        for underperformer in opportunities.get("underperforming_rules", []):
            rule_id = underperformer["rule_id"]
            if rule_id in improved_state["rule_performance"]:
                # Simulate rule improvement
                old_rate = improved_state["rule_performance"][rule_id]["success_rate"]
                improvement = min(0.15, underperformer["improvement_needed"])
                new_rate = min(1.0, old_rate + improvement)
                improved_state["rule_performance"][rule_id]["success_rate"] = new_rate
                
                # Also update in rules data
                if rule_id in improved_state["rules"]:
                    improved_state["rules"][rule_id]["success_rate"] = new_rate
                    
                improvements_made.append({
                    "type": "rule_optimization",
                    "rule_id": rule_id,
                    "old_success_rate": old_rate,
                    "new_success_rate": new_rate
                })
                
        # Address coverage gaps by creating virtual rules
        for gap in opportunities.get("coverage_gaps", []):
            principle = gap["principle"]
            new_rules_needed = gap.get("recommended_rules", 1)
            
            # Simulate adding new rules to coverage
            current_coverage = improved_state["principle_coverage"][principle]
            improved_state["principle_coverage"][principle] = current_coverage + new_rules_needed
            
            improvements_made.append({
                "type": "coverage_enhancement",
                "principle": principle,
                "rules_added": new_rules_needed,
                "new_coverage": improved_state["principle_coverage"][principle]
            })
            
        # Resolve policy conflicts by adjusting priorities
        for conflict in opportunities.get("policy_conflicts", []):
            conflicting_rules = conflict["conflicting_rules"]
            # Simulate priority rebalancing
            for i, rule_id in enumerate(conflicting_rules):
                if rule_id in improved_state["rules"]:
                    # Spread priorities to avoid conflicts
                    new_priority = conflict["priority_level"] + i
                    improved_state["rules"][rule_id]["priority"] = new_priority
                    
            improvements_made.append({
                "type": "conflict_resolution",
                "original_priority": conflict["priority_level"],
                "rules_affected": len(conflicting_rules),
                "resolution": "Priority levels adjusted to prevent conflicts"
            })
            
        # Update overall metrics
        if improvements_made:
            # Recalculate ethical metrics
            rule_improvements = sum(1 for imp in improvements_made if imp["type"] == "rule_optimization")
            coverage_improvements = sum(1 for imp in improvements_made if imp["type"] == "coverage_enhancement")
            
            old_metrics = improved_state["ethical_metrics"]
            improved_state["ethical_metrics"]["accountability_score"] = min(1.0, old_metrics["accountability_score"] + rule_improvements * 0.05)
            improved_state["ethical_metrics"]["transparency_score"] = min(1.0, old_metrics["transparency_score"] + coverage_improvements * 0.03)
            
        improved_state["improvements_made"] = improvements_made
        improved_state["timestamp"] = datetime.now().isoformat()
        
        return improved_state


class EthicalDecisionQualityStrategy(ImprovementStrategy):
    """Strategy for improving the quality of ethical decision-making."""
    
    def get_name(self) -> str:
        return "ethical_decision_quality"
        
    def analyze(self, subsystem_state: Dict) -> Dict:
        """Analyze decision quality and identify improvement opportunities."""
        opportunities = {
            "improvements_available": False,
            "low_confidence_decisions": [],
            "decision_pattern_issues": [],
            "stakeholder_concerns": [],
            "quality_enhancement_potential": 0.0
        }
        
        recent_decisions = subsystem_state.get("recent_decisions", [])
        ethical_metrics = subsystem_state.get("ethical_metrics", {})
        avg_confidence = subsystem_state.get("recent_decision_confidence", 0.8)
        
        # Identify low confidence decisions
        for decision in recent_decisions:
            confidence = decision.get("confidence_score", 0.0)
            if confidence < 0.6:
                opportunities["low_confidence_decisions"].append({
                    "scenario_id": decision.get("scenario_id"),
                    "confidence_score": confidence,
                    "ethical_concerns": decision.get("ethical_concerns", []),
                    "risk_level": decision.get("risk_level", "unknown")
                })
                
        # Check decision patterns
        if avg_confidence < 0.7:
            opportunities["decision_pattern_issues"].append({
                "issue": "low_overall_confidence",
                "current_confidence": avg_confidence,
                "target_confidence": 0.8,
                "improvement_needed": 0.8 - avg_confidence
            })
            
        # Check stakeholder satisfaction
        stakeholder_satisfaction = ethical_metrics.get("stakeholder_satisfaction", 0.8)
        if stakeholder_satisfaction < 0.75:
            opportunities["stakeholder_concerns"].append({
                "metric": "stakeholder_satisfaction",
                "current_score": stakeholder_satisfaction,
                "target_score": 0.85,
                "improvement_needed": 0.85 - stakeholder_satisfaction
            })
            
        if (opportunities["low_confidence_decisions"] or 
            opportunities["decision_pattern_issues"] or 
            opportunities["stakeholder_concerns"]):
            opportunities["improvements_available"] = True
            opportunities["quality_enhancement_potential"] = (
                min(len(opportunities["low_confidence_decisions"]), 5) * 0.1 +
                len(opportunities["decision_pattern_issues"]) * 0.2 +
                len(opportunities["stakeholder_concerns"]) * 0.15
            )
            
        return opportunities
        
    def improve(self, subsystem_state: Dict, opportunities: Dict) -> Dict:
        """Execute decision quality improvements."""
        improved_state = subsystem_state.copy()
        improvements_made = []
        
        # Improve decision confidence through enhanced analysis
        low_confidence_count = len(opportunities.get("low_confidence_decisions", []))
        if low_confidence_count > 0:
            # Simulate confidence improvement through better analysis methods
            current_avg = improved_state.get("recent_decision_confidence", 0.6)
            improvement = min(0.15, low_confidence_count * 0.03)
            improved_state["recent_decision_confidence"] = min(1.0, current_avg + improvement)
            
            improvements_made.append({
                "type": "confidence_enhancement",
                "old_avg_confidence": current_avg,
                "new_avg_confidence": improved_state["recent_decision_confidence"],
                "decisions_improved": low_confidence_count
            })
            
        # Address stakeholder satisfaction issues
        for concern in opportunities.get("stakeholder_concerns", []):
            if concern["metric"] == "stakeholder_satisfaction":
                old_score = improved_state["ethical_metrics"]["stakeholder_satisfaction"]
                improvement = min(0.1, concern["improvement_needed"])
                new_score = min(1.0, old_score + improvement)
                improved_state["ethical_metrics"]["stakeholder_satisfaction"] = new_score
                
                improvements_made.append({
                    "type": "stakeholder_satisfaction_improvement",
                    "old_score": old_score,
                    "new_score": new_score
                })
                
        improved_state["improvements_made"] = improvements_made
        improved_state["timestamp"] = datetime.now().isoformat()
        
        return improved_state


# Global ethical engine instance
_ethical_engine = None


def get_ethical_engine() -> EthicalReflectionEngine:
    """Get or create the global ethical reflection engine."""
    global _ethical_engine
    if _ethical_engine is None:
        _ethical_engine = EthicalReflectionEngine()
    return _ethical_engine


def initialize_ethical_reflection() -> SubsystemHook:
    """Initialize ethical reflection with recursive improvement hooks."""
    engine = get_ethical_engine()
    
    # Create improvement strategies
    strategies = [
        EthicalPolicyOptimizationStrategy(),
        EthicalDecisionQualityStrategy()
    ]
    
    # Create subsystem hook
    hook = SubsystemHook(
        name="ethics",
        get_state_func=engine.get_system_state,
        improvement_strategies=strategies
    )
    
    # Register with the framework
    framework = get_framework()
    framework.register_subsystem(hook)
    
    return hook


# Example usage functions
def improve_ethical_system() -> Dict:
    """Manual trigger for ethical system improvement."""
    framework = get_framework()
    return framework.run_manual_improvement("ethics")


def get_ethical_status() -> Dict:
    """Get current ethical system status."""
    engine = get_ethical_engine()
    return engine.get_system_state()


def evaluate_scenario(scenario: Dict) -> Dict:
    """Evaluate an ethical scenario."""
    engine = get_ethical_engine()
    return engine.evaluate_ethical_scenario(scenario)


if __name__ == "__main__":
    # Demo the ethical reflection system
    print("⚖️  EpochCore RAS Ethical Reflection Demo")
    print("=" * 50)
    
    # Initialize
    hook = initialize_ethical_reflection()
    engine = get_ethical_engine()
    
    print("\n🎯 Initial Ethical Status:")
    status = get_ethical_status()
    print(f"  Total Rules: {status['total_rules']}")
    print(f"  Active Rules: {status['active_rules']}")
    print(f"  Principle Coverage: {len([p for p in status['principle_coverage'].values() if p > 0])}/8")
    print(f"  Decision Confidence: {status['recent_decision_confidence']:.1%}")
    print(f"  Stakeholder Satisfaction: {status['ethical_metrics']['stakeholder_satisfaction']:.1%}")
    
    print("\n🤔 Evaluating Sample Ethical Scenario...")
    scenario = {
        "id": "demo_scenario",
        "description": "AI system making automated decisions about user data access",
        "involves": ["user privacy", "data processing", "automated decision"],
        "stakeholders": ["users", "organization", "regulators"]
    }
    
    evaluation = evaluate_scenario(scenario)
    print(f"  Scenario ID: {evaluation['scenario_id']}")
    print(f"  Risk Level: {evaluation['risk_level']}")
    print(f"  Ethical Concerns: {', '.join(evaluation['ethical_concerns'])}")
    print(f"  Confidence: {evaluation['confidence_score']:.1%}")
    
    print("\n🔧 Running Improvement Cycle...")
    improvement_result = improve_ethical_system()
    
    print(f"\n✅ Improvement Result: {improvement_result['status']}")
    if improvement_result['status'] == 'success':
        for improvement in improvement_result['improvements']:
            print(f"  Strategy: {improvement['strategy']}")
            if 'improvements_made' in improvement['after_state']:
                for imp in improvement['after_state']['improvements_made']:
                    print(f"    - {imp}")
    
    print("\n🎯 Final Ethical Status:")
    final_status = get_ethical_status()
    print(f"  Total Rules: {final_status['total_rules']}")
    print(f"  Active Rules: {final_status['active_rules']}")
    print(f"  Principle Coverage: {len([p for p in final_status['principle_coverage'].values() if p > 0])}/8")
    print(f"  Decision Confidence: {final_status['recent_decision_confidence']:.1%}")
    print(f"  Stakeholder Satisfaction: {final_status['ethical_metrics']['stakeholder_satisfaction']:.1%}")