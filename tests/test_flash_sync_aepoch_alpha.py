"""Tests for FlashSyncAepochAlpha functionality."""

import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch

import sys
from pathlib import Path

# Add the scripts directory to path and import directly from files
scripts_path = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_path))
sys.path.insert(0, str(scripts_path / "ai_agent" / "core"))

# Import directly from module files
from flash_sync_aepoch_alpha import (
    FlashSyncAepochAlpha,
    FlashSyncState,
    FlashSyncResult,
    EpochSyncResult,
    AgentSynchronizer,
)


@pytest.fixture
def mock_synchronizer():
    """Create a mock AgentSynchronizer for testing."""
    synchronizer = Mock(spec=AgentSynchronizer)
    synchronizer.create_sync_point = AsyncMock()
    synchronizer.join_sync_point = AsyncMock(return_value=True)
    synchronizer.cleanup_sync_point = Mock()
    return synchronizer


@pytest.fixture
def flash_sync(mock_synchronizer):
    """Create FlashSyncAepochAlpha instance for testing."""
    config = {
        "alpha_timeout": 10.0,
        "regular_timeout": 20.0,
        "epoch_window": 30.0,
        "max_flash_agents": 5,
    }
    return FlashSyncAepochAlpha(mock_synchronizer, config)


@pytest.mark.asyncio
async def test_flash_sync_initialization(flash_sync, mock_synchronizer):
    """Test FlashSyncAepochAlpha initialization."""
    assert flash_sync.synchronizer == mock_synchronizer
    assert flash_sync.config["alpha_timeout"] == 10.0
    assert flash_sync.config["regular_timeout"] == 20.0
    assert len(flash_sync._active_flash_syncs) == 0


@pytest.mark.asyncio
async def test_sync_alpha_agents_success(flash_sync, mock_synchronizer):
    """Test successful alpha agent synchronization."""
    alpha_agents = {"alpha1", "alpha2"}
    regular_agents = {"regular1", "regular2"}

    # Mock successful sync point creation and joining
    mock_synchronizer.create_sync_point.return_value = None
    mock_synchronizer.join_sync_point.return_value = True

    result = await flash_sync.sync_alpha_agents(
        sync_id="test_sync_001",
        alpha_agents=alpha_agents,
        regular_agents=regular_agents,
    )

    # Verify result
    assert result.sync_id == "test_sync_001"
    assert result.state == FlashSyncState.COMPLETED
    assert result.alpha_agents_synced == alpha_agents
    assert result.regular_agents_synced == regular_agents
    assert result.start_time is not None
    assert result.completion_time is not None
    assert result.error_message is None

    # Verify synchronizer calls
    assert mock_synchronizer.create_sync_point.call_count == 2
    expected_calls = [
        ("test_sync_001_alpha", alpha_agents, 10.0),
        ("test_sync_001_regular", regular_agents, 20.0),
    ]
    actual_calls = [
        call.args for call in mock_synchronizer.create_sync_point.call_args_list
    ]
    assert actual_calls == expected_calls


@pytest.mark.asyncio
async def test_sync_alpha_agents_alpha_only(flash_sync, mock_synchronizer):
    """Test alpha agent synchronization without regular agents."""
    alpha_agents = {"alpha1", "alpha2"}

    mock_synchronizer.create_sync_point.return_value = None
    mock_synchronizer.join_sync_point.return_value = True

    result = await flash_sync.sync_alpha_agents(
        sync_id="test_sync_002", alpha_agents=alpha_agents, regular_agents=None
    )

    assert result.state == FlashSyncState.COMPLETED
    assert result.alpha_agents_synced == alpha_agents
    assert len(result.regular_agents_synced) == 0
    assert mock_synchronizer.create_sync_point.call_count == 1


@pytest.mark.asyncio
async def test_sync_alpha_agents_failure(flash_sync, mock_synchronizer):
    """Test flash sync failure when alpha agents fail to sync."""
    alpha_agents = {"alpha1", "alpha2"}

    mock_synchronizer.create_sync_point.return_value = None
    mock_synchronizer.join_sync_point.return_value = False  # Simulate failure

    result = await flash_sync.sync_alpha_agents(
        sync_id="test_sync_003", alpha_agents=alpha_agents
    )

    assert result.state == FlashSyncState.FAILED
    assert result.error_message == "Alpha agent sync failed"
    assert len(result.alpha_agents_synced) == 0


@pytest.mark.asyncio
async def test_sync_with_epoch_success(flash_sync, mock_synchronizer):
    """Test successful epoch-based synchronization."""
    agents = {"agent1", "agent2", "agent3"}
    epoch_id = "EPOCH_ALPHA_001"

    mock_synchronizer.create_sync_point.return_value = None
    mock_synchronizer.join_sync_point.return_value = True

    result = await flash_sync.sync_with_epoch(
        sync_id="epoch_sync_001", agents=agents, epoch_id=epoch_id
    )

    assert isinstance(result, EpochSyncResult)
    assert result.sync_id == "epoch_sync_001"
    assert result.epoch_id == epoch_id
    assert result.state == FlashSyncState.COMPLETED
    assert result.regular_agents_synced == agents
    assert result.epoch_window_start is not None
    assert result.epoch_window_end is not None
    assert result.epoch_metrics is not None

    # Check epoch metrics
    metrics = result.epoch_metrics
    assert metrics["total_agents"] == 3
    assert "sync_duration" in metrics
    assert "epoch_utilization" in metrics
    assert 0.0 <= metrics["epoch_utilization"] <= 1.0


