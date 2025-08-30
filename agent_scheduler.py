#!/usr/bin/env python3
"""
Agent Sync Scheduler - Manages automatic scheduling of agent flash syncs and monitoring
"""

import argparse
import datetime as dt
import json
import logging
import os
import subprocess
import time
from pathlib import Path

import schedule

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("agent_scheduler.log"), logging.StreamHandler()],
)
logger = logging.getLogger("AgentScheduler")

# Default configuration
DEFAULT_CONFIG = {
    "flash_sync": {
        "enabled": True,
        "schedule": {
            "interval_minutes": 60,
            "fixed_times": ["06:00", "12:00", "18:00", "00:00"],
            "use_fixed_times": False,
        },
    },
    "health_monitor": {"enabled": True, "start_on_boot": True},
    "dashboard": {"enabled": True, "update_interval_minutes": 15},
    "anomaly_response": {
        "trigger_sync_on_anomalies": True,
        "max_consecutive_syncs": 3,
        "cooldown_minutes": 15,
    },
}

# Paths
CONFIG_FILE = "agent_scheduler_config.json"
MONITOR_PROCESS = None
SYNC_COUNT = 0
LAST_SYNC_TIME = dt.datetime.min
COOLDOWN_UNTIL = dt.datetime.min


def load_config():
    """Load scheduler configuration"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    # Create default config
    with open(CONFIG_FILE, "w") as f:
        json.dump(DEFAULT_CONFIG, f, indent=2)
    return DEFAULT_CONFIG


def save_config(config):
    """Save scheduler configuration"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def run_flash_sync():
    """Run the flash sync process"""
    global SYNC_COUNT, LAST_SYNC_TIME

    # Check cooldown
    if dt.datetime.now() < COOLDOWN_UNTIL:
        logger.info(
            f"Flash sync in cooldown until {COOLDOWN_UNTIL.strftime('%H:%M:%S')}"
        )
        return

    logger.info("Running flash sync...")
    try:
        result = subprocess.run(
            ["python3", "flash_sync_agents.py"], capture_output=True, text=True
        )

        if result.returncode == 0:
            logger.info("Flash sync completed successfully")
            SYNC_COUNT += 1
            LAST_SYNC_TIME = dt.datetime.now()

            # Check for max consecutive syncs
            config = load_config()
            max_syncs = config["anomaly_response"]["max_consecutive_syncs"]
            if SYNC_COUNT >= max_syncs:
                cooldown_minutes = config["anomaly_response"]["cooldown_minutes"]
                global COOLDOWN_UNTIL
                COOLDOWN_UNTIL = dt.datetime.now() + dt.timedelta(
                    minutes=cooldown_minutes
                )
                logger.info(
                    f"Reached {max_syncs} consecutive syncs, entering cooldown for {cooldown_minutes} minutes"
                )
                SYNC_COUNT = 0
        else:
            logger.error(f"Flash sync failed: {result.stderr}")
    except Exception as e:
        logger.error(f"Error running flash sync: {e}")


def update_dashboard():
    """Update the agent dashboard"""
    logger.info("Updating dashboard...")
    try:
        subprocess.run(
            ["python3", "agent_health_monitor.py", "--dashboard"],
            capture_output=True,
            text=True,
        )
        logger.info("Dashboard updated successfully")
    except Exception as e:
        logger.error(f"Error updating dashboard: {e}")


