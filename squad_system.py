"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set


class SquadRole(Enum):
    ANCHOR = "anchor"      # Ari Vox
    CHRONICLER = "chronicler"  # Liora
    BASTION = "bastion"    # Kael Drav
    PATHFINDER = "pathfinder"  # Veyra Sol
    BREAKER = "breaker"    # Nyx Varra (antagonist)


class PowerType(Enum):
    ECHO_RECALL = "echo_recall"
    P95_CALM = "p95_calm"
    UNITY_SEAL = "unity_seal"
    WR_PACE = "wr_pace"
    SEQUENCE_BREAK = "sequence_break"


@dataclass
class SquadPower:
    type: PowerType
    cooldown: float  # seconds
    duration: float  # seconds
    intensity: float  # power level 0-1
    requires_allies: int = 0  # number of allies needed to activate


@dataclass
class SquadMember:
    name: str
    role: SquadRole
    signature_power: SquadPower
    position: tuple[float, float, float]  # x, y, z coordinates
    active_effects: Set[str]
    health: float = 100.0
    energy: float = 100.0

    def can_use_power(self, squad: 'Squad') -> bool:
        """Check if member can use their signature power"""
        if self.energy < 30.0:  # Base energy cost
            return False

        if self.signature_power.requires_allies > 0:
            nearby_allies = squad.get_nearby_allies(self.position, radius=10.0)
            if len(nearby_allies) < self.signature_power.requires_allies:
                return False

        return True


class Squad:
    def __init__(self):
        self.members: Dict[str, SquadMember] = {}
        self.active_powers: List[tuple[PowerType, float]] = []  # power and expiry time

    def initialize_squad(self):
        """Create the core squad members"""
        # Ari Vox - The Mesh Anchor
        ari = SquadMember(
            name="Ari Vox",
            role=SquadRole.ANCHOR,
            signature_power=SquadPower(
                type=PowerType.ECHO_RECALL,
                cooldown=30.0,
                duration=10.0,
                intensity=0.8
            ),
            position=(0, 0, 0),
            active_effects=set()
        )

        # Liora - The Chroniclebearer
        liora = SquadMember(
            name="Liora",
            role=SquadRole.CHRONICLER,
            signature_power=SquadPower(
                type=PowerType.P95_CALM,
                cooldown=45.0,
                duration=15.0,
                intensity=0.7
            ),
            position=(0, 0, 0),
            active_effects=set()
        )

        # Kael Drav - The Bastionkeeper
        kael = SquadMember(
            name="Kael Drav",
            role=SquadRole.BASTION,
            signature_power=SquadPower(
                type=PowerType.UNITY_SEAL,
                cooldown=60.0,
                duration=20.0,
                intensity=1.0,
                requires_allies=2  # Needs 2 allies in shield
            ),
            position=(0, 0, 0),
            active_effects=set()
        )

        # Veyra Sol - The Starpathfinder
        veyra = SquadMember(
            name="Veyra Sol",
            role=SquadRole.PATHFINDER,
            signature_power=SquadPower(
                type=PowerType.WR_PACE,
                cooldown=40.0,
                duration=8.0,
                intensity=0.9
            ),
            position=(0, 0, 0),
            active_effects=set()
        )

        self.members = {
            "ari": ari,
            "liora": liora,
            "kael": kael,
            "veyra": veyra
        }

    def get_nearby_allies(self, position: tuple[float, float, float],
                          radius: float) -> List[SquadMember]:
        """Get allies within radius of position"""
        nearby = []
        for member in self.members.values():
            dx = member.position[0] - position[0]
            dy = member.position[1] - position[1]
            dz = member.position[2] - position[2]
            distance = (dx*dx + dy*dy + dz*dz) ** 0.5
            if distance <= radius:
                nearby.append(member)
        return nearby

    def activate_power(self, member_id: str) -> bool:
        """Attempt to activate a squad member's power"""
        if member_id not in self.members:
            return False

        member = self.members[member_id]
        if not member.can_use_power(self):
            return False

        # Deduct energy cost
        member.energy -= 30.0

        # Add power effect
        import time
        expiry = time.time() + member.signature_power.duration
        self.active_powers.append((member.signature_power.type, expiry))

        # Special power effects
        if member.signature_power.type == PowerType.UNITY_SEAL:
            nearby = self.get_nearby_allies(member.position, 10.0)
            for ally in nearby:
                ally.active_effects.add("unity_shield")

        return True

    def update(self, dt: float):
        """Update squad state"""
        import time
        current_time = time.time()

        # Update active powers
        self.active_powers = [
            (power, expiry) for power, expiry in self.active_powers
            if expiry > current_time
        ]

        # Regenerate energy
        for member in self.members.values():
            member.energy = min(100.0, member.energy + 5.0 * dt)
