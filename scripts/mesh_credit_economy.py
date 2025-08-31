#!/usr/bin/env python3
# EpochCore — Mesh Credit Economy Module
# No external deps. Safe. Implements the core Mesh Credit whitepaper.

import hashlib
import json
import os
import pathlib
import sys
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

# ---------- Constants ----------
ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
LEDGER = os.path.join(ROOT, "ledger_main.jsonl")
ECONOMY_DIR = os.path.join(ROOT, "economy")
MESH_CREDIT_DIR = os.path.join(ECONOMY_DIR, "mesh_credit")
WALLETS_DIR = os.path.join(MESH_CREDIT_DIR, "wallets")
GOVERNANCE_DIR = os.path.join(MESH_CREDIT_DIR, "governance")
CAS_DIR = os.path.join(MESH_CREDIT_DIR, "cas")  # Content-addressable storage

# Ensure all directories exist
for dir_path in [ECONOMY_DIR, MESH_CREDIT_DIR, WALLETS_DIR, GOVERNANCE_DIR, CAS_DIR]:
    pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)

# ---------- Helpers ----------


def utc_now() -> str:
    """Get current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha256_bytes(b: bytes) -> str:
    """Get SHA-256 hash of bytes."""
    return hashlib.sha256(b).hexdigest()


def sha256_str(s: str) -> str:
    """Get SHA-256 hash of string."""
    return sha256_bytes(s.encode('utf-8'))


def sha256_file(path: str) -> str:
    """Get SHA-256 hash of file."""
    with open(path, 'rb') as f:
        return sha256_bytes(f.read())


def cas_store(data: Any) -> str:
    """Store data in CAS and return content hash."""
    data_json = json.dumps(data, sort_keys=True, ensure_ascii=False)
    data_hash = sha256_str(data_json)
    cas_path = os.path.join(CAS_DIR, f"{data_hash}.json")

    with open(cas_path, 'w', encoding='utf-8') as f:
        f.write(data_json)

    return data_hash


def cas_get(content_hash: str) -> Optional[Any]:
    """Get data from CAS by content hash."""
    cas_path = os.path.join(CAS_DIR, f"{content_hash}.json")
    if not os.path.exists(cas_path):
        return None

    with open(cas_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ledger_append(event: Dict) -> None:
    """Append event to ledger."""
    event.setdefault('ts', utc_now())
    line = json.dumps(event, separators=(',', ':'), ensure_ascii=False)
    with open(LEDGER, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def compute_merkle_root(hashes: List[str]) -> str:
    """Compute a simple Merkle root from a list of hashes."""
    if not hashes:
        return sha256_str("empty_tree")

    if len(hashes) == 1:
        return hashes[0]

    # Ensure even number of leaves by duplicating last one if needed
    if len(hashes) % 2 == 1:
        hashes.append(hashes[-1])

    # Compute parent nodes
    parents = []
    for i in range(0, len(hashes), 2):
        combined = hashes[i] + hashes[i+1]
        parents.append(sha256_str(combined))

    # Recurse to compute root
    return compute_merkle_root(parents)

# ---------- Mesh Credit Core ----------


class MeshCredit:
    def __init__(self):
        self.manifest_path = os.path.join(MESH_CREDIT_DIR, "manifest.json")
        self.pricing_path = os.path.join(MESH_CREDIT_DIR, "pricing.json")
        self.yield_path = os.path.join(MESH_CREDIT_DIR, "yield_curve.json")
        self.params_path = os.path.join(MESH_CREDIT_DIR, "params.json")

        # Initialize if not exists
        if not os.path.exists(self.manifest_path):
            self._initialize_economy()

        # Load current state
        self.manifest = self._load_json(self.manifest_path)
        self.pricing = self._load_json(self.pricing_path)
        self.yield_curve = self._load_json(self.yield_path)
        self.params = self._load_json(self.params_path)

    def _load_json(self, path: str) -> Dict:
        """Load JSON file or return empty dict if not exists."""
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_json(self, data: Dict, path: str) -> None:
        """Save data to JSON file."""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _initialize_economy(self) -> None:
        """Initialize the Mesh Credit economy."""
        # Create manifest
        manifest = {
            "name": "Mesh Credit",
            "symbol": "MESH",
            "description": "Universal fair-by-design currency for EpochCore",
            "version": "1.0.0",
            "created_at": utc_now(),
            "updated_at": utc_now(),
            "total_supply": 0,
            "circulating_supply": 0,
            "staked_supply": 0,
            "governance_staked": 0,
            "mint_events": 0,
            "burn_events": 0,
            "epochs_completed": 0,
            "fair_by_design": {
                "cosmetics_only": True,
                "time_savers_only": True,
                "governance_ready": True,
                "no_pay_to_win": True
            }
        }

        # Create pricing table
        pricing = {
            "usd_to_mesh_rate": 10.0,  # 1 USD = 10 MESH
            "item_categories": {
                "character_cosmetic": {
                    "common": 50,
                    "rare": 100,
                    "epic": 200,
                    "legendary": 400
                },
                "gear_cosmetic": {
                    "common": 30,
                    "rare": 75,
                    "epic": 150,
                    "legendary": 300
                },
                "time_saver": {
                    "small": 25,
                    "medium": 50,
                    "large": 100
                },
                "governance": {
                    "vote_weight": 1000,  # MESH required for 1 vote weight
                    "proposal_creation": 5000  # MESH required to create proposal
                }
            },
            "last_updated": utc_now()
        }

        # Create yield curve parameters
        yield_curve = {
            "base_apy": 0.05,  # 5% base APY
            "max_apy": 0.12,   # 12% max APY
            "stake_tiers": [
                {"threshold": 0, "bonus": 0.00},
                {"threshold": 1000, "bonus": 0.01},
                {"threshold": 5000, "bonus": 0.02},
                {"threshold": 10000, "bonus": 0.03},
                {"threshold": 25000, "bonus": 0.04},
                {"threshold": 50000, "bonus": 0.05},
                {"threshold": 100000, "bonus": 0.07}
            ],
            "governance_bonus": 0.02,  # +2% for governance staking
            "lockup_bonus": {
                "30_days": 0.01,
                "90_days": 0.02,
                "180_days": 0.03,
                "365_days": 0.05
            },
            "epoch_length_days": 30,
            "compounding": True
        }

        # Create economic parameters
        params = {
            "mint_triggers": {
                "new_player": 100,        # Mint 100 MESH for new player
                "daily_login": 10,        # Mint 10 MESH for daily login
                "achievement": 25,        # Mint 25 MESH for achievement
                "season_completion": 500,  # Mint 500 MESH for season completion
                "raid_completion": 200    # Mint 200 MESH for raid completion
            },
            "burn_triggers": {
                "cosmetic_purchase": True,
                "time_saver_purchase": True,
                "governance_proposal": False  # Staked, not burned
            },
            "max_daily_mint": 1000,       # Cap daily minting per player
            "inflation_target": 0.05,     # 5% annual inflation target
            "deflation_threshold": 0.75,  # If 75% of supply is staked, reduce mint rates
            "stability_metrics": {
                "price_volatility_target": 0.10,  # 10% max volatility
                "liquidity_ratio_target": 0.30    # 30% of supply should be liquid
            }
        }

        # Save all files
        self._save_json(manifest, self.manifest_path)
        self._save_json(pricing, self.pricing_path)
        self._save_json(yield_curve, self.yield_path)
        self._save_json(params, self.params_path)

        # Log initialization
        ledger_append({
            "event": "mesh_credit_initialized",
            "manifest_hash": sha256_file(self.manifest_path),
            "pricing_hash": sha256_file(self.pricing_path),
            "yield_curve_hash": sha256_file(self.yield_path),
            "params_hash": sha256_file(self.params_path)
        })

    def get_epochroot(self) -> str:
        """Compute the EPOCHROOT Merkle hash of all economy files."""
        hashes = []
        for root, _, files in os.walk(MESH_CREDIT_DIR):
            for file in files:
                if file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    file_hash = sha256_file(file_path)
                    hashes.append(file_hash)

        # Sort for determinism
        hashes.sort()

        # Compute root
        merkle_root = compute_merkle_root(hashes)

        # Update manifest
        self.manifest["epochroot"] = merkle_root
        self.manifest["updated_at"] = utc_now()
        self._save_json(self.manifest, self.manifest_path)

        return merkle_root

    def is_flash_sale_active(self) -> bool:
        """Check if a flash sale is currently active."""
        flash_sale = self.params.get("flash_sale", {})
        if not flash_sale.get("active", False):
            return False
        
        # Check if sale has expired
        end_time = flash_sale.get("end_time")
        if end_time and datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z') > end_time:
            # Sale has expired, deactivate it
            self.deactivate_flash_sale()
            return False
            
        return True

    def activate_flash_sale(self, duration_hours: int = 24, multiplier: float = 2.0) -> Dict:
        """Activate a flash sale for the specified duration."""
        start_time = utc_now()
        end_time = datetime.now(timezone.utc) + timedelta(hours=duration_hours)
        end_time_str = end_time.isoformat().replace('+00:00', 'Z')
        
        # Update params
        self.params["flash_sale"] = {
            "active": True,
            "start_time": start_time,
            "end_time": end_time_str,
            "multiplier": multiplier,
            "total_bonus_minted": 0.0,
            "transactions_affected": 0
        }
        
        # Save params
        self._save_json(self.params, self.params_path)
        
        # Update economy
        self.update_economy()
        
        # Log activation
        ledger_append({
            "event": "flash_sale_activated",
            "start_time": start_time,
            "end_time": end_time_str,
            "duration_hours": duration_hours,
            "multiplier": multiplier
        })
        
        # Broadcast promotion details to mesh
        self._broadcast_promotion_details({
            "type": "flash_sale_activated",
            "multiplier": multiplier,
            "duration_hours": duration_hours,
            "start_time": start_time,
            "end_time": end_time_str,
            "message": f"🎉 FLASH SALE ACTIVE: {multiplier}x MESH credits for {duration_hours} hours!"
        })
        
        return {
            "success": True,
            "start_time": start_time,
            "end_time": end_time_str,
            "duration_hours": duration_hours,
            "multiplier": multiplier
        }

    def deactivate_flash_sale(self) -> Dict:
        """Deactivate the current flash sale."""
        flash_sale = self.params.get("flash_sale", {})
        
        # Get stats before deactivating
        total_bonus = flash_sale.get("total_bonus_minted", 0.0)
        transactions = flash_sale.get("transactions_affected", 0)
        
        # Deactivate
        self.params["flash_sale"] = {
            "active": False,
            "start_time": None,
            "end_time": None,
            "multiplier": 1.0,
            "total_bonus_minted": 0.0,
            "transactions_affected": 0
        }
        
        # Save params
        self._save_json(self.params, self.params_path)
        
        # Update economy
        self.update_economy()
        
        # Log deactivation
        ledger_append({
            "event": "flash_sale_deactivated",
            "total_bonus_minted": total_bonus,
            "transactions_affected": transactions
        })
        
        # Broadcast deactivation to mesh
        self._broadcast_promotion_details({
            "type": "flash_sale_deactivated", 
            "total_bonus_minted": total_bonus,
            "transactions_affected": transactions,
            "message": "🏁 Flash sale ended. Thanks for participating!"
        })
        
        return {
            "success": True,
            "total_bonus_minted": total_bonus,
            "transactions_affected": transactions
        }

    def get_flash_sale_status(self) -> Dict:
        """Get current flash sale status."""
        flash_sale = self.params.get("flash_sale", {})
        active = self.is_flash_sale_active()
        
        return {
            "active": active,
            "start_time": flash_sale.get("start_time"),
            "end_time": flash_sale.get("end_time"), 
            "multiplier": flash_sale.get("multiplier", 1.0),
            "total_bonus_minted": flash_sale.get("total_bonus_minted", 0.0),
            "transactions_affected": flash_sale.get("transactions_affected", 0)
        }

    def _broadcast_promotion_details(self, promo_data: Dict) -> None:
        """Broadcast promotion details to mesh network and save notification file."""
        # Create broadcast message for mesh network
        broadcast_file = os.path.join(MESH_CREDIT_DIR, "current_promotion.json")
        
        # Save current promotion details for agents and systems to read
        with open(broadcast_file, 'w', encoding='utf-8') as f:
            json.dump({
                **promo_data,
                "broadcast_time": utc_now(),
                "qr_codes": {
                    "payment_method_1": "QR_CODE_DATA_1", 
                    "payment_method_2": "QR_CODE_DATA_2",
                    "payment_method_3": "QR_CODE_DATA_3"
                },
                "instructions": [
                    "Flash sale active: All MESH credit transactions are multiplied",
                    "Promotion applies to achievements, daily logins, raid completions",
                    "Valid for all agents and transactions during promotion period",
                    "Use reference QR codes for transactions if needed"
                ]
            }, f, indent=2, ensure_ascii=False)
            
        # Log the broadcast
        ledger_append({
            "event": "promotion_broadcast",
            "type": promo_data["type"],
            "broadcast_file": broadcast_file,
            "file_hash": sha256_file(broadcast_file)
        })

    def update_economy(self) -> None:
        """Update economy state, compute new EPOCHROOT, and append to ledger."""
        # Get all wallet balances
        total_supply = 0
        circulating_supply = 0
        staked_supply = 0
        governance_staked = 0

        for wallet_file in os.listdir(WALLETS_DIR):
            if wallet_file.endswith('.json'):
                wallet_path = os.path.join(WALLETS_DIR, wallet_file)
                with open(wallet_path, 'r', encoding='utf-8') as f:
                    wallet = json.load(f)

                total_supply += wallet["balance"]
                circulating_supply += (wallet["balance"] -
                                       wallet["staked"] - wallet["governance_staked"])
                staked_supply += wallet["staked"]
                governance_staked += wallet["governance_staked"]

        # Update manifest
        self.manifest["total_supply"] = total_supply
        self.manifest["circulating_supply"] = circulating_supply
        self.manifest["staked_supply"] = staked_supply
        self.manifest["governance_staked"] = governance_staked
        self.manifest["updated_at"] = utc_now()

        # Save updated manifest
        self._save_json(self.manifest, self.manifest_path)

        # Compute new EPOCHROOT
        epochroot = self.get_epochroot()

        # Log update
        ledger_append({
            "event": "mesh_credit_economy_updated",
            "total_supply": total_supply,
            "circulating_supply": circulating_supply,
            "staked_supply": staked_supply,
            "governance_staked": governance_staked,
            "epochroot": epochroot
        })

    def mint(self, wallet_id: str, amount: float, reason: str) -> bool:
        """Mint MESH credits to a wallet."""
        wallet_path = os.path.join(WALLETS_DIR, f"{wallet_id}.json")
        if not os.path.exists(wallet_path):
            return False

        # Check mint triggers and limits
        triggers = self.params["mint_triggers"]
        if reason not in triggers and reason != "deposit_usd":
            return False

        # Check if flash sale is active and apply multiplier
        original_amount = amount
        bonus_amount = 0.0
        flash_sale_active = self.is_flash_sale_active()
        
        if flash_sale_active and reason != "deposit_usd":  # Don't apply flash sale to USD deposits
            multiplier = self.params["flash_sale"]["multiplier"]
            bonus_amount = amount * (multiplier - 1.0)  # Calculate bonus amount
            amount = original_amount + bonus_amount  # Apply total amount
            
            # Update flash sale stats
            self.params["flash_sale"]["total_bonus_minted"] += bonus_amount
            self.params["flash_sale"]["transactions_affected"] += 1
            self._save_json(self.params, self.params_path)

        # Load wallet
        with open(wallet_path, 'r', encoding='utf-8') as f:
            wallet = json.load(f)

        # Apply mint
        wallet["balance"] += amount
        wallet["last_updated"] = utc_now()

        # Save wallet
        with open(wallet_path, 'w', encoding='utf-8') as f:
            json.dump(wallet, f, indent=2, ensure_ascii=False)

        # Update economy
        self.manifest["mint_events"] += 1
        self._save_json(self.manifest, self.manifest_path)
        self.update_economy()

        # Log mint
        mint_event = {
            "event": "mesh_credit_minted",
            "wallet_id": wallet_id,
            "amount": amount,
            "original_amount": original_amount,
            "reason": reason,
            "wallet_hash": sha256_file(wallet_path)
        }
        
        if flash_sale_active and bonus_amount > 0:
            mint_event.update({
                "flash_sale_bonus": bonus_amount,
                "multiplier": self.params["flash_sale"]["multiplier"]
            })
            
        ledger_append(mint_event)

        return True

    def burn(self, wallet_id: str, amount: float, reason: str) -> bool:
        """Burn MESH credits from a wallet."""
        wallet_path = os.path.join(WALLETS_DIR, f"{wallet_id}.json")
        if not os.path.exists(wallet_path):
            return False

        # Load wallet
        with open(wallet_path, 'r', encoding='utf-8') as f:
            wallet = json.load(f)

        # Check if enough balance (not counting staked)
        available = wallet["balance"] - wallet["staked"] - wallet["governance_staked"]
        if available < amount:
            return False

        # Apply burn
        wallet["balance"] -= amount
        wallet["last_updated"] = utc_now()

        # Save wallet
        with open(wallet_path, 'w', encoding='utf-8') as f:
            json.dump(wallet, f, indent=2, ensure_ascii=False)

        # Update economy
        self.manifest["burn_events"] += 1
        self._save_json(self.manifest, self.manifest_path)
        self.update_economy()

        # Log burn
        ledger_append({
            "event": "mesh_credit_burned",
            "wallet_id": wallet_id,
            "amount": amount,
            "reason": reason,
            "wallet_hash": sha256_file(wallet_path)
        })

        return True

    def transfer(self, from_wallet: str, to_wallet: str, amount: float, memo: str = "") -> bool:
        """Transfer MESH credits between wallets."""
        from_path = os.path.join(WALLETS_DIR, f"{from_wallet}.json")
        to_path = os.path.join(WALLETS_DIR, f"{to_wallet}.json")

        if not os.path.exists(from_path) or not os.path.exists(to_path):
            return False

        # Load wallets
        with open(from_path, 'r', encoding='utf-8') as f:
            from_data = json.load(f)

        with open(to_path, 'r', encoding='utf-8') as f:
            to_data = json.load(f)

        # Check if enough balance (not counting staked)
        available = from_data["balance"] - \
            from_data["staked"] - from_data["governance_staked"]
        if available < amount:
            return False

        # Apply transfer
        from_data["balance"] -= amount
        from_data["last_updated"] = utc_now()
        to_data["balance"] += amount
        to_data["last_updated"] = utc_now()

        # Save wallets
        with open(from_path, 'w', encoding='utf-8') as f:
            json.dump(from_data, f, indent=2, ensure_ascii=False)

        with open(to_path, 'w', encoding='utf-8') as f:
            json.dump(to_data, f, indent=2, ensure_ascii=False)

        # Update economy
        self.update_economy()

        # Log transfer
        ledger_append({
            "event": "mesh_credit_transferred",
            "from_wallet": from_wallet,
            "to_wallet": to_wallet,
            "amount": amount,
            "memo": memo,
            "from_hash": sha256_file(from_path),
            "to_hash": sha256_file(to_path)
        })

        return True

    def stake(self, wallet_id: str, amount: float, lockup_days: int = 0) -> bool:
        """Stake MESH credits in a wallet."""
        wallet_path = os.path.join(WALLETS_DIR, f"{wallet_id}.json")
        if not os.path.exists(wallet_path):
            return False

        # Load wallet
        with open(wallet_path, 'r', encoding='utf-8') as f:
            wallet = json.load(f)

        # Check if enough balance (not counting already staked)
        available = wallet["balance"] - wallet["staked"] - wallet["governance_staked"]
        if available < amount:
            return False

        # Apply stake
        wallet["staked"] += amount

        # Handle lockup if specified
        if lockup_days > 0:
            now = datetime.now(timezone.utc)
            unlock_date = (now.replace(hour=0, minute=0, second=0, microsecond=0) +
                           timedelta(days=lockup_days)).isoformat().replace('+00:00', 'Z')

            wallet.setdefault("lockups", []).append({
                "amount": amount,
                "unlock_date": unlock_date,
                "lockup_days": lockup_days
            })

        wallet["last_updated"] = utc_now()

        # Save wallet
        with open(wallet_path, 'w', encoding='utf-8') as f:
            json.dump(wallet, f, indent=2, ensure_ascii=False)

        # Update economy
        self.update_economy()

        # Log stake
        ledger_append({
            "event": "mesh_credit_staked",
            "wallet_id": wallet_id,
            "amount": amount,
            "lockup_days": lockup_days,
            "wallet_hash": sha256_file(wallet_path)
        })

        return True

    def unstake(self, wallet_id: str, amount: float) -> bool:
        """Unstake MESH credits in a wallet."""
        wallet_path = os.path.join(WALLETS_DIR, f"{wallet_id}.json")
        if not os.path.exists(wallet_path):
            return False

        # Load wallet
        with open(wallet_path, 'r', encoding='utf-8') as f:
            wallet = json.load(f)

        # Check lockups first
        if "lockups" in wallet:
            now = datetime.now(timezone.utc)
            unlocked = []
            still_locked = []

            for lockup in wallet["lockups"]:
                unlock_date = datetime.fromisoformat(
                    lockup["unlock_date"].replace('Z', '+00:00'))
                if now >= unlock_date:
                    unlocked.append(lockup)
                else:
                    still_locked.append(lockup)

            # Process unlocked amounts
            for lockup in unlocked:
                ledger_append({
                    "event": "mesh_credit_lockup_expired",
                    "wallet_id": wallet_id,
                    "amount": lockup["amount"],
                    "lockup_days": lockup["lockup_days"]
                })

            wallet["lockups"] = still_locked

        # Check if enough staked
        if wallet["staked"] < amount:
            return False

        # Apply unstake
        wallet["staked"] -= amount
        wallet["last_updated"] = utc_now()

        # Save wallet
        with open(wallet_path, 'w', encoding='utf-8') as f:
            json.dump(wallet, f, indent=2, ensure_ascii=False)

        # Update economy
        self.update_economy()

        # Log unstake
        ledger_append({
            "event": "mesh_credit_unstaked",
            "wallet_id": wallet_id,
            "amount": amount,
            "wallet_hash": sha256_file(wallet_path)
        })

        return True

    def governance_stake(self, wallet_id: str, amount: float) -> bool:
        """Stake MESH credits for governance."""
        wallet_path = os.path.join(WALLETS_DIR, f"{wallet_id}.json")
        if not os.path.exists(wallet_path):
            return False

        # Load wallet
        with open(wallet_path, 'r', encoding='utf-8') as f:
            wallet = json.load(f)

        # Check if enough balance (not counting already staked)
        available = wallet["balance"] - wallet["staked"] - wallet["governance_staked"]
        if available < amount:
            return False

        # Apply governance stake
        wallet["governance_staked"] += amount
        wallet["last_updated"] = utc_now()

        # Calculate vote weight
        vote_weight = amount / \
            self.pricing["item_categories"]["governance"]["vote_weight"]
        wallet["vote_weight"] = wallet["governance_staked"] / \
            self.pricing["item_categories"]["governance"]["vote_weight"]

        # Save wallet
        with open(wallet_path, 'w', encoding='utf-8') as f:
            json.dump(wallet, f, indent=2, ensure_ascii=False)

        # Update economy
        self.update_economy()

        # Log governance stake
        ledger_append({
            "event": "mesh_credit_governance_staked",
            "wallet_id": wallet_id,
            "amount": amount,
            "vote_weight": vote_weight,
            "wallet_hash": sha256_file(wallet_path)
        })

        return True

    def governance_unstake(self, wallet_id: str, amount: float) -> bool:
        """Unstake MESH credits from governance."""
        wallet_path = os.path.join(WALLETS_DIR, f"{wallet_id}.json")
        if not os.path.exists(wallet_path):
            return False

        # Load wallet
        with open(wallet_path, 'r', encoding='utf-8') as f:
            wallet = json.load(f)

        # Check if enough governance staked
        if wallet["governance_staked"] < amount:
            return False

        # Apply governance unstake
        wallet["governance_staked"] -= amount
        wallet["last_updated"] = utc_now()

        # Recalculate vote weight
        wallet["vote_weight"] = wallet["governance_staked"] / \
            self.pricing["item_categories"]["governance"]["vote_weight"]

        # Save wallet
        with open(wallet_path, 'w', encoding='utf-8') as f:
            json.dump(wallet, f, indent=2, ensure_ascii=False)

        # Update economy
        self.update_economy()

        # Log governance unstake
        ledger_append({
            "event": "mesh_credit_governance_unstaked",
            "wallet_id": wallet_id,
            "amount": amount,
            "new_vote_weight": wallet["vote_weight"],
            "wallet_hash": sha256_file(wallet_path)
        })

        return True

    def calculate_yield(self, wallet_id: str) -> Dict:
        """Calculate yield for a wallet based on staking and governance."""
        wallet_path = os.path.join(WALLETS_DIR, f"{wallet_id}.json")
        if not os.path.exists(wallet_path):
            return {"error": "Wallet not found"}

        # Load wallet
        with open(wallet_path, 'r', encoding='utf-8') as f:
            wallet = json.load(f)

        # Base parameters
        base_apy = self.yield_curve["base_apy"]
        max_apy = self.yield_curve["max_apy"]
        governance_bonus = self.yield_curve["governance_bonus"]

        # Calculate tier bonus
        tier_bonus = 0
        for tier in sorted(self.yield_curve["stake_tiers"], key=lambda x: x["threshold"], reverse=True):
            if wallet["staked"] >= tier["threshold"]:
                tier_bonus = tier["bonus"]
                break

        # Calculate lockup bonus
        lockup_bonus = 0
        if "lockups" in wallet and wallet["lockups"]:
            # Find highest lockup bonus
            for lockup in wallet["lockups"]:
                days = lockup["lockup_days"]
                if days >= 365 and "365_days" in self.yield_curve["lockup_bonus"]:
                    lockup_bonus = max(
                        lockup_bonus, self.yield_curve["lockup_bonus"]["365_days"])
                elif days >= 180 and "180_days" in self.yield_curve["lockup_bonus"]:
                    lockup_bonus = max(
                        lockup_bonus, self.yield_curve["lockup_bonus"]["180_days"])
                elif days >= 90 and "90_days" in self.yield_curve["lockup_bonus"]:
                    lockup_bonus = max(
                        lockup_bonus, self.yield_curve["lockup_bonus"]["90_days"])
                elif days >= 30 and "30_days" in self.yield_curve["lockup_bonus"]:
                    lockup_bonus = max(
                        lockup_bonus, self.yield_curve["lockup_bonus"]["30_days"])

        # Calculate governance bonus if applicable
        gov_bonus = governance_bonus if wallet["governance_staked"] > 0 else 0

        # Total APY (capped at max_apy)
        total_apy = min(base_apy + tier_bonus + lockup_bonus + gov_bonus, max_apy)

        # Calculate daily yield
        daily_rate = total_apy / 365
        daily_yield_staked = wallet["staked"] * daily_rate
        daily_yield_governance = wallet["governance_staked"] * daily_rate
        total_daily_yield = daily_yield_staked + daily_yield_governance

        # Calculate epoch yield (typically 30 days)
        epoch_days = self.yield_curve["epoch_length_days"]
        epoch_yield = total_daily_yield * epoch_days

        return {
            "wallet_id": wallet_id,
            "staked": wallet["staked"],
            "governance_staked": wallet["governance_staked"],
            "base_apy": base_apy,
            "tier_bonus": tier_bonus,
            "lockup_bonus": lockup_bonus,
            "governance_bonus": gov_bonus,
            "total_apy": total_apy,
            "daily_yield": total_daily_yield,
            "epoch_yield": epoch_yield,
            "next_epoch_date": self._calculate_next_epoch_date()
        }

    def _calculate_next_epoch_date(self) -> str:
        """Calculate the date of the next epoch."""
        epoch_days = self.yield_curve["epoch_length_days"]
        current_epochs = self.manifest["epochs_completed"]

        # Assuming epochs start from script creation date
        start_date = datetime.fromisoformat(
            self.manifest["created_at"].replace('Z', '+00:00'))
        next_epoch_date = start_date + timedelta(days=(current_epochs + 1) * epoch_days)

        return next_epoch_date.isoformat().replace('+00:00', 'Z')

    def process_epoch(self) -> Dict:
        """Process yield for all staked wallets at the end of an epoch."""
        epoch_results = {
            "epoch_number": self.manifest["epochs_completed"] + 1,
            "processed_at": utc_now(),
            "wallets_processed": 0,
            "total_yield_distributed": 0,
            "wallet_details": []
        }

        # Process each wallet
        for wallet_file in os.listdir(WALLETS_DIR):
            if wallet_file.endswith('.json'):
                wallet_id = wallet_file.replace('.json', '')
                wallet_path = os.path.join(WALLETS_DIR, wallet_file)

                # Calculate yield
                yield_info = self.calculate_yield(wallet_id)
                if "error" in yield_info:
                    continue

                # Load wallet
                with open(wallet_path, 'r', encoding='utf-8') as f:
                    wallet = json.load(f)

                # Apply yield
                epoch_yield = yield_info["epoch_yield"]
                wallet["balance"] += epoch_yield
                wallet["last_yield"] = epoch_yield
                wallet["last_yield_date"] = utc_now()
                wallet["total_yield_earned"] = wallet.get(
                    "total_yield_earned", 0) + epoch_yield
                wallet["last_updated"] = utc_now()

                # Save wallet
                with open(wallet_path, 'w', encoding='utf-8') as f:
                    json.dump(wallet, f, indent=2, ensure_ascii=False)

                # Update epoch results
                epoch_results["wallets_processed"] += 1
                epoch_results["total_yield_distributed"] += epoch_yield
                epoch_results["wallet_details"].append({
                    "wallet_id": wallet_id,
                    "yield_earned": epoch_yield,
                    "new_balance": wallet["balance"],
                    "staked": wallet["staked"],
                    "governance_staked": wallet["governance_staked"]
                })

        # Update manifest
        self.manifest["epochs_completed"] += 1
        self.manifest["updated_at"] = utc_now()
        self._save_json(self.manifest, self.manifest_path)

        # Store epoch results in CAS
        epoch_hash = cas_store(epoch_results)

        # Update economy
        self.update_economy()

        # Log epoch processing
        ledger_append({
            "event": "mesh_credit_epoch_processed",
            "epoch_number": epoch_results["epoch_number"],
            "wallets_processed": epoch_results["wallets_processed"],
            "total_yield_distributed": epoch_results["total_yield_distributed"],
            "epoch_hash": epoch_hash
        })

        return epoch_results

    def get_item_price(self, item_type: str, rarity: str) -> Optional[float]:
        """Get the price for an item based on type and rarity."""
        if item_type not in self.pricing["item_categories"]:
            return None

        category = self.pricing["item_categories"][item_type]
        if rarity not in category:
            return None

        return category[rarity]

    def process_purchase(self, wallet_id: str, item_id: str, item_type: str, rarity: str) -> Dict:
        """Process a purchase of an item."""
        wallet_path = os.path.join(WALLETS_DIR, f"{wallet_id}.json")
        if not os.path.exists(wallet_path):
            return {"error": "Wallet not found"}

        # Get item price
        price = self.get_item_price(item_type, rarity)
        if price is None:
            return {"error": "Invalid item type or rarity"}

        # Load wallet
        with open(wallet_path, 'r', encoding='utf-8') as f:
            wallet = json.load(f)

        # Check if enough available balance
        available = wallet["balance"] - wallet["staked"] - wallet["governance_staked"]
        if available < price:
            return {"error": "Insufficient balance"}

        # Process purchase (burn MESH)
        if self.params["burn_triggers"].get(f"{item_type}_purchase", True):
            self.burn(wallet_id, price, f"purchase_{item_type}")
        else:
            # Just deduct without burning
            wallet["balance"] -= price
            wallet["last_updated"] = utc_now()

            with open(wallet_path, 'w', encoding='utf-8') as f:
                json.dump(wallet, f, indent=2, ensure_ascii=False)

        # Record purchase
        purchase_record = {
            "wallet_id": wallet_id,
            "item_id": item_id,
            "item_type": item_type,
            "rarity": rarity,
            "price": price,
            "purchased_at": utc_now()
        }

        purchase_hash = cas_store(purchase_record)

        # Add to wallet's purchase history
        wallet.setdefault("purchases", []).append({
            "item_id": item_id,
            "price": price,
            "date": utc_now(),
            "record_hash": purchase_hash
        })

        with open(wallet_path, 'w', encoding='utf-8') as f:
            json.dump(wallet, f, indent=2, ensure_ascii=False)

        # Update economy
        self.update_economy()

        # Log purchase
        ledger_append({
            "event": "mesh_credit_purchase",
            "wallet_id": wallet_id,
            "item_id": item_id,
            "item_type": item_type,
            "rarity": rarity,
            "price": price,
            "purchase_hash": purchase_hash
        })

        return {"success": True, "price": price, "purchase_hash": purchase_hash}

    def verify_file_integrity(self, file_path: str) -> Dict:
        """Verify a file against its seal."""
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        # Check if it's a JSON file
        if not file_path.endswith('.json'):
            return {"error": "Not a JSON file"}

        # Check if seal exists
        seal_path = file_path.replace('.json', '.seal.json')
        if not os.path.exists(seal_path):
            return {"error": "Seal file not found"}

        # Calculate file hash
        file_hash = sha256_file(file_path)

        # Load seal
        with open(seal_path, 'r', encoding='utf-8') as f:
            seal = json.load(f)

        # Verify hash
        if file_hash != seal.get("sha256"):
            return {
                "verified": False,
                "file": os.path.basename(file_path),
                "calculated_hash": file_hash,
                "seal_hash": seal.get("sha256"),
                "error": "Hash mismatch"
            }

        return {
            "verified": True,
            "file": os.path.basename(file_path),
            "hash": file_hash,
            "seal_date": seal.get("ts")
        }

    def reseal_file(self, file_path: str) -> Dict:
        """Create a new seal for a file."""
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        # Check if it's a JSON file
        if not file_path.endswith('.json'):
            return {"error": "Not a JSON file"}

        # Calculate file hash
        file_hash = sha256_file(file_path)

        # Create new seal
        seal = {
            "ts": utc_now(),
            "file": os.path.basename(file_path),
            "sha256": file_hash
        }

        # Save seal
        seal_path = file_path.replace('.json', '.seal.json')
        with open(seal_path, 'w', encoding='utf-8') as f:
            json.dump(seal, f, ensure_ascii=False, indent=2)

        # Log reseal
        ledger_append({
            "event": "file_resealed",
            "file": os.path.basename(file_path),
            "hash": file_hash
        })

        return {
            "resealed": True,
            "file": os.path.basename(file_path),
            "hash": file_hash
        }

# ---------- Wallet Management ----------


class MeshWallet:
    def __init__(self, wallet_id: str = None):
        self.wallets_dir = WALLETS_DIR
        self.wallet_id = wallet_id
        self.wallet_path = os.path.join(
            self.wallets_dir, f"{wallet_id}.json") if wallet_id else None

    def create(self, wallet_id: str, initial_balance: float = 0) -> Dict:
        """Create a new wallet."""
        wallet_path = os.path.join(self.wallets_dir, f"{wallet_id}.json")
        if os.path.exists(wallet_path):
            return {"error": "Wallet already exists"}

        # Generate a seed for the wallet
        seed = sha256_str(f"{wallet_id}|{utc_now()}|MESH")

        # Create wallet
        wallet = {
            "id": wallet_id,
            "created_at": utc_now(),
            "last_updated": utc_now(),
            "balance": initial_balance,
            "staked": 0,
            "governance_staked": 0,
            "vote_weight": 0,
            "seed": seed
        }

        # Save wallet
        with open(wallet_path, 'w', encoding='utf-8') as f:
            json.dump(wallet, f, indent=2, ensure_ascii=False)

        # Log creation
        ledger_append({
            "event": "mesh_wallet_created",
            "wallet_id": wallet_id,
            "initial_balance": initial_balance,
            "wallet_hash": sha256_file(wallet_path)
        })

        self.wallet_id = wallet_id
        self.wallet_path = wallet_path

        return {
            "created": True,
            "wallet_id": wallet_id,
            "initial_balance": initial_balance,
            "seed": seed
        }

    def get(self, wallet_id: str = None) -> Dict:
        """Get wallet details."""
        wid = wallet_id or self.wallet_id
        if not wid:
            return {"error": "No wallet ID provided"}

        wallet_path = os.path.join(self.wallets_dir, f"{wid}.json")
        if not os.path.exists(wallet_path):
            return {"error": "Wallet not found"}

        # Load wallet
        with open(wallet_path, 'r', encoding='utf-8') as f:
            wallet = json.load(f)

        # Calculate available balance
        available = wallet["balance"] - wallet["staked"] - wallet["governance_staked"]

        # Add available balance to response
        wallet["available_balance"] = available

        return wallet

    def list_all(self) -> List[Dict]:
        """List all wallets."""
        wallets = []
        for wallet_file in os.listdir(self.wallets_dir):
            if wallet_file.endswith('.json'):
                wallet_id = wallet_file.replace('.json', '')
                wallet_data = self.get(wallet_id)
                if "error" not in wallet_data:
                    wallets.append({
                        "id": wallet_id,
                        "balance": wallet_data["balance"],
                        "available": wallet_data["available_balance"],
                        "staked": wallet_data["staked"],
                        "governance_staked": wallet_data["governance_staked"],
                        "vote_weight": wallet_data.get("vote_weight", 0)
                    })

        return wallets

    def deposit_usd(self, wallet_id: str, usd_amount: float) -> Dict:
        """Deposit USD and convert to MESH."""
        wid = wallet_id or self.wallet_id
        if not wid:
            return {"error": "No wallet ID provided"}

        # Get exchange rate
        mesh_credit = MeshCredit()
        rate = mesh_credit.pricing["usd_to_mesh_rate"]

        # Calculate MESH amount
        mesh_amount = usd_amount * rate

        # Mint MESH to wallet
        success = mesh_credit.mint(wid, mesh_amount, "deposit_usd")
        if not success:
            return {"error": "Failed to mint MESH"}

        return {
            "success": True,
            "usd_amount": usd_amount,
            "mesh_amount": mesh_amount,
            "rate": rate,
            "wallet_id": wid
        }

# ---------- Main Functions ----------


def init_mesh_credit():
    """Initialize the Mesh Credit system."""
    mesh_credit = MeshCredit()
    epochroot = mesh_credit.get_epochroot()

    print(f"Mesh Credit economy initialized.")
    print(f"EPOCHROOT: {epochroot}")
    print(f"Check {MESH_CREDIT_DIR} for config files.")
    return mesh_credit


def create_wallet(wallet_id: str, initial_balance: float = 0):
    """Create a new wallet."""
    wallet = MeshWallet()
    result = wallet.create(wallet_id, initial_balance)

    if "error" in result:
        print(f"Error: {result['error']}")
        return None

    print(f"Wallet created: {wallet_id}")
    print(f"Initial balance: {initial_balance} MESH")
    print(f"Seed: {result['seed']}")
    return wallet


def get_wallet(wallet_id: str):
    """Get wallet details."""
    wallet = MeshWallet()
    result = wallet.get(wallet_id)

    if "error" in result:
        print(f"Error: {result['error']}")
        return None

    print(f"Wallet: {wallet_id}")
    print(f"Balance: {result['balance']} MESH")
    print(f"Available: {result['available_balance']} MESH")
    print(f"Staked: {result['staked']} MESH")
    print(f"Governance Staked: {result['governance_staked']} MESH")
    if "vote_weight" in result:
        print(f"Vote Weight: {result['vote_weight']}")

    return result


def deposit_usd(wallet_id: str, usd_amount: float):
    """Deposit USD to wallet and convert to MESH."""
    wallet = MeshWallet()
    result = wallet.deposit_usd(wallet_id, usd_amount)

    if "error" in result:
        print(f"Error: {result['error']}")
        return None

    print(f"Deposited: ${usd_amount:.2f} USD")
    print(f"Converted to: {result['mesh_amount']} MESH")
    print(f"Rate: 1 USD = {result['rate']} MESH")

    return result


def transfer_mesh(from_wallet: str, to_wallet: str, amount: float, memo: str = ""):
    """Transfer MESH between wallets."""
    mesh_credit = MeshCredit()
    result = mesh_credit.transfer(from_wallet, to_wallet, amount, memo)

    if not result:
        print("Transfer failed. Check wallet IDs and balance.")
        return False

    print(f"Transferred {amount} MESH from {from_wallet} to {to_wallet}")
    if memo:
        print(f"Memo: {memo}")

    return True


def stake_mesh(wallet_id: str, amount: float, lockup_days: int = 0):
    """Stake MESH in a wallet."""
    mesh_credit = MeshCredit()
    result = mesh_credit.stake(wallet_id, amount, lockup_days)

    if not result:
        print("Staking failed. Check wallet ID and available balance.")
        return False

    print(f"Staked {amount} MESH in wallet {wallet_id}")
    if lockup_days > 0:
        print(f"Lockup period: {lockup_days} days")

    return True


def unstake_mesh(wallet_id: str, amount: float):
    """Unstake MESH from a wallet."""
    mesh_credit = MeshCredit()
    result = mesh_credit.unstake(wallet_id, amount)

    if not result:
        print("Unstaking failed. Check wallet ID and staked amount.")
        return False

    print(f"Unstaked {amount} MESH from wallet {wallet_id}")
    return True


def governance_stake(wallet_id: str, amount: float):
    """Stake MESH for governance."""
    mesh_credit = MeshCredit()
    result = mesh_credit.governance_stake(wallet_id, amount)

    if not result:
        print("Governance staking failed. Check wallet ID and available balance.")
        return False

    print(f"Staked {amount} MESH for governance in wallet {wallet_id}")

    # Get updated wallet
    wallet = MeshWallet().get(wallet_id)
    if "vote_weight" in wallet:
        print(f"New vote weight: {wallet['vote_weight']}")

    return True


def governance_unstake(wallet_id: str, amount: float):
    """Unstake MESH from governance."""
    mesh_credit = MeshCredit()
    result = mesh_credit.governance_unstake(wallet_id, amount)

    if not result:
        print("Governance unstaking failed. Check wallet ID and staked amount.")
        return False

    print(f"Unstaked {amount} MESH from governance in wallet {wallet_id}")

    # Get updated wallet
    wallet = MeshWallet().get(wallet_id)
    if "vote_weight" in wallet:
        print(f"New vote weight: {wallet['vote_weight']}")

    return True


def calculate_yield(wallet_id: str):
    """Calculate yield for a wallet."""
    mesh_credit = MeshCredit()
    result = mesh_credit.calculate_yield(wallet_id)

    if "error" in result:
        print(f"Error: {result['error']}")
        return None

    print(f"Yield calculation for wallet {wallet_id}:")
    print(f"Staked: {result['staked']} MESH")
    print(f"Governance Staked: {result['governance_staked']} MESH")
    print(f"Base APY: {result['base_apy']:.2%}")
    print(f"Tier Bonus: {result['tier_bonus']:.2%}")
    print(f"Lockup Bonus: {result['lockup_bonus']:.2%}")
    print(f"Governance Bonus: {result['governance_bonus']:.2%}")
    print(f"Total APY: {result['total_apy']:.2%}")
    print(f"Daily Yield: {result['daily_yield']:.6f} MESH")
    print(f"Epoch Yield: {result['epoch_yield']:.6f} MESH")
    print(f"Next Epoch Date: {result['next_epoch_date']}")

    return result


def process_epoch():
    """Process an epoch and distribute yield."""
    mesh_credit = MeshCredit()
    result = mesh_credit.process_epoch()

    print(f"Processed Epoch #{result['epoch_number']}")
    print(f"Wallets Processed: {result['wallets_processed']}")
    print(f"Total Yield Distributed: {result['total_yield_distributed']} MESH")

    return result


def verify_file(file_path: str):
    """Verify a file against its seal."""
    mesh_credit = MeshCredit()
    result = mesh_credit.verify_file_integrity(file_path)

    if "error" in result:
        print(f"Error: {result['error']}")
        return None

    if result["verified"]:
        print(f"✓ Verified: {result['file']}")
        print(f"Hash: {result['hash']}")
        print(f"Seal Date: {result['seal_date']}")
    else:
        print(f"✗ Verification Failed: {result['file']}")
        print(f"Calculated Hash: {result['calculated_hash']}")
        print(f"Seal Hash: {result['seal_hash']}")

    return result


def reseal_file(file_path: str):
    """Reseal a file with a new hash."""
    mesh_credit = MeshCredit()
    result = mesh_credit.reseal_file(file_path)

    if "error" in result:
        print(f"Error: {result['error']}")
        return None

    print(f"✓ Resealed: {result['file']}")
    print(f"New Hash: {result['hash']}")

    return result


def buy_item(wallet_id: str, item_id: str, item_type: str, rarity: str):
    """Buy an item with MESH."""
    mesh_credit = MeshCredit()
    result = mesh_credit.process_purchase(wallet_id, item_id, item_type, rarity)

    if "error" in result:
        print(f"Error: {result['error']}")
        return None

    print(f"✓ Purchased: {item_id}")
    print(f"Type: {item_type}")
    print(f"Rarity: {rarity}")
    print(f"Price: {result['price']} MESH")
    print(f"Purchase Hash: {result['purchase_hash']}")

    return result


def update_economy():
    """Update the economy state and compute new EPOCHROOT."""
    mesh_credit = MeshCredit()
    epochroot = mesh_credit.update_economy()

    print(f"Economy updated.")
    print(f"EPOCHROOT: {mesh_credit.manifest['epochroot']}")

    return epochroot


def activate_flash_sale(duration_hours: int = 24, multiplier: float = 2.0):
    """Activate a flash sale."""
    mesh_credit = MeshCredit()
    result = mesh_credit.activate_flash_sale(duration_hours, multiplier)
    
    if result.get("success"):
        print(f"🎉 Flash Sale Activated!")
        print(f"📅 Start Time: {result['start_time']}")
        print(f"⏰ End Time: {result['end_time']}")
        print(f"🔥 Duration: {result['duration_hours']} hours") 
        print(f"💰 Multiplier: {result['multiplier']}x MESH credits")
        print(f"🎯 Promotion: Double mesh credit for all agents and transactions!")
    else:
        print("Failed to activate flash sale")
        
    return result


def deactivate_flash_sale():
    """Deactivate the current flash sale."""
    mesh_credit = MeshCredit()
    result = mesh_credit.deactivate_flash_sale()
    
    if result.get("success"):
        print(f"🏁 Flash Sale Deactivated!")
        print(f"💎 Total Bonus Minted: {result['total_bonus_minted']} MESH")
        print(f"📊 Transactions Affected: {result['transactions_affected']}")
    else:
        print("Failed to deactivate flash sale")
        
    return result


def flash_sale_status():
    """Get current flash sale status."""
    mesh_credit = MeshCredit()
    status = mesh_credit.get_flash_sale_status()
    
    if status["active"]:
        print(f"🔥 Flash Sale ACTIVE!")
        print(f"📅 Start Time: {status['start_time']}")
        print(f"⏰ End Time: {status['end_time']}")
        print(f"💰 Multiplier: {status['multiplier']}x MESH credits")
        print(f"💎 Total Bonus Minted: {status['total_bonus_minted']} MESH")
        print(f"📊 Transactions Affected: {status['transactions_affected']}")
    else:
        print(f"💤 No Flash Sale Active")
        if status.get('total_bonus_minted', 0) > 0:
            print(f"📊 Last Sale Stats:")
            print(f"   💎 Total Bonus Minted: {status['total_bonus_minted']} MESH") 
            print(f"   📊 Transactions Affected: {status['transactions_affected']}")
    
    return status


if __name__ == "__main__":
    # Command-line interface
    import argparse

    parser = argparse.ArgumentParser(description="Mesh Credit Economy Management")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Mesh Credit economy")

    # Wallet commands
    wallet_parser = subparsers.add_parser("wallet", help="Wallet management")
    wallet_subparsers = wallet_parser.add_subparsers(
        dest="wallet_command", help="Wallet command")

    create_parser = wallet_subparsers.add_parser("create", help="Create a new wallet")
    create_parser.add_argument("wallet_id", help="Wallet ID")
    create_parser.add_argument("--balance", type=float,
                               default=0, help="Initial balance")

    get_parser = wallet_subparsers.add_parser("get", help="Get wallet details")
    get_parser.add_argument("wallet_id", help="Wallet ID")

    list_parser = wallet_subparsers.add_parser("list", help="List all wallets")

    deposit_parser = wallet_subparsers.add_parser(
        "deposit", help="Deposit USD to wallet")
    deposit_parser.add_argument("wallet_id", help="Wallet ID")
    deposit_parser.add_argument("amount", type=float, help="USD amount")

    transfer_parser = wallet_subparsers.add_parser(
        "transfer", help="Transfer MESH between wallets")
    transfer_parser.add_argument("from_wallet", help="Source wallet ID")
    transfer_parser.add_argument("to_wallet", help="Destination wallet ID")
    transfer_parser.add_argument("amount", type=float, help="MESH amount")
    transfer_parser.add_argument("--memo", default="", help="Transfer memo")

    # Staking commands
    stake_parser = subparsers.add_parser("stake", help="Staking management")
    stake_subparsers = stake_parser.add_subparsers(
        dest="stake_command", help="Stake command")

    stake_mesh_parser = stake_subparsers.add_parser("add", help="Stake MESH")
    stake_mesh_parser.add_argument("wallet_id", help="Wallet ID")
    stake_mesh_parser.add_argument("amount", type=float, help="MESH amount")
    stake_mesh_parser.add_argument(
        "--lockup", type=int, default=0, help="Lockup period in days")

    unstake_mesh_parser = stake_subparsers.add_parser("remove", help="Unstake MESH")
    unstake_mesh_parser.add_argument("wallet_id", help="Wallet ID")
    unstake_mesh_parser.add_argument("amount", type=float, help="MESH amount")

    yield_parser = stake_subparsers.add_parser("yield", help="Calculate yield")
    yield_parser.add_argument("wallet_id", help="Wallet ID")

    epoch_parser = stake_subparsers.add_parser("epoch", help="Process epoch")

    # Governance commands
    gov_parser = subparsers.add_parser("governance", help="Governance management")
    gov_subparsers = gov_parser.add_subparsers(
        dest="gov_command", help="Governance command")

    gov_stake_parser = gov_subparsers.add_parser("stake", help="Stake for governance")
    gov_stake_parser.add_argument("wallet_id", help="Wallet ID")
    gov_stake_parser.add_argument("amount", type=float, help="MESH amount")

    gov_unstake_parser = gov_subparsers.add_parser(
        "unstake", help="Unstake from governance")
    gov_unstake_parser.add_argument("wallet_id", help="Wallet ID")
    gov_unstake_parser.add_argument("amount", type=float, help="MESH amount")

    # Shop commands
    shop_parser = subparsers.add_parser("shop", help="Shop management")
    shop_subparsers = shop_parser.add_subparsers(
        dest="shop_command", help="Shop command")

    buy_parser = shop_subparsers.add_parser("buy", help="Buy item")
    buy_parser.add_argument("wallet_id", help="Wallet ID")
    buy_parser.add_argument("item_id", help="Item ID")
    buy_parser.add_argument("item_type", choices=["character_cosmetic", "gear_cosmetic", "time_saver"],
                            help="Item type")
    buy_parser.add_argument("rarity", help="Item rarity")

    # Verification commands
    verify_parser = subparsers.add_parser("verify", help="Verification tools")
    verify_subparsers = verify_parser.add_subparsers(
        dest="verify_command", help="Verify command")

    file_verify_parser = verify_subparsers.add_parser(
        "file", help="Verify file integrity")
    file_verify_parser.add_argument("file_path", help="Path to file")

    reseal_parser = verify_subparsers.add_parser("reseal", help="Reseal a file")
    reseal_parser.add_argument("file_path", help="Path to file")

    # Economy commands
    economy_parser = subparsers.add_parser("economy", help="Economy management")
    economy_subparsers = economy_parser.add_subparsers(
        dest="economy_command", help="Economy command")

    update_parser = economy_subparsers.add_parser("update", help="Update economy state")

    # Promotion/Flash Sale commands
    promo_parser = subparsers.add_parser("promotion", help="Flash sale/promotion management")
    promo_subparsers = promo_parser.add_subparsers(
        dest="promo_command", help="Promotion command")

    activate_parser = promo_subparsers.add_parser("activate", help="Activate flash sale")
    activate_parser.add_argument("--duration", type=int, default=24, 
                                help="Duration in hours (default: 24)")
    activate_parser.add_argument("--multiplier", type=float, default=2.0,
                                help="Credit multiplier (default: 2.0)")

    deactivate_parser = promo_subparsers.add_parser("deactivate", help="Deactivate flash sale")

    status_parser = promo_subparsers.add_parser("status", help="Check flash sale status")

    args = parser.parse_args()

    # Process commands
    if args.command == "init":
        init_mesh_credit()

    elif args.command == "wallet":
        if args.wallet_command == "create":
            create_wallet(args.wallet_id, args.balance)
        elif args.wallet_command == "get":
            get_wallet(args.wallet_id)
        elif args.wallet_command == "list":
            wallets = MeshWallet().list_all()
            print(f"Found {len(wallets)} wallets:")
            for wallet in wallets:
                print(f"ID: {wallet['id']}")
                print(f"  Balance: {wallet['balance']} MESH")
                print(f"  Available: {wallet['available']} MESH")
                print(f"  Staked: {wallet['staked']} MESH")
                print(f"  Governance: {wallet['governance_staked']} MESH")
                print(f"  Vote Weight: {wallet['vote_weight']}")
                print()
        elif args.wallet_command == "deposit":
            deposit_usd(args.wallet_id, args.amount)
        elif args.wallet_command == "transfer":
            transfer_mesh(args.from_wallet, args.to_wallet, args.amount, args.memo)

    elif args.command == "stake":
        if args.stake_command == "add":
            stake_mesh(args.wallet_id, args.amount, args.lockup)
        elif args.stake_command == "remove":
            unstake_mesh(args.wallet_id, args.amount)
        elif args.stake_command == "yield":
            calculate_yield(args.wallet_id)
        elif args.stake_command == "epoch":
            process_epoch()

    elif args.command == "governance":
        if args.gov_command == "stake":
            governance_stake(args.wallet_id, args.amount)
        elif args.gov_command == "unstake":
            governance_unstake(args.wallet_id, args.amount)

    elif args.command == "shop":
        if args.shop_command == "buy":
            buy_item(args.wallet_id, args.item_id, args.item_type, args.rarity)

    elif args.command == "verify":
        if args.verify_command == "file":
            verify_file(args.file_path)
        elif args.verify_command == "reseal":
            reseal_file(args.file_path)

    elif args.command == "economy":
        if args.economy_command == "update":
            update_economy()

    elif args.command == "promotion":
        if args.promo_command == "activate":
            activate_flash_sale(args.duration, args.multiplier)
        elif args.promo_command == "deactivate":
            deactivate_flash_sale()
        elif args.promo_command == "status":
            flash_sale_status()

    else:
        parser.print_help()
