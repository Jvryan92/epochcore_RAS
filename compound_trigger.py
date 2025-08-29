"""Compound Trigger System with Oscillation Windows"""

import asyncio
import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("compound_trigger")


@dataclass
class OscillationWindow:
    """Represents an oscillation window for compound execution"""
    start_step: int
    window_size: int
    intensity: float
    resonance: float
    triggers: List[str]
    seal_hash: Optional[str] = None


@dataclass
class CompoundState:
    """Tracks compound execution state"""
    current_step: int
    total_steps: int
    intensity: float
    window_size: int
    active_windows: List[OscillationWindow]
    completed_triggers: List[str]
    state_hash: str
    timestamp: str


class CompoundTriggerSystem:
    """Manages compound trigger execution with oscillation windows"""

    def __init__(
        self,
        root_dir: str = "data/compound",
        ledger_path: str = "ledger/compound_ledger.jsonl"
    ):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

        self.windows: List[OscillationWindow] = []
        self.state: Optional[CompoundState] = None

    async def initialize(
        self,
        total_steps: int = 180,
        window_size: int = 5,
        intensity: float = 1000.0
    ):
        """Initialize the compound system"""
        logger.info(
            f"Initializing compound system with {total_steps} steps, "
            f"window size {window_size}, intensity {intensity}"
        )

        self.state = CompoundState(
            current_step=0,
            total_steps=total_steps,
            intensity=intensity,
            window_size=window_size,
            active_windows=[],
            completed_triggers=[],
            state_hash=self._generate_state_hash([]),
            timestamp=datetime.utcnow().isoformat()
        )

    def _generate_state_hash(self, data: List[str]) -> str:
        """Generate SHA256 hash of state data"""
        hasher = hashlib.sha256()
        for item in sorted(data):
            hasher.update(item.encode())
        return hasher.hexdigest()

    async def create_oscillation_window(
        self,
        triggers: List[str],
        intensity_modifier: float = 1.0
    ) -> OscillationWindow:
        """Create a new oscillation window"""
        if not self.state:
            raise ValueError("System not initialized")

        window = OscillationWindow(
            start_step=self.state.current_step,
            window_size=self.state.window_size,
            intensity=self.state.intensity * intensity_modifier,
            resonance=0.0,
            triggers=triggers
        )

        # Generate seal hash for window
        window.seal_hash = self._generate_state_hash(triggers)

        self.windows.append(window)
        self.state.active_windows.append(window)

        return window

    async def process_window(
        self,
        window: OscillationWindow
    ) -> Dict:
        """Process triggers in an oscillation window"""
        results = []

        for trigger in window.triggers:
            # Simulate trigger execution with intensity scaling
            execution_time = 1.0 / window.intensity
            await asyncio.sleep(execution_time)

            result = {
                "trigger": trigger,
                "step": self.state.current_step,
                "window_hash": window.seal_hash,
                "execution_time": execution_time,
                "intensity": window.intensity,
                "timestamp": datetime.utcnow().isoformat()
            }

            results.append(result)
            self.state.completed_triggers.append(trigger)

        return {
            "window_hash": window.seal_hash,
            "results": results,
            "resonance": window.resonance
        }

    async def advance_windows(self) -> None:
        """Advance all active oscillation windows"""
        if not self.state:
            raise ValueError("System not initialized")

        self.state.current_step += 1

        # Remove completed windows
        self.state.active_windows = [
            w for w in self.state.active_windows
            if (self.state.current_step - w.start_step) < w.window_size
        ]

        # Update state hash
        self.state.state_hash = self._generate_state_hash(
            self.state.completed_triggers
        )

    async def seal_ledger(self, results: List[Dict]) -> None:
        """Seal results to ledger with SHA256 hash"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "state_hash": self.state.state_hash,
            "completed_triggers": len(self.state.completed_triggers),
            "results": results
        }

        # Append to ledger
        with open(self.ledger_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    async def run_compound_mode(
        self,
        family: Optional[str] = None,
        dry_run: bool = True
    ) -> None:
        """Run compound mode execution"""
        if not self.state:
            raise ValueError("System not initialized")

        logger.info(
            f"Starting compound mode: family={family}, "
            f"steps={self.state.total_steps}, "
            f"window={self.state.window_size}"
        )

        all_results = []

        while self.state.current_step < self.state.total_steps:
            # Create new window if needed
            if len(self.state.active_windows) < 3:  # Max 3 concurrent windows
                triggers = [
                    f"{family}-{i}" if family
                    else f"TRIGGER-{i}"
                    for i in range(self.state.window_size)
                ]

                window = await self.create_oscillation_window(
                    triggers,
                    intensity_modifier=1.0 + (self.state.current_step / 100)
                )

                if dry_run:
                    logger.info(
                        f"DRY RUN: Created window {window.seal_hash} "
                        f"at step {self.state.current_step}"
                    )

            # Process active windows
            for window in self.state.active_windows:
                results = await self.process_window(window)
                all_results.append(results)

                if dry_run:
                    logger.info(
                        f"DRY RUN: Processed window {window.seal_hash} "
                        f"with {len(results['results'])} triggers"
                    )

            # Advance windows
            await self.advance_windows()

        # Seal final results
        await self.seal_ledger(all_results)

        logger.info(
            f"Compound mode completed: {len(self.state.completed_triggers)} "
            f"triggers processed"
        )


async def main():
    """Main entry point for compound trigger system"""
    system = CompoundTriggerSystem()

    # Initialize with default settings
    await system.initialize(
        total_steps=180,
        window_size=5,
        intensity=1000.0
    )

    # Run in dry mode
    await system.run_compound_mode(dry_run=True)

    # Run for GAME family
    await system.run_compound_mode(family="GAME", dry_run=True)


if __name__ == "__main__":
    asyncio.run(main())
