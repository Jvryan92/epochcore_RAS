"""
Game Analytics and Visualization System
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from game_replay import ReplayManager


class GameAnalytics:
    def __init__(self, replay_manager: ReplayManager):
        self.replay_manager = replay_manager
        self.output_dir = Path("data/analytics")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def generate_agent_report(self, agent_id: str, days: int = 7):
        """Generate comprehensive agent performance report"""
        perf = await self.replay_manager.get_agent_performance(agent_id, days)

        if perf["games_played"] == 0:
            return {"status": "no_data"}

        # Convert performances to DataFrame
        df = pd.DataFrame(perf["performances"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Generate plots
        self._plot_score_progression(df, agent_id)
        self._plot_efficiency_distribution(df, agent_id)
        self._plot_mesh_accumulation(df, agent_id)

        # Calculate improvement trends
        trends = self._calculate_trends(df)

        return {
            "status": "success",
            "summary": {
                "total_games": perf["games_played"],
                "date_range": perf["date_range"],
                "score_improvement": trends["score_trend"],
                "efficiency_improvement": trends["efficiency_trend"],
                "total_mesh": perf["mesh_stats"]["total"]
            },
            "plots": {
                "score": f"data/analytics/{agent_id}_score_progression.png",
                "efficiency": f"data/analytics/{agent_id}_efficiency_dist.png",
                "mesh": f"data/analytics/{agent_id}_mesh_accumulation.png"
            }
        }

    def _plot_score_progression(self, df: pd.DataFrame, agent_id: str):
        """Plot score progression over time"""
        plt.figure(figsize=(12, 6))
        sns.scatterplot(data=df, x="timestamp", y="score")
        sns.regplot(data=df, x="timestamp", y="score", scatter=False)
        plt.title(f"Score Progression - Agent {agent_id}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{agent_id}_score_progression.png")
        plt.close()

    def _plot_efficiency_distribution(self, df: pd.DataFrame, agent_id: str):
        """Plot efficiency distribution"""
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x="efficiency", bins=20)
        plt.title(f"Efficiency Distribution - Agent {agent_id}")
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{agent_id}_efficiency_dist.png")
        plt.close()

    def _plot_mesh_accumulation(self, df: pd.DataFrame, agent_id: str):
        """Plot mesh factor accumulation"""
        plt.figure(figsize=(12, 6))
        df = df.sort_values("timestamp")
        df["cumulative_mesh"] = df["mesh_factor"].cumsum()
        plt.plot(df["timestamp"], df["cumulative_mesh"])
        plt.title(f"Cumulative Mesh Accumulation - Agent {agent_id}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{agent_id}_mesh_accumulation.png")
        plt.close()

    def _calculate_trends(self, df: pd.DataFrame) -> Dict:
        """Calculate improvement trends"""
        first_week = df.head(7)
        last_week = df.tail(7)

        return {
            "score_trend": (
                last_week["score"].mean() - first_week["score"].mean()
            ) / first_week["score"].mean() * 100,
            "efficiency_trend": (
                last_week["efficiency"].mean() - first_week["efficiency"].mean()
            ) / first_week["efficiency"].mean() * 100
        }

    async def generate_game_insights(self, game_id: str, days: int = 7):
        """Generate insights for a specific game type"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        game_data = []

        # Collect all replays for this game
        for date_dir in self.replay_manager.base_path.iterdir():
            if not date_dir.is_dir():
                continue
            date = datetime.strptime(date_dir.name, "%Y-%m-%d")
            if date < cutoff:
                continue

            for replay_file in date_dir.glob(f"{game_id}_*.jsonl"):
                replay = await self.replay_manager.load_replay(replay_file)
                if replay.final_state:
                    game_data.append({
                        "agent_id": replay.agent_id,
                        "timestamp": replay.timestamp,
                        "score": replay.final_state.get("final_score", 0),
                        "efficiency": replay.final_state.get("efficiency", 0)
                    })

        if not game_data:
            return {"status": "no_data"}

        df = pd.DataFrame(game_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Generate game-specific visualizations
        self._plot_agent_comparison(df, game_id)
        self._plot_score_distribution(df, game_id)

        return {
            "status": "success",
            "summary": {
                "total_plays": len(game_data),
                "unique_agents": df["agent_id"].nunique(),
                "avg_score": df["score"].mean(),
                "avg_efficiency": df["efficiency"].mean()
            },
            "plots": {
                "comparison": f"data/analytics/{game_id}_agent_comparison.png",
                "distribution": f"data/analytics/{game_id}_score_dist.png"
            }
        }

    def _plot_agent_comparison(self, df: pd.DataFrame, game_id: str):
        """Plot agent performance comparison"""
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df, x="agent_id", y="score")
        plt.title(f"Agent Performance Comparison - {game_id}")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{game_id}_agent_comparison.png")
        plt.close()

    def _plot_score_distribution(self, df: pd.DataFrame, game_id: str):
        """Plot score distribution for game"""
        plt.figure(figsize=(10, 6))
        sns.kdeplot(data=df, x="score", hue="agent_id")
        plt.title(f"Score Distribution by Agent - {game_id}")
        plt.tight_layout()
        plt.savefig(self.output_dir / f"{game_id}_score_dist.png")
        plt.close()
