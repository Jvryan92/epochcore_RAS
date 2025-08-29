"""Battle League System - Tiered competitions and team formations"""

from datetime import datetime
from typing import Dict, List

from omega_base import OmegaSubsystem


class BattleLeagueSystem(OmegaSubsystem):
    """Manages tiered competitions, league promotions, and team formations"""

    LEAGUES = [
        "Bronze",
        "Silver",
        "Gold",
        "Platinum",
        "Diamond",
        "Master",
        "Grandmaster",
        "Legend"
    ]

    async def initialize_agent(self, agent_id: str) -> Dict:
        """Initialize an agent in the battle league system"""
        state = {
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat(),
            "league": "Bronze",
            "league_points": 0,
            "matches_played": 0,
            "wins": 0,
            "losses": 0,
            "teams": [],
            "current_team": None,
            "achievements": [],
            "season_history": []
        }
        await self._save_state(agent_id, state)
        return state

    async def evolve_agent(self, agent_id: str) -> Dict:
        """Evolve agent through league battles"""
        state = await self._load_state(agent_id)
        if not state:
            raise ValueError(f"Agent {agent_id} not initialized")

        # Simulate a match
        match_result = await self._run_match(agent_id)

        # Update match statistics
        state["matches_played"] += 1
        if match_result["victory"]:
            state["wins"] += 1
        else:
            state["losses"] += 1

        # Update league points
        points_change = self._calculate_points_change(
            match_result["performance"],
            match_result["victory"]
        )
        state["league_points"] += points_change

        # Check for promotion/demotion
        old_league = state["league"]
        state["league"] = self._calculate_league(state["league_points"])

        # Update season history if league changed
        if old_league != state["league"]:
            state["season_history"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "old_league": old_league,
                "new_league": state["league"],
                "points": state["league_points"]
            })

        # Check for team formation opportunities
        if self._should_form_team(state):
            new_team = await self._form_team(agent_id)
            if new_team:
                state["teams"].append(new_team)
                state["current_team"] = new_team["id"]

        # Check for new achievements
        new_achievements = self._check_achievements(state)
        state["achievements"].extend(new_achievements)

        # Save updated state
        await self._save_state(agent_id, state)

        return {
            "match_result": match_result,
            "points_change": points_change,
            "new_league": state["league"],
            "new_achievements": new_achievements,
            "new_team": new_team if "new_team" in locals() else None
        }

    async def _run_match(self, agent_id: str) -> Dict:
        """Simulate a battle match"""
        # TODO: Implement actual battle mechanics
        # For now, return simulated results
        import random

        performance = random.uniform(0, 1)
        victory = performance > 0.5

        return {
            "victory": victory,
            "performance": performance,
            "opponent_rank": random.choice(self.LEAGUES)
        }

    def _calculate_points_change(self, performance: float, victory: bool) -> int:
        """Calculate league points change based on match performance"""
        base_points = 20 if victory else -15
        performance_bonus = int(performance * 10)
        return base_points + performance_bonus

    def _calculate_league(self, points: int) -> str:
        """Calculate league based on points"""
        if points < 100:
            return "Bronze"
        elif points < 300:
            return "Silver"
        elif points < 600:
            return "Gold"
        elif points < 1000:
            return "Platinum"
        elif points < 1500:
            return "Diamond"
        elif points < 2000:
            return "Master"
        elif points < 3000:
            return "Grandmaster"
        else:
            return "Legend"

    def _should_form_team(self, state: Dict) -> bool:
        """Determine if agent should form/join a new team"""
        # Form team if agent has none and has good performance
        return (
            not state["current_team"]
            and state["matches_played"] >= 10
            and (state["wins"] / state["matches_played"]) > 0.5
        )

    async def _form_team(self, agent_id: str) -> Dict:
        """Form or join a team"""
        # TODO: Implement actual team formation logic
        # For now, create a simulated team
        import uuid

        return {
            "id": str(uuid.uuid4()),
            "name": f"Team {agent_id[:8]}",
            "created_at": datetime.utcnow().isoformat(),
            "members": [agent_id],
            "rank": "Rookie",
            "points": 0
        }

    def _check_achievements(self, state: Dict) -> List[str]:
        """Check for new achievements"""
        new_achievements = []

        # Win-based achievements
        if state["wins"] >= 10 and "Wins10" not in state["achievements"]:
            new_achievements.append("Wins10")
        if state["wins"] >= 100 and "Wins100" not in state["achievements"]:
            new_achievements.append("Wins100")

        # League-based achievements
        if state["league"] == "Gold" and "ReachGold" not in state["achievements"]:
            new_achievements.append("ReachGold")
        if state["league"] == "Diamond" and "ReachDiamond" not in state["achievements"]:
            new_achievements.append("ReachDiamond")

        # Team-based achievements
        if state["teams"] and "FirstTeam" not in state["achievements"]:
            new_achievements.append("FirstTeam")

        return new_achievements
