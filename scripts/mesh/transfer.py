"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

This file is protected under proprietary license.
Unauthorized copying, modification, or distribution is strictly prohibited.
Contact: jryan2k19@gmail.com for licensing inquiries.
"""

import hashlib
import hmac
import json
import os
from decimal import Decimal
from typing import Dict, Optional, Tuple


class Transfer:
    """Handles MeshCredit transfers between wallets."""

    def __init__(self, mesh_key: bytes, ledger_path: str):
        self.mesh_key = mesh_key
        self.ledger_path = ledger_path

    def transfer(
        self,
        from_wallet: str,
        to_wallet: str,
        amount: Decimal,
        tx_type: str = "standard"
    ) -> Tuple[bool, Optional[str]]:
        """Transfer MeshCredits between wallets.

        Args:
            from_wallet: Source wallet ID
            to_wallet: Destination wallet ID
            amount: Amount to transfer in MeshCredits
            tx_type: Transaction type (standard/genesis/investment)

        Returns:
            (success, error_message)
        """
        # Load wallet balances
        balances = self._load_balances()

        # For genesis transactions, create initial supply
        if tx_type == "genesis":
            balances[to_wallet] = balances.get(to_wallet, Decimal('0')) + amount
            success = True

        # For regular transfers
        elif tx_type in ["standard", "investment", "software_purchase",
                         "game_reward", "game_purchase", "mystery_reward"]:
            # Check sender has sufficient balance
            if from_wallet not in balances:
                return False, f"Source wallet {from_wallet} not found"

            if balances[from_wallet] < amount:
                return False, f"Insufficient balance in {from_wallet}"

            # Update balances
            balances[from_wallet] -= amount
            balances[to_wallet] = balances.get(to_wallet, Decimal('0')) + amount

        else:
            return False, f"Invalid transaction type: {tx_type}"

        # Record transaction
        transaction = {
            "type": tx_type,
            "from": from_wallet,
            "to": to_wallet,
            "amount": str(amount)
        }

        # Sign transaction
        transaction["signature"] = self._sign_transaction(transaction)

        # Save updated balances and record transaction
        self._save_balances(balances)
        self._record_transaction(transaction)

        return True, None

    def get_balance(self, wallet_id: str) -> Decimal:
        """Get current balance of a wallet."""
        balances = self._load_balances()
        return balances.get(wallet_id, Decimal('0'))

    def _load_balances(self) -> Dict[str, Decimal]:
        """Load current wallet balances."""
        balance_path = f"{os.path.splitext(self.ledger_path)[0]}_balances.json"
        if os.path.exists(balance_path):
            with open(balance_path) as f:
                raw_balances = json.load(f)
                return {k: Decimal(v) for k, v in raw_balances.items()}
        return {}

    def _save_balances(self, balances: Dict[str, Decimal]) -> None:
        """Save updated wallet balances."""
        balance_path = f"{os.path.splitext(self.ledger_path)[0]}_balances.json"
        serialized = {k: str(v) for k, v in balances.items()}
        with open(balance_path, "w") as f:
            json.dump(serialized, f, indent=2)

    def _sign_transaction(self, transaction: Dict) -> str:
        """Create cryptographic signature for transaction."""
        tx_data = json.dumps(transaction, sort_keys=True).encode()
        return hmac.new(self.mesh_key, tx_data, hashlib.sha256).hexdigest()

    def _record_transaction(self, transaction: Dict) -> None:
        """Record signed transaction in ledger."""
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(transaction) + "\n")
