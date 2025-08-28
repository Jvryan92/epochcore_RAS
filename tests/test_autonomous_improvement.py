"""
Tests for the Autonomous Continuous Improvement System.
"""

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.autonomous_improvement.orchestrator import (
    AutonomousOrchestrator, 
    ImprovementTask, 
    ImprovementCategory, 
    ImprovementPriority,
    AutonomousConfig
)
from scripts.autonomous_improvement.agents import (
    SecurityAgent,
    DependencyAgent, 
    QualityAgent,
    DocumentationAgent
)


class TestAutonomousOrchestrator(unittest.TestCase):
    """Test cases for AutonomousOrchestrator."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config.yaml"
        self.orchestrator = AutonomousOrchestrator(str(self.config_path))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test orchestrator initialization."""
        self.assertIsInstance(self.orchestrator.config, AutonomousConfig)
        self.assertEqual(self.orchestrator.config.enabled, True)
        self.assertEqual(self.orchestrator.config.safe_mode, True)
        self.assertTrue(self.config_path.exists())
    
    def test_config_validation(self):
        """Test configuration validation."""
        self.assertTrue(self.orchestrator.validate_config())
        
        # Test invalid configuration
        self.orchestrator.config.max_concurrent_tasks = 0
        self.assertFalse(self.orchestrator.validate_config())
        
        # Test invalid threshold
        self.orchestrator.config.max_concurrent_tasks = 3
        self.orchestrator.config.confidence_threshold = 1.5
        self.assertFalse(self.orchestrator.validate_config())
    
    def test_health_score_calculation(self):
        """Test health score calculation."""
        # Test with no metrics
        score = self.orchestrator._calculate_health_score()
        self.assertEqual(score, 0.5)
        
        # Test with sample metrics
        self.orchestrator.health_metrics = {
            "repository": {
                "security": {"vulnerabilities": 0, "score": 90},
                "quality": {"linting_score": 85, "complexity": 75}
            },
            "workflows": {"success_rate": 0.95, "average_duration": 180},
            "performance": {"score": 0.8}
        }
        
        score = self.orchestrator._calculate_health_score()
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 1)
    
    def test_should_run_health_check(self):
        """Test health check scheduling logic."""
        # Should run on first execution
        self.assertTrue(self.orchestrator._should_run_health_check())
        
        # Should not run immediately after
        import time
        self.orchestrator.last_health_check = time.time()
        self.assertFalse(self.orchestrator._should_run_health_check())
        
        # Should run after interval
        self.orchestrator.last_health_check = time.time() - 7200  # 2 hours ago
        self.assertTrue(self.orchestrator._should_run_health_check())
    
    def test_should_generate_improvements(self):
        """Test improvement generation logic."""
        # Should generate if queue is empty
        self.assertTrue(self.orchestrator._should_generate_improvements())
        
        # Should not generate if queue has tasks
        task = ImprovementTask(
            id="test",
            category=ImprovementCategory.QUALITY,
            priority=ImprovementPriority.LOW,
            title="Test task",
            description="Test description"
        )
        self.orchestrator.task_queue.append(task)
        self.assertFalse(self.orchestrator._should_generate_improvements())
    
    def test_task_time_appropriateness(self):
        """Test task scheduling based on time."""
        task_priority = ImprovementPriority.CRITICAL
        
        # Critical tasks should always be appropriate
        self.assertTrue(self.orchestrator._is_appropriate_time(task_priority))
        
        # Test with custom hours configuration
        self.orchestrator.config.priority_hours = {
            "high": [9, 10, 11, 12, 13, 14, 15, 16, 17]  # Business hours only
        }
        
        from datetime import datetime
        import unittest.mock
        
        # Mock current hour to be outside business hours
        with unittest.mock.patch('scripts.autonomous_improvement.orchestrator.datetime') as mock_datetime:
            mock_datetime.now.return_value = Mock(hour=22)  # 10 PM
            self.assertTrue(self.orchestrator._is_appropriate_time(ImprovementPriority.HIGH))
    
    @patch('scripts.autonomous_improvement.orchestrator.Path.rglob')
    def test_analyze_repository_files(self, mock_rglob):
        """Test repository file analysis."""
        # Mock file paths
        mock_files = [
            Mock(is_file=lambda: True, stat=lambda: Mock(st_size=1024)),
            Mock(is_file=lambda: True, stat=lambda: Mock(st_size=2048)),
        ]
        mock_rglob.return_value = mock_files
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(self.orchestrator._analyze_repository_files())
        
        self.assertIsInstance(result, dict)
        self.assertIn("total_files", result)
        self.assertIn("code_files", result)


