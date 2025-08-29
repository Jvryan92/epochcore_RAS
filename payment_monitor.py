"""
Multi-Payment Monitor for Stripe and PayPal
"""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict


class PaymentMonitor:
    def __init__(self):
        self.payment_methods = {
            "stripe": {
                "link": "https://donate.stripe.com/9B6aEYg3j6IG2SQ0t35sA04",
                "min_amount": Decimal('0.50'),
                "active": True
            },
            "paypal": {
                "address": "Awaiting QR code...",  # Will update when you have it
                "min_amount": Decimal('0.01'),     # PayPal allows smaller amounts
                "active": True
            }
        }

        self.transactions_file = Path("all_transactions.json")
        self.transactions = self._load_transactions()

    def _load_transactions(self) -> list:
        """Load existing transactions."""
        if self.transactions_file.exists():
            with open(self.transactions_file) as f:
                return json.load(f)
        return []

    def check_status(self):
        """Check payment status for all methods."""
        print("\nPayment System Status:")
        print("---------------------")

        # Show payment methods
        print("\nActive Payment Methods:")
        for method, details in self.payment_methods.items():
            print(f"\n{method.upper()}:")
            print(f"Minimum Amount: ${details['min_amount']}")
            if method == "stripe":
                print(f"Payment Link: {details['link']}")
            else:
                print(f"Payment Address: {details['address']}")

        # Show transactions
        if not self.transactions:
            print("\nStatus: Awaiting first payment")
            print("Transactions will be recorded here once received")
            return False

        print("\nRecorded Transactions:")
        totals = {"stripe": Decimal('0.00'), "paypal": Decimal('0.00')}

        for tx in self.transactions:
            amount = Decimal(tx['amount'])
            method = tx['payment_method']
            totals[method] += amount
            print(f"\nAmount: ${amount}")
            print(f"Method: {method}")
            print(f"Time: {tx['timestamp']}")
            print(f"Status: {tx['status']}")

        print("\nTotals by Method:")
        for method, total in totals.items():
            print(f"{method.upper()}: ${total}")

        return True

    def add_transaction(self, amount: Decimal, payment_method: str):
        """Record a new transaction."""
        if payment_method not in self.payment_methods:
            print(f"Error: Unknown payment method {payment_method}")
            return False

        method_details = self.payment_methods[payment_method]
        if amount < method_details['min_amount']:
            print(
                f"Error: Amount ${amount} is below {payment_method} minimum ${method_details['min_amount']}")
            return False

        tx = {
            "amount": str(amount),
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "payment_method": payment_method
        }

        if payment_method == "stripe":
            tx["link"] = method_details["link"]
        else:
            tx["address"] = method_details["address"]

        self.transactions.append(tx)

        # Save to file
        with open(self.transactions_file, 'w') as f:
            json.dump(self.transactions, f, indent=2)

        print(f"\nTransaction recorded: ${amount} via {payment_method}")
        return True

    def update_paypal_address(self, new_address: str):
        """Update PayPal address/QR code info."""
        self.payment_methods["paypal"]["address"] = new_address
        print(f"\nPayPal address updated: {new_address}")


if __name__ == "__main__":
    monitor = PaymentMonitor()
    monitor.check_status()

    # To update PayPal when you have the QR code:
    # monitor.update_paypal_address("your-paypal-details-here")

    # To record new transactions:
    # monitor.add_transaction(Decimal('0.50'), "stripe")
    # monitor.add_transaction(Decimal('0.01'), "paypal")
