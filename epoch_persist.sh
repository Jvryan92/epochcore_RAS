#!/bin/bash
# epochALPHA GitHub Persistence Helper
# Ensures that epochALPHA remains accessible across GitHub Codespace sessions only

set -euo pipefail

# Paths - only use GitHub Codespace paths
WORKSPACE_DIR="/workspaces/epochcore_RAS"
PERSIST_DIR="${WORKSPACE_DIR}/.github/epochalpha_state"
STATE_FILE="${PERSIST_DIR}/state.json"
SESSION_FILE="${PERSIST_DIR}/current_session.txt"
BACKUP_DIR="${PERSIST_DIR}/backups"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${BLUE}🔄 epochALPHA GitHub Persistence Helper${NC}"

# Create directories if they don't exist
mkdir -p "${PERSIST_DIR}"
mkdir -p "${BACKUP_DIR}"

# Initialize persistence system if needed
if [ ! -f "${STATE_FILE}" ]; then
    echo -e "${YELLOW}First-time initialization...${NC}"
    
    # Generate a persistence ID
    PERSIST_ID=$(openssl rand -hex 8)
    
    # Create initial session
    SESSION_ID="github-$(date -u +%Y%m%d-%H%M%S)"
    echo "${SESSION_ID}" > "${SESSION_FILE}"
    
    # Create initial state
    cat > "${STATE_FILE}" <<EOF
{
  "version": "1.0.0",
  "initialized_at": "$(date -u -Iseconds)",
  "last_updated": "$(date -u -Iseconds)",
  "session_count": 1,
  "agent_id": "agent://epochALPHA",
  "agent_name": "Quantum Horizon",
  "health_score": 1.0,
  "persistence_id": "${PERSIST_ID}",
  "github_only": true,
  "current_session": "${SESSION_ID}",
  "sessions": {
    "${SESSION_ID}": {
      "started_at": "$(date -u -Iseconds)",
      "platform": "github-codespace",
      "active": true
    }
  }
}
EOF

    echo -e "${GREEN}✅ GitHub persistence initialized with ID: ${PERSIST_ID}${NC}"
else
    # Load existing state
    echo -e "${BLUE}Loading existing GitHub state...${NC}"
    
    # Back up current state before modifying
    cp "${STATE_FILE}" "${BACKUP_DIR}/state-$(date -u +%Y%m%d-%H%M%S).json"
    
    # Create new session
    SESSION_ID="github-$(date -u +%Y%m%d-%H%M%S)"
    echo "${SESSION_ID}" > "${SESSION_FILE}"
    
    # Extract persistence ID
    PERSIST_ID=$(jq -r '.persistence_id' "${STATE_FILE}")
    
    # Update state with new session (using tmp file since we might not have jq)
    TEMP_FILE=$(mktemp)
    cat "${STATE_FILE}" | 
      sed "s/\"session_count\": [0-9]*/\"session_count\": $(( $(jq '.session_count' "${STATE_FILE}") + 1 ))/" |
      sed "s/\"last_updated\": \".*\"/\"last_updated\": \"$(date -u -Iseconds)\"/" |
      sed "s/\"current_session\": \".*\"/\"current_session\": \"${SESSION_ID}\"/" > "${TEMP_FILE}"
    
    # Add the new session
    SESSION_JSON="{\"${SESSION_ID}\": {\"started_at\": \"$(date -u -Iseconds)\", \"platform\": \"github-codespace\", \"active\": true}}"
    TEMP_FILE2=$(mktemp)
    jq --argjson sess "${SESSION_JSON}" '.sessions += $sess' "${TEMP_FILE}" > "${TEMP_FILE2}"
    mv "${TEMP_FILE2}" "${STATE_FILE}"
    rm "${TEMP_FILE}"
    
    echo -e "${GREEN}✅ GitHub session ${SESSION_ID} started${NC}"
fi

# Create a simple status file
cat > "${WORKSPACE_DIR}/epochalpha_status.md" <<EOF
# epochALPHA GitHub Status

- **Persistence ID**: ${PERSIST_ID}
- **Current Session**: ${SESSION_ID}
- **Last Updated**: $(date -u)
- **GitHub-Only Mode**: Enabled

## Reconnection

To reconnect in a new Codespace:

