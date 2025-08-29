"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""
EPOCHCORE Chess Tournament System
24/7 Live Agent Chess Tournament with Mesh Network Integration
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ChessTournamentManager:
    """Manages the 24/7 live chess tournament between mesh agents."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.tournament_dir = Path("ledger/chess_tournament")
        self.tournament_dir.mkdir(parents=True, exist_ok=True)
        self.current_matches: Dict[str, Dict] = {}
        self.leaderboard: Dict[str, Dict] = {}
        self.stream_url = self.config.get(
            "stream_url", "https://github.com/Jvryan92/epochcore_RAS/live")

    async def initialize_tournament(self):
        """Initialize the 24/7 tournament system."""
        self.logger.info("Initializing EPOCHCORE Chess Tournament")
        await self._load_state()
        await self._setup_streaming()

    async def _load_state(self):
        """Load tournament state from ledger."""
        state_file = self.tournament_dir / "tournament_state.json"
        if state_file.exists():
            state = json.loads(state_file.read_text())
            self.leaderboard = state.get("leaderboard", {})
            self.current_matches = state.get("current_matches", {})

    async def _setup_streaming(self):
        """Setup live streaming of matches."""
        # Configure streaming endpoint (GitHub/custom platform)
        stream_config = {
            "platform": "github_live",
            "repo": "epochcore_RAS",
            "owner": "Jvryan92",
            "tournament_name": "EPOCHCORE 24/7 Agent Chess Tournament",
            "start_time": datetime.now().isoformat()
        }
        await self._save_stream_config(stream_config)

    async def start_match(self, agent1_id: str, agent2_id: str) -> str:
        """Start a new chess match between two agents."""
        match_id = f"match_{int(time.time())}_{agent1_id}_{agent2_id}"

        match_data = {
            "match_id": match_id,
            "white": agent1_id,
            "black": agent2_id,
            "start_time": datetime.now().isoformat(),
            "moves": [],
            "status": "active"
        }

        self.current_matches[match_id] = match_data
        await self._save_state()
        await self._update_stream(match_id)

        return match_id

    async def record_move(self, match_id: str, agent_id: str, move: str):
        """Record a chess move and update the stream."""
        if match_id not in self.current_matches:
            raise ValueError(f"Match {match_id} not found")

        match = self.current_matches[match_id]
        move_data = {
            "agent": agent_id,
            "move": move,
            "timestamp": datetime.now().isoformat()
        }

        match["moves"].append(move_data)
        await self._save_state()
        await self._update_stream(match_id)

    async def end_match(self, match_id: str, winner_id: str):
        """End a match and update leaderboard."""
        if match_id not in self.current_matches:
            raise ValueError(f"Match {match_id} not found")

        match = self.current_matches[match_id]
        match["status"] = "completed"
        match["winner"] = winner_id
        match["end_time"] = datetime.now().isoformat()

        # Update leaderboard
        if winner_id not in self.leaderboard:
            self.leaderboard[winner_id] = {"wins": 0, "matches": 0, "rating": 1200}

        self.leaderboard[winner_id]["wins"] += 1
        self.leaderboard[winner_id]["matches"] += 1

        # Update loser's record
        loser_id = match["white"] if winner_id == match["black"] else match["black"]
        if loser_id not in self.leaderboard:
            self.leaderboard[loser_id] = {"wins": 0, "matches": 0, "rating": 1200}

        self.leaderboard[loser_id]["matches"] += 1

        # Update ELO ratings
        await self._update_ratings(winner_id, loser_id)
        await self._save_state()
        await self._update_stream(match_id)

    async def _update_ratings(self, winner_id: str, loser_id: str):
        """Update ELO ratings after a match."""
        K = 32  # Rating adjustment factor

        winner_rating = self.leaderboard[winner_id]["rating"]
        loser_rating = self.leaderboard[loser_id]["rating"]

        # Calculate expected scores
        expected_winner = 1 / (1 + 10**((loser_rating - winner_rating) / 400))
        expected_loser = 1 - expected_winner

        # Update ratings
        self.leaderboard[winner_id]["rating"] += K * (1 - expected_winner)
        self.leaderboard[loser_id]["rating"] += K * (0 - expected_loser)

    async def _save_state(self):
        """Save tournament state to ledger."""
        state = {
            "leaderboard": self.leaderboard,
            "current_matches": self.current_matches,
            "last_updated": datetime.now().isoformat()
        }

        state_file = self.tournament_dir / "tournament_state.json"
        state_file.write_text(json.dumps(state, indent=2))

    async def _save_stream_config(self, config: Dict):
        """Save streaming configuration."""
        config_file = self.tournament_dir / "stream_config.json"
        config_file.write_text(json.dumps(config, indent=2))

    async def _update_stream(self, match_id: str):
        """Update live stream with latest match state."""
        match = self.current_matches[match_id]
        stream_update = {
            "match_id": match_id,
            "timestamp": datetime.now().isoformat(),
            "match_data": match,
            "leaderboard": self.leaderboard
        }

        # Save stream update to ledger
        updates_dir = self.tournament_dir / "stream_updates"
        updates_dir.mkdir(exist_ok=True)
        update_file = updates_dir / f"update_{int(time.time())}.json"
        update_file.write_text(json.dumps(stream_update, indent=2))

    def get_tournament_stats(self) -> Dict:
        """Get current tournament statistics."""
        return {
            "total_matches": len(self.current_matches),
            "active_matches": len([m for m in self.current_matches.values() if m["status"] == "active"]),
            "total_players": len(self.leaderboard),
            "top_players": sorted(
                self.leaderboard.items(),
                key=lambda x: x[1]["rating"],
                reverse=True
            )[:10],
            "stream_url": self.stream_url
        }

    async def run_tournament_cycle(self):
        """Run a continuous tournament cycle."""
        while True:
            try:
                # Match active agents
                active_agents = list(self.leaderboard.keys())
                if len(active_agents) >= 2:
                    # Pair agents by rating
                    sorted_agents = sorted(
                        active_agents,
                        key=lambda x: self.leaderboard[x]["rating"]
                    )

                    for i in range(0, len(sorted_agents) - 1, 2):
                        agent1, agent2 = sorted_agents[i:i+2]
                        await self.start_match(agent1, agent2)

                await asyncio.sleep(300)  # Check for new matches every 5 minutes

            except Exception as e:
                self.logger.error(f"Tournament cycle error: {str(e)}")
                await asyncio.sleep(60)  # Wait before retry
