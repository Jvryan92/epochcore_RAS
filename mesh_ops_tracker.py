"""
MeshCredit Enhanced Operations Logger
Tracks all system changes and strategic decisions
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class MeshOpsTracker:
    def __init__(self):
        self.log_dir = Path("mesh_ops_logs")
        self.log_dir.mkdir(exist_ok=True)

        # Set up logging
        self.logger = logging.getLogger("MeshOps")
        self.logger.setLevel(logging.INFO)

        # File handler for detailed logs
        fh = logging.FileHandler(self.log_dir / "mesh_ops.log")
        fh.setLevel(logging.INFO)

        # Console handler for immediate feedback
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatting
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        # Initialize state tracking
        self.state_history = []
        self.critical_changes = []
        self.load_history()

    def load_history(self):
        """Load existing operation history"""
        try:
            history_file = self.log_dir / "state_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.state_history = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load history: {e}")
            self.state_history = []

    def track_change(self,
                     component: str,
                     action: str,
                     details: Dict[str, Any],
                     critical: bool = False):
        """Track a system change or strategic decision"""
        timestamp = datetime.now(timezone.utc).isoformat()

        change = {
            "timestamp": timestamp,
            "component": component,
            "action": action,
            "details": details,
            "critical": critical
        }

        # Add to history
        self.state_history.append(change)

        # Track critical changes separately
        if critical:
            self.critical_changes.append(change)
            self.logger.warning(
                f"CRITICAL CHANGE in {component}: {action}"
            )
        else:
            self.logger.info(
                f"Change in {component}: {action}"
            )

        # Save history
        self.save_history()

        return change

    def save_history(self):
        """Save the current state history"""
        try:
            with open(self.log_dir / "state_history.json", 'w') as f:
                json.dump(self.state_history, f, indent=2)

            if self.critical_changes:
                with open(self.log_dir / "critical_changes.json", 'w') as f:
                    json.dump(self.critical_changes, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save history: {e}")

    def get_recent_changes(self, limit: int = 10) -> List[Dict]:
        """Get most recent changes"""
        return self.state_history[-limit:]

    def get_critical_changes(self) -> List[Dict]:
        """Get all critical changes"""
        return self.critical_changes

    def get_component_history(self, component: str) -> List[Dict]:
        """Get history for a specific component"""
        return [
            change for change in self.state_history
            if change["component"] == component
        ]

    def create_checkpoint(self, name: str, state: Dict):
        """Create a named checkpoint of system state"""
        checkpoint = {
            "name": name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "state": state
        }

        checkpoint_file = self.log_dir / f"checkpoint_{name}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        self.logger.info(f"Created checkpoint: {name}")
        return checkpoint

    def load_checkpoint(self, name: str) -> Optional[Dict]:
        """Load a named checkpoint"""
        try:
            checkpoint_file = self.log_dir / f"checkpoint_{name}.json"
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error(f"Checkpoint not found: {name}")
            return None

    def compare_checkpoints(self, name1: str, name2: str) -> Dict:
        """Compare two checkpoints"""
        checkpoint1 = self.load_checkpoint(name1)
        checkpoint2 = self.load_checkpoint(name2)

        if not checkpoint1 or not checkpoint2:
            return {"error": "One or both checkpoints not found"}

        differences = {
            "timestamp_delta": (
                datetime.fromisoformat(checkpoint2["timestamp"]) -
                datetime.fromisoformat(checkpoint1["timestamp"])
            ).total_seconds(),
            "state_changes": self._compare_states(
                checkpoint1["state"],
                checkpoint2["state"]
            )
        }

        return differences

    def _compare_states(self, state1: Dict, state2: Dict) -> Dict:
        """Compare two states and return differences"""
        changes = {}

        # Compare all keys
        all_keys = set(state1.keys()) | set(state2.keys())

        for key in all_keys:
            if key not in state1:
                changes[key] = {"type": "added", "value": state2[key]}
            elif key not in state2:
                changes[key] = {"type": "removed", "value": state1[key]}
            elif state1[key] != state2[key]:
                changes[key] = {
                    "type": "modified",
                    "old": state1[key],
                    "new": state2[key]
                }

        return changes

    def summarize_changes(self, timeframe: str = "24h") -> Dict:
        """Summarize changes over a timeframe"""
        now = datetime.now(timezone.utc)

        # Filter changes within timeframe
        recent_changes = [
            change for change in self.state_history
            if (now - datetime.fromisoformat(change["timestamp"])).total_seconds() <=
            self._timeframe_to_seconds(timeframe)
        ]

        summary = {
            "total_changes": len(recent_changes),
            "critical_changes": len([c for c in recent_changes if c["critical"]]),
            "components_modified": len(set(c["component"] for c in recent_changes)),
            "most_active_component": self._most_common(
                [c["component"] for c in recent_changes]
            )
        }

        return summary

    def _timeframe_to_seconds(self, timeframe: str) -> int:
        """Convert timeframe string to seconds"""
        unit = timeframe[-1]
        value = int(timeframe[:-1])

        if unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        elif unit == 'w':
            return value * 604800
        else:
            raise ValueError(f"Invalid timeframe unit: {unit}")

    def _most_common(self, items: List) -> Optional[Any]:
        """Get most common item from a list"""
        if not items:
            return None

        counts = {}
        for item in items:
            counts[item] = counts.get(item, 0) + 1

        return max(counts.items(), key=lambda x: x[1])[0]
