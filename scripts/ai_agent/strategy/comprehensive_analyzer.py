"""Comprehensive investment analysis and planning tools."""

from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
import numpy as np
from scipy import stats
import pandas as pd
from enum import Enum
import logging


class RiskTolerance(Enum):
    """Risk tolerance levels with associated parameters."""
    
    VERY_CONSERVATIVE = {
        "return_rate": Decimal('0.04'),
        "volatility": Decimal('0.05'),
        "max_drawdown": Decimal('0.10'),
        "stocks": Decimal('0.30'),
        "bonds": Decimal('0.50'),
        "cash": Decimal('0.15'),
        "alternatives": Decimal('0.05')
    }
    
    CONSERVATIVE = {
        "return_rate": Decimal('0.06'),
        "volatility": Decimal('0.08'),
        "max_drawdown": Decimal('0.15'),
        "stocks": Decimal('0.40'),
        "bonds": Decimal('0.40'),
        "cash": Decimal('0.15'),
        "alternatives": Decimal('0.05')
    }
    
    MODERATE = {
        "return_rate": Decimal('0.08'),
        "volatility": Decimal('0.12'),
        "max_drawdown": Decimal('0.25'),
        "stocks": Decimal('0.60'),
        "bonds": Decimal('0.25'),
        "cash": Decimal('0.10'),
        "alternatives": Decimal('0.05')
    }
    
    GROWTH = {
        "return_rate": Decimal('0.10'),
        "volatility": Decimal('0.15'),
        "max_drawdown": Decimal('0.35'),
        "stocks": Decimal('0.70'),
        "bonds": Decimal('0.20'),
        "cash": Decimal('0.05'),
        "alternatives": Decimal('0.05')
    }
    
    AGGRESSIVE = {
        "return_rate": Decimal('0.12'),
        "volatility": Decimal('0.18'),
        "max_drawdown": Decimal('0.45'),
        "stocks": Decimal('0.80'),
        "bonds": Decimal('0.10'),
        "cash": Decimal('0.05'),
        "alternatives": Decimal('0.05')
    }


@dataclass
class RetirementGoals:
    """Retirement planning parameters."""
    
    target_retirement_age: int
    current_age: int
    life_expectancy: int = 90
    desired_retirement_income: Decimal
    social_security_estimate: Decimal
    pension_estimate: Decimal = Decimal('0')
    inflation_rate: Decimal = Decimal('0.025')
    healthcare_inflation: Decimal = Decimal('0.05')


@dataclass
class TaxParameters:
    """Tax optimization parameters."""
    
    current_tax_bracket: Decimal
    expected_retirement_tax_bracket: Decimal
    state_tax_rate: Decimal
    capital_gains_rate: Decimal
    has_401k: bool = False
    has_roth_ira: bool = False
    has_hsa: bool = False
    annual_401k_contribution: Decimal = Decimal('0')
    annual_ira_contribution: Decimal = Decimal('0')
    annual_hsa_contribution: Decimal = Decimal('0')


