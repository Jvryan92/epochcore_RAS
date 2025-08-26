#!/bin/bash
# EPOCH5 Enhanced Ceiling Management System Launcher
# Provides quick access to all ceiling-related features

echo "🏗️ EPOCH5 Enhanced Ceiling Management System"
echo "=============================================="
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if the system is initialized
if [ ! -d "archive/EPOCH5" ]; then
    echo "🔧 Initializing EPOCH5 system..."
    python3 integration.py setup-demo
    echo ""
fi

# Display menu
echo "Select an option:"
echo "1) 📊 Launch Real-time Ceiling Dashboard"
echo "2) 💰 Show Service Tier Pricing"
echo "3) 🔧 Create Ceiling Configuration"
echo "4) 📈 View Performance Status"
echo "5) 🎯 Get Upgrade Recommendations"
echo "6) 🖥️  System Status Overview"
echo "7) 🚀 Run Complete Demo Workflow"
echo "0) Exit"
echo ""

read -p "Enter your choice: " choice

case $choice in
    1)
        echo "🌐 Starting Ceiling Dashboard on http://localhost:8080..."
        python3 ceiling_dashboard.py
        ;;
    2)
        echo "💰 Service Tier Pricing Information:"
        python3 integration.py ceilings tiers
        ;;
    3)
        read -p "Enter configuration ID: " config_id
        echo "Select service tier:"
        echo "1) Freemium ($0/month)"
        echo "2) Professional ($49.99/month)" 
        echo "3) Enterprise ($199.99/month)"
        read -p "Choose tier (1-3): " tier_choice
        
        case $tier_choice in
            1) tier="freemium" ;;
            2) tier="professional" ;;
            3) tier="enterprise" ;;
            *) tier="freemium" ;;
        esac
        
        python3 integration.py ceilings create "$config_id" --tier "$tier"
        ;;
    4)
        echo "📈 Current System Performance Status:"
        python3 integration.py status
        echo ""
        echo "Detailed Ceiling Configurations:"
        python3 integration.py ceilings list
        ;;
    5)
        read -p "Enter configuration ID: " config_id
        echo "🎯 Upgrade Recommendations:"
        python3 integration.py ceilings upgrade-rec "$config_id"
        ;;
    6)
        echo "🖥️ Complete System Overview:"
        python3 integration.py status
        ;;
    7)
        echo "🚀 Running Complete EPOCH5 Workflow..."
        python3 integration.py run-workflow
        ;;
    0)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please try again."
        ;;
esac