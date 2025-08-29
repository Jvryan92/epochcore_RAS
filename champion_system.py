"""Champion Creator System - Custom agent development and training"""

from datetime import datetime
from typing import Dict, List, Optional

from omega_base import OmegaSubsystem


class ChampionCreatorSystem(OmegaSubsystem):
    """Manages custom agent development, training programs, and achievements"""

    SPECIALIZATIONS = [
        "Strategist",
        "Tactician",
        "Guardian",
        "Innovator",
        "Commander",
        "Diplomat"
    ]

    TRAINING_PROGRAMS = [
        "Basic Combat",
        "Advanced Tactics",
        "Strategic Planning",
        "Team Leadership",
        "Resource Management",
        "Diplomatic Relations"
    ]

    async def initialize_agent(self, agent_id: str) -> Dict:
        """Initialize an agent in the champion creation system"""
        state = {
            "agent_id": agent_id,
            "created_at": datetime.utcnow().isoformat(),
            "level": 1,
            "experience": 0,
            "specialization": None,
            "skills": {
                "combat": 1,
                "tactics": 1,
                "strategy": 1,
                "leadership": 1,
                "management": 1,
                "diplomacy": 1
            },
            "completed_training": [],
            "active_training": None,
            "achievements": [],
            "development_history": []
        }
        await self._save_state(agent_id, state)
        return state

    async def evolve_agent(self, agent_id: str) -> Dict:
        """Evolve agent through training and development"""
        state = await self._load_state(agent_id)
        if not state:
            raise ValueError(f"Agent {agent_id} not initialized")

        # Process active training if any
        if state["active_training"]:
            training_result = await self._process_training(state)
            if training_result["completed"]:
                state["completed_training"].append(state["active_training"])
                state["active_training"] = None

        # Gain experience
        exp_gained = await self._generate_experience(state)
        state["experience"] += exp_gained

        # Check for level up
        old_level = state["level"]
        state["level"] = self._calculate_level(state["experience"])

        if state["level"] > old_level:
            # Level up occurred
            skill_increases = self._process_level_up(state, old_level)
            state["skills"].update(skill_increases)

            # Record development
            state["development_history"].append({
                "timestamp": datetime.utcnow().isoformat(),
                "type": "level_up",
                "old_level": old_level,
                "new_level": state["level"],
                "skill_increases": skill_increases
            })

        # Check for specialization if none
        if not state["specialization"]:
            spec = self._determine_specialization(state)
            if spec:
                state["specialization"] = spec
                state["development_history"].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "specialization",
                    "specialization": spec
                })

        # Start new training if none active
        if not state["active_training"]:
            new_training = self._select_training(state)
            if new_training:
                state["active_training"] = {
                    "program": new_training,
                    "progress": 0,
                    "started_at": datetime.utcnow().isoformat()
                }

        # Check achievements
        new_achievements = self._check_achievements(state)
        state["achievements"].extend(new_achievements)

        # Save updated state
        await self._save_state(agent_id, state)

        return {
            "experience_gained": exp_gained,
            "new_level": state["level"] if state["level"] > old_level else None,
            "new_specialization": spec if "spec" in locals() and spec else None,
            "training_progress": training_result if "training_result" in locals() else None,
            "new_achievements": new_achievements
        }

    async def _process_training(self, state: Dict) -> Dict:
        """Process ongoing training program"""
        training = state["active_training"]
        progress_gain = self._calculate_training_progress(state)
        training["progress"] += progress_gain

        completed = training["progress"] >= 100
        if completed:
            # Apply training benefits
            skill_increases = self._apply_training_benefits(state, training["program"])
            state["skills"].update(skill_increases)

        return {
            "completed": completed,
            "progress": training["progress"],
            "progress_gain": progress_gain,
            "skill_increases": skill_increases if completed else None
        }

    async def _generate_experience(self, state: Dict) -> int:
        """Generate experience based on agent's current state"""
        # Base experience from level
        base_exp = 10 * state["level"]

        # Bonus from specialization
        spec_bonus = 5 if state["specialization"] else 0

        # Bonus from active training
        training_bonus = 3 if state["active_training"] else 0

        return base_exp + spec_bonus + training_bonus

    def _calculate_level(self, experience: int) -> int:
        """Calculate level based on total experience"""
        import math
        return min(100, max(1, math.floor(math.sqrt(experience / 100))))

    def _process_level_up(self, state: Dict, old_level: int) -> Dict[str, int]:
        """Process level up and return skill increases"""
        skill_increases = {}
        points = state["level"] - old_level

        # Prioritize skills based on specialization
        if state["specialization"]:
            primary_skills = self._get_specialization_skills(state["specialization"])

            # Distribute points prioritizing specialization skills
            for skill in primary_skills:
                if points > 0:
                    skill_increases[skill] = 2  # Primary skills get 2 points
                    points -= 1

        # Distribute remaining points randomly
        import random
        skills = list(state["skills"].keys())
        while points > 0:
            skill = random.choice(skills)
            if skill not in skill_increases:
                skill_increases[skill] = 1
                points -= 1

        return skill_increases

    def _determine_specialization(self, state: Dict) -> Optional[str]:
        """Determine agent specialization based on skills and level"""
        if state["level"] < 10:  # Need level 10 for specialization
            return None

        # Find highest skills
        skills = state["skills"]
        max_skill = max(skills.values())
        top_skills = [k for k, v in skills.items() if v == max_skill]

        # Map skills to specializations
        skill_spec_map = {
            "combat": ["Guardian", "Commander"],
            "tactics": ["Tactician", "Commander"],
            "strategy": ["Strategist", "Innovator"],
            "leadership": ["Commander", "Diplomat"],
            "management": ["Innovator", "Strategist"],
            "diplomacy": ["Diplomat", "Guardian"]
        }

        # Count specialization occurrences for top skills
        spec_counts = {}
        for skill in top_skills:
            for spec in skill_spec_map[skill]:
                spec_counts[spec] = spec_counts.get(spec, 0) + 1

        # Select highest count specialization
        if spec_counts:
            max_count = max(spec_counts.values())
            top_specs = [k for k, v in spec_counts.items() if v == max_count]
            import random
            return random.choice(top_specs)

        return None

    def _select_training(self, state: Dict) -> Optional[str]:
        """Select next training program"""
        if len(state["completed_training"]) >= len(self.TRAINING_PROGRAMS):
            return None  # All programs completed

        available = [p for p in self.TRAINING_PROGRAMS
                     if p not in state["completed_training"]]

        if state["specialization"]:
            # Prioritize programs that match specialization
            spec_programs = self._get_specialization_programs(state["specialization"])
            priority = [p for p in available if p in spec_programs]
            if priority:
                import random
                return random.choice(priority)

        import random
        return random.choice(available)

    def _calculate_training_progress(self, state: Dict) -> float:
        """Calculate training progress gain"""
        # Base progress
        progress = 5.0

        # Level bonus
        progress += state["level"] * 0.1

        # Specialization bonus
        if state["specialization"]:
            spec_programs = self._get_specialization_programs(state["specialization"])
            if state["active_training"]["program"] in spec_programs:
                progress *= 1.5

        return progress

    def _apply_training_benefits(self, state: Dict, program: str) -> Dict[str, int]:
        """Apply benefits from completed training"""
        benefits = {}

        # Map programs to primary and secondary skills
        program_skills = {
            "Basic Combat": (["combat"], ["tactics"]),
            "Advanced Tactics": (["tactics"], ["strategy"]),
            "Strategic Planning": (["strategy"], ["management"]),
            "Team Leadership": (["leadership"], ["diplomacy"]),
            "Resource Management": (["management"], ["strategy"]),
            "Diplomatic Relations": (["diplomacy"], ["leadership"])
        }

        primary, secondary = program_skills[program]

        # Apply increases
        for skill in primary:
            benefits[skill] = 2  # Primary skills get larger increase
        for skill in secondary:
            benefits[skill] = 1  # Secondary skills get smaller increase

        return benefits

    def _get_specialization_skills(self, spec: str) -> List[str]:
        """Get primary skills for specialization"""
        spec_skills = {
            "Strategist": ["strategy", "management"],
            "Tactician": ["tactics", "combat"],
            "Guardian": ["combat", "diplomacy"],
            "Innovator": ["management", "strategy"],
            "Commander": ["leadership", "tactics"],
            "Diplomat": ["diplomacy", "leadership"]
        }
        return spec_skills[spec]

    def _get_specialization_programs(self, spec: str) -> List[str]:
        """Get recommended training programs for specialization"""
        spec_programs = {
            "Strategist": ["Strategic Planning", "Resource Management"],
            "Tactician": ["Advanced Tactics", "Basic Combat"],
            "Guardian": ["Basic Combat", "Diplomatic Relations"],
            "Innovator": ["Resource Management", "Strategic Planning"],
            "Commander": ["Team Leadership", "Advanced Tactics"],
            "Diplomat": ["Diplomatic Relations", "Team Leadership"]
        }
        return spec_programs[spec]

    def _check_achievements(self, state: Dict) -> List[str]:
        """Check for new achievements"""
        new_achievements = []

        # Level achievements
        if state["level"] >= 10 and "Level10" not in state["achievements"]:
            new_achievements.append("Level10")
        if state["level"] >= 50 and "Level50" not in state["achievements"]:
            new_achievements.append("Level50")

        # Training achievements
        if len(state["completed_training"]) >= 3 and "Training3" not in state["achievements"]:
            new_achievements.append("Training3")
        if len(state["completed_training"]) >= 6 and "TrainingMaster" not in state["achievements"]:
            new_achievements.append("TrainingMaster")

        # Specialization achievement
        if state["specialization"] and "Specialized" not in state["achievements"]:
            new_achievements.append("Specialized")

        # Skill achievements
        max_skill = max(state["skills"].values())
        if max_skill >= 10 and "SkillMaster" not in state["achievements"]:
            new_achievements.append("SkillMaster")

        return new_achievements
