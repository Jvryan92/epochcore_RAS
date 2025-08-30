#!/bin/bash
# =========================================================================
# EPOCH Agent Charter Script
# A comprehensive script to initialize, configure, and launch agents within
# the EpochCore RAS (Recursive Autonomous Software) framework.
# =========================================================================

set -e

# Directory setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$SCRIPT_DIR"
AGENT_DIR="$BASE_DIR/agent_prompts"
LOG_DIR="$BASE_DIR/logs"
CONFIG_DIR="$BASE_DIR/.config"
CAPSULE_DIR="$BASE_DIR/capsules"

# Create required directories
mkdir -p "$LOG_DIR" "$CONFIG_DIR" "$CAPSULE_DIR"

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Log file
LOG_FILE="$LOG_DIR/agent_charter_$(date +%Y%m%d_%H%M%S).log"

# Logging function
log() {
    local level="$1"
    local message="$2"
    local color="$NC"
    
    case "$level" in
        "INFO") color="$GREEN" ;;
        "WARN") color="$YELLOW" ;;
        "ERROR") color="$RED" ;;
        "DEBUG") color="$CYAN" ;;
    esac
    
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $message${NC}" | tee -a "$LOG_FILE"
}

# Display banner
display_banner() {
    echo -e "${BLUE}=======================================================${NC}"
    echo -e "${BLUE}  ███████╗██████╗  ██████╗  ██████╗██╗  ██╗ ${NC}"
    echo -e "${BLUE}  ██╔════╝██╔══██╗██╔═══██╗██╔════╝██║  ██║ ${NC}"
    echo -e "${BLUE}  █████╗  ██████╔╝██║   ██║██║     ███████║ ${NC}"
    echo -e "${BLUE}  ██╔══╝  ██╔═══╝ ██║   ██║██║     ██╔══██║ ${NC}"
    echo -e "${BLUE}  ███████╗██║     ╚██████╔╝╚██████╗██║  ██║ ${NC}"
    echo -e "${BLUE}  ╚══════╝╚═╝      ╚═════╝  ╚═════╝╚═╝  ╚═╝ ${NC}"
    echo -e "${BLUE}                                           ${NC}"
    echo -e "${BLUE}   Agent Charter System - EpochCore RAS    ${NC}"
    echo -e "${BLUE}=======================================================${NC}"
    echo ""
}

# Check dependencies
check_dependencies() {
    log "INFO" "Checking dependencies..."
    
    local missing_deps=0
    local deps=("python3" "pip3" "jq" "curl")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log "ERROR" "Missing dependency: $dep"
            missing_deps=$((missing_deps + 1))
        fi
    done
    
    # Check Python dependencies
    if ! pip3 list | grep -q "numpy"; then
        log "WARN" "Python dependency 'numpy' not found. Installing..."
        pip3 install numpy
    fi
    
    if ! pip3 list | grep -q "networkx"; then
        log "WARN" "Python dependency 'networkx' not found. Installing..."
        pip3 install networkx
    fi
    
    if [ $missing_deps -gt 0 ]; then
        log "ERROR" "$missing_deps dependencies are missing. Please install them and try again."
        return 1
    fi
    
    log "INFO" "All dependencies satisfied."
    return 0
}

# Initialize agent configuration
initialize_agent_config() {
    local agent_type="$1"
    local agent_name="$2"
    
    log "INFO" "Initializing $agent_name ($agent_type) configuration..."
    
    # Create agent config file
    cat > "$CONFIG_DIR/${agent_type}_config.json" << EOF
{
    "agent_name": "$agent_name",
    "agent_type": "$agent_type",
    "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "prompt_path": "$AGENT_DIR/${agent_type}_agent_prompt.md",
    "capabilities": [
        "strategy_planning",
        "resource_optimization",
        "task_execution",
        "self_improvement"
    ],
    "collaboration_mode": "autonomous",
    "ethical_constraints": {
        "enable_ethical_checks": true,
        "require_impact_assessment": true,
        "stakeholder_consideration": true
    },
    "performance_metrics": {
        "success_rate": 0.0,
        "average_latency": 0.0,
        "total_tasks": 0,
        "successful_tasks": 0
    }
}
EOF
    
    log "INFO" "$agent_name configuration created successfully."
}

