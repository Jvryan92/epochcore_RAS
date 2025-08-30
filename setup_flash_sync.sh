#!/bin/bash
# Agent Flash Sync Quick Setup
# This script sets up the entire agent flash sync system

set -euo pipefail

echo "🔄 Setting up Agent Flash Sync System..."

# Create necessary directories
mkdir -p logs sync_results dashboard/templates dashboard/reports

# Make scripts executable
chmod +x flash_sync_agents.py schedule_flash_sync.py agent_dashboard.py

# Install dependencies
echo "📦 Installing dependencies..."
pip install flask pandas matplotlib

# Run initial sync
echo "⚡ Running initial flash sync..."
python3 flash_sync_agents.py

# Set up the dashboard
echo "🖥️  Setting up dashboard..."
python3 agent_dashboard.py &
DASHBOARD_PID=$!

# Wait for dashboard to start
sleep 2

echo "
✅ Setup complete!

🔄 Flash Sync system is now ready:
   - Manual sync: python3 flash_sync_agents.py
   - Scheduled syncs: python3 schedule_flash_sync.py
   - Dashboard: http://localhost:5000 (running in background)

📋 For more information, see AGENT_SYNC_README.md
"

# Optional: kill dashboard after setup
read -p "Press Enter to stop the dashboard and exit..." 
kill $DASHBOARD_PID
