"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import pytest


def pytest_configure(config):
            "core": "*agent*.py",
            "meta": "meta_*.py"
        },
        "capability_map": {
            "strategy_cognitive": ["reasoning", "learning", "adaptation"],
            "strategy_ethical": ["moral_evaluation", "constraint_checking"],
            "strategy_intelligence": ["planning", "optimization"],
            "strategy_resilience": ["error_handling", "recovery"]
        }
    }


@pytest.fixture
async def sync_manager():
    """Provide a configured sync manager instance."""
from typing import Generator
from pathlib import Path
import tempfile
import shutil
import sys
import pytest
import os
import asyncio
    from agent_sync import RepoSyncManager
    manager = RepoSyncManager()
    await manager.initialize_sync(str(Path.cwd()))
    return managere NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""Test configuration and fixtures."""


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def repo_root() -> Path:
    """Return the repository root path."""
    return project_root


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_icon_path() -> Path:
    """Return path to a sample icon file."""
    return project_root / "assets" / "icons" / "dark" / "flat-orange" / "48px" / "web" / "strategy_icon-dark-flat-orange-48px.png"


"""Test configuration and fixtures."""


# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Provide test configuration."""
    config = {
        "repo_urls": {
            "strategydeck": "https://github.com/Jvryan92/StategyDECK.git",
            "epoch5": "https://github.com/Jvryan92/epoch5-template.git"
        },
        "agent_paths": {
            "strategy": "strategy_*.py",
            "core": "*agent*.py",
            "meta": "meta_*.py"
        }
    }
    return config
    return {
        "repo_urls": {
            "strategydeck": "https://github.com/Jvryan92/StategyDECK.git",
            "epoch5": "https://github.com/Jvryan92/epoch5-template.git"
        },
        "agent_paths": {
            "strategy": "strategy_*.py",
            "core": "*agent*.py",
            "meta": "meta_*.py"
        },
        "capability_map": {
            "strategy_cognitive": ["reasoning", "learning", "adaptation"],
            "strategy_ethical": ["moral_evaluation", "constraint_checking"],
            "strategy_intelligence": ["planning", "optimization"],
            "strategy_resilience": ["error_handling", "recovery"]
        }
    }


@pytest.fixture
async def sync_manager():
    """Provide a configured sync manager instance."""
    from agent_sync import RepoSyncManager
    manager = RepoSyncManager()
    await manager.initialize_sync(str(Path.cwd()))
    return manager
    }
