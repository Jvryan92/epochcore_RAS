#!/bin/bash

# EpochCore RAS - Automated Demo Launch Script
echo "🚀 Launching EpochCore RAS Automated Demonstrations"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Start the dashboard
echo "🎮 Starting demonstration dashboard..."
python -m saas_verticals.automation.dashboard &
DASHBOARD_PID=$!

# Initialize system metrics collection
echo "📊 Initializing metrics collection..."
mkdir -p logs/metrics

# Launch vertical demonstrations in parallel
echo "✨ Launching vertical demonstrations..."

# AuditTrail Demo
echo "🔐 Launching AuditTrail-as-a-Service demo..."
python -m saas_verticals.automation.verticals.audittrail &

# DriftSentinel Demo
echo "🎯 Launching DriftSentinel demo..."
python -m saas_verticals.automation.verticals.driftsentinel &

# ProofSync Demo
echo "⚡ Launching ProofSync demo..."
python -m saas_verticals.automation.verticals.proofsync &

# Governance Demo
echo "🏛️ Launching Governance Capsule demo..."
python -m saas_verticals.automation.verticals.governance &

# Inheritor Demo
echo "🔒 Launching Inheritor Vault demo..."
python -m saas_verticals.automation.verticals.inheritor &

# Widget Demo
echo "🎨 Launching Capsule Widget demo..."
python -m saas_verticals.automation.verticals.widget &

# BusyWork Demo
echo "⚙️ Launching BusyWork Automator demo..."
python -m saas_verticals.automation.verticals.busywork &

# ScrollSync Demo
echo "📜 Launching ScrollSync demo..."
python -m saas_verticals.automation.verticals.scrollsync &

# FlashSale Demo
echo "🏷️ Launching FlashSale demo..."
python -m saas_verticals.automation.verticals.flashsale &

# Shield Demo
echo "🛡️ Launching EPOCH Shield demo..."
python -m saas_verticals.automation.verticals.shield &

echo "✅ All demonstrations launched!"
echo "📱 Dashboard available at http://localhost:8000"

# Trap Ctrl+C to gracefully shut down all demos
trap 'echo "🛑 Shutting down demonstrations..."; kill $(jobs -p); exit 0' SIGINT

# Keep script running
wait
