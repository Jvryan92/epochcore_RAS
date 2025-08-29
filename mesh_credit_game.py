"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from mesh_credit import MeshCredit, MeshGlyph


@dataclass
class GameAchievement:
    name: str
    description: str
    emotional_value: float  # 0.0 to 1.0
    trust_multiplier: float  # 1.0 to 3.0
    rarity: str  # "common", "rare", "epic", "legendary"


@dataclass
class PlayerProfile:
    wallet_id: str
    glyphs: List[MeshGlyph]
    achievements: List[GameAchievement]
    emotional_score: float
    trust_level: float
    mining_power: float


class MeshCreditGame:
    """Game integration layer for MeshCredit system"""

    def __init__(self):
        self.mesh = MeshCredit()
        self.players: Dict[str, PlayerProfile] = {}
        self.achievements = {
            "FIRST_WIN": GameAchievement(
                "First Victory",
                "Win your first match",
                0.6,
                1.2,
                "common"
            ),
            "TEAM_SPIRIT": GameAchievement(
                "Team Spirit",
                "Help 10 other players",
                0.8,
                1.5,
                "rare"
            ),
            "MASTER_TRADER": GameAchievement(
                "Master Trader",
                "Complete 100 successful trades",
                0.9,
                2.0,
                "epic"
            ),
            "LEGENDARY_PRESENCE": GameAchievement(
                "Legendary Presence",
                "Achieve 1000 hours of playtime",
                1.0,
                3.0,
                "legendary"
            )
        }

    def create_player(self, player_id: str) -> str:
        """Create new player wallet and profile"""
        # Generate unique wallet ID
        wallet_id = f"MESH_{player_id}_{int(time.time())}"

        # Create starter glyph
        starter_glyph = MeshGlyph(
            glyph_id=f"STARTER_{wallet_id}",
            trust_weight=0.3,
            emotional_resonance=0.5,
            founder_status=False
        )

        # Initialize player profile
        self.players[player_id] = PlayerProfile(
            wallet_id=wallet_id,
            glyphs=[starter_glyph],
            achievements=[],
            emotional_score=0.5,
            trust_level=0.3,
            mining_power=0.1
        )

        return wallet_id

    def award_achievement(self, player_id: str, achievement_id: str) -> Optional[MeshGlyph]:
        """Award achievement and generate corresponding glyph"""
        if player_id not in self.players or achievement_id not in self.achievements:
            return None

        achievement = self.achievements[achievement_id]
        player = self.players[player_id]

        # Create achievement glyph
        new_glyph = MeshGlyph(
            glyph_id=f"ACH_{achievement_id}_{player.wallet_id}",
            trust_weight=achievement.trust_multiplier * player.trust_level,
            emotional_resonance=achievement.emotional_value,
            founder_status=False
        )

        # Update player profile
        player.glyphs.append(new_glyph)
        player.achievements.append(achievement)
        player.emotional_score = min(1.0, player.emotional_score + 0.1)
        player.trust_level = min(1.0, player.trust_level + 0.05)
        player.mining_power = min(1.0, player.mining_power + 0.1)

        return new_glyph

    def mine_with_emotion(self, player_id: str, emotion_boost: float = 0.0) -> bool:
        """Attempt to mine a block using player's emotional state"""
        if player_id not in self.players:
            return False

        player = self.players[player_id]

        # Select player's best glyph
        best_glyph = max(
            player.glyphs,
            key=lambda g: g.trust_weight * g.emotional_resonance
        )

        # Apply emotion boost from gameplay
        boosted_glyph = MeshGlyph(
            glyph_id=best_glyph.glyph_id,
            trust_weight=best_glyph.trust_weight,
            emotional_resonance=min(
                1.0, best_glyph.emotional_resonance + emotion_boost),
            founder_status=best_glyph.founder_status
        )

        # Attempt to mine block
        block = self.mesh.mine_block(boosted_glyph)
        return block is not None

    def get_player_stats(self, player_id: str) -> Optional[dict]:
        """Get player's MeshCredit stats"""
        if player_id not in self.players:
            return None

        player = self.players[player_id]
        return {
            'balance': self.mesh.get_balance(player.wallet_id),
            'emotional_score': player.emotional_score,
            'trust_level': player.trust_level,
            'mining_power': player.mining_power,
            'achievements': len(player.achievements),
            'best_glyph': max(
                player.glyphs,
                key=lambda g: g.trust_weight * g.emotional_resonance
            ).glyph_id
        }

    def transfer_mesh(self, from_id: str, to_id: str, amount: float) -> bool:
        """Transfer MeshCredits between players"""
        if from_id not in self.players or to_id not in self.players:
            return False

        from_wallet = self.players[from_id].wallet_id
        to_wallet = self.players[to_id].wallet_id

        return self.mesh.add_transaction(from_wallet, to_wallet, amount)
