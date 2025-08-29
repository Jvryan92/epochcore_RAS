"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

import json
import os
import random
import time
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from scripts.mesh.transfer import Transfer

MESH_KEY = b"meshcredit2024"
LEDGER_PATH = os.path.join(os.path.dirname(__file__), "mesh_transactions.jsonl")
GAME_WALLET = "MESH_GAME_REWARDS"


class MeshGameIntegration:
    """Game integration for MeshCredit system."""

    ACHIEVEMENTS = {
        "FIRST_MISSION": {
            "name": "First Mission Complete",
            "reward": Decimal("100"),
            "description": "Complete your first mission",
            "glyph_bonus": 1
        },
        "SPEED_RUN": {
            "name": "Speed Demon",
            "reward": Decimal("500"),
            "description": "Complete mission in under 2 minutes",
            "glyph_bonus": 2
        },
        "PERFECT_SCORE": {
            "name": "Perfect Score",
            "reward": Decimal("1000"),
            "description": "100% mission completion",
            "glyph_bonus": 3
        },
        "COMBO_MASTER": {
            "name": "Combo Master",
            "reward": Decimal("750"),
            "description": "10x combo multiplier",
            "glyph_bonus": 2
        },
        "RESOURCE_KING": {
            "name": "Resource King",
            "reward": Decimal("1500"),
            "description": "Collect 1000 resources",
            "glyph_bonus": 4
        }
    }

    GAME_ITEMS = {
        "POWER_BOOST": {
            "name": "Power Boost",
            "price": Decimal("250"),
            "description": "2x power for 1 hour",
            "duration": 3600
        },
        "RESOURCE_MAGNET": {
            "name": "Resource Magnet",
            "price": Decimal("500"),
            "description": "Auto-collect nearby resources",
            "duration": 7200
        },
        "TIME_WARP": {
            "name": "Time Warp",
            "price": Decimal("1000"),
            "description": "Speed up time 2x",
            "duration": 1800
        },
        "MYSTERY_BOX": {
            "name": "Mystery Box",
            "price": Decimal("2000"),
            "description": "Random high-value reward",
            "duration": 0
        }
    }

    def __init__(self):
        self.transfer = Transfer(MESH_KEY, LEDGER_PATH)
        self.player_stats_path = f"{os.path.splitext(LEDGER_PATH)[0]}_game_stats.json"
        self.active_effects = {}
        self._load_player_stats()

    def _load_player_stats(self) -> None:
        """Load or initialize player stats."""
        if os.path.exists(self.player_stats_path):
            with open(self.player_stats_path) as f:
                self.player_stats = json.load(f)
        else:
            self.player_stats = {
                "achievements": {},
                "items": {},
                "total_glyphs": 0,
                "high_score": 0
            }

    def _save_player_stats(self) -> None:
        """Save player stats."""
        with open(self.player_stats_path, "w") as f:
            json.dump(self.player_stats, f, indent=2)

    def unlock_achievement(
        self,
        wallet_id: str,
        achievement_id: str
    ) -> Tuple[bool, Optional[Dict]]:
        """Unlock an achievement and receive MESH reward.

        Args:
            wallet_id: Player's wallet ID
            achievement_id: Achievement to unlock

        Returns:
            (success, achievement_details)
        """
        if achievement_id not in self.ACHIEVEMENTS:
            print(f"Invalid achievement: {achievement_id}")
            return False, None

        if achievement_id in self.player_stats["achievements"]:
            print("Achievement already unlocked!")
            return False, None

        achievement = self.ACHIEVEMENTS[achievement_id]

        # Transfer reward
        success, error = self.transfer.transfer(
            from_wallet=GAME_WALLET,
            to_wallet=wallet_id,
            amount=achievement["reward"],
            tx_type="game_reward"
        )

        if not success:
            print(f"Reward transfer failed: {error}")
            return False, None

        # Update stats
        self.player_stats["achievements"][achievement_id] = {
            "unlocked_at": time.time(),
            "reward": str(achievement["reward"]),
            "glyphs": achievement["glyph_bonus"]
        }
        self.player_stats["total_glyphs"] += achievement["glyph_bonus"]
        self._save_player_stats()

        return True, achievement

    def buy_game_item(
        self,
        wallet_id: str,
        item_id: str
    ) -> Tuple[bool, Optional[Dict]]:
        """Purchase a game item with MESH.

        Args:
            wallet_id: Player's wallet ID
            item_id: Item to purchase

        Returns:
            (success, item_details)
        """
        if item_id not in self.GAME_ITEMS:
            print(f"Invalid item: {item_id}")
            return False, None

        item = self.GAME_ITEMS[item_id]
        balance = self.transfer.get_balance(wallet_id)

        if balance < item["price"]:
            print(f"Insufficient balance: {balance} MESH")
            print(f"Required: {item['price']} MESH")
            return False, None

        # Transfer payment
        success, error = self.transfer.transfer(
            from_wallet=wallet_id,
            to_wallet=GAME_WALLET,
            amount=item["price"],
            tx_type="game_purchase"
        )

        if not success:
            print(f"Purchase failed: {error}")
            return False, None

        # Activate item
        if item_id == "MYSTERY_BOX":
            reward = self._open_mystery_box(wallet_id)
            item_effect = {"mystery_reward": reward}
        else:
            item_effect = {
                "activated_at": time.time(),
                "expires_at": time.time() + item["duration"]
            }
            self.active_effects[item_id] = item_effect

        # Update stats
        if item_id not in self.player_stats["items"]:
            self.player_stats["items"][item_id] = []
        self.player_stats["items"][item_id].append(item_effect)
        self._save_player_stats()

        return True, {**item, "effect": item_effect}

    def _open_mystery_box(self, wallet_id: str) -> Dict:
        """Open a mystery box for random rewards."""
        rewards = [
            {"type": "mesh", "amount": Decimal("5000")},
            {"type": "glyph", "amount": 10},
            {"type": "power_boost", "duration": 7200},
            {"type": "resource_bonus", "multiplier": 3}
        ]

        reward = random.choice(rewards)

        if reward["type"] == "mesh":
            self.transfer.transfer(
                from_wallet=GAME_WALLET,
                to_wallet=wallet_id,
                amount=reward["amount"],
                tx_type="mystery_reward"
            )

        elif reward["type"] == "glyph":
            self.player_stats["total_glyphs"] += reward["amount"]
            self._save_player_stats()

        return reward

    def get_active_effects(self) -> Dict:
        """Get currently active game effects."""
        current_time = time.time()
        active = {}

        for item_id, effect in self.active_effects.items():
            if effect["expires_at"] > current_time:
                remaining = effect["expires_at"] - current_time
                active[item_id] = {
                    "name": self.GAME_ITEMS[item_id]["name"],
                    "remaining_seconds": remaining
                }
            else:
                del self.active_effects[item_id]

        return active

    def update_high_score(self, score: int) -> bool:
        """Update player's high score if beaten."""
        if score > self.player_stats["high_score"]:
            self.player_stats["high_score"] = score
            self._save_player_stats()
            return True
        return False