def start_health_monitor():
    """Start the health monitoring process"""
    global MONITOR_PROCESS

    if MONITOR_PROCESS is not None and MONITOR_PROCESS.poll() is None:
        logger.info("Health monitor is already running")
        return

    logger.info("Starting health monitor...")
    try:
        MONITOR_PROCESS = subprocess.Popen(
            ["python3", "agent_health_monitor.py", "--start"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info(f"Health monitor started with PID {MONITOR_PROCESS.pid}")
    except Exception as e:
        logger.error(f"Error starting health monitor: {e}")


def stop_health_monitor():
    """Stop the health monitoring process"""
    global MONITOR_PROCESS

    if MONITOR_PROCESS is None or MONITOR_PROCESS.poll() is not None:
        logger.info("Health monitor is not running")
        return

    logger.info("Stopping health monitor...")
    try:
        MONITOR_PROCESS.terminate()
        MONITOR_PROCESS.wait(timeout=5)
        logger.info("Health monitor stopped")
    except Exception as e:
        logger.error(f"Error stopping health monitor: {e}")
        # Force kill if terminate doesn't work
        try:
            MONITOR_PROCESS.kill()
            logger.info("Health monitor forcefully killed")
        except:
            pass


def check_anomalies():
    """Check for anomalies and trigger sync if needed"""
    config = load_config()
    if not config["anomaly_response"]["trigger_sync_on_anomalies"]:
        return

    # Check if we're in cooldown
    if dt.datetime.now() < COOLDOWN_UNTIL:
        return

    # Check for recent alerts indicating anomalies
    alert_file = "./monitor/alerts.jsonl"
    if not os.path.exists(alert_file):
        return

    # Read last few alerts
    try:
        recent_alerts = []
        with open(alert_file, "r") as f:
            lines = f.readlines()
            for line in lines[-10:]:  # Check last 10 alerts
                if not line.strip():
                    continue
                alert = json.loads(line)
                # Only consider alerts from the last 5 minutes
                alert_time = dt.datetime.strptime(alert["ts"], "%Y-%m-%dT%H:%M:%SZ")
                if (dt.datetime.utcnow() - alert_time).total_seconds() < 300:
                    recent_alerts.append(alert)

        # If we have critical alerts, trigger a sync
        critical_alerts = [a for a in recent_alerts if a.get("severity") == "critical"]
        if critical_alerts:
            logger.info(
                f"Detected {len(critical_alerts)} critical anomalies, triggering flash sync"
            )
            run_flash_sync()
    except Exception as e:
        logger.error(f"Error checking anomalies: {e}")


def setup_schedules():
    """Set up scheduled tasks"""
    config = load_config()

    # Clear existing schedules
    schedule.clear()

    # Set up flash sync schedule
    if config["flash_sync"]["enabled"]:
        if config["flash_sync"]["schedule"]["use_fixed_times"]:
            # Schedule at fixed times
            for time_str in config["flash_sync"]["schedule"]["fixed_times"]:
                schedule.every().day.at(time_str).do(run_flash_sync)
                logger.info(f"Scheduled flash sync at {time_str}")
        else:
            # Schedule at intervals
            interval = config["flash_sync"]["schedule"]["interval_minutes"]
            schedule.every(interval).minutes.do(run_flash_sync)
            logger.info(f"Scheduled flash sync every {interval} minutes")

    # Set up dashboard update schedule
    if config["dashboard"]["enabled"]:
        interval = config["dashboard"]["update_interval_minutes"]
        schedule.every(interval).minutes.do(update_dashboard)
        logger.info(f"Scheduled dashboard updates every {interval} minutes")

    # Check for anomalies every 5 minutes
    schedule.every(5).minutes.do(check_anomalies)
    logger.info("Scheduled anomaly checks every 5 minutes")


def main():
    """Main function for scheduler"""
    parser = argparse.ArgumentParser(description="Agent Sync Scheduler")
    parser.add_argument("--start", action="store_true", help="Start scheduler")
    parser.add_argument("--stop", action="store_true", help="Stop scheduler")
    parser.add_argument(
        "--sync-now", action="store_true", help="Run flash sync immediately"
    )
    parser.add_argument("--config", action="store_true", help="Edit configuration")
    parser.add_argument("--status", action="store_true", help="Show scheduler status")

    args = parser.parse_args()

    if args.start:
        logger.info("Starting agent scheduler...")

        # Load configuration
        config = load_config()

        # Start health monitor if enabled
        if (
            config["health_monitor"]["enabled"]
            and config["health_monitor"]["start_on_boot"]
        ):
            start_health_monitor()

        # Set up schedules
        setup_schedules()

        # Run initial dashboard update
        if config["dashboard"]["enabled"]:
            update_dashboard()

        # Run initial sync if needed
        if config["flash_sync"]["enabled"]:
            run_flash_sync()

        # Keep the scheduler running
        logger.info("Scheduler is running. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            stop_health_monitor()

    elif args.stop:
        logger.info("Stopping scheduler...")
        stop_health_monitor()
        logger.info("Scheduler stopped")

    elif args.sync_now:
        run_flash_sync()

    elif args.config:
        # Open config file in default editor
        config = load_config()
        print(json.dumps(config, indent=2))
        print(
            "\nTo modify the configuration, edit the file:",
            os.path.abspath(CONFIG_FILE),
        )

    elif args.status:
        # Show scheduler status
        config = load_config()

        print("=== Agent Scheduler Status ===")
        print(
            f"Health Monitor: {'Running' if MONITOR_PROCESS and MONITOR_PROCESS.poll() is None else 'Stopped'}"
        )
        print(
            f"Flash Sync: {'Enabled' if config['flash_sync']['enabled'] else 'Disabled'}"
        )

        if config["flash_sync"]["schedule"]["use_fixed_times"]:
            times = ", ".join(config["flash_sync"]["schedule"]["fixed_times"])
            print(f"Sync Schedule: Daily at {times}")
        else:
            interval = config["flash_sync"]["schedule"]["interval_minutes"]
            print(f"Sync Schedule: Every {interval} minutes")

        print(
            f"Dashboard Updates: {'Enabled' if config['dashboard']['enabled'] else 'Disabled'}"
        )
        if config["dashboard"]["enabled"]:
            interval = config["dashboard"]["update_interval_minutes"]
            print(f"Dashboard Update Interval: Every {interval} minutes")

        print(
            f"Last Sync: {LAST_SYNC_TIME.strftime('%Y-%m-%d %H:%M:%S') if LAST_SYNC_TIME > dt.datetime.min else 'Never'}"
        )

        if COOLDOWN_UNTIL > dt.datetime.now():
            print(f"Cooldown: Active until {COOLDOWN_UNTIL.strftime('%H:%M:%S')}")
        else:
            print("Cooldown: Inactive")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