# Register agent with the management system
register_agent() {
    local agent_type="$1"
    
    log "INFO" "Registering $agent_type agent with management system..."
    
    # Extract capabilities from config
    local capabilities=$(jq -r '.capabilities | join(" ")' "$CONFIG_DIR/${agent_type}_config.json")
    
    # Call the agent management script to register the agent
    python3 -c "
import sys
sys.path.insert(0, '$BASE_DIR')
from agent_management import AgentManager
manager = AgentManager()
agent = manager.create_agent(['$capabilities'], '$agent_type')
success = manager.register_agent(agent)
print(f'Agent registered with DID: {agent[\"did\"]}')
" || {
        log "ERROR" "Failed to register $agent_type agent."
        return 1
    }
    
    log "INFO" "$agent_type agent registered successfully."
    return 0
}

# Create a meta capsule for agent state preservation
create_meta_capsule() {
    local agent_type="$1"
    
    log "INFO" "Creating meta capsule for $agent_type agent..."
    
    python3 -c "
import sys
sys.path.insert(0, '$BASE_DIR')
from meta_capsule import create_capsule
from datetime import datetime
create_capsule(
    agent_type='$agent_type',
    timestamp=datetime.now().isoformat(),
    capsule_dir='$CAPSULE_DIR'
)
" || {
        log "ERROR" "Failed to create meta capsule for $agent_type agent."
        return 1
    }
    
    log "INFO" "Meta capsule created successfully for $agent_type agent."
    return 0
}

# Launch agent
launch_agent() {
    local agent_type="$1"
    
    log "INFO" "Launching $agent_type agent..."
    
    # Extract agent name from config
    local agent_name=$(jq -r '.agent_name' "$CONFIG_DIR/${agent_type}_config.json")
    
    python3 "$BASE_DIR/strategydeck_agent.py" \
        --agent-type "$agent_type" \
        --config-path "$CONFIG_DIR/${agent_type}_config.json" \
        --log-dir "$LOG_DIR" \
        --capsule-dir "$CAPSULE_DIR" || {
        log "ERROR" "Failed to launch $agent_type agent."
        return 1
    }
    
    log "INFO" "$agent_name ($agent_type) launched successfully."
    return 0
}

# Verify agent prompt exists
verify_agent_prompt() {
    local agent_type="$1"
    local prompt_file="$AGENT_DIR/${agent_type}_agent_prompt.md"
    
    if [ ! -f "$prompt_file" ]; then
        log "ERROR" "Agent prompt file not found: $prompt_file"
        return 1
    fi
    
    log "INFO" "Agent prompt verified: $prompt_file"
    return 0
}

# Main function to charter and launch an agent
charter_agent() {
    local agent_type="$1"
    local agent_name="$2"
    
    log "INFO" "Chartering $agent_name ($agent_type) agent..."
    
    # Verify prompt exists
    verify_agent_prompt "$agent_type" || return 1
    
    # Initialize configuration
    initialize_agent_config "$agent_type" "$agent_name" || return 1
    
    # Register with management system
    register_agent "$agent_type" || return 1
    
    # Create meta capsule
    create_meta_capsule "$agent_type" || return 1
    
    # Launch agent
    launch_agent "$agent_type" || return 1
    
    log "INFO" "$agent_name ($agent_type) agent chartered successfully."
    return 0
}

