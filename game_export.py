"""
Game Data Export System
"""

import json
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

import pandas as pd

from game_analytics import GameAnalytics
from game_replay import ReplayManager


class GameDataExport:
    def __init__(
        self,
        replay_manager: ReplayManager,
        analytics: GameAnalytics,
        export_dir: str = "data/exports"
    ):
        self.replay_manager = replay_manager
        self.analytics = analytics
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def export_daily_summary(self, date: str) -> Dict:
        """Export daily game data summary"""
        date_path = self.replay_manager.base_path / date
        if not date_path.exists():
            return {"status": "no_data"}

        summary_data = {
            "date": date,
            "games": {},
            "agents": {},
            "total_games": 0,
            "total_mesh": 0
        }

        # Process all games for the day
        for replay_file in date_path.glob("*.jsonl"):
            replay = await self.replay_manager.load_replay(replay_file)
            if not replay.final_state:
                continue

            game_id = replay.game_id
            agent_id = replay.agent_id

            # Update game stats
            summary_data["games"].setdefault(game_id, {
                "plays": 0,
                "total_score": 0,
                "total_mesh": 0
            })
            summary_data["games"][game_id]["plays"] += 1
            summary_data["games"][game_id]["total_score"] += replay.final_state.get(
                "final_score", 0
            )
            summary_data["games"][game_id]["total_mesh"] += replay.final_state.get(
                "mesh_factor", 0
            )

            # Update agent stats
            summary_data["agents"].setdefault(agent_id, {
                "games_played": 0,
                "total_score": 0,
                "total_mesh": 0
            })
            summary_data["agents"][agent_id]["games_played"] += 1
            summary_data["agents"][agent_id]["total_score"] += replay.final_state.get(
                "final_score", 0
            )
            summary_data["agents"][agent_id]["total_mesh"] += replay.final_state.get(
                "mesh_factor", 0
            )

            summary_data["total_games"] += 1
            summary_data["total_mesh"] += replay.final_state.get("mesh_factor", 0)

        # Export summary
        output_file = self.export_dir / f"{date}_summary.json"
        with open(output_file, "w") as f:
            json.dump(summary_data, f, indent=2)

        return {
            "status": "success",
            "file": str(output_file),
            "summary": summary_data
        }

    async def export_agent_archive(self, agent_id: str, days: int = 7) -> Dict:
        """Create comprehensive agent data archive"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Create temporary directory for archive contents
        temp_dir = self.export_dir / "temp" / agent_id
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Generate analytics report
        analytics_report = await self.analytics.generate_agent_report(agent_id, days)
        if analytics_report["status"] == "no_data":
            return {"status": "no_data"}

        # Copy analytics plots
        for plot_name, plot_path in analytics_report["plots"].items():
            src = Path(plot_path)
            if src.exists():
                dst = temp_dir / src.name
                dst.write_bytes(src.read_bytes())

        # Collect game replays
        replays = []
        for date_dir in self.replay_manager.base_path.iterdir():
            if not date_dir.is_dir():
                continue
            date = datetime.strptime(date_dir.name, "%Y-%m-%d")
            if date < cutoff:
                continue

            for replay_file in date_dir.glob(f"*_{agent_id}_*.jsonl"):
                replays.append(replay_file)
                dst = temp_dir / "replays" / replay_file.name
                dst.parent.mkdir(exist_ok=True)
                dst.write_text(replay_file.read_text())

        # Create performance CSV
        perf_data = []
        for replay_file in replays:
            replay = await self.replay_manager.load_replay(replay_file)
            if replay.final_state:
                perf_data.append({
                    "game_id": replay.game_id,
                    "timestamp": replay.timestamp,
                    "score": replay.final_state.get("final_score", 0),
                    "efficiency": replay.final_state.get("efficiency", 0),
                    "mesh_factor": replay.final_state.get("mesh_factor", 1.0)
                })

        if perf_data:
            df = pd.DataFrame(perf_data)
            df.to_csv(temp_dir / "performance.csv", index=False)

        # Create archive
        archive_name = f"{agent_id}_archive_{datetime.utcnow().strftime('%Y%m%d')}.zip"
        archive_path = self.export_dir / archive_name

        with zipfile.ZipFile(archive_path, "w") as zf:
            for file in temp_dir.rglob("*"):
                if file.is_file():
                    zf.write(file, file.relative_to(temp_dir))

        # Cleanup
        for file in temp_dir.rglob("*"):
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                file.rmdir()
        temp_dir.rmdir()

        return {
            "status": "success",
            "file": str(archive_path),
            "summary": {
                "replays": len(replays),
                "plots": len(analytics_report["plots"]),
                "date_range": f"{cutoff.date()} to {datetime.utcnow().date()}"
            }
        }

    async def export_game_insights(self, game_id: str, days: int = 7) -> Dict:
        """Export game-specific insights and data"""
        insights = await self.analytics.generate_game_insights(game_id, days)
        if insights["status"] == "no_data":
            return {"status": "no_data"}

        # Create game insights directory
        game_dir = self.export_dir / f"{game_id}_insights"
        game_dir.mkdir(exist_ok=True)

        # Copy visualization plots
        for plot_name, plot_path in insights["plots"].items():
            src = Path(plot_path)
            if src.exists():
                dst = game_dir / src.name
                dst.write_bytes(src.read_bytes())

        # Export summary
        summary_file = game_dir / "summary.json"
        with open(summary_file, "w") as f:
            json.dump(insights["summary"], f, indent=2)

        return {
            "status": "success",
            "directory": str(game_dir),
            "summary": insights["summary"]
        }
