"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/bin/bash

# EPOCHCORE Kids Content Generator Launcher
# Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC

echo "🎨 EPOCHCORE Kids Content Generator Launcher"
echo "=========================================="

# Ensure Python environment is active
source .venv/bin/activate 2>/dev/null || true

# Create content directories
mkdir -p ledger/kids_content/stream_updates

# Launch the content generator
echo "🚀 Launching EPOCHCORE Kids Content Generator..."
echo "📺 Stream URL: https://github.com/Jvryan92/epochcore_RAS/kids/content"
echo ""

python3 - << EOF
import asyncio
from strategy_kids_content import KidsContentGenerator, ContentType, ContentTheme

async def main():
    generator = KidsContentGenerator()
    print("✨ Content Generator initialized!")
    print("\n📚 Content Types:")
    for content_type in ContentType:
        print(f"  • {content_type.value}")
    print("\n🎨 Content Themes:")
    for theme in ContentTheme:
        print(f"  • {theme.value}")
    print("\n🤖 Agent Specialties:")
    for agent, specialties in generator.agent_specialties.items():
        print(f"  {agent}:")
        for specialty in specialties:
            print(f"    - {specialty.value}")
    print("\n🎮 Starting content generation cycle...")
    await generator.run_generation_cycle()

asyncio.run(main())
EOF
