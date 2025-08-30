#!/usr/bin/env python3
"""
Ledger Agent - Specialized agent for monitoring and syncing the ledger across
the EpochCore mesh. Integrates with the Ultra Trigger Pack system.

This agent:
1. Monitors the ledger for new capsules
2. Verifies capsule integrity using SHA-256 seals
3. Facilitates mesh synchronization of capsule states
4. Provides mathematical analysis of trigger effects
"""

import hashlib
import json
import logging
import math
import os
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] LedgerAgent: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ledger_agent.log')
    ]
)
logger = logging.getLogger('ledger_agent')

# Configuration
ROOT = Path(os.getcwd())
LEDGER_PATH = ROOT / "ledger_main.jsonl"
CAPSULES_DIR = ROOT / "out" / "capsules"
ARCHIVES_DIR = ROOT / "out" / "archive"
SYNC_INTERVAL = 5  # seconds between sync operations

# Mathematical model parameters - same as in dashboard
LEVERAGE_FACTOR = 10.0
VELOCITY_FACTOR = 5.0
BASE_COMPOUND_RATE = 0.010072  # Base compound rate (1.0072%)
TRIGGER_MULTIPLIERS = {
    "TREASURYFLOW💵": 1.0,      # base impact
    "MARKETCAP📈": 1.5,         # stronger impact
    "PRICINGFORGE💳": 1.2,      # moderate impact
    "BONUSDROP🎁": 1.8,         # high variability
    "GOVCOUNCIL⚖️": 1.0,        # stability-focused
    "PULLREQUESTVOTE🔀": 1.0,   # stability-focused
    "ROLLBACKSEAL⏪": 0.8,       # safety, slightly reduces growth
    "MESHSPAWN🌱": 2.0,         # strong network effect
    "CIVILIZATIONBLOCK🌍": 2.5,  # strongest compound effect
    "AUTOCOMPOUND⏩": 10.0       # direct 10X multiplier
}


