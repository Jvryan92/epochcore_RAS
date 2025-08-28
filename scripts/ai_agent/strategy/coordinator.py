"""Strategy coordination and integration module."""

from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
import asyncio
import logging

from . import StrategyComponent
from .cognitive import CognitiveStrategy
from .ethical import EthicalStrategy
from .resilience import ResilienceStrategy
from ..core.metrics import AgentMetrics
from ..core.error_handling import log_errors, safe_execute


@dataclass
class StrategyState:
    """Container for overall strategy state."""

    active_strategies: Dict[str, StrategyComponent] = field(default_factory=dict)
    results_cache: Dict[str, Any] = field(default_factory=dict)
    execution_order: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)


class StrategyCoordinator(StrategyComponent):
    """Coordinates multiple strategy components."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize strategy coordinator.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__("strategy_coordinator", config)
        self.state = StrategyState()
        self._initialize_strategies()

    def _initialize_strategies(self):
        """Initialize core strategy components."""
        # Register core strategies
        self.register_strategy(
            "cognitive",
            CognitiveStrategy(self.config.get("cognitive", {}))
        )
        self.register_strategy(
            "ethical",
            EthicalStrategy(self.config.get("ethical", {}))
        )
        self.register_strategy(
            "resilience",
            ResilienceStrategy(self.config.get("resilience", {}))
        )

        # Set up dependencies
        self.state.dependencies = {
            "ethical": ["cognitive"],  # Ethical depends on cognitive analysis
            "resilience": []  # Resilience is independent
        }

        # Calculate execution order
        self._calculate_execution_order()

    def _calculate_execution_order(self):
        """Calculate optimal strategy execution order."""
        # Reset execution order
        self.state.execution_order = []
        visited = set()

        def visit(strategy: str):
            """Depth-first traversal for topological sort."""
            if strategy in visited:
                return
            visited.add(strategy)
            
            # Visit dependencies first
            for dep in self.state.dependencies.get(strategy, []):
                visit(dep)
            
            self.state.execution_order.append(strategy)

        # Visit all strategies
        for strategy in self.state.active_strategies:
            visit(strategy)

    def register_strategy(
        self,
        name: str,
        strategy: StrategyComponent,
        dependencies: Optional[List[str]] = None
    ):
        """Register a new strategy component.

        Args:
            name: Strategy identifier
            strategy: Strategy component instance
            dependencies: Optional list of dependent strategies
        """
        self.state.active_strategies[name] = strategy
        if dependencies is not None:
            self.state.dependencies[name] = dependencies
        self._calculate_execution_order()

    def _execute(self) -> Dict[str, Any]:
        """Execute all strategies in order.

        Returns:
            Dictionary containing all execution results
        """
        results = {}
        
        # Execute strategies in dependency order
        for strategy_name in self.state.execution_order:
            strategy = self.state.active_strategies[strategy_name]
            
            try:
                # Execute strategy
                result = strategy.execute()
                results[strategy_name] = result
                
                # Cache results for dependent strategies
                self.state.results_cache[strategy_name] = result

            except Exception as e:
                self.logger.error(
                    f"Error executing strategy {strategy_name}: {e}"
                )
                results[strategy_name] = {
                    "status": "error",
                    "error": str(e)
                }

        return {
            "results": results,
            "execution_order": self.state.execution_order,
            "cache_status": {
                name: "available" if name in self.state.results_cache 
                else "missing"
                for name in self.state.active_strategies
            }
        }

    async def execute_async(self) -> Dict[str, Any]:
        """Execute strategies asynchronously when possible.

        Returns:
            Dictionary containing all execution results
        """
        results = {}
        tasks = []

        # Group strategies by execution level (based on dependencies)
        levels: Dict[int, List[str]] = {}
        visited = set()

        def get_level(strategy: str, current_level: int = 0) -> int:
            """Calculate execution level for a strategy."""
            if strategy in visited:
                return current_level
            visited.add(strategy)
            
            max_dep_level = current_level
            for dep in self.state.dependencies.get(strategy, []):
                dep_level = get_level(dep, current_level + 1)
                max_dep_level = max(max_dep_level, dep_level)
            
            return max_dep_level

        # Calculate levels for all strategies
        for strategy in self.state.active_strategies:
            level = get_level(strategy)
            if level not in levels:
                levels[level] = []
            levels[level].append(strategy)

        # Execute strategies level by level
        for level in sorted(levels.keys()):
            level_tasks = []
            
            for strategy_name in levels[level]:
                strategy = self.state.active_strategies[strategy_name]
                
                # Create execution task
                task = asyncio.create_task(
                    self._execute_strategy_async(strategy_name, strategy)
                )
                level_tasks.append(task)
            
            # Wait for all strategies at this level to complete
            level_results = await asyncio.gather(*level_tasks)
            
            # Store results
            for strategy_name, result in zip(levels[level], level_results):
                results[strategy_name] = result
                self.state.results_cache[strategy_name] = result

        return {
            "results": results,
            "execution_order": self.state.execution_order,
            "cache_status": {
                name: "available" if name in self.state.results_cache 
                else "missing"
                for name in self.state.active_strategies
            }
        }

    async def _execute_strategy_async(
        self,
        name: str,
        strategy: StrategyComponent
    ) -> Dict[str, Any]:
        """Execute a single strategy asynchronously.

        Args:
            name: Strategy name
            strategy: Strategy component to execute

        Returns:
            Strategy execution results
        """
        try:
            # Execute in thread pool if not async-capable
            if not hasattr(strategy, "execute_async"):
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None, strategy.execute
                )
            
            # Execute async if supported
            return await strategy.execute_async()
            
        except Exception as e:
            self.logger.error(f"Error executing strategy {name}: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    @safe_execute(logging.getLogger("strategy_ai_agent.coordinator"), {})
    def get_strategy_status(self) -> Dict[str, Any]:
        """Get status of all registered strategies.

        Returns:
            Dictionary containing strategy statuses
        """
        return {
            name: strategy.get_status()
            for name, strategy in self.state.active_strategies.items()
        }

    def get_cached_result(
        self,
        strategy_name: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached result for a strategy.

        Args:
            strategy_name: Strategy identifier

        Returns:
            Cached result if available
        """
        return self.state.results_cache.get(strategy_name)