class ComprehensiveInvestmentAnalyzer:
    """Advanced investment analysis and planning tool."""

    def __init__(self, logger=None):
        """Initialize analyzer with optional logger."""
        self.logger = logger or logging.getLogger(__name__)

    def generate_detailed_comparison(
        self,
        initial_capital: Decimal,
        monthly_contribution: Decimal,
        time_horizon: int = 30
    ) -> Dict[str, Any]:
        """Generate detailed comparison of different investment approaches.
        
        Args:
            initial_capital: Starting investment amount
            monthly_contribution: Monthly investment addition
            time_horizon: Investment timeline in years
            
        Returns:
            Dictionary containing detailed comparison analysis
        """
        models = {}
        
        # Calculate for each risk tolerance level
        for risk_level in RiskTolerance:
            params = risk_level.value
            
            # Monte Carlo simulation
            scenarios = self._run_monte_carlo(
                initial_capital=initial_capital,
                monthly_contribution=monthly_contribution,
                return_rate=params["return_rate"],
                volatility=params["volatility"],
                time_horizon=time_horizon,
                simulations=1000
            )
            
            models[risk_level.name] = {
                "allocation": {
                    k: float(v) 
                    for k, v in params.items() 
                    if k in ['stocks', 'bonds', 'cash', 'alternatives']
                },
                "metrics": {
                    "expected_return": float(params["return_rate"]),
                    "volatility": float(params["volatility"]),
                    "max_drawdown": float(params["max_drawdown"]),
                    "sharpe_ratio": self._calculate_sharpe_ratio(
                        params["return_rate"],
                        params["volatility"]
                    )
                },
                "simulation_results": {
                    "median_outcome": float(np.median(scenarios)),
                    "worst_case": float(np.percentile(scenarios, 5)),
                    "best_case": float(np.percentile(scenarios, 95)),
                    "success_rate": float(
                        np.mean(scenarios > float(initial_capital))
                    )
                }
            }

        return {
            "models": models,
            "comparison_metrics": {
                "risk_adjusted_returns": {
                    level.name: self._calculate_risk_adjusted_return(
                        level.value["return_rate"],
                        level.value["volatility"]
                    )
                    for level in RiskTolerance
                },
                "probability_of_loss": {
                    level.name: self._calculate_probability_of_loss(
                        level.value["return_rate"],
                        level.value["volatility"]
                    )
                    for level in RiskTolerance
                }
            },
            "recommendations": self._generate_recommendations(
                initial_capital,
                monthly_contribution,
                time_horizon
            )
        }

    def create_personal_plan(
        self,
        initial_capital: Decimal,
        monthly_contribution: Decimal,
        risk_tolerance: RiskTolerance,
        retirement_goals: RetirementGoals,
        tax_params: TaxParameters
    ) -> Dict[str, Any]:
        """Create comprehensive personal investment plan.
        
        Args:
            initial_capital: Starting investment amount
            monthly_contribution: Monthly investment addition
            risk_tolerance: Risk tolerance level
            retirement_goals: Retirement planning parameters
            tax_params: Tax optimization parameters
            
        Returns:
            Dictionary containing personal investment plan
        """
        # Calculate retirement needs
        retirement_analysis = self._analyze_retirement_needs(
            retirement_goals,
            initial_capital,
            monthly_contribution,
            risk_tolerance
        )
        
        # Optimize tax strategy
        tax_strategy = self._optimize_tax_strategy(
            tax_params,
            retirement_analysis["required_savings"]
        )
        
        # Create investment timeline
        timeline = self._create_investment_timeline(
            initial_capital,
            monthly_contribution,
            risk_tolerance,
            retirement_goals.target_retirement_age - retirement_goals.current_age
        )
        
        return {
            "retirement_analysis": retirement_analysis,
            "tax_strategy": tax_strategy,
            "investment_timeline": timeline,
            "action_items": self._generate_action_items(
                retirement_analysis,
                tax_strategy,
                timeline
            ),
            "monitoring_plan": self._create_monitoring_plan(risk_tolerance)
        }

    def _analyze_retirement_needs(
        self,
        goals: RetirementGoals,
        initial_capital: Decimal,
        monthly_contribution: Decimal,
        risk_tolerance: RiskTolerance
    ) -> Dict[str, Any]:
        """Analyze retirement needs and funding requirements."""
        # Calculate years until and in retirement
        years_to_retirement = goals.target_retirement_age - goals.current_age
        retirement_years = goals.life_expectancy - goals.target_retirement_age
        
        # Calculate inflation-adjusted retirement income need
        inflation_factor = (1 + goals.inflation_rate) ** years_to_retirement
        adjusted_income_need = goals.desired_retirement_income * inflation_factor
        
        # Calculate total retirement fund needed
        # Using 4% withdrawal rate as baseline
        total_fund_needed = adjusted_income_need * Decimal('25')
        
        # Calculate required savings rate
        params = risk_tolerance.value
        required_monthly_savings = self._calculate_required_savings(
            total_fund_needed,
            initial_capital,
            monthly_contribution,
            params["return_rate"],
            years_to_retirement
        )
        
        return {
            "total_fund_needed": total_fund_needed,
            "required_monthly_savings": required_monthly_savings,
            "current_gap": required_monthly_savings - monthly_contribution,
            "retirement_income_sources": {
                "social_security": float(goals.social_security_estimate),
                "pension": float(goals.pension_estimate),
                "investment_income": float(
                    adjusted_income_need - 
                    goals.social_security_estimate - 
                    goals.pension_estimate
                )
            }
        }

    def optimize_tax_strategy(
        self,
        params: TaxParameters,
        target_savings: Decimal
    ) -> Dict[str, Any]:
        """Optimize investment accounts for tax efficiency."""
        tax_optimal_allocation = {}
        remaining_savings = target_savings
        
        # 1. Maximize HSA if available (triple tax advantage)
        if params.has_hsa:
            hsa_limit = Decimal('3850')  # 2024 limit for individual
            hsa_allocation = min(remaining_savings, hsa_limit)
            tax_optimal_allocation["HSA"] = hsa_allocation
            remaining_savings -= hsa_allocation
        
        # 2. Maximize 401(k) up to employer match
        if params.has_401k:
            match_limit = Decimal('20500')  # 2024 limit
            k401_allocation = min(remaining_savings, match_limit)
            tax_optimal_allocation["401k"] = k401_allocation
            remaining_savings -= k401_allocation
        
        # 3. Maximize Roth IRA if eligible
        if params.has_roth_ira:
            roth_limit = Decimal('6500')  # 2024 limit
            roth_allocation = min(remaining_savings, roth_limit)
            tax_optimal_allocation["Roth_IRA"] = roth_allocation
            remaining_savings -= roth_allocation
        
        # 4. Additional 401(k) contributions
        if params.has_401k and remaining_savings > 0:
            additional_401k = min(
                remaining_savings,
                Decimal('20500') - tax_optimal_allocation.get("401k", 0)
            )
            tax_optimal_allocation["Additional_401k"] = additional_401k
            remaining_savings -= additional_401k
        
        # 5. Taxable accounts
        if remaining_savings > 0:
            tax_optimal_allocation["Taxable_Account"] = remaining_savings
        
        return {
            "optimal_allocation": tax_optimal_allocation,
            "tax_savings": self._calculate_tax_savings(
                tax_optimal_allocation,
                params
            ),
            "recommendations": [
                "Maximize HSA contributions for triple tax advantage",
                "Capture full employer 401(k) match",
                "Utilize Roth IRA for tax-free growth",
                "Consider tax-loss harvesting in taxable accounts",
                "Review tax brackets annually for Roth conversion opportunities"
            ]
        }

    def _run_monte_carlo(
        self,
        initial_capital: Decimal,
        monthly_contribution: Decimal,
        return_rate: Decimal,
        volatility: Decimal,
        time_horizon: int,
        simulations: int = 1000
    ) -> np.ndarray:
        """Run Monte Carlo simulation for investment outcomes."""
        annual_contribution = float(monthly_contribution * 12)
        results = np.zeros(simulations)
        
        for i in range(simulations):
            balance = float(initial_capital)
            for _ in range(time_horizon):
                # Generate random return from normal distribution
                annual_return = np.random.normal(
                    float(return_rate),
                    float(volatility)
                )
                # Apply return and add contribution
                balance = balance * (1 + annual_return) + annual_contribution
            results[i] = balance
            
        return results

    def _calculate_sharpe_ratio(
        self,
        return_rate: Decimal,
        volatility: Decimal,
        risk_free_rate: Decimal = Decimal('0.03')
    ) -> float:
        """Calculate Sharpe ratio."""
        return float((return_rate - risk_free_rate) / volatility)

    def _calculate_risk_adjusted_return(
        self,
        return_rate: Decimal,
        volatility: Decimal
    ) -> float:
        """Calculate risk-adjusted return."""
        return float(return_rate / volatility)

    def _calculate_probability_of_loss(
        self,
        return_rate: Decimal,
        volatility: Decimal
    ) -> float:
        """Calculate probability of negative returns."""
        z_score = float(-return_rate / volatility)
        return float(stats.norm.cdf(z_score))

    def _generate_recommendations(
        self,
        initial_capital: Decimal,
        monthly_contribution: Decimal,
        time_horizon: int
    ) -> List[str]:
        """Generate personalized investment recommendations."""
        annual_contribution = monthly_contribution * 12
        total_contribution = initial_capital + (annual_contribution * time_horizon)
        
        recommendations = []
        
        if total_contribution < Decimal('100000'):
            recommendations.extend([
                "Focus on building emergency fund first",
                "Consider low-cost index funds",
                "Maximize tax-advantaged accounts"
            ])
        elif total_contribution < Decimal('500000'):
            recommendations.extend([
                "Consider diversified ETF portfolio",
                "Implement tax-loss harvesting",
                "Review asset location strategy"
            ])
        else:
            recommendations.extend([
                "Consider individual stock positions",
                "Explore alternative investments",
                "Implement advanced tax strategies"
            ])
            
        return recommendations

    def _calculate_required_savings(
        self,
        target_amount: Decimal,
        initial_capital: Decimal,
        current_monthly_savings: Decimal,
        return_rate: Decimal,
        years: int
    ) -> Decimal:
        """Calculate required monthly savings to reach target."""
        # Future value needed
        fv = target_amount
        
        # Future value of initial capital
        fv_initial = initial_capital * (1 + return_rate) ** years
        
        # Additional savings needed
        additional_needed = fv - fv_initial
        
        # Calculate required monthly savings using PMT formula
        monthly_rate = return_rate / 12
        months = years * 12
        
        # PMT = FV * r / ((1 + r)^n - 1)
        pmt = additional_needed * monthly_rate / (
            (1 + monthly_rate) ** months - 1
        )
        
        return pmt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _create_monitoring_plan(
        self,
        risk_tolerance: RiskTolerance
    ) -> Dict[str, Any]:
        """Create investment monitoring plan."""
        return {
            "rebalancing_schedule": "Quarterly",
            "review_points": [
                "Asset allocation vs target",
                "Risk metrics within tolerance",
                "Tax efficiency metrics",
                "Performance vs benchmarks"
            ],
            "alert_triggers": {
                "max_drawdown": float(risk_tolerance.value["max_drawdown"]),
                "volatility_threshold": float(
                    risk_tolerance.value["volatility"] * Decimal('1.2')
                ),
                "tracking_error_limit": 0.05
            }
        }

    def _generate_action_items(
        self,
        retirement_analysis: Dict[str, Any],
        tax_strategy: Dict[str, Any],
        timeline: Dict[str, Any]
    ) -> List[str]:
        """Generate specific action items based on analysis."""
        actions = []
        
        # Add retirement-based actions
        if retirement_analysis["current_gap"] > 0:
            actions.append(
                f"Increase monthly savings by "
                f"${float(retirement_analysis['current_gap']):.2f}"
            )
            
        # Add tax strategy actions
        for account, amount in tax_strategy["optimal_allocation"].items():
            actions.append(
                f"Contribute ${float(amount):.2f} to {account}"
            )
            
        # Add timeline-based actions
        if "rebalancing_needed" in timeline:
            actions.append("Rebalance portfolio to target allocation")
            
        return actions

    def _create_investment_timeline(
        self,
        initial_capital: Decimal,
        monthly_contribution: Decimal,
        risk_tolerance: RiskTolerance,
        years: int
    ) -> Dict[str, Any]:
        """Create detailed investment timeline."""
        params = risk_tolerance.value
        
        # Run Monte Carlo simulation
        scenarios = self._run_monte_carlo(
            initial_capital=initial_capital,
            monthly_contribution=monthly_contribution,
            return_rate=params["return_rate"],
            volatility=params["volatility"],
            time_horizon=years
        )
        
        milestones = []
        median_outcome = float(np.median(scenarios))
        
        # Create milestone checkpoints
        checkpoint_years = [1, 2, 5, 10, 15, 20, 25, 30]
        for year in checkpoint_years:
            if year <= years:
                milestone_scenarios = self._run_monte_carlo(
                    initial_capital=initial_capital,
                    monthly_contribution=monthly_contribution,
                    return_rate=params["return_rate"],
                    volatility=params["volatility"],
                    time_horizon=year
                )
                
                milestones.append({
                    "year": year,
                    "median_value": float(np.median(milestone_scenarios)),
                    "worst_case": float(np.percentile(milestone_scenarios, 5)),
                    "best_case": float(np.percentile(milestone_scenarios, 95))
                })
        
        return {
            "final_median_outcome": median_outcome,
            "milestones": milestones,
            "rebalancing_schedule": "Quarterly",
            "review_points": checkpoint_years
        }
