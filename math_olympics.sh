"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/bin/bash

# EPOCHCORE Math Olympics Launcher
# Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC

echo "🏆 EPOCHCORE Math Olympics Launcher"
echo "=================================="

# Ensure Python environment is active
source .venv/bin/activate 2>/dev/null || true

# Check dependencies
python -c "import asyncio" 2>/dev/null || pip install asyncio
python -c "import aiohttp" 2>/dev/null || pip install aiohttp

# Create Olympics directories
mkdir -p ledger/math_olympics/stream_updates

# Launch the Olympics manager
echo "🚀 Launching EPOCHCORE Math Olympics..."
echo "📺 Stream URL: https://github.com/Jvryan92/epochcore_RAS/olympics"
echo ""

python3 - << EOF
import asyncio
from strategy_math_olympics import MathOlympicsManager

async def main():
    manager = MathOlympicsManager()
    await manager.initialize_olympics()
    print("✨ Math Olympics initialized!")
    print("\n🏆 Current Olympics Stats:")
    stats = manager.get_olympics_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("\nEvent Schedule:")
    print("  1. Pattern Recognition Olympics")
    print("  2. Strategic Planning Competition")
    print("  3. Cryptographic Puzzles Challenge")
    print("  4. Resource Optimization Games")
    print("  5. Multi-Agent Coordination Challenge")
    print("  6. Network Topology Problems")
    print("  7. Market Simulation Competition")
    print("  8. Process Optimization Race")
    print("\n🎲 Starting Olympics cycle...")
    await manager.run_olympics_cycle()

asyncio.run(main())
EOF