@pytest.mark.asyncio
async def test_sync_with_epoch_timeout(flash_sync, mock_synchronizer):
    """Test epoch sync timeout handling."""
    agents = {"agent1", "agent2"}

    mock_synchronizer.create_sync_point.return_value = None
    mock_synchronizer.join_sync_point.return_value = False  # Simulate timeout

    result = await flash_sync.sync_with_epoch(
        sync_id="epoch_sync_002", agents=agents, epoch_id="EPOCH_ALPHA_002"
    )

    assert result.state == FlashSyncState.FAILED
    assert result.error_message == "Epoch sync timed out"


def test_get_flash_sync_status(flash_sync):
    """Test getting flash sync status."""
    # Create a test result in active syncs
    result = FlashSyncResult(
        sync_id="test_status",
        state=FlashSyncState.COMPLETED,
        alpha_agents_synced={"alpha1"},
        regular_agents_synced={"regular1"},
        start_time=datetime.now(timezone.utc),
    )
    flash_sync._active_flash_syncs["test_status"] = result

    status = flash_sync.get_flash_sync_status("test_status")

    assert status is not None
    assert status["sync_id"] == "test_status"
    assert status["state"] == "completed"
    assert status["alpha_agents_synced"] == ["alpha1"]
    assert status["regular_agents_synced"] == ["regular1"]
    assert status["start_time"] is not None

    # Test non-existent sync
    assert flash_sync.get_flash_sync_status("nonexistent") is None


def test_cleanup_flash_sync(flash_sync, mock_synchronizer):
    """Test flash sync cleanup."""
    # Add a test sync to active syncs
    result = FlashSyncResult(
        sync_id="cleanup_test",
        state=FlashSyncState.COMPLETED,
        alpha_agents_synced=set(),
        regular_agents_synced=set(),
    )
    flash_sync._active_flash_syncs["cleanup_test"] = result

    # Test successful cleanup
    success = flash_sync.cleanup_flash_sync("cleanup_test")
    assert success is True
    assert "cleanup_test" not in flash_sync._active_flash_syncs

    # Verify synchronizer cleanup calls
    expected_cleanup_calls = [
        "cleanup_test_alpha",
        "cleanup_test_regular",
        "cleanup_test",
    ]
    actual_cleanup_calls = [
        call.args[0] for call in mock_synchronizer.cleanup_sync_point.call_args_list
    ]
    assert actual_cleanup_calls == expected_cleanup_calls

    # Test cleanup of non-existent sync
    success = flash_sync.cleanup_flash_sync("nonexistent")
    assert success is False


def test_list_active_flash_syncs(flash_sync):
    """Test listing active flash syncs."""
    # Initially empty
    active_syncs = flash_sync.list_active_flash_syncs()
    assert active_syncs == []

    # Add test syncs
    result1 = FlashSyncResult(
        sync_id="sync1",
        state=FlashSyncState.COMPLETED,
        alpha_agents_synced=set(),
        regular_agents_synced=set(),
    )
    result2 = FlashSyncResult(
        sync_id="sync2",
        state=FlashSyncState.ALPHA_SYNC,
        alpha_agents_synced=set(),
        regular_agents_synced=set(),
    )

    flash_sync._active_flash_syncs["sync1"] = result1
    flash_sync._active_flash_syncs["sync2"] = result2

    active_syncs = flash_sync.list_active_flash_syncs()
    assert len(active_syncs) == 2

    sync_ids = {sync["sync_id"] for sync in active_syncs}
    assert sync_ids == {"sync1", "sync2"}


@pytest.mark.asyncio
async def test_duplicate_sync_id_error(flash_sync):
    """Test error when using duplicate sync ID."""
    alpha_agents = {"alpha1"}

    # Add a sync to active syncs
    result = FlashSyncResult(
        sync_id="duplicate_test",
        state=FlashSyncState.READY,
        alpha_agents_synced=set(),
        regular_agents_synced=set(),
    )
    flash_sync._active_flash_syncs["duplicate_test"] = result

    # Try to create another sync with same ID
    with pytest.raises(ValueError, match="Flash sync duplicate_test already active"):
        await flash_sync.sync_alpha_agents(
            sync_id="duplicate_test", alpha_agents=alpha_agents
        )


def test_default_config():
    """Test default configuration creation."""
    mock_sync = Mock(spec=AgentSynchronizer)
    flash_sync = FlashSyncAepochAlpha(mock_sync)

    config = flash_sync.config
    assert config["alpha_timeout"] == 15.0
    assert config["regular_timeout"] == 30.0
    assert config["epoch_window"] == 60.0
    assert config["max_flash_agents"] == 10
    assert "priority_levels" in config
