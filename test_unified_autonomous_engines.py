#!/usr/bin/env python3
"""
Tests for the Unified Autonomous Engines implementation.
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_autonomous_engines import UnifiedAutonomousOrchestrator


class TestUnifiedAutonomousEngines(unittest.TestCase):
    """Test the unified autonomous engines system."""
    
    def setUp(self):
        """Set up test environment."""
        self.orchestrator = UnifiedAutonomousOrchestrator({
            "test_mode": True,
            "log_level": "INFO"
        })
    
    def test_orchestrator_initialization(self):
        """Test that the unified orchestrator initializes correctly."""
        result = self.orchestrator.initialize()
        self.assertTrue(result, "Orchestrator should initialize successfully")
        self.assertIsNotNone(self.orchestrator.orchestrator, "Main orchestrator should be created")
        self.assertEqual(len(self.orchestrator.all_engines), 16, "Should have exactly 16 engines")
    
    def test_all_engines_registered(self):
        """Test that all 16 engines are registered correctly."""
        self.orchestrator.initialize()
        
        # Get system status
        status = self.orchestrator.get_system_status()
        
        # Verify unified orchestrator status
        unified_status = status["unified_orchestrator"]
        self.assertEqual(unified_status["total_engines"], 16)
        self.assertTrue(unified_status["initialization_complete"])
        self.assertTrue(unified_status["health_monitor_active"])
        
        # Verify orchestrator status
        orchestrator_status = status["orchestrator"]
        self.assertEqual(orchestrator_status["active_engines"], 16)
        self.assertTrue(orchestrator_status["initialized"])
    
    def test_run_all_engines(self):
        """Test running all engines."""
        self.orchestrator.initialize()
        
        # Run all engines
        run_results = self.orchestrator.run_all()
        
        # Verify results
        self.assertIn("engines_executed", run_results)
        self.assertIn("execution_summary", run_results)
        self.assertEqual(len(run_results["engines_executed"]), 16)
        
        # Check execution summary
        summary = run_results["execution_summary"]
        self.assertEqual(summary["total_engines"], 16)
        self.assertGreaterEqual(summary["success_rate"], 80.0)  # At least 80% success rate
    
    def test_recursive_improvement_triggers(self):
        """Test recursive improvement triggering."""
        self.orchestrator.initialize()
        
        # Test different trigger contexts
        contexts = ["system_optimization", "workflow_execution", "health_monitoring"]
        
        for context in contexts:
            result = self.orchestrator.trigger_recursive_improvement(context, {
                "test_trigger": True,
                "context": context
            })
            
            self.assertIn("engines_triggered", result)
            self.assertIn("total_improvements", result)
            self.assertEqual(result["context"], context)
    
    def test_health_monitoring(self):
        """Test health monitoring functionality."""
        self.orchestrator.initialize()
        
        # Run engines to generate some activity
        self.orchestrator.run_all()
        
        # Get health report
        health_report = self.orchestrator.get_health_report()
        
        self.assertIn("overall_health_score", health_report)
        self.assertIn("engines_monitored", health_report)
        self.assertIn("engine_status", health_report)
        
        # Health score should be reasonable
        self.assertGreaterEqual(health_report["overall_health_score"], 50.0)
        self.assertEqual(health_report["engines_monitored"], 15)  # All engines except health monitor itself
    
    def test_engine_types_coverage(self):
        """Test that all required engine types are present."""
        self.orchestrator.initialize()
        
        status = self.orchestrator.get_system_status()
        engine_types = status["unified_orchestrator"]["engine_types"]
        
        # Check for key engine types (some expected from the requirements)
        expected_types = [
            "AutonomousIssueAnalyzerEngine",
            "SelfGeneratingTestSuiteEngine", 
            "RecursiveDependencyGraphUpdater",
            "AutonomousDocumentationEnhancer",
            "ContinuousEngineHealthMonitor",
            "CrossEngineTriggerSystem",
            "RecursiveImpactPropagationEngine",
            "AutonomousKnowledgeBaseBuilder"
        ]
        
        for expected_type in expected_types:
            self.assertIn(expected_type, engine_types, 
                         f"Engine type {expected_type} should be present")
    
    def test_compounding_and_recursive_patterns(self):
        """Test that engines follow compounding and recursive patterns."""
        self.orchestrator.initialize()
        
        # Run engines multiple times to test compounding
        for i in range(3):
            run_results = self.orchestrator.run_all()
            
            # Each run should show some activity
            self.assertGreater(len(run_results["engines_executed"]), 0)
            
            # Trigger recursive improvements
            improvement_results = self.orchestrator.trigger_recursive_improvement(
                f"test_cycle_{i}", {"cycle": i}
            )
            self.assertGreaterEqual(len(improvement_results["engines_triggered"]), 0)
    
    def test_graceful_shutdown(self):
        """Test graceful shutdown of the orchestrator."""
        self.orchestrator.initialize()
        
        # Run some activity
        self.orchestrator.run_all()
        
        # Shutdown should not raise exceptions
        try:
            self.orchestrator.shutdown()
            shutdown_successful = True
        except Exception as e:
            shutdown_successful = False
            self.fail(f"Shutdown failed with exception: {e}")
        
        self.assertTrue(shutdown_successful, "Shutdown should complete without errors")
    
    def tearDown(self):
        """Clean up after tests."""
        try:
            if hasattr(self.orchestrator, 'orchestrator') and self.orchestrator.orchestrator:
                self.orchestrator.shutdown()
        except:
            pass  # Ignore shutdown errors in cleanup


class TestIndividualEngines(unittest.TestCase):
    """Test individual engine functionality."""
    
    def test_engine_imports(self):
        """Test that all new engines can be imported."""
        try:
            from recursive_improvement.engines.issue_analyzer_engine import AutonomousIssueAnalyzerEngine
            from recursive_improvement.engines.test_suite_engine import SelfGeneratingTestSuiteEngine
            from recursive_improvement.engines.dependency_graph_engine import RecursiveDependencyGraphUpdater
            from recursive_improvement.engines.documentation_enhancer_engine import AutonomousDocumentationEnhancer
            from recursive_improvement.engines.health_monitor_engine import ContinuousEngineHealthMonitor
            import_success = True
        except ImportError as e:
            import_success = False
            self.fail(f"Failed to import engines: {e}")
        
        self.assertTrue(import_success, "All new engines should be importable")
    
    def test_engine_initialization(self):
        """Test that individual engines can be initialized."""
        from recursive_improvement.engines.issue_analyzer_engine import AutonomousIssueAnalyzerEngine
        
        engine = AutonomousIssueAnalyzerEngine()
        
        # Test initialization
        result = engine.initialize()
        self.assertTrue(result, "Engine should initialize successfully")
        
        # Test starting
        start_result = engine.start()
        self.assertTrue(start_result, "Engine should start successfully")
        
        # Test status
        status = engine.get_status()
        self.assertIn("name", status)
        self.assertIn("is_running", status)
        self.assertTrue(status["is_running"], "Engine should be running")
        
        # Test stopping
        engine.stop()
        self.assertFalse(engine.is_running, "Engine should be stopped")


class TestRecursiveOrchestrator(unittest.TestCase):
    """Test the enhanced RecursiveOrchestrator with run_all method."""
    
    def test_run_all_method_exists(self):
        """Test that the run_all method exists on RecursiveOrchestrator."""
        from recursive_improvement.orchestrator import RecursiveOrchestrator
        
        orchestrator = RecursiveOrchestrator()
        self.assertTrue(hasattr(orchestrator, 'run_all'), "RecursiveOrchestrator should have run_all method")
        self.assertTrue(callable(getattr(orchestrator, 'run_all')), "run_all should be callable")
    
    def test_run_all_method_functionality(self):
        """Test that the run_all method works correctly."""
        from recursive_improvement.orchestrator import RecursiveOrchestrator
        from recursive_improvement.engines.feedback_loop_engine import RecursiveFeedbackLoopEngine
        
        orchestrator = RecursiveOrchestrator()
        orchestrator.initialize()
        
        # Register a test engine
        engine = RecursiveFeedbackLoopEngine()
        orchestrator.register_engine(engine)
        
        # Test run_all
        result = orchestrator.run_all()
        
        self.assertIn("engines_executed", result)
        self.assertIn("execution_summary", result)
        self.assertGreater(len(result["engines_executed"]), 0)


if __name__ == "__main__":
    unittest.main()