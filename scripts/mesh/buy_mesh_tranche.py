"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved 

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

import hashlib
import json
import os
from decimal import Decimal
from typing import Dict, Optional

from scripts.mesh.transfer import Transfer

LEDGER_PATH = os.path.join(os.path.dirname(__file__), "mesh_transactions.jsonl")
MESH_KEY = b"meshcredit2024"  # Just for testing
ADMIN_WALLET = "MESH_ADMIN_GENESIS"


def load_tranches() -> Dict:
    """Load available investment tranches."""
    return {
        "AAA": {
            "amount": Decimal("100000"),
            "yield_rate": Decimal("0.12"),  # 12% APY
            "lock_period": 90,  # days
            "penny_backing": 400,
        },
        "AA": {
            "amount": Decimal("50000"),
            "yield_rate": Decimal("0.15"),  # 15% APY
            "lock_period": 60,  # days
            "penny_backing": 175,
        },
        "A": {
            "amount": Decimal("25000"),
            "yield_rate": Decimal("0.18"),  # 18% APY
            "lock_period": 45,  # days
            "penny_backing": 75,
        },
        "BBB": {
            "amount": Decimal("10000"),
            "yield_rate": Decimal("0.22"),  # 22% APY
            "lock_period": 30,  # days
            "penny_backing": 25,
        },
        "BB": {
            "amount": Decimal("5000"),
            "yield_rate": Decimal("0.28"),  # 28% APY
            "lock_period": 15,  # days
            "penny_backing": 10,
        },
        "B": {
            "amount": Decimal("2500"),
            "yield_rate": Decimal("0.35"),  # 35% APY
            "lock_period": 7,  # days
            "penny_backing": 3,
        }
    }


def setup_genesis():
    """Create initial genesis transaction."""
    print("Processing Genesis Transaction:")
    print(f"Amount: 21,000,000 MESH")
    print(f"Recipient: {ADMIN_WALLET}")

    transfer = Transfer(MESH_KEY, LEDGER_PATH)

    # Create initial supply
    success, error = transfer.transfer(
        from_wallet=ADMIN_WALLET,
        to_wallet=ADMIN_WALLET,
        amount=Decimal("21000000"),
        tx_type="genesis"
    )

    if success:
        print("Genesis block mined successfully")
        print(f"Block hash: {hashlib.sha256(b'genesis').hexdigest()}")

        # Send initial investment amount to the user's wallet
        initial_transfer = Decimal("200000")  # 200k MESH for investing
        success, error = transfer.transfer(
            from_wallet=ADMIN_WALLET,
            to_wallet="MESH_JVRYAN92_1756445384",
            amount=initial_transfer,
            tx_type="investment"
        )

        if success:
            print(f"\nInitial balance transferred: {initial_transfer:,} MESH")
        else:
            print(f"\nInitial transfer failed: {error}")
    else:
        print(f"Genesis failed: {error}")


def buy_tranche(wallet_id: str, risk_level: str) -> Optional[Dict]:
    """Buy an investment tranche."""
    tranches = load_tranches()
    if risk_level not in tranches:
        print(f"Invalid risk level: {risk_level}")
        return None

    tranche = tranches[risk_level]
    transfer = Transfer(MESH_KEY, LEDGER_PATH)

    # Check wallet has sufficient balance
    balance = transfer.get_balance(wallet_id)
    if balance < tranche["amount"]:
        print("Insufficient balance for tranche purchase")
        print(f"Required: {tranche['amount']} MESH")
        print(f"Your balance: {balance} MESH")
        return None

    # Execute transfer
    success, error = transfer.transfer(
        from_wallet=wallet_id,
        to_wallet=ADMIN_WALLET,
        amount=tranche["amount"],
        tx_type="investment"
    )

    if not success:
        print(f"Investment transfer failed: {error}")
        return None

    # Record investment
    investment = {
        "wallet": wallet_id,
        "risk_level": risk_level,
        "amount": str(tranche["amount"]),
        "yield_rate": str(tranche["yield_rate"]),
        "lock_period": tranche["lock_period"],
        "penny_backing": tranche["penny_backing"]
    }

    investment_path = f"{os.path.splitext(LEDGER_PATH)[0]}_investments.jsonl"
    with open(investment_path, "a") as f:
        f.write(json.dumps(investment) + "\n")

    return investment


def main():
    """Main execution function."""
    # Initialize genesis if needed
    setup_genesis()

    # Display wallet info
    wallet_id = "MESH_JVRYAN92_1756445384"
    transfer = Transfer(MESH_KEY, LEDGER_PATH)
    balance = transfer.get_balance(wallet_id)

    print("\n=== System Initialization ===")
    print(f"Wallet ID: {wallet_id}")
    print(f"Balance: {balance} MESH")
    print(f"Penny Backing: 2500 pennies")
    print("Investment Glyph: INVESTOR_1756445384")

    # Display available tranches
    print("\n=== Available Tranches ===\n")
    tranches = load_tranches()
    for i, (risk_level, tranche) in enumerate(tranches.items(), 1):
        print(f"{i}. Risk Level: {risk_level}")
        print(f"   Amount: {tranche['amount']:,} MESH")
        print(f"   Yield Rate: {float(tranche['yield_rate']*100):.1f}% APY")
        print(f"   Lock Period: {tranche['lock_period']} days")
        print(f"   Penny Backing: {tranche['penny_backing']} pennies\n")

    # Execute diversified investment strategy
    investments = []

    # Buy AA tranche (50k MESH)
    investment = buy_tranche(wallet_id, "AA")
    if investment:
        investments.append(investment)
        print("\nAA Tranche purchased successfully!")
        print(f"Amount: {investment['amount']} MESH")
        print(f"Yield Rate: {float(Decimal(investment['yield_rate'])*100):.1f}% APY")
        print(f"Lock Period: {investment['lock_period']} days")

    # Buy A tranche (25k MESH)
    investment = buy_tranche(wallet_id, "A")
    if investment:
        investments.append(investment)
        print("\nA Tranche purchased successfully!")
        print(f"Amount: {investment['amount']} MESH")
        print(f"Yield Rate: {float(Decimal(investment['yield_rate'])*100):.1f}% APY")
        print(f"Lock Period: {investment['lock_period']} days")

    # Calculate portfolio stats
    if investments:
        total_invested = sum(Decimal(inv['amount']) for inv in investments)
        weighted_yield = sum(
            Decimal(inv['amount']) * Decimal(inv['yield_rate'])
            for inv in investments
        ) / total_invested if total_invested > 0 else Decimal('0')

        print("\n=== Investment Portfolio Summary ===")
        print(f"Total Invested: {total_invested:,} MESH")
        print(f"Average Yield: {float(weighted_yield*100):.1f}% APY")
        print(f"Remaining Balance: {transfer.get_balance(wallet_id):,} MESH")
    else:
        print("\nNo investments made!")
        print(f"Balance: {balance} MESH")


if __name__ == "__main__":
    main()
