"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""Test suite for verifying agent synchronization and functionality."""

from pathlib import Path

import pytest

from agent_sync import AgentMeshConnection, AgentProxy, RepoSyncManager


@pytest.mark.asyncio
async def test_repo_connection(sync_manager, test_config):
    """Test repository connection functionality."""
    for name, url in test_config["repo_urls"].items():
        repo = await sync_manager.connect_to_repo({"url": url})
        assert repo is not None
        assert url in sync_manager.known_repos


@pytest.mark.asyncio
async def test_agent_discovery():
    """Test that agents are properly discovered."""
    sync_manager = RepoSyncManager()
    await sync_manager.initialize_sync(str(Path.cwd()))

    # Connect to both repositories
    for url in ["https://github.com/Jvryan92/StategyDECK.git",
                "https://github.com/Jvryan92/epoch5-template.git"]:
        await sync_manager.connect_to_repo({"url": url})

        # Create mesh connection
        connection = AgentMeshConnection(url, sync_manager)
        await connection.initialize()

        # Verify agents are discovered
        assert len(connection.active_agents) > 0
        print(f"\nDiscovered agents in {url}:")
        for agent_name in connection.active_agents.keys():
            print(f"  - {agent_name}")


@pytest.mark.asyncio
async def test_capability_sync():
    """Test capability synchronization between agents."""
    sync_manager = RepoSyncManager()
    await sync_manager.initialize_sync(str(Path.cwd()))

    # Connect repositories
    sd_url = "https://github.com/Jvryan92/StategyDECK.git"
    ep_url = "https://github.com/Jvryan92/epoch5-template.git"

    await sync_manager.connect_to_repo({"url": sd_url})
    await sync_manager.connect_to_repo({"url": ep_url})

    # Create connections
    sd_conn = AgentMeshConnection(sd_url, sync_manager)
    ep_conn = AgentMeshConnection(ep_url, sync_manager)

    await sd_conn.initialize()
    await ep_conn.initialize()

    # Verify capabilities are synced
    for agent_name, proxy in sd_conn.active_agents.items():
        if proxy:
            caps = await proxy.get_capabilities()
            assert len(caps) > 0
            print(f"\nCapabilities for {agent_name}:")
            for cap in caps:
                print(f"  - {cap}")
