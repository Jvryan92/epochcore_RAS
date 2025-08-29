"""
Enhanced Game Controller with Mesh Integration
"""

import asyncio
from typing import Dict, List

from game_integration import GameController, GameResult
from game_library_config import (
    ACHIEVEMENTS,
    AGENT_TRAINING,
    GAME_LIBRARY,
    LEARNING_PATHS,
    MESH_FACTORS,
)
from game_streaming import GameStreamManager


class EnhancedGameController(GameController):
    def __init__(self):
        super().__init__()
        self.achievements = set()
        self.learning_progress = {}
        self.current_path = None
        self.stream_manager = GameStreamManager()
        self._active_stream = None

    async def start_learning_path(self, path_type: str = "beginner"):
        """Start a structured learning path"""
        if path_type not in LEARNING_PATHS:
            raise ValueError(f"Unknown path type: {path_type}")

        self.current_path = path_type
        self.learning_progress[path_type] = {
            "completed_games": [],
            "current_category": None,
            "start_time": asyncio.get_event_loop().time()
        }

        # Start first category
        await self._advance_category(path_type)

    async def _advance_category(self, path_type: str):
        """Move to next category in learning path"""
        progress = self.learning_progress[path_type]
        path = LEARNING_PATHS[path_type]

        # Find next uncompleted category
        current_idx = 0
        if progress["current_category"]:
            current_idx = next(
                i for i, (cat, _) in enumerate(path)
                if cat == progress["current_category"]
            ) + 1

        if current_idx >= len(path):
            await self._complete_path(path_type)
            return

        category, games = path[current_idx]
        progress["current_category"] = category

        # Start first game in category
        await self.start_game(games[0], category)

    async def start_game(self, game_type: str, category: str, agent_id: str):
        """Start a specific game with mesh enhancement and streaming"""
        mesh_factor = MESH_FACTORS.get(category, 1.0)

        # Start game stream
        self._active_stream = await self.stream_manager.start_stream(
            game_type, agent_id
        )

        result = await self.run_agent_game(
            game_type=game_type,
            mesh_enhanced=True,
            difficulty=self._calculate_difficulty()
        )

        # Apply mesh factor
        result.mesh_factor *= mesh_factor

        # Record final state
        await self.stream_manager.end_stream(
            self._active_stream,
            {
                "final_score": result.score,
                "mesh_factor": result.mesh_factor,
                "efficiency": result.efficiency,
                "category": category
            }
        )
        self._active_stream = None

        # Update progress
        if self.current_path:
            progress = self.learning_progress[self.current_path]
            progress["completed_games"].append(game_type)

            # Check for category completion
            category, games = next(
                (cat, g) for cat, g in LEARNING_PATHS[self.current_path]
                if cat == progress["current_category"]
            )

            if all(g in progress["completed_games"] for g in games):
                await self._advance_category(self.current_path)

        await self._check_achievements()
        return result

    async def _complete_path(self, path_type: str):
        """Handle completion of a learning path"""
        end_time = asyncio.get_event_loop().time()
        progress = self.learning_progress[path_type]
        duration = end_time - progress["start_time"]

        # Check for quick learner achievement
        if duration < 3600:  # 1 hour
            self.achievements.add("quick_learner")

        self.current_path = None

    async def _check_achievements(self):
        """Check and award achievements"""
        # Check versatile agent
        categories_mastered = set(
            cat for cat, games in self.learning_progress.items()
            if len(games["completed_games"]) >= 3
        )
        if len(categories_mastered) >= 3:
            self.achievements.add("versatile_agent")

        # Check economy expert
        eco_games = set(
            game for cat, config in GAME_LIBRARY.items()
            for game, details in config.items()
            if details.get("economy_features")
        )
        completed_eco = set(
            game for path in self.learning_progress.values()
            for game in path["completed_games"]
            if game in eco_games
        )
        if len(completed_eco) == len(eco_games):
            self.achievements.add("economy_expert")

    def _calculate_difficulty(self) -> float:
        """Calculate appropriate difficulty based on progress"""
        if not self.current_path:
            return 0.5

        progress = self.learning_progress[self.current_path]
        completed = len(progress["completed_games"])

        return min(1.0, 0.3 + (completed * 0.1))

    def get_achievement_bonus(self) -> float:
        """Calculate total mesh bonus from achievements"""
        return sum(
            ACHIEVEMENTS[ach]["mesh_bonus"]
            for ach in self.achievements
        )

    def get_progress_summary(self) -> Dict:
        """Get summary of learning progress"""
        return {
            "paths_started": list(self.learning_progress.keys()),
            "current_path": self.current_path,
            "achievements": list(self.achievements),
            "total_games_completed": sum(
                len(p["completed_games"])
                for p in self.learning_progress.values()
            ),
            "achievement_bonus": self.get_achievement_bonus()
        }

    async def run_training_sequence(
        self, sequence_type: str, agent_id: str
    ) -> List[GameResult]:
        """Run a predefined training sequence for agents with streaming"""
        if sequence_type not in AGENT_TRAINING:
            raise ValueError(f"Unknown training sequence: {sequence_type}")

        results = []
        for game in AGENT_TRAINING[sequence_type]:
            # Start game stream
            self._active_stream = await self.stream_manager.start_stream(
                game, agent_id
            )

            result = await self.run_agent_game(
                game_type=game,
                mesh_enhanced=True
            )

            # Record game state
            await self.stream_manager.end_stream(
                self._active_stream,
                {
                    "final_score": result.score,
                    "mesh_factor": result.mesh_factor,
                    "efficiency": result.efficiency,
                    "sequence": sequence_type
                }
            )

            results.append(result)
            self._active_stream = None

        return results
