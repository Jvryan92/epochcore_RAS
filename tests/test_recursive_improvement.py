"""Tests for recursive improvement framework integration"""
import unittest
from datetime import datetime


class TestRecursiveImprovement(unittest.TestCase):
    """Test cases for the recursive improvement framework."""

    def test_framework_import(self):
        """Test that we can import the framework."""
        from recursive_improvement import get_framework, RecursiveImprovementFramework
        self.assertIsNotNone(get_framework)
        self.assertIsNotNone(RecursiveImprovementFramework)

    def test_framework_initialization(self):
        """Test framework initialization."""
        from recursive_improvement import get_framework
        framework = get_framework()
        self.assertIsNotNone(framework)
        
        status = framework.get_status()
        self.assertIsInstance(status, dict)
        self.assertIn("autonomous_mode", status)
        self.assertIn("registered_subsystems", status)

    def test_subsystem_modules_import(self):
        """Test that all subsystem modules can be imported."""
        from agent_management import initialize_agent_management
        from dag_management import initialize_dag_management
        from capsule_metadata import initialize_capsule_management
        from ethical_reflection import initialize_ethical_reflection
        from ml_optimization import initialize_ml_optimization
        
        self.assertIsNotNone(initialize_agent_management)
        self.assertIsNotNone(initialize_dag_management)
        self.assertIsNotNone(initialize_capsule_management)
        self.assertIsNotNone(initialize_ethical_reflection)
        self.assertIsNotNone(initialize_ml_optimization)

    def test_agent_management_initialization(self):
        """Test agent management subsystem."""
        from agent_management import initialize_agent_management, get_agent_status
        
        hook = initialize_agent_management()
        self.assertEqual(hook.name, "agents")
        self.assertTrue(hook.enabled)
        self.assertEqual(len(hook.strategies), 2)
        
        status = get_agent_status()
        self.assertIn("total_agents", status)
        self.assertIn("average_performance", status)
        self.assertGreater(status["total_agents"], 0)

    def test_dag_management_initialization(self):
        """Test DAG management subsystem."""
        from dag_management import initialize_dag_management, get_dag_status
        
        hook = initialize_dag_management()
        self.assertEqual(hook.name, "dags")
        self.assertTrue(hook.enabled)
        self.assertEqual(len(hook.strategies), 2)
        
        status = get_dag_status()
        self.assertIn("total_workflows", status)
        self.assertIn("avg_success_rate", status)
        self.assertGreater(status["total_workflows"], 0)

    def test_capsule_management_initialization(self):
        """Test capsule management subsystem."""
        from capsule_metadata import initialize_capsule_management, get_capsule_status
        
        hook = initialize_capsule_management()
        self.assertEqual(hook.name, "capsules")
        self.assertTrue(hook.enabled)
        self.assertEqual(len(hook.strategies), 2)
        
        status = get_capsule_status()
        self.assertIn("total_capsules", status)
        self.assertIn("integrity_rate", status)
        self.assertGreater(status["total_capsules"], 0)

    def test_ethical_reflection_initialization(self):
        """Test ethical reflection subsystem."""
        from ethical_reflection import initialize_ethical_reflection, get_ethical_status
        
        hook = initialize_ethical_reflection()
        self.assertEqual(hook.name, "ethics")
        self.assertTrue(hook.enabled)
        self.assertEqual(len(hook.strategies), 2)
        
        status = get_ethical_status()
        self.assertIn("total_rules", status)
        self.assertIn("active_rules", status)
        self.assertGreater(status["total_rules"], 0)

    def test_ml_optimization_initialization(self):
        """Test ML optimization subsystem."""
        from ml_optimization import initialize_ml_optimization, get_ml_status
        
        hook = initialize_ml_optimization()
        self.assertEqual(hook.name, "ml")
        self.assertTrue(hook.enabled)
        self.assertEqual(len(hook.strategies), 2)
        
        status = get_ml_status()
        self.assertIn("system_metrics", status)
        self.assertGreater(status["system_metrics"]["total_models"], 0)

    def test_manual_improvement_trigger(self):
        """Test manual improvement triggering."""
        from recursive_improvement import get_framework
        from agent_management import initialize_agent_management
        
        framework = get_framework()
        hook = initialize_agent_management()
        
        # Test specific subsystem improvement
        result = framework.run_manual_improvement("agents")
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")
        
        # Check that improvements were recorded
        metrics = framework.get_metrics()
        improvements = metrics.get_recent_improvements(1)
        self.assertGreater(len(improvements), 0)

    def test_framework_status_after_improvements(self):
        """Test framework status after running improvements."""
        from recursive_improvement import get_framework
        from agent_management import initialize_agent_management
        from dag_management import initialize_dag_management
        
        framework = get_framework()
        agent_hook = initialize_agent_management()
        dag_hook = initialize_dag_management()
        
        # Run improvements
        result = framework.run_manual_improvement()
        self.assertEqual(result["status"], "success")
        
        # Check framework status
        status = framework.get_status()
        self.assertGreaterEqual(len(status["registered_subsystems"]), 2)  # At least 2, could be more from other tests
        self.assertGreater(status["total_improvements"], 0)

    def test_autonomous_mode_control(self):
        """Test autonomous mode start/stop functionality."""
        from recursive_improvement import get_framework
        
        framework = get_framework()
        
        # Test starting autonomous mode
        initial_status = framework.get_status()
        self.assertFalse(initial_status["autonomous_mode"])
        
        framework.start_autonomous_mode()
        active_status = framework.get_status()
        self.assertTrue(active_status["autonomous_mode"])
        
        # Test stopping autonomous mode
        framework.stop_autonomous_mode()
        final_status = framework.get_status()
        self.assertFalse(final_status["autonomous_mode"])

    def test_integration_functions(self):
        """Test the updated integration functions."""
        from integration import setup_demo, run_workflow, validate_system
        
        # Test setup demo
        setup_result = setup_demo()
        self.assertEqual(setup_result["status"], "success")
        self.assertIn("improvement_hooks", setup_result)
        self.assertGreaterEqual(setup_result["improvement_hooks"], 5)
        
        # Test workflow execution
        workflow_result = run_workflow()
        self.assertEqual(workflow_result["status"], "success")
        self.assertIn("subsystems_improved", workflow_result)
        
        # Test validation
        validation_result = validate_system()
        self.assertEqual(validation_result["status"], "valid")


if __name__ == '__main__':
    unittest.main()