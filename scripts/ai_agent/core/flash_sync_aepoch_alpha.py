"""Flash synchronization with aepochALPHA capabilities."""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Set, Optional, List
from enum import Enum
from dataclasses import dataclass
import logging


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


# Mock AgentSynchronizer interface for testing
class AgentSynchronizer:
    """Mock synchronizer for testing purposes."""

    def __init__(self, timeout: float = 30.0):
        self.sync_points: Dict[str, SyncPoint] = {}
        self.default_timeout = timeout
        self.logger = logging.getLogger("strategy_ai_agent.synchronizer")

    async def create_sync_point(
        self, sync_id: str, required_agents: Set[str], timeout: Optional[float] = None
    ) -> SyncPoint:
        sync_point = SyncPoint(
            id=sync_id,
            agents=set(),
            required_agents=required_agents,
            timeout=timeout or self.default_timeout,
        )
        self.sync_points[sync_id] = sync_point
        return sync_point

    async def join_sync_point(self, sync_id: str, agent_name: str) -> bool:
        if sync_id not in self.sync_points:
            return False
        sync_point = self.sync_points[sync_id]
        sync_point.agents.add(agent_name)
        return True

    def cleanup_sync_point(self, sync_id: str) -> None:
        if sync_id in self.sync_points:
            del self.sync_points[sync_id]


class FlashSyncState(Enum):
    """States for flash sync operations."""

    READY = "ready"
    ALPHA_SYNC = "alpha_sync"
    REGULAR_SYNC = "regular_sync"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FlashSyncResult:
    """Result of a flash sync operation."""

    sync_id: str
    state: FlashSyncState
    alpha_agents_synced: Set[str]
    regular_agents_synced: Set[str]
    start_time: Optional[datetime] = None
    alpha_completion_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    error_message: Optional[str] = None
    epoch_id: Optional[str] = None


@dataclass
class EpochSyncResult(FlashSyncResult):
    """Result of an epoch-based sync operation."""

    epoch_window_start: Optional[datetime] = None
    epoch_window_end: Optional[datetime] = None
    epoch_metrics: Optional[Dict[str, Any]] = None


