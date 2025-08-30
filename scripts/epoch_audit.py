#!/usr/bin/env python3
"""
EpochCore RAS Audit System

This module implements secure audit logging, verification, and integrity 
features inspired by the Alpha Ceiling, GBTEpoch, and Phone Audit Scroll
concepts from the bash scripts.
"""

import datetime
import hashlib
import json
import logging
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EpochAudit")


class EpochAudit:
    """
    Implements secure audit logging and verification for EpochCore RAS.
    Inspired by Alpha Ceiling, GBTEpoch and Phone Audit Scroll concepts.
    """

    def __init__(self, ledger_root: Optional[str] = None):
        """
        Initialize the EpochAudit system.

        Args:
            ledger_root: Root directory for ledger data. If None, defaults to ./ledger
        """
        self.ledger_root = Path(ledger_root) if ledger_root else Path("./ledger")

        # Create directory structure
        self.logs_dir = self.ledger_root / "logs"
        self.seals_dir = self.ledger_root / "seals"
        self.capsules_dir = self.ledger_root / "capsules"

        # Ensure directories exist
        self.ledger_root.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        self.seals_dir.mkdir(exist_ok=True)
        self.capsules_dir.mkdir(exist_ok=True)

        # Ledger file
        self.ledger_file = self.ledger_root / "ledger_main.jsonl"

        # Alpha Ceiling (maximum allowed value for numeric parameters)
        self.alpha_ceiling = 100

        # Initialize ledger if needed
        if not self.ledger_file.exists():
            self._initialize_ledger()

    def _initialize_ledger(self) -> None:
        """Initialize the main ledger file with genesis entry."""
        timestamp = self._get_timestamp()
        genesis_entry = {
            "ts": timestamp,
            "event": "genesis",
            "note": "EpochCore RAS Audit System initialized"
        }

        with open(self.ledger_file, "w") as f:
            f.write(json.dumps(genesis_entry) + "\n")

        # Create GBTEpoch capsule (initial state)
        gbt_capsule = {
            "ts": timestamp,
            "capsule": "GBTEpoch_init",
            "status": "ready",
            "sha256": self._hash_string("GBTEpoch_init")
        }

        with open(self.capsules_dir / "gbtepoch_init.json", "w") as f:
            json.dump(gbt_capsule, f, indent=2)

        logger.info(f"Ledger initialized at {timestamp}")

    def _get_timestamp(self) -> str:
        """Get ISO-8601 UTC timestamp."""
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _hash_string(self, text: str) -> str:
        """Create SHA-256 hash of a string."""
        return hashlib.sha256(text.encode()).hexdigest()

    def _hash_file(self, file_path: Path) -> str:
        """Create SHA-256 hash of a file."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    def log_event(self, event: str, note: str, **kwargs) -> Dict[str, Any]:
        """
        Log an event to the audit ledger.

        Args:
            event: Event type identifier
            note: Description of the event
            **kwargs: Additional fields to include in the log entry

        Returns:
            The complete log entry as a dictionary
        """
        timestamp = self._get_timestamp()
        entry = {
            "ts": timestamp,
            "event": event,
            "note": note,
            **kwargs
        }

        with open(self.ledger_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        logger.info(f"Logged event: {event} at {timestamp}")
        return entry

    def enforce_alpha_ceiling(self, value: int, ceiling: Optional[int] = None) -> int:
        """
        Enforce Alpha Ceiling on a numeric value.

        Args:
            value: The value to check
            ceiling: Optional override for the default alpha ceiling

        Returns:
            The value, capped at the ceiling if necessary
        """
        max_value = ceiling if ceiling is not None else self.alpha_ceiling

        if value > max_value:
            logger.warning(
                f"Alpha Ceiling enforcement: {value} exceeds maximum {max_value}, capping.")

            # Log the ceiling enforcement
            self.log_event(
                "alpha_ceiling_enforced",
                f"Value {value} exceeded ceiling {max_value}",
                original_value=value,
                capped_value=max_value
            )

            return max_value
        return value

    def create_seal(self, name: str, data: str) -> Dict[str, Any]:
        """
        Create a cryptographic seal for data.

        Args:
            name: Identifier for the seal
            data: The data to seal

        Returns:
            Seal information
        """
        timestamp = self._get_timestamp()
        seal_hash = self._hash_string(data)

        # Create the seal file
        seal_file = self.seals_dir / f"{name}.{timestamp}.sha"
        with open(seal_file, "w") as f:
            f.write(seal_hash)

        # Log the seal creation
        seal_info = {
            "ts": timestamp,
            "seal": name,
            "sha256": seal_hash,
            "file": str(seal_file)
        }

        self.log_event(
            "seal_created",
            f"Created seal for {name}",
            **seal_info
        )

        return seal_info

    def verify_seal(self, seal_file: Path, data: str) -> bool:
        """
        Verify that data matches a previously created seal.

        Args:
            seal_file: Path to the seal file
            data: The data to verify

        Returns:
            True if the seal verifies, False otherwise
        """
        if not seal_file.exists():
            logger.error(f"Seal file {seal_file} does not exist")
            return False

        with open(seal_file, "r") as f:
            stored_hash = f.read().strip()

        current_hash = self._hash_string(data)
        verified = stored_hash == current_hash

        self.log_event(
            "seal_verified" if verified else "seal_failed",
            f"Verified seal {seal_file.name}" if verified else f"Seal verification failed for {seal_file.name}",
            seal_file=str(seal_file),
            verified=verified
        )

        return verified

    def gbt_epoch(self) -> Dict[str, Any]:
        """
        Get current GBTEpoch information.

        Returns:
            Dictionary with epoch timestamp and related info
        """
        timestamp = self._get_timestamp()
        epoch_time = int(time.time())

        gbt_info = {
            "ts": timestamp,
            "epoch": epoch_time,
            "note": "GBTEpoch timestamp captured"
        }

        self.log_event(
            "gbt_epoch",
            "GBTEpoch timestamp captured",
            epoch=epoch_time
        )

        return gbt_info

    def phone_audit_scroll(self) -> Dict[str, Any]:
        """
        Create a Phone Audit Scroll - a snapshot of system state for auditing.

        Returns:
            Dictionary with audit information
        """
        timestamp = self._get_timestamp()
        audit_file = self.logs_dir / f"phone_audit_{timestamp}.log"

        # Collect system information
        try:
            # Get system logs (simulated, as not all systems have dmesg)
            system_info = []

            try:
                # Try to get last system logs if available
                dmesg_output = subprocess.check_output(["dmesg", "--time-format", "iso", "-l", "warn,err", "-n", "50"],
                                                       stderr=subprocess.DEVNULL).decode()
                system_info.append("=== System Logs ===")
                system_info.append(dmesg_output)
            except (subprocess.SubprocessError, FileNotFoundError):
                system_info.append("=== System Logs Unavailable ===")

            # Get process information
            try:
                ps_output = subprocess.check_output(["ps", "aux", "--sort=-%cpu", "|", "head", "-10"],
                                                    shell=True).decode()
                system_info.append("\n=== Top Processes ===")
                system_info.append(ps_output)
            except subprocess.SubprocessError:
                system_info.append("\n=== Process Information Unavailable ===")

            # Get ledger stats
            ledger_count = 0
            if self.ledger_file.exists():
                with open(self.ledger_file, "r") as f:
                    ledger_count = sum(1 for _ in f)

            system_info.append("\n=== Ledger Stats ===")
            system_info.append(f"Total entries: {ledger_count}")
            system_info.append(f"Last update: {timestamp}")

            # Write to audit file
            with open(audit_file, "w") as f:
                f.write("\n".join(system_info))

            # Hash the file
            file_hash = self._hash_file(audit_file)

            # Log the audit
            audit_info = {
                "ts": timestamp,
                "file": str(audit_file),
                "sha256": file_hash,
                "entries": ledger_count
            }

            self.log_event(
                "phone_audit_scroll",
                "Phone Audit Scroll created",
                **audit_info
            )

            return audit_info

        except Exception as e:
            logger.error(f"Failed to create Phone Audit Scroll: {str(e)}")
            self.log_event(
                "phone_audit_error",
                f"Failed to create Phone Audit Scroll: {str(e)}"
            )
            raise

    def schedule_audit(self, delay_seconds: int = 3600) -> None:
        """
        Schedule a Phone Audit Scroll to run after a delay.

        Args:
            delay_seconds: Number of seconds to wait before running the audit
        """
        def delayed_audit():
            time.sleep(delay_seconds)
            try:
                self.phone_audit_scroll()
                logger.info(
                    f"Scheduled Phone Audit Scroll completed after {delay_seconds}s delay")
            except Exception as e:
                logger.error(f"Scheduled Phone Audit Scroll failed: {str(e)}")

        # Start in background thread
        thread = threading.Thread(target=delayed_audit)
        thread.daemon = True
        thread.start()

        self.log_event(
            "audit_scheduled",
            f"Phone Audit Scroll scheduled in {delay_seconds} seconds"
        )

        logger.info(f"Phone Audit Scroll scheduled in {delay_seconds} seconds")

    def get_audit_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent entries from the audit ledger.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of recent audit entries
        """
        if not self.ledger_file.exists():
            return []

        entries = []
        with open(self.ledger_file, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue

        # Return most recent entries first
        return sorted(entries, key=lambda x: x.get("ts", ""), reverse=True)[:limit]


def main():
    """
    Example usage of the EpochAudit system.
    """
    # Create audit system with default ledger location
    audit = EpochAudit()

    # Log a simple event
    audit.log_event("example_event", "Testing the audit system")

    # Test Alpha Ceiling enforcement
    value = 150
    capped = audit.enforce_alpha_ceiling(value)
    print(f"Original value: {value}, After Alpha Ceiling: {capped}")

    # Create a seal
    test_data = f"Test data at {audit._get_timestamp()}"
    seal = audit.create_seal("test_seal", test_data)
    print(f"Created seal: {seal}")

    # Get GBTEpoch
    epoch = audit.gbt_epoch()
    print(f"Current GBTEpoch: {epoch}")

    # Create Phone Audit Scroll
    try:
        audit_info = audit.phone_audit_scroll()
        print(f"Created Phone Audit Scroll: {audit_info}")
    except Exception as e:
        print(f"Failed to create Phone Audit Scroll: {e}")

    # Schedule an audit for later
    audit.schedule_audit(10)  # 10 seconds
    print("Scheduled Phone Audit Scroll in 10 seconds")

    # Get recent audit history
    history = audit.get_audit_history(5)
    print("\nRecent Audit History:")
    for entry in history:
        print(f"- {entry.get('ts')}: {entry.get('event')} - {entry.get('note')}")

    print("\nAudit system demonstration complete.")
    print("Wait 15 seconds for scheduled audit to complete...")
    time.sleep(15)


if __name__ == "__main__":
    main()
