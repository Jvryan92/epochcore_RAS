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

        # Check if sync has already failed or completed
        if sync_point.state == SyncState.ERROR:
            self.logger.warning(f"Agent {agent_name} attempted to join failed sync point {sync_id}")
            return False
            
        if sync_point.state == SyncState.COMPLETED:
            self.logger.warning(f"Agent {agent_name} attempted to join completed sync point {sync_id}")
            return True  # Consider this successful since sync already completed

        # Check if agent already joined
        if agent_name in sync_point.agents:
            self.logger.debug(f"Agent {agent_name} already in sync point {sync_id}")
            # Still need to wait for completion
        else:
            # First agent to join starts the sync
            if not sync_point.agents and sync_point.state == SyncState.READY:
                sync_point.state = SyncState.SYNCING
                sync_point.start_time = datetime.now(timezone.utc)
                self.logger.info(f"Sync point {sync_id} started by agent {agent_name}")

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
            missing_agents = sync_point.required_agents - sync_point.agents
            self.logger.error(
                f"Sync point {sync_id} timed out waiting for agents: {missing_agents}"
            )
            return False
        except Exception as e:
            sync_point.state = SyncState.ERROR
            self.logger.error(f"Sync point {sync_id} failed with error: {str(e)}")
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

    def list_active_sync_points(self) -> List[Dict[str, Any]]:
        """List all active sync points.

        Returns:
            List of active sync point statuses
        """
        return [self.get_sync_status(sync_id) for sync_id in self.sync_points.keys()]

    def diagnose_sync_issues(self, sync_id: str) -> Dict[str, Any]:
        """Diagnose potential issues with a sync point.

        Args:
            sync_id: Sync point identifier

        Returns:
            Dictionary with diagnostic information
        """
        if sync_id not in self.sync_points:
            return {"error": f"Sync point {sync_id} not found"}

        sync_point = self.sync_points[sync_id]
        status = self.get_sync_status(sync_id)
        
        diagnostics = {
            "sync_id": sync_id,
            "status": status,
            "issues": [],
            "recommendations": []
        }

        # Check for common issues
        if sync_point.state == SyncState.ERROR:
            diagnostics["issues"].append("Sync point is in error state")
            diagnostics["recommendations"].append("Check logs for timeout or error details")

        if sync_point.state == SyncState.SYNCING:
            missing_agents = sync_point.required_agents - sync_point.agents
            if missing_agents:
                diagnostics["issues"].append(f"Missing agents: {missing_agents}")
                diagnostics["recommendations"].append("Check if missing agents are running and can reach sync point")

        # Check timing
        if sync_point.start_time:
            import time
            elapsed = time.time() - sync_point.start_time.timestamp()
            if elapsed > sync_point.timeout * 0.8:  # 80% of timeout
                diagnostics["issues"].append(f"Sync taking long time: {elapsed:.1f}s / {sync_point.timeout}s")
                diagnostics["recommendations"].append("Consider increasing timeout or checking agent performance")

        return diagnostics

    def force_complete_sync(self, sync_id: str) -> bool:
        """Force complete a sync point (emergency recovery).

        Args:
            sync_id: Sync point identifier

        Returns:
            True if forced completion succeeded
        """
        if sync_id not in self.sync_points:
            self.logger.warning(f"Cannot force complete unknown sync point: {sync_id}")
            return False

        sync_point = self.sync_points[sync_id]
        sync_point.state = SyncState.COMPLETED
        sync_point.completion_time = datetime.now(timezone.utc)
        
        self.logger.warning(f"Force completed sync point {sync_id}")
        return True
    
    async def join_or_create_sync_point(
        self, 
        sync_id: str, 
        agent_name: str, 
        required_agents: Set[str], 
        timeout: Optional[float] = None
    ) -> bool:
        """Join existing sync point or create new one if needed.
        
        This method handles the common case where agents want to sync 
        but may have slightly different views of who should participate.
        
        Args:
            sync_id: Sync point identifier
            agent_name: Name of agent joining
            required_agents: Set of agents this agent believes should participate
            timeout: Optional timeout override
            
        Returns:
            True if sync successful, False otherwise
        """
        # Ensure agent is in required set
        required_agents = required_agents.copy()
        required_agents.add(agent_name)
        
        # Create sync point if it doesn't exist
        if sync_id not in self.sync_points:
            try:
                await self.create_sync_point(sync_id, required_agents, timeout)
            except ValueError as e:
                if "already exists" in str(e):
                    # Race condition - another agent created it
                    pass
                else:
                    raise
        
        # Check if we can join
        sync_point = self.sync_points[sync_id]
        if agent_name not in sync_point.required_agents:
            # We're not in the required set - for now just log and fail gracefully
            missing_agents = required_agents - sync_point.required_agents
            extra_agents = sync_point.required_agents - required_agents
            
            self.logger.warning(
                f"Agent {agent_name} sync set mismatch for {sync_id}. "
                f"Missing from sync: {missing_agents}, Extra in sync: {extra_agents}"
            )
            return False
        
        # Join the sync point
        return await self.join_sync_point(sync_id, agent_name)


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
            # Use the improved join_or_create method
            success = await self.synchronizer.join_or_create_sync_point(
                sync_id, self.name, agents, timeout
            )
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
