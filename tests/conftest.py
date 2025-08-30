"""Test configuration and fixtures."""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Generator

import pytest

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


@pytest.fixture
def test_config() -> dict:
    """Return test configuration."""
    return {
        "assets": {
            "icons": {
                "sizes": ["16px", "32px", "48px"],
                "variants": ["dark", "light"],
                "colors": ["flat-orange", "burnt-orange", "copper-foil"]
            }
        }
    }
