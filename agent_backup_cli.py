#!/usr/bin/env python3
"""
Agent Backup CLI
Manage agent backups and restoration
"""

import argparse
import asyncio
import logging

from agent_backup import AgentBackupOrchestrator


async def backup_command(orchestrator: AgentBackupOrchestrator, args):
    """Handle backup operations"""
    if args.agent:
        result = await orchestrator.backup_agent(args.agent)
        if result["status"] == "success":
            print(f"Successfully backed up agent {args.agent}")
            print(f"Archive: {result['archive']}")
        else:
            print(f"Backup failed for agent {args.agent}: {result['error']}")
    else:
        print("Starting backup of all agents...")
        summary = await orchestrator.backup_all_agents()
        print(f"\nBackup Summary:")
        print(f"Total Agents: {summary['total_agents']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")


async def verify_command(orchestrator: AgentBackupOrchestrator, args):
    """Handle verification operations"""
    result = await orchestrator.verify_backup(args.agent, args.timestamp)
    if result["status"] == "success":
        print(f"\nVerification Results for {args.agent}:")
        for key, valid in result["verification"].items():
            print(f"{key}: {'✓' if valid else '✗'}")
    else:
        print(f"Verification failed: {result['error']}")


async def restore_command(orchestrator: AgentBackupOrchestrator, args):
    """Handle restore operations"""
    print(f"Restoring {args.agent} from backup {args.timestamp}...")
    result = await orchestrator.restore_agent(args.agent, args.timestamp)
    if result["status"] == "success":
        print("\nRestoration successful!")
        print("\nRestored items:")
        for item, restored in result["restored_items"].items():
            print(f"{item}: {'✓' if restored else '✗'}")
    else:
        print(f"Restoration failed: {result['error']}")


def main():
    parser = argparse.ArgumentParser(description="Agent Backup Management")
    subparsers = parser.add_subparsers(dest="command")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup agents")
    backup_parser.add_argument(
        "--agent",
        help="Specific agent to backup. Omit for all agents"
    )

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify backup")
    verify_parser.add_argument("agent", help="Agent ID")
    verify_parser.add_argument("timestamp", help="Backup timestamp")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("agent", help="Agent ID")
    restore_parser.add_argument("timestamp", help="Backup timestamp")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    orchestrator = AgentBackupOrchestrator()

    if args.command == "backup":
        asyncio.run(backup_command(orchestrator, args))
    elif args.command == "verify":
        asyncio.run(verify_command(orchestrator, args))
    elif args.command == "restore":
        asyncio.run(restore_command(orchestrator, args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
