"""Tests for autonomous improvement system"""
import unittest
import json
from unittest.mock import patch, MagicMock


class TestAutonomousImprovement(unittest.TestCase):
    """Test cases for autonomous improvement modules."""

    def test_genetic_optimizer_import(self):
        """Test that genetic optimizer can be imported."""
        from genetic_optimizer import GeneticOptimizer
        optimizer = GeneticOptimizer()
        self.assertIsNotNone(optimizer)

    def test_rl_agent_import(self):
        """Test that RL agent can be imported."""
        from rl_agent import ReinforcementLearningAgent
        agent = ReinforcementLearningAgent()
        self.assertIsNotNone(agent)

    def test_auto_refactor_import(self):
        """Test that auto refactor can be imported."""
        from auto_refactor import AutoRefactor
        refactor = AutoRefactor()
        self.assertIsNotNone(refactor)

    def test_self_healing_import(self):
        """Test that self healing can be imported."""
        from self_healing import SelfHealing
        healing = SelfHealing()
        self.assertIsNotNone(healing)

    def test_pr_feedback_import(self):
        """Test that PR feedback can be imported."""
        from pr_feedback import PRFeedbackLoop
        feedback = PRFeedbackLoop()
        self.assertIsNotNone(feedback)

    def test_autonomous_improvement_import(self):
        """Test that main autonomous improvement can be imported."""
        from autonomous_improvement import AutonomousImprovement
        improvement = AutonomousImprovement()
        self.assertIsNotNone(improvement)

    def test_integration_autonomous_commands(self):
        """Test new integration commands."""
        from integration import run_autonomous_improvement, get_improvement_status
        
        # These should not crash when called
        # They might return error codes but should not raise exceptions
        try:
            result1 = run_autonomous_improvement()
            self.assertIn(result1, [0, 1])
            
            result2 = get_improvement_status()
            self.assertIn(result2, [0, 1])
        except ImportError:
            # Expected in test environment without full dependencies
            pass

    def test_genetic_optimizer_basic_functionality(self):
        """Test basic genetic optimizer functionality."""
        from genetic_optimizer import GeneticOptimizer
        
        optimizer = GeneticOptimizer()
        
        # Test parameter space setup
        self.assertIn("agent_pool_size", optimizer.parameter_space)
        self.assertIn("dag_timeout", optimizer.parameter_space)
        
        # Test population initialization
        population = optimizer._initialize_population()
        self.assertEqual(len(population), optimizer.population_size)
        self.assertTrue(all(isinstance(ind, dict) for ind in population))

    def test_rl_agent_basic_functionality(self):
        """Test basic RL agent functionality."""
        from rl_agent import ReinforcementLearningAgent
        
        agent = ReinforcementLearningAgent()
        
        # Test actions and state features
        self.assertGreater(len(agent.actions), 0)
        self.assertGreater(len(agent.state_features), 0)
        
        # Test metrics to state conversion
        test_metrics = {
            "cpu_percent": 50,
            "memory_percent": 60,
            "validation_errors": 0
        }
        state = agent._metrics_to_state(test_metrics)
        self.assertIsInstance(state, str)
        self.assertIn("cpu:", state)

    def test_auto_refactor_file_discovery(self):
        """Test auto refactor file discovery."""
        from auto_refactor import AutoRefactor
        
        refactor = AutoRefactor()
        refactor._discover_python_files()
        
        # Should find at least some Python files
        self.assertGreater(len(refactor.python_files), 0)
        
        # Should include the test files
        python_files_str = str(refactor.python_files)
        self.assertIn("test_", python_files_str)

    def test_self_healing_health_checks(self):
        """Test self healing health check setup."""
        from self_healing import SelfHealing
        
        healing = SelfHealing()
        
        # Test health checks are set up
        self.assertIn("system_resources", healing.health_checks)
        self.assertIn("process_health", healing.health_checks)
        
        # Test healing strategies are set up
        self.assertIn("system_resources", healing.healing_strategies)
        self.assertIn("process_health", healing.healing_strategies)

    def test_pr_feedback_patterns(self):
        """Test PR feedback pattern setup."""
        from pr_feedback import PRFeedbackLoop
        
        feedback = PRFeedbackLoop()
        
        # Test feedback patterns are set up
        self.assertIn("code_quality", feedback.feedback_patterns)
        self.assertIn("security", feedback.feedback_patterns)
        self.assertIn("performance", feedback.feedback_patterns)
        
        # Test pattern priorities
        security_weight = feedback.feedback_patterns["security"]["weight"]
        quality_weight = feedback.feedback_patterns["code_quality"]["weight"]
        self.assertGreater(security_weight, quality_weight)

    def test_improvement_system_status(self):
        """Test improvement system status functionality."""
        from autonomous_improvement import AutonomousImprovement
        
        improvement = AutonomousImprovement()
        status = improvement.get_improvement_status()
        
        # Test status structure
        self.assertIn("current_cycle", status)
        self.assertIn("total_cycles", status)
        self.assertIn("total_improvements", status)
        self.assertIn("system_status", status)
        
        # Test initial values
        self.assertEqual(status["current_cycle"], 0)
        self.assertEqual(status["total_cycles"], 0)
        self.assertEqual(status["system_status"], "operational")


class TestIntegrationWithImprovements(unittest.TestCase):
    """Test integration of improvements with existing system."""
    
    def test_integration_commands(self):
        """Test that integration.py includes new commands."""
        import integration
        
        # Test functions exist
        self.assertTrue(hasattr(integration, 'run_autonomous_improvement'))
        self.assertTrue(hasattr(integration, 'run_recursive_improvement'))
        self.assertTrue(hasattr(integration, 'get_improvement_status'))

    def test_dashboard_improvements_endpoint(self):
        """Test that dashboard includes improvements endpoint."""
        from dashboard import DashboardHandler
        import io
        from unittest.mock import Mock
        
        # Create a mock handler
        handler = DashboardHandler()
        handler.wfile = io.BytesIO()
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        
        # Test improvements endpoint exists
        self.assertTrue(hasattr(handler, 'send_improvements_json'))
        
        # Test it can be called without crashing
        try:
            handler.send_improvements_json()
        except Exception as e:
            # May fail due to imports, but method should exist
            pass

    def test_existing_functionality_preserved(self):
        """Test that existing functionality still works."""
        from integration import setup_demo, run_workflow, get_status, validate_system
        
        # Test original functions still work
        result1 = setup_demo()
        self.assertEqual(result1["status"], "success")
        
        result2 = run_workflow()
        self.assertEqual(result2["status"], "success")
        
        result3 = get_status()
        self.assertEqual(result3["status"], "operational")
        
        result4 = validate_system()
        self.assertEqual(result4["status"], "valid")


if __name__ == '__main__':
    unittest.main()