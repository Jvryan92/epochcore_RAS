"""
Tests for PR Automation Engine
"""

import unittest
import json
from datetime import datetime
from recursive_improvement.engines.pr_automation_engine import PRAutomationEngine


class TestPRAutomationEngine(unittest.TestCase):
    """Test cases for the PR Automation Engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = PRAutomationEngine()
    
    def test_engine_initialization(self):
        """Test that the PR automation engine initializes correctly."""
        result = self.engine.initialize()
        self.assertTrue(result)
        self.assertEqual(self.engine.name, "pr_automation")
        self.assertIsNotNone(self.engine.automation_metrics)
        self.assertEqual(len(self.engine.available_engines), 15)
    
    def test_available_engines_list(self):
        """Test that all expected engines are available."""
        expected_engines = [
            'ai_code_review_bot',
            'auto_refactor', 
            'dependency_health',
            'workflow_auditor',
            'doc_updater',
            'feedback_loop_engine',
            'experimentation_tree_engine',
            'self_cloning_mvp_agent',
            'asset_library_engine',
            'weekly_auto_debrief_bot',
            'kpi_mutation_engine',
            'autonomous_escalation_logic',
            'recursive_workflow_automation',
            'content_stack_engine',
            'playbook_generator_engine'
        ]
        
        for engine in expected_engines:
            self.assertIn(engine, self.engine.available_engines)
    
    def test_pr_scanning(self):
        """Test PR scanning functionality."""
        result = self.engine.execute_pre_action()
        
        self.assertEqual(result["action"], "pr_scanning")
        self.assertEqual(result["status"], "completed")
        self.assertIn("new_prs_found", result)
        self.assertIn("contexts_prepared", result)
    
    def test_comprehensive_pr_processing(self):
        """Test comprehensive PR processing with all engines."""
        # Initialize first
        self.engine.initialize()
        
        result = self.engine.execute_main_action()
        
        self.assertEqual(result["action"], "comprehensive_pr_processing")
        self.assertEqual(result["status"], "completed")
        self.assertIn("prs_processed", result)
        self.assertIn("engines_executed", result)
        self.assertIn("processing_results", result)
    
    def test_risk_assessment(self):
        """Test PR risk assessment functionality."""
        # Test high-risk PR
        high_risk_pr = {
            "id": "test_pr_1",
            "title": "Security fix for authentication",
            "author": "developer"
        }
        risk = self.engine._assess_pr_risk(high_risk_pr)
        self.assertEqual(risk, "high")
        
        # Test medium-risk PR
        medium_risk_pr = {
            "id": "test_pr_2", 
            "title": "Bug fix for user interface",
            "author": "developer"
        }
        risk = self.engine._assess_pr_risk(medium_risk_pr)
        self.assertEqual(risk, "medium")
        
        # Test low-risk PR
        low_risk_pr = {
            "id": "test_pr_3",
            "title": "Add new feature",
            "author": "developer"
        }
        risk = self.engine._assess_pr_risk(low_risk_pr)
        self.assertEqual(risk, "low")
    
    def test_automation_plan_creation(self):
        """Test automation plan creation based on PR risk."""
        pr = {
            "id": "test_pr",
            "title": "Critical security update",
            "author": "security-team"
        }
        
        plan = self.engine._create_automation_plan(pr)
        
        self.assertIn("risk_level", plan)
        self.assertIn("engines_to_run", plan)
        self.assertIn("processing_order", plan)
        self.assertEqual(plan["risk_level"], "high")
        self.assertEqual(len(plan["engines_to_run"]), 15)  # All engines for high-risk
    
    def test_processing_priority_determination(self):
        """Test processing priority determination."""
        # High-risk PR should get urgent priority
        high_risk_pr = {"title": "Security vulnerability fix", "author": "developer"}
        priority = self.engine._determine_processing_priority(high_risk_pr)
        self.assertEqual(priority, "urgent")
        
        # Dependabot PR should get urgent priority
        bot_pr = {"title": "Update dependencies", "author": "dependabot"}
        priority = self.engine._determine_processing_priority(bot_pr)
        self.assertEqual(priority, "urgent")
        
        # Medium-risk PR should get high priority
        medium_pr = {"title": "Fix bug in login", "author": "developer"}
        priority = self.engine._determine_processing_priority(medium_pr)
        self.assertEqual(priority, "high")
    
    def test_engine_simulation(self):
        """Test individual engine simulation functions."""
        pr = {"id": "test", "title": "Test PR", "author": "test"}
        
        # Test AI review simulation
        result = self.engine._simulate_ai_review(pr)
        self.assertEqual(result["engine"], "ai_code_review_bot")
        self.assertTrue(result["review_completed"])
        
        # Test refactoring simulation
        result = self.engine._simulate_refactoring(pr)
        self.assertEqual(result["engine"], "auto_refactor")
        self.assertGreater(result["prs_created"], 0)
        
        # Test dependency check simulation
        result = self.engine._simulate_dependency_check(pr)
        self.assertEqual(result["engine"], "dependency_health")
        self.assertGreater(result["prs_created"], 0)
    
    def test_metrics_tracking(self):
        """Test automation metrics tracking."""
        # Initialize engine
        self.engine.initialize()
        
        # Simulate processing results
        results = {
            "prs_processed": 2,
            "engines_executed": 10,
            "automation_prs_created": 3,
            "status": "completed"
        }
        
        # Update metrics
        self.engine._update_automation_metrics(results, 5.0)
        
        metrics = self.engine.automation_metrics
        self.assertEqual(metrics["prs_processed"], 2)
        self.assertEqual(metrics["engines_triggered"], 10)
        self.assertEqual(metrics["automation_prs_created"], 3)
        self.assertEqual(metrics["successful_automations"], 1)
        self.assertGreater(metrics["total_processing_time"], 0)
    
    def test_github_pr_creation_simulation(self):
        """Test GitHub PR creation (simulated without token)."""
        result = self.engine.create_github_pr(
            title="Test PR",
            body="Test body",
            branch="test-branch"
        )
        
        self.assertEqual(result["status"], "simulated")
        self.assertEqual(result["title"], "Test PR")
        self.assertEqual(result["branch"], "test-branch")
        self.assertIn("simulated", result["message"])
    
    def test_engine_status(self):
        """Test engine status reporting."""
        self.engine.initialize()
        
        status = self.engine.get_status()
        
        self.assertEqual(status["engine"], "pr_automation")
        self.assertIn("status", status)
        self.assertIn("metrics", status)
        self.assertIn("available_engines", status)
        self.assertEqual(status["available_engines"], 15)
        self.assertIn("engines_list", status)
        self.assertIn("github_integration", status)
        self.assertIn("repository", status)


if __name__ == '__main__':
    unittest.main()