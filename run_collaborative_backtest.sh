#!/bin/bash

# PROTECTED FILE - EPOCHCORE RAS
# Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
# All Rights Reserved

# Collaborative Backtest Runner

echo "🔄 Starting Collaborative Backtest System..."

# Ensure Python environment is active
if [ -z "${VIRTUAL_ENV}" ]; then
    echo "⚠️  No virtual environment detected, checking requirements..."
    if [ ! -f "requirements.txt" ]; then
        echo "❌ requirements.txt not found!"
        exit 1
    fi
    pip install -r requirements.txt
fi

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"

# Create output directory
mkdir -p output/backtest

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="output/backtest/collaborative_backtest_${TIMESTAMP}.json"

echo "📊 Running collaborative backtest..."
echo "Output will be saved to: ${OUTPUT_FILE}"

# Run Python script
python3 - << EOF
import asyncio
import json
from datetime import datetime, timedelta
from collaborative_backtest import CollaborativeBacktest

async def main():
    # Initialize backtest system
    backtest = CollaborativeBacktest()
    
    # Sample backtest data (replace with your actual data)
    backtest_data = {
        'start_date': (datetime.now() - timedelta(days=30)).isoformat(),
        'end_date': datetime.now().isoformat(),
        'parameters': {
            'time_horizon': '30d',
            'resolution': '1h',
            'agents': ['intelligence', 'quantum', 'temporal', 'evolution', 
                      'collaboration', 'resilience', 'ethical', 'self_improve']
        },
        'mode': 'collaborative',
        'synchronization': 'full'
    }
    
    # Run backtest
    print("\n🔍 Running collaborative backtest...")
    results = await backtest.run_backtest(backtest_data, '${OUTPUT_FILE}')
    
    print("\n✅ Backtest completed successfully!")
    print(f"📝 Results saved to: ${OUTPUT_FILE}")
    
    # Display summary
    print("\n📊 Quick Summary:")
    print("-" * 50)
    for phase, data in results.items():
        if isinstance(data, list):
            print(f"{phase}: {len(data)} results")
        elif isinstance(data, dict):
            print(f"{phase}: {len(data.keys())} components")
        else:
            print(f"{phase}: completed")
    print("-" * 50)

# Run async main
asyncio.run(main())
EOF

# Check execution status
if [ $? -eq 0 ]; then
    echo "✨ Collaborative backtest completed successfully!"
else
    echo "❌ Error during backtest execution"
    exit 1
fi

# Add execution to ledger
LEDGER_FILE="ledger/backtest_executions.jsonl"
mkdir -p "$(dirname "$LEDGER_FILE")"
echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"output_file\":\"${OUTPUT_FILE}\",\"status\":\"completed\"}" >> "$LEDGER_FILE"

echo "🔒 Backtest execution logged in ledger"
