"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

from mesh_credit import MeshCredit, MeshGlyph


def test_genesis_block():
    """Test genesis block creation"""
    mesh = MeshCredit()

    # Verify genesis block
    assert len(mesh.chain) == 1
    genesis = mesh.chain[0]
    assert genesis.index == 0
    assert genesis.previous_hash == "0"
    assert len(genesis.glyphs) == 3  # Three founder glyphs


def test_supply_cap():
    """Test maximum supply cap enforcement"""
    mesh = MeshCredit()

    # Try to exceed supply cap
    exceed_cap = mesh.add_transaction(
        sender="TEST_WALLET_1",
        recipient="TEST_WALLET_2",
        amount=25_000_000  # Greater than 21M cap
    )
    assert not exceed_cap

    # Valid transaction within cap
    valid_tx = mesh.add_transaction(
        sender="TEST_WALLET_1",
        recipient="TEST_WALLET_2",
        amount=100
    )
    assert valid_tx


def test_mining_gravity():
    """Test emotional gravity requirements for mining"""
    mesh = MeshCredit()

    # Add test transaction
    mesh.add_transaction("TEST1", "TEST2", 50)

    # Try mining with low gravity
    low_glyph = MeshGlyph("LOW_GRAVITY", 0.1, 0.1, False)
    low_block = mesh.mine_block(low_glyph)
    assert low_block is None  # Should fail

    # Mine with sufficient gravity
    good_glyph = MeshGlyph("GOOD_GRAVITY", 0.8, 0.8, False)
    good_block = mesh.mine_block(good_glyph)
    assert good_block is not None
    assert good_block.proof_gravity >= mesh.min_gravity


def test_penny_backing():
    """Test penny backing system"""
    mesh = MeshCredit()

    initial_backing = mesh.backing_pennies
    mesh.back_with_pennies(100)
    assert mesh.backing_pennies == initial_backing + 100


def test_wallet_balance():
    """Test wallet balance tracking"""
    mesh = MeshCredit()

    # Add and mine some transactions
    mesh.add_transaction("WALLET_A", "WALLET_B", 50)
    glyph = MeshGlyph("TEST_GLYPH", 0.9, 0.9, False)
    mesh.mine_block(glyph)

    assert mesh.get_balance("WALLET_A") == -50
    assert mesh.get_balance("WALLET_B") == 50


def test_chain_verification():
    """Test blockchain integrity verification"""
    mesh = MeshCredit()

    # Add some valid blocks
    mesh.add_transaction("TEST1", "TEST2", 100)
    glyph = MeshGlyph("TEST_GLYPH", 0.9, 0.9, False)
    mesh.mine_block(glyph)

    assert mesh.verify_chain()

    # Tamper with a block
    mesh.chain[1].transactions[0]['amount'] = 200

    assert not mesh.verify_chain()  # Should detect tampering
