"""
PROTECTED FILE - EPOCHCORE MESHCREDIT TOKENOMICS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import json
from decimal import Decimal
from typing import Dict


class MeshTokenomics:
    def __init__(self):
        # Token Supply Configuration
        self.total_supply = Decimal('1000000000')  # 1 billion MESH
        self.initial_price = Decimal('0.10')       # $0.10 USD per MESH

        # Distribution Schedule (5 years)
        self.distribution_schedule = {
            'year_1': {
                'gameplay_rewards': Decimal('80000000'),   # 80M MESH
                'staking_rewards': Decimal('40000000'),    # 40M MESH
                'development': Decimal('30000000'),        # 30M MESH
                'ecosystem_growth': Decimal('30000000'),   # 30M MESH
                'team': Decimal('20000000')               # 20M MESH
            },
            'year_2': {
                'gameplay_rewards': Decimal('60000000'),   # 60M MESH
                'staking_rewards': Decimal('30000000'),    # 30M MESH
                'development': Decimal('22500000'),        # 22.5M MESH
                'ecosystem_growth': Decimal('22500000'),   # 22.5M MESH
                'team': Decimal('15000000')               # 15M MESH
            },
            'year_3': {
                'gameplay_rewards': Decimal('40000000'),   # 40M MESH
                'staking_rewards': Decimal('20000000'),    # 20M MESH
                'development': Decimal('15000000'),        # 15M MESH
                'ecosystem_growth': Decimal('15000000'),   # 15M MESH
                'team': Decimal('10000000')               # 10M MESH
            },
            'year_4': {
                'gameplay_rewards': Decimal('20000000'),   # 20M MESH
                'staking_rewards': Decimal('10000000'),    # 10M MESH
                'development': Decimal('7500000'),         # 7.5M MESH
                'ecosystem_growth': Decimal('7500000'),    # 7.5M MESH
                'team': Decimal('5000000')                # 5M MESH
            },
            'year_5': {
                'gameplay_rewards': Decimal('10000000'),   # 10M MESH
                'staking_rewards': Decimal('5000000'),     # 5M MESH
                'development': Decimal('3750000'),         # 3.75M MESH
                'ecosystem_growth': Decimal('3750000'),    # 3.75M MESH
                'team': Decimal('2500000')                # 2.5M MESH
            }
        }

        # Yield Mechanisms
        self.yield_config = {
            'staking': {
                'min_stake': Decimal('1000'),        # 1000 MESH minimum stake
                'lock_period': 30,                   # 30 days minimum
                'base_apy': Decimal('0.12'),         # 12% base APY
                'bonus_multiplier': Decimal('1.5')   # 1.5x for longer locks
            },
            'gameplay': {
                'daily_cap': Decimal('1000'),        # Max 1000 MESH per day
                'activity_multipliers': {
                    'boss_defeat': Decimal('2.0'),
                    'tournament_win': Decimal('3.0'),
                    'quest_completion': Decimal('1.5')
                }
            },
            'governance': {
                'voting_weight': Decimal('1.2'),     # 20% bonus for voters
                'proposal_stake': Decimal('10000'),  # 10k MESH to propose
                'vote_minimum': Decimal('100')       # 100 MESH to vote
            }
        }

        # Utility Features
        self.utility_features = {
            'marketplace': {
                'listing_fee': Decimal('0.01'),      # 1% listing fee
                'transaction_fee': Decimal('0.02'),   # 2% transaction fee
                'creator_royalty': Decimal('0.07')    # 7% to content creator
            },
            'premium_features': {
                'character_customization': Decimal('100'),
                'private_servers': Decimal('500'),
                'tournament_entry': Decimal('250')
            }
        }

        # Burn Mechanisms
        self.burn_mechanisms = {
            'marketplace_fees': Decimal('0.5'),      # 50% of fees burned
            'premium_features': Decimal('0.3'),      # 30% of premium payments
            'governance_slashing': Decimal('1.0')    # 100% of slashed tokens
        }

        # Economic Controls
        self.economic_controls = {
            'max_daily_mint': Decimal('1000000'),    # 1M MESH max daily mint
            'min_price_floor': Decimal('0.05'),      # $0.05 USD price floor
            'treasury_reserve': Decimal('50000000')  # 50M MESH reserve
        }

    def calculate_rewards(self,
                          activity_type: str,
                          performance_score: Decimal) -> Dict:
        """Calculate rewards based on activity and performance"""
        base_reward = Decimal('10')  # Base 10 MESH

        if activity_type in self.yield_config['gameplay']['activity_multipliers']:
            multiplier = self.yield_config['gameplay']['activity_multipliers'][activity_type]
            reward = base_reward * multiplier * (performance_score / Decimal('100'))

            # Apply daily cap
            daily_cap = self.yield_config['gameplay']['daily_cap']
            reward = min(reward, daily_cap)

            return {
                'base_reward': base_reward,
                'multiplier': multiplier,
                'performance_factor': performance_score / Decimal('100'),
                'final_reward': reward,
                'reached_cap': reward >= daily_cap
            }

        return {'error': 'Invalid activity type'}

    def get_staking_rewards(self,
                            stake_amount: Decimal,
                            lock_days: int) -> Dict:
        """Calculate staking rewards"""
        if stake_amount < self.yield_config['staking']['min_stake']:
            return {'error': 'Below minimum stake amount'}

        base_apy = self.yield_config['staking']['base_apy']

        # Calculate lock bonus
        lock_bonus = Decimal('1.0')
        if lock_days > self.yield_config['staking']['lock_period']:
            lock_bonus = self.yield_config['staking']['bonus_multiplier']

        annual_yield = stake_amount * base_apy * lock_bonus
        daily_yield = annual_yield / Decimal('365')

        return {
            'stake_amount': stake_amount,
            'lock_days': lock_days,
            'base_apy': base_apy,
            'lock_bonus': lock_bonus,
            'annual_yield': annual_yield,
            'daily_yield': daily_yield
        }

    def export_tokenomics(self) -> str:
        """Export tokenomics configuration to JSON"""
        config = {
            'total_supply': str(self.total_supply),
            'initial_price': str(self.initial_price),
            'distribution_schedule': {
                year: {
                    category: str(amount)
                    for category, amount in allocation.items()
                }
                for year, allocation in self.distribution_schedule.items()
            },
            'yield_config': self.yield_config,
            'utility_features': self.utility_features,
            'burn_mechanisms': self.burn_mechanisms,
            'economic_controls': {
                k: str(v) for k, v in self.economic_controls.items()
            }
        }

        return json.dumps(config, indent=2)


# Example usage
if __name__ == "__main__":
    tokenomics = MeshTokenomics()

    # Calculate gameplay rewards
    reward_calc = tokenomics.calculate_rewards('tournament_win', Decimal('95'))
    print(f"Tournament Reward Calculation: {reward_calc}")

    # Calculate staking rewards
    staking = tokenomics.get_staking_rewards(Decimal('5000'), 90)
    print(f"Staking Rewards: {staking}")

    # Export full tokenomics
    print("\nFull Tokenomics Configuration:")
    print(tokenomics.export_tokenomics())
