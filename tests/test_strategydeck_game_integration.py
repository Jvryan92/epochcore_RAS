#!/usr/bin/env python3
"""
Integration Test for StrategyDECK Icon System with Game Assets

This script tests the integration between the StrategyDECK icon generation system
and the game assets connector, ensuring that icons are properly synced to
game and SaaS targets.
"""

import os
import sys
import json
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import modules to test
from strategydeck_game_assets_connector import GameAssetsConnector


class TestStrategyDeckGameIntegration(unittest.TestCase):
    """Test integration between StrategyDECK and game assets"""
    
    def setUp(self):
        """Set up test environment"""
        self.root_dir = Path(__file__).resolve().parent.parent
        self.assets_dir = self.root_dir / "assets"
        self.icons_dir = self.assets_dir / "icons"
        self.dist_dir = self.root_dir / "dist"
        self.game_assets_dir = self.dist_dir / "game-assets"
        
        # Ensure directories exist
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        self.game_assets_dir.mkdir(parents=True, exist_ok=True)
        
        # Create connector
        self.connector = GameAssetsConnector()
    
    def test_icon_generation(self):
        """Test that icons are generated"""
        # Check that we have at least some SVG files
        svg_files = list(self.icons_dir.glob("**/*.svg"))
        self.assertGreater(len(svg_files), 0, "No SVG icons were generated")
    
    def test_sync_targets(self):
        """Test that sync targets are defined"""
        # Check that we have sync targets
        self.assertGreater(
            len(self.connector.config["sync_targets"]), 
            0, 
            "No sync targets defined"
        )
    
    def test_sync_process(self):
        """Test the sync process"""
        # Run the sync
        result = self.connector.sync_icons()
        
        # Check that sync was successful
        self.assertTrue(result["success"], f"Sync failed: {result.get('error', 'Unknown error')}")
        
        # Check that files were synced
        self.assertGreater(result["synced_files"], 0, "No files were synced")
    
    def test_shared_storage(self):
        """Test shared storage update"""
        # Update shared storage
        result = self.connector.update_shared_storage()
        
        # Check that update was successful
        self.assertTrue(result, "Failed to update shared storage")
        
        # Check that shared directory contains files
        shared_path = Path(self.connector.config["shared_storage"]["path"])
        files = list(shared_path.glob("**/*.*"))
        self.assertGreater(len(files), 0, "No files in shared storage")
    
    def test_game_context_icons(self):
        """Test that game context icons are generated and synced"""
        # Find game context icons
        game_icons = list(self.icons_dir.glob("**/game/*.svg"))
        self.assertGreater(
            len(game_icons), 
            0, 
            "No game context icons were generated"
        )
        
        # Check they were synced to game assets
        unity_path = self.game_assets_dir / "unity"
        if unity_path.exists():
            unity_icons = list(unity_path.glob("**/*.*"))
            self.assertGreater(
                len(unity_icons), 
                0, 
                "No icons were synced to Unity game target"
            )
    
    def test_saas_context_icons(self):
        """Test that SaaS context icons are generated and synced"""
        # Find SaaS context icons
        saas_icons = list(self.icons_dir.glob("**/saas/*.svg"))
        self.assertGreater(
            len(saas_icons), 
            0, 
            "No SaaS context icons were generated"
        )
        
        # Check they were synced to SaaS assets
        saas_path = self.game_assets_dir / "saas"
        if saas_path.exists():
            saas_icons = list(saas_path.glob("**/*.*"))
            self.assertGreater(
                len(saas_icons), 
                0, 
                "No icons were synced to SaaS platform target"
            )


if __name__ == "__main__":
    # Run tests
    unittest.main()
