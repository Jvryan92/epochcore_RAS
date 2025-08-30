#!/usr/bin/env python3
"""
MeshCredit Banking System

This module provides banking functionality for MeshCredit assets, allowing for:
1. Account management (create, view, update)
2. Transaction processing (deposits, withdrawals, transfers)
3. Interest accrual based on compounding methods
4. Asset valuation and reporting
5. Integration with the Capsule Compounding system

Works alongside the Capsule Compounding Engine to provide financial services
for the EpochCore ecosystem.
"""

import json
import hashlib
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] MeshCreditBank: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("meshcredit_bank.log")],
)
logger = logging.getLogger("meshcredit_bank")

# Integration constants
ROOT = Path(os.getcwd())
LEDGER_DIR = ROOT / "ledger"
BANK_DIR = LEDGER_DIR / "meshcredit_bank"
ACCOUNTS_DIR = BANK_DIR / "accounts"
TRANSACTIONS_DIR = BANK_DIR / "transactions"
ASSET_CLASSES = ["liquid", "staked", "compound", "governance"]

# Ensure directories exist
BANK_DIR.mkdir(parents=True, exist_ok=True)
ACCOUNTS_DIR.mkdir(parents=True, exist_ok=True)
TRANSACTIONS_DIR.mkdir(parents=True, exist_ok=True)

# Default interest rates for different asset classes (annual rates)
DEFAULT_INTEREST_RATES = {
    "liquid": 0.005,      # 0.5% APY for liquid assets
    "staked": 0.025,      # 2.5% APY for staked assets
    "compound": 0.04,     # 4.0% APY for assets in compounding strategies
    "governance": 0.03,   # 3.0% APY for governance tokens
}

# Transaction fees (as percentage)
TRANSACTION_FEES = {
    "transfer": 0.001,    # 0.1% fee for transfers
    "withdraw": 0.002,    # 0.2% fee for withdrawals
    "compound": 0.005,    # 0.5% fee for compounding operations
}


