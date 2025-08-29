"""
Game Streaming and Recording System for Agent Arcade
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class GameStream:
    game_id: str
    agent_id: str
    timestamp: str
    type: str
    metrics: Dict
    state: Dict
    frame: int


class GameStreamManager:
    def __init__(self, base_path: str = "data/game_streams"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.active_streams: Dict[str, asyncio.Queue] = {}
        self.logger = logging.getLogger("GameStream")

    def get_stream_path(self, game_id: str, agent_id: str, timestamp: str) -> Path:
        """Generate path for stream recording"""
        date = timestamp.split("T")[0]
        filename = f"{game_id}_{agent_id}_{timestamp.replace(':','-')}.jsonl"
        return self.base_path / date / filename

    async def start_stream(self, game_id: str, agent_id: str) -> str:
        """Start a new game stream"""
        timestamp = datetime.utcnow().isoformat()
        stream_id = f"{game_id}_{agent_id}_{timestamp}"

        # Create queue for real-time streaming
        self.active_streams[stream_id] = asyncio.Queue()

        # Ensure directory exists
        stream_path = self.get_stream_path(game_id, agent_id, timestamp)
        stream_path.parent.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Started stream {stream_id}")
        return stream_id

    async def record_frame(
        self,
        stream_id: str,
        metrics: Dict,
        state: Dict,
        frame: int
    ):
        """Record a frame of game data"""
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not found")

        game_id, agent_id, timestamp = stream_id.split("_", 2)

        stream = GameStream(
            game_id=game_id,
            agent_id=agent_id,
            timestamp=timestamp,
            type="frame",
            metrics=metrics,
            state=state,
            frame=frame
        )

        # Add to real-time queue
        await self.active_streams[stream_id].put(stream)

        # Write to file
        stream_path = self.get_stream_path(game_id, agent_id, timestamp)
        with open(stream_path, "a") as f:
            f.write(json.dumps(asdict(stream)) + "\n")

    async def end_stream(self, stream_id: str, final_state: Dict):
        """End a game stream"""
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not found")

        game_id, agent_id, timestamp = stream_id.split("_", 2)

        # Record final state
        stream = GameStream(
            game_id=game_id,
            agent_id=agent_id,
            timestamp=timestamp,
            type="end",
            metrics={},
            state=final_state,
            frame=-1
        )

        # Write final state
        stream_path = self.get_stream_path(game_id, agent_id, timestamp)
        with open(stream_path, "a") as f:
            f.write(json.dumps(asdict(stream)) + "\n")

        # Close queue
        queue = self.active_streams.pop(stream_id)
        await queue.put(None)  # Signal end of stream

    async def get_stream(self, stream_id: str) -> asyncio.Queue:
        """Get queue for real-time streaming"""
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not found")
        return self.active_streams[stream_id]

    def get_daily_streams(self, date: str) -> List[Path]:
        """Get all streams for a given date"""
        date_path = self.base_path / date
        if not date_path.exists():
            return []
        return list(date_path.glob("*.jsonl"))

    def get_agent_streams(self, agent_id: str, date: str) -> List[Path]:
        """Get all streams for an agent on a given date"""
        return [p for p in self.get_daily_streams(date) if f"_{agent_id}_" in p.name]

    def get_game_streams(self, game_id: str, date: str) -> List[Path]:
        """Get all streams for a game on a given date"""
        streams = self.get_daily_streams(date)
        return [p for p in streams if p.name.startswith(f"{game_id}_")]
