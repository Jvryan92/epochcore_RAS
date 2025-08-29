"""Runner script for compound triggers"""

import argparse
import asyncio
import logging
from pathlib import Path

from compound_trigger import CompoundTriggerSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("epoch_run")


async def run_compound(args):
    """Run compound trigger system with args"""
    system = CompoundTriggerSystem(
        root_dir=args.data_dir,
        ledger_path=args.ledger
    )

    await system.initialize(
        total_steps=args.limit,
        window_size=args.phase_window,
        intensity=args.intensity
    )

    await system.run_compound_mode(
        family=args.family,
        dry_run=args.mode == "dry"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Compound Trigger Runner"
    )

    parser.add_argument(
        "--mode",
        choices=["dry", "live"],
        default="dry",
        help="Execution mode"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=180,
        help="Step limit"
    )

    parser.add_argument(
        "--phase-window",
        type=int,
        default=5,
        help="Oscillation window size"
    )

    parser.add_argument(
        "--intensity",
        type=float,
        default=1000.0,
        help="Base intensity"
    )

    parser.add_argument(
        "--family",
        help="Optional trigger family"
    )

    parser.add_argument(
        "--compound",
        action="store_true",
        help="Enable compound mode"
    )

    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/compound",
        help="Data directory"
    )

    parser.add_argument(
        "--ledger",
        type=str,
        default="ledger/compound_ledger.jsonl",
        help="Ledger path"
    )

    args = parser.parse_args()

    if args.compound:
        asyncio.run(run_compound(args))
    else:
        logger.error("Non-compound mode not yet implemented")


if __name__ == "__main__":
    main()
