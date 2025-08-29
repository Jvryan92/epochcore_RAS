"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""Investment strategy models for both sales and personal investment scenarios."""

from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import logging


class ModelType(Enum):
    """Type of investment model."""
    
    SALES_PITCH = "sales_pitch"
    PERSONAL_INVESTMENT = "personal_investment"


@dataclass
class ModelParameters:
    """Parameters for investment model calculations."""
    
    initial_capital: Decimal
    model_type: ModelType
    risk_tolerance: str = "Moderate"  # Conservative, Moderate, Aggressive
    monthly_contribution: Decimal = Decimal('0')
    tax_bracket: Decimal = Decimal('0.25')  # 25% default
    inflation_rate: Decimal = Decimal('0.03')  # 3% default
    emergency_fund_months: int = 6


class InvestmentModelStrategy:
    """Dual-purpose investment model for sales pitches and personal planning."""

    def __init__(self, logger=None):
        """Initialize strategy with optional logger."""
        self.logger = logger or logging.getLogger(__name__)

    def _calculate_sales_model(
        self,
        params: ModelParameters
    ) -> Dict[str, Any]:
        """Calculate optimistic sales pitch model.
        
        This model emphasizes:
        - Potential maximum returns
        - Compound growth visualization
        - Success case scenarios
        - Competitive advantage examples
        """
        base_growth = Decimal('0.15')  # 15% base growth rate
        scenarios = []
        current_capital = params.initial_capital

        for year in range(1, 11):
            # Progressive growth rates for sales pitch
            growth_rate = base_growth * (1 + Decimal('0.2') * (year - 1))
            
            # Calculate compound growth with reinvestment
            compound_value = current_capital * (
                1 + growth_rate
            ) ** year
            
            # Calculate potential client base
            potential_clients = 10 * (2 ** (year - 1))  # Geometric growth
            
            scenario = {
                "year": year,
                "initial_investment": str(current_capital),
                "projected_value": str(compound_value.quantize(
                    Decimal('0.01'),
                    rounding=ROUND_HALF_UP
                )),
                "potential_clients": potential_clients,
                "revenue_potential": str((compound_value * Decimal('0.02')).quantize(
                    Decimal('0.01'),
                    rounding=ROUND_HALF_UP
                )),
                "market_opportunity": f"Tier {min(year, 5)}",
                "competitive_advantage": [
                    "Proprietary Strategy",
                    "AI-Driven Insights",
                    "Market Adaptation",
                    "Risk Management"
                ]
            }
            scenarios.append(scenario)
            current_capital = current_capital * Decimal('1.5')

        return {
            "model_type": "Sales Pitch",
            "scenarios": scenarios,
            "pitch_points": [
                "Exponential Growth Potential",
                "Proven Track Record",
                "Innovative Technology Integration",
                "Risk-Managed Approach",
                "Scalable Business Model"
            ],
            "market_positioning": {
                "target_market": "High-Growth Segments",
                "competitive_edge": "AI-Powered Strategy",
                "value_proposition": "Accelerated Growth Path"
            }
        }

    def _calculate_personal_model(
        self,
        params: ModelParameters
    ) -> Dict[str, Any]:
        """Calculate realistic personal investment model.
        
        This model emphasizes:
        - Conservative growth estimates
        - Risk management
        - Emergency fund planning
        - Tax implications
        - Inflation adjustment
        """
        # Risk-based growth rates
        growth_rates = {
            "Conservative": Decimal('0.06'),  # 6%
            "Moderate": Decimal('0.08'),      # 8%
            "Aggressive": Decimal('0.10')     # 10%
        }
        base_growth = growth_rates[params.risk_tolerance]
        
        # Calculate emergency fund requirement
        monthly_expenses = params.initial_capital * Decimal('0.05')  # Estimated
        emergency_fund = monthly_expenses * params.emergency_fund_months
        
        # Investable amount after emergency fund
        investable_capital = max(
            params.initial_capital - emergency_fund,
            Decimal('0')
        )
        
        scenarios = []
        current_capital = investable_capital

        for year in range(1, 11):
            # Calculate real return (after inflation)
            real_growth_rate = (
                (1 + base_growth) / (1 + params.inflation_rate) - 1
            )
            
            # Calculate compound growth with monthly contributions
            compound_value = current_capital * (1 + real_growth_rate) ** year
            contribution_value = params.monthly_contribution * 12 * year
            
            # Tax implications
            taxable_gains = compound_value - current_capital - contribution_value
            tax_impact = taxable_gains * params.tax_bracket
            
            scenario = {
                "year": year,
                "initial_investment": str(current_capital),
                "monthly_contribution": str(params.monthly_contribution),
                "projected_value_pre_tax": str(compound_value.quantize(
                    Decimal('0.01'),
                    rounding=ROUND_HALF_UP
                )),
                "projected_value_post_tax": str(
                    (compound_value - tax_impact).quantize(
                        Decimal('0.01'),
                        rounding=ROUND_HALF_UP
                    )
                ),
                "emergency_fund": str(emergency_fund.quantize(
                    Decimal('0.01'),
                    rounding=ROUND_HALF_UP
                )),
                "real_return_rate": f"{float(real_growth_rate * 100):.1f}%",
                "recommended_rebalancing": "Quarterly",
                "risk_mitigation": [
                    "Diversification",
                    "Regular Rebalancing",
                    "Emergency Fund Maintenance",
                    "Tax Optimization"
                ]
            }
            scenarios.append(scenario)

        return {
            "model_type": "Personal Investment",
            "emergency_fund": str(emergency_fund),
            "scenarios": scenarios,
            "investment_strategy": {
                "risk_tolerance": params.risk_tolerance,
                "asset_allocation": self._get_allocation(params.risk_tolerance),
                "rebalancing_schedule": "Quarterly",
                "tax_strategy": "Tax-Loss Harvesting",
                "emergency_fund_months": params.emergency_fund_months
            },
            "action_items": [
                "Set up emergency fund",
                "Establish automatic monthly contributions",
                "Implement tax-efficient strategy",
                "Regular portfolio rebalancing",
                "Annual strategy review"
            ]
        }

    def _get_allocation(self, risk_tolerance: str) -> Dict[str, Decimal]:
        """Get recommended asset allocation based on risk tolerance."""
        allocations = {
            "Conservative": {
                "stocks": Decimal('0.40'),
                "bonds": Decimal('0.40'),
                "cash": Decimal('0.15'),
                "alternatives": Decimal('0.05')
            },
            "Moderate": {
                "stocks": Decimal('0.60'),
                "bonds": Decimal('0.25'),
                "cash": Decimal('0.10'),
                "alternatives": Decimal('0.05')
            },
            "Aggressive": {
                "stocks": Decimal('0.80'),
                "bonds": Decimal('0.10'),
                "cash": Decimal('0.05'),
                "alternatives": Decimal('0.05')
            }
        }
        return allocations[risk_tolerance]

    def calculate_model(
        self,
        params: ModelParameters
    ) -> Dict[str, Any]:
        """Calculate investment model based on type.
        
        Args:
            params: Model parameters including type and initial capital
            
        Returns:
            Dictionary containing model calculations and recommendations
        """
        if params.model_type == ModelType.SALES_PITCH:
            return self._calculate_sales_model(params)
        else:
            return self._calculate_personal_model(params)

    def generate_comparison(
        self,
        initial_capital: Decimal
    ) -> Dict[str, Any]:
        """Generate comparison between sales and personal models.
        
        Args:
            initial_capital: Starting investment amount
            
        Returns:
            Dictionary containing both models and key differences
        """
        sales_params = ModelParameters(
            initial_capital=initial_capital,
            model_type=ModelType.SALES_PITCH
        )
        
        personal_params = ModelParameters(
            initial_capital=initial_capital,
            model_type=ModelType.PERSONAL_INVESTMENT,
            risk_tolerance="Moderate"
        )

        sales_model = self._calculate_sales_model(sales_params)
        personal_model = self._calculate_personal_model(personal_params)

        return {
            "sales_model": sales_model,
            "personal_model": personal_model,
            "key_differences": {
                "growth_assumptions": "Sales model uses optimistic growth rates",
                "risk_consideration": "Personal model includes risk management",
                "tax_treatment": "Personal model accounts for tax implications",
                "emergency_planning": "Personal model includes emergency fund",
                "realistic_factors": "Personal model accounts for inflation"
            },
            "recommendation": "Use sales model for business pitches, "
                            "personal model for actual investment planning"
        }
