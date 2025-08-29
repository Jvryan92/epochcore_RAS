"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from .zone_base import SeasonPhase, Zone, ZoneType


class ZoneManager:
    """Manages all zones in EpochCore Open World."""

    def __init__(self):
        self.zones: Dict[str, Zone] = {}
        self.active_zones: Set[str] = set()
        self.season_zones: Dict[SeasonPhase, List[str]] = {
            phase: [] for phase in SeasonPhase
        }
        self.zone_types: Dict[ZoneType, List[str]] = {
            ztype: [] for ztype in ZoneType
        }

    def register_zone(self, zone: Zone) -> bool:
        """Register a new zone in the manager."""
        if zone.zone_id in self.zones:
            return False

        self.zones[zone.zone_id] = zone
        self.season_zones[zone.season].append(zone.zone_id)
        self.zone_types[zone.zone_type].append(zone.zone_id)
        return True

    def activate_zone(self, zone_id: str) -> bool:
        """Activate a specific zone."""
        if zone_id not in self.zones:
            return False

        zone = self.zones[zone_id]
        if zone.activate():
            self.active_zones.add(zone_id)
            return True
        return False

    def deactivate_zone(self, zone_id: str) -> bool:
        """Deactivate a specific zone."""
        if zone_id not in self.active_zones:
            return False

        zone = self.zones[zone_id]
        if zone.deactivate():
            self.active_zones.remove(zone_id)
            return True
        return False

    def get_season_zones(self, season: SeasonPhase) -> List[Zone]:
        """Get all zones for a specific season."""
        zone_ids = self.season_zones[season]
        return [self.zones[zid] for zid in zone_ids]

    def get_zone_type(self, zone_type: ZoneType) -> List[Zone]:
        """Get all zones of a specific type."""
        zone_ids = self.zone_types[zone_type]
        return [self.zones[zid] for zid in zone_ids]

    def get_active_zones(self) -> List[Zone]:
        """Get all currently active zones."""
        return [self.zones[zid] for zid in self.active_zones]

    def update_zones(self, delta_time: float) -> None:
        """Update all active zones."""
        for zone_id in self.active_zones:
            self.zones[zone_id].update(delta_time)

    def get_zone_stats(self) -> Dict:
        """Get statistics about all zones."""
        return {
            "total_zones": len(self.zones),
            "active_zones": len(self.active_zones),
            "zones_by_season": {
                season.name: len(zones)
                for season, zones in self.season_zones.items()
            },
            "zones_by_type": {
                ztype.name: len(zones)
                for ztype, zones in self.zone_types.items()
            }
        }

    def save_state(self, filepath: Path) -> bool:
        """Save current zone states to file."""
        try:
            state = {
                "active_zones": list(self.active_zones),
                "zone_states": {
                    zid: zone.state for zid, zone in self.zones.items()
                }
            }
            with open(filepath, 'w') as f:
                json.dump(state, f)
            return True
        except Exception:
            return False

    def load_state(self, filepath: Path) -> bool:
        """Load zone states from file."""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)

            # Restore active zones
            self.active_zones = set(state["active_zones"])

            # Restore zone states
            for zid, zone_state in state["zone_states"].items():
                if zid in self.zones:
                    self.zones[zid].state = zone_state
            return True
        except Exception:
            return False

    def __str__(self) -> str:
        return f"ZoneManager: {len(self.zones)} zones, {len(self.active_zones)} active"
