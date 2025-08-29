"""Base classes for Omega System components"""

import asyncio
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class OmegaSubsystem(ABC):
    """Abstract base class for all Omega subsystems"""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir) if root_dir else Path("data/omega/subsystems")
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.system_dir = self.root_dir / self.__class__.__name__.lower()
        self.system_dir.mkdir(exist_ok=True)

    @abstractmethod
    async def initialize_agent(self, agent_id: str) -> Dict:
        """Initialize an agent in this subsystem"""
        pass

    @abstractmethod
    async def evolve_agent(self, agent_id: str) -> Dict:
        """Evolve an agent through this subsystem"""
        pass

    async def _save_state(self, agent_id: str, state: Dict):
        """Save agent state for this subsystem"""
        state_file = self.system_dir / f"{agent_id}.json"
        async with asyncio.Lock():
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)

    async def _load_state(self, agent_id: str) -> Optional[Dict]:
        """Load agent state for this subsystem"""
        state_file = self.system_dir / f"{agent_id}.json"
        if not state_file.exists():
            return None
        async with asyncio.Lock():
            with open(state_file) as f:
                return json.load(f)
