"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from ..zones.zone_base import SeasonPhase, Zone


class MissionType(Enum):
    """Types of missions in EpochCore Open World."""
    TUTORIAL = "tutorial"          # Teaching new mechanics
    STORY = "story"               # Main narrative missions
    HUNT = "hunt"                # Beast/target hunting
    PUZZLE = "puzzle"            # Pure puzzle solving
    RAID = "raid"                # Multi-player raids
    GOVERNANCE = "governance"    # Political/voting missions
    COLLECTION = "collection"    # Resource gathering
    EXPLORATION = "exploration"  # World discovery
    COMBAT = "combat"           # Pure combat focus
    HYBRID = "hybrid"           # Mixed objective types


@dataclass
class MissionObjective:
    """Individual mission objective."""
    description: str
    required_count: int = 1
    current_count: int = 0
    completed: bool = False

    def update(self, count: int) -> bool:
        """Update objective progress."""
        self.current_count += count
        if self.current_count >= self.required_count:
            self.completed = True
        return self.completed


@dataclass
class MissionRewards:
    """Rewards for completing a mission."""
    meshcredit: int
    glyphs: List[str]
    safehouse_items: List[str]
    experience: int
    achievement_id: Optional[str] = None


class Mission:
    """Base class for all missions in EpochCore Open World."""

    def __init__(
        self,
        mission_id: str,
        name: str,
        mission_type: MissionType,
        season: SeasonPhase,
        zone: Zone,
        objectives: List[MissionObjective],
        rewards: MissionRewards,
        required_level: int = 1,
        required_missions: List[str] = None
    ):
        self.mission_id = mission_id
        self.name = name
        self.mission_type = mission_type
        self.season = season
        self.zone = zone
        self.objectives = objectives
        self.rewards = rewards
        self.required_level = required_level
        self.required_missions = required_missions or []
        self.is_active = False
        self.is_completed = False
        self.start_time = None
        self.completion_time = None

    def can_start(self, player_level: int, completed_missions: List[str]) -> bool:
        """Check if mission can be started."""
        if player_level < self.required_level:
            return False

        if not all(mid in completed_missions for mid in self.required_missions):
            return False

        return True

    def start(self) -> bool:
        """Start the mission."""
        if self.is_active or self.is_completed:
            return False

        self.is_active = True
        from datetime import datetime
        self.start_time = datetime.now()
        return True

    def update_objective(self, objective_index: int, progress: int) -> bool:
        """Update progress on a specific objective."""
        if not self.is_active or self.is_completed:
            return False

        if objective_index >= len(self.objectives):
            return False

        objective = self.objectives[objective_index]
        if objective.update(progress):
            self._check_completion()
        return True

    def _check_completion(self) -> bool:
        """Check if all objectives are completed."""
        if all(obj.completed for obj in self.objectives):
            self.complete()
            return True
        return False

    def complete(self) -> bool:
        """Mark mission as completed."""
        if not self.is_active or self.is_completed:
            return False

        self.is_active = False
        self.is_completed = True
        from datetime import datetime
        self.completion_time = datetime.now()
        return True

    def get_progress(self) -> Dict:
        """Get current mission progress."""
        return {
            "active": self.is_active,
            "completed": self.is_completed,
            "objectives": [
                {
                    "description": obj.description,
                    "progress": obj.current_count,
                    "required": obj.required_count,
                    "completed": obj.completed
                }
                for obj in self.objectives
            ]
        }

    def __str__(self) -> str:
        status = "Completed" if self.is_completed else "Active" if self.is_active else "Not Started"
        return f"{self.name} ({self.mission_type.value}) - {status}"
