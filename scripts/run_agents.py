"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

#!/usr/bin/env python3
"""Main entry point for the StrategyDECK AI Agent system."""

import sys
import argparse
from pathlib import Path
# Add the parent directory to the path so we can import the agent modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_agent.core.agent_manager import AgentManager
from ai_agent.agents.asset_manager import AssetManagerAgent
from ai_agent.agents.ledger_agent import LedgerAgent


def main():
    """Main function for running the AI agent system."""
    parser = argparse.ArgumentParser(
        description="StrategyDECK AI Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_agents.py                           # Run all agents
  python run_agents.py --agent project_monitor  # Run specific agent
  python run_agents.py --list                   # List available agents
  python run_agents.py --config custom.json    # Use custom config
        """,
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--agent",
        help="Run a specific agent by name"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available agents"
    )
    parser.add_argument(
        "--config",
        default="ai_agent/config/default.json",
        help="Path to custom config file"
    )

    args = parser.parse_args()

    # Setup agent manager
    config_path = Path(__file__).parent / args.config
    if not config_path.exists():
        print(f"Warning: Config file {config_path} not found, using defaults")
        config_path = None

    manager = AgentManager(config_path)

    # Register available agents
    agents = [
        AssetManagerAgent(
            manager.config.get("agents", {}).get("asset_manager", {})
        ),
        LedgerAgent(
            manager.config.get("agents", {}).get("ledger", {})
        ),
    ]

    for agent in agents:
        # Only register enabled agents
        agent_config = manager.config.get("agents", {}).get(agent.name, {})
        if agent_config.get("enabled", True):
            manager.register_agent(agent)

    # Handle list command
    if args.list:
        print("Available AI Agents:")
        for agent_name in manager.list_agents():
            print(f"  - {agent_name}")
        return 0

    # Run specific agent or all agents
    try:
        if args.agent:
            if args.agent not in manager.list_agents():
                print(f"Error: Agent '{args.agent}' not found or not enabled")
                print("Use --list to see available agents")
                return 1

            print(f"Running agent: {args.agent}")
            result = manager.run_agent(args.agent)
            print_result(result)

        else:
            print("Running all AI agents...")
            results = manager.run_all_agents()
            for result in results:
                print_result(result)
                print("-" * 50)

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def print_result(result):
    """Print agent execution result in a formatted way."""
    status = result.get("status", "unknown")
    agent = result.get("agent", "unknown")

    if status == "success":
        print(f"✅ {agent}: SUCCESS")
        if "result" in result and isinstance(result["result"], dict):
            # Print key metrics from the result
            print_summary(result["result"])
    else:
        print(f"❌ {agent}: ERROR - {result.get('error', 'Unknown error')}")


def print_summary(result_data):
    """Print a summary of agent results."""
    if "timestamp" in result_data:
        print(f"   Timestamp: {result_data['timestamp']}")

    if "project_structure" in result_data:
        ps = result_data["project_structure"]
        print(
            f"   Files: {ps.get('total_files', 0)} total, "
            f"{ps.get('python_files', 0)} Python"
        )

    if "asset_validation" in result_data:
        av = result_data["asset_validation"]
        issues = len(av.get("issues", []))
        print(f"   Asset validation: {issues} issues found")

    if "workflow_analysis" in result_data:
        wa = result_data["workflow_analysis"]
        print(f"   Workflows: {wa.get('total_workflows', 0)} found")

    if "optimization_suggestions" in result_data:
        suggestions = result_data["optimization_suggestions"]
        if isinstance(suggestions, list):
            print(f"   Optimization suggestions: {len(suggestions)}")
        elif isinstance(suggestions, dict):
            # Handle nested structure
            total_suggestions = sum(
                len(v) if isinstance(v, list) else 1
                for v in suggestions.values()
            )
            print(f"   Optimization suggestions: {total_suggestions}")


if __name__ == "__main__":
    sys.exit(main())
