"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

from mesh_credit_admin import MeshCreditAdmin


def main():
    admin = MeshCreditAdmin()

    # Process $100 investment
    result = admin.process_investment(100.0, 'JVRYAN92')

    print('\n=== Investment Result ===')
    print(f'USD Amount: ${result["usd_amount"]}')
    print(f'MeshCredits: {result["mesh_amount"]:,}')
    print(f'Penny Backing: {result["penny_backing"]} pennies')
    print(f'Wallet ID: {result["wallet_id"]}')
    print(f'Investment Glyph: {result["investment_glyph"]}')
    print(f'New Balance: {result["new_balance"]:,} MESH\n')

    print('=== System Status ===')
    stats = admin.get_system_stats()
    print(f'Total Supply: {stats["total_supply"]:,} MESH')
    print(f'Current Supply: {stats["current_supply"]:,} MESH')
    print(f'Penny Backing: {stats["penny_backing"]} pennies')
    print(f'Stability Ratio: {stats["stability_ratio"]:.2%}')
    print(f'Active Players: {stats["active_players"]}')
    print(f'Total Blocks: {stats["total_blocks"]}')
    print(f'Conversion Rate: {stats["conversion_rate"]} MESH/USD')
    print(f'Min Gravity: {stats["min_gravity"]}')


if __name__ == '__main__':
    main()
