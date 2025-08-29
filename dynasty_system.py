"""Dynasty Development System - Multi-generational agent evolution"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from omega_base import OmegaSubsystem


class DynastySystem(OmegaSubsystem):
    """Manages multi-generational agent evolution and lineage tracking"""

    DYNASTY_RANKS = [
        "Foundling",      # New dynasty
        "Established",    # 2+ generations
        "Venerable",      # 5+ generations
        "Ancient",        # 10+ generations
        "Legendary",      # 20+ generations
        "Immortal"        # 50+ generations
    ]

    INHERITANCE_TRAITS = [
        "strategic_insight",
        "tactical_prowess",
        "learning_rate",
        "adaptability",
        "resilience",
        "innovation"
    ]

    async def initialize_agent(self, agent_id: str) -> Dict:
        """Initialize a new dynasty"""
        dynasty_id = str(uuid.uuid4())

        state = {
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat(),
            "dynasty_id": dynasty_id,
            "generation": 1,
            "rank": "Foundling",
            "lineage": [{
                "agent_id": agent_id,
                "generation": 1,
                "created_at": datetime.utcnow().isoformat(),
                "achievements": []
            }],
            "inherited_traits": self._generate_initial_traits(),
            "legacy_score": 0,
            "successor_candidates": []
        }

        await self._save_state(agent_id, state)
        return state

    async def evolve_agent(self, agent_id: str) -> Dict:
        """Evolve agent through dynasty mechanics"""
        state = await self._load_state(agent_id)
        if not state:
            raise ValueError(f"Agent {agent_id} not initialized")

        # Accumulate legacy score
        legacy_gained = self._calculate_legacy_gain(state)
        state["legacy_score"] += legacy_gained

        # Check for rank advancement
        old_rank = state["rank"]
        state["rank"] = self._calculate_rank(state)

        # Update traits based on experience
        trait_changes = self._evolve_traits(state)
        state["inherited_traits"].update(trait_changes)

        # Consider producing successor
        successor = None
        if self._should_produce_successor(state):
            successor = await self._create_successor(state)
            if successor:
                state["successor_candidates"].append(successor)

        # Save state
        await self._save_state(agent_id, state)

        return {
            "legacy_gained": legacy_gained,
            "new_rank": state["rank"] if state["rank"] != old_rank else None,
            "trait_changes": trait_changes,
            "successor": successor
        }

    def _generate_initial_traits(self) -> Dict[str, float]:
        """Generate initial trait values for a new dynasty"""
        import random
        return {
            trait: random.uniform(0.1, 0.3)
            for trait in self.INHERITANCE_TRAITS
        }

    def _calculate_legacy_gain(self, state: Dict) -> int:
        """Calculate legacy points gained"""
        # Base gain
        base_gain = 10

        # Generation bonus
        gen_bonus = state["generation"] * 5

        # Trait bonus
        trait_bonus = sum(state["inherited_traits"].values()) * 10

        return int(base_gain + gen_bonus + trait_bonus)

    def _calculate_rank(self, state: Dict) -> str:
        """Calculate dynasty rank based on generation and legacy"""
        if state["generation"] >= 50:
            return "Immortal"
        elif state["generation"] >= 20:
            return "Legendary"
        elif state["generation"] >= 10:
            return "Ancient"
        elif state["generation"] >= 5:
            return "Venerable"
        elif state["generation"] >= 2:
            return "Established"
        else:
            return "Foundling"

    def _evolve_traits(self, state: Dict) -> Dict[str, float]:
        """Evolve inherited traits based on experience"""
        import random

        changes = {}
        for trait, value in state["inherited_traits"].items():
            # Small random improvement
            change = random.uniform(0, 0.05)
            # More improvement for higher generations
            change *= (1 + state["generation"] * 0.1)
            # Cap at 1.0
            new_value = min(1.0, value + change)
            if new_value != value:
                changes[trait] = new_value

        return changes

    def _should_produce_successor(self, state: Dict) -> bool:
        """Determine if agent should produce a successor"""
        # Require minimum legacy score
        if state["legacy_score"] < 1000:
            return False

        # Limit number of successors
        if len(state["successor_candidates"]) >= 3:
            return False

        # Random chance based on generation
        import random
        chance = 0.1 + (state["generation"] * 0.02)
        return random.random() < chance

    async def _create_successor(self, state: Dict) -> Optional[Dict]:
        """Create a successor agent"""
        successor_id = str(uuid.uuid4())

        # Inherit and mutate traits
        inherited_traits = self._mutate_traits(state["inherited_traits"])

        successor = {
            "id": successor_id,
            "parent_id": state["agent_id"],
            "dynasty_id": state["dynasty_id"],
            "generation": state["generation"] + 1,
            "created_at": datetime.utcnow().isoformat(),
            "inherited_traits": inherited_traits,
            "status": "candidate"
        }

        return successor

    def _mutate_traits(self, parent_traits: Dict[str, float]) -> Dict[str, float]:
        """Mutate inherited traits for successor"""
        import random

        mutated = {}
        for trait, value in parent_traits.items():
            # Random mutation
            mutation = random.uniform(-0.1, 0.1)
            # Larger mutations are less likely
            mutation *= random.random()
            # Ensure value stays in [0, 1]
            mutated[trait] = max(0.0, min(1.0, value + mutation))

        return mutated

    async def activate_successor(self, agent_id: str, successor_id: str) -> Dict:
        """Activate a successor, advancing the dynasty"""
        state = await self._load_state(agent_id)
        if not state:
            raise ValueError(f"Agent {agent_id} not initialized")

        # Find successor
        successor = None
        for candidate in state["successor_candidates"]:
            if candidate["id"] == successor_id:
                successor = candidate
                break

        if not successor:
            raise ValueError(f"Successor {successor_id} not found")

        # Create new dynasty member
        successor["status"] = "active"
        successor["activated_at"] = datetime.utcnow().isoformat()

        # Update lineage
        state["lineage"].append({
            "agent_id": successor_id,
            "generation": successor["generation"],
            "created_at": successor["created_at"],
            "activated_at": successor["activated_at"],
            "achievements": []
        })

        # Save state
        await self._save_state(agent_id, state)

        return successor
