#!/usr/bin/env python3
"""
Test suite for EpochCore Recursive Autonomy System
Tests agents, manifests, and flash sync functionality
"""

import unittest
import json
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime


class TestRecursiveAutonomyAgents(unittest.TestCase):
    """Test autonomous agent execution and manifest generation."""
    
    def setUp(self):
        self.base_path = Path(__file__).parent.parent
        self.agents_path = self.base_path / "agents"
        self.manifests_path = self.base_path / "manifests"
        
        # List of agents to test
        self.agents = [
            "kpi_prediction_agent",
            "failure_remediation_agent", 
            "portfolio_optimizer",
            "meta_experiment_cascade",
            "resource_allocation_agent",
            "compliance_auditor",
            "innovation_diffuser",
            "user_feedback_engine",
            "explainability_agent",
            "agent_registry",
            "audit_evolution_manager"
        ]

    def test_agents_exist(self):
        """Test that all agent files exist."""
        for agent_name in self.agents:
            agent_file = self.agents_path / f"{agent_name}.py"
            self.assertTrue(agent_file.exists(), f"Agent file missing: {agent_file}")

    def test_agent_execution(self):
        """Test that agents can be executed successfully."""
        import subprocess
        import sys
        
        # Test a sample of agents to avoid timeout
        test_agents = ["kpi_prediction_agent", "agent_registry", "audit_evolution_manager"]
        
        for agent_name in test_agents:
            with self.subTest(agent=agent_name):
                agent_file = self.agents_path / f"{agent_name}.py"
                
                # Change to base directory for execution
                original_cwd = os.getcwd()
                os.chdir(self.base_path)
                
                try:
                    result = subprocess.run(
                        [sys.executable, str(agent_file)],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    self.assertEqual(result.returncode, 0, 
                                   f"Agent {agent_name} failed with stderr: {result.stderr}")
                    
                finally:
                    os.chdir(original_cwd)

    def test_manifest_generation(self):
        """Test that agents generate valid manifests."""
        # Execute a sample agent first
        import subprocess
        import sys
        
        agent_name = "kpi_prediction_agent"
        agent_file = self.agents_path / f"{agent_name}.py"
        
        original_cwd = os.getcwd()
        os.chdir(self.base_path)
        
        try:
            subprocess.run([sys.executable, str(agent_file)], check=True, timeout=30)
            
            # Check manifest was created
            # Agent creates manifest with specific naming pattern
            if agent_name == "kpi_prediction_agent":
                manifest_file = self.manifests_path / "kpi_prediction_results.json"
            elif agent_name == "explainability_agent":
                manifest_file = self.manifests_path / "explainability_reports.json"
            else:
                manifest_file = self.manifests_path / f"{agent_name}_results.json"
            self.assertTrue(manifest_file.exists(), f"Manifest not created: {manifest_file}")
            
            # Validate manifest content
            with open(manifest_file, 'r') as f:
                manifest_data = json.load(f)
            
            # Check required fields
            required_fields = ["agent_id", "execution_time", "status", "cycles_completed"]
            for field in required_fields:
                self.assertIn(field, manifest_data, f"Missing field: {field}")
            
            self.assertEqual(manifest_data["status"], "success")
            self.assertGreater(manifest_data["cycles_completed"], 0)
            
        finally:
            os.chdir(original_cwd)

    def test_meta_controller_manifest(self):
        """Test the meta controller manifest structure."""
        manifest_file = self.manifests_path / "meta_controller_manifest.json"
        self.assertTrue(manifest_file.exists(), "Meta controller manifest missing")
        
        with open(manifest_file, 'r') as f:
            manifest_data = json.load(f)
        
        # Validate structure
        self.assertIn("meta_controller", manifest_data)
        meta_controller = manifest_data["meta_controller"]
        
        required_fields = ["agent_id", "status", "recursion_depth", "layers"]
        for field in required_fields:
            self.assertIn(field, meta_controller, f"Missing meta controller field: {field}")
        
        # Check layers structure
        self.assertIsInstance(meta_controller["layers"], list)
        self.assertGreater(len(meta_controller["layers"]), 0)
        
        # Check that all agents are represented in layers
        all_layer_agents = []
        for layer in meta_controller["layers"]:
            self.assertIn("agents", layer)
            for agent in layer["agents"]:
                all_layer_agents.append(agent["name"])
        
        for agent_name in self.agents:
            self.assertIn(agent_name, all_layer_agents, f"Agent {agent_name} not in meta manifest")


class TestFlashSyncScripts(unittest.TestCase):
    """Test flash sync script functionality."""
    
    def setUp(self):
        self.base_path = Path(__file__).parent.parent
        self.scripts_path = self.base_path / "scripts"

    def test_flash_sync_scripts_exist(self):
        """Test that flash sync scripts exist and are executable."""
        scripts = ["flash_sync.sh", "flash_sync_api.py", "run_recursive_autonomy.py"]
        
        for script_name in scripts:
            script_file = self.scripts_path / script_name
            self.assertTrue(script_file.exists(), f"Script missing: {script_file}")
            
            # Check if executable (on Unix systems)
            if os.name == 'posix':
                self.assertTrue(os.access(script_file, os.X_OK), f"Script not executable: {script_file}")

    def test_orchestrator_script(self):
        """Test the recursive autonomy orchestrator."""
        orchestrator_file = self.scripts_path / "run_recursive_autonomy.py"
        
        # Import and test the orchestrator class
        import sys
        sys.path.insert(0, str(self.scripts_path))
        
        try:
            from run_recursive_autonomy import RecursiveAutonomyOrchestrator
            
            orchestrator = RecursiveAutonomyOrchestrator()
            
            # Test initialization
            self.assertTrue(orchestrator.base_path.exists())
            self.assertTrue(orchestrator.agents_path.exists())
            self.assertTrue(orchestrator.manifests_path.exists())
            
            # Test agent list
            self.assertGreater(len(orchestrator.agents), 0)
            
        finally:
            sys.path.remove(str(self.scripts_path))


class TestWorkflowIntegration(unittest.TestCase):
    """Test GitHub Actions workflow configuration."""
    
    def setUp(self):
        self.base_path = Path(__file__).parent.parent
        self.workflow_file = self.base_path / ".github" / "workflows" / "recursive_matrix_autonomy.yml"

    def test_workflow_file_exists(self):
        """Test that the GitHub Actions workflow exists."""
        self.assertTrue(self.workflow_file.exists(), "GitHub Actions workflow missing")

    def test_workflow_structure(self):
        """Test the workflow file structure."""
        with open(self.workflow_file, 'r') as f:
            workflow_content = f.read()
        
        # Check for key workflow components
        required_elements = [
            "name: Recursive Matrix Autonomy Pipeline",
            "matrix-setup:",
            "recursive-agent-execution:",
            "orchestration-summary:",
            "cross-repo-sync:",
            "strategy:",
            "matrix:"
        ]
        
        for element in required_elements:
            self.assertIn(element, workflow_content, f"Missing workflow element: {element}")


class TestIntegrationWithExistingSystem(unittest.TestCase):
    """Test integration with the existing EpochCore RAS system."""
    
    def setUp(self):
        self.base_path = Path(__file__).parent.parent

    def test_integration_script_compatibility(self):
        """Test that the integration script still works with new agents."""
        # Import the integration module
        import sys
        sys.path.insert(0, str(self.base_path))
        
        try:
            import integration
            
            # Test that we can import without errors
            self.assertTrue(hasattr(integration, 'setup_demo'))
            self.assertTrue(hasattr(integration, 'get_status'))
            self.assertTrue(hasattr(integration, 'validate_system'))
            
        finally:
            if str(self.base_path) in sys.path:
                sys.path.remove(str(self.base_path))

    def test_recursive_improvement_integration(self):
        """Test integration with existing recursive improvement framework."""
        # Check that recursive improvement modules exist
        recursive_path = self.base_path / "recursive_improvement"
        self.assertTrue(recursive_path.exists(), "Recursive improvement framework missing")
        
        init_file = recursive_path / "__init__.py"
        self.assertTrue(init_file.exists(), "Recursive improvement init missing")


def run_tests():
    """Run all tests with detailed output."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestRecursiveAutonomyAgents,
        TestFlashSyncScripts,
        TestWorkflowIntegration,
        TestIntegrationWithExistingSystem
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)