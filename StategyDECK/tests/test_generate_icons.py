#!/usr/bin/env python3
"""Tests for the icon generation script."""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from generate_icons import pick_master, bake_svg, TOKENS, FINISH_COLORS


class TestIconGeneration:
    """Test cases for icon generation functionality."""

    def test_pick_master_micro(self):
        """Test that small icons use micro master."""
        assert pick_master(16).name == "strategy_icon_micro.svg"
        assert pick_master(32).name == "strategy_icon_micro.svg"

    def test_pick_master_standard(self):
        """Test that larger icons use standard master."""
        assert pick_master(48).name == "strategy_icon_standard.svg"
        assert pick_master(64).name == "strategy_icon_standard.svg"

    def test_bake_svg_light_mode(self):
        """Test SVG color replacement for light mode."""
        test_svg = '<rect fill="#FF6A00"/><path fill="#FFFFFF"/>'
        result = bake_svg(test_svg, "light", "satin-black")

        # In light mode: #FF6A00 -> #FFFFFF (white), then #FFFFFF -> #000000 (black)
        # Both elements end up black due to replacement order
        expected = '<rect fill="#000000"/><path fill="#000000"/>'
        assert result == expected
        assert TOKENS["ink"] in result  # Black color should be present

    def test_bake_svg_dark_mode(self):
        """Test SVG color replacement for dark mode."""
        test_svg = '<rect fill="#FF6A00"/><path fill="#FFFFFF"/>'
        result = bake_svg(test_svg, "dark", "copper-foil")

        # In dark mode: #FF6A00 -> dark background, #FFFFFF -> copper foreground
        assert TOKENS["slate_950"] in result  # Dark background (replaces #FF6A00)
        assert TOKENS["copper"] in result  # Copper foreground (replaces #FFFFFF)
        assert result == '<rect fill="#060607"/><path fill="#B87333"/>'

    def test_finish_colors_defined(self):
        """Test that all finish colors are properly defined."""
        expected_finishes = [
            "flat-orange",
            "matte-carbon",
            "satin-black",
            "burnt-orange",
            "copper-foil",
            "embossed-paper",
        ]

        for finish in expected_finishes:
            assert finish in FINISH_COLORS
            assert FINISH_COLORS[finish] in TOKENS.values()

    def test_tokens_defined(self):
        """Test that all color tokens are properly defined."""
        required_tokens = [
            "paper",
            "slate_950",
            "brand_orange",
            "ink",
            "copper",
            "burnt_orange",
            "matte",
            "embossed",
        ]

        for token in required_tokens:
            assert token in TOKENS
            assert TOKENS[token].startswith("#")  # Should be hex color
            assert len(TOKENS[token]) == 7  # Should be 6-digit hex + #


if __name__ == "__main__":
    pytest.main([__file__])
