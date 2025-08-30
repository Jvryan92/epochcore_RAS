#!/usr/bin/env python3
"""Tests for epoch_scheduler.py flash sync functionality."""

import json
import pytest
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch, Mock
import sys

# Add the FounderALPHA scripts directory to path
scripts_path = Path(__file__).parent.parent / "FounderALPHA" / "scripts"
sys.path.insert(0, str(scripts_path))

import epoch_scheduler


@pytest.fixture
def sample_trigger_data():
    """Create sample trigger data for testing."""
    return [
        {"id": 1, "key": "ALPHA-001", "family": "ALPHA", "title": "Initialize Alpha", 
         "exec": "init_alpha", "comp": "low", "full": "Alpha initialization"},
        {"id": 2, "key": "ALPHA-002", "family": "ALPHA", "title": "Alpha Core Sync", 
         "exec": "sync_alpha", "comp": "medium", "full": "Alpha synchronization"},
        {"id": 3, "key": "BETA-001", "family": "BETA", "title": "Beta Test", 
         "exec": "test_beta", "comp": "high", "full": "Beta testing"},
        {"id": 4, "key": "ALPHA-003", "family": "ALPHA", "title": "Alpha Flash Sync", 
         "exec": "flash_sync_alpha", "comp": "critical", "full": "Flash sync with epochALPHA"}
    ]


