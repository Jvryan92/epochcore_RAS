"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import json
from dataclasses import asdict
from typing import Dict, List, Optional

from world_zones import Capacity, Dimensions, Zone, ZoneFeature, ZoneType


class WorldZoneManager:
    def __init__(self):
        self.zones: Dict[ZoneType, Zone] = {}
        # zone_id -> {instance_id -> player_count}
        self.active_instances: Dict[str, Dict[str, int]] = {}

    def initialize_zones(self):
        """Initialize the base game zones"""
        # Downtown Zone
        downtown = Zone(
            zone_type=ZoneType.DOWNTOWN,
            dimensions=Dimensions(
                width=800,    # 800m
                length=800,   # 800m
                max_height=50,  # Tallest skyscraper
                min_height=-10  # Underground areas
            ),
            capacity=Capacity(
                max_players=100,
                optimal_players=80,
                event_capacity=120,
                instance_limit=100
            ),
            features={},  # Will be populated with buildings, roads etc
            sightlines=[],
            spawn_points=[(400, 400, 0)]  # Center plaza
        )

        # Forest Village
        forest = Zone(
            zone_type=ZoneType.FOREST_VILLAGE,
            dimensions=Dimensions(
                width=600,
                length=600,
                max_height=30,  # Hilltop + water tower
                min_height=-5   # Cave
            ),
            capacity=Capacity(
                max_players=50,
                optimal_players=40,
                event_capacity=60,
                instance_limit=50
            ),
            features={},
            sightlines=[],
            spawn_points=[(300, 300, 0)]
        )

        # Neon District
        neon = Zone(
            zone_type=ZoneType.NEON_DISTRICT,
            dimensions=Dimensions(
                width=600,
                length=600,
                max_height=40,  # Tallest neon tower
                min_height=-8   # Underground arcade
            ),
            capacity=Capacity(
                max_players=80,
                optimal_players=60,
                event_capacity=100,
                instance_limit=80
            ),
            features={},
            sightlines=[],
            spawn_points=[(300, 300, 0)]
        )

        self.zones = {
            ZoneType.DOWNTOWN: downtown,
            ZoneType.FOREST_VILLAGE: forest,
            ZoneType.NEON_DISTRICT: neon
        }

    def create_zone_instance(self, zone_type: ZoneType) -> str:
        """Create a new instance of a zone"""
        if zone_type not in self.zones:
            return ""

        instance_id = f"{zone_type.value}-{len(self.active_instances)}"
        if instance_id not in self.active_instances:
            self.active_instances[instance_id] = {}

        return instance_id

    def add_player_to_instance(self, instance_id: str, player_id: str) -> bool:
        """Add a player to a zone instance"""
        if instance_id not in self.active_instances:
            return False

        # Get zone type from instance ID
        zone_type = ZoneType(instance_id.split("-")[0])
        zone = self.zones[zone_type]

        current_players = len(self.active_instances[instance_id])
        if current_players >= zone.capacity.instance_limit:
            return False

        self.active_instances[instance_id][player_id] = 1
        return True

    def remove_player_from_instance(self, instance_id: str, player_id: str):
        """Remove a player from a zone instance"""
        if instance_id in self.active_instances:
            if player_id in self.active_instances[instance_id]:
                del self.active_instances[instance_id][player_id]

    def get_zone_population(self, zone_type: ZoneType) -> Dict[str, int]:
        """Get current population of all instances of a zone"""
        populations = {}
        for instance_id in self.active_instances:
            if instance_id.startswith(zone_type.value):
                populations[instance_id] = len(self.active_instances[instance_id])
        return populations

    def export_zone_data(self) -> str:
        """Export zone configurations as JSON"""
        data = {
            "zones": {
                zone_type.value: asdict(zone)
                for zone_type, zone in self.zones.items()
            },
            "active_instances": self.active_instances
        }
        return json.dumps(data, indent=2)
