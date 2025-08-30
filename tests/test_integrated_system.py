#!/usr/bin/env python3
"""
Tests for the Integrated Agent System.

This module tests the integration of the Kids Friendly AI Guide,
Epoch Audit System, and Mesh Trigger Core with the existing
EpochCore RAS agent architecture.
"""

import tempfile
import unittest
from pathlib import Path

from integrated_agent_system import IntegratedAgentSystem


class TestIntegratedAgentSystem(unittest.TestCase):
    """Simple tests for the Integrated Agent System."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for system data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_path = self.temp_dir.name

        # Create the integrated system
        self.system = IntegratedAgentSystem(
            name="test_integrated_system",
            data_dir=self.data_path
        )

    def tearDown(self):
        """Clean up test environment."""
        self.system.shutdown()
        self.temp_dir.cleanup()

    def test_system_initialization(self):
        """Test that the system initializes properly."""
        # Verify components are initialized
        self.assertIsNotNone(self.system.kids_friendly)
        self.assertIsNotNone(self.system.epoch_audit)
        self.assertIsNotNone(self.system.mesh_trigger)

        # Verify data directory exists
        data_dir = Path(self.data_path)
        self.assertTrue(data_dir.exists())

    def test_create_system_audit(self):
        """Test creating a system audit."""
        # Test creating a system audit
        audit_info = self.system.create_system_audit()

        # Verify audit info
        self.assertIn("timestamp", audit_info)
        self.assertIn("audit_scroll", audit_info)
        self.assertIn("file", audit_info["audit_scroll"])

        # Verify audit file exists
        self.assertTrue(Path(audit_info["audit_scroll"]["file"]).exists())


if __name__ == "__main__":
    unittest.main()
