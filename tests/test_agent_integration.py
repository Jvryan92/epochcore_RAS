"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

from pathlib import Path

import pytest

from agent_sync import AgentMeshConnection, RepoSyncManager


@pytest.mark.asyncio
async def test_agent_discovery(sync_manager, test_config):
    """Test that agents are properly discovered and loaded."""
    # Connect to both repositories
    for name, url in test_config["repo_urls"].items():
        await sync_manager.connect_to_repo({"url": url})

    # Verify connections are established
    assert len(sync_manager.known_repos) == 2

    # Create mesh connections
    connections = {}
    for repo_url in sync_manager.known_repos:
        connection = AgentMeshConnection(repo_url, sync_manager)
        await connection.initialize()
        connections[repo_url] = connection

    # Verify agents are discovered
    for conn in connections.values():
        assert len(conn.active_agents) > 0

        # Check capability synchronization
        for agent_name, proxy in conn.active_agents.items():
            assert len(conn.shared_capabilities[agent_name]) > 0


@pytest.mark.asyncio
async def test_agent_interaction(sync_manager, test_config):
    """Test that agents can interact across repositories."""
    # Set up connections
    strategydeck_url = test_config["repo_urls"]["strategydeck"]
    epoch5_url = test_config["repo_urls"]["epoch5"]

    await sync_manager.connect_to_repo({"url": strategydeck_url})
    await sync_manager.connect_to_repo({"url": epoch5_url})

    # Create mesh connections
    sd_conn = AgentMeshConnection(strategydeck_url, sync_manager)
    ep_conn = AgentMeshConnection(epoch5_url, sync_manager)

    await sd_conn.initialize()
    await ep_conn.initialize()

    # Verify cross-repo agent links
    for agent_name, proxy in sd_conn.active_agents.items():
        if proxy and proxy.remote_instances:
            assert any(epoch5_url in url for url in proxy.remote_instances.keys())

    for agent_name, proxy in ep_conn.active_agents.items():
        if proxy and proxy.remote_instances:
            assert any(strategydeck_url in url for url in proxy.remote_instances.keys())
