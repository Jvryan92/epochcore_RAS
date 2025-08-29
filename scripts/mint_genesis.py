"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import json
from datetime import datetime, timezone
from decimal import Decimal

from blockchain.mesh_credit import MeshCredit


def mint_genesis():
    """Mint the MeshCredit genesis block"""

    print("\n=== Minting MeshCredit Genesis Block ===")
    print("Initializing MeshCredit system...")
    mesh = MeshCredit()

    # Verify the genesis block
    genesis = mesh.chain[0]

    print("\nGenesis Block Details:")
    print("----------------------")
    print(f"Block Height: {genesis.index}")
    print(
        f"Timestamp: {datetime.fromtimestamp(genesis.timestamp, tz=timezone.utc).isoformat()}")
    print(f"Number of Transactions: {len(genesis.transactions)}")

    # Display founder glyph details
    print("\nFounder Glyph Initialization:")
    print("--------------------------")
    for tx in genesis.transactions:
        if tx.get('type') == 'founder_genesis':
            glyph_id = tx.get('glyph_id')
            gravity = tx.get('emotional_gravity')
            resonance = tx.get('resonance', {})
            echo = tx.get('echo_strength')

            print(f"\nGlyph: {glyph_id}")
            print(f"Emotional Gravity: {gravity}")
            print(f"Echo Strength: {echo}")
            print(f"Resonance Metadata:")
            for k, v in resonance.items():
                print(f"  - {k}: {v}")

    # Display network configuration
    print("\nNetwork Configuration:")
    print("---------------------")
    for tx in genesis.transactions:
        if tx.get('type') == 'network_genesis':
            config = tx.get('data', {})
            print(f"Game Version: {config.get('game_version')}")
            print(f"Total Supply: {config.get('total_supply')} MESH")
            print(f"Governance: {config.get('governance_model')}")
            print(f"Yield Mechanism: {config.get('yield_mechanism')}")
            print("\nGenesis Proof Cycles:")
            for action, cycles in config.get('proof_cycles', {}).items():
                print(f"  - {action}: {cycles}")

    # Save genesis data
    genesis_data = {
        'block': {
            'index': genesis.index,
            'timestamp': genesis.timestamp,
            'hash': genesis.calculate_hash(),
            'transactions': genesis.transactions
        },
        'network': {
            'total_supply': str(mesh.total_supply),
            'initial_block_reward': str(mesh.initial_block_reward),
            'halving_blocks': mesh.halving_blocks
        }
    }

    # Add proof chain data if available
    if mesh.immutable.proof_chain:
        latest_proof = mesh.immutable.proof_chain[-1]
        genesis_data['proof_chain'] = {
            'height': len(mesh.immutable.proof_chain),
            'merkle_root': latest_proof.merkle_root
        }
        print("\nVerifying Proof Chain:")
        print("--------------------")
        if mesh.immutable.verify_proof_chain():
            print("✅ Genesis proof chain verified!")
            print(f"Chain Height: {len(mesh.immutable.proof_chain)}")
            print(f"Latest Merkle Root: {latest_proof.merkle_root[:16]}...")

    with open('genesis_block.json', 'w') as f:
        json.dump(genesis_data, f, indent=2)
    print("\nGenesis data saved to: genesis_block.json")

    print("\n=== Genesis Block Minted Successfully ===\n")
    return mesh


if __name__ == "__main__":
    mint_genesis()
