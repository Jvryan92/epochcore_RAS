"""Epoch Evolution System - Time-based agent improvements"""

from datetime import datetime, timedelta
from typing import Dict, List

from omega_base import OmegaSubsystem


class EpochSystem(OmegaSubsystem):
    """Manages time-based improvements and historical tracking"""

    EPOCH_DURATIONS = {
        "Dawn": timedelta(hours=1),
        "Day": timedelta(days=1),
        "Week": timedelta(weeks=1),
        "Month": timedelta(days=30),
        "Season": timedelta(days=90),
        "Year": timedelta(days=365)
    }

    EVOLUTION_FACTORS = [
        "speed",
        "efficiency",
        "accuracy",
        "creativity",
        "reliability",
        "complexity"
    ]

    async def initialize_agent(self, agent_id: str) -> Dict:
        """Initialize epoch-based evolution"""
        state = {
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat(),
            "current_epoch": {
                "name": "Dawn",
                "started_at": datetime.utcnow().isoformat(),
                "evolution_factors": self._initialize_factors()
            },
            "epoch_history": [],
            "milestones": [],
            "temporal_score": 0
        }

        await self._save_state(agent_id, state)
        return state

    async def evolve_agent(self, agent_id: str) -> Dict:
        """Evolve agent through temporal progression"""
        state = await self._load_state(agent_id)
        if not state:
            raise ValueError(f"Agent {agent_id} not initialized")

        now = datetime.utcnow()
        current_epoch = state["current_epoch"]
        epoch_start = datetime.fromisoformat(current_epoch["started_at"])

        # Check for epoch completion
        completed_epoch = None
        new_epoch = None

        if self._should_advance_epoch(epoch_start, now, current_epoch["name"]):
            # Complete current epoch
            completed_epoch = self._complete_epoch(state, now)
            state["epoch_history"].append(completed_epoch)

            # Start new epoch
            new_epoch = self._start_new_epoch(state, now)
            state["current_epoch"] = new_epoch

        # Evolve current factors
        factor_changes = self._evolve_factors(
            state["current_epoch"]["evolution_factors"],
            epoch_start,
            now
        )
        state["current_epoch"]["evolution_factors"].update(factor_changes)

        # Update temporal score
        temporal_gain = self._calculate_temporal_gain(state, now)
        state["temporal_score"] += temporal_gain

        # Check for milestones
        new_milestones = self._check_milestones(state)
        state["milestones"].extend(new_milestones)

        # Save state
        await self._save_state(agent_id, state)

        return {
            "completed_epoch": completed_epoch,
            "new_epoch": new_epoch,
            "factor_changes": factor_changes,
            "temporal_gain": temporal_gain,
            "new_milestones": new_milestones
        }

    def _initialize_factors(self) -> Dict[str, float]:
        """Initialize evolution factors"""
        return {factor: 0.1 for factor in self.EVOLUTION_FACTORS}

    def _should_advance_epoch(
        self,
        start: datetime,
        now: datetime,
        epoch_name: str
    ) -> bool:
        """Determine if epoch should advance"""
        duration = self.EPOCH_DURATIONS[epoch_name]
        return (now - start) >= duration

    def _complete_epoch(self, state: Dict, now: datetime) -> Dict:
        """Complete current epoch and calculate results"""
        current = state["current_epoch"]
        return {
            "name": current["name"],
            "started_at": current["started_at"],
            "completed_at": now.isoformat(),
            "final_factors": current["evolution_factors"].copy(),
            "achievements": []  # TODO: Add epoch-specific achievements
        }

    def _start_new_epoch(self, state: Dict, now: datetime) -> Dict:
        """Start a new epoch"""
        current_name = state["current_epoch"]["name"]
        new_name = self._next_epoch_name(current_name)

        return {
            "name": new_name,
            "started_at": now.isoformat(),
            "evolution_factors": self._evolve_epoch_factors(
                state["current_epoch"]["evolution_factors"]
            )
        }

    def _next_epoch_name(self, current: str) -> str:
        """Determine next epoch name"""
        sequence = list(self.EPOCH_DURATIONS.keys())
        try:
            idx = sequence.index(current)
            return sequence[idx + 1]
        except (ValueError, IndexError):
            return sequence[0]  # Restart from beginning

    def _evolve_factors(
        self,
        factors: Dict[str, float],
        start: datetime,
        now: datetime
    ) -> Dict[str, float]:
        """Evolve factors based on time passed"""
        import random

        time_factor = (now - start).total_seconds() / 86400  # Days
        changes = {}

        for factor, value in factors.items():
            # Base change based on time
            base_change = time_factor * 0.01

            # Random variation
            variation = random.uniform(-0.005, 0.015)

            # Calculate new value
            new_value = min(1.0, value + base_change + variation)
            if new_value != value:
                changes[factor] = new_value

        return changes

    def _evolve_epoch_factors(self, factors: Dict[str, float]) -> Dict[str, float]:
        """Evolve factors for new epoch"""
        import random

        new_factors = {}
        for factor, value in factors.items():
            # Retain 80-90% of progress
            retention = random.uniform(0.8, 0.9)
            new_factors[factor] = value * retention

        return new_factors

    def _calculate_temporal_gain(self, state: Dict, now: datetime) -> int:
        """Calculate temporal score gain"""
        # Base gain from current epoch
        current = state["current_epoch"]
        epoch_time = (
            now - datetime.fromisoformat(current["started_at"])).total_seconds()
        base_gain = epoch_time / 3600  # Points per hour

        # Factor bonus
        factor_avg = sum(current["evolution_factors"].values()
                         ) / len(current["evolution_factors"])
        factor_bonus = factor_avg * 100

        # History bonus
        history_bonus = len(state["epoch_history"]) * 50

        return int(base_gain + factor_bonus + history_bonus)

    def _check_milestones(self, state: Dict) -> List[Dict]:
        """Check for new milestones"""
        new_milestones = []

        # Epoch count milestones
        epoch_count = len(state["epoch_history"])
        if epoch_count == 1 and "FirstEpoch" not in [m["id"] for m in state["milestones"]]:
            new_milestones.append({
                "id": "FirstEpoch",
                "name": "First Epoch Completion",
                "achieved_at": datetime.utcnow().isoformat()
            })

        # Factor milestones
        factors = state["current_epoch"]["evolution_factors"]
        for factor, value in factors.items():
            if value >= 0.5:
                milestone_id = f"{factor}Mastery"
                if milestone_id not in [m["id"] for m in state["milestones"]]:
                    new_milestones.append({
                        "id": milestone_id,
                        "name": f"{factor.title()} Mastery",
                        "achieved_at": datetime.utcnow().isoformat()
                    })

        # Temporal score milestones
        score = state["temporal_score"]
        for threshold in [1000, 5000, 10000, 50000]:
            if score >= threshold:
                milestone_id = f"Score{threshold}"
                if milestone_id not in [m["id"] for m in state["milestones"]]:
                    new_milestones.append({
                        "id": milestone_id,
                        "name": f"Temporal Score {threshold}",
                        "achieved_at": datetime.utcnow().isoformat()
                    })

        return new_milestones
