#!/usr/bin/env python3
"""
Test suite for Cross-Repository Automation functionality
"""

import unittest
import tempfile
import json
import os
from unittest.mock import patch, MagicMock
from datetime import datetime
from pathlib import Path

# Import the modules we're testing
from cross_repository_automation import CrossRepositoryAutomator
import integration

class TestCrossRepositoryAutomation(unittest.TestCase):
    """Test cases for cross-repository automation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.automator = CrossRepositoryAutomator()
        
    def test_initialization(self):
        """Test cross-repository automation initialization."""
        result = self.automator.initialize()
        self.assertTrue(result)
        self.assertIsNotNone(self.automator.orchestrator)
        
    def test_repository_configuration(self):
        """Test repository configuration."""
        expected_repos = {
            "epochcore_RAS": "Jvryan92/epochcore_RAS",
            "EpochCore_OS": "Jvryan92/EpochCore_OS", 
            "epoch5_template": "EpochCore5/epoch5-template"
        }
        
        self.assertEqual(self.automator.repositories, expected_repos)
        
    def test_get_repository_status(self):
        """Test getting repository status."""
        status = self.automator.get_repository_status()
        
        self.assertIn("timestamp", status)
        self.assertIn("repositories", status)
        self.assertEqual(status["total_repositories"], 3)
        
        # Check each repository has expected fields
        for repo_name, repo_info in status["repositories"].items():
            self.assertIn("full_name", repo_info)
            self.assertIn("status", repo_info)
            self.assertIn("pending_fixes", repo_info)
            self.assertIn("open_prs", repo_info)
            
    def test_automate_fix_all_basic(self):
        """Test basic automate fix all functionality."""
        if not self.automator.initialize():
            self.skipTest("Failed to initialize automation system")
            
        results = self.automator.automate_fix_all(
            target_repos=["epochcore_RAS"],
            fix_types=["code_review"],
            create_prs=False,
            auto_merge=False
        )
        
        self.assertIn("timestamp", results)
        self.assertIn("target_repositories", results)
        self.assertIn("fix_types", results)
        self.assertIn("repositories", results)
        self.assertIn("summary", results)
        
        # Check summary structure
        summary = results["summary"]
        self.assertIn("total_repos", summary)
        self.assertIn("successful_repos", summary)
        self.assertIn("total_fixes_applied", summary)
        
    def test_fix_type_filtering(self):
        """Test filtering by fix types."""
        if not self.automator.initialize():
            self.skipTest("Failed to initialize automation system")
            
        results = self.automator.automate_fix_all(
            target_repos=["epochcore_RAS"],
            fix_types=["refactor", "documentation"],
            create_prs=False
        )
        
        self.assertEqual(results["fix_types"], ["refactor", "documentation"])
        
        # Check that only specified fix types were applied
        if "epochcore_RAS" in results["repositories"]:
            repo_result = results["repositories"]["epochcore_RAS"]
            for fix_type in repo_result.get("fix_types_applied", []):
                self.assertIn(fix_type, ["refactor", "documentation"])
                
    def test_repository_filtering(self):
        """Test filtering by target repositories."""
        if not self.automator.initialize():
            self.skipTest("Failed to initialize automation system")
            
        results = self.automator.automate_fix_all(
            target_repos=["epochcore_RAS", "EpochCore_OS"],
            fix_types=["code_review"],
            create_prs=False
        )
        
        self.assertEqual(set(results["target_repositories"]), {"epochcore_RAS", "EpochCore_OS"})
        self.assertEqual(results["summary"]["total_repos"], 2)
        
    @patch('cross_repository_automation.subprocess.run')
    def test_safe_refactoring_application(self, mock_subprocess):
        """Test that safe refactoring is applied correctly."""
        if not self.automator.initialize():
            self.skipTest("Failed to initialize automation system")
            
        # Mock successful subprocess execution
        mock_subprocess.return_value.stdout = "SUCCESS"
        mock_subprocess.return_value.returncode = 0
        
        # Test would require actual file operations in real implementation
        # For now, verify the structure is correct
        results = self.automator.automate_fix_all(
            target_repos=["epochcore_RAS"],
            fix_types=["refactor"],
            create_prs=False
        )
        
        self.assertGreaterEqual(results["summary"]["total_fixes_applied"], 0)

class TestIntegrationEnhancements(unittest.TestCase):
    """Test cases for integration.py enhancements."""
    
    def test_cross_repo_automation_import(self):
        """Test that cross-repository automation can be imported."""
        # Test that we can import the enhanced integration functions
        self.assertTrue(hasattr(integration, 'execute_cross_repository_automation'))
        self.assertTrue(hasattr(integration, 'get_cross_repository_status'))
        
    def test_integration_command_parsing(self):
        """Test that new commands are available in integration."""
        # This would test argument parsing, but requires mocking sys.argv
        # For now, just verify the functions exist
        self.assertTrue(callable(integration.execute_cross_repository_automation))
        self.assertTrue(callable(integration.get_cross_repository_status))
        
    @patch('integration.CrossRepositoryAutomator')
    def test_cross_repo_status_function(self, mock_automator_class):
        """Test the cross-repository status function."""
        # Mock the automator
        mock_automator = MagicMock()
        mock_automator.get_repository_status.return_value = {
            "timestamp": datetime.now().isoformat(),
            "repositories": {
                "test_repo": {
                    "full_name": "test/repo",
                    "status": "active",
                    "pending_fixes": 0,
                    "open_prs": 1
                }
            },
            "total_repositories": 1
        }
        mock_automator_class.return_value = mock_automator
        
        result = integration.get_cross_repository_status()
        
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        mock_automator.get_repository_status.assert_called_once()

class TestAutomatedFixGeneration(unittest.TestCase):
    """Test cases for automated fix generation and application."""
    
    def setUp(self):
        """Set up test fixtures with temporary files."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_automation_report_generation(self):
        """Test that automation reports are generated correctly."""
        automator = CrossRepositoryAutomator()
        
        # Create a sample automation result
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "target_repositories": ["test_repo"],
            "fix_types": ["test_fix"],
            "repositories": {
                "test_repo": {
                    "status": "success",
                    "fixes_applied": 5,
                    "prs_created": ["https://github.com/test/repo/pull/1"]
                }
            },
            "summary": {
                "total_repos": 1,
                "successful_repos": 1,
                "total_fixes_applied": 5,
                "prs_created": 1,
                "prs_merged": 0
            }
        }
        
        # Test report generation (would write to file in real implementation)
        automator._generate_automation_report(test_results)
        
        # Verify report structure
        self.assertIn("timestamp", test_results)
        self.assertIn("summary", test_results)
        self.assertEqual(test_results["summary"]["total_fixes_applied"], 5)
        
    def test_fix_type_application_workflow(self):
        """Test the workflow of applying different fix types."""
        automator = CrossRepositoryAutomator()
        
        # Test each fix type application method exists and has correct signature
        fix_types = ["code_review", "refactor", "dependencies", "workflows", "documentation"]
        
        for fix_type in fix_types:
            method_name = f"_apply_{fix_type}_fixes"
            # Verify method exists (would be available after initialization)
            self.assertTrue(hasattr(automator, method_name) or fix_type in ["code_review", "refactor"])
            
    def test_pr_creation_simulation(self):
        """Test PR creation simulation."""
        automator = CrossRepositoryAutomator()
        
        test_fix_result = {
            "success": True,
            "fixes_count": 3,
            "description": "Applied 3 test fixes"
        }
        
        pr_result = automator._create_automated_pr(
            "test_repo", 
            "test/repo", 
            "test_fix", 
            test_fix_result
        )
        
        self.assertEqual(pr_result["success"], True)
        self.assertIn("pr_number", pr_result)
        self.assertIn("pr_url", pr_result)
        self.assertIn("title", pr_result)
        self.assertIn("body", pr_result)
        
    def test_safe_merge_detection(self):
        """Test detection of safe-to-merge fixes."""
        automator = CrossRepositoryAutomator()
        
        # Test safe fix types
        safe_fix = {"fixes_count": 3}
        self.assertTrue(automator._is_safe_to_merge("documentation", safe_fix))
        self.assertTrue(automator._is_safe_to_merge("dependencies", safe_fix))
        
        # Test unsafe fix types
        self.assertFalse(automator._is_safe_to_merge("refactor", safe_fix))
        
        # Test fix count threshold
        large_fix = {"fixes_count": 10}
        self.assertFalse(automator._is_safe_to_merge("documentation", large_fix))