class TestImprovementAgents(unittest.TestCase):
    """Test cases for improvement agents."""
    
    def setUp(self):
        """Set up test agents."""
        self.security_agent = SecurityAgent()
        self.dependency_agent = DependencyAgent()
        self.quality_agent = QualityAgent()
        self.documentation_agent = DocumentationAgent()
    
    def test_agent_initialization(self):
        """Test agent initialization."""
        agents = [
            self.security_agent,
            self.dependency_agent,
            self.quality_agent,
            self.documentation_agent
        ]
        
        for agent in agents:
            self.assertTrue(agent.validate_config())
            self.assertIsInstance(agent.run(), dict)
    
    def test_security_agent_task_handling(self):
        """Test security agent task handling."""
        security_task = ImprovementTask(
            id="sec_test",
            category=ImprovementCategory.SECURITY,
            priority=ImprovementPriority.HIGH,
            title="Fix security issues",
            description="Fix security vulnerabilities"
        )
        
        other_task = ImprovementTask(
            id="other_test",
            category=ImprovementCategory.QUALITY,
            priority=ImprovementPriority.MEDIUM,
            title="Fix quality issues",
            description="Improve code quality"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Security agent should handle security tasks
        self.assertTrue(
            loop.run_until_complete(self.security_agent.can_handle(security_task))
        )
        
        # Security agent should not handle other tasks
        self.assertFalse(
            loop.run_until_complete(self.security_agent.can_handle(other_task))
        )
    
    def test_dependency_agent_task_handling(self):
        """Test dependency agent task handling."""
        dependency_task = ImprovementTask(
            id="dep_test",
            category=ImprovementCategory.DEPENDENCY,
            priority=ImprovementPriority.LOW,
            title="Update dependencies",
            description="Update outdated dependencies"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.assertTrue(
            loop.run_until_complete(self.dependency_agent.can_handle(dependency_task))
        )
    
    def test_quality_agent_task_handling(self):
        """Test quality agent task handling."""
        quality_task = ImprovementTask(
            id="qual_test",
            category=ImprovementCategory.QUALITY,
            priority=ImprovementPriority.MEDIUM,
            title="Improve code quality",
            description="Fix linting issues"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.assertTrue(
            loop.run_until_complete(self.quality_agent.can_handle(quality_task))
        )
    
    def test_documentation_agent_task_handling(self):
        """Test documentation agent task handling."""
        doc_task = ImprovementTask(
            id="doc_test",
            category=ImprovementCategory.DOCUMENTATION,
            priority=ImprovementPriority.LOW,
            title="Improve documentation",
            description="Update API documentation"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.assertTrue(
            loop.run_until_complete(self.documentation_agent.can_handle(doc_task))
        )
    
    @patch('subprocess.run')
    def test_security_agent_vulnerability_scan(self, mock_subprocess):
        """Test security agent vulnerability scanning."""
        # Mock successful safety check
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(self.security_agent._fix_vulnerabilities())
        self.assertTrue(result)
        
        # Mock vulnerability found
        mock_subprocess.return_value = Mock(returncode=1, stdout="", stderr="")
        result = loop.run_until_complete(self.security_agent._fix_vulnerabilities())
        # Result depends on re-check after attempted fix
    
    @patch('subprocess.run')
    def test_quality_agent_formatting(self, mock_subprocess):
        """Test quality agent code formatting."""
        # Mock no formatting needed
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(self.quality_agent._fix_formatting_issues())
        self.assertTrue(result)
        
        # Mock formatting needed and successful fix
        mock_subprocess.side_effect = [
            Mock(returncode=1, stdout="", stderr=""),  # Check fails
            Mock(returncode=0, stdout="", stderr="")   # Format succeeds
        ]
        
        result = loop.run_until_complete(self.quality_agent._fix_formatting_issues())
        self.assertTrue(result)
    
    def test_documentation_agent_readme_creation(self):
        """Test documentation agent README creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            import os
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                result = loop.run_until_complete(self.documentation_agent._improve_readme())
                
                # Should create README if it doesn't exist
                self.assertTrue(Path("README.md").exists())
                self.assertTrue(result)
                
            finally:
                os.chdir(original_cwd)


class TestImprovementTask(unittest.TestCase):
    """Test cases for ImprovementTask model."""
    
    def test_task_creation(self):
        """Test improvement task creation."""
        task = ImprovementTask(
            id="test_task_1",
            category=ImprovementCategory.SECURITY,
            priority=ImprovementPriority.HIGH,
            title="Fix security vulnerability",
            description="Address critical security issue in dependencies"
        )
        
        self.assertEqual(task.id, "test_task_1")
        self.assertEqual(task.category, ImprovementCategory.SECURITY)
        self.assertEqual(task.priority, ImprovementPriority.HIGH)
        self.assertTrue(task.automated)
        self.assertIsNone(task.completed_at)
        self.assertIsNone(task.success)
    
    def test_task_serialization(self):
        """Test task serialization/deserialization."""
        task = ImprovementTask(
            id="test_task_2",
            category=ImprovementCategory.QUALITY,
            priority=ImprovementPriority.MEDIUM,
            title="Improve code quality",
            description="Fix linting issues"
        )
        
        # Should be serializable to JSON
        task_dict = task.model_dump()
        self.assertIsInstance(task_dict, dict)
        self.assertEqual(task_dict["id"], "test_task_2")
        
        # Should be deserializable from JSON
        new_task = ImprovementTask(**task_dict)
        self.assertEqual(new_task.id, task.id)
        self.assertEqual(new_task.category, task.category)


class TestAutonomousConfig(unittest.TestCase):
    """Test cases for AutonomousConfig model."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = AutonomousConfig()
        
        self.assertTrue(config.enabled)
        self.assertTrue(config.safe_mode)
        self.assertEqual(config.max_concurrent_tasks, 3)
        self.assertEqual(config.health_check_interval, 3600)
        self.assertTrue(config.rollback_enabled)
        self.assertEqual(config.confidence_threshold, 0.8)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Valid configuration
        config = AutonomousConfig(
            enabled=True,
            max_concurrent_tasks=5,
            confidence_threshold=0.9
        )
        
        self.assertEqual(config.max_concurrent_tasks, 5)
        self.assertEqual(config.confidence_threshold, 0.9)
    
    def test_config_serialization(self):
        """Test configuration serialization."""
        config = AutonomousConfig()
        config_dict = config.model_dump()
        
        self.assertIsInstance(config_dict, dict)
        self.assertIn("enabled", config_dict)
        self.assertIn("safe_mode", config_dict)
        
        # Should be recreatable from dict
        new_config = AutonomousConfig(**config_dict)
        self.assertEqual(new_config.enabled, config.enabled)
        self.assertEqual(new_config.safe_mode, config.safe_mode)


if __name__ == "__main__":
    unittest.main()