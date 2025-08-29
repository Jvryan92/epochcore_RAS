"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import time

from mesh_credit_admin import MeshCreditAdmin
from mesh_tranche import MeshTrancheMaster


def main():
    # Initialize admin and tranche systems
    admin = MeshCreditAdmin()
    tranche_master = MeshTrancheMaster(admin.game)

    # Create available tranches
    tranches = [
        tranche_master.create_tranche("AAA", 100_000),  # AAA-rated 100K MESH
        tranche_master.create_tranche("AA", 50_000),    # AA-rated 50K MESH
        tranche_master.create_tranche("A", 25_000),     # A-rated 25K MESH
        tranche_master.create_tranche("BBB", 10_000),   # BBB-rated 10K MESH
        tranche_master.create_tranche("BB", 5_000),     # BB-rated 5K MESH
        tranche_master.create_tranche("B", 2_500)       # B-rated 2.5K MESH
    ]

    # Display available tranches
    print("\n=== Available MeshCredit Tranches ===")
    available = tranche_master.get_available_tranches()
    for i, tranche in enumerate(available):
        print(f"\n{i+1}. Risk Level: {tranche['risk_level']}")
        print(f"   Amount: {tranche['mesh_amount']:,} MESH")
        print(f"   Yield Rate: {tranche['yield_rate']*100:.1f}% APY")
        print(f"   Lock Period: {tranche['lock_period']} days")
        print(f"   Penny Backing: {tranche['penny_backing']} pennies")

    # Purchase example tranche (B-rated for demo)
    tranche_id = available[-1]['tranche_id']  # Get B-rated tranche
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

        # Show expected yield
        days_to_unlock = result['lock_period']
        expected_yield = result['mesh_amount'] * \
            result['yield_rate'] * (days_to_unlock/365)
        print(f"\nExpected Yield: {expected_yield:,.2f} MESH")
        print(f"Total Return: {(result['mesh_amount'] + expected_yield):,.2f} MESH")
    else:
        print("\nTranche purchase failed. Please check your MESH balance.")


if __name__ == '__main__':
    main()
