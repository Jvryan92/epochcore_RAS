"""
Simplified Payment Monitor
"""

import json
from decimal import Decimal
from pathlib import Path


class SimplePaymentMonitor:
    def __init__(self):
        self.payment_info = {
            "stripe": {
                "link": "https://donate.stripe.com/9B6aEYg3j6IG2SQ0t35sA04",
                "min": Decimal('0.50')
            },
            "paypal": {
                "email": "jryan2k19@gmail.com",  # Using email instead of QR
                "min": Decimal('0.01')
            }
        }

    def show_payment_options(self):
        """Display available payment options."""
        print("\nAvailable Payment Methods:")
        print("-----------------------")

        print("\nSTRIPE:")
        print(f"Minimum: ${self.payment_info['stripe']['min']}")
        print(f"Link: {self.payment_info['stripe']['link']}")

        print("\nPAYPAL:")
        print(f"Minimum: ${self.payment_info['paypal']['min']}")
        print(f"Send to: {self.payment_info['paypal']['email']}")

        print("\nWaiting for first transaction...")
        print("Any amount helps start the revenue stream!")


if __name__ == "__main__":
    monitor = SimplePaymentMonitor()
    monitor.show_payment_options()
