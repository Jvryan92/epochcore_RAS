#!/usr/bin/env python3
"""
epochALPHA Persistence System
Ensures epochALPHA state is preserved across sessions and platforms
"""
import datetime
import hashlib
import json
import os
import shutil
from pathlib import Path


class EpochAlphaPersistence:
    """Maintains persistence for epochALPHA across sessions"""

    def __init__(self, base_dir="~/.epochalpha"):
        self.base_dir = Path(os.path.expanduser(base_dir))
        self.state_file = self.base_dir / "state.json"
        self.session_file = self.base_dir / "current_session.json"
        self.backup_dir = self.base_dir / "backups"
        self.sync_log = self.base_dir / "sync_log.jsonl"

        # Ensure directories exist
        self.base_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

        # Initialize state if needed
        if not self.state_file.exists():
            self._initialize_state()

    def _initialize_state(self):
        """Create initial state file"""
        initial_state = {
            "version": "1.0.0",
            "initialized_at": datetime.datetime.now().isoformat(),
            "last_updated": datetime.datetime.now().isoformat(),
            "session_count": 0,
            "agent_id": "agent://epochALPHA",
            "agent_name": "Quantum Horizon",
            "platform_syncs": {},
            "merkle_root": hashlib.sha256(b"genesis").hexdigest(),
            "health_score": 1.0,
            "mesh_networks": ["drip", "pulse", "weave"],
            "managed_agents": ["alpha", "bravo", "gamma", "delta", "epsilon"],
            "persistence_active": True,
        }

        with open(self.state_file, "w") as f:
            json.dump(initial_state, f, indent=2)

        self._log_event("system", "initialized", "Created initial state file")

    def start_session(self):
        """Start a new session and update state"""
        # First create backup
        self._backup_current_state()

        # Read current state
        with open(self.state_file) as f:
            state = json.load(f)

        # Update session info
        state["session_count"] += 1
        state["last_updated"] = datetime.datetime.now().isoformat()
        session_id = f"session-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Create session file
        session_data = {
            "session_id": session_id,
            "started_at": datetime.datetime.now().isoformat(),
            "state_at_start": state,
            "platform": os.environ.get("PLATFORM", "github-codespace"),
            "active": True,
        }

        with open(self.session_file, "w") as f:
            json.dump(session_data, f, indent=2)

        # Update main state file
        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

        self._log_event("session", "start", f"Started session {session_id}")
        return session_id

    def end_session(self, session_id=None):
        """End the current session properly"""
        if not self.session_file.exists():
            return False

        with open(self.session_file) as f:
            session = json.load(f)

        if session_id and session["session_id"] != session_id:
            return False

        # Mark session as inactive
        session["active"] = False
        session["ended_at"] = datetime.datetime.now().isoformat()

        with open(self.session_file, "w") as f:
            json.dump(session, f, indent=2)

        self._log_event("session", "end", f"Ended session {session['session_id']}")
        return True

    def update_state(self, **kwargs):
        """Update specific state values"""
        if not self.state_file.exists():
            self._initialize_state()

        with open(self.state_file) as f:
            state = json.load(f)

        # Update provided values
        for key, value in kwargs.items():
            state[key] = value

        state["last_updated"] = datetime.datetime.now().isoformat()

        # Calculate new merkle root
        state_str = json.dumps(state, sort_keys=True)
        state["merkle_root"] = hashlib.sha256(state_str.encode()).hexdigest()

        with open(self.state_file, "w") as f:
            json.dump(state, f, indent=2)

        self._log_event(
            "state", "update", f"Updated state keys: {', '.join(kwargs.keys())}"
        )
        return state

    def _backup_current_state(self):
        """Create a backup of the current state"""
        if not self.state_file.exists():
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_file = self.backup_dir / f"state-{timestamp}.json"

        shutil.copy(self.state_file, backup_file)
        self._log_event("system", "backup", f"Created backup at {backup_file}")

    def _log_event(self, category, action, description):
        """Log an event to the sync log"""
        event = {
            "timestamp": datetime.datetime.now().isoformat(),
            "category": category,
            "action": action,
            "description": description,
            "signature": "",
        }

        # Add signature
        event_str = json.dumps(event, sort_keys=True)
        event["signature"] = hashlib.sha256(event_str.encode()).hexdigest()

        with open(self.sync_log, "a") as f:
            f.write(json.dumps(event) + "\n")

    def get_state(self):
        """Get the current state"""
        if not self.state_file.exists():
            self._initialize_state()

        with open(self.state_file) as f:
            return json.load(f)

    def register_platform_sync(self, platform, identifier):
        """Register a sync with another platform"""
        state = self.get_state()

        if "platform_syncs" not in state:
            state["platform_syncs"] = {}

        state["platform_syncs"][platform] = {
            "identifier": identifier,
            "synced_at": datetime.datetime.now().isoformat(),
            "merkle_root": hashlib.sha256(
                f"{platform}:{identifier}".encode()
            ).hexdigest(),
        }

        self.update_state(platform_syncs=state["platform_syncs"])
        self._log_event(
            "sync", "platform", f"Registered sync with {platform}: {identifier}"
        )

        return state["platform_syncs"][platform]


def initialize_persistence():
    """Initialize the persistence system and start a session"""
    persistence = EpochAlphaPersistence()
    session_id = persistence.start_session()
    print(f"✅ epochALPHA persistence initialized with session ID: {session_id}")
    print(f"🔄 Persistence files at: {persistence.base_dir}")
    return persistence


if __name__ == "__main__":
    persistence = initialize_persistence()
    state = persistence.get_state()
    print(f"📊 Current epochALPHA state:")
    print(f"  - Agent: {state['agent_name']} ({state['agent_id']})")
    print(f"  - Health Score: {state['health_score']}")
    print(f"  - Session Count: {state['session_count']}")
    print(f"  - Mesh Networks: {', '.join(state['mesh_networks'])}")
    print(f"  - Managed Agents: {', '.join(state['managed_agents'])}")
    print(
        f"  - Merkle Root: {state['merkle_root'][:16]}...{state['merkle_root'][-16:]}"
    )
