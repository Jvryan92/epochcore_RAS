"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class ZoneType(Enum):
    """Types of zones in EpochCore Open World."""
    PROLOGUE = "prologue"  # Tutorial/intro zones
    BIOME = "biome"        # Natural environment zones
    URBAN = "urban"        # City/built environment zones
    MYTHIC = "mythic"      # Legendary/fantasy zones
    COSMIC = "cosmic"      # Space/time zones
    SHADOW = "shadow"      # Dark/corrupted zones
    PRIMAL = "primal"      # Wild/nature zones
    UNDERWORLD = "underworld"  # Crypt/ghost zones
    RENAISSANCE = "renaissance"  # Civilization zones
    SINGULARITY = "singularity"  # Final convergence zones
    RAID = "raid"          # Boss raid zones


class SeasonPhase(Enum):
    """Game seasons/major content phases."""
    PROLOGUE = 0    # Tutorial season
    BIOMES = 1      # First major season
    ELEMENTAL = 2   # Elemental frontiers
    URBAN = 3       # Urban mesh metropolis
    MYTHIC = 4      # Mythic realms
    COSMIC = 5      # Cosmic/temporal
    SHADOW = 6      # Shadowfront
    PRIMAL = 7      # Wild meshfrontiers
    UNDERWORLD = 8  # Underworld mesh
    RENAISSANCE = 9  # Mesh renaissance
    SINGULARITY = 10  # Final season


@dataclass
class ZoneDimensions:
    """Physical dimensions and characteristics of a zone."""
    width: int   # Width in meters
    length: int  # Length in meters
    height: int  # Height in meters (for vertical zones)
    elevation_min: int = 0  # Minimum elevation in meters
    elevation_max: int = 0  # Maximum elevation in meters

    @property
    def area(self) -> int:
        """Calculate total ground area in square meters."""
        return self.width * self.length

    @property
    def volume(self) -> int:
        """Calculate total volume in cubic meters."""
        return self.width * self.length * self.height


@dataclass
class ZoneMechanics:
    """Gameplay mechanics and features of a zone."""
    core_mechanic: str  # Primary gameplay mechanic
    puzzle_type: Optional[str] = None  # Type of puzzles if any
    combat_type: Optional[str] = None  # Type of combat if any
    has_boss: bool = False  # Whether zone has a boss
    boss_name: Optional[str] = None  # Name of zone boss if any
    time_cycle: Optional[int] = None  # Time cycle in minutes if dynamic
    required_players: int = 1  # Minimum players needed


@dataclass
class ZoneRewards:
    """Rewards and unlocks available in a zone."""
    glyphs: List[str]  # Cosmetic glyph rewards
    safehouse_decor: List[str]  # Safehouse decoration unlocks
    meshcredit_min: int  # Minimum MeshCredit reward
    meshcredit_max: int  # Maximum MeshCredit reward


class Zone:
    """Base class for all zones in EpochCore Open World."""

    def __init__(
        self,
        zone_id: str,
        name: str,
        zone_type: ZoneType,
        season: SeasonPhase,
        dimensions: ZoneDimensions,
        mechanics: ZoneMechanics,
        rewards: ZoneRewards
    ):
        self.zone_id = zone_id
        self.name = name
        self.zone_type = zone_type
        self.season = season
        self.dimensions = dimensions
        self.mechanics = mechanics
        self.rewards = rewards
        self.is_active = False
        self.player_count = 0
        self.state: Dict = {}

    def activate(self) -> bool:
        """Activate the zone for play."""
        self.is_active = True
        return True

    def deactivate(self) -> bool:
        """Deactivate the zone."""
        self.is_active = False
        return True

    def update(self, delta_time: float) -> None:
        """Update zone state based on time passage."""
        if self.mechanics.time_cycle and self.is_active:
            current_cycle = self.state.get('time_cycle', 0)
            new_cycle = (current_cycle + delta_time) % self.mechanics.time_cycle
            self.state['time_cycle'] = new_cycle

    def get_player_count(self) -> int:
        """Get current number of players in zone."""
        return self.player_count

    def can_enter(self, player_count: int) -> bool:
        """Check if more players can enter the zone."""
        return True  # Override in specific zones for capacity limits

    def get_active_mechanics(self) -> List[str]:
        """Get list of currently active mechanics."""
        mechanics = [self.mechanics.core_mechanic]
        if self.mechanics.puzzle_type:
            mechanics.append(self.mechanics.puzzle_type)
        if self.mechanics.combat_type:
            mechanics.append(self.mechanics.combat_type)
        return mechanics

    def get_rewards_for_completion(self, score: float) -> ZoneRewards:
        """Calculate rewards based on completion score."""
        return self.rewards  # Override for dynamic rewards

    def __str__(self) -> str:
        return f"{self.name} ({self.zone_type.value}) - Season {self.season.value}"
