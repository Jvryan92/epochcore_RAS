#!/usr/bin/env python3
"""
Agent Supervisor CLI
Control and monitor the agent supervision system
"""

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from agent_supervisor import AgentSupervisor


async def start_command(supervisor: AgentSupervisor, args):
    """Start the supervisor"""
    await supervisor.start()


async def status_command(supervisor: AgentSupervisor, args):
    """Show current system status"""
    metrics_dir = Path("data/supervisor/metrics")
    if not metrics_dir.exists():
        print("No metrics data available")
        return

    # Get latest metrics file
    latest = max(metrics_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
    with open(latest) as f:
        metrics = json.load(f)

    print(f"\nSystem Status as of {metrics['timestamp']}:")
    print("-" * 50)
    system = metrics["system"]
    print(f"Active Agents: {system['active_agents']}/{system['total_agents']}")
    print(f"System Load: {system['system_load']:.1f}%")
    print(f"Memory Usage: {system['memory_usage']:.1f}%")
    print(f"Error Count: {system['error_count']}")
    print(f"Backup Status: {system['backup_status']}")

    print("\nAgent Status:")
    print("-" * 50)
    for agent_id, health in metrics["agents"].items():
        status_color = {
            "active": "\033[92m",  # green
            "paused": "\033[93m",  # yellow
            "error": "\033[91m",  # red
            "recovering": "\033[94m",  # blue
        }.get(health["status"], "")
        reset_color = "\033[0m"

        print(f"\n{agent_id}:")
        print(f"  Status: {status_color}{health['status']}{reset_color}")
        print(f"  CPU: {health['cpu_usage']:.1f}%")
        print(f"  Memory: {health['memory_usage']:.1f}%")
        print(f"  Error Rate: {health['error_rate']:.3f}")
        print(f"  Games Completed: {health['games_completed']}")


async def backup_command(supervisor: AgentSupervisor, args):
    """Trigger immediate backup"""
    print("Initiating backup of all agents...")
    result = await supervisor.backup_orchestrator.backup_all_agents()

    print(f"\nBackup Summary:")
    print(f"Total Agents: {result['total_agents']}")
    print(f"Successful: {result['successful']}")
    print(f"Failed: {result['failed']}")


async def monitor_command(supervisor: AgentSupervisor, args):
    """Live monitoring mode"""
    try:
        while True:
            # Clear screen
            print("\033[2J\033[H")

            await status_command(supervisor, args)
            print("\nPress Ctrl+C to exit")
            await asyncio.sleep(5)

    except KeyboardInterrupt:
        print("\nExiting monitor mode")


def main():
    parser = argparse.ArgumentParser(description="Agent Supervisor Management")
    subparsers = parser.add_subparsers(dest="command")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start supervisor")
    start_parser.add_argument(
        "--config",
        help="Path to configuration file"
    )

    # Status command
    status_parser = subparsers.add_parser("status", help="Show system status")

    # Backup command
    backup_parser = subparsers.add_parser(
        "backup",
        help="Trigger immediate backup"
    )

    # Monitor command
    monitor_parser = subparsers.add_parser(
        "monitor",
        help="Live monitoring mode"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    supervisor = AgentSupervisor(args.config if hasattr(args, 'config') else None)

    if args.command == "start":
        asyncio.run(start_command(supervisor, args))
    elif args.command == "status":
        asyncio.run(status_command(supervisor, args))
    elif args.command == "backup":
        asyncio.run(backup_command(supervisor, args))
    elif args.command == "monitor":
        asyncio.run(monitor_command(supervisor, args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
