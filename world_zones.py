"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class ZoneType(Enum):
    DOWNTOWN = "downtown"
    FOREST_VILLAGE = "forest_village"
    NEON_DISTRICT = "neon_district"


@dataclass
class Dimensions:
    width: float  # meters
    length: float  # meters
    max_height: float  # meters for tallest structure
    min_height: float  # meters for lowest point (e.g. tunnels)


@dataclass
class Capacity:
    max_players: int
    optimal_players: int
    event_capacity: int  # For special events
    instance_limit: int  # Technical limit per instance


@dataclass
class ZoneFeature:
    name: str
    location: Tuple[float, float, float]  # x, y, z coordinates
    dimensions: Dimensions
    capacity: int  # How many players can interact simultaneously
    category: str  # social, market, puzzle, transport, etc.
    connectivity: List[str]  # IDs of connected features


@dataclass
class Zone:
    zone_type: ZoneType
    dimensions: Dimensions
    capacity: Capacity
    features: Dict[str, ZoneFeature]
    sightlines: List[Tuple[str, str]]  # Pairs of intervisible features
    spawn_points: List[Tuple[float, float, float]]

    def get_area(self) -> float:
        """Get zone area in square kilometers"""
        return (self.dimensions.width * self.dimensions.length) / 1_000_000

    def is_at_capacity(self, current_players: int) -> bool:
        """Check if zone is at player capacity"""
        return current_players >= self.capacity.max_players
