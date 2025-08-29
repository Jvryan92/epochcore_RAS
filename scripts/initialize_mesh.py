"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import os
import sys


def setup_blockchain():
    """Setup the blockchain environment"""

    # Ensure blockchain directory exists
    blockchain_dir = os.path.join(os.path.dirname(__file__), '..', 'blockchain')
    if not os.path.exists(blockchain_dir):
        os.makedirs(blockchain_dir)

    # Create necessary __init__ files
    init_files = [
        os.path.join(blockchain_dir, '__init__.py'),
        os.path.join(os.path.dirname(__file__), '__init__.py')
    ]

    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Package initialization"""')


def main():
    """Initialize and run genesis minting"""
    print("\n=== Setting up MeshCredit Environment ===")

    # Setup environment
    setup_blockchain()

    # Add project root to Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Import after environment setup
    from scripts.mint_genesis import mint_genesis

    # Run genesis minting
    try:
        mesh = mint_genesis()
        print("\n✅ Genesis block minted successfully!")
        return 0
    except Exception as e:
        print(f"\n❌ Error minting genesis block: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