class MeshCreditBank:
    """Banking system for managing MeshCredit assets"""

    def __init__(
        self,
        bank_name: str = "EpochCore MeshCredit Bank",
        interest_rates: Optional[Dict[str, float]] = None,
        transaction_fees: Optional[Dict[str, float]] = None,
        capsule_integration: bool = True,
    ):
        """Initialize the MeshCredit banking system"""
        self.bank_name = bank_name
        self.interest_rates = interest_rates or DEFAULT_INTEREST_RATES
        self.transaction_fees = transaction_fees or TRANSACTION_FEES
        self.capsule_integration = capsule_integration
        
        # Load bank metadata
        self.metadata = self._load_metadata()
        
        # Create bank ID if not exists
        if "bank_id" not in self.metadata:
            self.metadata["bank_id"] = hashlib.sha256(
                f"{bank_name}:{time.time()}".encode()
            ).hexdigest()
            self._save_metadata()
        
        logger.info(f"MeshCredit Bank initialized: {bank_name} [ID: {self.metadata['bank_id'][:8]}]")
        logger.info(f"Interest rates: {self.interest_rates}")
        
        # Cache for account data
        self._account_cache = {}
        
    def _load_metadata(self) -> Dict[str, Any]:
        """Load bank metadata from file"""
        metadata_file = BANK_DIR / "bank_metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logger.warning(f"Could not load bank metadata from {metadata_file}")
        
        # Default metadata if file doesn't exist or can't be loaded
        return {
            "name": self.bank_name,
            "created_at": datetime.now().isoformat(),
            "interest_rates": self.interest_rates,
            "transaction_fees": self.transaction_fees,
            "total_accounts": 0,
            "total_assets": 0.0,
            "last_interest_payout": None,
        }
    
    def _save_metadata(self) -> None:
        """Save bank metadata to file"""
        metadata_file = BANK_DIR / "bank_metadata.json"
        try:
            with open(metadata_file, "w") as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving bank metadata: {e}")
    
    def create_account(
        self, 
        account_name: str, 
        owner_id: str, 
        initial_deposit: float = 0.0,
        account_type: str = "standard"
    ) -> Dict[str, Any]:
        """Create a new MeshCredit account"""
        # Generate account ID
        account_id = hashlib.sha256(
            f"{owner_id}:{account_name}:{time.time()}".encode()
        ).hexdigest()
        
        # Initialize account structure
        account = {
            "account_id": account_id,
            "name": account_name,
            "owner_id": owner_id,
            "type": account_type,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "balance": {
                "total": initial_deposit,
                "liquid": initial_deposit,
                "staked": 0.0,
                "compound": 0.0,
                "governance": 0.0,
            },
            "interest": {
                "last_accrual": datetime.now().isoformat(),
                "accrued_interest": 0.0,
            },
            "transactions": [],
            "linked_capsules": [],
            "status": "active",
        }
        
        # Save account data
        account_file = ACCOUNTS_DIR / f"{account_id}.json"
        with open(account_file, "w") as f:
            json.dump(account, f, indent=2)
        
        # Update bank metadata
        self.metadata["total_accounts"] += 1
        self.metadata["total_assets"] += initial_deposit
        self._save_metadata()
        
        # Record initial deposit if any
        if initial_deposit > 0:
            self._record_transaction(
                account_id=account_id,
                transaction_type="deposit",
                amount=initial_deposit,
                description="Initial deposit",
                asset_class="liquid",
            )
        
        logger.info(f"Created account: {account_name} [ID: {account_id[:8]}] with initial deposit of {initial_deposit} MeshCredit")
        return account
    
    def get_account(self, account_id: str) -> Dict[str, Any]:
        """Get account details"""
        # Check cache first
        if account_id in self._account_cache:
            return self._account_cache[account_id]
        
        # Load from file
        account_file = ACCOUNTS_DIR / f"{account_id}.json"
        if not account_file.exists():
            raise ValueError(f"Account not found: {account_id}")
        
        try:
            with open(account_file, "r") as f:
                account = json.load(f)
                # Update cache
                self._account_cache[account_id] = account
                return account
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading account {account_id}: {e}")
            raise ValueError(f"Error loading account: {e}")
    
    def update_account(self, account_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update account details"""
        account = self.get_account(account_id)
        
        # Update fields
        for key, value in data.items():
            if key in ["account_id", "created_at", "owner_id"]:
                # Skip immutable fields
                continue
            if key == "balance" and isinstance(value, dict):
                for asset_class, amount in value.items():
                    if asset_class in account["balance"]:
                        account["balance"][asset_class] = amount
            elif key in account:
                account[key] = value
        
        # Update timestamp
        account["last_updated"] = datetime.now().isoformat()
        
        # Save updated account
        account_file = ACCOUNTS_DIR / f"{account_id}.json"
        with open(account_file, "w") as f:
            json.dump(account, f, indent=2)
        
        # Update cache
        self._account_cache[account_id] = account
        
        return account
    
    def deposit(
        self,
        account_id: str,
        amount: float,
        description: str = "Deposit",
        asset_class: str = "liquid",
    ) -> Dict[str, Any]:
        """Deposit MeshCredit into an account"""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        if asset_class not in ASSET_CLASSES:
            raise ValueError(f"Invalid asset class: {asset_class}. Must be one of {ASSET_CLASSES}")
        
        account = self.get_account(account_id)
        
        # Update balance
        account["balance"][asset_class] += amount
        account["balance"]["total"] += amount
        
        # Record transaction
        transaction = self._record_transaction(
            account_id=account_id,
            transaction_type="deposit",
            amount=amount,
            description=description,
            asset_class=asset_class,
        )
        
        # Update account
        account["last_updated"] = datetime.now().isoformat()
        account["transactions"].append(transaction["transaction_id"])
        
        # Save updated account
        self.update_account(account_id, account)
        
        # Update bank metadata
        self.metadata["total_assets"] += amount
        self._save_metadata()
        
        logger.info(f"Deposited {amount} MeshCredit into account {account_id[:8]} ({asset_class})")
        return transaction
    
    def withdraw(
        self,
        account_id: str,
        amount: float,
        description: str = "Withdrawal",
        asset_class: str = "liquid",
    ) -> Dict[str, Any]:
        """Withdraw MeshCredit from an account"""
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if asset_class not in ASSET_CLASSES:
            raise ValueError(f"Invalid asset class: {asset_class}. Must be one of {ASSET_CLASSES}")
        
        account = self.get_account(account_id)
        
        # Check if sufficient balance
        if account["balance"][asset_class] < amount:
            raise ValueError(
                f"Insufficient {asset_class} balance: {account['balance'][asset_class]} < {amount}"
            )
        
        # Calculate fee
        fee = amount * self.transaction_fees.get("withdraw", 0)
        net_amount = amount - fee
        
        # Update balance
        account["balance"][asset_class] -= amount
        account["balance"]["total"] -= amount
        
        # Record transaction
        transaction = self._record_transaction(
            account_id=account_id,
            transaction_type="withdraw",
            amount=-amount,
            description=description,
            asset_class=asset_class,
            fee=fee,
        )
        
        # Update account
        account["last_updated"] = datetime.now().isoformat()
        account["transactions"].append(transaction["transaction_id"])
        
        # Save updated account
        self.update_account(account_id, account)
        
        # Update bank metadata
        self.metadata["total_assets"] -= amount
        self._save_metadata()
        
        logger.info(
            f"Withdrew {amount} MeshCredit (fee: {fee}, net: {net_amount}) "
            f"from account {account_id[:8]} ({asset_class})"
        )
        return transaction
    
    def transfer(
        self,
        from_account_id: str,
        to_account_id: str,
        amount: float,
        description: str = "Transfer",
        asset_class: str = "liquid",
    ) -> Dict[str, Any]:
        """Transfer MeshCredit between accounts"""
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        
        if asset_class not in ASSET_CLASSES:
            raise ValueError(f"Invalid asset class: {asset_class}. Must be one of {ASSET_CLASSES}")
        
        # Get source account
        from_account = self.get_account(from_account_id)
        
        # Check if sufficient balance
        if from_account["balance"][asset_class] < amount:
            raise ValueError(
                f"Insufficient {asset_class} balance: {from_account['balance'][asset_class]} < {amount}"
            )
        
        # Calculate fee
        fee = amount * self.transaction_fees.get("transfer", 0)
        net_amount = amount - fee
        
        # Update source account balance
        from_account["balance"][asset_class] -= amount
        from_account["balance"]["total"] -= amount
        
        # Get destination account
        to_account = self.get_account(to_account_id)
        
        # Update destination account balance
        to_account["balance"][asset_class] += net_amount
        to_account["balance"]["total"] += net_amount
        
        # Record transactions
        from_transaction = self._record_transaction(
            account_id=from_account_id,
            transaction_type="transfer_out",
            amount=-amount,
            description=f"{description} to {to_account_id[:8]}",
            asset_class=asset_class,
            fee=fee,
            related_account=to_account_id,
        )
        
        to_transaction = self._record_transaction(
            account_id=to_account_id,
            transaction_type="transfer_in",
            amount=net_amount,
            description=f"{description} from {from_account_id[:8]}",
            asset_class=asset_class,
            related_account=from_account_id,
        )
        
        # Update accounts
        from_account["last_updated"] = datetime.now().isoformat()
        from_account["transactions"].append(from_transaction["transaction_id"])
        
        to_account["last_updated"] = datetime.now().isoformat()
        to_account["transactions"].append(to_transaction["transaction_id"])
        
        # Save updated accounts
        self.update_account(from_account_id, from_account)
        self.update_account(to_account_id, to_account)
        
        logger.info(
            f"Transferred {amount} MeshCredit (fee: {fee}, net: {net_amount}) "
            f"from account {from_account_id[:8]} to {to_account_id[:8]} ({asset_class})"
        )
        
        return {
            "from_transaction": from_transaction,
            "to_transaction": to_transaction,
            "fee": fee,
            "net_amount": net_amount,
        }
    
    def _record_transaction(
        self,
        account_id: str,
        transaction_type: str,
        amount: float,
        description: str,
        asset_class: str,
        fee: float = 0.0,
        related_account: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record a transaction"""
        transaction_id = hashlib.sha256(
            f"{account_id}:{transaction_type}:{amount}:{time.time()}".encode()
        ).hexdigest()
        
        transaction = {
            "transaction_id": transaction_id,
            "account_id": account_id,
            "type": transaction_type,
            "amount": amount,
            "fee": fee,
            "net_amount": amount - fee if amount > 0 else amount + fee,
            "asset_class": asset_class,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
        }
        
        if related_account:
            transaction["related_account"] = related_account
        
        # Save transaction
        transaction_file = TRANSACTIONS_DIR / f"{transaction_id}.json"
        with open(transaction_file, "w") as f:
            json.dump(transaction, f, indent=2)
        
        return transaction
    
    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction details"""
        transaction_file = TRANSACTIONS_DIR / f"{transaction_id}.json"
        if not transaction_file.exists():
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        try:
            with open(transaction_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading transaction {transaction_id}: {e}")
            raise ValueError(f"Error loading transaction: {e}")
    
    def get_account_transactions(
        self, 
        account_id: str, 
        limit: int = 20, 
        offset: int = 0,
        transaction_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get transactions for an account"""
        account = self.get_account(account_id)
        
        # Get transaction IDs, newest first
        transaction_ids = account.get("transactions", [])
        transaction_ids.reverse()
        
        # Apply pagination
        paginated_ids = transaction_ids[offset:offset + limit]
        
        # Load transactions
        transactions = []
        for tx_id in paginated_ids:
            try:
                tx = self.get_transaction(tx_id)
                if transaction_type is None or tx["type"] == transaction_type:
                    transactions.append(tx)
            except ValueError:
                continue
        
        return transactions
    
    def accrue_interest(
        self, 
        account_id: str, 
        days: int = 1,
        compound: bool = True,
    ) -> Dict[str, float]:
        """Accrue interest for an account"""
        account = self.get_account(account_id)
        
        # Calculate interest for each asset class
        interest_earned = {}
        total_interest = 0.0
        
        for asset_class in ASSET_CLASSES:
            if asset_class == "total":
                continue
                
            balance = account["balance"][asset_class]
            rate = self.interest_rates.get(asset_class, 0)
            
            # Calculate daily interest (annual rate / 365)
            daily_rate = rate / 365
            
            # Calculate interest amount
            if compound:
                # Compound interest formula: P * (1 + r)^t - P
                interest = balance * ((1 + daily_rate) ** days) - balance
            else:
                # Simple interest formula: P * r * t
                interest = balance * daily_rate * days
            
            interest_earned[asset_class] = interest
            total_interest += interest
        
        # Update account
        if total_interest > 0:
            # Record interest transaction
            transaction = self._record_transaction(
                account_id=account_id,
                transaction_type="interest",
                amount=total_interest,
                description=f"Interest accrual ({days} days)",
                asset_class="liquid",  # Interest is initially liquid
            )
            
            # Update account balance
            account["balance"]["liquid"] += total_interest
            account["balance"]["total"] += total_interest
            
            # Update interest tracking
            account["interest"]["last_accrual"] = datetime.now().isoformat()
            account["interest"]["accrued_interest"] = account["interest"].get("accrued_interest", 0) + total_interest
            
            # Add transaction to account
            account["transactions"].append(transaction["transaction_id"])
            
            # Save updated account
            self.update_account(account_id, account)
            
            # Update bank metadata
            self.metadata["total_assets"] += total_interest
            self._save_metadata()
            
            logger.info(f"Accrued {total_interest:.6f} MeshCredit interest for account {account_id[:8]}")
        
        return {
            "total_interest": total_interest,
            "by_asset_class": interest_earned,
            "days_accrued": days,
        }
    
    def accrue_all_interest(self, days: int = 1) -> Dict[str, Any]:
        """Accrue interest for all accounts"""
        # Get all account IDs
        account_files = list(ACCOUNTS_DIR.glob("*.json"))
        account_ids = [f.stem for f in account_files]
        
        results = {
            "total_interest_paid": 0.0,
            "accounts_processed": 0,
            "details": {},
        }
        
        # Process each account
        for account_id in account_ids:
            try:
                account = self.get_account(account_id)
                
                # Skip inactive accounts
                if account.get("status") != "active":
                    continue
                
                # Accrue interest
                interest_result = self.accrue_interest(account_id, days)
                
                # Update results
                results["total_interest_paid"] += interest_result["total_interest"]
                results["accounts_processed"] += 1
                results["details"][account_id] = interest_result
                
            except Exception as e:
                logger.error(f"Error accruing interest for account {account_id}: {e}")
                continue
        
        # Update bank metadata
        self.metadata["last_interest_payout"] = datetime.now().isoformat()
        self._save_metadata()
        
        logger.info(
            f"Accrued interest for {results['accounts_processed']} accounts, "
            f"total: {results['total_interest_paid']:.6f} MeshCredit"
        )
        
        return results
    
    def change_asset_class(
        self,
        account_id: str,
        amount: float,
        from_class: str,
        to_class: str,
        description: str = "Asset class change",
    ) -> Dict[str, Any]:
        """Change asset class for a portion of balance"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if from_class not in ASSET_CLASSES or to_class not in ASSET_CLASSES:
            raise ValueError(f"Invalid asset class. Must be one of {ASSET_CLASSES}")
        
        if from_class == to_class:
            raise ValueError("Source and destination asset classes must be different")
        
        account = self.get_account(account_id)
        
        # Check if sufficient balance
        if account["balance"][from_class] < amount:
            raise ValueError(
                f"Insufficient {from_class} balance: {account['balance'][from_class]} < {amount}"
            )
        
        # Update balance
        account["balance"][from_class] -= amount
        account["balance"][to_class] += amount
        
        # Record transaction
        transaction = self._record_transaction(
            account_id=account_id,
            transaction_type="asset_class_change",
            amount=amount,
            description=f"{description}: {from_class} → {to_class}",
            asset_class=f"{from_class}_to_{to_class}",
        )
        
        # Update account
        account["last_updated"] = datetime.now().isoformat()
        account["transactions"].append(transaction["transaction_id"])
        
        # Save updated account
        self.update_account(account_id, account)
        
        logger.info(
            f"Changed {amount} MeshCredit from {from_class} to {to_class} "
            f"for account {account_id[:8]}"
        )
        
        return transaction
    
    def link_capsule(
        self,
        account_id: str,
        capsule_id: str,
        amount: float = 0.0,
        description: str = "Capsule link",
    ) -> Dict[str, Any]:
        """Link a capsule to an account"""
        if self.capsule_integration:
            # Import here to avoid circular imports
            try:
                from capsule_compounding import CapsuleCompoundingEngine
                engine = CapsuleCompoundingEngine()
            except ImportError:
                logger.warning("Capsule Compounding Engine not available")
                engine = None
        else:
            engine = None
        
        account = self.get_account(account_id)
        
        # Check if capsule is already linked
        if capsule_id in [link.get("capsule_id") for link in account.get("linked_capsules", [])]:
            raise ValueError(f"Capsule {capsule_id} is already linked to account {account_id}")
        
        # If amount specified, move it to compound class
        if amount > 0:
            if account["balance"]["liquid"] < amount:
                raise ValueError(
                    f"Insufficient liquid balance: {account['balance']['liquid']} < {amount}"
                )
            
            # Move from liquid to compound
            account["balance"]["liquid"] -= amount
            account["balance"]["compound"] += amount
        
        # Create link record
        link = {
            "capsule_id": capsule_id,
            "linked_at": datetime.now().isoformat(),
            "initial_amount": amount,
            "current_amount": amount,
            "status": "active",
        }
        
        # If engine available, register with it
        if engine and amount > 0:
            try:
                # Choose a random trick for the capsule
                import random
                from capsule_compounding import COMPOUNDING_TRICKS
                trick = random.choice(COMPOUNDING_TRICKS)
                
                # Register the trick
                result = engine.register_compound_trick(trick, capsule_id)
                link["trick_name"] = trick
                link["trigger_id"] = result.get("trigger_id")
                
                logger.info(
                    f"Registered trick {trick} for capsule {capsule_id} "
                    f"with account {account_id[:8]}"
                )
            except Exception as e:
                logger.error(f"Error registering capsule with compounding engine: {e}")
        
        # Add link to account
        if not account.get("linked_capsules"):
            account["linked_capsules"] = []
        account["linked_capsules"].append(link)
        
        # Record transaction if amount > 0
        if amount > 0:
            transaction = self._record_transaction(
                account_id=account_id,
                transaction_type="capsule_link",
                amount=amount,
                description=f"{description}: {capsule_id}",
                asset_class="compound",
            )
            account["transactions"].append(transaction["transaction_id"])
        
        # Save updated account
        account["last_updated"] = datetime.now().isoformat()
        self.update_account(account_id, account)
        
        logger.info(
            f"Linked capsule {capsule_id} to account {account_id[:8]} "
            f"with {amount} MeshCredit"
        )
        
        return link
    
    def unlink_capsule(
        self,
        account_id: str,
        capsule_id: str,
        description: str = "Capsule unlink",
    ) -> Dict[str, Any]:
        """Unlink a capsule from an account"""
        account = self.get_account(account_id)
        
        # Find capsule link
        capsule_link = None
        for link in account.get("linked_capsules", []):
            if link.get("capsule_id") == capsule_id and link.get("status") == "active":
                capsule_link = link
                break
        
        if not capsule_link:
            raise ValueError(f"Capsule {capsule_id} not linked to account {account_id}")
        
        # Mark as inactive
        capsule_link["status"] = "inactive"
        capsule_link["unlinked_at"] = datetime.now().isoformat()
        
        # Move amount back to liquid
        amount = capsule_link.get("current_amount", 0)
        if amount > 0:
            account["balance"]["compound"] -= amount
            account["balance"]["liquid"] += amount
            
            # Record transaction
            transaction = self._record_transaction(
                account_id=account_id,
                transaction_type="capsule_unlink",
                amount=amount,
                description=f"{description}: {capsule_id}",
                asset_class="liquid",
            )
            account["transactions"].append(transaction["transaction_id"])
        
        # Save updated account
        account["last_updated"] = datetime.now().isoformat()
        self.update_account(account_id, account)
        
        logger.info(
            f"Unlinked capsule {capsule_id} from account {account_id[:8]}, "
            f"returned {amount} MeshCredit to liquid"
        )
        
        return {
            "capsule_id": capsule_id,
            "amount_returned": amount,
            "status": "unlinked",
        }
    
    def apply_compound_rewards(
        self, 
        account_id: str, 
        capsule_id: str, 
        reward_amount: float,
        description: str = "Compound rewards",
    ) -> Dict[str, Any]:
        """Apply compounding rewards to an account from a linked capsule"""
        account = self.get_account(account_id)
        
        # Find capsule link
        capsule_link = None
        for link in account.get("linked_capsules", []):
            if link.get("capsule_id") == capsule_id and link.get("status") == "active":
                capsule_link = link
                break
        
        if not capsule_link:
            raise ValueError(f"Capsule {capsule_id} not linked to account {account_id}")
        
        # Apply reward
        if reward_amount <= 0:
            raise ValueError("Reward amount must be positive")
        
        # Record transaction
        transaction = self._record_transaction(
            account_id=account_id,
            transaction_type="compound_reward",
            amount=reward_amount,
            description=f"{description}: {capsule_id}",
            asset_class="compound",
        )
        
        # Update account
        account["balance"]["compound"] += reward_amount
        account["balance"]["total"] += reward_amount
        account["transactions"].append(transaction["transaction_id"])
        
        # Update capsule link
        capsule_link["current_amount"] += reward_amount
        capsule_link["last_reward"] = {
            "amount": reward_amount,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Save updated account
        account["last_updated"] = datetime.now().isoformat()
        self.update_account(account_id, account)
        
        # Update bank metadata
        self.metadata["total_assets"] += reward_amount
        self._save_metadata()
        
        logger.info(
            f"Applied {reward_amount} MeshCredit compound rewards to account {account_id[:8]} "
            f"from capsule {capsule_id}"
        )
        
        return {
            "transaction_id": transaction["transaction_id"],
            "capsule_id": capsule_id,
            "reward_amount": reward_amount,
            "new_capsule_amount": capsule_link["current_amount"],
        }
    
    def get_balance_summary(self, account_id: str) -> Dict[str, Any]:
        """Get a summary of account balance"""
        account = self.get_account(account_id)
        
        return {
            "account_id": account_id,
            "account_name": account.get("name", ""),
            "total_balance": account["balance"]["total"],
            "liquid_balance": account["balance"]["liquid"],
            "staked_balance": account["balance"]["staked"],
            "compound_balance": account["balance"]["compound"],
            "governance_balance": account["balance"]["governance"],
            "linked_capsules": len([l for l in account.get("linked_capsules", []) if l.get("status") == "active"]),
            "accrued_interest": account["interest"].get("accrued_interest", 0),
            "last_updated": account["last_updated"],
        }
    
    def get_bank_summary(self) -> Dict[str, Any]:
        """Get a summary of the bank's state"""
        # Get latest totals
        account_files = list(ACCOUNTS_DIR.glob("*.json"))
        active_accounts = 0
        asset_totals = {asset: 0.0 for asset in ASSET_CLASSES}
        asset_totals["total"] = 0.0
        
        for account_file in account_files:
            try:
                with open(account_file, "r") as f:
                    account = json.load(f)
                    
                if account.get("status") == "active":
                    active_accounts += 1
                    for asset, amount in account.get("balance", {}).items():
                        if asset in asset_totals:
                            asset_totals[asset] += amount
            except Exception:
                continue
        
        # Update metadata with latest totals
        self.metadata["total_accounts"] = active_accounts
        self.metadata["total_assets"] = asset_totals["total"]
        self._save_metadata()
        
        return {
            "bank_name": self.bank_name,
            "bank_id": self.metadata["bank_id"],
            "created_at": self.metadata["created_at"],
            "total_accounts": active_accounts,
            "asset_totals": asset_totals,
            "interest_rates": self.interest_rates,
            "transaction_fees": self.transaction_fees,
            "last_interest_payout": self.metadata.get("last_interest_payout"),
        }


def create_demo_bank_data() -> None:
    """Create sample data for demonstration purposes"""
    bank = MeshCreditBank()
    
    # Create accounts
    alice = bank.create_account("Alice's Account", "user123", 1000.0)
    bob = bank.create_account("Bob's MeshCredit", "user456", 500.0)
    project_x = bank.create_account("Project X Fund", "project789", 5000.0, "project")
    
    # Perform some transactions
    bank.deposit(alice["account_id"], 250.0, "Bonus deposit")
    bank.withdraw(bob["account_id"], 100.0, "Test withdrawal")
    bank.transfer(project_x["account_id"], alice["account_id"], 500.0, "Project contribution")
    
    # Change asset classes
    bank.change_asset_class(alice["account_id"], 300.0, "liquid", "staked", "Stake for governance")
    bank.change_asset_class(project_x["account_id"], 1000.0, "liquid", "governance", "Governance allocation")
    
    # Create and link capsules
    import uuid
    capsule1 = f"DEMO-{uuid.uuid4().hex[:8]}"
    capsule2 = f"DEMO-{uuid.uuid4().hex[:8]}"
    
    bank.link_capsule(alice["account_id"], capsule1, 200.0, "Growth strategy")
    bank.link_capsule(project_x["account_id"], capsule2, 1000.0, "Project amplification")
    
    # Apply compound rewards
    bank.apply_compound_rewards(alice["account_id"], capsule1, 15.0, "7-day compounding")
    bank.apply_compound_rewards(project_x["account_id"], capsule2, 85.0, "7-day compounding")
    
    # Accrue interest
    bank.accrue_interest(alice["account_id"], 30)
    bank.accrue_interest(bob["account_id"], 30)
    bank.accrue_interest(project_x["account_id"], 30)
    
    logger.info("Demo bank data created successfully")


def main() -> None:
    """CLI interface for MeshCredit Bank"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MeshCredit Banking System")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create account command
    create_parser = subparsers.add_parser("create", help="Create a new account")
    create_parser.add_argument("name", help="Account name")
    create_parser.add_argument("owner", help="Owner ID")
    create_parser.add_argument("--deposit", type=float, default=0.0, help="Initial deposit")
    create_parser.add_argument("--type", default="standard", help="Account type")
    
    # Get account command
    get_parser = subparsers.add_parser("get", help="Get account details")
    get_parser.add_argument("account_id", help="Account ID")
    
    # Deposit command
    deposit_parser = subparsers.add_parser("deposit", help="Deposit MeshCredit")
    deposit_parser.add_argument("account_id", help="Account ID")
    deposit_parser.add_argument("amount", type=float, help="Amount to deposit")
    deposit_parser.add_argument("--asset", default="liquid", help="Asset class")
    deposit_parser.add_argument("--description", help="Transaction description")
    
    # Withdraw command
    withdraw_parser = subparsers.add_parser("withdraw", help="Withdraw MeshCredit")
    withdraw_parser.add_argument("account_id", help="Account ID")
    withdraw_parser.add_argument("amount", type=float, help="Amount to withdraw")
    withdraw_parser.add_argument("--asset", default="liquid", help="Asset class")
    withdraw_parser.add_argument("--description", help="Transaction description")
    
    # Transfer command
    transfer_parser = subparsers.add_parser("transfer", help="Transfer MeshCredit")
    transfer_parser.add_argument("from_account", help="Source account ID")
    transfer_parser.add_argument("to_account", help="Destination account ID")
    transfer_parser.add_argument("amount", type=float, help="Amount to transfer")
    transfer_parser.add_argument("--asset", default="liquid", help="Asset class")
    transfer_parser.add_argument("--description", help="Transaction description")
    
    # Get transactions command
    txs_parser = subparsers.add_parser("transactions", help="List account transactions")
    txs_parser.add_argument("account_id", help="Account ID")
    txs_parser.add_argument("--limit", type=int, default=10, help="Number of transactions to list")
    txs_parser.add_argument("--type", help="Transaction type filter")
    
    # Interest command
    interest_parser = subparsers.add_parser("interest", help="Accrue interest")
    interest_parser.add_argument("account_id", help="Account ID (or 'all' for all accounts)")
    interest_parser.add_argument("--days", type=int, default=1, help="Days to accrue")
    
    # Link capsule command
    link_parser = subparsers.add_parser("link", help="Link a capsule")
    link_parser.add_argument("account_id", help="Account ID")
    link_parser.add_argument("capsule_id", help="Capsule ID")
    link_parser.add_argument("--amount", type=float, default=0.0, help="Amount to allocate")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Create demo data")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Get bank summary")
    
    args = parser.parse_args()
    
    # Initialize the bank
    bank = MeshCreditBank()
    
    if args.command == "create":
        account = bank.create_account(args.name, args.owner, args.deposit, args.type)
        print(f"Created account: {account['name']} [ID: {account['account_id']}]")
        print(f"Initial balance: {account['balance']['total']} MeshCredit")
    
    elif args.command == "get":
        account = bank.get_account(args.account_id)
        print(f"Account: {account['name']} [ID: {account['account_id']}]")
        print(f"Owner: {account['owner_id']}")
        print(f"Type: {account['type']}")
        print(f"Created: {account['created_at']}")
        print(f"Status: {account['status']}")
        print("\nBalance:")
        for asset, amount in account['balance'].items():
            print(f"  {asset.capitalize()}: {amount} MeshCredit")
        
        active_capsules = [c for c in account.get('linked_capsules', []) if c.get('status') == 'active']
        if active_capsules:
            print("\nLinked Capsules:")
            for capsule in active_capsules:
                print(f"  {capsule['capsule_id']} - {capsule['current_amount']} MeshCredit")
    
    elif args.command == "deposit":
        description = args.description or f"Deposit ({args.asset})"
        tx = bank.deposit(args.account_id, args.amount, description, args.asset)
        print(f"Deposited {args.amount} MeshCredit to account {args.account_id[:8]}")
        print(f"Transaction ID: {tx['transaction_id']}")
    
    elif args.command == "withdraw":
        description = args.description or f"Withdrawal ({args.asset})"
        tx = bank.withdraw(args.account_id, args.amount, description, args.asset)
        print(f"Withdrew {args.amount} MeshCredit from account {args.account_id[:8]}")
        print(f"Fee: {tx['fee']} MeshCredit")
        print(f"Net amount: {tx['net_amount']} MeshCredit")
        print(f"Transaction ID: {tx['transaction_id']}")
    
    elif args.command == "transfer":
        description = args.description or f"Transfer ({args.asset})"
        result = bank.transfer(args.from_account, args.to_account, args.amount, description, args.asset)
        print(f"Transferred {args.amount} MeshCredit from {args.from_account[:8]} to {args.to_account[:8]}")
        print(f"Fee: {result['fee']} MeshCredit")
        print(f"Net amount received: {result['net_amount']} MeshCredit")
    
    elif args.command == "transactions":
        transactions = bank.get_account_transactions(args.account_id, args.limit, 0, args.type)
        print(f"Transactions for account {args.account_id[:8]}:")
        for tx in transactions:
            sign = "+" if tx['amount'] > 0 else ""
            print(f"  {tx['timestamp'][:16]} | {tx['type']:<15} | {sign}{tx['amount']:<10.2f} | {tx['description']}")
    
    elif args.command == "interest":
        if args.account_id.lower() == "all":
            result = bank.accrue_all_interest(args.days)
            print(f"Accrued interest for {result['accounts_processed']} accounts")
            print(f"Total interest paid: {result['total_interest_paid']} MeshCredit")
        else:
            result = bank.accrue_interest(args.account_id, args.days)
            print(f"Accrued interest for account {args.account_id[:8]} ({args.days} days)")
            print(f"Total interest: {result['total_interest']} MeshCredit")
            print("\nBreakdown by asset class:")
            for asset, amount in result['by_asset_class'].items():
                if amount > 0:
                    print(f"  {asset}: {amount} MeshCredit")
    
    elif args.command == "link":
        result = bank.link_capsule(args.account_id, args.capsule_id, args.amount)
        print(f"Linked capsule {args.capsule_id} to account {args.account_id[:8]}")
        if args.amount > 0:
            print(f"Allocated {args.amount} MeshCredit to the capsule")
    
    elif args.command == "demo":
        create_demo_bank_data()
        print("Created demo bank data with sample accounts and transactions")
        print("Use other commands to explore the demo data")
    
    elif args.command == "summary":
        summary = bank.get_bank_summary()
        print(f"Bank: {summary['bank_name']} [ID: {summary['bank_id'][:8]}]")
        print(f"Accounts: {summary['total_accounts']}")
        print("\nAsset Totals:")
        for asset, amount in summary['asset_totals'].items():
            if asset != "total":
                print(f"  {asset.capitalize()}: {amount} MeshCredit")
        print(f"  Total: {summary['asset_totals']['total']} MeshCredit")
        
        print("\nInterest Rates (APY):")
        for asset, rate in summary['interest_rates'].items():
            print(f"  {asset.capitalize()}: {rate*100:.2f}%")
        
        if summary['last_interest_payout']:
            print(f"\nLast Interest Payout: {summary['last_interest_payout'][:16]}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
