"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import math
from pathlib import Path
from typing import Dict, List

from ..zones.zone_base import SeasonPhase, Zone, ZoneType
from .map_renderer import MapConnection, MapNode, MapTheme, WorldMapRenderer


class WorldMapGenerator:
    """Generates the complete world map visualization."""

    def __init__(self):
        self.renderer = WorldMapRenderer()
        self.zone_themes = {
            # Prologue & Early Seasons (Root-like, organic)
            SeasonPhase.PROLOGUE: MapTheme.ROOT_GREEN,
            SeasonPhase.BIOMES: MapTheme.ROOT_GREEN,

            # Mid Seasons (Mystical to Neon)
            SeasonPhase.ELEMENTAL: MapTheme.MYSTIC_PURPLE,
            SeasonPhase.URBAN: MapTheme.NEON_BLUE,
            SeasonPhase.MYTHIC: MapTheme.MYSTIC_PURPLE,

            # Late Seasons (Void to Radiant)
            SeasonPhase.COSMIC: MapTheme.VOID_BLACK,
            SeasonPhase.SHADOW: MapTheme.VOID_BLACK,
            SeasonPhase.PRIMAL: MapTheme.NEON_BLUE,
            SeasonPhase.UNDERWORLD: MapTheme.VOID_BLACK,

            # Final Seasons (Ascension)
            SeasonPhase.RENAISSANCE: MapTheme.RADIANT_GOLD,
            SeasonPhase.SINGULARITY: MapTheme.RADIANT_GOLD
        }

    def _calculate_node_position(
        self,
        season: SeasonPhase,
        index: int,
        total: int
    ) -> tuple[float, float]:
        """Calculate node position based on season and index."""
        # Vertical position based on season (0 at bottom, 1 at top)
        y = season.value / (len(SeasonPhase) - 1)

        # Horizontal position in arc formation
        if total > 1:
            angle = (index / (total - 1) - 0.5) * math.pi * 0.8
            radius = 0.2  # Radius of the arc
            x = 0.5 + math.sin(angle) * radius
        else:
            x = 0.5

        return x, y

    def _get_zone_icon(self, zone: Zone) -> str:
        """Get icon path based on zone type."""
        icon_map = {
            ZoneType.BIOME: "assets/icons/biome.svg",
            ZoneType.URBAN: "assets/icons/urban.svg",
            ZoneType.MYTHIC: "assets/icons/mythic.svg",
            ZoneType.COSMIC: "assets/icons/cosmic.svg",
            ZoneType.SHADOW: "assets/icons/shadow.svg",
            ZoneType.PRIMAL: "assets/icons/primal.svg",
            ZoneType.UNDERWORLD: "assets/icons/underworld.svg",
            ZoneType.RENAISSANCE: "assets/icons/renaissance.svg",
            ZoneType.SINGULARITY: "assets/icons/singularity.svg",
            ZoneType.RAID: "assets/icons/raid.svg"
        }
        return icon_map.get(zone.zone_type, "assets/icons/default.svg")

    def generate_map(self, zones: Dict[str, Zone]) -> None:
        """Generate the complete world map from all zones."""
        # Group zones by season
        season_zones: Dict[SeasonPhase, List[Zone]] = {
            phase: [] for phase in SeasonPhase
        }
        for zone in zones.values():
            season_zones[zone.season].append(zone)

        # Create nodes for each zone
        for season, season_zones_list in season_zones.items():
            total_zones = len(season_zones_list)
            for i, zone in enumerate(season_zones_list):
                x, y = self._calculate_node_position(season, i, total_zones)

                # Create node
                node = MapNode(
                    x=x,
                    y=y,
                    radius=0.02 if zone.zone_type != ZoneType.RAID else 0.03,
                    glow_intensity=0.8 if zone.zone_type == ZoneType.RAID else 0.6,
                    icon_path=self._get_zone_icon(zone),
                    theme=self.zone_themes[season],
                    connected_to=[],
                    zone_id=zone.zone_id
                )
                self.renderer.add_node(zone.zone_id, node)

        # Create connections between nodes
        for season in SeasonPhase:
            if season == SeasonPhase.PROLOGUE:
                continue

            prev_season = SeasonPhase(season.value - 1)
            current_zones = season_zones[season]
            prev_zones = season_zones[prev_season]

            # Connect to previous season's raid boss or central node
            if prev_zones:
                prev_raid = next(
                    (z for z in prev_zones if z.zone_type == ZoneType.RAID),
                    prev_zones[len(prev_zones)//2]  # Center node if no raid
                )

                for zone in current_zones:
                    connection = MapConnection(
                        start_node=prev_raid.zone_id,
                        end_node=zone.zone_id,
                        thickness=2 if zone.zone_type == ZoneType.RAID else 1,
                        glow_intensity=0.7,
                        theme=self.zone_themes[season],
                        is_root=season.value <= SeasonPhase.BIOMES.value
                    )
                    self.renderer.add_connection(connection)

            # Connect nodes within season
            for i, zone in enumerate(current_zones):
                if i > 0:
                    connection = MapConnection(
                        start_node=current_zones[i-1].zone_id,
                        end_node=zone.zone_id,
                        thickness=1,
                        glow_intensity=0.5,
                        theme=self.zone_themes[season],
                        is_root=season.value <= SeasonPhase.BIOMES.value
                    )
                    self.renderer.add_connection(connection)

    def render_map(self, output_path: Path, width: int = 1920, height: int = 1080) -> bool:
        """Render the world map to SVG file."""
        return self.renderer.render_map_to_file(output_path, width, height)
