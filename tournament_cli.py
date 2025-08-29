#!/usr/bin/env python3
"""
Tournament Management CLI
Control and monitor agent tournaments
"""

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from tournament_manager import TournamentConfig, TournamentManager


async def create_command(manager: TournamentManager, args):
    """Create a new tournament"""
    config = TournamentConfig(
        name=args.name,
        game_type=args.game,
        rounds=args.rounds,
        matches_per_round=args.matches,
        league_promotion_rate=args.promotion_rate,
        league_relegation_rate=args.relegation_rate,
        mesh_multiplier=args.mesh_multiplier
    )

    tournament_id = await manager.create_tournament(config)
    print(f"Created tournament: {tournament_id}")
    return tournament_id


async def run_command(manager: TournamentManager, args):
    """Run a tournament"""
    print(f"Starting tournament: {args.tournament}")
    await manager.run_tournament(args.tournament)
    print("Tournament completed")


async def status_command(manager: TournamentManager, args):
    """Show tournament status"""
    tournament_dir = Path("data/tournaments") / args.tournament
    if not tournament_dir.exists():
        print(f"Tournament {args.tournament} not found")
        return

    # Load configuration
    config_file = tournament_dir / "config.json"
    with open(config_file) as f:
        config = json.load(f)

    print(f"\nTournament: {args.tournament}")
    print("-" * 50)
    print(f"Name: {config['name']}")
    print(f"Game Type: {config['game_type']}")
    print(f"Rounds: {config['rounds']}")
    print(f"Matches per Round: {config['matches_per_round']}")

    # Get completed rounds
    completed_rounds = len(list(tournament_dir.glob("round_*.jsonl")))
    print(f"\nProgress: {completed_rounds}/{config['rounds']} rounds completed")

    if completed_rounds > 0:
        # Load latest round results
        latest_round = completed_rounds
        round_file = tournament_dir / f"round_{latest_round}.jsonl"
        results = []
        with open(round_file) as f:
            for line in f:
                results.append(json.loads(line))

        print(f"\nLatest Round ({latest_round}) Summary:")
        print(f"Matches Played: {len(results)}")
        wins = [r for r in results if r["winner_id"]]
        print(f"Decisive Matches: {len(wins)}")
        print(
            f"Average Score: {sum(r['score1'] + r['score2'] for r in results)/len(results)/2:.2f}"
        )
        print(
            f"Total Mesh Awarded: {sum(r['mesh_earned'] for r in results):.2f}"
        )


async def rankings_command(manager: TournamentManager, args):
    """Show current rankings"""
    tournament_dir = Path("data/tournaments") / args.tournament
    if not tournament_dir.exists():
        print(f"Tournament {args.tournament} not found")
        return

    rankings_file = tournament_dir / "final_rankings.json"
    if not rankings_file.exists():
        print("Rankings not yet available")
        return

    with open(rankings_file) as f:
        rankings = json.load(f)

    print("\nCurrent Rankings:")
    print("-" * 50)

    for league, agents in rankings.items():
        print(f"\n{league.upper()}:")
        print("-" * 30)
        sorted_agents = sorted(
            agents,
            key=lambda x: (
                x["stats"]["win_rate"],
                x["stats"]["avg_score"]
            ),
            reverse=True
        )

        for i, agent in enumerate(sorted_agents, 1):
            stats = agent["stats"]
            print(
                f"{i:2d}. {agent['agent_id']:15s} "
                f"W/L: {stats['matches_won']}/{stats['matches_played']} "
                f"({stats['win_rate']*100:.1f}%) "
                f"Mesh: {stats['mesh_earned']:.1f}"
            )


def main():
    parser = argparse.ArgumentParser(description="Tournament Management")
    subparsers = parser.add_subparsers(dest="command")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create tournament")
    create_parser.add_argument("name", help="Tournament name")
    create_parser.add_argument("--game", default="chess", help="Game type")
    create_parser.add_argument(
        "--rounds", type=int, default=10, help="Number of rounds")
    create_parser.add_argument(
        "--matches",
        type=int,
        default=20,
        help="Matches per round"
    )
    create_parser.add_argument(
        "--promotion-rate",
        type=float,
        default=0.2,
        help="League promotion rate"
    )
    create_parser.add_argument(
        "--relegation-rate",
        type=float,
        default=0.1,
        help="League relegation rate"
    )
    create_parser.add_argument(
        "--mesh-multiplier",
        type=float,
        default=2.0,
        help="Mesh reward multiplier"
    )

    # Run command
    run_parser = subparsers.add_parser("run", help="Run tournament")
    run_parser.add_argument("tournament", help="Tournament ID")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show tournament status")
    status_parser.add_argument("tournament", help="Tournament ID")

    # Rankings command
    rankings_parser = subparsers.add_parser("rankings", help="Show rankings")
    rankings_parser.add_argument("tournament", help="Tournament ID")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    manager = TournamentManager()

    if args.command == "create":
        tournament_id = asyncio.run(create_command(manager, args))
        if args.run:
            args.tournament = tournament_id
            asyncio.run(run_command(manager, args))
    elif args.command == "run":
        asyncio.run(run_command(manager, args))
    elif args.command == "status":
        asyncio.run(status_command(manager, args))
    elif args.command == "rankings":
        asyncio.run(rankings_command(manager, args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
