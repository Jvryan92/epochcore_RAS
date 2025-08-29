#!/usr/bin/env python3
"""Epoch Scheduler for managing trigger execution sequences"""

from game_streaming import GameStreamManager
from game_replay import ReplayManager
from game_analytics import GameAnalytics
from enhanced_game_controller import EnhancedGameController
from typing import Dict, List, Optional
from dataclasses import asdict, dataclass
import argparse
import asyncio
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('epoch_scheduler')


@dataclass
class PhaseConfig:
    family: str
    intensity: int
    steps: int
    phase_window: int
    start_step: Optional[int] = None
    end_step: Optional[int] = None


@dataclass
class ExecutionResult:
    phase_id: str
    family: str
    step: int
    timestamp: str
    score: float
    efficiency: float
    mesh_factor: float
    metrics: Dict


class EpochScheduler:
    def __init__(
        self,
        dry_run: bool = False,
        json_log: Optional[str] = None,
        base_path: str = "data/epoch_runs"
    ):
        self.dry_run = dry_run
        self.json_log = json_log
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.game_controller = EnhancedGameController()
        self.stream_manager = GameStreamManager()
        self.replay_manager = ReplayManager()
        self.analytics = GameAnalytics(self.replay_manager)

        # Setup logging
        self.logger = logging.getLogger("EpochScheduler")
        if json_log:
            self.log_file = open(json_log, "a")
        else:
            self.log_file = None

    async def run_phase(
        self,
        phase_id: str,
        family: str,
        step: int,
        intensity: int
    ) -> ExecutionResult:
        """Execute a single phase"""
        self.logger.info(f"Running phase {phase_id} (Family: {family}, Step: {step})")

        if self.dry_run:
            # Simulate results for dry run
            import random
            result = ExecutionResult(
                phase_id=phase_id,
                family=family,
                step=step,
                timestamp=datetime.utcnow().isoformat(),
                score=random.random() * intensity,
                efficiency=0.5 + random.random() * 0.5,
                mesh_factor=1.0 + random.random() * 0.5,
                metrics={
                    "intensity": intensity,
                    "convergence": random.random(),
                    "stability": random.random()
                }
            )
        else:
            # Run actual game phase
            game_result = await self.game_controller.start_game(
                game_type=family.lower(),
                category="training",
                agent_id=f"agent_{phase_id}"
            )

            result = ExecutionResult(
                phase_id=phase_id,
                family=family,
                step=step,
                timestamp=datetime.utcnow().isoformat(),
                score=game_result.score,
                efficiency=game_result.efficiency,
                mesh_factor=game_result.mesh_factor,
                metrics={
                    "intensity": intensity,
                    "convergence": game_result.metrics.get("convergence", 0),
                    "stability": game_result.metrics.get("stability", 0)
                }
            )

        # Log result
        if self.log_file:
            self.log_file.write(json.dumps(asdict(result)) + "\n")
            self.log_file.flush()

        return result

    async def run_sequence(self, config: PhaseConfig) -> List[ExecutionResult]:
        """Run a sequence of phases"""
        results = []

        start = config.start_step or 1
        end = config.end_step or config.steps

        for step in range(start, end + 1):
            # Check if step is within phase window
            if config.phase_window:
                if (step % config.phase_window) != 0:
                    continue

            phase_id = f"{config.family}_{step:04d}"
            result = await self.run_phase(
                phase_id=phase_id,
                family=config.family,
                step=step,
                intensity=config.intensity
            )
            results.append(result)

            # Generate analytics after each phase
            if not self.dry_run:
                await self.analytics.generate_agent_report(f"agent_{phase_id}")

        return results

    def close(self):
        """Cleanup resources"""
        if self.log_file:
            self.log_file.close()

    @staticmethod
    def parse_args():
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description="Epoch Scheduler")
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without execution"
        )
        parser.add_argument("--family", default="ASTRA", help="Phase family")
        parser.add_argument(
            "--intensity",
            type=int,
            default=1000,
            help="Phase intensity"
        )
        parser.add_argument("--phase-window", type=int, help="Phase window size")
        parser.add_argument("--limit", type=int, help="Limit number of steps")
        parser.add_argument("--start", type=int, help="Start step")
        parser.add_argument("--end", type=int, help="End step")
        parser.add_argument("--json-log", help="JSON log file")
        return parser.parse_args()


async def main():
    args = EpochScheduler.parse_args()

    config = PhaseConfig(
        family=args.family,
        intensity=args.intensity,
        steps=args.limit or 1000,
        phase_window=args.phase_window,
        start_step=args.start,
        end_step=args.end
    )

    scheduler = EpochScheduler(
        dry_run=args.dry_run,
        json_log=args.json_log
    )

    try:
        results = await scheduler.run_sequence(config)

        # Print summary
        print("\nExecution Summary:")
        print(f"Family: {config.family}")
        print(f"Steps Executed: {len(results)}")
        if results:
            avg_score = sum(r.score for r in results) / len(results)
            avg_eff = sum(r.efficiency for r in results) / len(results)
            print(f"Average Score: {avg_score:.2f}")
            print(f"Average Efficiency: {avg_eff:.2f}")
            print(f"Total Mesh Factor: {sum(r.mesh_factor for r in results):.2f}")

    finally:
        scheduler.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
