"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/bin/bash

# EPOCHCORE Innovation Playoffs Launcher
# Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC

echo "💡 EPOCHCORE Innovation Playoffs Launcher"
echo "======================================"

# Ensure Python environment is active
source .venv/bin/activate 2>/dev/null || true

# Create playoffs directories
mkdir -p ledger/innovation_playoffs/stream_updates

# Launch the playoffs manager
echo "🚀 Launching EPOCHCORE Innovation Playoffs..."
echo "📺 Stream URL: https://github.com/Jvryan92/epochcore_RAS/playoffs"
echo ""

python3 - << EOF
import asyncio
from strategy_innovation_playoffs import InnovationPlayoffsManager, IdeaCategory

async def main():
    manager = InnovationPlayoffsManager()
    await manager.initialize_playoffs()
    print("✨ Innovation Playoffs initialized!")
    print("\n💡 Current Playoffs Stats:")
    stats = manager.get_playoffs_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("\nIdea Categories:")
    for category in IdeaCategory:
        print(f"  • {category.value}")
    print("\n🎲 Starting playoffs cycle...")
    await manager.run_playoffs_cycle()

asyncio.run(main())
EOF
