"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from ..zones.zone_manager import ZoneManager
from .mission_base import Mission, MissionType, SeasonPhase


class MissionManager:
    """Manages all missions and progression in EpochCore Open World."""

    def __init__(self, zone_manager: ZoneManager):
        self.zone_manager = zone_manager
        self.missions: Dict[str, Mission] = {}
        self.active_missions: Dict[str, Mission] = {}
        self.completed_missions: Dict[str, Mission] = {}
        self.season_missions: Dict[SeasonPhase, List[str]] = {
            phase: [] for phase in SeasonPhase
        }
        self.mission_types: Dict[MissionType, List[str]] = {
            mtype: [] for mtype in MissionType
        }

    def register_mission(self, mission: Mission) -> bool:
        """Register a new mission."""
        if mission.mission_id in self.missions:
            return False

        self.missions[mission.mission_id] = mission
        self.season_missions[mission.season].append(mission.mission_id)
        self.mission_types[mission.mission_type].append(mission.mission_id)
        return True

    def start_mission(self, mission_id: str, player_level: int) -> bool:
        """Start a mission for a player."""
        if mission_id not in self.missions:
            return False

        mission = self.missions[mission_id]
        completed = [m.mission_id for m in self.completed_missions.values()]

        if mission.can_start(player_level, completed):
            if mission.start():
                self.active_missions[mission_id] = mission
                return True
        return False

    def complete_mission(self, mission_id: str) -> bool:
        """Mark a mission as completed."""
        if mission_id not in self.active_missions:
            return False

        mission = self.active_missions[mission_id]
        if mission.complete():
            self.completed_missions[mission_id] = mission
            del self.active_missions[mission_id]
            return True
        return False

    def update_mission_progress(
        self,
        mission_id: str,
        objective_index: int,
        progress: int
    ) -> bool:
        """Update progress on a mission objective."""
        if mission_id not in self.active_missions:
            return False

        mission = self.active_missions[mission_id]
        return mission.update_objective(objective_index, progress)

    def get_available_missions(self, player_level: int) -> List[Mission]:
        """Get all missions available to start."""
        completed = [m.mission_id for m in self.completed_missions.values()]
        return [
            mission for mission in self.missions.values()
            if mission.can_start(player_level, completed)
            and mission.mission_id not in self.active_missions
            and mission.mission_id not in self.completed_missions
        ]

    def get_season_progress(self, season: SeasonPhase) -> Dict:
        """Get progress stats for a season."""
        season_missions = self.season_missions[season]
        total = len(season_missions)
        completed = sum(
            1 for mid in season_missions
            if mid in self.completed_missions
        )
        active = sum(
            1 for mid in season_missions
            if mid in self.active_missions
        )

        return {
            "total": total,
            "completed": completed,
            "active": active,
            "progress": (completed / total) if total > 0 else 0
        }

    def save_progress(self, filepath: Path) -> bool:
        """Save mission progress to file."""
        try:
            progress = {
                "active_missions": {
                    mid: mission.get_progress()
                    for mid, mission in self.active_missions.items()
                },
                "completed_missions": list(self.completed_missions.keys())
            }
            with open(filepath, 'w') as f:
                json.dump(progress, f)
            return True
        except Exception:
            return False

    def load_progress(self, filepath: Path) -> bool:
        """Load mission progress from file."""
        try:
            with open(filepath, 'r') as f:
                progress = json.load(f)

            # Restore completed missions
            for mission_id in progress["completed_missions"]:
                if mission_id in self.missions:
                    mission = self.missions[mission_id]
                    mission.complete()
                    self.completed_missions[mission_id] = mission

            # Restore active missions
            for mission_id, mission_progress in progress["active_missions"].items():
                if mission_id in self.missions:
                    mission = self.missions[mission_id]
                    if mission.start():
                        self.active_missions[mission_id] = mission
                        # Restore objective progress
                        for i, obj in enumerate(mission_progress["objectives"]):
                            if obj["completed"]:
                                mission.update_objective(i, obj["required"])
            return True
        except Exception:
            return False

    def __str__(self) -> str:
        return (
            f"MissionManager: {len(self.missions)} total, "
            f"{len(self.active_missions)} active, "
            f"{len(self.completed_missions)} completed"
        )
