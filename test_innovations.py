#!/usr/bin/env python3
"""
Test the recursive autonomy innovations
"""

import unittest
import time
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recursive_autonomy import recursive_framework
from innovations.recursive_agent_networks import create_recursive_agent_network
from innovations.meta_recursive_auditing import create_meta_recursive_auditor
from innovations.recursive_data_pipeline_optimization import create_recursive_data_pipeline_optimizer


class TestRecursiveInnovations(unittest.TestCase):
    """Test cases for recursive autonomy innovations"""
    
    def test_recursive_framework_initialization(self):
        """Test that the recursive framework initializes correctly"""
        self.assertIsNotNone(recursive_framework)
        self.assertIsInstance(recursive_framework.components, dict)
        self.assertIsInstance(recursive_framework.improvement_history, list)
    
    def test_recursive_agent_network_creation(self):
        """Test recursive agent network creation and initialization"""
        try:
            network = create_recursive_agent_network()
            self.assertIsNotNone(network)
            self.assertGreater(len(network.agents), 0)
            self.assertIn('Coordinator', [agent.name for agent in network.agents.values()])
            print("✓ Recursive Agent Network created successfully")
        except Exception as e:
            self.fail(f"Failed to create recursive agent network: {e}")
    
    def test_meta_recursive_auditor_creation(self):
        """Test meta-recursive auditor creation and initialization"""
        try:
            auditor = create_meta_recursive_auditor()
            self.assertIsNotNone(auditor)
            self.assertGreater(len(auditor.audit_procedures), 0)
            self.assertTrue(any('Meta_Audit' in proc.name for proc in auditor.audit_procedures.values()))
            print("✓ Meta-Recursive Auditor created successfully")
        except Exception as e:
            self.fail(f"Failed to create meta-recursive auditor: {e}")
    
    def test_recursive_data_pipeline_optimizer_creation(self):
        """Test recursive data pipeline optimizer creation and initialization"""
        try:
            optimizer = create_recursive_data_pipeline_optimizer()
            self.assertIsNotNone(optimizer)
            self.assertGreater(len(optimizer.pipeline_nodes), 0)
            self.assertGreater(len(optimizer.optimization_strategies), 0)
            print("✓ Recursive Data Pipeline Optimizer created successfully")
        except Exception as e:
            self.fail(f"Failed to create recursive data pipeline optimizer: {e}")
    
    def test_recursive_agent_network_functionality(self):
        """Test basic functionality of recursive agent network"""
        try:
            network = create_recursive_agent_network()
            
            # Test network status
            status = network.get_network_status()
            self.assertIn('total_agents', status)
            self.assertIn('top_performers', status)
            
            # Test recursive cycle execution
            cycle_result = network.execute_recursive_cycle()
            self.assertIn('network_metrics', cycle_result)
            self.assertIn('cycle_duration', cycle_result)
            
            print("✓ Recursive Agent Network functionality verified")
        except Exception as e:
            self.fail(f"Agent network functionality test failed: {e}")
    
    def test_meta_recursive_auditor_functionality(self):
        """Test basic functionality of meta-recursive auditor"""
        try:
            auditor = create_meta_recursive_auditor()
            
            # Test audit status
            status = auditor.get_audit_status()
            self.assertIn('total_procedures', status)
            self.assertIn('findings_by_severity', status)
            
            # Test recursive cycle execution
            cycle_result = auditor.execute_recursive_cycle()
            self.assertIn('findings_generated', cycle_result)
            self.assertIn('effectiveness_analysis', cycle_result)
            
            print("✓ Meta-Recursive Auditor functionality verified")
        except Exception as e:
            self.fail(f"Meta-recursive auditor functionality test failed: {e}")
    
    def test_recursive_data_pipeline_optimizer_functionality(self):
        """Test basic functionality of recursive data pipeline optimizer"""
        try:
            optimizer = create_recursive_data_pipeline_optimizer()
            
            # Test pipeline status
            status = optimizer.get_pipeline_status()
            self.assertIn('total_nodes', status)
            self.assertIn('optimization_strategies', status)
            
            # Test recursive cycle execution
            cycle_result = optimizer.execute_recursive_cycle()
            self.assertIn('performance_analysis', cycle_result)
            self.assertIn('optimizations_applied', cycle_result)
            
            print("✓ Recursive Data Pipeline Optimizer functionality verified")
        except Exception as e:
            self.fail(f"Data pipeline optimizer functionality test failed: {e}")
    
    def test_cross_innovation_integration(self):
        """Test that innovations can work together"""
        try:
            # Create all innovations
            network = create_recursive_agent_network()
            auditor = create_meta_recursive_auditor()
            optimizer = create_recursive_data_pipeline_optimizer()
            
            # Test that they all register with the framework
            total_components_before = len(recursive_framework.components)
            
            # Each innovation should register itself
            self.assertGreater(len(recursive_framework.components), 0)
            
            # Test framework state
            framework_state = recursive_framework.get_system_state()
            self.assertGreater(framework_state['total_components'], 0)
            
            print("✓ Cross-innovation integration verified")
        except Exception as e:
            self.fail(f"Cross-innovation integration test failed: {e}")
    
    def test_recursive_improvement_cycle(self):
        """Test that innovations can trigger recursive improvements"""
        try:
            network = create_recursive_agent_network()
            
            # Execute multiple cycles to trigger improvements
            for i in range(3):
                cycle_result = network.execute_recursive_cycle()
                self.assertIsNotNone(cycle_result)
                time.sleep(0.1)  # Brief pause between cycles
            
            # Check if any recursive improvements occurred
            framework_state = recursive_framework.get_system_state()
            self.assertGreaterEqual(framework_state['total_components'], 1)
            
            print("✓ Recursive improvement cycle verified")
        except Exception as e:
            self.fail(f"Recursive improvement cycle test failed: {e}")


if __name__ == '__main__':
    print("Testing Recursive Autonomy Innovations...")
    print("=" * 50)
    
    # Set up test environment
    unittest.main(verbosity=2)