#!/usr/bin/env python3
"""
Scheduled Agent Flash Sync
Automatically runs flash sync operations at scheduled times (9 AM, 2 PM, and 5 PM)
"""

import datetime
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

# Setup logging
log_dir = Path("./logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "scheduled_sync.log"),
        logging.StreamHandler(sys.stdout),
    ],
)

# Configuration
FLASH_SYNC_SCRIPT = Path("./flash_sync_agents.py")
SCHEDULE = [
    {"hour": 9, "minute": 0, "name": "morning"},
    {"hour": 14, "minute": 0, "name": "afternoon"},
    {"hour": 17, "minute": 0, "name": "evening"},
]
RESULTS_DIR = Path("./sync_results")
RESULTS_DIR.mkdir(exist_ok=True)


def get_next_scheduled_time():
    """Calculate the next scheduled sync time"""
    now = datetime.datetime.now()
    today_schedule = []

    for schedule in SCHEDULE:
        scheduled_time = now.replace(
            hour=schedule["hour"], minute=schedule["minute"], second=0, microsecond=0
        )
        if scheduled_time <= now:
            # If this time has passed today, schedule for tomorrow
            scheduled_time = scheduled_time + datetime.timedelta(days=1)

        today_schedule.append({"time": scheduled_time, "name": schedule["name"]})

    # Get the next scheduled time (minimum time in the future)
    next_schedule = min(today_schedule, key=lambda x: x["time"])
    return next_schedule


def run_flash_sync(schedule_name):
    """Run the flash sync script and capture the results"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / f"sync_{schedule_name}_{timestamp}.json"

    try:
        logging.info(f"Running flash sync ({schedule_name})...")

        # Run the flash sync script and capture the output
        result = subprocess.run(
            [sys.executable, str(FLASH_SYNC_SCRIPT)],
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse JSON output from the script
        output_lines = result.stdout.strip().split("\n")
        json_output = None

        for line in output_lines:
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    json_output = json.loads(line)
                    break
                except json.JSONDecodeError:
                    pass

        # Save the results
        with open(result_file, "w") as f:
            if json_output:
                json.dump(json_output, f, indent=2)
            else:
                f.write(result.stdout)

        # Log success
        consensus = (
            "achieved"
            if json_output and json_output.get("consensus_achieved", False)
            else "FAILED"
        )
        anomalies = json_output.get("anomalies", 0) if json_output else "unknown"
        logging.info(
            f"Flash sync completed. Consensus: {consensus}, Anomalies: {anomalies}"
        )

        return True
    except Exception as e:
        logging.error(f"Error running flash sync: {str(e)}")
        with open(result_file, "w") as f:
            f.write(f"ERROR: {str(e)}")
        return False


def run_as_daemon():
    """Run as a daemon process, scheduling syncs at specified times"""
    logging.info("Starting scheduled flash sync daemon")
    schedule_str = ", ".join(
        [f"{s['hour']}:{s['minute']:02d} ({s['name']})" for s in SCHEDULE]
    )
    logging.info(f"Scheduled times: {schedule_str}")

    while True:
        next_schedule = get_next_scheduled_time()
        now = datetime.datetime.now()
        wait_seconds = (next_schedule["time"] - now).total_seconds()

        logging.info(
            f"Next scheduled sync: {next_schedule['name']} at {next_schedule['time'].strftime('%Y-%m-%d %H:%M:%S')} (in {wait_seconds:.0f} seconds)"
        )

        if wait_seconds > 0:
            # Sleep at most 60 seconds at a time to allow for clean shutdown
            time.sleep(min(wait_seconds, 60))

        # Check if it's time to run
        now = datetime.datetime.now()
        if now >= next_schedule["time"]:
            run_flash_sync(next_schedule["name"])


def run_once():
    """Run the flash sync once immediately"""
    logging.info("Running flash sync once immediately")
    now = datetime.datetime.now()
    schedule_name = "manual"

    # Determine if we're close to a scheduled time
    for schedule in SCHEDULE:
        scheduled_time = now.replace(hour=schedule["hour"], minute=schedule["minute"])
        diff = abs((scheduled_time - now).total_seconds())
        if diff < 30 * 60:  # Within 30 minutes
            schedule_name = schedule["name"]
            break

    run_flash_sync(schedule_name)


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # Run once immediately
        run_once()
    else:
        # Run as a daemon
        run_as_daemon()


if __name__ == "__main__":
    if not FLASH_SYNC_SCRIPT.exists():
        logging.error(f"Flash sync script not found at {FLASH_SYNC_SCRIPT}")
        sys.exit(1)

    main()
