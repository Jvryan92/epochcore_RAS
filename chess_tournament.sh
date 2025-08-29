"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/bin/bash

# EPOCHCORE Chess Tournament Launcher
# Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC

echo "🎮 EPOCHCORE Chess Tournament Launcher"
echo "======================================"

# Ensure Python environment is active
source .venv/bin/activate 2>/dev/null || true

# Check dependencies
python -c "import asyncio" 2>/dev/null || pip install asyncio
python -c "import aiohttp" 2>/dev/null || pip install aiohttp

# Create tournament directories
mkdir -p ledger/chess_tournament/stream_updates

# Launch the tournament manager
echo "🚀 Launching EPOCHCORE Chess Tournament..."
echo "📺 Stream URL: https://github.com/Jvryan92/epochcore_RAS/live"
echo ""

python3 - << EOF
import asyncio
from strategy_chess_tournament import ChessTournamentManager

async def main():
    manager = ChessTournamentManager()
    await manager.initialize_tournament()
    print("✨ Tournament initialized!")
    print("\n🏆 Current Tournament Stats:")
    stats = manager.get_tournament_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("\n🎲 Starting tournament cycle...")
    await manager.run_tournament_cycle()

asyncio.run(main())
EOF
