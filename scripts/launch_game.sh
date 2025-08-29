#!/bin/bash

# EpochCore RAS - Game Launch Script
echo "🎮 Launching EpochCore RAS Game"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start the dashboard
echo "🎮 Starting game dashboard..."
python -m game_launch.dashboard &
DASHBOARD_PID=$!

# Initialize game systems
echo "⚙️ Initializing game systems..."
mkdir -p logs/game

# Launch game modes in parallel
echo "✨ Launching game modes..."

# Characters Mode
echo "👥 Launching Characters mode..."
python -m game_launch.modes.characters &

# Meshgear Mode
echo "🎨 Launching Meshgear mode..."
python -m game_launch.modes.meshgear &

# Governance Mode
echo "🏛️ Launching Governance mode..."
python -m game_launch.modes.governance &

# Story Mode
echo "📖 Launching Story mode..."
python -m game_launch.modes.story &

# Competitive Mode
echo "⚔️ Launching Competitive mode..."
python -m game_launch.modes.competitive &

echo "✅ All game modes launched!"
echo "📱 Dashboard available at http://localhost:8000"

# Launch automated demonstrations
echo "🎯 Starting automated gameplay demonstrations..."

# Character Demo
echo "🦸 Running character showcase..."
python -m game_launch.demos.character_demo &

# Meshgear Demo
echo "🎨 Running meshgear preview..."
python -m game_launch.demos.meshgear_demo &

# Governance Demo
echo "🗳️ Running governance simulation..."
python -m game_launch.demos.governance_demo &

# Arena Demo
echo "⚔️ Running arena matches..."
python -m game_launch.demos.arena_demo &

# Marketplace Demo
echo "🏪 Running marketplace simulation..."
python -m game_launch.demos.marketplace_demo &

echo "✨ All demonstrations active!"

# Trap Ctrl+C to gracefully shut down all components
trap 'echo "🛑 Shutting down game systems..."; kill $(jobs -p); exit 0' SIGINT

# Keep script running
wait
