"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/bin/bash

# EPOCHCORE Agentic Arcade Launcher
# Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC

echo "🎰 EPOCHCORE Agentic Arcade Launcher"
echo "=================================="

# Ensure Python environment is active
source .venv/bin/activate 2>/dev/null || true

# Create arcade directories
mkdir -p ledger/agentic_arcade/stream_updates

# Launch the arcade manager
echo "🚀 Launching EPOCHCORE Agentic Arcade..."
echo "📺 Stream URL: https://github.com/Jvryan92/epochcore_RAS/arcade"
echo ""

python3 - << EOF
import asyncio
from strategy_agentic_arcade import ArcadeManager, GameType

async def main():
    manager = ArcadeManager()
    await manager.initialize_arcade()
    print("✨ Agentic Arcade initialized!")
    print("\n🎲 Current Arcade Stats:")
    stats = manager.get_arcade_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("\nAvailable Games:")
    print("  🃏 Blackjack - Classic casino card game")
    print("  🎲 Roulette - European roulette wheel")
    print("  🎴 Baccarat - High-stakes card game")
    print("  ♠️  Texas Hold'em - No-limit tournament poker")
    print("\n🎮 Starting arcade cycle...")
    await manager.run_arcade_cycle()

asyncio.run(main())
EOF
