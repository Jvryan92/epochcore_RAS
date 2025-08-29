"""
Agent Tournament System
Organizes competitive matches between agents with rankings, leagues, and deep analytics
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

from agent_backup import AgentBackupOrchestrator
from enhanced_game_controller import EnhancedGameController
from game_analytics import GameAnalytics
from game_replay import ReplayManager
from game_streaming import GameStreamManager


@dataclass
class TournamentConfig:
    name: str
    game_type: str
    rounds: int
    matches_per_round: int
    league_promotion_rate: float = 0.2
    league_relegation_rate: float = 0.1
    mesh_multiplier: float = 2.0


@dataclass
class MatchResult:
    tournament_id: str
    round_number: int
    match_id: str
    agent1_id: str
    agent2_id: str
    winner_id: str
    score1: float
    score2: float
    duration: float
    mesh_earned: float
    timestamp: str


@dataclass
class AgentStats:
    agent_id: str
    league: str
    rank: int
    matches_played: int
    matches_won: int
    total_score: float
    mesh_earned: float
    win_rate: float
    avg_score: float
    peak_rank: int


class TournamentManager:
    def __init__(self, root_dir: str = "data/tournaments"):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.game_controller = EnhancedGameController()
        self.stream_manager = GameStreamManager()
        self.replay_manager = ReplayManager()
        self.analytics = GameAnalytics(self.replay_manager)
        self.backup_orchestrator = AgentBackupOrchestrator()

        # Tournament state
        self.active_tournament: Optional[str] = None
        self.league_rankings: Dict[str, List[str]] = {
            "premier": [],
            "division1": [],
            "division2": [],
            "division3": []
        }
        self.agent_stats: Dict[str, AgentStats] = {}

        # Setup logging
        self.logger = logging.getLogger("Tournament")
        self._setup_logging()

    def _setup_logging(self):
        """Configure tournament logging"""
        log_file = self.root_dir / "tournament.log"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    async def create_tournament(self, config: TournamentConfig) -> str:
        """Create a new tournament"""
        tournament_id = f"{config.name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

        # Create tournament directory
        tournament_dir = self.root_dir / tournament_id
        tournament_dir.mkdir()

        # Save configuration
        config_file = tournament_dir / "config.json"
        with open(config_file, "w") as f:
            json.dump(asdict(config), f, indent=2)

        self.active_tournament = tournament_id
        self.logger.info(f"Created tournament: {tournament_id}")

        return tournament_id

    async def run_tournament(self, tournament_id: str):
        """Run a complete tournament"""
        tournament_dir = self.root_dir / tournament_id
        if not tournament_dir.exists():
            raise ValueError(f"Tournament {tournament_id} not found")

        # Load configuration
        config_file = tournament_dir / "config.json"
        with open(config_file) as f:
            config = TournamentConfig(**json.load(f))

        self.logger.info(f"Starting tournament: {tournament_id}")

        # Run rounds
        for round_num in range(1, config.rounds + 1):
            self.logger.info(f"Starting round {round_num}")

            # Generate matches
            matches = self._generate_matches(config)

            # Run matches
            results = []
            for match in matches:
                result = await self._run_match(
                    tournament_id,
                    round_num,
                    match,
                    config
                )
                results.append(result)

            # Update rankings
            await self._update_rankings(results)

            # Save round results
            round_file = tournament_dir / f"round_{round_num}.jsonl"
            with open(round_file, "w") as f:
                for result in results:
                    f.write(json.dumps(asdict(result)) + "\n")

            # Generate round analytics
            await self._generate_round_analytics(
                tournament_id,
                round_num,
                results
            )

        # Tournament completion
        await self._complete_tournament(tournament_id)

    async def _run_match(
        self,
        tournament_id: str,
        round_num: int,
        match: tuple,
        config: TournamentConfig
    ) -> MatchResult:
        """Run a single tournament match"""
        agent1_id, agent2_id = match
        self.logger.info(f"Match: {agent1_id} vs {agent2_id}")

        start_time = datetime.utcnow()

        # Run game for both agents
        result1 = await self.game_controller.start_game(
            config.game_type,
            "tournament",
            agent1_id
        )
        result2 = await self.game_controller.start_game(
            config.game_type,
            "tournament",
            agent2_id
        )

        duration = (datetime.utcnow() - start_time).total_seconds()

        # Determine winner
        if result1.score > result2.score:
            winner_id = agent1_id
            mesh_earned = result1.mesh_factor * config.mesh_multiplier
        elif result2.score > result1.score:
            winner_id = agent2_id
            mesh_earned = result2.mesh_factor * config.mesh_multiplier
        else:
            # Tie - both get partial mesh
            winner_id = None
            mesh_earned = (
                (result1.mesh_factor + result2.mesh_factor)
                * config.mesh_multiplier
                * 0.5
            )

        return MatchResult(
            tournament_id=tournament_id,
            round_number=round_num,
            match_id=f"{tournament_id}_R{round_num}_M{agent1_id}_{agent2_id}",
            agent1_id=agent1_id,
            agent2_id=agent2_id,
            winner_id=winner_id,
            score1=result1.score,
            score2=result2.score,
            duration=duration,
            mesh_earned=mesh_earned,
            timestamp=datetime.utcnow().isoformat()
        )

    def _generate_matches(self, config: TournamentConfig) -> List[tuple]:
        """Generate matches for tournament round"""
        matches = []

        # Generate within-league matches
        for league, agents in self.league_rankings.items():
            if len(agents) < 2:
                continue

            # Randomize order for pairings
            np.random.shuffle(agents)

            # Create pairings
            for i in range(0, len(agents) - 1, 2):
                if len(matches) >= config.matches_per_round:
                    break
                matches.append((agents[i], agents[i + 1]))

        # Fill remaining slots with cross-league matches
        while len(matches) < config.matches_per_round:
            # Select random leagues and agents
            league1, league2 = np.random.choice(
                list(self.league_rankings.keys()),
                size=2,
                replace=False
            )
            if not (self.league_rankings[league1] and self.league_rankings[league2]):
                continue

            agent1 = np.random.choice(self.league_rankings[league1])
            agent2 = np.random.choice(self.league_rankings[league2])
            matches.append((agent1, agent2))

        return matches

    async def _update_rankings(self, results: List[MatchResult]):
        """Update rankings based on match results"""
        # Update agent stats
        for result in results:
            # Update agent 1
            if result.agent1_id not in self.agent_stats:
                self._initialize_agent(result.agent1_id)
            stats1 = self.agent_stats[result.agent1_id]
            stats1.matches_played += 1
            stats1.total_score += result.score1
            if result.winner_id == result.agent1_id:
                stats1.matches_won += 1
                stats1.mesh_earned += result.mesh_earned

            # Update agent 2
            if result.agent2_id not in self.agent_stats:
                self._initialize_agent(result.agent2_id)
            stats2 = self.agent_stats[result.agent2_id]
            stats2.matches_played += 1
            stats2.total_score += result.score2
            if result.winner_id == result.agent2_id:
                stats2.matches_won += 1
                stats2.mesh_earned += result.mesh_earned

            # Update derived stats
            for stats in [stats1, stats2]:
                stats.win_rate = stats.matches_won / stats.matches_played
                stats.avg_score = stats.total_score / stats.matches_played

        # Rerank agents within leagues
        for league in self.league_rankings:
            agents = self.league_rankings[league]
            agents.sort(
                key=lambda x: (
                    self.agent_stats[x].win_rate,
                    self.agent_stats[x].avg_score
                ),
                reverse=True
            )

            # Update ranks
            for rank, agent_id in enumerate(agents, 1):
                self.agent_stats[agent_id].rank = rank
                self.agent_stats[agent_id].peak_rank = min(
                    rank,
                    self.agent_stats[agent_id].peak_rank
                )

    def _initialize_agent(self, agent_id: str):
        """Initialize a new agent in the ranking system"""
        # Start in lowest division
        league = "division3"
        self.league_rankings[league].append(agent_id)
        rank = len(self.league_rankings[league])

        self.agent_stats[agent_id] = AgentStats(
            agent_id=agent_id,
            league=league,
            rank=rank,
            matches_played=0,
            matches_won=0,
            total_score=0.0,
            mesh_earned=0.0,
            win_rate=0.0,
            avg_score=0.0,
            peak_rank=rank
        )

    async def _generate_round_analytics(
        self,
        tournament_id: str,
        round_num: int,
        results: List[MatchResult]
    ):
        """Generate analytics for a tournament round"""
        tournament_dir = self.root_dir / tournament_id
        analytics_dir = tournament_dir / "analytics"
        analytics_dir.mkdir(exist_ok=True)

        # Prepare data
        scores = []
        durations = []
        mesh_earned = []
        for result in results:
            scores.extend([result.score1, result.score2])
            durations.append(result.duration)
            mesh_earned.append(result.mesh_earned)

        # Calculate statistics
        stats = {
            "round": round_num,
            "matches": len(results),
            "scores": {
                "mean": np.mean(scores),
                "std": np.std(scores),
                "min": np.min(scores),
                "max": np.max(scores)
            },
            "duration": {
                "mean": np.mean(durations),
                "std": np.std(durations),
                "total": np.sum(durations)
            },
            "mesh": {
                "total": np.sum(mesh_earned),
                "mean": np.mean(mesh_earned)
            }
        }

        # Save analytics
        analytics_file = analytics_dir / f"round_{round_num}_analytics.json"
        with open(analytics_file, "w") as f:
            json.dump(stats, f, indent=2)

        # Generate visualizations
        await self._generate_round_plots(
            tournament_id,
            round_num,
            results
        )

    async def _generate_round_plots(
        self,
        tournament_id: str,
        round_num: int,
        results: List[MatchResult]
    ):
        """Generate visualization plots for round analytics"""
        import matplotlib.pyplot as plt
        import seaborn as sns

        tournament_dir = self.root_dir / tournament_id
        plots_dir = tournament_dir / "plots"
        plots_dir.mkdir(exist_ok=True)

        # Score distribution
        plt.figure(figsize=(10, 6))
        scores = [(r.score1, r.score2) for r in results]
        sns.histplot(scores, bins=20)
        plt.title(f"Score Distribution - Round {round_num}")
        plt.xlabel("Score")
        plt.ylabel("Count")
        plt.savefig(plots_dir / f"round_{round_num}_scores.png")
        plt.close()

        # Win rates by league
        plt.figure(figsize=(12, 6))
        league_wins = {league: [] for league in self.league_rankings}
        for agent_id, stats in self.agent_stats.items():
            league_wins[stats.league].append(stats.win_rate)

        sns.boxplot(data=[
            (league, rate)
            for league, rates in league_wins.items()
            for rate in rates
        ])
        plt.title(f"Win Rates by League - Round {round_num}")
        plt.xlabel("League")
        plt.ylabel("Win Rate")
        plt.savefig(plots_dir / f"round_{round_num}_winrates.png")
        plt.close()

        # Mesh earnings
        plt.figure(figsize=(10, 6))
        sns.histplot([r.mesh_earned for r in results], bins=20)
        plt.title(f"Mesh Earnings Distribution - Round {round_num}")
        plt.xlabel("Mesh Earned")
        plt.ylabel("Count")
        plt.savefig(plots_dir / f"round_{round_num}_mesh.png")
        plt.close()

    async def _complete_tournament(self, tournament_id: str):
        """Handle tournament completion"""
        self.logger.info(f"Completing tournament: {tournament_id}")

        tournament_dir = self.root_dir / tournament_id

        # Generate final rankings
        rankings = {
            league: [
                {
                    "agent_id": agent_id,
                    "stats": asdict(self.agent_stats[agent_id])
                }
                for agent_id in agents
            ]
            for league, agents in self.league_rankings.items()
        }

        # Save final rankings
        rankings_file = tournament_dir / "final_rankings.json"
        with open(rankings_file, "w") as f:
            json.dump(rankings, f, indent=2)

        # Handle promotions/relegations
        await self._handle_league_transitions()

        # Backup agent states
        await self.backup_orchestrator.backup_all_agents()

        # Reset tournament state
        self.active_tournament = None

    async def _handle_league_transitions(self):
        """Handle promotions and relegations between leagues"""
        config = self._get_active_config()

        # Process promotions (bottom to top)
        leagues = list(self.league_rankings.keys())
        for i in range(len(leagues) - 1, 0, -1):
            lower_league = leagues[i]
            upper_league = leagues[i - 1]

            # Calculate number of promotions
            promote_count = int(
                len(self.league_rankings[lower_league])
                * config.league_promotion_rate
            )

            # Get top performers from lower league
            promotions = self.league_rankings[lower_league][:promote_count]

            # Update league assignments
            for agent_id in promotions:
                self.league_rankings[lower_league].remove(agent_id)
                self.league_rankings[upper_league].append(agent_id)
                self.agent_stats[agent_id].league = upper_league

        # Process relegations (top to bottom)
        for i in range(len(leagues) - 1):
            upper_league = leagues[i]
            lower_league = leagues[i + 1]

            # Calculate number of relegations
            relegate_count = int(
                len(self.league_rankings[upper_league])
                * config.league_relegation_rate
            )

            # Get bottom performers from upper league
            relegations = self.league_rankings[upper_league][-relegate_count:]

            # Update league assignments
            for agent_id in relegations:
                self.league_rankings[upper_league].remove(agent_id)
                self.league_rankings[lower_league].append(agent_id)
                self.agent_stats[agent_id].league = lower_league

    def _get_active_config(self) -> TournamentConfig:
        """Get configuration for active tournament"""
        if not self.active_tournament:
            raise ValueError("No active tournament")

        config_file = self.root_dir / self.active_tournament / "config.json"
        with open(config_file) as f:
            return TournamentConfig(**json.load(f))
