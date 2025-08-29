"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class PhaseState:
    id: int
    phase: str
    status: str
    timestamp: float
    dependencies: List[int] = None
    oscillation_hash: Optional[str] = None


class PhaseHandler:
    """Handles phase transitions with oscillation validation"""

    def __init__(self):
        self.states: Dict[int, PhaseState] = {}
        self.oscillation_window = 5  # Match trigger window size

    def _calculate_oscillation_hash(self, state: PhaseState) -> str:
        """Calculate verification hash for oscillation state"""
        data = {
            "id": state.id,
            "phase": state.phase,
            "status": state.status,
            "timestamp": state.timestamp
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def _validate_dependencies(self, state: PhaseState) -> bool:
        """Check if all dependencies are in valid states"""
        if not state.dependencies:
            return True

        for dep_id in state.dependencies:
            if dep_id not in self.states:
                return False
            dep_state = self.states[dep_id]
            if dep_state.status != "ok":
                return False
        return True

    def handle_phase(self, id: int, phase: str, status: str,
                     dependencies: List[int] = None) -> bool:
        """Process a phase transition"""
        # Create or update state
        current_time = time.time()
        state = PhaseState(
            id=id,
            phase=phase,
            status=status,
            timestamp=current_time,
            dependencies=dependencies
        )

        # Validate dependencies
        if not self._validate_dependencies(state):
            return False

        # Special handling for oscillation phases
        if phase == "oscillate":
            if status != "audit":
                return False
            # Calculate verification hash
            state.oscillation_hash = self._calculate_oscillation_hash(state)

        # Update state
        self.states[id] = state
        return True

    def verify_oscillation(self, id: int) -> bool:
        """Verify oscillation state is valid"""
        if id not in self.states:
            return False

        state = self.states[id]
        if state.phase != "oscillate":
            return False

        # Verify hash
        current_hash = self._calculate_oscillation_hash(state)
        return current_hash == state.oscillation_hash
