"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

"""
EPOCHCORE Math Olympics - Multi-Agent Competition System
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set


class OlympicEvent(Enum):
    PATTERN_RECOGNITION = "pattern_recognition"
    STRATEGIC_PLANNING = "strategic_planning"
    CRYPTOGRAPHY = "cryptography"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    COORDINATION = "coordination"
    NETWORK_TOPOLOGY = "network_topology"
    MARKET_SIMULATION = "market_simulation"
    PROCESS_OPTIMIZATION = "process_optimization"


class MathOlympicsManager:
    """Manages the EPOCHCORE Math Olympics competition between mesh agents."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.olympics_dir = Path("ledger/math_olympics")
        self.olympics_dir.mkdir(parents=True, exist_ok=True)

        # Track active competitions and medals
        self.active_events: Dict[str, Dict] = {}
        self.medals: Dict[str, Dict[str, int]] = {}
        self.stream_url = self.config.get(
            "stream_url", "https://github.com/Jvryan92/epochcore_RAS/olympics")

    async def initialize_olympics(self):
        """Initialize the Math Olympics system."""
        self.logger.info("Initializing EPOCHCORE Math Olympics")
        await self._load_state()
        await self._setup_streaming()

    async def _load_state(self):
        """Load Olympics state from ledger."""
        state_file = self.olympics_dir / "olympics_state.json"
        if state_file.exists():
            state = json.loads(state_file.read_text())
            self.medals = state.get("medals", {})
            self.active_events = state.get("active_events", {})

    async def _setup_streaming(self):
        """Setup live streaming of Olympic events."""
        stream_config = {
            "platform": "github_live",
            "repo": "epochcore_RAS",
            "owner": "Jvryan92",
            "event_name": "EPOCHCORE Math Olympics 2025",
            "start_time": datetime.now().isoformat()
        }
        await self._save_stream_config(stream_config)

    async def start_event(self, event: OlympicEvent, participants: List[str]) -> str:
        """Start a new Olympic event."""
        event_id = f"event_{int(time.time())}_{event.value}"

        event_data = {
            "event_id": event_id,
            "event_type": event.value,
            "participants": participants,
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "rounds": [],
            "scores": {p: 0 for p in participants}
        }

        self.active_events[event_id] = event_data
        await self._save_state()
        await self._update_stream(event_id)

        return event_id

    async def record_score(self, event_id: str, agent_id: str, score: float):
        """Record an agent's score in an event."""
        if event_id not in self.active_events:
            raise ValueError(f"Event {event_id} not found")

        event = self.active_events[event_id]
        if agent_id not in event["participants"]:
            raise ValueError(f"Agent {agent_id} not a participant in event {event_id}")

        event["scores"][agent_id] = score
        await self._save_state()
        await self._update_stream(event_id)

    async def end_event(self, event_id: str):
        """End an Olympic event and award medals."""
        if event_id not in self.active_events:
            raise ValueError(f"Event {event_id} not found")

        event = self.active_events[event_id]
        event["status"] = "completed"
        event["end_time"] = datetime.now().isoformat()

        # Sort participants by score
        sorted_scores = sorted(
            event["scores"].items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Award medals
        medals = [("gold", 3), ("silver", 2), ("bronze", 1)]
        for i, (agent_id, _) in enumerate(sorted_scores[:3]):
            if agent_id not in self.medals:
                self.medals[agent_id] = {"gold": 0, "silver": 0, "bronze": 0}

            medal, points = medals[i]
            self.medals[agent_id][medal] += 1
            event["scores"][agent_id] = points

        await self._save_state()
        await self._update_stream(event_id)

    async def _save_state(self):
        """Save Olympics state to ledger."""
        state = {
            "medals": self.medals,
            "active_events": self.active_events,
            "last_updated": datetime.now().isoformat()
        }

        state_file = self.olympics_dir / "olympics_state.json"
        state_file.write_text(json.dumps(state, indent=2))

    async def _save_stream_config(self, config: Dict):
        """Save streaming configuration."""
        config_file = self.olympics_dir / "stream_config.json"
        config_file.write_text(json.dumps(config, indent=2))

    async def _update_stream(self, event_id: str):
        """Update live stream with latest event state."""
        event = self.active_events[event_id]
        stream_update = {
            "event_id": event_id,
            "timestamp": datetime.now().isoformat(),
            "event_data": event,
            "medal_table": self.medals
        }

        # Save stream update to ledger
        updates_dir = self.olympics_dir / "stream_updates"
        updates_dir.mkdir(exist_ok=True)
        update_file = updates_dir / f"update_{int(time.time())}.json"
        update_file.write_text(json.dumps(stream_update, indent=2))

    def get_olympics_stats(self) -> Dict:
        """Get current Olympics statistics."""
        return {
            "total_events": len(self.active_events),
            "active_events": len([e for e in self.active_events.values() if e["status"] == "active"]),
            "total_participants": len(set(a for e in self.active_events.values() for a in e["participants"])),
            "medal_table": sorted(
                self.medals.items(),
                key=lambda x: (x[1]["gold"], x[1]["silver"], x[1]["bronze"]),
                reverse=True
            ),
            "stream_url": self.stream_url
        }

    async def run_olympics_cycle(self):
        """Run a continuous Olympics cycle."""
        events = list(OlympicEvent)
        while True:
            try:
                # Start new events if none are active
                active_count = len(
                    [e for e in self.active_events.values() if e["status"] == "active"])

                if active_count < len(events):
                    # Get available agents
                    available_agents = self._get_available_agents()

                    # Start new events
                    for event in events:
                        if len(available_agents) >= 2:
                            # Up to 4 agents per event
                            participants = available_agents[:4]
                            await self.start_event(event, participants)
                            available_agents = available_agents[4:]

                await asyncio.sleep(300)  # Check for new events every 5 minutes

            except Exception as e:
                self.logger.error(f"Olympics cycle error: {str(e)}")
                await asyncio.sleep(60)  # Wait before retry

    def _get_available_agents(self) -> List[str]:
        """Get list of available agents for competition."""
        busy_agents = set(
            agent for event in self.active_events.values()
            if event["status"] == "active"
            for agent in event["participants"]
        )

        all_agents = {
            "analyst_agent",
            "strategist_agent",
            "ledger_agent",
            "asset_manager_agent",
            "coordinator_agent",
            "multimesh_agent",
            "ecommerce_agent",
            "workflow_optimizer_agent"
        }

        return list(all_agents - busy_agents)
