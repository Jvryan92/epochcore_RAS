"""
Stripe-focused Transaction Monitor
"""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict


class StripeMonitor:
    def __init__(self):
        self.stripe_link = "https://donate.stripe.com/9B6aEYg3j6IG2SQ0t35sA04"
        self.min_amount = Decimal('0.50')
        self.transactions_file = Path("stripe_transactions.json")
        self.transactions = self._load_transactions()

    def _load_transactions(self) -> list:
        """Load existing transactions."""
        if self.transactions_file.exists():
            with open(self.transactions_file) as f:
                return json.load(f)
        return []

    def check_status(self):
        """Check payment status."""
        print("\nStripe Payment Link Status:")
        print("--------------------------")
        print(f"Minimum Amount: ${self.min_amount}")
        print(f"Payment Link: {self.stripe_link}")

        if not self.transactions:
            print("\nStatus: Awaiting first payment")
            print("Once payment is made, it will be recorded here")
            return False

        print("\nRecorded Transactions:")
        total = Decimal('0.00')
        for tx in self.transactions:
            amount = Decimal(tx['amount'])
            total += amount
            print(f"\nAmount: ${amount}")
            print(f"Time: {tx['timestamp']}")
            print(f"Status: {tx['status']}")

        print(f"\nTotal Received: ${total}")
        return True

    def add_transaction(self, amount: Decimal):
        """Record a new transaction."""
        if amount < self.min_amount:
            print(f"Error: Amount ${amount} is below minimum ${self.min_amount}")
            return False

        tx = {
            "amount": str(amount),
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "payment_method": "stripe",
            "link": self.stripe_link
        }

        self.transactions.append(tx)

        # Save to file
        with open(self.transactions_file, 'w') as f:
            json.dump(self.transactions, f, indent=2)

        print(f"\nTransaction recorded: ${amount}")
        return True


if __name__ == "__main__":
    monitor = StripeMonitor()
    monitor.check_status()

    # To record a new transaction, uncomment and modify:
    # monitor.add_transaction(Decimal('0.50'))
