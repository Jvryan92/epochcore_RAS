"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/bin/bash

# EPOCHCORE Kids Academy Launcher
# Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC

echo "🎓 EPOCHCORE Kids Academy Launcher"
echo "================================="

# Ensure Python environment is active
source .venv/bin/activate 2>/dev/null || true

# Create academy directories
mkdir -p ledger/kids_academy/stream_updates

# Launch the academy manager
echo "🚀 Launching EPOCHCORE Kids Academy..."
echo "📺 Stream URL: https://github.com/Jvryan92/epochcore_RAS/kids"
echo ""

python3 - << EOF
import asyncio
from strategy_kids_academy import KidsAcademyManager, LearningCategory

async def main():
    manager = KidsAcademyManager()
    await manager.initialize_academy()
    print("✨ Kids Academy initialized!")
    print("\n📚 Current Academy Stats:")
    stats = manager.get_academy_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("\nLearning Categories:")
    print("  🔢 Math Adventures - Number Ninja, Fraction Friends, Shape Shifters")
    print("  🔬 Science Explorers - Lab Heroes, Element Quest, Science Safari")
    print("  💻 Code Wizards - Code Blocks, Robot Programmer, Logic Loops")
    print("  📚 Story Quest - Reading Adventures, Word Games, Creative Writing")
    print("  🎨 Imagination Lab - Art Projects, Music Making, Digital Creation")
    print("  🧩 Puzzle Masters - Logic Games, Strategy Challenges, Brain Teasers")
    print("  🌿 Eco Rangers - Nature Studies, Environmental Projects, Green Tech")
    print("  🚀 Cosmic Crew - Space Science, Astronomy Fun, Rocket Design")
    print("\n🎮 Starting academy cycle...")
    await manager.run_academy_cycle()

asyncio.run(main())
EOF