# Charter multiple agents
charter_agents() {
    local agents=(
        "cognitive:Strategic Cognitive Agent"
        "ethical:Ethical Decision Engine"
        "evolution:Autonomous Evolution Agent"
        "quantum:Quantum Architecture Agent"
        "resilience:System Resilience Agent"
    )
    
    local success_count=0
    local total_agents=${#agents[@]}
    
    for agent_pair in "${agents[@]}"; do
        IFS=':' read -r agent_type agent_name <<< "$agent_pair"
        
        charter_agent "$agent_type" "$agent_name"
        if [ $? -eq 0 ]; then
            success_count=$((success_count + 1))
        fi
        
        # Sleep briefly between agent launches to prevent race conditions
        sleep 2
    done
    
    log "INFO" "Chartered $success_count out of $total_agents agents successfully."
    
    if [ $success_count -eq $total_agents ]; then
        return 0
    else
        return 1
    fi
}

# Function to initialize the StrategyDECK icons
initialize_icons() {
    log "INFO" "Initializing StrategyDECK icons..."
    
    # Check if icon generation script exists
    if [ ! -f "$BASE_DIR/scripts/generate_icons.py" ]; then
        log "ERROR" "Icon generation script not found: $BASE_DIR/scripts/generate_icons.py"
        return 1
    fi
    
    # Generate icons
    python3 "$BASE_DIR/scripts/generate_icons.py" || {
        log "ERROR" "Failed to generate StrategyDECK icons."
        return 1
    }
    
    log "INFO" "StrategyDECK icons generated successfully."
    return 0
}

# Show help message
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help               Show this help message"
    echo "  -a, --all                Charter all agents"
    echo "  -t, --type TYPE          Charter a specific agent type"
    echo "  -n, --name NAME          Specify the agent name (required with -t)"
    echo "  -i, --icons              Generate StrategyDECK icons"
    echo "  -c, --check              Check dependencies only"
    echo ""
    echo "Agent Types:"
    echo "  cognitive                Strategic Cognitive Agent"
    echo "  ethical                  Ethical Decision Engine"
    echo "  evolution                Autonomous Evolution Agent"
    echo "  quantum                  Quantum Architecture Agent"
    echo "  resilience               System Resilience Agent"
    echo ""
    echo "Examples:"
    echo "  $0 --all                 Charter all agent types"
    echo "  $0 --type cognitive --name 'My Cognitive Agent'"
    echo "  $0 --icons               Generate only StrategyDECK icons"
    echo ""
}

# Main execution
main() {
    # Parse command line arguments
    local charter_all=false
    local charter_specific=false
    local agent_type=""
    local agent_name=""
    local generate_icons=false
    local check_deps_only=false
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_help
                exit 0
                ;;
            -a|--all)
                charter_all=true
                shift
                ;;
            -t|--type)
                charter_specific=true
                agent_type="$2"
                shift 2
                ;;
            -n|--name)
                agent_name="$2"
                shift 2
                ;;
            -i|--icons)
                generate_icons=true
                shift
                ;;
            -c|--check)
                check_deps_only=true
                shift
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Display banner
    display_banner
    
    # Check dependencies
    check_dependencies || exit 1
    
    # If only checking dependencies, exit now
    if [ "$check_deps_only" = true ]; then
        log "INFO" "Dependency check completed successfully."
        exit 0
    fi
    
    # Generate icons if requested
    if [ "$generate_icons" = true ]; then
        initialize_icons
    fi
    
    # Charter specific agent if requested
    if [ "$charter_specific" = true ]; then
        if [ -z "$agent_name" ]; then
            log "ERROR" "Agent name is required when chartering a specific agent type."
            show_help
            exit 1
        fi
        
        charter_agent "$agent_type" "$agent_name"
        exit $?
    fi
    
    # Charter all agents if requested
    if [ "$charter_all" = true ]; then
        charter_agents
        exit $?
    fi
    
    # If no specific action was requested, show help
    if [ "$charter_all" = false ] && [ "$charter_specific" = false ] && [ "$generate_icons" = false ]; then
        show_help
        exit 0
    fi
    
    log "INFO" "All operations completed successfully."
    exit 0
}

# Run main function
main "$@"
