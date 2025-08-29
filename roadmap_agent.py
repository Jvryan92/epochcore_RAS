"""
EpochCore Roadmap Integration Agent
Combines main game and kids edition with mesh enhancement
"""

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from mesh_enhanced_agent import MeshEnhancedAgent


class RoadmapAgent:
    def __init__(self):
        self.enhanced = MeshEnhancedAgent()
        self.root = Path("/workspaces/epochcore_RAS/epoch_game_pack")
        self.roadmap_dir = self.root / "roadmap"
        self.edu_dir = self.root / "edu_kids"
        self.roadmap_data = None
        self.kids_data = None
        self._load_roadmaps()

    def _load_roadmaps(self):
        """Load both roadmap configurations"""
        try:
            # Main roadmap
            with open(self.roadmap_dir / "roadmap_100.json", "r") as f:
                self.roadmap_data = json.load(f)

            # Kids roadmap
            with open(self.edu_dir / "edu_roadmap_100.json", "r") as f:
                self.kids_data = json.load(f)

            # Initialize mesh network with both
            self._init_mesh_network()

        except FileNotFoundError as e:
            print(f"Error loading roadmaps: {e}")
            raise

    def _init_mesh_network(self):
        """Initialize mesh network with both roadmaps"""
        # Add main roadmap nodes
        for stage in self.roadmap_data["stages"]:
            self.enhanced.mesh_network.add_node(
                f"main_{stage['index']}",
                type="main",
                meshmap=stage["meshmap"],
                creativity=stage["creativity"],
                mesh_factor=stage["mesh_factor"]
            )

        # Add kids roadmap nodes with connections to main
        for stage in self.kids_data["stages"]:
            self.enhanced.mesh_network.add_node(
                f"kids_{stage['index']}",
                type="kids",
                meshmap=stage["meshmap"],
                creativity=stage["creativity"],
                autonomy=stage["autonomy_level"],
                mesh_richness=stage["mesh_richness"]
            )

        # Create strategic connections
        self._build_cross_connections()

    def _build_cross_connections(self):
        """Build connections between main and kids roadmaps"""
        for i in range(1, 101):
            main_node = f"main_{i}"
            kids_node = f"kids_{i}"

            # Connect parallel stages
            self.enhanced.mesh_network.add_edge(
                main_node, kids_node,
                weight=self._calculate_synergy(i)
            )

            # Connect to nearby stages
            for offset in [-1, 1]:
                if 1 <= i + offset <= 100:
                    self.enhanced.mesh_network.add_edge(
                        main_node, f"kids_{i+offset}",
                        weight=self._calculate_synergy(i, i+offset) * 0.8
                    )

    def _calculate_synergy(self, main_idx: int, kids_idx: Optional[int] = None) -> float:
        """Calculate synergy between main and kids roadmap stages"""
        kids_idx = kids_idx or main_idx

        main_stage = next(
            s for s in self.roadmap_data["stages"] if s["index"] == main_idx)
        kids_stage = next(s for s in self.kids_data["stages"] if s["index"] == kids_idx)

        # Calculate synergy based on:
        # - Creativity alignment
        # - Mesh factor compatibility
        # - Architectural resonance
        creativity_sync = abs(main_stage["creativity"] - kids_stage["creativity"])
        mesh_sync = abs(float(main_stage["mesh_factor"]) -
                        float(kids_stage["mesh_richness"]))

        return max(0.1, 1.0 - (creativity_sync + mesh_sync) / 4)

    async def optimize_stage(self, stage_num: int, edition: str = "main"):
        """Optimize a specific stage in either roadmap"""
        node_id = f"{edition}_{stage_num}"

        # Get stage data
        if edition == "main":
            stage = next(
                s for s in self.roadmap_data["stages"] if s["index"] == stage_num)
        else:
            stage = next(s for s in self.kids_data["stages"] if s["index"] == stage_num)

        # Enhance using mesh network
        result = await self.enhanced.enhance_strategy(node_id)

        # Apply optimizations
        optimized = {
            "stage": stage_num,
            "edition": edition,
            "original_creativity": stage["creativity"],
            "enhanced_creativity": result["enhancement_level"],
            "mesh_coherence": result["mesh_coherence"],
            "evolution_score": result["evolution_score"]
        }

        return optimized

    async def analyze_viral_potential(self, stage_num: int):
        """Analyze viral mechanics across both editions"""
        main_stage = next(
            s for s in self.roadmap_data["stages"] if s["index"] == stage_num)
        kids_stage = next(
            s for s in self.kids_data["stages"] if s["index"] == stage_num)

        main_viral = main_stage.get("viral_hooks", [])
        kids_viral = kids_stage.get("viral_hooks", [])

        return {
            "stage": stage_num,
            "main_hooks": main_viral,
            "kids_hooks": kids_viral,
            "synergy_score": len(set(main_viral) & set(kids_viral)) / len(set(main_viral) | set(kids_viral))
        }

    def export_meshmap(self, stage_num: int, edition: str = "main"):
        """Export meshmap visualization for a stage"""
        if edition == "main":
            stage = next(
                s for s in self.roadmap_data["stages"] if s["index"] == stage_num)
        else:
            stage = next(s for s in self.kids_data["stages"] if s["index"] == stage_num)

        mm = stage["meshmap"]

        return {
            "stage": stage_num,
            "edition": edition,
            "archetype": mm["archetype"],
            "nodes": mm["nodes"],
            "edges": mm["edges"],
            "p95_target": mm["p95_target_ms"]
        }

    def get_stage_summary(self, stage_num: int):
        """Get comprehensive summary of both editions for a stage"""
        main = next(s for s in self.roadmap_data["stages"] if s["index"] == stage_num)
        kids = next(s for s in self.kids_data["stages"] if s["index"] == stage_num)

        return {
            "stage": stage_num,
            "main": {
                "theme": main["season_theme"],
                "creativity": main["creativity"],
                "mesh_factor": main["mesh_factor"],
                "multiplayer": main["multiplayer"],
                "viral": main["viral_hooks"]
            },
            "kids": {
                "theme": kids["season_theme"],
                "age_band": kids["age_band"],
                "platform": kids["platform"],
                "creativity": kids["creativity"],
                "mesh_richness": kids["mesh_richness"],
                "viral": kids["viral_hooks"]
            },
            "synergy": self._calculate_synergy(stage_num)
        }
