#!/usr/bin/env python3
"""
Comprehensive test suite for PR management system
"""

import unittest
import json
import sys
import os

# Add the parent directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pr_manager import PRManager, PRCategory, ConflictLevel
from integration import (
    handle_pr_management,
    execute_comprehensive_pr_handling,
    show_pr_integration_status
)


class TestPRManager(unittest.TestCase):
    """Test cases for PR Manager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = PRManager()
    
    def test_pr_metadata_loading(self):
        """Test that PR metadata is loaded correctly"""
        self.assertEqual(len(self.manager.prs_metadata), 8)
        self.assertIn(29, self.manager.prs_metadata)
        self.assertIn(15, self.manager.prs_metadata)
        
        # Check specific PR data
        pr_29 = self.manager.prs_metadata[29]
        self.assertEqual(pr_29.category, PRCategory.RECURSIVE_IMPROVEMENT)
        self.assertEqual(len(pr_29.features), 10)
        self.assertEqual(pr_29.integration_priority, 9)
    
    def test_conflict_analysis(self):
        """Test conflict analysis functionality"""
        conflicts = self.manager.analyze_conflicts()
        
        # Check conflict structure
        self.assertIn('high_conflicts', conflicts)
        self.assertIn('medium_conflicts', conflicts)
        self.assertIn('low_conflicts', conflicts)
        self.assertIn('conflict_groups', conflicts)
        self.assertIn('resolution_strategies', conflicts)
        
        # Verify we have expected conflicts
        high_conflicts = conflicts['high_conflicts']
        self.assertGreater(len(high_conflicts), 0)
        
        # Check conflict data structure
        for conflict in high_conflicts:
            self.assertIn('pr1', conflict)
            self.assertIn('pr2', conflict)
            self.assertIn('level', conflict)
            self.assertIn('reason', conflict)
    
    def test_integration_plan(self):
        """Test integration plan creation"""
        plan = self.manager.create_integration_plan()
        
        # Check plan structure
        self.assertIn('integration_order', plan)
        self.assertIn('phases', plan)
        self.assertIn('timeline', plan)
        self.assertIn('risks', plan)
        
        # Verify integration order starts with bug fixes
        integration_order = plan['integration_order']
        self.assertEqual(integration_order[0], 15)  # Bug fixes first
        self.assertEqual(integration_order[1], 20)  # Documentation second
        
        # Check phases
        phases = plan['phases']
        self.assertIn('Phase 1 - Foundation', phases)
        phase_1 = phases['Phase 1 - Foundation']
        self.assertEqual(phase_1['prs'], [15, 20])
    
    def test_consolidation_report(self):
        """Test consolidation report generation"""
        report = self.manager.generate_consolidation_report()
        
        # Check report structure
        required_keys = [
            'timestamp', 'total_prs', 'prs_ready_to_merge',
            'total_lines_added', 'total_lines_deleted',
            'conflict_analysis', 'integration_plan',
            'pr_metadata', 'recommendations'
        ]
        
        for key in required_keys:
            self.assertIn(key, report)
        
        # Verify data accuracy
        self.assertEqual(report['total_prs'], 8)
        self.assertEqual(report['prs_ready_to_merge'], 4)
        self.assertGreater(report['total_lines_added'], 0)
        self.assertIsInstance(report['recommendations'], list)
        self.assertGreater(len(report['recommendations']), 0)
    
    def test_export_report(self):
        """Test report export functionality"""
        filename = self.manager.export_report()
        self.assertTrue(os.path.exists(filename))
        
        # Verify file contents
        with open(filename, 'r') as f:
            data = json.load(f)
            self.assertIn('total_prs', data)
            self.assertEqual(data['total_prs'], 8)
        
        # Cleanup
        os.remove(filename)


class TestPRIntegration(unittest.TestCase):
    """Test PR integration with main system"""
    
    def test_pr_management_commands(self):
        """Test PR management command handling"""
        # Test analyze command
        result = handle_pr_management('analyze')
        self.assertEqual(result, 0)
        
        # Test plan command
        result = handle_pr_management('plan')
        self.assertEqual(result, 0)
        
        # Test export command
        result = handle_pr_management('export')
        self.assertEqual(result, 0)
        
        # Test invalid command
        result = handle_pr_management('invalid')
        self.assertEqual(result, 1)
    
    def test_comprehensive_pr_handling(self):
        """Test comprehensive PR handling process"""
        result = execute_comprehensive_pr_handling()
        self.assertEqual(result, 0)
    
    def test_pr_integration_status(self):
        """Test PR integration status reporting"""
        result = show_pr_integration_status()
        self.assertEqual(result, 0)


class TestPRConflictResolution(unittest.TestCase):
    """Test conflict resolution strategies"""
    
    def setUp(self):
        self.manager = PRManager()
    
    def test_monetization_conflict_identification(self):
        """Test identification of monetization conflicts"""
        conflicts = self.manager.analyze_conflicts()
        
        # Should identify conflict between PR #24 and #27 (both monetization)
        high_conflicts = conflicts['high_conflicts']
        monetization_conflict = None
        
        for conflict in high_conflicts:
            if (conflict['pr1'] == 24 and conflict['pr2'] == 27) or \
               (conflict['pr1'] == 27 and conflict['pr2'] == 24):
                monetization_conflict = conflict
                break
        
        self.assertIsNotNone(monetization_conflict, "Should identify monetization PR conflict")
    
    def test_recursive_improvement_conflict_identification(self):
        """Test identification of recursive improvement conflicts"""
        conflicts = self.manager.analyze_conflicts()
        
        # Should identify conflicts between recursive improvement PRs
        high_conflicts = conflicts['high_conflicts']
        recursive_conflicts = [
            c for c in high_conflicts 
            if (c['pr1'] in [23, 25, 29] and c['pr2'] in [23, 25, 29])
        ]
        
        self.assertGreater(len(recursive_conflicts), 0, 
                          "Should identify recursive improvement conflicts")
    
    def test_resolution_strategies(self):
        """Test resolution strategy generation"""
        conflicts = self.manager.analyze_conflicts()
        strategies = conflicts['resolution_strategies']
        
        self.assertIn('general', strategies)
        self.assertIsInstance(strategies['general'], str)
        self.assertGreater(len(strategies), 0)


class TestIntegrationPhases(unittest.TestCase):
    """Test integration phase planning"""
    
    def setUp(self):
        self.manager = PRManager()
    
    def test_phase_dependencies(self):
        """Test that phases have correct dependencies"""
        plan = self.manager.create_integration_plan()
        phases = plan['phases']
        
        # Phase 1 should have no dependencies
        phase_1 = phases['Phase 1 - Foundation']
        self.assertEqual(phase_1['dependencies'], [])
        
        # Later phases should have dependencies
        phase_2 = phases['Phase 2 - Framework']
        self.assertIn('Phase 1', phase_2['dependencies'])
        
        # Final phase should depend on multiple phases
        phase_5 = phases['Phase 5 - Comprehensive System']
        self.assertGreater(len(phase_5['dependencies']), 1)
    
    def test_timeline_estimation(self):
        """Test timeline estimation accuracy"""
        plan = self.manager.create_integration_plan()
        timeline = plan['timeline']
        
        # Should have realistic timeline estimates
        parallel_days = timeline['parallel_execution_days']
        sequential_days = float(timeline['sequential_execution_days'])
        
        self.assertIsInstance(parallel_days, str)
        self.assertGreater(sequential_days, 0)
        self.assertLess(sequential_days, 20)  # Should be reasonable


def run_comprehensive_pr_test():
    """Run comprehensive PR management test"""
    print("🧪 Running Comprehensive PR Management Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPRManager))
    suite.addTests(loader.loadTestsFromTestCase(TestPRIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestPRConflictResolution))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationPhases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.splitlines()[-1]}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.splitlines()[-1]}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    status = "✅ All tests passed!" if success else "❌ Some tests failed"
    print(f"\n{status}")
    
    return success


if __name__ == '__main__':
    success = run_comprehensive_pr_test()
    sys.exit(0 if success else 1)