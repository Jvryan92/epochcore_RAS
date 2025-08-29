"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class MapTheme(Enum):
    """Visual themes for different map regions."""
    ROOT_GREEN = "root_green"         # Bottom level, organic
    MYSTIC_PURPLE = "mystic_purple"   # Early seasons, mystical
    NEON_BLUE = "neon_blue"          # Mid seasons, cyberpunk
    VOID_BLACK = "void_black"        # Late seasons, cosmic
    RADIANT_GOLD = "radiant_gold"    # Final season, transcendent


@dataclass
class MapColor:
    """Color definitions with RGB and alpha."""
    r: int
    g: int
    b: int
    a: float = 1.0

    def to_hex(self) -> str:
        """Convert to hex color code."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @staticmethod
    def lerp(color1: 'MapColor', color2: 'MapColor', t: float) -> 'MapColor':
        """Linear interpolation between two colors."""
        return MapColor(
            int(color1.r + (color2.r - color1.r) * t),
            int(color1.g + (color2.g - color1.g) * t),
            int(color1.b + (color2.b - color1.b) * t),
            color1.a + (color2.a - color1.a) * t
        )


@dataclass
class MapNode:
    """Represents a zone node on the map."""
    x: float                    # X coordinate (0-1)
    y: float                    # Y coordinate (0-1)
    radius: float              # Node size
    glow_intensity: float      # Glow effect strength
    icon_path: str            # Path to node icon
    theme: MapTheme           # Visual theme
    connected_to: List[str]   # IDs of connected nodes
    zone_id: str             # Reference to actual zone


@dataclass
class MapConnection:
    """Connection between two map nodes."""
    start_node: str          # Starting node ID
    end_node: str           # Ending node ID
    thickness: float        # Line thickness
    glow_intensity: float   # Glow effect strength
    theme: MapTheme        # Visual theme
    is_root: bool = False  # Whether this is a root-like connection


class WorldMapRenderer:
    """Renders the stylized world map with glowing connections."""

    def __init__(self):
        self.nodes: Dict[str, MapNode] = {}
        self.connections: List[MapConnection] = []
        self.theme_colors = {
            MapTheme.ROOT_GREEN: MapColor(0, 255, 128),      # Bright green
            MapTheme.MYSTIC_PURPLE: MapColor(147, 0, 211),   # Deep purple
            MapTheme.NEON_BLUE: MapColor(0, 195, 255),       # Cyan blue
            MapTheme.VOID_BLACK: MapColor(15, 15, 35),       # Near black
            MapTheme.RADIANT_GOLD: MapColor(255, 215, 0)     # Gold
        }

    def add_node(self, node_id: str, node: MapNode) -> None:
        """Add a node to the map."""
        self.nodes[node_id] = node

    def add_connection(self, connection: MapConnection) -> None:
        """Add a connection between nodes."""
        self.connections.append(connection)

    def calculate_root_path(self, start: MapNode, end: MapNode) -> List[Tuple[float, float]]:
        """Calculate a natural-looking root path between nodes."""
        points = []
        # Start point
        points.append((start.x, start.y))

        # Calculate control points for curve
        dx = end.x - start.x
        dy = end.y - start.y
        dist = math.sqrt(dx * dx + dy * dy)

        # Add some natural variation
        num_segments = max(2, int(dist * 10))
        for i in range(1, num_segments):
            t = i / num_segments
            # Add slight random offset for organic look
            offset_x = math.sin(t * math.pi) * 0.1 * dist
            offset_y = 0

            x = start.x + dx * t + offset_x
            y = start.y + dy * t + offset_y
            points.append((x, y))

        # End point
        points.append((end.x, end.y))
        return points

    def get_node_color(self, node: MapNode, pulse_time: float = 0) -> MapColor:
        """Get the color for a node with optional pulse effect."""
        base_color = self.theme_colors[node.theme]
        if pulse_time > 0:
            # Create pulsing effect
            intensity = (math.sin(pulse_time * 2 * math.pi) + 1) / 2
            glow = MapColor(255, 255, 255, intensity * 0.5)
            return MapColor.lerp(base_color, glow, node.glow_intensity)
        return base_color

    def render_map_to_svg(self, width: int, height: int) -> str:
        """Render the world map to SVG format."""
        svg_elements = []

        # SVG header
        svg_elements.append(
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">')

        # Add gradient definitions
        svg_elements.append('<defs>')
        for theme in MapTheme:
            color = self.theme_colors[theme]
            svg_elements.append(f'''
                <radialGradient id="glow_{theme.value}">
                    <stop offset="0%" stop-color="#{color.to_hex()}" stop-opacity="0.8"/>
                    <stop offset="100%" stop-color="#{color.to_hex()}" stop-opacity="0"/>
                </radialGradient>
            ''')
        svg_elements.append('</defs>')

        # Render connections first (background)
        for conn in self.connections:
            start = self.nodes[conn.start_node]
            end = self.nodes[conn.end_node]

            if conn.is_root:
                # Generate organic path for roots
                path_points = self.calculate_root_path(start, end)
                path_d = f"M {path_points[0][0]*width} {path_points[0][1]*height}"
                for x, y in path_points[1:]:
                    path_d += f" L {x*width} {y*height}"

                svg_elements.append(f'''
                    <path d="{path_d}"
                          stroke="#{self.theme_colors[conn.theme].to_hex()}"
                          stroke-width="{conn.thickness*width/100}"
                          fill="none"
                          opacity="{conn.glow_intensity}">
                        <animate attributeName="stroke-opacity"
                                values="0.4;0.8;0.4"
                                dur="3s"
                                repeatCount="indefinite"/>
                    </path>
                ''')
            else:
                # Direct connection for upper zones
                svg_elements.append(f'''
                    <line x1="{start.x*width}"
                          y1="{start.y*height}"
                          x2="{end.x*width}"
                          y2="{end.y*height}"
                          stroke="#{self.theme_colors[conn.theme].to_hex()}"
                          stroke-width="{conn.thickness*width/100}"
                          opacity="{conn.glow_intensity}"/>
                ''')

        # Render nodes
        for node_id, node in self.nodes.items():
            color = self.get_node_color(node)

            # Node glow
            svg_elements.append(f'''
                <circle cx="{node.x*width}"
                        cy="{node.y*height}"
                        r="{node.radius*width/50}"
                        fill="url(#glow_{node.theme.value})"
                        opacity="{node.glow_intensity}">
                    <animate attributeName="r"
                            values="{node.radius*width/50};{node.radius*width/40};{node.radius*width/50}"
                            dur="4s"
                            repeatCount="indefinite"/>
                </circle>
            ''')

            # Node core
            svg_elements.append(f'''
                <circle cx="{node.x*width}"
                        cy="{node.y*height}"
                        r="{node.radius*width/100}"
                        fill="#{color.to_hex()}"
                        stroke="white"
                        stroke-width="1"/>
            ''')

            # Node icon (if specified)
            if node.icon_path:
                svg_elements.append(f'''
                    <image x="{(node.x*width)-(node.radius*width/150)}"
                           y="{(node.y*height)-(node.radius*width/150)}"
                           width="{node.radius*width/75}"
                           height="{node.radius*width/75}"
                           href="{node.icon_path}"/>
                ''')

        svg_elements.append('</svg>')
        return '\n'.join(svg_elements)

    def render_map_to_file(self, filepath: str, width: int, height: int) -> bool:
        """Save the rendered map to an SVG file."""
        try:
            svg_content = self.render_map_to_svg(width, height)
            with open(filepath, 'w') as f:
                f.write(svg_content)
            return True
        except Exception:
            return False
