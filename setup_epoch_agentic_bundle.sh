"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/bin/bash

# Create folder structure
mkdir -p epoch_agentic_bundle/agents

# agent_self_register.py
cat > epoch_agentic_bundle/agents/agent_self_register.py <<'EOF'
import json
import os

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "agent_registry.json")

def register_agent(agent_id, agent_role, status, last_action, registry_path=REGISTRY_PATH):
    if not os.path.isfile(registry_path):
        registry = {}
    else:
        with open(registry_path, "r") as f:
            registry = json.load(f)
    registry[agent_id] = {
        "role": agent_role,
        "status": status,
        "last_action": last_action
    }
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)

def log_action(agent_id, action, registry_path=REGISTRY_PATH):
    if not os.path.isfile(registry_path):
        registry = {}
    else:
        with open(registry_path, "r") as f:
            registry = json.load(f)
    if agent_id in registry:
        registry[agent_id]["last_action"] = action
        with open(registry_path, "w") as f:
            json.dump(registry, f, indent=2)
    else:
        raise ValueError(f"Agent {agent_id} not registered yet.")
EOF

# agent_register_sync.py
cat > epoch_agentic_bundle/agents/agent_register_sync.py <<'EOF'
import os
import sys

sys.path.append(os.path.dirname(__file__))
from agent_self_register import register_agent, log_action

def sync_agent_registry():
    agent_id = os.getenv("AGENT_ID")
    agent_role = os.getenv("AGENT_ROLE")
    if not agent_id:
        agent_id = input("Enter this agent's name (AGENT_ID): ")
    if not agent_role:
        agent_role = input("Enter this agent's role (AGENT_ROLE): ")
    last_action = "auto-sync thread"
    register_agent(agent_id, agent_role, "active", last_action)
    log_action(agent_id, "sync", os.path.join(os.path.dirname(__file__), "agent_registry.json"))

if __name__ == "__main__":
    sync_agent_registry()
EOF

# epochroot_log_self.py
cat > epoch_agentic_bundle/agents/epochroot_log_self.py <<'EOF'
import os
import sys

sys.path.append(os.path.dirname(__file__))
from agent_self_register import register_agent, log_action

def log_epochroot():
    agent_id = "epochroot"
    agent_role = "root orchestrator, governance, audit, registry"
    last_action = "self-log"
    register_agent(agent_id, agent_role, "active", last_action)
    log_action(agent_id, "self-log", os.path.join(os.path.dirname(__file__), "agent_registry.json"))

if __name__ == "__main__":
    log_epochroot()
EOF

# agent_registry.json
echo '{}' > epoch_agentic_bundle/agents/agent_registry.json

# registry_audit.py
cat > epoch_agentic_bundle/registry_audit.py <<'EOF'
import json
import os

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), "agents/agent_registry.json")

def audit_registry():
    if not os.path.isfile(REGISTRY_PATH):
        print("No registry found.")
        return
    with open(REGISTRY_PATH, "r") as f:
        registry = json.load(f)
    print("=== Agent Registry Audit ===")
    for aid, info in registry.items():
        print(f"Agent: {aid}\n  Role: {info['role']}\n  Status: {info['status']}\n  Last Action: {info['last_action']}\n")

if __name__ == "__main__":
    audit_registry()
EOF

# README.md
cat > epoch_agentic_bundle/README.md <<'EOF'
# EPOCH Agentic Governance Bundle

Everything you need for automated agent onboarding, registry, and audit.

## Usage

1. **Register an agent:**  
   `python agents/agent_register_sync.py` (Set AGENT_ID and AGENT_ROLE env vars for automation, or enter values when prompted.)

2. **Log epochroot:**  
   `python agents/epochroot_log_self.py`

3. **Audit the registry:**  
   `python registry_audit.py`

---
All files live in `epoch_agentic_bundle/` for easy review, update, or removal.
EOF

# manifest.yaml
cat > epoch_agentic_bundle/manifest.yaml <<'EOF'
bundle: epoch_agentic_bundle
description: >
  Automated agentic governance bundle for epoch5-template.
files:
  - agents/agent_self_register.py
  - agents/agent_register_sync.py
  - agents/epochroot_log_self.py
  - agents/agent_registry.json
  - registry_audit.py
  - README.md
maintainer: "epochroot"
created: "2025-08-28"
provenance: "Generated and consolidated by Copilot, with Jvryan92 approval."
EOF

echo "✅ epoch_agentic_bundle is created and ready to use."
