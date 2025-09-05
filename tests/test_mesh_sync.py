#!/usr/bin/env python3
"""
Test for Org Mesh Sync functionality
"""

import unittest
import json
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to import integration
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/../'))

import integration


class TestMeshSync(unittest.TestCase):
    """Test cases for the Org Mesh Sync functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.config_file = "ops/mesh/org_mesh_config.json"
        self.report_file = "ops/mesh/reports/mesh_report.json"
    
    def test_mesh_config_exists(self):
        """Test that mesh configuration file exists and is valid."""
        self.assertTrue(os.path.exists(self.config_file), 
                       f"Mesh config file should exist at {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        # Verify required config structure
        self.assertIn("repositories", config)
        self.assertIn("mesh_modules", config)
        self.assertIsInstance(config["repositories"], list)
        self.assertGreater(len(config["repositories"]), 0)
    
    def test_mesh_sync_dry_run(self):
        """Test mesh sync in dry-run mode."""
        result = integration.run_mesh_sync(dry_run="true", target_branch="main")
        
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["dry_run"])
        self.assertGreater(result["repositories_processed"], 0)
        self.assertTrue(os.path.exists(result["report_path"]))
        
        # Verify report format
        with open(result["report_path"], 'r') as f:
            report = json.load(f)
        
        self.assertIn("ts", report)
        self.assertIn("dry_run", report)
        self.assertIn("target", report)
        self.assertIn("repos", report)
        self.assertTrue(report["dry_run"])
        self.assertEqual(report["target"], "main")
    
    def test_mesh_sync_real_mode(self):
        """Test mesh sync in real mode (simulated)."""
        result = integration.run_mesh_sync(dry_run="false", target_branch="main")
        
        self.assertEqual(result["status"], "success")
        self.assertFalse(result["dry_run"])
        self.assertGreater(result["repositories_processed"], 0)
        
        # Verify report contains PR information for real mode
        with open(result["report_path"], 'r') as f:
            report = json.load(f)
        
        self.assertFalse(report["dry_run"])
        
        # Check that repos have PR information in real mode
        for repo in report["repos"]:
            if not report["dry_run"]:
                self.assertIn("pr", repo)
                self.assertIn("branch", repo)
                self.assertEqual(repo["status"], "pr-opened")
    
    def test_mesh_directories_exist(self):
        """Test that required mesh directories exist."""
        self.assertTrue(os.path.exists("ops/mesh/"), 
                       "ops/mesh/ directory should exist")
        self.assertTrue(os.path.exists("ops/mesh/reports/"), 
                       "ops/mesh/reports/ directory should exist")
        self.assertTrue(os.path.exists("reports/mesh/"), 
                       "reports/mesh/ directory should exist")
    
    def test_trigger_script_exists(self):
        """Test that trigger script exists and is executable."""
        trigger_script = "ops/mesh/trigger.sh"
        self.assertTrue(os.path.exists(trigger_script))
        self.assertTrue(os.access(trigger_script, os.X_OK), 
                       "Trigger script should be executable")


if __name__ == '__main__':
    unittest.main()