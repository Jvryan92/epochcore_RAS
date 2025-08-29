#!/bin/bash

# Source environment variables
source /workspaces/epochcore_RAS/scripts/mesh/.env

# Start reminder daemon
while true; do
    current_hour=$(date +%H)
    current_min=$(date +%M)
    
    # 9 AM Check
    if [ "$current_hour" -eq "09" ] && [ "$current_min" -eq "00" ]; then
        PYTHONPATH=/workspaces/epochcore_RAS python3 /workspaces/epochcore_RAS/scripts/mesh/daily_reminder.py
        sleep 60
    fi
    
    # 12 PM Check
    if [ "$current_hour" -eq "12" ] && [ "$current_min" -eq "00" ]; then
        PYTHONPATH=/workspaces/epochcore_RAS python3 /workspaces/epochcore_RAS/scripts/mesh/daily_reminder.py
        sleep 60
    fi
    
    # 5 PM Check
    if [ "$current_hour" -eq "17" ] && [ "$current_min" -eq "00" ]; then
        PYTHONPATH=/workspaces/epochcore_RAS python3 /workspaces/epochcore_RAS/scripts/mesh/daily_reminder.py
        sleep 60
    fi
    
    sleep 30
done
