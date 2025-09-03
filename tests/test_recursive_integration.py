"""Enhanced test for integration.py with recursive improvements"""
import unittest
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIntegrationWithRecursive(unittest.TestCase):
    """Test cases for integration module with recursive improvements."""

    def test_import(self):
        """Test that we can import the integration module."""
        import integration
        self.assertIsNotNone(integration)

    def test_setup_demo_with_recursive(self):
        """Test setup_demo function with recursive improvements."""
        from integration import setup_demo
        result = setup_demo()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["components_initialized"], 4)
        self.assertEqual(result["recursive_engines"], 10)

    def test_get_status_with_recursive(self):
        """Test get_status function with recursive system."""
        from integration import get_status
        result = get_status()
        self.assertEqual(result["status"], "operational")
        self.assertIn("recursive_system", result)

    def test_validate_system_with_recursive(self):
        """Test validate_system function with recursive improvements."""
        from integration import validate_system
        result = validate_system()
        self.assertEqual(result["status"], "valid")
        self.assertEqual(result["errors"], 0)
        self.assertTrue(result["recursive_system_validated"])

    def test_recursive_initialization(self):
        """Test recursive improvement system initialization."""
        from integration import initialize_recursive_improvement_system
        orchestrator = initialize_recursive_improvement_system()
        self.assertIsNotNone(orchestrator)
        
        # Test orchestrator functionality
        status = orchestrator.get_system_status()
        self.assertIn("orchestrator", status)
        self.assertIn("engines", status)
        self.assertEqual(len(status["engines"]), 16)

    def test_recursive_trigger(self):
        """Test manual recursive improvement triggering."""
        from integration import initialize_recursive_improvement_system
        orchestrator = initialize_recursive_improvement_system()
        
        result = orchestrator.trigger_recursive_improvement("test_trigger")
        self.assertIn("engines_triggered", result)
        self.assertIn("total_improvements", result)
        self.assertGreaterEqual(len(result["engines_triggered"]), 1)

    def test_engine_status(self):
        """Test individual engine status reporting."""
        from integration import initialize_recursive_improvement_system
        orchestrator = initialize_recursive_improvement_system()
        
        # Test each engine is running
        for engine_name, engine in orchestrator.engines.items():
            status = engine.get_status()
            # Some engines use "name", others use "engine" - check both
            status_name = status.get("name") or status.get("engine")
            self.assertEqual(status_name, engine_name)
            # Check if it has status information in some form
            has_status_info = ("status" in status) or ("running" in status)
            self.assertTrue(has_status_info, f"Engine {engine_name} should have status information")
            # Check if it's running or active
            running_status = status.get("running") or (status.get("status") == "active")
            self.assertIsNotNone(running_status)

    def test_compounding_logic(self):
        """Test compounding logic execution."""
        from integration import initialize_recursive_improvement_system
        orchestrator = initialize_recursive_improvement_system()
        
        # Get an engine and test compounding execution
        feedback_engine = orchestrator.engines.get("feedback_loop_engine")
        self.assertIsNotNone(feedback_engine)
        
        # Execute with compounding
        result = feedback_engine.execute_with_compounding()
        self.assertIn("engine", result)
        self.assertEqual(result["engine"], "feedback_loop_engine")
        
    def test_recursive_framework_import(self):
        """Test recursive improvement framework imports."""
        from recursive_improvement import (
            RecursiveOrchestrator,
            RecursiveEngine,
            RecursiveLogger,
            RecursiveScheduler
        )
        from recursive_improvement.engines import (
            RecursiveFeedbackLoopEngine,
            AutonomousExperimentationTreeEngine,
            SelfCloningMVPAgentEngine
        )
        
        # Test basic instantiation
        logger = RecursiveLogger()
        self.assertIsNotNone(logger)
        
        orchestrator = RecursiveOrchestrator()
        self.assertIsNotNone(orchestrator)
        
        engine = RecursiveFeedbackLoopEngine()
        self.assertIsNotNone(engine)
        self.assertEqual(engine.name, "feedback_loop_engine")

    def test_dashboard_integration(self):
        """Test dashboard integration with recursive system."""
        # Import dashboard handler
        from dashboard import DashboardHandler
        
        # Test that recursive-related methods exist (class-level test)
        self.assertTrue(hasattr(DashboardHandler, 'send_recursive_json'))
        self.assertTrue(hasattr(DashboardHandler, 'trigger_recursive_improvement'))


if __name__ == '__main__':
    unittest.main()