class LedgerAgent:
    """Agent responsible for ledger monitoring, verification, and sync"""

    def __init__(self):
        self.ledger_entries = []
        self.known_capsules = set()
        self.last_sync_time = datetime.min
        self.sync_active = False
        self.total_value = 7.0  # Initial mathematical value
        self.trigger_counts = defaultdict(int)
        self.mesh_nodes = {}  # node_id -> connection info

        # Ensure directories exist
        CAPSULES_DIR.mkdir(parents=True, exist_ok=True)
        ARCHIVES_DIR.mkdir(parents=True, exist_ok=True)

        # Initialize ledger if it doesn't exist
        if not LEDGER_PATH.exists():
            with open(LEDGER_PATH, "w") as f:
                f.write("")

        # Load initial state
        self.load_ledger()
        logger.info(
            f"LedgerAgent initialized with {len(self.ledger_entries)} ledger entries")

    def load_ledger(self):
        """Load the ledger file and update internal state"""
        entries = []
        if LEDGER_PATH.exists():
            with open(LEDGER_PATH, "r") as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        entries.append(entry)

                        # Update known capsules
                        capsule_path = entry.get("capsule", "")
                        if capsule_path:
                            self.known_capsules.add(Path(capsule_path).name)

                        # Update trigger counts
                        trigger = entry.get("trigger", "")
                        if trigger:
                            self.trigger_counts[trigger] += 1

                    except json.JSONDecodeError:
                        pass

        self.ledger_entries = entries
        return entries

    def verify_capsule(self, capsule_path):
        """Verify a capsule's integrity using its SHA-256 seal"""
        if not Path(capsule_path).exists():
            return False, "Capsule file not found"

        # Find ledger entry for this capsule
        capsule_name = Path(capsule_path).name
        entry = next((e for e in self.ledger_entries
                     if Path(e.get("capsule", "")).name == capsule_name), None)

        if not entry:
            return False, "No ledger entry found for capsule"

        # Calculate SHA-256 hash
        with open(capsule_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Compare with recorded hash
        recorded_hash = entry.get("sha256", "")
        if file_hash == recorded_hash:
            return True, "Capsule integrity verified"
        else:
            return False, f"Hash mismatch: {file_hash} vs {recorded_hash}"

    def calculate_growth_impact(self, trigger, base_value=None):
        """Calculate the mathematical impact of a trigger on the system value"""
        if base_value is None:
            base_value = self.total_value

        if trigger == "AUTOCOMPOUND⏩":
            # Apply leverage directly
            return base_value * LEVERAGE_FACTOR
        else:
            # Apply compound growth
            multiplier = TRIGGER_MULTIPLIERS.get(trigger, 1.0)
            compound_rate = BASE_COMPOUND_RATE * multiplier
            # Single activation for this trigger
            return base_value * (1 + compound_rate)

    def process_new_capsule(self, capsule_path):
        """Process a newly detected capsule"""
        if not Path(capsule_path).exists():
            return False

        # Load the capsule
        with open(capsule_path, "r") as f:
            try:
                capsule = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in capsule: {capsule_path}")
                return False

        # Extract trigger
        trigger = capsule.get("trigger", "")
        if not trigger:
            logger.warning(f"No trigger found in capsule: {capsule_path}")
            return False

        # Update mathematical value based on trigger
        old_value = self.total_value
        self.total_value = self.calculate_growth_impact(trigger)

        logger.info(f"Processed capsule with trigger: {trigger}")
        logger.info(f"Value change: {old_value:.2f} → {self.total_value:.2f} " +
                    f"(×{self.total_value/old_value:.2f})")

        return True

    def sync_with_mesh(self):
        """Synchronize with other nodes in the mesh"""
        if not self.mesh_nodes:
            logger.info("No mesh nodes configured - running in standalone mode")
            return

        logger.info(f"Syncing with {len(self.mesh_nodes)} mesh nodes...")
        # In a real implementation, this would perform network operations
        # to sync capsule state with other nodes

        # Simulate sync time
        time.sleep(0.5)

        self.last_sync_time = datetime.now()
        logger.info(f"Sync completed at {self.last_sync_time.isoformat()}")

    def monitor_ledger(self):
        """Monitor the ledger for changes and process new entries"""
        last_entry_count = len(self.ledger_entries)

        while True:
            try:
                # Reload the ledger
                self.load_ledger()

                # Check for new entries
                current_count = len(self.ledger_entries)
                if current_count > last_entry_count:
                    logger.info(
                        f"Detected {current_count - last_entry_count} new ledger entries")

                    # Process new capsules
                    for entry in self.ledger_entries[-1 * (current_count - last_entry_count):]:
                        capsule_path = entry.get("capsule", "")
                        if capsule_path and Path(capsule_path).exists():
                            self.process_new_capsule(capsule_path)

                    # Perform sync
                    if not self.sync_active:
                        self.sync_active = True
                        self.sync_with_mesh()
                        self.sync_active = False

                last_entry_count = current_count

            except Exception as e:
                logger.error(f"Error monitoring ledger: {e}")

            # Sleep before next check
            time.sleep(SYNC_INTERVAL)

    def print_status(self):
        """Print the current status of the agent"""
        logger.info("=" * 50)
        logger.info("Ledger Agent Status")
        logger.info("=" * 50)
        logger.info(f"Known Capsules: {len(self.known_capsules)}")
        logger.info(f"Current Value: {self.total_value:.2f}")
        logger.info(f"Last Sync: {self.last_sync_time.isoformat()}")

        logger.info("\nTrigger Counts:")
        for trigger, count in sorted(self.trigger_counts.items()):
            logger.info(f"  {trigger}: {count}")

        logger.info("\nMathematical Analysis:")
        doubling_time = 72 / (BASE_COMPOUND_RATE * 100)
        logger.info(f"  Base compound rate: {BASE_COMPOUND_RATE*100:.4f}%")
        logger.info(f"  Doubling time: {doubling_time:.1f} triggers")
        logger.info(f"  Growth factor: {self.total_value/7.0:.2f}x")

        logger.info("=" * 50)

    def join_sync(self):
        """Join the synchronization process"""
        logger.info("Ledger Agent joining synchronization process...")

        # Start monitoring thread
        monitor_thread = Thread(target=self.monitor_ledger)
        monitor_thread.daemon = True
        monitor_thread.start()

        # Print initial status
        self.print_status()

        # Check if we can trigger ROI burst
        burst_triggered = False
        try:
            ultra_script = ROOT / "ultra_trigger_pack_batch.sh"
            if ultra_script.exists() and os.access(ultra_script, os.X_OK):
                logger.info("Triggering ROI burst...")
                result = subprocess.run(
                    [str(ultra_script), "--batch", "roi-burst"],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    logger.info("ROI burst successfully triggered")
                    burst_triggered = True
                else:
                    logger.error(f"ROI burst trigger failed: {result.stderr}")
            else:
                logger.warning("Ultra Trigger Pack script not found or not executable")
        except Exception as e:
            logger.error(f"Error triggering ROI burst: {e}")

        # Main agent loop
        try:
            while True:
                # Print status every 30 seconds
                self.print_status()
                time.sleep(30)
        except KeyboardInterrupt:
            logger.info("Ledger Agent shutting down...")
            return


def main():
    """Main entry point"""
    print("=" * 60)
    print(" EpochCore Ledger Agent ".center(60, "="))
    print("=" * 60)
    print("Starting agent and joining synchronization process...")

    agent = LedgerAgent()
    agent.join_sync()


if __name__ == "__main__":
    main()
