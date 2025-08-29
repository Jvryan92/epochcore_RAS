"""Agent synchronization coordinator for the StrategyDECK system."""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Set, Optional
import logging
from enum import Enum
from dataclasses import dataclass
from ..core.base_agent import BaseAgent


class SyncState(Enum):
    """Synchronization states for agents."""

    READY = "ready"
    SYNCING = "syncing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SyncPoint:
    """Represents a synchronization point for agents."""

    id: str
    agents: Set[str]
    required_agents: Set[str]
    timeout: float
    state: SyncState = SyncState.READY
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None


class AgentSynchronizer:
    """Coordinates synchronization between multiple agents."""

    def __init__(self, timeout: float = 30.0):
        """Initialize the synchronizer.

        Args:
            timeout: Default timeout in seconds for sync operations
        """
        self.sync_points: Dict[str, SyncPoint] = {}
        self.default_timeout = timeout
        self.logger = logging.getLogger("strategy_ai_agent.synchronizer")
        self._loop = asyncio.get_event_loop()

    async def create_sync_point(
        self, sync_id: str, required_agents: Set[str], timeout: Optional[float] = None
    ) -> SyncPoint:
        """Create a new synchronization point.

        Args:
            sync_id: Unique identifier for the sync point
            required_agents: Set of agent names required for sync
            timeout: Optional timeout override

        Returns:
            Created SyncPoint
        """
        if sync_id in self.sync_points:
            raise ValueError(f"Sync point {sync_id} already exists")

        sync_point = SyncPoint(
            id=sync_id,
            agents=set(),
            required_agents=required_agents,
            timeout=timeout or self.default_timeout,
        )

        self.sync_points[sync_id] = sync_point
        self.logger.info(f"Created sync point {sync_id} for agents: {required_agents}")
        return sync_point

    async def join_sync_point(self, sync_id: str, agent_name: str) -> bool:
        """Join an agent to a sync point.

        Args:
            sync_id: Sync point identifier
            agent_name: Name of agent joining

        Returns:
            True if join successful, False if sync failed
        """
        if sync_id not in self.sync_points:
            raise ValueError(f"Unknown sync point: {sync_id}")

        sync_point = self.sync_points[sync_id]

        if agent_name not in sync_point.required_agents:
            raise ValueError(
                f"Agent {agent_name} not registered for sync point {sync_id}"
            )

        if sync_point.state != SyncState.READY:
            return False

        # First agent to join starts the sync
        if not sync_point.agents:
            sync_point.state = SyncState.SYNCING
            sync_point.start_time = datetime.now(timezone.utc)

        sync_point.agents.add(agent_name)
        self.logger.debug(
            f"Agent {agent_name} joined sync point {sync_id}. "
            f"Waiting on {len(sync_point.required_agents) - len(sync_point.agents)} more agents"
        )

        try:
            # Wait for all agents or timeout
            await asyncio.wait_for(
                self._wait_for_sync_completion(sync_point), timeout=sync_point.timeout
            )
            return True

        except asyncio.TimeoutError:
            sync_point.state = SyncState.ERROR
            self.logger.error(
                f"Sync point {sync_id} timed out waiting for agents: "
                f"{sync_point.required_agents - sync_point.agents}"
            )
            return False

    async def _wait_for_sync_completion(self, sync_point: SyncPoint) -> None:
        """Wait for all required agents to join the sync point."""
        while len(sync_point.agents) < len(sync_point.required_agents):
            await asyncio.sleep(0.1)  # Small sleep to prevent tight loop

            # Check if sync failed
            if sync_point.state == SyncState.ERROR:
                raise RuntimeError(f"Sync point {sync_point.id} failed")

        sync_point.state = SyncState.COMPLETED
        sync_point.completion_time = datetime.now(timezone.utc)
        self.logger.info(f"Sync point {sync_point.id} completed")

    def get_sync_status(self, sync_id: str) -> Dict[str, Any]:
        """Get status of a sync point.

        Args:
            sync_id: Sync point identifier

        Returns:
            Status dictionary
        """
        if sync_id not in self.sync_points:
            raise ValueError(f"Unknown sync point: {sync_id}")

        sync_point = self.sync_points[sync_id]
        return {
            "id": sync_point.id,
            "state": sync_point.state.value,
            "agents_joined": list(sync_point.agents),
            "agents_pending": list(sync_point.required_agents - sync_point.agents),
            "start_time": (
                sync_point.start_time.isoformat() if sync_point.start_time else None
            ),
            "completion_time": (
                sync_point.completion_time.isoformat()
                if sync_point.completion_time
                else None
            ),
        }

    def cleanup_sync_point(self, sync_id: str) -> None:
        """Clean up a completed sync point.

        Args:
            sync_id: Sync point identifier to clean up
        """
        if sync_id in self.sync_points:
            del self.sync_points[sync_id]
            self.logger.debug(f"Cleaned up sync point {sync_id}")


class SynchronizedAgent(BaseAgent):
    """Base class for agents that support synchronization."""

    def __init__(
        self,
        name: str,
        synchronizer: AgentSynchronizer,
        config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize synchronized agent.

        Args:
            name: Agent name
            synchronizer: Agent synchronizer instance
            config: Optional configuration
        """
        super().__init__(name, config)
        self.synchronizer = synchronizer
        self._sync_results: Dict[str, bool] = {}

    async def sync_with_agents(
        self, sync_id: str, agents: Set[str], timeout: Optional[float] = None
    ) -> bool:
        """Synchronize with other agents.

        Args:
            sync_id: Unique sync point identifier
            agents: Set of agent names to sync with
            timeout: Optional timeout override

        Returns:
            True if sync successful, False otherwise
        """
        try:
            # Create sync point if we're the first
            if sync_id not in self.synchronizer.sync_points:
                agents.add(self.name)  # Include self
                await self.synchronizer.create_sync_point(sync_id, agents, timeout)

            # Join the sync point
            success = await self.synchronizer.join_sync_point(sync_id, self.name)
            self._sync_results[sync_id] = success
            return success

        except Exception as e:
            self.logger.error(f"Sync failed for agent {self.name}: {str(e)}")
            self._sync_results[sync_id] = False
            return False

    def get_sync_result(self, sync_id: str) -> Optional[bool]:
        """Get result of a previous sync operation.

        Args:
            sync_id: Sync point identifier

        Returns:
            True if sync was successful, False if failed, None if not found
        """
        return self._sync_results.get(sync_id)