class FlashSyncAepochAlpha:
    """Flash synchronization coordinator with aepochALPHA capabilities."""

    def __init__(
        self, synchronizer: AgentSynchronizer, config: Optional[Dict[str, Any]] = None
    ):
        """Initialize flash sync coordinator.

        Args:
            synchronizer: Agent synchronizer instance
            config: Configuration dictionary
        """
        self.synchronizer = synchronizer
        self.config = config or self._default_config()
        self.logger = logging.getLogger("strategy_ai_agent.flash_sync_aepoch_alpha")
        self._active_flash_syncs: Dict[str, FlashSyncResult] = {}

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "alpha_timeout": 15.0,
            "regular_timeout": 30.0,
            "epoch_window": 60.0,
            "max_flash_agents": 10,
            "priority_levels": ["alpha", "beta", "gamma"],
        }

    async def sync_alpha_agents(
        self,
        sync_id: str,
        alpha_agents: Set[str],
        regular_agents: Optional[Set[str]] = None,
        timeout: Optional[float] = None,
    ) -> FlashSyncResult:
        """Coordinate flash sync with alpha agent priority.

        Args:
            sync_id: Unique identifier for this flash sync
            alpha_agents: Set of alpha priority agent names
            regular_agents: Set of regular agent names (optional)
            timeout: Override timeout for the operation

        Returns:
            FlashSyncResult with sync details
        """
        if sync_id in self._active_flash_syncs:
            raise ValueError(f"Flash sync {sync_id} already active")

        # Initialize result tracking
        result = FlashSyncResult(
            sync_id=sync_id,
            state=FlashSyncState.READY,
            alpha_agents_synced=set(),
            regular_agents_synced=set(),
            start_time=datetime.now(timezone.utc),
        )
        self._active_flash_syncs[sync_id] = result

        try:
            # Phase 1: Alpha agent synchronization
            alpha_timeout = timeout or self.config["alpha_timeout"]
            self.logger.info(f"Starting alpha phase for flash sync {sync_id}")
            result.state = FlashSyncState.ALPHA_SYNC

            alpha_sync_id = f"{sync_id}_alpha"
            await self.synchronizer.create_sync_point(
                alpha_sync_id, alpha_agents, alpha_timeout
            )

            # Wait for all alpha agents
            alpha_success = await self._wait_for_agents(
                alpha_sync_id, alpha_agents, alpha_timeout
            )

            if alpha_success:
                result.alpha_agents_synced = alpha_agents.copy()
                result.alpha_completion_time = datetime.now(timezone.utc)
                self.logger.info(f"Alpha sync completed for {sync_id}")
            else:
                result.state = FlashSyncState.FAILED
                result.error_message = "Alpha agent sync failed"
                return result

            # Phase 2: Regular agent synchronization (if provided)
            if regular_agents:
                regular_timeout = timeout or self.config["regular_timeout"]
                self.logger.info(f"Starting regular phase for flash sync {sync_id}")
                result.state = FlashSyncState.REGULAR_SYNC

                regular_sync_id = f"{sync_id}_regular"
                await self.synchronizer.create_sync_point(
                    regular_sync_id, regular_agents, regular_timeout
                )

                regular_success = await self._wait_for_agents(
                    regular_sync_id, regular_agents, regular_timeout
                )

                if regular_success:
                    result.regular_agents_synced = regular_agents.copy()
                else:
                    # Alpha succeeded, but regular failed - still partial success
                    self.logger.warning(f"Regular agent sync failed for {sync_id}")

            result.state = FlashSyncState.COMPLETED
            result.completion_time = datetime.now(timezone.utc)
            self.logger.info(f"Flash sync {sync_id} completed successfully")

        except Exception as e:
            result.state = FlashSyncState.FAILED
            result.error_message = str(e)
            self.logger.error(f"Flash sync {sync_id} failed: {e}")

        return result

    async def sync_with_epoch(
        self,
        sync_id: str,
        agents: Set[str],
        epoch_id: str,
        epoch_config: Optional[Dict[str, Any]] = None,
    ) -> EpochSyncResult:
        """Synchronize agents within an epoch processing window.

        Args:
            sync_id: Unique identifier for this sync
            agents: Set of agent names to synchronize
            epoch_id: Identifier for the epoch
            epoch_config: Optional epoch-specific configuration

        Returns:
            EpochSyncResult with epoch timing data
        """
        epoch_window = (epoch_config or {}).get(
            "epoch_window", self.config["epoch_window"]
        )

        # Calculate epoch window
        start_time = datetime.now(timezone.utc)
        window_start = start_time
        # Properly calculate end time by adding seconds using timedelta
        window_end = start_time + timedelta(seconds=int(epoch_window))

        # Initialize epoch result
        result = EpochSyncResult(
            sync_id=sync_id,
            state=FlashSyncState.READY,
            alpha_agents_synced=set(),
            regular_agents_synced=set(),
            start_time=start_time,
            epoch_id=epoch_id,
            epoch_window_start=window_start,
            epoch_window_end=window_end,
        )

        self._active_flash_syncs[sync_id] = result

        try:
            self.logger.info(f"Starting epoch sync {sync_id} for epoch {epoch_id}")
            result.state = FlashSyncState.REGULAR_SYNC

            # Create sync point for epoch processing
            await self.synchronizer.create_sync_point(sync_id, agents, epoch_window)

            # Wait for agents within epoch window
            success = await self._wait_for_agents(sync_id, agents, epoch_window)

            if success:
                result.regular_agents_synced = agents.copy()
                result.state = FlashSyncState.COMPLETED
                result.completion_time = datetime.now(timezone.utc)

                # Calculate epoch metrics
                result.epoch_metrics = {
                    "total_agents": len(agents),
                    "sync_duration": (
                        result.completion_time - start_time
                    ).total_seconds(),
                    "epoch_utilization": min(
                        1.0,
                        (result.completion_time - start_time).total_seconds()
                        / epoch_window,
                    ),
                }

                self.logger.info(f"Epoch sync {sync_id} completed for epoch {epoch_id}")
            else:
                result.state = FlashSyncState.FAILED
                result.error_message = "Epoch sync timed out"

        except Exception as e:
            result.state = FlashSyncState.FAILED
            result.error_message = str(e)
            self.logger.error(f"Epoch sync {sync_id} failed: {e}")

        return result

    async def _wait_for_agents(
        self, sync_id: str, agents: Set[str], timeout: float
    ) -> bool:
        """Wait for all agents to join a sync point.

        Args:
            sync_id: Sync point identifier
            agents: Set of agent names to wait for
            timeout: Timeout in seconds

        Returns:
            True if all agents joined, False if timeout/failure
        """
        try:
            # Simulate agents joining (in real implementation, agents would call join_sync_point)
            for agent_name in agents:
                success = await self.synchronizer.join_sync_point(sync_id, agent_name)
                if not success:
                    return False
            return True

        except asyncio.TimeoutError:
            self.logger.warning(f"Timeout waiting for agents in sync {sync_id}")
            return False
        except Exception as e:
            self.logger.error(f"Error waiting for agents in sync {sync_id}: {e}")
            return False

    def get_flash_sync_status(self, sync_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of flash sync operation.

        Args:
            sync_id: Flash sync identifier

        Returns:
            Status dictionary or None if not found
        """
        result = self._active_flash_syncs.get(sync_id)
        if not result:
            return None

        return {
            "sync_id": result.sync_id,
            "state": result.state.value,
            "alpha_agents_synced": list(result.alpha_agents_synced),
            "regular_agents_synced": list(result.regular_agents_synced),
            "start_time": result.start_time.isoformat() if result.start_time else None,
            "alpha_completion_time": (
                result.alpha_completion_time.isoformat()
                if result.alpha_completion_time
                else None
            ),
            "completion_time": (
                result.completion_time.isoformat() if result.completion_time else None
            ),
            "error_message": result.error_message,
            "epoch_id": getattr(result, "epoch_id", None),
        }

    def cleanup_flash_sync(self, sync_id: str) -> bool:
        """Clean up completed flash sync operation.

        Args:
            sync_id: Flash sync identifier to clean up

        Returns:
            True if cleaned up, False if not found
        """
        result = self._active_flash_syncs.pop(sync_id, None)
        if result:
            # Clean up associated sync points
            self.synchronizer.cleanup_sync_point(f"{sync_id}_alpha")
            self.synchronizer.cleanup_sync_point(f"{sync_id}_regular")
            self.synchronizer.cleanup_sync_point(sync_id)
            self.logger.debug(f"Cleaned up flash sync {sync_id}")
            return True
        return False

    def list_active_flash_syncs(self) -> List[Dict[str, Any]]:
        """List all active flash sync operations.

        Returns:
            List of active flash sync status dictionaries
        """
        return [
            self.get_flash_sync_status(sync_id)
            for sync_id in self._active_flash_syncs.keys()
        ]