def main():
    """Main execution function."""
    game = MeshGameIntegration()
    wallet_id = "MESH_JVRYAN92_1756445384"

    # Show balance
    balance = game.transfer.get_balance(wallet_id)
    print(f"\nWallet Balance: {balance:,} MESH")

    # Display achievements
    print("\n=== Available Achievements ===")
    for aid, achievement in game.ACHIEVEMENTS.items():
        unlocked = aid in game.player_stats["achievements"]
        print(f"\n{achievement['name']}")
        print(f"Reward: {achievement['reward']:,} MESH")
        print(f"Glyph Bonus: {achievement['glyph_bonus']}")
        print(f"Status: {'🔓 Unlocked' if unlocked else '🔒 Locked'}")

    # Display game items
    print("\n=== Game Store ===")
    for iid, item in game.GAME_ITEMS.items():
        print(f"\n{item['name']}")
        print(f"Price: {item['price']:,} MESH")
        print(f"Effect: {item['description']}")
        if item['duration']:
            print(f"Duration: {item['duration']} seconds")

    # Example achievement unlock
    print("\n=== Achievement Test ===")
    success, achievement = game.unlock_achievement(wallet_id, "FIRST_MISSION")
    if success:
        print(f"Achievement unlocked: {achievement['name']}")
        print(f"Reward: {achievement['reward']:,} MESH")
        print(f"Glyphs: +{achievement['glyph_bonus']}")

    # Example item purchase
    print("\n=== Item Purchase Test ===")
    success, item = game.buy_game_item(wallet_id, "MYSTERY_BOX")
    if success:
        print(f"Purchased: {item['name']}")
        if "mystery_reward" in item["effect"]:
            reward = item["effect"]["mystery_reward"]
            print(f"Mystery Reward: {reward['type']}, {reward['amount']}")

    # Show active effects
    print("\n=== Active Effects ===")
    for item_id, effect in game.get_active_effects().items():
        print(f"{effect['name']}: {effect['remaining_seconds']:.0f}s remaining")

    print(f"\nFinal Balance: {game.transfer.get_balance(wallet_id):,} MESH")
    print(f"Total Glyphs: {game.player_stats['total_glyphs']}")


if __name__ == "__main__":
    main()
