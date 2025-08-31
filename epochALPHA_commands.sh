#!/bin/bash
# epochALPHA Command Suite
# Created: August 30, 2025
# Description: A collection of useful commands for working with epochALPHA

# Basic sync operation
echo "🔄 Running basic epochALPHA sync..."
python sync_epochALPHA.py

# Check MESH wallet status
echo -e "\n💰 Checking MESH wallet status..."
python sync_epochALPHA.py --mesh-wallet

# Visualize MESH networks
echo -e "\n📊 Generating MESH network visualizations..."
python sync_epochALPHA.py --mesh-visualize

# Execute specific MESH goals
echo -e "\n🌐 Executing MESH goal: drip.signal..."
python sync_epochALPHA.py --mesh-goal drip.signal

echo -e "\n🌐 Executing MESH goal: pulse.sync..."
python sync_epochALPHA.py --mesh-goal pulse.sync

echo -e "\n🌐 Executing MESH goal: weave.bind..."
python sync_epochALPHA.py --mesh-goal weave.bind

# Generate StrategyDECK icons
echo -e "\n🎨 Generating StrategyDECK icons..."
python scripts/generate_icons.py

# epochMESHOPERATER operations
echo -e "\n🤖 epochMESHOPERATER - Advanced Mesh Operations..."

# Single goal execution with enhanced tracking
echo -e "\n🎯 epochMESHOPERATER single goal execution..."
python epochMESHOPERATER.py --goal drip.signal

# Batch goal execution with parallel processing
echo -e "\n🚀 epochMESHOPERATER batch execution..."
python epochMESHOPERATER.py --batch-goals drip.signal pulse.sync weave.bind --parallel

# Mesh health monitoring
echo -e "\n🩺 epochMESHOPERATER health check..."
python epochMESHOPERATER.py --health

# Mesh topology optimization
echo -e "\n🔧 epochMESHOPERATER optimization..."
python epochMESHOPERATER.py --optimize

# Autonomous mode (commented out by default - uncomment to use)
# echo -e "\n🤖 Running in autonomous mode (5 minutes)..."
# python sync_epochALPHA.py --autonomous --duration 5 --interval 30

echo -e "\n✨ All commands completed!"