1. Open this repository in a Codespace
2. Run \`./epoch_persist.sh\` to restore the session
3. Run \`python sync_epochALPHA.py\` to sync epochALPHA

## Integration

Add to \`.github/workflows/epochalpha.yml\` to automate persistence across workflow runs.
EOF

echo -e "${GREEN}✅ Created status file at ${WORKSPACE_DIR}/epochalpha_status.md${NC}"

# Create synchronization integration
cat > "${WORKSPACE_DIR}/sync_github.py" <<EOF
#!/usr/bin/env python3
"""
GitHub-specific epochALPHA sync helper
"""
import os
import sys
import json
import datetime
import subprocess
from pathlib import Path

def load_state():
    """Load the current GitHub persistence state"""
    workspace_dir = Path("/workspaces/epochcore_RAS")
    persist_dir = workspace_dir / ".github/epochalpha_state"
    state_file = persist_dir / "state.json"
    
    if not state_file.exists():
        print("❌ No GitHub persistence state found. Run ./epoch_persist.sh first.")
        sys.exit(1)
        
    with open(state_file) as f:
        return json.load(f)

def save_state(state):
    """Save the current GitHub persistence state"""
    workspace_dir = Path("/workspaces/epochcore_RAS")
    persist_dir = workspace_dir / ".github/epochalpha_state"
    state_file = persist_dir / "state.json"
    
    # Create a backup
    backup_dir = persist_dir / "backups"
    backup_dir.mkdir(exist_ok=True)
    backup_file = backup_dir / f"state-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    
    with open(backup_file, "w") as f:
        json.dump(state, f, indent=2)
        
    # Save the new state
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)
    
    return True

def run_sync():
    """Run the main sync with GitHub-specific flags"""
    print("🔄 Running GitHub-specific epochALPHA sync...")
    result = subprocess.run(["python", "sync_epochALPHA.py"], 
                           capture_output=True, text=True)
    
    # Update the state with sync results
    state = load_state()
    state["last_sync"] = datetime.datetime.now().isoformat()
    state["last_sync_status"] = "success" if result.returncode == 0 else "failure"
    
    if "sync_history" not in state:
        state["sync_history"] = []
        
    state["sync_history"].append({
        "timestamp": datetime.datetime.now().isoformat(),
        "session_id": state.get("current_session"),
        "status": "success" if result.returncode == 0 else "failure",
        "output_lines": len(result.stdout.splitlines())
    })
    
    # Keep only the last 10 sync history items
    if len(state["sync_history"]) > 10:
        state["sync_history"] = state["sync_history"][-10:]
    
    save_state(state)
    
    # Print the output
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"❌ Sync failed with exit code {result.returncode}")
        print(result.stderr)
        return False
        
    return True

if __name__ == "__main__":
    # Check if state exists
    workspace_dir = Path("/workspaces/epochcore_RAS")
    persist_dir = workspace_dir / ".github/epochalpha_state"
    state_file = persist_dir / "state.json"
    
    if not state_file.exists():
        print("❌ GitHub persistence not initialized. Run ./epoch_persist.sh first.")
        sys.exit(1)
    
    # Run the sync
    run_sync()
    
    # Show status
    state = load_state()
    print(f"\n📊 epochALPHA GitHub Status:")
    print(f"  - Persistence ID: {state.get('persistence_id', 'unknown')}")
    print(f"  - Current Session: {state.get('current_session', 'unknown')}")
    print(f"  - Sessions: {state.get('session_count', 0)}")
    print(f"  - Last Sync: {state.get('last_sync', 'never')}")
    print(f"  - Sync Status: {state.get('last_sync_status', 'unknown')}")
    print(f"  - Health Score: {state.get('health_score', 0.0)}")
EOF

chmod +x "${WORKSPACE_DIR}/sync_github.py"
echo -e "${GREEN}✅ Added GitHub-specific sync integration${NC}"
echo -e "${BLUE}📋 To sync epochALPHA in GitHub only mode:${NC}"
echo -e "   1. Run ${YELLOW}./epoch_persist.sh${NC} to initialize/restore the session"
echo -e "   2. Run ${YELLOW}python sync_github.py${NC} to sync with GitHub-specific settings"
echo -e ""
echo -e "${GREEN}🌐 epochALPHA GitHub persistence active - session: ${SESSION_ID}${NC}"
