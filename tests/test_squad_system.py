"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import pytest

from squad_system import PowerType, Squad, SquadRole


def test_squad_initialization():
    squad = Squad()
    squad.initialize_squad()

    assert len(squad.members) == 4  # Core squad without Nyx
    assert "ari" in squad.members
    assert squad.members["ari"].role == SquadRole.ANCHOR

    # Verify signature powers
    assert squad.members["ari"].signature_power.type == PowerType.ECHO_RECALL
    assert squad.members["kael"].signature_power.requires_allies == 2


def test_power_activation():
    squad = Squad()
    squad.initialize_squad()

    # Test Ari's Echo Recall
    assert squad.activate_power("ari")  # Should succeed with full energy
    assert squad.members["ari"].energy < 100.0  # Energy consumed
    assert len(squad.active_powers) == 1

    # Test Kael's Unity Seal (should fail without nearby allies)
    squad.members["kael"].position = (0, 0, 0)
    assert not squad.activate_power("kael")  # Should fail - needs 2 allies

    # Position allies nearby and try again
    squad.members["ari"].position = (1, 0, 0)
    squad.members["liora"].position = (0, 1, 0)
    assert squad.activate_power("kael")  # Should succeed with allies

    # Verify Unity Shield effect
    nearby = squad.get_nearby_allies((0, 0, 0), 10.0)
    assert all("unity_shield" in member.active_effects for member in nearby)


def test_energy_regeneration():
    squad = Squad()
    squad.initialize_squad()

    # Use Veyra's power to consume energy
    assert squad.activate_power("veyra")
    initial_energy = squad.members["veyra"].energy

    # Update with time passing
    squad.update(1.0)  # 1 second
    assert squad.members["veyra"].energy > initial_energy


def test_nearby_allies():
    squad = Squad()
    squad.initialize_squad()

    # Position squad members
    squad.members["ari"].position = (0, 0, 0)
    squad.members["liora"].position = (5, 0, 0)  # 5 units away
    squad.members["kael"].position = (20, 0, 0)  # 20 units away

    nearby = squad.get_nearby_allies((0, 0, 0), 10.0)
    assert len(nearby) == 2  # Should find Ari and Liora
    assert squad.members["kael"] not in nearby  # Too far
