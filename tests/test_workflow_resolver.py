#!/usr/bin/env python3
"""
Test Suite for Workflow Conflict Resolver
EpochCore RAS Enhanced PR Management System
"""

import unittest
import asyncio
import tempfile
import shutil
import os
import json
from datetime import datetime
from pathlib import Path

from workflow_conflict_resolver import (
    WorkflowConflictResolver, 
    PRConflictInfo, 
    MergeQueueItem
)


class TestWorkflowConflictResolver(unittest.TestCase):
    """Test cases for WorkflowConflictResolver."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "test_config.yaml")
        
        # Create test configuration
        test_config = {
            "merge_queue": {
                "max_concurrent_merges": 2,
                "priority_weights": {"hotfix": 10, "feature": 5},
                "merge_window": {"start_hour": 0, "end_hour": 23}
            },
            "conflict_resolution": {
                "auto_resolution_strategies": {"documentation": "prefer_incoming"},
                "conflict_severity_thresholds": {"low": 5, "medium": 15},
                "auto_resolve_timeout": 300
            },
            "quality_gates": {
                "required_checks": ["lint", "test"],
                "failure_handling": {"required_failure": "block_merge"}
            }
        }
        
        # Save test config
        import yaml
        with open(self.config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        # Initialize resolver with test config
        self.resolver = WorkflowConflictResolver(self.config_path)
        
        # Override paths for testing
        self.resolver.resolution_log = os.path.join(self.test_dir, "resolution.json")
        
        # Create test directories
        os.makedirs(os.path.join(self.test_dir, "logs"), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, "config"), exist_ok=True)
        
        # Clear any existing queue items
        self.resolver.merge_queue.clear()
        self.resolver.conflict_cache.clear()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_resolver_initialization(self):
        """Test resolver initialization."""
        self.assertIsNotNone(self.resolver)
        self.assertIsNotNone(self.resolver.config)
        self.assertEqual(self.resolver.config["merge_queue"]["max_concurrent_merges"], 2)
    
    def test_config_loading(self):
        """Test configuration loading."""
        self.assertTrue(self.resolver.load_config())
        self.assertIn("merge_queue", self.resolver.config)
        self.assertIn("conflict_resolution", self.resolver.config)
    
    def test_pr_priority_calculation(self):
        """Test PR priority calculation."""
        # High priority PR
        hotfix_pr = {
            "labels": ["hotfix"],
            "author": "Jvryan92",
            "created_at": "2025-09-01T10:00:00Z"
        }
        priority = self.resolver._calculate_pr_priority(hotfix_pr)
        self.assertGreaterEqual(priority, 8)
        
        # Normal priority PR
        feature_pr = {
            "labels": ["feature"],
            "author": "contributor",
            "created_at": "2025-09-01T10:00:00Z"
        }
        priority = self.resolver._calculate_pr_priority(feature_pr)
        self.assertLessEqual(priority, 7)
    
    def test_conflict_severity_calculation(self):
        """Test conflict severity calculation."""
        # No conflicts
        severity = self.resolver._calculate_conflict_severity([])
        self.assertEqual(severity, "none")
        
        # Low severity
        low_conflicts = ["file1.py", "file2.py"]
        severity = self.resolver._calculate_conflict_severity(low_conflicts)
        self.assertEqual(severity, "low")
        
        # Medium severity
        medium_conflicts = ["file{}.py".format(i) for i in range(10)]
        severity = self.resolver._calculate_conflict_severity(medium_conflicts)
        self.assertEqual(severity, "medium")
    
    def test_auto_resolvable_detection(self):
        """Test auto-resolvable conflict detection."""
        # Documentation conflicts (auto-resolvable)
        doc_conflicts = ["README.md", "docs/guide.md"]
        self.assertTrue(self.resolver._can_auto_resolve(doc_conflicts, "low"))
        
        # Code conflicts (not auto-resolvable)
        code_conflicts = ["main.py", "utils.py"]
        self.assertFalse(self.resolver._can_auto_resolve(code_conflicts, "low"))
        
        # High severity (not auto-resolvable regardless of file type)
        self.assertFalse(self.resolver._can_auto_resolve(doc_conflicts, "high"))
    
    def test_resolution_strategy_determination(self):
        """Test resolution strategy determination."""
        # Documentation files
        doc_pr = {"labels": []}
        strategy = self.resolver._determine_resolution_strategy(["README.md"], doc_pr)
        self.assertEqual(strategy, "prefer_incoming")
        
        # Code files
        code_pr = {"labels": []}
        strategy = self.resolver._determine_resolution_strategy(["main.py"], code_pr)
        self.assertEqual(strategy, "require_manual")
        
        # Hotfix priority
        hotfix_pr = {"labels": ["hotfix"]}
        strategy = self.resolver._determine_resolution_strategy(["config.yml"], hotfix_pr)
        self.assertEqual(strategy, "prioritize_incoming")
    
    def test_merge_queue_operations(self):
        """Test merge queue operations."""
        # Create test PR info
        pr_info = {
            "repo": "test/repo",
            "number": 123,
            "labels": ["feature"],
            "author": "testuser",
            "created_at": "2025-09-01T10:00:00Z",
            "mergeable_state": "clean"
        }
        
        # Create test conflict info
        conflict_info = PRConflictInfo(
            pr_number=123,
            repo_name="test/repo",
            source_branch="feature-branch",
            target_branch="main",
            conflicts=["file1.py"],
            conflict_severity="low",
            auto_resolvable=False,
            requires_manual_review=True,
            resolution_strategy="require_manual",
            estimated_resolution_time=30,
            dependencies=[]
        )
        
        # Add to merge queue
        success = self.resolver.add_to_merge_queue(pr_info, conflict_info)
        self.assertTrue(success)
        self.assertEqual(len(self.resolver.merge_queue), 1)
        
        # Check queue item
        queue_item = self.resolver.merge_queue[0]
        self.assertEqual(queue_item.pr_number, 123)
        self.assertEqual(queue_item.repo_name, "test/repo")
        self.assertEqual(queue_item.conflict_status, "low")
    
    def test_merge_window_check(self):
        """Test merge window checking."""
        # Should always be true with our test config (0-23 hours)
        self.assertTrue(self.resolver._in_merge_window())
    
    def test_dependency_satisfaction(self):
        """Test dependency satisfaction checking."""
        # Queue item with no dependencies
        queue_item = MergeQueueItem(
            pr_number=123,
            repo_name="test/repo",
            priority=5,
            created_at=datetime.now(),
            dependencies=[],
            merge_strategy="auto_merge",
            estimated_merge_time=10,
            quality_gates_passed=True,
            conflict_status="none"
        )
        self.assertTrue(self.resolver._dependencies_satisfied(queue_item))
        
        # Queue item with dependencies
        queue_item_with_deps = MergeQueueItem(
            pr_number=124,
            repo_name="test/repo",
            priority=5,
            created_at=datetime.now(),
            dependencies=[123],
            merge_strategy="auto_merge",
            estimated_merge_time=10,
            quality_gates_passed=True,
            conflict_status="none"
        )
        
        # Add dependent item to queue
        self.resolver.merge_queue = [queue_item]
        # Dependencies not satisfied because PR 123 is still in queue
        self.assertFalse(self.resolver._dependencies_satisfied(queue_item_with_deps))
        
        # Remove dependency from queue
        self.resolver.merge_queue = []
        # Dependencies satisfied because PR 123 is no longer in queue (assumed merged)
        self.assertTrue(self.resolver._dependencies_satisfied(queue_item_with_deps))
    
    def test_queue_status_retrieval(self):
        """Test queue status retrieval."""
        # Clear existing queue items
        self.resolver.merge_queue.clear()
        
        # Add some test items to queue
        for i in range(3):
            queue_item = MergeQueueItem(
                pr_number=100 + i,
                repo_name=f"test/repo{i}",
                priority=5 + i,
                created_at=datetime.now(),
                dependencies=[],
                merge_strategy="auto_merge",
                estimated_merge_time=10,
                quality_gates_passed=True,
                conflict_status="low" if i % 2 == 0 else "none"
            )
            self.resolver.merge_queue.append(queue_item)
        
        status = self.resolver.get_queue_status()
        self.assertEqual(status["queue_size"], 3)
        self.assertEqual(status["estimated_completion_minutes"], 30)
        self.assertIn("breakdown", status)
        self.assertIn("by_status", status["breakdown"])
        self.assertIn("cache_info", status)
    
    def test_async_discover_prs(self):
        """Test async PR discovery."""
        async def run_test():
            # This will use mock data since no GitHub token
            prs = await self.resolver.discover_open_prs()
            self.assertIsInstance(prs, list)
            self.assertGreaterEqual(len(prs), 0)
            
            if prs:
                pr = prs[0]
                self.assertIn("repo", pr)
                self.assertIn("number", pr)
                self.assertIn("title", pr)
        
        asyncio.run(run_test())
    
    def test_async_conflict_analysis(self):
        """Test async conflict analysis."""
        async def run_test():
            # Test PR info
            pr_info = {
                "repo": "test/repo",
                "number": 123,
                "title": "Test PR",
                "source_branch": "feature",
                "target_branch": "main",
                "labels": ["feature"]
            }
            
            conflict_info = await self.resolver.analyze_pr_conflicts(pr_info)
            self.assertIsInstance(conflict_info, PRConflictInfo)
            self.assertEqual(conflict_info.pr_number, 123)
            self.assertEqual(conflict_info.repo_name, "test/repo")
            self.assertIsInstance(conflict_info.conflicts, list)
            self.assertIn(conflict_info.conflict_severity, ["none", "low", "medium", "high", "critical", "unknown"])
        
        asyncio.run(run_test())
    
    def test_estimation_time_calculation(self):
        """Test resolution time estimation."""
        # No conflicts
        time = self.resolver._estimate_resolution_time([], True)
        self.assertEqual(time, 5)
        
        # Auto-resolvable conflicts
        time = self.resolver._estimate_resolution_time(["file1.md", "file2.md"], True)
        self.assertEqual(time, 14)  # 10 + (2 * 2)
        
        # Manual conflicts
        time = self.resolver._estimate_resolution_time(["file1.py", "file2.py"], False)
        self.assertEqual(time, 50)  # 30 + (2 * 10)
    
    def test_cache_operations(self):
        """Test cache loading and saving operations."""
        # Create test conflict info
        conflict_info = PRConflictInfo(
            pr_number=123,
            repo_name="test/repo",
            source_branch="feature",
            target_branch="main",
            conflicts=["file1.py"],
            conflict_severity="low",
            auto_resolvable=False,
            requires_manual_review=True,
            resolution_strategy="require_manual",
            estimated_resolution_time=30,
            dependencies=[]
        )
        
        # Add to cache
        cache_key = "test/repo#123"
        self.resolver.conflict_cache[cache_key] = conflict_info
        
        # Save cache
        success = self.resolver.save_conflict_cache()
        self.assertTrue(success)
        
        # Clear cache and reload
        self.resolver.conflict_cache.clear()
        success = self.resolver.load_conflict_cache()
        self.assertTrue(success)
        
        # Verify loaded data
        self.assertIn(cache_key, self.resolver.conflict_cache)
        loaded_info = self.resolver.conflict_cache[cache_key]
        self.assertEqual(loaded_info.pr_number, 123)
        self.assertEqual(loaded_info.repo_name, "test/repo")


class TestAsyncWorkflowOperations(unittest.TestCase):
    """Test async operations of workflow resolver."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.resolver = WorkflowConflictResolver()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_comprehensive_analysis(self):
        """Test comprehensive workflow analysis."""
        async def run_test():
            result = await self.resolver.run_comprehensive_analysis()
            
            self.assertIsInstance(result, dict)
            self.assertIn("timestamp", result)
            self.assertIn("discovered_prs", result)
            self.assertIn("analyzed_conflicts", result)
            self.assertIn("queue_status", result)
            self.assertIn("recommendations", result)
            
            # Check that mock data was processed
            self.assertGreaterEqual(result["discovered_prs"], 0)
        
        asyncio.run(run_test())
    
    def test_merge_queue_processing(self):
        """Test merge queue processing."""
        async def run_test():
            # Add some test items to the queue first
            test_pr = {
                "repo": "test/repo",
                "number": 123,
                "labels": ["feature"],
                "author": "testuser",
                "created_at": "2025-09-01T10:00:00Z",
                "mergeable_state": "clean"
            }
            
            conflict_info = PRConflictInfo(
                pr_number=123,
                repo_name="test/repo",
                source_branch="feature",
                target_branch="main",
                conflicts=[],
                conflict_severity="none",
                auto_resolvable=True,
                requires_manual_review=False,
                resolution_strategy="auto_merge",
                estimated_resolution_time=5,
                dependencies=[]
            )
            
            self.resolver.add_to_merge_queue(test_pr, conflict_info)
            
            # Process the queue
            result = await self.resolver.process_merge_queue()
            
            self.assertIsInstance(result, dict)
            self.assertIn("processed", result)
            self.assertIn("successful", result)
            self.assertIn("failed", result)
            self.assertIn("skipped", result)
            self.assertIn("queue_size", result)
        
        asyncio.run(run_test())


if __name__ == "__main__":
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestWorkflowConflictResolver))
    suite.addTest(unittest.makeSuite(TestAsyncWorkflowOperations))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)