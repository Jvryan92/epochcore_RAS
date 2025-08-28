"""Investment strategy component for monetary analysis and recommendations."""

from typing import Dict, Any, List
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import logging

from . import StrategyComponent
from ..core.error_handling import safe_execute


@dataclass
class InvestmentScenario:
    """Container for investment scenario calculations."""
    
    initial_amount: Decimal
    growth_rate: Decimal
    risk_level: str
    time_horizon: int
    compound_frequency: int
    description: str
    strategic_actions: List[str]
    expected_outcome: Decimal

    def calculate_compound_value(self) -> Decimal:
        """Calculate compound value over time horizon."""
        rate = self.growth_rate / self.compound_frequency
        periods = self.time_horizon * self.compound_frequency
        
        # (1 + r/n)^(nt) where:
        # r = annual rate
        # n = number of times compounded per year
        # t = time in years
        compound_factor = (1 + rate) ** periods
        
        return (self.initial_amount * compound_factor).quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP
        )


class InvestmentStrategy(StrategyComponent):
    """Strategic investment analysis and recommendations."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize investment strategy component."""
        super().__init__("investment_strategy", config)
        self.logger = logging.getLogger(__name__)

    def _generate_scenarios(self) -> List[InvestmentScenario]:
        """Generate progressive investment scenarios."""
        scenarios = []
        
        # Base parameters
        initial_amount = Decimal('10000.00')  # Starting with 10k
        base_growth = Decimal('0.15')         # 15% base growth rate
        compound_freq = 12                    # Monthly compounding
        
        # Progressive scenarios with increasing complexity and return potential
        scenarios = [
            InvestmentScenario(
                initial_amount=initial_amount,
                growth_rate=base_growth,
                risk_level="Conservative",
                time_horizon=1,
                compound_frequency=compound_freq,
                description="Index Fund Portfolio",
                strategic_actions=[
                    "Allocate 70% to broad market index funds",
                    "30% to bond index funds",
                    "Monthly rebalancing"
                ],
                expected_outcome=Decimal('0')  # Calculated later
            ),
            InvestmentScenario(
                initial_amount=initial_amount * Decimal('1.5'),
                growth_rate=base_growth * Decimal('1.2'),
                risk_level="Moderate",
                time_horizon=2,
                compound_frequency=compound_freq,
                description="Smart Beta Strategy",
                strategic_actions=[
                    "Factor-based investment approach",
                    "Quality and momentum tilts",
                    "Quarterly rebalancing"
                ],
                expected_outcome=Decimal('0')
            ),
            InvestmentScenario(
                initial_amount=initial_amount * Decimal('2.25'),
                growth_rate=base_growth * Decimal('1.4'),
                risk_level="Growth",
                time_horizon=3,
                compound_frequency=compound_freq,
                description="Sector Rotation",
                strategic_actions=[
                    "Dynamic sector allocation",
                    "Economic cycle positioning",
                    "Monthly sector review"
                ],
                expected_outcome=Decimal('0')
            ),
            InvestmentScenario(
                initial_amount=initial_amount * Decimal('3.375'),
                growth_rate=base_growth * Decimal('1.6'),
                risk_level="Aggressive Growth",
                time_horizon=4,
                compound_frequency=compound_freq,
                description="Growth Stock Focus",
                strategic_actions=[
                    "High-growth stock selection",
                    "Technology sector emphasis",
                    "Quarterly performance review"
                ],
                expected_outcome=Decimal('0')
            ),
            InvestmentScenario(
                initial_amount=initial_amount * Decimal('5.0625'),
                growth_rate=base_growth * Decimal('1.8'),
                risk_level="Opportunistic",
                time_horizon=5,
                compound_frequency=compound_freq,
                description="Market Opportunities",
                strategic_actions=[
                    "Emerging market allocation",
                    "Thematic investment focus",
                    "Bi-monthly rebalancing"
                ],
                expected_outcome=Decimal('0')
            ),
            InvestmentScenario(
                initial_amount=initial_amount * Decimal('7.59375'),
                growth_rate=base_growth * Decimal('2.0'),
                risk_level="Dynamic",
                time_horizon=6,
                compound_frequency=compound_freq,
                description="Alternative Strategy",
                strategic_actions=[
                    "Alternative investment inclusion",
                    "Real estate and commodities",
                    "Quarterly risk assessment"
                ],
                expected_outcome=Decimal('0')
            ),
            InvestmentScenario(
                initial_amount=initial_amount * Decimal('11.390625'),
                growth_rate=base_growth * Decimal('2.2'),
                risk_level="Aggressive",
                time_horizon=7,
                compound_frequency=compound_freq,
                description="High Conviction",
                strategic_actions=[
                    "Concentrated position management",
                    "High-conviction investments",
                    "Monthly risk monitoring"
                ],
                expected_outcome=Decimal('0')
            ),
            InvestmentScenario(
                initial_amount=initial_amount * Decimal('17.0859375'),
                growth_rate=base_growth * Decimal('2.4'),
                risk_level="Maximum Growth",
                time_horizon=8,
                compound_frequency=compound_freq,
                description="Accelerated Growth",
                strategic_actions=[
                    "Aggressive growth tactics",
                    "Emerging technology focus",
                    "Weekly performance tracking"
                ],
                expected_outcome=Decimal('0')
            ),
            InvestmentScenario(
                initial_amount=initial_amount * Decimal('25.62890625'),
                growth_rate=base_growth * Decimal('2.6'),
                risk_level="Speculative",
                time_horizon=9,
                compound_frequency=compound_freq,
                description="Innovation Portfolio",
                strategic_actions=[
                    "Disruptive innovation focus",
                    "Early-stage opportunities",
                    "Daily monitoring required"
                ],
                expected_outcome=Decimal('0')
            ),
            InvestmentScenario(
                initial_amount=initial_amount * Decimal('38.443359375'),
                growth_rate=base_growth * Decimal('2.8'),
                risk_level="Maximum Opportunity",
                time_horizon=10,
                compound_frequency=compound_freq,
                description="Venture Strategy",
                strategic_actions=[
                    "Pre-IPO opportunities",
                    "Strategic partnerships",
                    "Continuous opportunity scanning"
                ],
                expected_outcome=Decimal('0')
            )
        ]

        # Calculate expected outcomes
        for scenario in scenarios:
            scenario.expected_outcome = scenario.calculate_compound_value()

        return scenarios

    @safe_execute(logging.getLogger(__name__), {"status": "error"})
    def _execute(self) -> Dict[str, Any]:
        """Execute investment strategy analysis.

        Returns:
            Dictionary containing investment scenarios and recommendations
        """
        scenarios = self._generate_scenarios()
        
        return {
            "status": "success",
            "recommendations": [
                {
                    "level": i + 1,
                    "initial_investment": str(s.initial_amount),
                    "risk_level": s.risk_level,
                    "time_horizon": s.time_horizon,
                    "growth_rate": f"{float(s.growth_rate * 100):.1f}%",
                    "compound_frequency": s.compound_frequency,
                    "expected_outcome": str(s.expected_outcome),
                    "description": s.description,
                    "strategic_actions": s.strategic_actions,
                    "annual_return": f"{float(s.expected_outcome / s.initial_amount - 1) * 100:.1f}%"
                }
                for i, s in enumerate(scenarios)
            ],
            "meta": {
                "total_scenarios": len(scenarios),
                "compound_frequency": "Monthly",
                "risk_progression": "Progressive increase",
                "time_span": "1-10 years"
            }
        }
