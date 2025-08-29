"""
Agent Supervision and Orchestration System
Provides high-level monitoring, control, and emergency management for all agents.
"""

import asyncio
import json
import logging
import signal
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import psutil

from agent_backup import AgentBackupOrchestrator
from enhanced_game_controller import EnhancedGameController
from game_analytics import GameAnalytics
from game_export import GameDataExport
from game_replay import ReplayManager
from game_streaming import GameStreamManager


@dataclass
class AgentHealth:
    agent_id: str
    status: str  # active, paused, error, recovering
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    last_backup: str
    games_completed: int
    uptime: float


@dataclass
class SystemMetrics:
    total_agents: int
    active_agents: int
    total_games: int
    system_load: float
    memory_usage: float
    backup_status: str
    error_count: int


class AgentSupervisor:
    def __init__(self, config_path: Optional[str] = None):
        self.root_dir = Path("data/supervisor")
        self.root_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config(config_path)

        # Initialize components
        self.game_controller = EnhancedGameController()
        self.stream_manager = GameStreamManager()
        self.replay_manager = ReplayManager()
        self.analytics = GameAnalytics(self.replay_manager)
        self.backup_orchestrator = AgentBackupOrchestrator()

        # Monitoring state
        self.agent_health: Dict[str, AgentHealth] = {}
        self.system_metrics = SystemMetrics(
            total_agents=0,
            active_agents=0,
            total_games=0,
            system_load=0.0,
            memory_usage=0.0,
            backup_status="unknown",
            error_count=0
        )

        # Emergency recovery state
        self.recovery_mode = False
        self.recovery_agents = set()

        # Setup logging
        self.logger = logging.getLogger("AgentSupervisor")
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging with rotating file handler"""
        from logging.handlers import RotatingFileHandler

        log_file = self.root_dir / "supervisor.log"
        handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load supervisor configuration"""
        default_config = {
            "health_check_interval": 60,  # seconds
            "backup_interval": 3600,  # seconds
            "max_memory_percent": 85,
            "max_cpu_percent": 90,
            "error_threshold": 0.1,
            "response_time_threshold": 2.0,
            "recovery_timeout": 300,  # seconds
            "alert_thresholds": {
                "memory": 80,
                "cpu": 85,
                "error_rate": 0.05,
                "response_time": 1.5
            }
        }

        if config_path:
            try:
                with open(config_path) as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}")

        return default_config

    async def start(self):
        """Start the supervisor"""
        self.logger.info("Starting Agent Supervisor")
        self.running = True

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        try:
            # Start monitoring tasks
            monitoring_task = asyncio.create_task(self._monitor_loop())
            backup_task = asyncio.create_task(self._backup_loop())

            # Wait for shutdown signal
            while self.running:
                await asyncio.sleep(1)

            # Cleanup
            monitoring_task.cancel()
            backup_task.cancel()
            await self._shutdown()

        except Exception as e:
            self.logger.error(f"Supervisor error: {e}")
            await self._emergency_shutdown()

    async def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Update system metrics
                await self._update_system_metrics()

                # Check agent health
                for agent_id in await self._get_active_agents():
                    await self._check_agent_health(agent_id)

                # Handle any recoveries
                await self._handle_recoveries()

                # Export monitoring data
                await self._export_metrics()

                await asyncio.sleep(self.config["health_check_interval"])

            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await self._handle_monitoring_error()

    async def _backup_loop(self):
        """Periodic backup loop"""
        while self.running:
            try:
                self.logger.info("Starting scheduled backup")
                result = await self.backup_orchestrator.backup_all_agents()

                if result["failed"] > 0:
                    self.logger.warning(
                        f"Backup completed with {result['failed']} failures"
                    )
                else:
                    self.logger.info("Backup completed successfully")

                self.system_metrics.backup_status = "success"
                await asyncio.sleep(self.config["backup_interval"])

            except Exception as e:
                self.logger.error(f"Backup error: {e}")
                self.system_metrics.backup_status = "error"
                await asyncio.sleep(300)  # Retry in 5 minutes

    async def _check_agent_health(self, agent_id: str):
        """Check health metrics for an agent"""
        try:
            # Get process metrics
            process = psutil.Process()  # This should be agent specific
            cpu = process.cpu_percent()
            memory = process.memory_percent()

            # Get agent metrics
            metrics = await self._get_agent_metrics(agent_id)

            health = AgentHealth(
                agent_id=agent_id,
                status="active",
                cpu_usage=cpu,
                memory_usage=memory,
                response_time=metrics["response_time"],
                error_rate=metrics["error_rate"],
                last_backup=metrics["last_backup"],
                games_completed=metrics["games_completed"],
                uptime=metrics["uptime"]
            )

            # Check for concerning metrics
            if (
                cpu > self.config["alert_thresholds"]["cpu"] or
                memory > self.config["alert_thresholds"]["memory"] or
                metrics["error_rate"] > self.config["alert_thresholds"]["error_rate"] or
                metrics["response_time"] > self.config["alert_thresholds"]["response_time"]
            ):
                await self._handle_agent_alert(agent_id, health)

            self.agent_health[agent_id] = health

        except Exception as e:
            self.logger.error(f"Health check failed for {agent_id}: {e}")
            await self._handle_agent_error(agent_id)

    async def _handle_agent_alert(self, agent_id: str, health: AgentHealth):
        """Handle agent alerts"""
        self.logger.warning(f"Alert for agent {agent_id}:")
        self.logger.warning(f"CPU: {health.cpu_usage:.1f}%")
        self.logger.warning(f"Memory: {health.memory_usage:.1f}%")
        self.logger.warning(f"Error Rate: {health.error_rate:.3f}")
        self.logger.warning(f"Response Time: {health.response_time:.2f}s")

        # Implement automated responses here
        if health.error_rate > self.config["error_threshold"]:
            await self._pause_agent(agent_id)

    async def _handle_agent_error(self, agent_id: str):
        """Handle agent errors"""
        self.logger.error(f"Agent {agent_id} encountered an error")
        self.system_metrics.error_count += 1

        if agent_id not in self.recovery_agents:
            self.recovery_agents.add(agent_id)
            await self._initiate_recovery(agent_id)

    async def _initiate_recovery(self, agent_id: str):
        """Start recovery process for an agent"""
        self.logger.info(f"Initiating recovery for agent {agent_id}")

        try:
            # Backup current state
            await self.backup_orchestrator.backup_agent(agent_id)

            # Reset agent state
            await self._reset_agent(agent_id)

            # Restore from last known good backup
            last_good_backup = await self._find_last_good_backup(agent_id)
            if last_good_backup:
                await self.backup_orchestrator.restore_agent(
                    agent_id,
                    last_good_backup
                )

            self.logger.info(f"Recovery completed for {agent_id}")
            self.recovery_agents.remove(agent_id)

        except Exception as e:
            self.logger.error(f"Recovery failed for {agent_id}: {e}")
            await self._handle_recovery_failure(agent_id)

    async def _export_metrics(self):
        """Export monitoring data"""
        timestamp = datetime.utcnow().isoformat()
        metrics_file = self.root_dir / "metrics" / f"{timestamp}_metrics.json"
        metrics_file.parent.mkdir(exist_ok=True)

        metrics = {
            "timestamp": timestamp,
            "system": asdict(self.system_metrics),
            "agents": {
                agent_id: asdict(health)
                for agent_id, health in self.agent_health.items()
            }
        }

        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

    async def _update_system_metrics(self):
        """Update system-wide metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent

            # Update system metrics
            self.system_metrics.system_load = cpu_percent
            self.system_metrics.memory_usage = memory_percent
            self.system_metrics.active_agents = len(self.agent_health)

            # Check system health
            if (
                cpu_percent > self.config["max_cpu_percent"] or
                memory_percent > self.config["max_memory_percent"]
            ):
                await self._handle_system_overload()

        except Exception as e:
            self.logger.error(f"Failed to update system metrics: {e}")

    async def _handle_system_overload(self):
        """Handle system resource overload"""
        self.logger.warning("System resources critical!")

        # Pause non-critical agents
        active_agents = list(self.agent_health.keys())
        for agent_id in active_agents:
            if not await self._is_critical_agent(agent_id):
                await self._pause_agent(agent_id)

    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signal"""
        self.logger.info("Shutdown signal received")
        self.running = False

    async def _shutdown(self):
        """Clean shutdown"""
        self.logger.info("Starting clean shutdown")

        # Backup all agents
        await self.backup_orchestrator.backup_all_agents()

        # Stop all agents
        for agent_id in list(self.agent_health.keys()):
            await self._pause_agent(agent_id)

        self.logger.info("Shutdown complete")

    async def _emergency_shutdown(self):
        """Emergency shutdown procedure"""
        self.logger.error("Emergency shutdown initiated")

        try:
            # Quick backup of critical agents
            critical_agents = [
                agent_id
                for agent_id in self.agent_health
                if await self._is_critical_agent(agent_id)
            ]

            for agent_id in critical_agents:
                await self.backup_orchestrator.backup_agent(agent_id)

            # Force stop all agents
            for agent_id in list(self.agent_health.keys()):
                await self._force_stop_agent(agent_id)

        except Exception as e:
            self.logger.error(f"Emergency shutdown error: {e}")

        finally:
            self.logger.error("Emergency shutdown complete")

    async def _get_agent_metrics(self, agent_id: str) -> Dict:
        """Get detailed metrics for an agent"""
        # This is a placeholder - implement based on your metrics collection
        return {
            "response_time": np.random.normal(1.0, 0.2),
            "error_rate": np.random.beta(1, 20),
            "last_backup": (
                datetime.utcnow() - timedelta(hours=1)
            ).isoformat(),
            "games_completed": np.random.randint(10, 100),
            "uptime": np.random.uniform(3600, 86400)
        }

    async def _get_active_agents(self) -> List[str]:
        """Get list of all active agents"""
        # This is a placeholder - implement based on your agent management
        return list(self.agent_health.keys())

    async def _is_critical_agent(self, agent_id: str) -> bool:
        """Determine if an agent is critical"""
        # This is a placeholder - implement based on your criteria
        return False

    async def _pause_agent(self, agent_id: str):
        """Pause an agent"""
        self.logger.info(f"Pausing agent {agent_id}")
        if agent_id in self.agent_health:
            self.agent_health[agent_id].status = "paused"

    async def _force_stop_agent(self, agent_id: str):
        """Force stop an agent"""
        self.logger.warning(f"Force stopping agent {agent_id}")
        if agent_id in self.agent_health:
            self.agent_health[agent_id].status = "stopped"

    async def _reset_agent(self, agent_id: str):
        """Reset agent to initial state"""
        self.logger.info(f"Resetting agent {agent_id}")
        if agent_id in self.agent_health:
            self.agent_health[agent_id].status = "resetting"

    async def _find_last_good_backup(self, agent_id: str) -> Optional[str]:
        """Find last known good backup for an agent"""
        # This is a placeholder - implement based on your backup system
        return None

    async def _handle_recovery_failure(self, agent_id: str):
        """Handle failed recovery attempt"""
        self.logger.error(f"Recovery failed for agent {agent_id}")
        # Implement escalation procedures here
