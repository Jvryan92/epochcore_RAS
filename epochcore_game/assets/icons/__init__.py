"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import os
from pathlib import Path

# Base icon paths
ICON_ROOT = Path(__file__).parent

# Map glyph icons
ICONS = {
    'biome': ICON_ROOT / 'biome.svg',
    'urban': ICON_ROOT / 'urban.svg',
    'mythic': ICON_ROOT / 'mythic.svg',
    'cosmic': ICON_ROOT / 'cosmic.svg',
    'shadow': ICON_ROOT / 'shadow.svg',
    'primal': ICON_ROOT / 'primal.svg',
    'underworld': ICON_ROOT / 'underworld.svg',
    'renaissance': ICON_ROOT / 'renaissance.svg',
    'singularity': ICON_ROOT / 'singularity.svg',
    'raid': ICON_ROOT / 'raid.svg',
    'default': ICON_ROOT / 'default.svg'
}

# Ensure all icon paths exist


def validate_icons() -> bool:
    """Validate that all required icons exist."""
    missing = []
    for name, path in ICONS.items():
        if not path.exists():
            missing.append(name)
    return len(missing) == 0


# Icon color themes
ICON_COLORS = {
    'root_green': '#00FF80',    # Bright green
    'mystic_purple': '#9300D3',  # Deep purple
    'neon_blue': '#00C3FF',     # Cyan blue
    'void_black': '#0F0F23',    # Near black
    'radiant_gold': '#FFD700'   # Gold
}

# Icon sizes
ICON_SIZES = {
    'small': 32,
    'medium': 64,
    'large': 128
}
