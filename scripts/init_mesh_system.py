"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import logging
import time

from mesh_credit import MeshCredit, MeshGlyph
from mesh_credit_game import MeshCreditGame
from mesh_tranche import MeshTrancheMaster

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def init_mesh_system():
    """Initialize the complete MeshCredit system"""

    # Create base system
    mesh = MeshCredit()
    game = MeshCreditGame()
    game.mesh = mesh  # Share the same mesh instance
    tranche_master = MeshTrancheMaster(game)

    # Create genesis wallet
    genesis_glyph = MeshGlyph(
        glyph_id="GENESIS_MASTER",
        trust_weight=1.0,
        emotional_resonance=1.0,
        founder_status=True
    )

    # Initialize supply
    mesh.add_transaction(
        "GENESIS",
        "MESH_ADMIN_GENESIS",
        mesh.total_supply
    )

    # Initialize tranche escrow
    mesh.add_transaction(
        "MESH_ADMIN_GENESIS",
        "MESH_TRANCHE_ESCROW",
        mesh.total_supply * 0.1  # 10% for tranches
    )

    # Create investor account
    wallet_id = game.create_player('JVRYAN92')

    # Process $100 investment
    mesh_amount = 1_000_000  # $100 * 10000 rate
    penny_backing = 2500  # 25% of $100 in pennies

    # Add penny backing
    mesh.back_with_pennies(penny_backing)

    # Create investment glyph
    investor_glyph = MeshGlyph(
        glyph_id=f"INVESTOR_{int(time.time())}",
        trust_weight=0.8,
        emotional_resonance=0.8,
        founder_status=False
    )

    # Add glyph to investor
    game.players['JVRYAN92'].glyphs.append(investor_glyph)

    # Transfer investment amount
    if mesh.add_transaction(
        "MESH_ADMIN_GENESIS",
        wallet_id,
        mesh_amount
    ):
        print("\n=== Investment Transfer ===")
        print(f"From: MESH_ADMIN_GENESIS")
        print(f"To: {wallet_id}")
        print(f"Amount: {mesh_amount:,} MESH")
    else:
        print("\nInvestment transfer failed!")

    print("\n=== System Initialization ===")
    print(f"Wallet ID: {wallet_id}")
    print(f"Balance: {mesh.get_balance(wallet_id):,} MESH")
    print(f"Penny Backing: {mesh.backing_pennies} pennies")
    print(f"Investment Glyph: {investor_glyph.glyph_id}")

    # Create initial tranches
    tranches = [
        tranche_master.create_tranche("AAA", 100_000),
        tranche_master.create_tranche("AA", 50_000),
        tranche_master.create_tranche("A", 25_000),
        tranche_master.create_tranche("BBB", 10_000),
        tranche_master.create_tranche("BB", 5_000),
        tranche_master.create_tranche("B", 2_500)
    ]

    # Display available tranches
    print("\n=== Available Tranches ===")
    available = tranche_master.get_available_tranches()
    for i, tranche in enumerate(available):
        print(f"\n{i+1}. Risk Level: {tranche['risk_level']}")
        print(f"   Amount: {tranche['mesh_amount']:,} MESH")
        print(f"   Yield Rate: {tranche['yield_rate']*100:.1f}% APY")
        print(f"   Lock Period: {tranche['lock_period']} days")
        print(f"   Penny Backing: {tranche['penny_backing']} pennies")

    return game, tranche_master


if __name__ == '__main__':
    game, tranche_master = init_mesh_system()
