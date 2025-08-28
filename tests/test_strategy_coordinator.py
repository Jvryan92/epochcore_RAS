"""Unit tests for strategy coordinator."""

import unittest
from unittest.mock import Mock, patch
import asyncio
from typing import Dict, Any

from scripts.ai_agent.strategy.coordinator import StrategyCoordinator, StrategyState
from scripts.ai_agent.strategy import StrategyComponent


class MockStrategy(StrategyComponent):
    """Mock strategy for testing."""
    
    def __init__(self, name: str, result: Dict[str, Any] = None):
        super().__init__(name)
        self.result = result or {"status": "success"}
        self.execute_called = False
        
    def _execute(self) -> Dict[str, Any]:
        self.execute_called = True
        return self.result


class TestStrategyCoordinator(unittest.TestCase):
    """Test cases for StrategyCoordinator."""

    def setUp(self):
        """Set up test environment."""
        self.coordinator = StrategyCoordinator()
        
        # Clear existing strategies for testing
        self.coordinator.state = StrategyState()

    def test_register_strategy(self):
        """Test strategy registration."""
        mock_strategy = MockStrategy("test_strategy")
        
        self.coordinator.register_strategy("test", mock_strategy)
        
        self.assertIn("test", self.coordinator.state.active_strategies)
        self.assertEqual(
            self.coordinator.state.active_strategies["test"],
            mock_strategy
        )

    def test_dependency_order(self):
        """Test correct dependency-based execution order."""
        strategy_a = MockStrategy("strategy_a")
        strategy_b = MockStrategy("strategy_b")
        strategy_c = MockStrategy("strategy_c")
        
        # C depends on B, B depends on A
        self.coordinator.register_strategy("a", strategy_a)
        self.coordinator.register_strategy("b", strategy_b, ["a"])
        self.coordinator.register_strategy("c", strategy_c, ["b"])
        
        # Execute strategies
        results = self.coordinator._execute()
        
        # Check execution order
        self.assertEqual(
            self.coordinator.state.execution_order,
            ["a", "b", "c"]
        )

    def test_result_caching(self):
        """Test strategy result caching."""
        strategy = MockStrategy("test", {"value": 42})
        
        self.coordinator.register_strategy("test", strategy)
        self.coordinator._execute()
        
        cached = self.coordinator.get_cached_result("test")
        self.assertEqual(cached, {"value": 42})

    def test_error_handling(self):
        """Test error handling during strategy execution."""
        def failing_execute():
            raise ValueError("Test error")
            
        strategy = MockStrategy("failing")
        strategy._execute = failing_execute
        
        self.coordinator.register_strategy("failing", strategy)
        results = self.coordinator._execute()
        
        self.assertEqual(
            results["results"]["failing"]["status"],
            "error"
        )

    @patch("asyncio.create_task")
    async def test_async_execution(self, mock_create_task):
        """Test asynchronous strategy execution."""
        async def mock_execute():
            return {"status": "async_success"}
            
        strategy = MockStrategy("async_test")
        strategy.execute_async = mock_execute
        
        self.coordinator.register_strategy("async_test", strategy)
        
        mock_create_task.return_value = asyncio.Future()
        mock_create_task.return_value.set_result({"status": "async_success"})
        
        results = await self.coordinator.execute_async()
        
        self.assertEqual(
            results["results"]["async_test"]["status"],
            "async_success"
        )

    def test_get_strategy_status(self):
        """Test retrieving strategy status."""
        strategy = MockStrategy("test")
        self.coordinator.register_strategy("test", strategy)
        
        status = self.coordinator.get_strategy_status()
        
        self.assertIn("test", status)
        self.assertEqual(
            status["test"]["name"],
            "test"
        )


if __name__ == "__main__":
    unittest.main()
