#!/usr/bin/env python3
"""
Tests for the EpochAudit system.
"""

import json
import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path

from scripts.epoch_audit import EpochAudit


class TestEpochAudit(unittest.TestCase):
    """Test cases for the EpochAudit class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for ledger data
        self.temp_dir = tempfile.mkdtemp()
        self.audit = EpochAudit(ledger_root=self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test that the audit system initializes correctly."""
        # Check that directories were created
        ledger_dir = Path(self.temp_dir)
        self.assertTrue(ledger_dir.exists())
        self.assertTrue((ledger_dir / "logs").exists())
        self.assertTrue((ledger_dir / "seals").exists())
        self.assertTrue((ledger_dir / "capsules").exists())

        # Check that the ledger file was created
        ledger_file = ledger_dir / "ledger_main.jsonl"
        self.assertTrue(ledger_file.exists())

        # Verify genesis entry
        with open(ledger_file, "r") as f:
            entry = json.loads(f.readline())
            self.assertEqual(entry["event"], "genesis")

    def test_log_event(self):
        """Test that events are logged correctly."""
        # Log a test event
        test_event = "test_event"
        test_note = "Test note"
        additional_field = "additional_value"

        entry = self.audit.log_event(
            test_event, test_note, additional_field=additional_field
        )

        # Check the returned entry
        self.assertEqual(entry["event"], test_event)
        self.assertEqual(entry["note"], test_note)
        self.assertEqual(entry["additional_field"], additional_field)

        # Check the ledger file
        ledger_file = Path(self.temp_dir) / "ledger_main.jsonl"
        with open(ledger_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)  # Genesis + our new event
            last_entry = json.loads(lines[-1])
            self.assertEqual(last_entry["event"], test_event)
            self.assertEqual(last_entry["note"], test_note)

    def test_alpha_ceiling(self):
        """Test Alpha Ceiling enforcement."""
        # Test a value below ceiling
        value = 50
        result = self.audit.enforce_alpha_ceiling(value)
        self.assertEqual(result, value)

        # Test a value above ceiling
        value = 150
        result = self.audit.enforce_alpha_ceiling(value)
        self.assertEqual(result, self.audit.alpha_ceiling)

        # Test with custom ceiling
        custom_ceiling = 200
        value = 150
        result = self.audit.enforce_alpha_ceiling(value, custom_ceiling)
        self.assertEqual(result, value)

        value = 250
        result = self.audit.enforce_alpha_ceiling(value, custom_ceiling)
        self.assertEqual(result, custom_ceiling)

    def test_create_and_verify_seal(self):
        """Test creating and verifying seals."""
        # Create a test seal
        test_data = "Test data for sealing"
        seal_info = self.audit.create_seal("test_seal", test_data)

        # Check seal information
        self.assertIn("ts", seal_info)
        self.assertIn("seal", seal_info)
        self.assertIn("sha256", seal_info)
        self.assertIn("file", seal_info)

        # Verify the seal with correct data
        seal_file = Path(seal_info["file"])
        self.assertTrue(seal_file.exists())
        result = self.audit.verify_seal(seal_file, test_data)
        self.assertTrue(result)

        # Verify with incorrect data
        bad_data = "Modified data"
        result = self.audit.verify_seal(seal_file, bad_data)
        self.assertFalse(result)

    def test_gbt_epoch(self):
        """Test GBTEpoch functionality."""
        epoch_info = self.audit.gbt_epoch()

        # Check epoch information
        self.assertIn("ts", epoch_info)
        self.assertIn("epoch", epoch_info)
        self.assertIsInstance(epoch_info["epoch"], int)

    def test_audit_history(self):
        """Test retrieving audit history."""
        # Create multiple events
        for i in range(5):
            self.audit.log_event(
                f"test_event_{i}",
                f"Test note {i}",
                index=i
            )

        # Get history
        history = self.audit.get_audit_history(10)

        # Check history
        self.assertEqual(len(history), 6)  # 5 events + genesis

        # Check order (most recent first)
        self.assertEqual(history[0]["event"], "test_event_4")

        # Check with limit
        limited_history = self.audit.get_audit_history(3)
        self.assertEqual(len(limited_history), 3)


if __name__ == "__main__":
    unittest.main()
