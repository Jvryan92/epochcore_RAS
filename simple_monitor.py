"""
Simple Transaction Monitor
"""

import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict


class SimpleMonitor:
    def __init__(self):
        self.transactions_file = Path("transactions.json")
        self.transactions = self._load_transactions()

    def _load_transactions(self) -> list:
        """Load existing transactions."""
        if self.transactions_file.exists():
            with open(self.transactions_file) as f:
                return json.load(f)
        return []

    def check_transactions(self):
        """Check for any transactions."""
        if not self.transactions:
            print("No transactions recorded yet.")
            print("\nWaiting for first payment to:")
            print("Coinbase: jryan2k19@gmail.com")
            return False

        print("\nTransactions Found:")
        print("-----------------")
        total_usd = Decimal('0.00')
        total_mesh = Decimal('0.00')

        for tx in self.transactions:
            print(f"\nAmount: {tx['amount']} {tx['currency']}")
            print(f"Time: {tx['timestamp']}")
            print(f"Status: {tx['status']}")

            if tx['currency'] == 'USD':
                total_usd += Decimal(tx['amount'])
            else:
                total_mesh += Decimal(tx['amount'])

        print("\nTotals:")
        print(f"USD: ${total_usd}")
        print(f"MESH: {total_mesh}")
        return True


if __name__ == "__main__":
    monitor = SimpleMonitor()
    monitor.check_transactions()
