#!/usr/bin/env python3
"""
Example usage of flash_sync_with_aepochALPHA feature.

This demonstrates the basic functionality and integration patterns
for the FlashSyncAepochAlpha synchronization system.
"""

import asyncio
import logging
from datetime import datetime, timezone
import sys
from pathlib import Path

# Add scripts path for imports
sys.path.insert(0, str(Path(__file__).parent / "scripts" / "ai_agent" / "core"))

from flash_sync_aepoch_alpha import FlashSyncAepochAlpha, AgentSynchronizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demo_alpha_flash_sync():
    """Demonstrate alpha priority flash sync."""
    logger.info("=== Alpha Flash Sync Demo ===")

    # Initialize components
    synchronizer = AgentSynchronizer(timeout=30.0)
    flash_sync = FlashSyncAepochAlpha(
        synchronizer=synchronizer,
        config={
            "alpha_timeout": 10.0,
            "regular_timeout": 20.0,
            "epoch_window": 30.0,
            "max_flash_agents": 8,
        },
    )

    # Define agent groups
    alpha_agents = {"alpha_trader", "alpha_analyzer"}
    regular_agents = {"trader1", "trader2", "analyzer1"}

    logger.info(f"Alpha agents: {alpha_agents}")
    logger.info(f"Regular agents: {regular_agents}")

    # Execute flash sync with alpha priority
    try:
        result = await flash_sync.sync_alpha_agents(
            sync_id="demo_flash_001",
            alpha_agents=alpha_agents,
            regular_agents=regular_agents,
        )

        logger.info(f"Flash sync completed: {result.state.value}")
        logger.info(f"Alpha agents synced: {result.alpha_agents_synced}")
        logger.info(f"Regular agents synced: {result.regular_agents_synced}")

        if result.start_time and result.completion_time:
            duration = (result.completion_time - result.start_time).total_seconds()
            logger.info(f"Total sync time: {duration:.2f} seconds")

        # Get sync status
        status = flash_sync.get_flash_sync_status("demo_flash_001")
        logger.info(f"Final status: {status}")

        # Cleanup
        flash_sync.cleanup_flash_sync("demo_flash_001")

    except Exception as e:
        logger.error(f"Flash sync failed: {e}")


async def demo_epoch_sync():
    """Demonstrate epoch-based synchronization."""
    logger.info("\n=== Epoch Sync Demo ===")

    # Initialize components
    synchronizer = AgentSynchronizer(timeout=30.0)
    flash_sync = FlashSyncAepochAlpha(synchronizer=synchronizer)

    # Define agents for epoch processing
    epoch_agents = {"epoch_processor1", "epoch_processor2", "epoch_validator"}
    epoch_id = "ALPHA_EPOCH_20240101"

    logger.info(f"Epoch agents: {epoch_agents}")
    logger.info(f"Epoch ID: {epoch_id}")

    try:
        result = await flash_sync.sync_with_epoch(
            sync_id="demo_epoch_001",
            agents=epoch_agents,
            epoch_id=epoch_id,
            epoch_config={"epoch_window": 45.0},
        )

        logger.info(f"Epoch sync completed: {result.state.value}")
        logger.info(f"Agents synced: {result.regular_agents_synced}")
        logger.info(
            f"Epoch window: {result.epoch_window_start} to {result.epoch_window_end}"
        )

        if result.epoch_metrics:
            metrics = result.epoch_metrics
            logger.info(f"Sync metrics: {metrics}")
            logger.info(f"  - Total agents: {metrics['total_agents']}")
            logger.info(f"  - Sync duration: {metrics['sync_duration']:.2f}s")
            logger.info(f"  - Epoch utilization: {metrics['epoch_utilization']:.1%}")

        # Cleanup
        flash_sync.cleanup_flash_sync("demo_epoch_001")

    except Exception as e:
        logger.error(f"Epoch sync failed: {e}")


async def demo_concurrent_syncs():
    """Demonstrate concurrent flash sync operations."""
    logger.info("\n=== Concurrent Sync Demo ===")

    synchronizer = AgentSynchronizer(timeout=30.0)
    flash_sync = FlashSyncAepochAlpha(synchronizer=synchronizer)

    # Create multiple concurrent sync operations
    sync_tasks = []

    # Task 1: Alpha sync for trading
    sync_tasks.append(
        flash_sync.sync_alpha_agents(
            sync_id="concurrent_trade_001",
            alpha_agents={"alpha_trader_1"},
            regular_agents={"trader_a", "trader_b"},
        )
    )

    # Task 2: Epoch sync for analysis
    sync_tasks.append(
        flash_sync.sync_with_epoch(
            sync_id="concurrent_analysis_001",
            agents={"analyzer_1", "analyzer_2"},
            epoch_id="ANALYSIS_EPOCH_001",
        )
    )

    # Task 3: Alpha sync for monitoring
    sync_tasks.append(
        flash_sync.sync_alpha_agents(
            sync_id="concurrent_monitor_001",
            alpha_agents={"alpha_monitor"},
            regular_agents={"monitor_a"},
        )
    )

    try:
        logger.info("Starting concurrent sync operations...")
        results = await asyncio.gather(*sync_tasks, return_exceptions=True)

        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                logger.error(f"Task {i} failed: {result}")
            else:
                logger.info(
                    f"Task {i} completed: {result.state.value} (ID: {result.sync_id})"
                )

        # Show active syncs
        active_syncs = flash_sync.list_active_flash_syncs()
        logger.info(f"Active syncs: {len(active_syncs)}")

        # Cleanup all syncs
        for sync_info in active_syncs:
            flash_sync.cleanup_flash_sync(sync_info["sync_id"])
            logger.info(f"Cleaned up sync: {sync_info['sync_id']}")

    except Exception as e:
        logger.error(f"Concurrent sync demo failed: {e}")


async def main():
    """Run all demo scenarios."""
    logger.info("Flash Sync with aepochALPHA - Demo Application")
    logger.info("=" * 50)

    try:
        # Run demonstration scenarios
        await demo_alpha_flash_sync()
        await demo_epoch_sync()
        await demo_concurrent_syncs()

        logger.info("\n" + "=" * 50)
        logger.info("All demos completed successfully!")

    except Exception as e:
        logger.error(f"Demo application failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
