#!/bin/bash
# StrategyDECK Epoch Runner
# This script initializes and runs the EpochCore RAS system with StrategyDECK integration

set -e

# ANSI color codes for prettier output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}   StrategyDECK Epoch Runner        ${NC}"
echo -e "${BLUE}=====================================${NC}"

# Configuration
PYTHON_PATH="/workspaces/epochcore_RAS/.venv/bin/python"
CONFIG_DIR="./config"
AGENTS_DIR="./agents"
LOG_DIR="./logs"
ASSETS_DIR="./assets"

# Create required directories
mkdir -p "$CONFIG_DIR" "$AGENTS_DIR" "$LOG_DIR"

# Functions
function check_dependencies() {
    echo -e "\n${YELLOW}Checking dependencies...${NC}"
    
    if [ ! -f "$PYTHON_PATH" ]; then
        echo -e "${RED}Error: Python virtual environment not found at $PYTHON_PATH${NC}"
        echo -e "${YELLOW}Running setup script...${NC}"
        ./setup_epochcore_ras.sh
        
        if [ ! -f "$PYTHON_PATH" ]; then
            echo -e "${RED}Setup failed. Please set up the environment manually.${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✓ Dependencies checked${NC}"
}

function generate_icons() {
    echo -e "\n${YELLOW}Generating StrategyDECK icons...${NC}"
    ./generate_strategydeck.sh --clean
    echo -e "${GREEN}✓ Icons generated${NC}"
}

function sync_assets() {
    echo -e "\n${YELLOW}Syncing assets with game and SaaS products...${NC}"
    "$PYTHON_PATH" strategydeck_game_assets_connector.py update-shared
    "$PYTHON_PATH" strategydeck_game_assets_connector.py sync
    echo -e "${GREEN}✓ Assets synced${NC}"
}

function launch_agents() {
    echo -e "\n${YELLOW}Launching EpochCore agents...${NC}"
    
    # Initialize agent system
    ./epoch_agent_charter.sh --init
    
    # Start individual agent channels
    echo -e "${CYAN}Starting Intelligence channel...${NC}"
    "$PYTHON_PATH" strategy_intelligence.py &
    
    echo -e "${CYAN}Starting Resilience channel...${NC}"
    "$PYTHON_PATH" strategy_resilience.py &
    
    echo -e "${CYAN}Starting Collaboration channel...${NC}"
    "$PYTHON_PATH" strategy_collaboration.py &
    
    echo -e "${CYAN}Starting Evolution channel...${NC}"
    "$PYTHON_PATH" strategy_evolution.py &
    
    echo -e "${CYAN}Starting Quantum channel...${NC}"
    "$PYTHON_PATH" strategy_quantum.py &
    
    echo -e "${CYAN}Starting Cognitive channel...${NC}"
    "$PYTHON_PATH" strategy_cognitive.py &
    
    echo -e "${CYAN}Starting Ethical channel...${NC}"
    "$PYTHON_PATH" strategy_ethical.py &
    
    echo -e "${CYAN}Starting Temporal channel...${NC}"
    "$PYTHON_PATH" strategy_temporal.py &
    
    echo -e "${GREEN}✓ All agent channels started${NC}"
}

function monitor_system() {
    echo -e "\n${YELLOW}Starting system monitoring...${NC}"
    "$PYTHON_PATH" ceiling_dashboard.py &
    echo -e "${GREEN}✓ Monitoring started${NC}"
}

# Main execution
check_dependencies
generate_icons
sync_assets

# Launch agent system
launch_agents
monitor_system

echo -e "\n${BLUE}=====================================${NC}"
echo -e "${GREEN}EpochCore RAS with StrategyDECK is now running!${NC}"
echo -e "${YELLOW}Use Ctrl+C to stop all agents${NC}"
echo -e "${BLUE}=====================================${NC}"

# Wait for user to stop the system
wait
