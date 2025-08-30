#!/usr/bin/env python3
"""
MeshCredit Integration for Capsule Compounding

This script integrates the MeshCredit banking system with the Capsule Compounding
Engine, providing a unified interface for managing capsules with financial backing.

Key features:
1. Create MeshCredit-backed capsules
2. Apply compounding strategies with financial tracking
3. Generate reports on ROI and financial performance
4. Auto-distribute yields across multiple accounts
"""

import argparse
import json
import logging
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] MeshIntegration: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("mesh_integration.log")],
)
logger = logging.getLogger("mesh_integration")

# Import local modules
try:
    from scripts.capsule_compounding import CapsuleCompoundingEngine, COMPOUNDING_TRICKS
    from scripts.meshcredit_bank import MeshCreditBank
except ImportError:
    # Handle case where script is run from scripts directory
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from capsule_compounding import CapsuleCompoundingEngine, COMPOUNDING_TRICKS
    from meshcredit_bank import MeshCreditBank


class MeshCreditIntegration:
    """Integration between MeshCredit Bank and Capsule Compounding Engine"""
    
    def __init__(self):
        """Initialize the integration"""
        self.bank = MeshCreditBank()
        self.engine = CapsuleCompoundingEngine()
        
        logger.info("MeshCredit Integration initialized")
    
    def create_backed_capsule(
        self,
        account_id: str,
        capsule_name: str,
        initial_value: float,
        trick_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new capsule backed by MeshCredit"""
        # Generate capsule ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        capsule_id = f"MESH-{capsule_name.replace(' ', '-')}-{timestamp}"
        
        # Validate account and funds
        account = self.bank.get_account(account_id)
        if account["balance"]["liquid"] < initial_value:
            raise ValueError(
                f"Insufficient funds: {account['balance']['liquid']} < {initial_value}"
            )
        
        # If no trick specified, choose one
        if trick_name is None:
            trick_name = random.choice(COMPOUNDING_TRICKS)
        elif trick_name not in COMPOUNDING_TRICKS:
            raise ValueError(f"Invalid trick name: {trick_name}")
        
        # Link capsule in bank
        link_result = self.bank.link_capsule(
            account_id,
            capsule_id,
            initial_value,
            f"New backed capsule: {capsule_name}"
        )
        
        # Register compound trick
        trick_result = self.engine.register_compound_trick(trick_name, capsule_id)
        
        logger.info(
            f"Created backed capsule {capsule_id} with {initial_value} MeshCredit "
            f"using trick: {trick_name}"
        )
        
        return {
            "capsule_id": capsule_id,
            "account_id": account_id,
            "name": capsule_name,
            "initial_value": initial_value,
            "trick_name": trick_name,
            "trick_result": trick_result,
            "bank_result": link_result,
            "created_at": datetime.now().isoformat(),
        }
    
    def apply_compounding(
        self,
        account_id: str,
        capsule_id: str,
        duration: int = 1,
    ) -> Dict[str, Any]:
        """Apply compounding to a backed capsule"""
        # Get account and validate capsule link
        account = self.bank.get_account(account_id)
        
        # Find capsule link
        capsule_link = None
        for link in account.get("linked_capsules", []):
            if link.get("capsule_id") == capsule_id and link.get("status") == "active":
                capsule_link = link
                break
        
        if not capsule_link:
            raise ValueError(f"Capsule {capsule_id} not linked to account {account_id}")
        
        # Get current capsule value
        current_value = capsule_link.get("current_amount", 0)
        if current_value <= 0:
            raise ValueError(f"Capsule {capsule_id} has no value to compound")
        
        # Get trick name from link
        trick_name = capsule_link.get("trick_name")
        if not trick_name:
            # If no trick is stored in the link, try to find the latest one
            # This is a fallback for compatibility with existing capsules
            trick_name = "Recursive Yield Amplification"  # Default
        
        # Apply compounding via engine
        compound_result = self.engine.apply_compound_trick(
            trick_name,
            capsule_id,
            current_value,
            duration,
        )
        
        # Calculate the gain
        original_value = current_value
        new_value = compound_result["adjusted_value"]
        gain = new_value - original_value
        
        # Apply the gain to the bank account
        if gain > 0:
            reward_result = self.bank.apply_compound_rewards(
                account_id,
                capsule_id,
                gain,
                f"Compounding with {trick_name} for {duration} periods"
            )
        else:
            reward_result = {"reward_amount": 0}
        
        logger.info(
            f"Applied compounding to capsule {capsule_id}: "
            f"{original_value:.2f} → {new_value:.2f} MeshCredit (+{gain:.2f})"
        )
        
        return {
            "capsule_id": capsule_id,
            "account_id": account_id,
            "original_value": original_value,
            "new_value": new_value,
            "gain": gain,
            "trick_name": trick_name,
            "duration": duration,
            "compound_result": compound_result,
            "reward_result": reward_result,
            "timestamp": datetime.now().isoformat(),
        }
    
    def batch_compound(
        self,
        account_id: str,
        duration: int = 1,
    ) -> Dict[str, Any]:
        """Apply compounding to all capsules linked to an account"""
        # Get account
        account = self.bank.get_account(account_id)
        
        # Find active capsules
        active_capsules = [
            link.get("capsule_id") 
            for link in account.get("linked_capsules", []) 
            if link.get("status") == "active"
        ]
        
        if not active_capsules:
            return {
                "account_id": account_id,
                "status": "no_capsules",
                "message": "No active capsules found for this account",
                "results": [],
            }
        
        # Apply compounding to each capsule
        results = []
        total_gain = 0.0
        
        for capsule_id in active_capsules:
            try:
                result = self.apply_compounding(account_id, capsule_id, duration)
                results.append(result)
                total_gain += result.get("gain", 0)
            except Exception as e:
                logger.error(f"Error compounding capsule {capsule_id}: {e}")
                results.append({
                    "capsule_id": capsule_id,
                    "status": "error",
                    "error": str(e),
                })
        
        logger.info(
            f"Batch compounding completed for account {account_id}: "
            f"{len(results)} capsules, total gain: {total_gain:.2f} MeshCredit"
        )
        
        return {
            "account_id": account_id,
            "status": "success",
            "total_gain": total_gain,
            "capsules_processed": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }
    
    def create_investment_portfolio(
        self,
        account_id: str,
        portfolio_name: str,
        total_investment: float,
        strategy: str = "balanced",
    ) -> Dict[str, Any]:
        """Create a portfolio of capsules with different compounding strategies"""
        # Get account and validate funds
        account = self.bank.get_account(account_id)
        if account["balance"]["liquid"] < total_investment:
            raise ValueError(
                f"Insufficient liquid balance: {account['balance']['liquid']} < {total_investment}"
            )
        
        # Define strategies and their trick allocations
        strategies = {
            "conservative": {
                "Ledger Provenance Chaining": 0.25,
                "Ethical Reflection Loop": 0.25,
                "Temporal Mesh Rebalancing": 0.20,
                "Resilience Mesh Overlay": 0.20,
                "Collaborative Mesh Expansion": 0.10,
            },
            "balanced": {
                "Recursive Yield Amplification": 0.15,
                "Adaptive Interest Compounding": 0.15,
                "MeshCredit Cascade": 0.15,
                "StrategyDeck Interlink": 0.15,
                "Intelligence Capsule Chaining": 0.15,
                "Multi-Domain Mesh Synthesis": 0.15,
                "Recursive Ledger Growth": 0.10,
            },
            "aggressive": {
                "Quantum Liquidity Loop": 0.20,
                "Self-Referential Growth": 0.20,
                "Quantum Mesh Fork": 0.20,
                "Quantum Capsule Amplification": 0.20,
                "Capsule Swarm Optimization": 0.10,
                "Evolutionary Capsule Mutation": 0.10,
            },
        }
        
        # Use requested strategy or default to balanced
        if strategy not in strategies:
            logger.warning(f"Unknown strategy: {strategy}, defaulting to balanced")
            strategy = "balanced"
        
        allocation = strategies[strategy]
        
        # Create capsules according to allocation
        capsules = []
        remaining_investment = total_investment
        
        for trick, percentage in allocation.items():
            # For the last trick, use all remaining funds to avoid rounding issues
            if trick == list(allocation.keys())[-1]:
                amount = remaining_investment
            else:
                amount = round(total_investment * percentage, 2)
                remaining_investment -= amount
            
            if amount <= 0:
                continue
            
            capsule_name = f"{portfolio_name}-{trick.split()[0]}"
            
            try:
                result = self.create_backed_capsule(
                    account_id,
                    capsule_name,
                    amount,
                    trick,
                )
                capsules.append(result)
            except Exception as e:
                logger.error(f"Error creating capsule {capsule_name}: {e}")
                capsules.append({
                    "name": capsule_name,
                    "status": "error",
                    "error": str(e),
                })
        
        logger.info(
            f"Created {len(capsules)} capsule portfolio for account {account_id}: "
            f"{portfolio_name} with {total_investment} MeshCredit ({strategy} strategy)"
        )
        
        return {
            "portfolio_name": portfolio_name,
            "account_id": account_id,
            "strategy": strategy,
            "total_investment": total_investment,
            "capsule_count": len(capsules),
            "capsules": capsules,
            "created_at": datetime.now().isoformat(),
        }
    
    def get_capsule_report(
        self,
        capsule_id: str,
    ) -> Dict[str, Any]:
        """Get a detailed report for a specific capsule"""
        # Find the capsule in the bank system
        account_id = None
        capsule_data = None
        
        # Search through all accounts (not efficient, but works for demo)
        account_files = list(Path(self.bank.ACCOUNTS_DIR).glob("*.json"))
        
        for account_file in account_files:
            try:
                with open(account_file, "r") as f:
                    account = json.load(f)
                
                for link in account.get("linked_capsules", []):
                    if link.get("capsule_id") == capsule_id:
                        account_id = account["account_id"]
                        capsule_data = link
                        break
                
                if account_id:
                    break
            except Exception:
                continue
        
        if not capsule_data:
            raise ValueError(f"Capsule not found: {capsule_id}")
        
        # Get trick details if available
        trick_name = capsule_data.get("trick_name")
        trick_properties = None
        
        if trick_name:
            trick_properties = self.engine.get_trick_properties(trick_name)
        
        # Build the report
        initial_amount = capsule_data.get("initial_amount", 0)
        current_amount = capsule_data.get("current_amount", 0)
        growth = current_amount - initial_amount
        growth_pct = (growth / initial_amount * 100) if initial_amount > 0 else 0
        
        linked_at = datetime.fromisoformat(capsule_data.get("linked_at"))
        now = datetime.now()
        days_active = (now - linked_at).days
        
        # Annualized return (if active for at least 1 day)
        if days_active > 0 and initial_amount > 0:
            annualized_return = ((current_amount / initial_amount) ** (365 / days_active) - 1) * 100
        else:
            annualized_return = 0
        
        return {
            "capsule_id": capsule_id,
            "account_id": account_id,
            "status": capsule_data.get("status", "unknown"),
            "initial_amount": initial_amount,
            "current_amount": current_amount,
            "growth": growth,
            "growth_percentage": growth_pct,
            "days_active": days_active,
            "annualized_return": annualized_return,
            "linked_at": capsule_data.get("linked_at"),
            "trick_name": trick_name,
            "trick_properties": trick_properties,
            "last_reward": capsule_data.get("last_reward"),
        }
    
    def get_portfolio_report(
        self,
        account_id: str,
    ) -> Dict[str, Any]:
        """Get a consolidated report of all capsules for an account"""
        # Get account
        account = self.bank.get_account(account_id)
        
        # Get active capsules
        active_capsules = [
            link for link in account.get("linked_capsules", []) 
            if link.get("status") == "active"
        ]
        
        if not active_capsules:
            return {
                "account_id": account_id,
                "account_name": account.get("name", ""),
                "status": "no_capsules",
                "capsule_count": 0,
                "total_invested": 0,
                "total_current_value": 0,
                "total_growth": 0,
                "capsules": [],
            }
        
        # Get report for each capsule
        capsule_reports = []
        total_invested = 0
        total_current_value = 0
        
        for link in active_capsules:
            capsule_id = link.get("capsule_id")
            try:
                report = self.get_capsule_report(capsule_id)
                capsule_reports.append(report)
                total_invested += report["initial_amount"]
                total_current_value += report["current_amount"]
            except Exception as e:
                logger.error(f"Error getting report for capsule {capsule_id}: {e}")
                capsule_reports.append({
                    "capsule_id": capsule_id,
                    "status": "error",
                    "error": str(e),
                })
        
        # Calculate overall performance
        total_growth = total_current_value - total_invested
        growth_pct = (total_growth / total_invested * 100) if total_invested > 0 else 0
        
        # Sort by performance (highest growth first)
        capsule_reports.sort(key=lambda x: x.get("growth", 0), reverse=True)
        
        return {
            "account_id": account_id,
            "account_name": account.get("name", ""),
            "capsule_count": len(active_capsules),
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_growth": total_growth,
            "growth_percentage": growth_pct,
            "compound_balance": account["balance"]["compound"],
            "capsules": capsule_reports,
            "generated_at": datetime.now().isoformat(),
        }


def create_demo_data() -> None:
    """Create demonstration data"""
    integration = MeshCreditIntegration()
    bank = integration.bank
    
    # Create accounts if they don't exist
    try:
        alice = bank.get_account("demo_alice")
    except ValueError:
        alice = bank.create_account("Alice's MeshCredit", "demo_alice", 5000.0)
    
    try:
        bob = bank.get_account("demo_bob")
    except ValueError:
        bob = bank.create_account("Bob's MeshCredit", "demo_bob", 3000.0)
    
    try:
        project = bank.get_account("demo_project")
    except ValueError:
        project = bank.create_account("Project Alpha", "demo_project", 10000.0, "project")
    
    # Create investment portfolios
    try:
        integration.create_investment_portfolio(
            alice["account_id"],
            "Growth-Fund",
            1000.0,
            "aggressive"
        )
    except Exception as e:
        logger.error(f"Error creating Alice's portfolio: {e}")
    
    try:
        integration.create_investment_portfolio(
            bob["account_id"],
            "Safe-Fund",
            800.0,
            "conservative"
        )
    except Exception as e:
        logger.error(f"Error creating Bob's portfolio: {e}")
    
    try:
        integration.create_investment_portfolio(
            project["account_id"],
            "Project-Fund",
            5000.0,
            "balanced"
        )
    except Exception as e:
        logger.error(f"Error creating Project portfolio: {e}")
    
    # Create individual capsules
    try:
        integration.create_backed_capsule(
            alice["account_id"],
            "Quantum-Boost",
            500.0,
            "Quantum Liquidity Loop"
        )
    except Exception as e:
        logger.error(f"Error creating Alice's capsule: {e}")
    
    try:
        integration.create_backed_capsule(
            project["account_id"],
            "Strategic-Reserve",
            2000.0,
            "StrategyDeck Interlink"
        )
    except Exception as e:
        logger.error(f"Error creating Project's capsule: {e}")
    
    # Apply compounding to simulate growth
    for _ in range(3):  # Simulate 3 compounding cycles
        try:
            integration.batch_compound(alice["account_id"], 10)
        except Exception:
            pass
        
        try:
            integration.batch_compound(bob["account_id"], 10)
        except Exception:
            pass
        
        try:
            integration.batch_compound(project["account_id"], 10)
        except Exception:
            pass
    
    logger.info("Demo data created successfully")


def main() -> None:
    """Command-line interface for MeshCredit Integration"""
    parser = argparse.ArgumentParser(description="MeshCredit Integration for Capsule Compounding")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create capsule command
    create_parser = subparsers.add_parser("create", help="Create a MeshCredit-backed capsule")
    create_parser.add_argument("account_id", help="Account ID")
    create_parser.add_argument("name", help="Capsule name")
    create_parser.add_argument("amount", type=float, help="Initial investment amount")
    create_parser.add_argument("--trick", help="Compounding trick to use (optional)")
    
    # Apply compounding command
    compound_parser = subparsers.add_parser("compound", help="Apply compounding to a capsule")
    compound_parser.add_argument("account_id", help="Account ID")
    compound_parser.add_argument("capsule_id", help="Capsule ID")
    compound_parser.add_argument("--duration", type=int, default=1, help="Compounding duration")
    
    # Batch compound command
    batch_parser = subparsers.add_parser("batch", help="Apply compounding to all capsules in an account")
    batch_parser.add_argument("account_id", help="Account ID")
    batch_parser.add_argument("--duration", type=int, default=1, help="Compounding duration")
    
    # Create portfolio command
    portfolio_parser = subparsers.add_parser("portfolio", help="Create an investment portfolio")
    portfolio_parser.add_argument("account_id", help="Account ID")
    portfolio_parser.add_argument("name", help="Portfolio name")
    portfolio_parser.add_argument("amount", type=float, help="Total investment amount")
    portfolio_parser.add_argument("--strategy", default="balanced", 
                                choices=["conservative", "balanced", "aggressive"],
                                help="Investment strategy")
    
    # Capsule report command
    capsule_report_parser = subparsers.add_parser("capsule-report", help="Get report for a capsule")
    capsule_report_parser.add_argument("capsule_id", help="Capsule ID")
    
    # Portfolio report command
    portfolio_report_parser = subparsers.add_parser("portfolio-report", help="Get portfolio report")
    portfolio_report_parser.add_argument("account_id", help="Account ID")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Create demonstration data")
    
    args = parser.parse_args()
    
    # Initialize integration
    integration = MeshCreditIntegration()
    
    if args.command == "create":
        result = integration.create_backed_capsule(
            args.account_id,
            args.name,
            args.amount,
            args.trick,
        )
        print(f"Created capsule: {result['capsule_id']}")
        print(f"Initial value: {result['initial_value']} MeshCredit")
        print(f"Compounding trick: {result['trick_name']}")
    
    elif args.command == "compound":
        result = integration.apply_compounding(
            args.account_id,
            args.capsule_id,
            args.duration,
        )
        print(f"Applied compounding to capsule {args.capsule_id}")
        print(f"Original value: {result['original_value']} MeshCredit")
        print(f"New value: {result['new_value']} MeshCredit")
        print(f"Gain: {result['gain']} MeshCredit")
        print(f"Trick: {result['trick_name']}")
    
    elif args.command == "batch":
        result = integration.batch_compound(
            args.account_id,
            args.duration,
        )
        print(f"Batch compounding for account {args.account_id}")
        print(f"Capsules processed: {result['capsules_processed']}")
        print(f"Total gain: {result['total_gain']} MeshCredit")
    
    elif args.command == "portfolio":
        result = integration.create_investment_portfolio(
            args.account_id,
            args.name,
            args.amount,
            args.strategy,
        )
        print(f"Created portfolio: {result['portfolio_name']}")
        print(f"Strategy: {result['strategy']}")
        print(f"Total investment: {result['total_investment']} MeshCredit")
        print(f"Capsules created: {result['capsule_count']}")
    
    elif args.command == "capsule-report":
        result = integration.get_capsule_report(args.capsule_id)
        print(f"Report for capsule {result['capsule_id']}:")
        print(f"Status: {result['status']}")
        print(f"Initial investment: {result['initial_amount']} MeshCredit")
        print(f"Current value: {result['current_amount']} MeshCredit")
        print(f"Growth: {result['growth']} MeshCredit ({result['growth_percentage']:.2f}%)")
        print(f"Days active: {result['days_active']}")
        print(f"Annualized return: {result['annualized_return']:.2f}%")
        print(f"Compounding trick: {result['trick_name']}")
    
    elif args.command == "portfolio-report":
        result = integration.get_portfolio_report(args.account_id)
        print(f"Portfolio report for account {result['account_name']}:")
        print(f"Capsules: {result['capsule_count']}")
        print(f"Total invested: {result['total_invested']} MeshCredit")
        print(f"Current value: {result['total_current_value']} MeshCredit")
        print(f"Overall growth: {result['total_growth']} MeshCredit ({result['growth_percentage']:.2f}%)")
        print("\nTop performing capsules:")
        
        for i, capsule in enumerate(result['capsules'][:3], 1):
            print(f"  {i}. {capsule['capsule_id']} - {capsule['growth']} MeshCredit ({capsule['growth_percentage']:.2f}%)")
    
    elif args.command == "demo":
        create_demo_data()
        print("Created demonstration data")
        print("Use other commands to explore the demo data")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