@pytest.fixture
def temp_trigger_files(sample_trigger_data):
    """Create temporary trigger files for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create jsonl file
        jsonl_file = tmppath / "epoch_triggers.jsonl"
        with open(jsonl_file, "w") as f:
            for record in sample_trigger_data:
                f.write(json.dumps(record) + "\n")
        
        # Create edges file
        edges_file = tmppath / "epoch_triggers_edges.csv"
        with open(edges_file, "w") as f:
            f.write("from,to\n")
            f.write("1,2\n")
            f.write("2,4\n")
        
        yield jsonl_file, edges_file


def test_flash_sync_handler():
    """Test the flash_sync_handler function."""
    record = {"id": 1, "key": "ALPHA-001", "title": "Test Alpha"}
    intensity = 1500
    dry_run = True
    
    result = epoch_scheduler.flash_sync_handler(record, intensity, dry_run)
    
    assert result["sync_type"] == "flash"
    assert result["agent"] == "epochALPHA"
    assert result["intensity"] == intensity
    assert "timestamp" in result
    
    # Verify timestamp format
    timestamp = datetime.fromisoformat(result["timestamp"].replace('Z', '+00:00'))
    assert timestamp.tzinfo == timezone.utc


def test_run_step_with_flash_sync_handler():
    """Test run_step with flash sync handler during ignite phase."""
    record = {"id": 1, "key": "ALPHA-001", "title": "Test Alpha"}
    handlers = {"ignite": epoch_scheduler.flash_sync_handler}
    
    result = epoch_scheduler.run_step(
        record, "ignite", 1000, dry_run=True, handlers=handlers
    )
    
    assert result["id"] == 1
    assert result["phase"] == "ignite"
    assert result["action"] == "ignite"
    assert result["intensity"] == 1000
    assert result["status"] == "dry-run"
    
    # Verify flash sync handler was called
    assert "handler_result" in result
    handler_result = result["handler_result"]
    assert handler_result["sync_type"] == "flash"
    assert handler_result["agent"] == "epochALPHA"
    assert handler_result["intensity"] == 1000


def test_run_step_without_handlers():
    """Test run_step without handlers (non-ignite phases)."""
    record = {"id": 1, "key": "ALPHA-001", "title": "Test Alpha"}
    
    result = epoch_scheduler.run_step(
        record, "compress", 1000, dry_run=True, handlers=None
    )
    
    assert result["id"] == 1
    assert result["phase"] == "compress"
    assert result["action"] == "compress"
    assert "handler_result" not in result


def test_run_step_with_mesh_integration():
    """Test run_step with mesh integration enabled."""
    record = {"id": 1, "key": "ALPHA-001", "title": "Test Alpha"}
    
    def mock_mesh_integration(record, phase, intensity, dry_run):
        return {
            "mesh_enabled": True,
            "mesh_phase": phase,
            "mesh_record_id": record["id"]
        }
    
    result = epoch_scheduler.run_step(
        record, "compress", 1000, dry_run=True, 
        handlers=None, mesh_integration=mock_mesh_integration
    )
    
    assert result["id"] == 1
    assert "mesh_result" in result
    mesh_result = result["mesh_result"]
    assert mesh_result["mesh_enabled"] is True
    assert mesh_result["mesh_phase"] == "compress"
    assert mesh_result["mesh_record_id"] == 1


def test_run_step_ignite_with_both_handler_and_mesh():
    """Test run_step during ignite phase with both handler and mesh integration."""
    record = {"id": 1, "key": "ALPHA-001", "title": "Test Alpha"}
    handlers = {"ignite": epoch_scheduler.flash_sync_handler}
    
    def mock_mesh_integration(record, phase, intensity, dry_run):
        return {
            "mesh_enabled": True,
            "mesh_phase": phase,
            "mesh_record_id": record["id"]
        }
    
    result = epoch_scheduler.run_step(
        record, "ignite", 1000, dry_run=True,
        handlers=handlers, mesh_integration=mock_mesh_integration
    )
    
    # Verify both handler and mesh results are present
    assert "handler_result" in result
    assert "mesh_result" in result
    
    # Verify flash sync handler result
    handler_result = result["handler_result"]
    assert handler_result["sync_type"] == "flash"
    assert handler_result["agent"] == "epochALPHA"
    
    # Verify mesh integration result
    mesh_result = result["mesh_result"]
    assert mesh_result["mesh_enabled"] is True
    assert mesh_result["mesh_phase"] == "ignite"


def test_cycle_phase():
    """Test the phase cycling logic."""
    # Test with phase_window = 3
    phase_window = 3
    
    # First 3 should be compress
    assert epoch_scheduler.cycle_phase(0, phase_window) == "compress"
    assert epoch_scheduler.cycle_phase(1, phase_window) == "compress"
    assert epoch_scheduler.cycle_phase(2, phase_window) == "compress"
    
    # Next 3 should be ultracomp
    assert epoch_scheduler.cycle_phase(3, phase_window) == "ultracomp"
    assert epoch_scheduler.cycle_phase(4, phase_window) == "ultracomp"
    assert epoch_scheduler.cycle_phase(5, phase_window) == "ultracomp"
    
    # Next 3 should be ignite
    assert epoch_scheduler.cycle_phase(6, phase_window) == "ignite"
    assert epoch_scheduler.cycle_phase(7, phase_window) == "ignite"
    assert epoch_scheduler.cycle_phase(8, phase_window) == "ignite"
    
    # Should cycle back to compress
    assert epoch_scheduler.cycle_phase(9, phase_window) == "compress"


def test_main_flash_sync_ignite_phase(temp_trigger_files, capsys):
    """Test main function ensures flash sync triggers during ignite phase."""
    jsonl_file, edges_file = temp_trigger_files
    
    # Test with phase-window=1 to get quick ignite phases
    argv = [
        "--jsonl", str(jsonl_file),
        "--edges", str(edges_file),
        "--dry-run",
        "--limit", "4",
        "--phase-window", "1"
    ]
    
    epoch_scheduler.main(argv)
    captured = capsys.readouterr()
    
    # Parse the output lines
    lines = [line.strip() for line in captured.out.split('\n') if line.strip() and line.startswith('{')]
    
    # Find ignite phase entries and verify flash sync
    ignite_entries = []
    for line in lines:
        entry = json.loads(line)
        if entry.get("phase") == "ignite":
            ignite_entries.append(entry)
    
    # Should have at least one ignite entry
    assert len(ignite_entries) > 0
    
    # All ignite entries should have handler_result with flash sync
    for entry in ignite_entries:
        assert "handler_result" in entry
        handler_result = entry["handler_result"]
        assert handler_result["sync_type"] == "flash"
        assert handler_result["agent"] == "epochALPHA"


def test_main_with_mesh_integration_flag(temp_trigger_files, capsys):
    """Test main function with mesh integration enabled."""
    jsonl_file, edges_file = temp_trigger_files
    
    argv = [
        "--jsonl", str(jsonl_file),
        "--edges", str(edges_file),
        "--dry-run",
        "--limit", "3",
        "--phase-window", "1",
        "--mesh-integration"
    ]
    
    epoch_scheduler.main(argv)
    captured = capsys.readouterr()
    
    # Parse the output lines
    lines = [line.strip() for line in captured.out.split('\n') if line.strip() and line.startswith('{')]
    
    # All entries should have mesh_result
    mesh_entries = 0
    ignite_with_flash_and_mesh = 0
    
    for line in lines:
        entry = json.loads(line)
        if "mesh_result" in entry:
            mesh_entries += 1
            
        if entry.get("phase") == "ignite" and "handler_result" in entry and "mesh_result" in entry:
            ignite_with_flash_and_mesh += 1
            # Verify flash sync details
            handler_result = entry["handler_result"]
            assert handler_result["sync_type"] == "flash"
            assert handler_result["agent"] == "epochALPHA"
            
            # Verify mesh details
            mesh_result = entry["mesh_result"]
            assert mesh_result["mesh_enabled"] is True
            assert mesh_result["mesh_phase"] == "ignite"
    
    assert mesh_entries > 0  # Should have mesh results
    # Should have at least one ignite phase with both flash sync and mesh
    assert ignite_with_flash_and_mesh > 0


def test_policy_gate():
    """Test the policy gate function."""
    # Test allowed record
    good_record = {"title": "Safe Operation", "exec": "safe_exec", "comp": "low"}
    allowed, msg = epoch_scheduler.policy_gate(good_record)
    assert allowed is True
    assert msg == "ok"
    
    # Test blocked record
    bad_record = {"title": "Dangerous Operation", "exec": "explosive_exec", "comp": "high"}
    allowed, msg = epoch_scheduler.policy_gate(bad_record)
    assert allowed is False
    assert "explosive" in msg


def test_load_nodes():
    """Test loading nodes from JSONL file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        f.write('{"id": 1, "key": "TEST-001", "title": "Test Node 1"}\n')
        f.write('{"id": 2, "key": "TEST-002", "title": "Test Node 2"}\n')
        f.flush()
        
        nodes = epoch_scheduler.load_nodes(Path(f.name))
        
    assert len(nodes) == 2
    assert 1 in nodes
    assert 2 in nodes
    assert nodes[1]["key"] == "TEST-001"
    assert nodes[2]["key"] == "TEST-002"


def test_load_edges():
    """Test loading edges from CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('from,to\n')
        f.write('1,2\n')
        f.write('2,3\n')
        f.flush()
        
        edges = epoch_scheduler.load_edges(Path(f.name))
        
    assert len(edges) == 2
    assert (1, 2) in edges
    assert (2, 3) in edges


if __name__ == "__main__":
    pytest.main([__file__])