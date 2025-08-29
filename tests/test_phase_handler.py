"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import pytest

from phase_handler import PhaseHandler


def test_basic_phase_transition():
    handler = PhaseHandler()

    # Test simple phase
    assert handler.handle_phase(2001, "compress", "ok")
    assert 2001 in handler.states
    assert handler.states[2001].phase == "compress"
    assert handler.states[2001].status == "ok"


def test_dependency_validation():
    handler = PhaseHandler()

    # Set up dependency
    assert handler.handle_phase(2000, "compress", "ok")

    # Test with valid dependency
    assert handler.handle_phase(2001, "compress", "ok", dependencies=[2000])

    # Test with invalid dependency
    assert not handler.handle_phase(2002, "compress", "ok", dependencies=[9999])


def test_oscillation_validation():
    handler = PhaseHandler()

    # Initial phase
    assert handler.handle_phase(2001, "compress", "ok")

    # Oscillation check
    assert handler.handle_phase(2001, "oscillate", "audit")
    assert handler.verify_oscillation(2001)

    # Next phase
    assert handler.handle_phase(2001, "ultracomp", "ok")

    # Another oscillation
    assert handler.handle_phase(2001, "oscillate", "audit")
    assert handler.verify_oscillation(2001)


def test_invalid_oscillation():
    handler = PhaseHandler()

    # Test invalid phase
    assert not handler.handle_phase(2001, "oscillate", "ok")

    # Test invalid verification
    assert not handler.verify_oscillation(9999)
