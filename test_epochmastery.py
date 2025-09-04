#!/usr/bin/env python3
"""
Test EPOCHMASTERY AGENTIC SYNC & AUTO-PR System
Comprehensive test suite for the new functionality
"""

import unittest
import json
import os
from datetime import datetime
import tempfile
import shutil

from epochmastery_sync import EpochmasteryAgentSync
from github_api_client import GitHubAPIClient, create_github_client


class TestEpochmasterySync(unittest.TestCase):
    """Test suite for EPOCHMASTERY AGENTIC SYNC system."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)
        
        # Create necessary directories
        os.makedirs('reports', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Initialize sync system
        self.sync_system = EpochmasteryAgentSync()
    
    def tearDown(self):
        """Clean up test environment."""
        try:
            shutil.rmtree(self.test_dir)
        except:
            pass
    
    def test_github_client_creation(self):
        """Test GitHub client creation and simulation mode."""
        client = create_github_client()
        
        self.assertIsInstance(client, GitHubAPIClient)
        self.assertEqual(client.owner, "Jvryan92")
        self.assertEqual(client.repo, "epochcore_RAS")
    
    def test_simulated_pr_creation(self):
        """Test simulated PR creation (no GitHub token)."""
        client = create_github_client()
        
        result = client.create_pull_request(
            title="Test PR",
            body="Test body", 
            head_branch="test-branch",
            base_branch="main",
            labels=["test", "automation"]
        )
        
        self.assertEqual(result["status"], "simulated")
        self.assertEqual(result["title"], "Test PR")
        self.assertEqual(result["head_branch"], "test-branch")
        self.assertEqual(result["labels"], ["test", "automation"])
    
    def test_agent_sync_pr_creation(self):
        """Test comprehensive agent sync PR creation."""
        client = create_github_client()
        
        agent_data = {
            "id": "test_agent",
            "name": "Test Agent", 
            "type": "test_engine",
            "status": "active",
            "health_score": 1.0,
            "last_sync": datetime.now().isoformat(),
            "capabilities": ["testing", "validation"]
        }
        
        improvements = [
            {
                "type": "performance",
                "description": "Improved test execution speed",
                "impact": "High",
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        audit_log = [
            {
                "timestamp": datetime.now().isoformat(),
                "action": "test_action",
                "status": "success"
            }
        ]
        
        governance_report = {
            "compliance_score": 1.0,
            "security_score": 1.0,
            "status": "compliant",
            "timestamp": datetime.now().isoformat(),
            "compliance_checks": [
                {"name": "audit_present", "passed": True},
                {"name": "security_validated", "passed": True}
            ]
        }
        
        result = client.create_agent_sync_pr(
            agent_data=agent_data,
            improvements=improvements, 
            audit_log=audit_log,
            governance_report=governance_report
        )
        
        self.assertEqual(result["status"], "simulated")
        self.assertIn("EPOCHMASTERY Agent Sync", result["title"])
    
    def test_manifest_initialization(self):
        """Test manifest file initialization."""
        # Ensure manifest exists
        manifest_path = "reports/manifest.json"
        self.assertTrue(os.path.exists(manifest_path))
        
        # Load and validate manifest
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        self.assertIn("manifest_version", manifest)
        self.assertIn("agents", manifest)
        self.assertIn("governance", manifest)
        self.assertIn("ledger", manifest)
        self.assertIn("metadata", manifest)
        
        # Validate governance structure
        governance = manifest["governance"]
        self.assertIn("compliance_rules", governance)
        self.assertIn("governance_score", governance)
        
        # Validate ledger structure
        ledger = manifest["ledger"]
        self.assertIn("total_actions", ledger)
        self.assertIn("successful_prs", ledger)
    
    def test_agent_discovery(self):
        """Test agent discovery functionality."""
        agents = self.sync_system.discover_all_agents()
        
        self.assertIsInstance(agents, list)
        self.assertGreater(len(agents), 0)
        
        # Validate agent structure
        for agent in agents[:3]:  # Check first 3 agents
            self.assertIn("id", agent)
            self.assertIn("name", agent)
            self.assertIn("type", agent)
            self.assertIn("status", agent)
    
    def test_data_sync(self):
        """Test full data synchronization."""
        # Discover agents first
        agents = self.sync_system.discover_all_agents()
        
        # Perform sync
        sync_result = self.sync_system.full_data_sync(agents)
        
        self.assertIn("timestamp", sync_result)
        self.assertIn("agents_synced", sync_result)
        self.assertIn("manifest_updated", sync_result)
        self.assertIn("governance_updated", sync_result)
        
        # Verify sync was successful
        self.assertGreater(sync_result["agents_synced"], 0)
        self.assertTrue(sync_result["manifest_updated"])
    
    def test_pr_generation(self):
        """Test automated PR generation."""
        # Setup sync result
        sync_result = {
            "agents_synced": 5,
            "manifest_updated": True,
            "governance_updated": True
        }
        
        # Generate PRs
        pr_results = self.sync_system.generate_automated_prs(sync_result)
        
        self.assertIsInstance(pr_results, list)
        self.assertGreater(len(pr_results), 0)
        
        # Validate PR structure
        for pr in pr_results[:3]:  # Check first 3 PRs
            self.assertIn("status", pr)
            self.assertIn("title", pr) 
    
    def test_audit_and_explainability(self):
        """Test recursive audit and explainability."""
        # Mock PR results
        pr_results = [
            {
                "status": "simulated",
                "title": "Test PR 1",
                "pr_number": None
            },
            {
                "status": "simulated", 
                "title": "Test PR 2",
                "pr_number": None
            }
        ]
        
        audit_result = self.sync_system.recursive_audit_and_feedback(pr_results)
        
        self.assertIn("timestamp", audit_result)
        self.assertIn("prs_audited", audit_result)
        self.assertIn("compliance_score", audit_result)
        self.assertIn("explainability_reports", audit_result)
        
        self.assertEqual(audit_result["prs_audited"], 2)
        self.assertIsInstance(audit_result["compliance_score"], float)
        self.assertIsInstance(audit_result["explainability_reports"], list)
    
    def test_full_sync_workflow(self):
        """Test complete EPOCHMASTERY sync workflow."""
        result = self.sync_system.run_full_epochmastery_sync()
        
        self.assertIn("session_id", result)
        self.assertIn("overall_status", result)
        self.assertIn("phases", result)
        
        # Verify all phases completed
        phases = result["phases"]
        expected_phases = [
            "agent_discovery", 
            "data_sync", 
            "pr_generation", 
            "audit", 
            "feedback_cycle"
        ]
        
        for phase in expected_phases:
            self.assertIn(phase, phases)
            self.assertIn("status", phases[phase])
    
    def test_status_reporting(self):
        """Test EPOCHMASTERY status reporting."""
        # Ensure manifest exists with data
        manifest = self.sync_system._load_manifest()
        
        # Check status data
        self.assertIn("metadata", manifest)
        self.assertIn("agents", manifest)
        self.assertIn("governance", manifest)
        self.assertIn("ledger", manifest)
    
    def test_governance_compliance(self):
        """Test governance compliance features."""
        agents = []  # Empty list for testing
        
        governance_report = self.sync_system._generate_governance_report(agents)
        
        self.assertIn("compliance_score", governance_report)
        self.assertIn("security_score", governance_report)
        self.assertIn("status", governance_report)
        self.assertIn("compliance_checks", governance_report)
        
        # Verify scores are valid
        self.assertIsInstance(governance_report["compliance_score"], float)
        self.assertGreaterEqual(governance_report["compliance_score"], 0.0)
        self.assertLessEqual(governance_report["compliance_score"], 1.0)


class TestWorkflowAuditorPRIntegration(unittest.TestCase):
    """Test updated workflow auditor PR integration."""
    
    def test_security_pr_creation(self):
        """Test security improvement PR creation."""
        from recursive_improvement.engines.workflow_auditor import WorkflowAuditorEngine
        
        engine = WorkflowAuditorEngine()
        
        security_suggestions = [
            {
                "category": "Security",
                "description": "Fix hardcoded secret in workflow",
                "priority": "high",
                "file": ".github/workflows/test.yml"
            }
        ]
        
        # This should create a simulated PR
        result = engine._create_security_improvement_pr(security_suggestions)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "security_improvement")
        self.assertIn("pr_result", result)
    
    def test_optimization_pr_creation(self):
        """Test optimization PR creation."""
        from recursive_improvement.engines.workflow_auditor import WorkflowAuditorEngine
        
        engine = WorkflowAuditorEngine()
        
        optimization_suggestions = [
            {
                "category": "Performance",
                "description": "Add caching for dependencies",
                "priority": "medium",
                "file": ".github/workflows/ci.yml"
            }
        ]
        
        result = engine._create_optimization_pr(optimization_suggestions)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["type"], "optimization")
        self.assertIn("pr_result", result)


def run_comprehensive_test():
    """Run comprehensive test of EPOCHMASTERY system."""
    print("🧪 Running EPOCHMASTERY AGENTIC SYNC Test Suite")
    print("=" * 50)
    
    # Create test loader and runner
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestEpochmasterySync))
    suite.addTests(loader.loadTestsFromTestCase(TestWorkflowAuditorPRIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("✅ All EPOCHMASTERY tests passed!")
        return 0
    else:
        print(f"❌ {len(result.failures)} test(s) failed, {len(result.errors)} error(s)")
        return 1


if __name__ == "__main__":
    exit(run_comprehensive_test())