"""
Agent Data Backup and Synchronization System
"""

import asyncio
import json
import logging
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from enhanced_game_controller import EnhancedGameController
from game_analytics import GameAnalytics
from game_export import GameDataExport
from game_replay import ReplayManager
from game_streaming import GameStreamManager


class AgentBackupOrchestrator:
    def __init__(self, root_dir: str = "data/agent_backups"):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.game_controller = EnhancedGameController()
        self.stream_manager = GameStreamManager()
        self.replay_manager = ReplayManager()
        self.analytics = GameAnalytics(self.replay_manager)
        self.exporter = GameDataExport(self.replay_manager, self.analytics)

        # Setup logging
        self.logger = logging.getLogger("AgentBackup")
        self.logger.setLevel(logging.INFO)

    async def backup_agent(self, agent_id: str) -> Dict:
        """Create comprehensive backup for an agent"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.root_dir / f"{agent_id}_{timestamp}"
        backup_dir.mkdir(parents=True)

        try:
            # 1. Export agent archive with replay data
            archive = await self.exporter.export_agent_archive(agent_id)
            if archive["status"] == "success":
                shutil.copy2(archive["file"], backup_dir / "replays.zip")

            # 2. Export analytics
            analytics_report = await self.analytics.generate_agent_report(agent_id)
            if analytics_report["status"] == "success":
                for plot_name, plot_path in analytics_report["plots"].items():
                    shutil.copy2(plot_path, backup_dir / f"{plot_name}.png")

                with open(backup_dir / "analytics.json", "w") as f:
                    json.dump(analytics_report["summary"], f, indent=2)

            # 3. Backup game states
            game_states = await self._collect_game_states(agent_id)
            with open(backup_dir / "game_states.json", "w") as f:
                json.dump(game_states, f, indent=2)

            # 4. Create manifest
            manifest = {
                "agent_id": agent_id,
                "timestamp": timestamp,
                "contents": {
                    "replays": bool(archive["status"] == "success"),
                    "analytics": bool(analytics_report["status"] == "success"),
                    "game_states": len(game_states)
                }
            }
            with open(backup_dir / "manifest.json", "w") as f:
                json.dump(manifest, f, indent=2)

            # 5. Create compressed archive
            archive_path = self.root_dir / f"{agent_id}_{timestamp}.zip"
            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file in backup_dir.rglob("*"):
                    if file.is_file():
                        zf.write(file, file.relative_to(backup_dir))

            # Cleanup temporary directory
            shutil.rmtree(backup_dir)

            return {
                "status": "success",
                "agent_id": agent_id,
                "timestamp": timestamp,
                "archive": str(archive_path),
                "manifest": manifest
            }

        except Exception as e:
            self.logger.error(f"Backup failed for agent {agent_id}: {str(e)}")
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": str(e)
            }

    async def backup_all_agents(self) -> Dict:
        """Backup all agents"""
        # Get list of all agents
        agents = await self._get_active_agents()
        results = {}

        for agent_id in agents:
            results[agent_id] = await self.backup_agent(agent_id)

        # Create backup summary
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        summary = {
            "timestamp": timestamp,
            "total_agents": len(agents),
            "successful": sum(1 for r in results.values() if r["status"] == "success"),
            "failed": sum(1 for r in results.values() if r["status"] == "error"),
            "results": results
        }

        summary_path = self.root_dir / f"backup_summary_{timestamp}.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)

        return summary

    async def verify_backup(self, agent_id: str, timestamp: str) -> Dict:
        """Verify integrity of an agent backup"""
        archive_path = self.root_dir / f"{agent_id}_{timestamp}.zip"
        if not archive_path.exists():
            return {"status": "error", "error": "Backup archive not found"}

        try:
            # Create temporary directory for verification
            verify_dir = self.root_dir / "verify" / f"{agent_id}_{timestamp}"
            verify_dir.mkdir(parents=True)

            # Extract archive
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(verify_dir)

            # Check manifest
            manifest_path = verify_dir / "manifest.json"
            if not manifest_path.exists():
                raise ValueError("Manifest file missing")

            with open(manifest_path) as f:
                manifest = json.load(f)

            # Verify contents
            verification = {
                "manifest_valid": True,
                "replays_valid": False,
                "analytics_valid": False,
                "game_states_valid": False
            }

            if manifest["contents"]["replays"]:
                verification["replays_valid"] = (verify_dir / "replays.zip").exists()

            if manifest["contents"]["analytics"]:
                verification["analytics_valid"] = (
                    verify_dir / "analytics.json").exists()

            verification["game_states_valid"] = (
                verify_dir / "game_states.json"
            ).exists()

            # Cleanup
            shutil.rmtree(verify_dir)

            return {
                "status": "success",
                "agent_id": agent_id,
                "timestamp": timestamp,
                "verification": verification,
                "manifest": manifest
            }

        except Exception as e:
            self.logger.error(f"Verification failed for {agent_id}: {str(e)}")
            if verify_dir.exists():
                shutil.rmtree(verify_dir)
            return {"status": "error", "error": str(e)}

    async def restore_agent(self, agent_id: str, timestamp: str) -> Dict:
        """Restore agent from backup"""
        archive_path = self.root_dir / f"{agent_id}_{timestamp}.zip"
        if not archive_path.exists():
            return {"status": "error", "error": "Backup archive not found"}

        try:
            # Verify backup first
            verification = await self.verify_backup(agent_id, timestamp)
            if verification["status"] != "success":
                raise ValueError("Backup verification failed")

            # Create temporary directory for restoration
            restore_dir = self.root_dir / "restore" / f"{agent_id}_{timestamp}"
            restore_dir.mkdir(parents=True)

            # Extract archive
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(restore_dir)

            # Restore game states
            game_states_path = restore_dir / "game_states.json"
            if game_states_path.exists():
                with open(game_states_path) as f:
                    game_states = json.load(f)
                await self._restore_game_states(agent_id, game_states)

            # Restore replays
            replays_path = restore_dir / "replays.zip"
            if replays_path.exists():
                with zipfile.ZipFile(replays_path, "r") as zf:
                    zf.extractall(self.stream_manager.base_path)

            # Cleanup
            shutil.rmtree(restore_dir)

            return {
                "status": "success",
                "agent_id": agent_id,
                "timestamp": timestamp,
                "restored_items": {
                    "game_states": bool(game_states_path.exists()),
                    "replays": bool(replays_path.exists())
                }
            }

        except Exception as e:
            self.logger.error(f"Restoration failed for {agent_id}: {str(e)}")
            if restore_dir.exists():
                shutil.rmtree(restore_dir)
            return {"status": "error", "error": str(e)}

    async def _get_active_agents(self) -> List[str]:
        """Get list of all active agents"""
        # Collect unique agent IDs from all data sources
        agent_ids = set()

        # From game streams
        for date_dir in self.stream_manager.base_path.iterdir():
            if date_dir.is_dir():
                for replay_file in date_dir.glob("*.jsonl"):
                    parts = replay_file.stem.split("_")
                    if len(parts) >= 2:
                        agent_ids.add(parts[1])

        return sorted(list(agent_ids))

    async def _collect_game_states(self, agent_id: str) -> Dict:
        """Collect all game states for an agent"""
        # This is a placeholder - implement based on your game state storage
        return {
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "states": {}  # Add actual game states here
        }

    async def _restore_game_states(self, agent_id: str, states: Dict):
        """Restore game states for an agent"""
        # This is a placeholder - implement based on your game state storage
        pass
