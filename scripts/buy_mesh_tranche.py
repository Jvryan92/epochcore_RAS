"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import time

from scripts.init_mesh_system import init_mesh_system


def buy_tranche():
    """Purchase a MeshCredit tranche"""

    # Initialize system
    game, tranche_master = init_mesh_system()

    # Get available tranches
    available = tranche_master.get_available_tranches()

    # Select B-rated tranche (lowest risk for demo)
    tranche_id = available[-1]['tranche_id']

    # Purchase tranche
    result = tranche_master.purchase_tranche(tranche_id, 'JVRYAN92')

    if result:
        print("\n=== Tranche Purchase Successful ===")
        print(f"Tranche ID: {result['tranche_id']}")
        print(f"Amount: {result['mesh_amount']:,} MESH")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Yield Rate: {result['yield_rate']*100:.1f}% APY")
        print(f"Lock Period: {result['lock_period']} days")
        print(f"Penny Backing: {result['penny_backing']} pennies")
        print(f"Unlock Date: {time.ctime(result['unlock_time'])}")
        print(f"Investor Glyph: {result['investor_glyph']}")

        # Calculate expected returns
        days = result['lock_period']
        rate = result['yield_rate']
        amount = result['mesh_amount']

        expected_yield = amount * rate * (days/365)
        print(f"\nExpected Yield: {expected_yield:,.2f} MESH")
        print(f"Total Return: {(amount + expected_yield):,.2f} MESH")
    else:
        print("\nTranche purchase failed!")

        # Show current balance
        wallet_id = game.players['JVRYAN92'].wallet_id
        print(f"Your balance: {game.mesh.get_balance(wallet_id):,} MESH")


if __name__ == '__main__':
    buy_tranche()
