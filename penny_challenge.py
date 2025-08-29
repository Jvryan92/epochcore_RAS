"""
Penny Challenge - First Real Revenue Generation System
Focus: Converting software value to real USD or MeshCredit transactions
Target: Minimum $0.01 USD or 1 MeshCredit per transaction
"""

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict


class PennyChallenge:
    def __init__(self):
        self.min_usd = Decimal('0.01')
        self.min_mesh = Decimal('1.00')
        self.coinbase_integration = {
            "account": "jryan2k19@gmail.com",
            "payment_methods": [
                "direct_deposit",
                "crypto_transfer",
                "payment_card"
            ]
        }

        # Revenue tracking
        self.transactions = []
        self.total_usd = Decimal('0.00')
        self.total_mesh = Decimal('0.00')

    def track_transaction(self, amount: Decimal, currency: str,
                          method: str, timestamp: str = None) -> Dict[str, Any]:
        """Record a successful revenue transaction."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        transaction = {
            "id": self._generate_tx_id(timestamp),
            "amount": str(amount),
            "currency": currency,
            "method": method,
            "timestamp": timestamp,
            "status": "completed"
        }

        # Update totals
        if currency == "USD":
            self.total_usd += amount
        else:
            self.total_mesh += amount

        self.transactions.append(transaction)
        return transaction

    def get_revenue_stats(self) -> Dict[str, Any]:
        """Get current revenue statistics."""
        return {
            "total_usd": str(self.total_usd),
            "total_mesh": str(self.total_mesh),
            "transaction_count": len(self.transactions),
            "latest_transaction": self.transactions[-1] if self.transactions else None,
            "first_revenue_achieved": bool(self.total_usd >= self.min_usd or
                                           self.total_mesh >= self.min_mesh)
        }

    def _generate_tx_id(self, timestamp: str) -> str:
        """Generate unique transaction ID."""
        data = f"{timestamp}:{len(self.transactions)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


# Available Revenue Sources
REVENUE_SOURCES = {
    "instant_access": {
        "description": "Instant access to base feature set",
        "usd_price": Decimal('0.01'),
        "mesh_price": Decimal('1.00')
    },
    "priority_support": {
        "description": "24-hour priority support ticket",
        "usd_price": Decimal('0.01'),
        "mesh_price": Decimal('1.00')
    },
    "early_access": {
        "description": "Early access to new features",
        "usd_price": Decimal('0.01'),
        "mesh_price": Decimal('1.00')
    }
}

if __name__ == "__main__":
    # Initialize challenge
    challenge = PennyChallenge()

    # Print available options
    print("Penny Challenge Revenue Sources:")
    print("--------------------------------")
    for id, source in REVENUE_SOURCES.items():
        print(f"\n{id}:")
        print(f"  {source['description']}")
        print(f"  USD: ${source['usd_price']}")
        print(f"  MESH: {source['mesh_price']} credits")

    print("\nTo make a purchase, send payment to:")
    print("Coinbase: jryan2k19@gmail.com")
    print("Reference: Include the revenue source ID in payment memo")
