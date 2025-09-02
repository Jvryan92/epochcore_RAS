"""
Test Complex Autonomy Innovations

This test demonstrates the advanced autonomous notification resolution capabilities
implemented as part of the Complex Autonomy Innovation framework.
"""

import unittest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from integration import (
    initialize_recursive_improvement_system,
    trigger_autonomous_resolution_test,
    get_complex_autonomy_status
)


class TestComplexAutonomyInnovations(unittest.TestCase):
    """Test the complex autonomy innovation features."""
    
    def setUp(self):
        """Set up test environment."""
        self.orchestrator = initialize_recursive_improvement_system()
    
    def test_complex_autonomy_initialization(self):
        """Test that complex autonomy engines are properly initialized."""
        self.assertIsNotNone(self.orchestrator, "Orchestrator should be initialized")
        
        # Check that all 19 engines are registered (15 original + 4 complex autonomy)
        status = get_complex_autonomy_status()
        self.assertIsInstance(status, dict, "Status should be a dictionary")
        
        # Should have original engines plus new complex autonomy engines
        total_engines = status.get('total_engines', 0)
        self.assertGreaterEqual(total_engines, 19, f"Should have at least 19 engines, got {total_engines}")
        
        # Check complex autonomy specific engines
        complex_autonomy_engines = status.get('complex_autonomy_engines', 0)
        self.assertEqual(complex_autonomy_engines, 4, "Should have exactly 4 complex autonomy engines")
    
    def test_autonomous_notification_resolution(self):
        """Test autonomous notification resolution capabilities."""
        result = trigger_autonomous_resolution_test()
        
        self.assertEqual(result['status'], 'success', "Autonomous resolution test should succeed")
        self.assertIn('results', result, "Should contain resolution results")
        self.assertIn('autonomous_status', result, "Should contain autonomous status")
        
        # Check that autonomous capabilities are available
        autonomous_status = result['autonomous_status']
        self.assertTrue(autonomous_status.get('notification_intelligence_available', False), 
                       "Notification intelligence should be available")
        self.assertTrue(autonomous_status.get('notification_resolver_available', False),
                       "Notification resolver should be available") 
        self.assertTrue(autonomous_status.get('resolution_validator_available', False),
                       "Resolution validator should be available")
        self.assertTrue(autonomous_status.get('predictive_engine_available', False),
                       "Predictive engine should be available")
    
    def test_complex_autonomy_status_structure(self):
        """Test the structure and completeness of complex autonomy status."""
        status = get_complex_autonomy_status()
        
        # Check main structure
        required_keys = [
            'system_overview',
            'autonomous_capabilities', 
            'notification_intelligence',
            'autonomous_resolver',
            'resolution_validator',
            'predictive_engine',
            'innovation_summary'
        ]
        
        for key in required_keys:
            self.assertIn(key, status, f"Status should contain '{key}'")
        
        # Check innovation summary
        innovation_summary = status.get('innovation_summary', {})
        summary_keys = ['autonomous_resolutions', 'prevented_notifications', 'total_improvements', 'uptime_seconds']
        
        for key in summary_keys:
            self.assertIn(key, innovation_summary, f"Innovation summary should contain '{key}'")
    
    def test_autonomous_capabilities_enabled(self):
        """Test that autonomous capabilities are properly enabled."""
        if self.orchestrator:
            autonomous_status = self.orchestrator.get_autonomous_status()
            
            # Check that autonomous features are enabled
            self.assertTrue(autonomous_status.get('autonomous_resolution_enabled', False),
                           "Autonomous resolution should be enabled by default")
            self.assertTrue(autonomous_status.get('auto_learning_enabled', False),
                           "Auto learning should be enabled by default")
            self.assertTrue(autonomous_status.get('predictive_prevention_enabled', False),
                           "Predictive prevention should be enabled by default")
    
    def test_notification_processing_pipeline(self):
        """Test the complete notification processing pipeline."""
        if self.orchestrator:
            # Create a test notification
            test_notification = {
                "id": "pipeline_test_001",
                "category": "error",
                "severity": "high", 
                "content": "Test error for pipeline validation",
                "source": "test_system",
                "timestamp": "2025-09-02T22:05:00Z"
            }
            
            # Trigger autonomous resolution
            result = self.orchestrator.trigger_autonomous_notification_resolution(test_notification)
            
            # Verify the result structure
            self.assertIsInstance(result, dict, "Resolution result should be a dictionary")
            self.assertIn('triggered', result, "Result should indicate if resolution was triggered")
            self.assertIn('notification', result, "Result should contain the original notification")
            self.assertTrue(result.get('triggered', False), "Resolution should be triggered")
    
    def tearDown(self):
        """Clean up test environment."""
        if self.orchestrator:
            # Clean shutdown
            pass


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)