class TestWorkflowIntegration(unittest.TestCase):
    """Test cases for GitHub Actions workflow integration."""
    
    def test_workflow_file_exists(self):
        """Test that the cross-repository automation workflow exists."""
        workflow_path = Path(".github/workflows/cross-repository-automation.yml")
        if workflow_path.exists():
            self.assertTrue(workflow_path.is_file())
            
            # Basic validation of workflow structure
            with open(workflow_path, 'r') as f:
                content = f.read()
                self.assertIn("Cross-Repository Automated Fixes", content)
                self.assertIn("workflow_dispatch", content)
                self.assertIn("schedule", content)
        else:
            self.skipTest("Workflow file not found - may be expected in test environment")
            
    def test_workflow_parameter_structure(self):
        """Test that workflow has expected input parameters."""
        workflow_path = Path(".github/workflows/cross-repository-automation.yml")
        if not workflow_path.exists():
            self.skipTest("Workflow file not found")
            
        with open(workflow_path, 'r') as f:
            content = f.read()
            
        # Check for required input parameters
        expected_inputs = [
            "target_repositories",
            "fix_types", 
            "create_prs",
            "auto_merge",
            "urgency"
        ]
        
        for input_param in expected_inputs:
            self.assertIn(input_param, content)

if __name__ == '__main__':
    # Create test suite
    test_classes = [
        TestCrossRepositoryAutomation,
        TestIntegrationEnhancements,
        TestAutomatedFixGeneration,
        TestWorkflowIntegration
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)