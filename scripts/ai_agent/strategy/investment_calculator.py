"""Flexible investment calculator for different starting capitals."""

from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
import logging

@dataclass
class CalculationParameters:
    """Parameters for investment calculations."""
    
    initial_capital: Decimal
    base_growth_rate: Decimal = Decimal('0.15')  # 15% default
    capital_multiplier: Decimal = Decimal('1.5')  # 50% increase default
    growth_rate_increment: Decimal = Decimal('0.2')  # 20% increase default
    compound_frequency: int = 12  # Monthly default
    min_time_horizon: int = 1  # Start with 1 year
    max_time_horizon: int = 10  # Up to 10 years

class InvestmentCalculator:
    """Flexible calculator for investment scenarios."""

    def __init__(self, logger=None):
        """Initialize calculator with optional logger."""
        self.logger = logger or logging.getLogger(__name__)

    def calculate_scenarios(self, params: CalculationParameters) -> List[Dict[str, Any]]:
        """Calculate investment scenarios based on given parameters.
        
        Args:
            params: Calculation parameters including initial capital
            
        Returns:
            List of investment scenarios with calculations
        """
        scenarios = []
        current_capital = params.initial_capital
        current_growth_rate = params.base_growth_rate

        for year in range(params.min_time_horizon, params.max_time_horizon + 1):
            # Calculate compound growth
            rate = current_growth_rate / params.compound_frequency
            periods = year * params.compound_frequency
            
            compound_factor = (1 + rate) ** periods
            expected_outcome = (current_capital * compound_factor).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
            )

            # Risk level based on growth rate increase
            risk_levels = [
                "Conservative", "Moderate", "Growth", "Aggressive Growth",
                "Opportunistic", "Dynamic", "Aggressive", "Maximum Growth",
                "Speculative", "Maximum Opportunity"
            ]
            risk_index = min(year - 1, len(risk_levels) - 1)

            # Calculate annual return
            annual_return = (
                (expected_outcome / current_capital) ** (Decimal('1') / year) - 1
            ) * 100

            scenario = {
                "level": year,
                "initial_investment": str(current_capital),
                "risk_level": risk_levels[risk_index],
                "time_horizon": year,
                "growth_rate": f"{float(current_growth_rate * 100):.1f}%",
                "compound_frequency": params.compound_frequency,
                "expected_outcome": str(expected_outcome),
                "annual_return": f"{float(annual_return):.1f}%",
                "monthly_contribution_suggested": str(
                    (current_capital * Decimal('0.05')).quantize(
                        Decimal('0.01'),
                        rounding=ROUND_HALF_UP
                    )
                )
            }
            
            scenarios.append(scenario)

            # Increase capital and growth rate for next level
            current_capital = current_capital * params.capital_multiplier
            current_growth_rate = current_growth_rate * (
                1 + params.growth_rate_increment
            )

        return scenarios

    def calculate_single_scenario(
        self,
        initial_capital: Decimal,
        growth_rate: Decimal,
        time_horizon: int,
        compound_frequency: int = 12
    ) -> Dict[str, Any]:
        """Calculate a single investment scenario.
        
        Args:
            initial_capital: Starting investment amount
            growth_rate: Annual growth rate as decimal
            time_horizon: Investment period in years
            compound_frequency: Number of times compounded per year
            
        Returns:
            Dictionary with scenario calculations
        """
        rate = growth_rate / compound_frequency
        periods = time_horizon * compound_frequency
        
        compound_factor = (1 + rate) ** periods
        expected_outcome = (initial_capital * compound_factor).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )

        annual_return = (
            (expected_outcome / initial_capital) ** (
                Decimal('1') / time_horizon
            ) - 1
        ) * 100

        return {
            "initial_investment": str(initial_capital),
            "growth_rate": f"{float(growth_rate * 100):.1f}%",
            "time_horizon": time_horizon,
            "compound_frequency": compound_frequency,
            "expected_outcome": str(expected_outcome),
            "annual_return": f"{float(annual_return):.1f}%",
            "monthly_contribution_suggested": str(
                (initial_capital * Decimal('0.05')).quantize(
                    Decimal('0.01'),
                    rounding=ROUND_HALF_UP
                )
            )
        }

    def calculate_required_growth_rate(
        self,
        initial_capital: Decimal,
        target_amount: Decimal,
        time_horizon: int,
        compound_frequency: int = 12
    ) -> Decimal:
        """Calculate required growth rate to reach target amount.
        
        Args:
            initial_capital: Starting investment amount
            target_amount: Desired final amount
            time_horizon: Investment period in years
            compound_frequency: Number of times compounded per year
            
        Returns:
            Required annual growth rate as decimal
        """
        periods = time_horizon * compound_frequency
        
        # Using the compound interest formula backwards:
        # target = initial * (1 + r/n)^(nt)
        # Solve for r:
        # r = n * ((target/initial)^(1/nt) - 1)
        
        growth_factor = (target_amount / initial_capital) ** (
            Decimal('1') / (periods)
        )
        required_rate = (growth_factor - 1) * compound_frequency

        return required_rate.quantize(
            Decimal('0.0001'),
            rounding=ROUND_HALF_UP
        )
