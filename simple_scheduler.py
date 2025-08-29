"""Simple epoch trigger scheduler"""

import argparse
import asyncio
import csv
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


async def run_scheduler(jsonl_path: str, edges_path: str, dry_run: bool = True):
    """Run the epoch scheduler"""
    # Load triggers
    triggers = {}
    with open(jsonl_path) as f:
        for line in f:
            trigger = json.loads(line)
            triggers[trigger['id']] = trigger

    # Load edges
    edges = {}
    with open(edges_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            source = row['source']
            target = row['target']
            if source not in edges:
                edges[source] = []
            edges[source].append(target)

    # Find roots (triggers with no dependencies)
    dependent_triggers = set()
    for deps in edges.values():
        dependent_triggers.update(deps)

    root_triggers = set(triggers.keys()) - dependent_triggers

    # Execute triggers
    completed = set()
    while root_triggers:
        # Get next batch
        batch = list(root_triggers)[:5]

        # Execute batch
        for trigger_id in batch:
            trigger = triggers[trigger_id]
            if dry_run:
                logging.info(
                    f"DRY RUN: Would execute {trigger_id} ({trigger['family']})")
            else:
                logging.info(f"Executing {trigger_id}")

            # Mark as completed
            completed.add(trigger_id)
            root_triggers.remove(trigger_id)

            # Add any triggers that are now ready
            for source, targets in edges.items():
                if source not in completed and all(t in completed for t in targets):
                    root_triggers.add(source)

        # Small delay between batches
        await asyncio.sleep(0.1)

    logging.info(f"Completed {len(completed)} triggers")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jsonl', required=True)
    parser.add_argument('--edges', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    await run_scheduler(args.jsonl, args.edges, args.dry_run)

if __name__ == "__main__":
    asyncio.run(main())
