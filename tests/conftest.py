"""
Test fixtures and utilities for EPOCH5 tests
"""
import pytest
import tempfile
import shutil
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing"""
    return {
        "did": "did:example:12345",
        "skills": ["data_analysis", "encryption"],
        "reliability_score": 0.95,
        "trust_score": 0.87,
        "status": "active"
    }


@pytest.fixture
def sample_policy_data():
    """Sample policy data for testing"""
    return {
        "policy_id": "test_policy_001",
        "type": "budget_limit",
        "conditions": {"max_budget": 1000},
        "enforcement_level": "strict"
    }


@pytest.fixture
def sample_capsule_data():
    """Sample capsule data for testing"""
    return {
        "capsule_id": "test_capsule_001",
        "content": b"Test capsule content",
        "metadata": {
            "created_at": "2024-01-01T00:00:00Z",
            "content_type": "text/plain",
            "size": 20
        }
    }