"""Tests for the monetization pipeline module."""
import unittest
from unittest.mock import patch
from datetime import datetime

from monetization_pipeline import (
    MonetizationPipeline,
    create_monetization_workflow,
    execute_monetization_pipeline
)


class TestMonetizationPipeline(unittest.TestCase):
    """Test cases for MonetizationPipeline class."""

    def setUp(self):
        """Set up test fixtures."""
        self.pipeline = MonetizationPipeline()

    def test_pipeline_initialization(self):
        """Test that pipeline initializes correctly."""
        self.assertIsInstance(self.pipeline.pipeline_state, dict)
        self.assertEqual(self.pipeline.pipeline_state["steps_completed"], 0)
        self.assertEqual(self.pipeline.pipeline_state["total_monetary_value"], 0.0)
        self.assertEqual(self.pipeline.pipeline_state["compounding_factor"], 1.0)

    def test_step_1_feature_gating(self):
        """Test step 1: feature gating implementation."""
        result = self.pipeline.step_1_feature_gating()
        
        self.assertIsInstance(result, dict)
        self.assertIn("monetary_impact", result)
        self.assertIn("multiplier", result)
        self.assertIn("user_segments", result)
        self.assertGreater(result["monetary_impact"], 0)
        self.assertEqual(result["multiplier"], 1.15)
        self.assertEqual(result["automated_gates"], 12)

    def test_step_2_dynamic_bundling(self):
        """Test step 2: dynamic bundling and upsells."""
        # First run step 1 to set up user segments
        self.pipeline.step_1_feature_gating()
        result = self.pipeline.step_2_dynamic_bundling()
        
        self.assertIsInstance(result, dict)
        self.assertIn("monetary_impact", result)
        self.assertIn("multiplier", result)
        self.assertGreater(result["monetary_impact"], 0)
        self.assertEqual(result["multiplier"], 1.25)
        self.assertTrue(result["dynamic_pricing"])

    def test_step_3_personalized_subscriptions(self):
        """Test step 3: personalized subscription offers."""
        result = self.pipeline.step_3_personalized_subscriptions()
        
        self.assertIsInstance(result, dict)
        self.assertIn("monetary_impact", result)
        self.assertIn("multiplier", result)
        self.assertIn("personalization_accuracy", result)
        self.assertGreater(result["monetary_impact"], 0)
        self.assertEqual(result["multiplier"], 1.35)
        self.assertEqual(result["active_campaigns"], 24)

    def test_step_4_referral_engine(self):
        """Test step 4: referral engine activation."""
        result = self.pipeline.step_4_referral_engine()
        
        self.assertIsInstance(result, dict)
        self.assertIn("monetary_impact", result)
        self.assertIn("viral_coefficient", result)
        self.assertGreater(result["monetary_impact"], 0)
        self.assertEqual(result["multiplier"], 1.30)
        self.assertGreater(result["viral_coefficient"], 1.0)

    def test_step_5_content_flywheel(self):
        """Test step 5: content flywheel for marketing."""
        result = self.pipeline.step_5_content_flywheel()
        
        self.assertIsInstance(result, dict)
        self.assertIn("monetary_impact", result)
        self.assertIn("organic_traffic_monthly", result)
        self.assertGreater(result["monetary_impact"], 0)
        self.assertEqual(result["multiplier"], 1.40)
        self.assertEqual(result["content_pieces_monthly"], 200)

    def test_step_6_pricing_optimization(self):
        """Test step 6: autonomous pricing optimization."""
        result = self.pipeline.step_6_pricing_optimization()
        
        self.assertIsInstance(result, dict)
        self.assertIn("monetary_impact", result)
        self.assertIn("optimization_uplift", result)
        self.assertGreater(result["monetary_impact"], 0)
        self.assertEqual(result["multiplier"], 1.25)
        self.assertGreater(result["pricing_algorithms"], 0)

    def test_step_7_asset_tagging(self):
        """Test step 7: automated asset tagging for reuse."""
        result = self.pipeline.step_7_asset_tagging()
        
        self.assertIsInstance(result, dict)
        self.assertIn("monetary_impact", result)
        self.assertIn("assets_tagged", result)
        self.assertGreater(result["monetary_impact"], 0)
        self.assertEqual(result["multiplier"], 1.20)
        self.assertGreater(result["assets_tagged"], 0)

    def test_step_8_auto_debrief(self):
        """Test step 8: auto-debrief and experiment suggestion."""
        # Run a few previous steps to have data for analysis
        self.pipeline.step_1_feature_gating()
        self.pipeline.step_2_dynamic_bundling()
        
        result = self.pipeline.step_8_auto_debrief()
        
        self.assertIsInstance(result, dict)
        self.assertIn("monetary_impact", result)
        self.assertIn("experiments_suggested", result)
        self.assertGreater(result["monetary_impact"], 0)
        self.assertEqual(result["multiplier"], 1.15)
        self.assertGreater(result["experiments_suggested"], 0)

    def test_step_9_recursive_workflows(self):
        """Test step 9: recursive workflow creation for manual actions."""
        result = self.pipeline.step_9_recursive_workflows()
        
        self.assertIsInstance(result, dict)
        self.assertIn("monetary_impact", result)
        self.assertIn("workflows_automated", result)
        self.assertGreater(result["monetary_impact"], 0)
        self.assertEqual(result["multiplier"], 1.30)
        self.assertGreater(result["workflows_automated"], 0)

    def test_step_10_kpi_mutation(self):
        """Test step 10: KPI mutation and automated improvement."""
        # Run previous steps to have performance data
        self.pipeline.step_1_feature_gating()
        self.pipeline.step_2_dynamic_bundling()
        
        result = self.pipeline.step_10_kpi_mutation()
        
        self.assertIsInstance(result, dict)
        self.assertIn("monetary_impact", result)
        self.assertIn("evolution_factor", result)
        self.assertGreater(result["monetary_impact"], 0)
        self.assertEqual(result["multiplier"], 1.50)  # Highest multiplier
        self.assertGreater(result["mutation_algorithms"], 0)

    def test_complete_pipeline_execution(self):
        """Test complete pipeline execution with all steps."""
        result = self.pipeline.execute_complete_pipeline()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["steps_completed"], 10)
        self.assertGreater(result["final_monetary_value"], 0)
        self.assertGreater(result["compounding_factor"], 1.0)
        self.assertIn("pipeline_state", result)
        self.assertIn("step_outputs", result)

    def test_get_pipeline_metrics(self):
        """Test pipeline metrics retrieval."""
        # Run a few steps first
        self.pipeline.step_1_feature_gating()
        self.pipeline.step_2_dynamic_bundling()
        
        metrics = self.pipeline.get_pipeline_metrics()
        
        self.assertIsInstance(metrics, dict)
        self.assertIn("pipeline_status", metrics)
        self.assertIn("total_monetary_value", metrics)
        self.assertIn("compounding_factor", metrics)
        self.assertIn("steps_completed", metrics)
        self.assertIn("automation_level", metrics)
        self.assertIn("roi_percentage", metrics)

    def test_factory_function(self):
        """Test factory function for creating pipeline instances."""
        pipeline = create_monetization_workflow()
        self.assertIsInstance(pipeline, MonetizationPipeline)

    def test_execute_monetization_pipeline_function(self):
        """Test standalone pipeline execution function."""
        with patch('builtins.print'):  # Suppress print output during test
            result = execute_monetization_pipeline()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["steps_completed"], 10)
        self.assertGreater(result["final_monetary_value"], 0)

    def test_compounding_effects(self):
        """Test that each step increases the compounding factor."""
        initial_factor = self.pipeline.pipeline_state["compounding_factor"]
        
        result1 = self.pipeline.step_1_feature_gating()
        self.pipeline._update_pipeline_state(result1)
        factor_after_step_1 = self.pipeline.pipeline_state["compounding_factor"]
        
        result2 = self.pipeline.step_2_dynamic_bundling()
        self.pipeline._update_pipeline_state(result2)
        factor_after_step_2 = self.pipeline.pipeline_state["compounding_factor"]
        
        self.assertGreater(factor_after_step_1, initial_factor)
        self.assertGreater(factor_after_step_2, factor_after_step_1)

    def test_monetary_value_accumulation(self):
        """Test that monetary value accumulates across steps."""
        initial_value = self.pipeline.pipeline_state["total_monetary_value"]
        
        result1 = self.pipeline.step_1_feature_gating()
        self.pipeline._update_pipeline_state(result1)
        value_after_step_1 = self.pipeline.pipeline_state["total_monetary_value"]
        
        result2 = self.pipeline.step_2_dynamic_bundling()
        self.pipeline._update_pipeline_state(result2)
        value_after_step_2 = self.pipeline.pipeline_state["total_monetary_value"]
        
        self.assertGreater(value_after_step_1, initial_value)
        self.assertGreater(value_after_step_2, value_after_step_1)

    def test_pipeline_state_persistence(self):
        """Test that pipeline state is maintained between steps."""
        self.pipeline.step_1_feature_gating()
        
        # Check that user segments are stored in pipeline state
        self.assertIn("user_segments", self.pipeline.pipeline_state)
        user_segments = self.pipeline.pipeline_state["user_segments"]
        self.assertIsInstance(user_segments, dict)
        self.assertGreater(len(user_segments), 0)

    def test_automation_levels(self):
        """Test that automation levels are properly tracked."""
        result = self.pipeline.step_4_referral_engine()
        self.assertIn("automation_level", result)
        self.assertGreaterEqual(result["automation_level"], 0.9)

        result = self.pipeline.step_8_auto_debrief()
        self.assertIn("automation_level", result)
        self.assertGreaterEqual(result["automation_level"], 0.9)


class TestIntegrationWithExistingSystem(unittest.TestCase):
    """Test integration with existing EpochCore RAS system."""

    def test_import_availability(self):
        """Test that monetization pipeline can be imported."""
        from monetization_pipeline import MonetizationPipeline
        self.assertTrue(MonetizationPipeline)

    def test_no_conflicts_with_existing_system(self):
        """Test that monetization pipeline doesn't conflict with existing system."""
        # This test ensures our monetization pipeline doesn't break existing functionality
        from integration import setup_demo, run_workflow, get_status, validate_system
        
        # Test existing functions still work
        demo_result = setup_demo()
        self.assertEqual(demo_result["status"], "success")
        
        workflow_result = run_workflow()
        self.assertEqual(workflow_result["status"], "success")
        
        status_result = get_status()
        self.assertEqual(status_result["status"], "operational")
        
        validation_result = validate_system()
        self.assertEqual(validation_result["status"], "valid")


if __name__ == '__main__':
    unittest.main()