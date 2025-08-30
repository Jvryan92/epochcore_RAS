#!/usr/bin/env python3
"""
Mesh Security and Trigger Core

This module provides core security and trigger functionality for the mesh network,
implementing concepts from the EpochCore Alpha Ceiling and audit system.
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MeshTrigger")


class MeshTriggerCore:
    """
    Core trigger system for mesh networks with security features.
    Incorporates concepts from Alpha Ceiling and GBTEpoch for secure 
    operation and auditing.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize the mesh trigger core.

        Args:
            base_dir: Base directory for mesh data
        """
        self.base_dir = Path(base_dir) if base_dir else Path("./ledger")
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # Mesh security settings
        self.alpha_ceiling = 100  # Maximum resource allocation
        self.seal_timeout = 300   # Seconds until seal expires
        self.min_verify_count = 3  # Minimum verifications needed

        # Registered triggers
        self.triggers: Dict[str, Dict[str, Any]] = {}

        # Registered trigger handlers
        self.handlers: Dict[str, List[Callable]] = {}

        # Load existing triggers
        self._load_triggers()

    def _load_triggers(self) -> None:
        """Load existing triggers from storage."""
        trigger_file = self.base_dir / "mesh_triggers.json"
        if trigger_file.exists():
            try:
                with open(trigger_file, "r") as f:
                    self.triggers = json.load(f)
                logger.info(f"Loaded {len(self.triggers)} triggers from {trigger_file}")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse trigger file {trigger_file}")
                self.triggers = {}

    def _save_triggers(self) -> None:
        """Save triggers to storage."""
        trigger_file = self.base_dir / "mesh_triggers.json"
        with open(trigger_file, "w") as f:
            json.dump(self.triggers, f, indent=2)

    def _get_timestamp(self) -> str:
        """Get ISO format timestamp."""
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    def _hash_data(self, data: Union[str, bytes]) -> str:
        """Create SHA-256 hash of data."""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()

    def _hmac_sign(self, key: bytes, data: Union[str, bytes]) -> str:
        """Sign data with HMAC-SHA256."""
        if isinstance(data, str):
            data = data.encode()
        return hmac.new(key, data, hashlib.sha256).hexdigest()

    def register_trigger(self,
                         trigger_id: str,
                         description: str,
                         resource_requirement: int,
                         trigger_type: str = "standard") -> Dict[str, Any]:
        """
        Register a new trigger in the mesh.

        Args:
            trigger_id: Unique identifier for trigger
            description: Human-readable description
            resource_requirement: Resource cost (subject to Alpha Ceiling)
            trigger_type: Type of trigger (standard, critical, etc.)

        Returns:
            Trigger information
        """
        # Apply Alpha Ceiling to resource requirement
        if resource_requirement > self.alpha_ceiling:
            logger.warning(
                f"Alpha Ceiling enforced on trigger {trigger_id}: "
                f"{resource_requirement} -> {self.alpha_ceiling}"
            )
            resource_requirement = self.alpha_ceiling

        # Create trigger with GBTEpoch timestamp
        timestamp = self._get_timestamp()
        epoch_time = int(time.time())

        trigger_info = {
            "id": trigger_id,
            "description": description,
            "resource_requirement": resource_requirement,
            "type": trigger_type,
            "created_ts": timestamp,
            "epoch": epoch_time,
            "status": "registered",
            "activations": 0,
            "last_activation": None
        }

        # Generate a trigger fingerprint
        data_for_hash = f"{trigger_id}|{description}|{resource_requirement}|{epoch_time}"
        trigger_info["fingerprint"] = self._hash_data(data_for_hash)

        # Store the trigger
        self.triggers[trigger_id] = trigger_info
        self._save_triggers()

        logger.info(f"Registered trigger: {trigger_id}")
        return trigger_info

    def register_handler(self, trigger_id: str, handler: Callable) -> bool:
        """
        Register a handler function for a trigger.

        Args:
            trigger_id: Trigger to handle
            handler: Function to call when trigger activates

        Returns:
            True if registered successfully, False otherwise
        """
        if trigger_id not in self.triggers:
            logger.error(
                f"Cannot register handler: Trigger {trigger_id} does not exist")
            return False

        if trigger_id not in self.handlers:
            self.handlers[trigger_id] = []

        self.handlers[trigger_id].append(handler)
        logger.info(f"Registered handler for trigger: {trigger_id}")
        return True

    def create_trigger_seal(self, trigger_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a cryptographic seal for a trigger to ensure integrity.

        Args:
            trigger_id: Trigger to seal
            context: Additional context for the seal

        Returns:
            Seal information or None if trigger not found
        """
        if trigger_id not in self.triggers:
            logger.error(f"Cannot create seal: Trigger {trigger_id} does not exist")
            return {}

        trigger = self.triggers[trigger_id]
        timestamp = self._get_timestamp()
        epoch_time = int(time.time())

        # Create seal data
        seal_data = {
            "trigger_id": trigger_id,
            "fingerprint": trigger["fingerprint"],
            "context": context,
            "ts": timestamp,
            "epoch": epoch_time,
            "expires": epoch_time + self.seal_timeout
        }

        # Sign the seal
        seal_json = json.dumps(seal_data, sort_keys=True)
        seal_hash = self._hash_data(seal_json)

        # Add hash to seal data
        seal_data["hash"] = seal_hash

        # Save seal to file
        seal_file = self.base_dir / f"seals/trigger_{trigger_id}_{epoch_time}.json"
        seal_file.parent.mkdir(parents=True, exist_ok=True)

        with open(seal_file, "w") as f:
            json.dump(seal_data, f, indent=2)

        logger.info(f"Created seal for trigger: {trigger_id}")
        return seal_data

    def verify_trigger_seal(self, seal_data: Dict[str, Any]) -> bool:
        """
        Verify a trigger seal's integrity.

        Args:
            seal_data: The seal data to verify

        Returns:
            True if seal is valid, False otherwise
        """
        # Check if seal is expired
        current_epoch = int(time.time())
        if current_epoch > seal_data.get("expires", 0):
            logger.warning(
                f"Seal for trigger {seal_data.get('trigger_id')} has expired")
            return False

        # Verify trigger exists
        trigger_id = seal_data.get("trigger_id")
        if trigger_id not in self.triggers:
            logger.error(f"Cannot verify seal: Trigger {trigger_id} does not exist")
            return False

        # Verify fingerprint
        if seal_data.get("fingerprint") != self.triggers[trigger_id].get("fingerprint"):
            logger.error(f"Seal fingerprint does not match trigger {trigger_id}")
            return False

        # Verify hash
        seal_copy = seal_data.copy()
        original_hash = seal_copy.pop("hash", None)
        if not original_hash:
            logger.error("Seal has no hash")
            return False

        seal_json = json.dumps(seal_copy, sort_keys=True)
        current_hash = self._hash_data(seal_json)

        if current_hash != original_hash:
            logger.error(f"Seal hash verification failed for trigger {trigger_id}")
            return False

        logger.info(f"Verified seal for trigger: {trigger_id}")
        return True

    def activate_trigger(self,
                         trigger_id: str,
                         context: Dict[str, Any] = None,
                         verify_count: int = 1) -> Dict[str, Any]:
        """
        Activate a trigger and execute its handlers.

        Args:
            trigger_id: Trigger to activate
            context: Activation context
            verify_count: Number of verifications required (for critical triggers)

        Returns:
            Activation information
        """
        if trigger_id not in self.triggers:
            logger.error(f"Cannot activate: Trigger {trigger_id} does not exist")
            return {"status": "error", "error": "Trigger not found"}

        trigger = self.triggers[trigger_id]
        context = context or {}

        # For critical triggers, ensure minimum verification count
        if trigger["type"] == "critical" and verify_count < self.min_verify_count:
            logger.error(
                f"Cannot activate critical trigger {trigger_id}: "
                f"Insufficient verifications ({verify_count}/{self.min_verify_count})"
            )
            return {
                "status": "error",
                "error": "Insufficient verifications for critical trigger"
            }

        # Create activation record
        timestamp = self._get_timestamp()
        epoch_time = int(time.time())

        activation = {
            "trigger_id": trigger_id,
            "ts": timestamp,
            "epoch": epoch_time,
            "context": context,
            "verify_count": verify_count,
            "status": "pending"
        }

        # Execute handlers
        results = []
        if trigger_id in self.handlers:
            for handler in self.handlers[trigger_id]:
                try:
                    result = handler(context)
                    results.append({"status": "success", "result": result})
                except Exception as e:
                    logger.error(f"Handler for trigger {trigger_id} failed: {str(e)}")
                    results.append({"status": "error", "error": str(e)})

        # Update activation record
        activation["results"] = results
        activation["status"] = "completed"

        # Update trigger information
        trigger["activations"] += 1
        trigger["last_activation"] = timestamp
        self._save_triggers()

        # Save activation record
        activations_dir = self.base_dir / "activations"
        activations_dir.mkdir(parents=True, exist_ok=True)

        activation_file = activations_dir / f"{trigger_id}_{epoch_time}.json"
        with open(activation_file, "w") as f:
            json.dump(activation, f, indent=2)

        logger.info(f"Activated trigger: {trigger_id}")
        return activation

    def list_triggers(self, trigger_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered triggers, optionally filtered by type.

        Args:
            trigger_type: Optional type filter

        Returns:
            List of trigger information
        """
        if trigger_type:
            return [
                trigger for trigger in self.triggers.values()
                if trigger["type"] == trigger_type
            ]
        return list(self.triggers.values())


def example_handler(context: Dict[str, Any]) -> Dict[str, Any]:
    """Example trigger handler function."""
    logger.info(f"Example handler called with context: {context}")
    return {"processed": True, "timestamp": int(time.time())}


def main():
    """
    Example usage of the MeshTriggerCore.
    """
    # Create trigger system
    trigger_core = MeshTriggerCore()

    # Register a standard trigger
    standard_trigger = trigger_core.register_trigger(
        "data_sync",
        "Synchronize data across mesh nodes",
        resource_requirement=50,
        trigger_type="standard"
    )

    # Register a critical trigger
    critical_trigger = trigger_core.register_trigger(
        "security_alert",
        "Handle security breach detection",
        resource_requirement=120,  # Will be capped by Alpha Ceiling
        trigger_type="critical"
    )

    # Register handlers
    trigger_core.register_handler("data_sync", example_handler)
    trigger_core.register_handler("security_alert", example_handler)

    # Create a seal for a trigger
    seal = trigger_core.create_trigger_seal(
        "data_sync",
        {"source": "node1", "target": "node2"}
    )

    # Verify the seal
    is_valid = trigger_core.verify_trigger_seal(seal)
    print(f"Seal verification: {is_valid}")

    # Activate a standard trigger
    activation = trigger_core.activate_trigger(
        "data_sync",
        {"time": int(time.time()), "mode": "full"}
    )
    print(f"Trigger activation: {activation['status']}")

    # Try to activate a critical trigger with insufficient verifications
    activation = trigger_core.activate_trigger(
        "security_alert",
        {"severity": "high", "source_ip": "192.168.1.1"},
        verify_count=1  # Below min_verify_count
    )
    print(
        f"Critical trigger activation: {activation['status']} - {activation.get('error', '')}")

    # Activate critical trigger with sufficient verifications
    activation = trigger_core.activate_trigger(
        "security_alert",
        {"severity": "high", "source_ip": "192.168.1.1"},
        verify_count=3  # At min_verify_count
    )
    print(f"Critical trigger activation: {activation['status']}")

    # List all triggers
    all_triggers = trigger_core.list_triggers()
    print(f"All triggers: {len(all_triggers)}")

    # List only critical triggers
    critical_triggers = trigger_core.list_triggers(trigger_type="critical")
    print(f"Critical triggers: {len(critical_triggers)}")


if __name__ == "__main__":
    main()
