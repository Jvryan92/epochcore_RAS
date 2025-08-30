#!/usr/bin/env python3
"""
Tests for the MeshTriggerCore system.
"""

import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path

from scripts.mesh.trigger_core import MeshTriggerCore


class TestMeshTriggerCore(unittest.TestCase):
    """Test cases for the MeshTriggerCore class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for mesh data
        self.temp_dir = tempfile.mkdtemp()
        self.trigger_core = MeshTriggerCore(base_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_register_trigger(self):
        """Test registering a trigger."""
        # Register a test trigger
        trigger_id = "test_trigger"
        description = "Test description"
        resource_requirement = 50

        trigger = self.trigger_core.register_trigger(
            trigger_id, description, resource_requirement
        )

        # Check trigger details
        self.assertEqual(trigger["id"], trigger_id)
        self.assertEqual(trigger["description"], description)
        self.assertEqual(trigger["resource_requirement"], resource_requirement)
        self.assertEqual(trigger["status"], "registered")
        self.assertEqual(trigger["activations"], 0)
        self.assertIsNone(trigger["last_activation"])

        # Check that trigger is stored in memory
        self.assertIn(trigger_id, self.trigger_core.triggers)

        # Check that trigger is stored on disk
        trigger_file = Path(self.temp_dir) / "mesh_triggers.json"
        self.assertTrue(trigger_file.exists())

        with open(trigger_file, "r") as f:
            saved_triggers = json.load(f)
            self.assertIn(trigger_id, saved_triggers)

    def test_alpha_ceiling(self):
        """Test Alpha Ceiling enforcement on trigger registration."""
        # Register a trigger with resource requirement above Alpha Ceiling
        trigger_id = "high_resource_trigger"
        resource_requirement = self.trigger_core.alpha_ceiling + 50

        trigger = self.trigger_core.register_trigger(
            trigger_id, "High resource trigger", resource_requirement
        )

        # Check that resource requirement was capped
        self.assertEqual(
            trigger["resource_requirement"],
            self.trigger_core.alpha_ceiling
        )

    def test_handler_registration(self):
        """Test registering a handler for a trigger."""
        # Register a test trigger
        trigger_id = "test_trigger"
        self.trigger_core.register_trigger(
            trigger_id, "Test description", 50
        )

        # Define a test handler
        def test_handler(context):
            return {"handled": True}

        # Register the handler
        result = self.trigger_core.register_handler(trigger_id, test_handler)
        self.assertTrue(result)

        # Check that handler is stored
        self.assertIn(trigger_id, self.trigger_core.handlers)
        self.assertEqual(len(self.trigger_core.handlers[trigger_id]), 1)

        # Try to register handler for non-existent trigger
        result = self.trigger_core.register_handler("nonexistent", test_handler)
        self.assertFalse(result)

    def test_trigger_seal(self):
        """Test creating and verifying a trigger seal."""
        # Register a test trigger
        trigger_id = "test_trigger"
        self.trigger_core.register_trigger(
            trigger_id, "Test description", 50
        )

        # Create a seal
        context = {"test": "value"}
        seal = self.trigger_core.create_trigger_seal(trigger_id, context)

        # Check seal data
        self.assertEqual(seal["trigger_id"], trigger_id)
        self.assertIn("fingerprint", seal)
        self.assertIn("ts", seal)
        self.assertIn("epoch", seal)
        self.assertIn("expires", seal)
        self.assertIn("hash", seal)
        self.assertEqual(seal["context"], context)

        # Verify the seal
        result = self.trigger_core.verify_trigger_seal(seal)
        self.assertTrue(result)

        # Tamper with the seal
        tampered_seal = seal.copy()
        tampered_seal["context"]["test"] = "modified"
        result = self.trigger_core.verify_trigger_seal(tampered_seal)
        self.assertFalse(result)

    def test_trigger_activation(self):
        """Test activating a trigger."""
        # Register a test trigger
        trigger_id = "test_trigger"
        self.trigger_core.register_trigger(
            trigger_id, "Test description", 50
        )

        # Define a test handler that counts activations
        activation_count = [0]

        def test_handler(context):
            activation_count[0] += 1
            return {"count": activation_count[0]}

        # Register the handler
        self.trigger_core.register_handler(trigger_id, test_handler)

        # Activate the trigger
        context = {"mode": "test"}
        activation = self.trigger_core.activate_trigger(trigger_id, context)

        # Check activation details
        self.assertEqual(activation["trigger_id"], trigger_id)
        self.assertEqual(activation["context"], context)
        self.assertEqual(activation["status"], "completed")

        # Check that handler was called
        self.assertEqual(activation_count[0], 1)

        # Check that trigger info was updated
        trigger = self.trigger_core.triggers[trigger_id]
        self.assertEqual(trigger["activations"], 1)
        self.assertIsNotNone(trigger["last_activation"])

    def test_critical_trigger_verification(self):
        """Test critical trigger verification requirements."""
        # Register a critical trigger
        trigger_id = "critical_trigger"
        self.trigger_core.register_trigger(
            trigger_id, "Critical operation", 80, trigger_type="critical"
        )

        # Try to activate with insufficient verifications
        activation = self.trigger_core.activate_trigger(
            trigger_id, {"mode": "test"}, verify_count=1
        )

        # Should fail due to insufficient verifications
        self.assertEqual(activation["status"], "error")

        # Activate with sufficient verifications
        min_verify = self.trigger_core.min_verify_count
        activation = self.trigger_core.activate_trigger(
            trigger_id, {"mode": "test"}, verify_count=min_verify
        )

        # Should succeed
        self.assertEqual(activation["status"], "completed")

    def test_list_triggers(self):
        """Test listing triggers."""
        # Register triggers of different types
        self.trigger_core.register_trigger(
            "standard1", "Standard trigger 1", 50, "standard"
        )
        self.trigger_core.register_trigger(
            "standard2", "Standard trigger 2", 40, "standard"
        )
        self.trigger_core.register_trigger(
            "critical1", "Critical trigger 1", 80, "critical"
        )

        # List all triggers
        all_triggers = self.trigger_core.list_triggers()
        self.assertEqual(len(all_triggers), 3)

        # List standard triggers
        standard_triggers = self.trigger_core.list_triggers("standard")
        self.assertEqual(len(standard_triggers), 2)

        # List critical triggers
        critical_triggers = self.trigger_core.list_triggers("critical")
        self.assertEqual(len(critical_triggers), 1)


if __name__ == "__main__":
    unittest.main()
