"""
EpochCore Game Integration System
Manages game instances and agent interactions
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union

import numpy as np


@dataclass
class GameInstance:
    game_id: str
    mode: str  # 'agent' or 'player'
    difficulty: float  # 0.0 to 1.0
    state: Dict
    mesh_enhanced: bool = True


@dataclass
class GameResult:
    game_id: str
    score: float
    moves: List[str]
    efficiency: float
    mesh_factor: float
    time_ms: int


class GameLibrary:
    def __init__(self):
        self.games = {
            # Classic Games - Agent Training
            "chess": {
                "modes": ["vs_agent", "agent_vs_agent", "analysis"],
                "difficulty_range": (800, 2800),  # ELO
                "mesh_compatible": True
            },
            "go": {
                "modes": ["vs_agent", "agent_vs_agent", "analysis"],
                "difficulty_range": (5, 19),  # board size as difficulty
                "mesh_compatible": True
            },

            # Puzzle Games - Logic Training
            "sokoban": {
                "modes": ["solve", "generate", "analyze"],
                "difficulty_range": (1, 10),
                "mesh_compatible": True
            },
            "maze_solver": {
                "modes": ["pathfind", "generate", "optimize"],
                "difficulty_range": (1, 100),  # size/complexity
                "mesh_compatible": True
            },

            # Platformer Games - Kids Edition
            "tarzan_lite": {
                "modes": ["play", "ghost_record", "assist"],
                "difficulty_range": (1, 5),  # vine complexity
                "mesh_compatible": True,
                "kid_safe": True
            },
            "puzzle_adventure": {
                "modes": ["play", "create", "share"],
                "difficulty_range": (1, 10),
                "mesh_compatible": True,
                "kid_safe": True
            },

            # Strategy Games
            "resource_manager": {
                "modes": ["optimize", "compete", "analyze"],
                "difficulty_range": (1, 10),
                "mesh_compatible": True
            },
            "mesh_tactics": {
                "modes": ["plan", "execute", "review"],
                "difficulty_range": (1, 15),
                "mesh_compatible": True
            },

            # Network Games
            "packet_racer": {
                "modes": ["route", "optimize", "secure"],
                "difficulty_range": (1, 20),
                "mesh_compatible": True
            },
            "consensus_builder": {
                "modes": ["propose", "validate", "finalize"],
                "difficulty_range": (1, 10),
                "mesh_compatible": True
            }
        }

        self.current_games: Dict[str, GameInstance] = {}
        self.results_history: List[GameResult] = []

    def create_game(self,
                    game_type: str,
                    mode: str = "vs_agent",
                    difficulty: float = 0.5,
                    mesh_enhanced: bool = True) -> GameInstance:
        """Create a new game instance"""
        if game_type not in self.games:
            raise ValueError(f"Unknown game type: {game_type}")

        game_config = self.games[game_type]
        if mode not in game_config["modes"]:
            raise ValueError(f"Invalid mode {mode} for game {game_type}")

        # Scale difficulty to game's range
        diff_range = game_config["difficulty_range"]
        scaled_diff = diff_range[0] + (diff_range[1] - diff_range[0]) * difficulty

        game_id = f"{game_type}_{len(self.current_games)}"
        instance = GameInstance(
            game_id=game_id,
            mode=mode,
            difficulty=scaled_diff,
            state={"status": "initialized"},
            mesh_enhanced=mesh_enhanced and game_config["mesh_compatible"]
        )

        self.current_games[game_id] = instance
        return instance

    def get_game(self, game_id: str) -> Optional[GameInstance]:
        """Get an existing game instance"""
        return self.current_games.get(game_id)

    def list_active_games(self, game_type: Optional[str] = None) -> List[GameInstance]:
        """List all active game instances, optionally filtered by type"""
        if game_type:
            return [g for g in self.current_games.values()
                    if g.game_id.startswith(f"{game_type}_")]
        return list(self.current_games.values())

    def end_game(self, game_id: str, result: GameResult):
        """End a game and store its result"""
        if game_id in self.current_games:
            self.results_history.append(result)
            del self.current_games[game_id]

    def get_stats(self, game_type: Optional[str] = None) -> Dict:
        """Get statistics for completed games"""
        results = self.results_history
        if game_type:
            results = [r for r in results if r.game_id.startswith(f"{game_type}_")]

        if not results:
            return {"error": "No completed games found"}

        return {
            "total_games": len(results),
            "avg_score": np.mean([r.score for r in results]),
            "avg_efficiency": np.mean([r.efficiency for r in results]),
            "avg_mesh_factor": np.mean([r.mesh_factor for r in results]),
            "avg_time_ms": np.mean([r.time_ms for r in results])
        }


class GameController:
    def __init__(self):
        self.library = GameLibrary()
        self.logger = logging.getLogger("GameController")

    async def run_agent_game(self,
                             game_type: str,
                             mode: str = "vs_agent",
                             difficulty: float = 0.5,
                             mesh_enhanced: bool = True) -> GameResult:
        """Run a game with an agent"""
        # Create new game instance
        instance = self.library.create_game(
            game_type=game_type,
            mode=mode,
            difficulty=difficulty,
            mesh_enhanced=mesh_enhanced
        )

        # Simulate game execution
        moves = []
        score = 0.0
        efficiency = 0.0
        mesh_factor = 0.0
        time_ms = 0

        try:
            # Run game loop
            start_time = asyncio.get_event_loop().time()

            # Simulate game progression
            game_steps = int(10 + difficulty * 20)
            for step in range(game_steps):
                # Update game state
                await asyncio.sleep(0.1)  # Simulate processing time
                moves.append(f"move_{step}")
                score += np.random.random() * 10

            end_time = asyncio.get_event_loop().time()
            time_ms = int((end_time - start_time) * 1000)

            # Calculate metrics
            efficiency = score / time_ms
            mesh_factor = efficiency * (1.5 if mesh_enhanced else 1.0)

        except Exception as e:
            self.logger.error(f"Game error: {e}")
            raise

        # Create and store result
        result = GameResult(
            game_id=instance.game_id,
            score=score,
            moves=moves,
            efficiency=efficiency,
            mesh_factor=mesh_factor,
            time_ms=time_ms
        )

        self.library.end_game(instance.game_id, result)
        return result

    async def run_training_session(self,
                                   game_type: str,
                                   num_games: int = 10,
                                   increasing_difficulty: bool = True) -> List[GameResult]:
        """Run a series of training games"""
        results = []
        base_difficulty = 0.3

        for i in range(num_games):
            if increasing_difficulty:
                difficulty = min(1.0, base_difficulty + (i * 0.1))
            else:
                difficulty = base_difficulty

            result = await self.run_agent_game(
                game_type=game_type,
                difficulty=difficulty,
                mesh_enhanced=True
            )
            results.append(result)

        return results

    def get_game_recommendations(self,
                                 skill_level: float = 0.5,
                                 kid_safe: bool = False) -> List[str]:
        """Get game recommendations based on skill level"""
        recommendations = []

        for game_type, config in self.library.games.items():
            if kid_safe and not config.get("kid_safe", False):
                continue

            # Calculate game suitability
            diff_range = config["difficulty_range"]
            mid_diff = (diff_range[0] + diff_range[1]) / 2
            normalized_diff = (
                mid_diff - diff_range[0]) / (diff_range[1] - diff_range[0])

            if abs(normalized_diff - skill_level) < 0.3:  # Within skill range
                recommendations.append(game_type)

        return sorted(recommendations)

    def get_learning_path(self,
                          start_game: str,
                          target_skill: float = 0.8,
                          kid_safe: bool = False) -> List[Dict]:
        """Generate a learning path from one game to reach a target skill"""
        if start_game not in self.library.games:
            raise ValueError(f"Unknown starting game: {start_game}")

        path = []
        current_skill = 0.3  # Starting skill assumption

        while current_skill < target_skill:
            next_games = self.get_game_recommendations(
                skill_level=current_skill + 0.2,
                kid_safe=kid_safe
            )

            if not next_games:
                break

            next_game = next_games[0]
            path.append({
                "game": next_game,
                "target_skill": current_skill + 0.2,
                "estimated_games": int(10 + (current_skill * 20))
            })

            current_skill += 0.2

        return path
