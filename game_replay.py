"""
Game Replay and Analysis System
"""

import asyncio
import json
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import AsyncGenerator, Dict, List


@dataclass
class GameReplay:
    game_id: str
    agent_id: str
    timestamp: str
    frames: List[Dict]
    final_state: Dict
    metrics: Dict[str, List[float]]


class ReplayManager:
    def __init__(self, base_path: str = "data/game_streams"):
        self.base_path = Path(base_path)

    async def load_replay(self, replay_path: Path) -> GameReplay:
        """Load a game replay from a stream file"""
        frames = []
        metrics = {}
        final_state = None

        # Parse game ID and agent from filename
        parts = replay_path.stem.split("_")
        game_id = parts[0]
        agent_id = parts[1]
        timestamp = parts[2]

        async with open(replay_path) as f:
            async for line in f:
                frame = json.loads(line)
                if frame["type"] == "end":
                    final_state = frame["state"]
                else:
                    frames.append(frame)
                    # Collect metrics
                    for k, v in frame["metrics"].items():
                        if isinstance(v, (int, float)):
                            metrics.setdefault(k, []).append(float(v))

        return GameReplay(
            game_id=game_id,
            agent_id=agent_id,
            timestamp=timestamp,
            frames=frames,
            final_state=final_state,
            metrics=metrics
        )

    async def get_agent_performance(self, agent_id: str, days: int = 7) -> Dict:
        """Analyze agent performance over time"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        performances = []

        # Gather all relevant replays
        for date_dir in self.base_path.iterdir():
            if not date_dir.is_dir():
                continue
            date = datetime.strptime(date_dir.name, "%Y-%m-%d")
            if date < cutoff:
                continue

            for replay_file in date_dir.glob(f"*_{agent_id}_*.jsonl"):
                replay = await self.load_replay(replay_file)
                if replay.final_state:
                    performances.append({
                        "game_id": replay.game_id,
                        "timestamp": replay.timestamp,
                        "score": replay.final_state.get("final_score", 0),
                        "efficiency": replay.final_state.get("efficiency", 0),
                        "mesh_factor": replay.final_state.get("mesh_factor", 1.0)
                    })

        # Calculate statistics
        if performances:
            scores = [p["score"] for p in performances]
            efficiencies = [p["efficiency"] for p in performances]
            mesh_factors = [p["mesh_factor"] for p in performances]

            return {
                "agent_id": agent_id,
                "games_played": len(performances),
                "date_range": f"{cutoff.date()} to {datetime.utcnow().date()}",
                "score_stats": {
                    "mean": statistics.mean(scores),
                    "median": statistics.median(scores),
                    "max": max(scores)
                },
                "efficiency_stats": {
                    "mean": statistics.mean(efficiencies),
                    "median": statistics.median(efficiencies)
                },
                "mesh_stats": {
                    "mean": statistics.mean(mesh_factors),
                    "total": sum(mesh_factors)
                },
                "performances": performances
            }
        return {"agent_id": agent_id, "games_played": 0}

    async def replay_game(self, replay_path: Path) -> AsyncGenerator[Dict, None]:
        """Replay a game frame by frame"""
        async with open(replay_path) as f:
            async for line in f:
                frame = json.loads(line)
                if frame["type"] != "end":
                    yield frame
                    # Simulate original frame timing
                    await asyncio.sleep(0.1)  # 10 FPS replay

    async def analyze_game_patterns(self, replay_path: Path) -> Dict:
        """Analyze patterns and interesting moments in a game"""
        replay = await self.load_replay(replay_path)
        patterns = {
            "efficiency_spikes": [],
            "score_plateaus": [],
            "interesting_sequences": []
        }

        # Analyze efficiency changes
        if "efficiency" in replay.metrics:
            efficiencies = replay.metrics["efficiency"]
            mean_eff = statistics.mean(efficiencies)
            std_eff = statistics.stdev(efficiencies) if len(efficiencies) > 1 else 0

            # Find significant spikes
            for i, eff in enumerate(efficiencies):
                if eff > mean_eff + 2 * std_eff:
                    patterns["efficiency_spikes"].append({
                        "frame": i,
                        "value": eff,
                        "deviation": (eff - mean_eff) / std_eff
                    })

        # Analyze score progression
        if "score" in replay.metrics:
            scores = replay.metrics["score"]
            windows = zip(scores[:-10], scores[10:])  # 10-frame windows

            # Find score plateaus
            for i, (start, end) in enumerate(windows):
                if abs(end - start) < 0.01 * start:  # < 1% change
                    patterns["score_plateaus"].append({
                        "start_frame": i,
                        "end_frame": i + 10,
                        "score": start
                    })

        return {
            "game_id": replay.game_id,
            "agent_id": replay.agent_id,
            "timestamp": replay.timestamp,
            "patterns": patterns,
            "summary": {
                "efficiency_spike_count": len(patterns["efficiency_spikes"]),
                "plateau_count": len(patterns["score_plateaus"])
            }
        }

    async def export_highlights(self, replay_path: Path) -> Dict:
        """Export interesting moments from a game"""
        replay = await self.load_replay(replay_path)
        patterns = await self.analyze_game_patterns(replay_path)

        highlights = []
        # Get frames around interesting moments
        for spike in patterns["patterns"]["efficiency_spikes"]:
            frame_idx = spike["frame"]
            # Get 5 frames before and after the spike
            start = max(0, frame_idx - 5)
            end = min(len(replay.frames), frame_idx + 6)
            highlights.append({
                "type": "efficiency_spike",
                "frames": replay.frames[start:end],
                "peak_value": spike["value"]
            })

        return {
            "game_id": replay.game_id,
            "agent_id": replay.agent_id,
            "timestamp": replay.timestamp,
            "highlights": highlights
        }
