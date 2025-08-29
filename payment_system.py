"""
PROTECTED FILE - EPOCHCORE RAS PAYMENT SYSTEM
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved
"""

import os
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

import stripe


@dataclass
class PaymentMethod:
    type: str
    frequency: str
    fee_percentage: Decimal
    payout_schedule: str


class PaymentProcessor:
    def __init__(self):
        # Initialize with multiple payment gateways
        self.payment_methods = {
            "STRIPE": PaymentMethod(
                "direct_deposit",
                "instant",
                Decimal("2.9"),  # 2.9% + $0.30
                "2_days"
            ),
            "PAYPAL": PaymentMethod(
                "digital_wallet",
                "instant",
                Decimal("2.9"),
                "instant"
            ),
            "WIRE": PaymentMethod(
                "bank_transfer",
                "manual",
                Decimal("1.0"),
                "3_5_days"
            ),
            "ACH": PaymentMethod(
                "bank_transfer",
                "scheduled",
                Decimal("0.8"),
                "3_days"
            )
        }

        # Revenue Collection Methods
        self.revenue_streams = {
            "GAME_SALES": {
                "frequency": "instant",
                "share": Decimal("100")  # You get 100% of game sales
            },
            "IN_APP": {
                "frequency": "instant",
                "share": Decimal("70")  # Standard 70% after platform fees
            },
            "CREATOR_PLATFORM": {
                "frequency": "instant",
                "share": Decimal("90")  # You get 90% as platform owner
            },
            "ENTERPRISE": {
                "frequency": "net30",
                "share": Decimal("100")  # Full enterprise license fees
            }
        }

    def setup_payment_account(self,
                              method: str,
                              bank_info: Dict) -> Dict:
        """Setup payment account for receiving money"""
        payment = self.payment_methods[method]

        account_info = {
            "payment_method": method,
            "payout_schedule": payment.payout_schedule,
            "fees": f"{payment.fee_percentage}%",
            "bank_info": "************" + bank_info["account_number"][-4:],
            "routing": "************" + bank_info["routing_number"][-4:],
            "verification_status": "pending"
        }

        return account_info

    def calculate_payout(self,
                         revenue: Dict[str, Decimal],
                         payment_method: str) -> Dict:
        """Calculate actual payout after fees"""
        method = self.payment_methods[payment_method]
        total_revenue = sum(revenue.values())
        fees = (total_revenue * method.fee_percentage) / 100

        payout = total_revenue - fees

        return {
            "gross_revenue": total_revenue,
            "fees": fees,
            "net_payout": payout,
            "payment_method": payment_method,
            "payout_schedule": method.payout_schedule
        }

    def generate_payment_schedule(self,
                                  start_date: datetime,
                                  recurring: bool = True) -> List[Dict]:
        """Generate payment schedule for recurring revenue"""
        schedule = []
        current_date = start_date

        for stream, details in self.revenue_streams.items():
            if details["frequency"] == "instant":
                schedule.append({
                    "stream": stream,
                    "date": "Instant",
                    "share": f"{details['share']}%",
                    "type": "Continuous"
                })
            elif details["frequency"] == "net30":
                schedule.append({
                    "stream": stream,
                    "date": current_date.replace(day=1) + pd.DateOffset(months=1),
                    "share": f"{details['share']}%",
                    "type": "Monthly"
                })

        return schedule

    def get_payment_instructions(self) -> str:
        """Get detailed payment setup instructions"""
        instructions = """
EPOCHCORE RAS PAYMENT SETUP INSTRUCTIONS
======================================

1. Direct Deposit Setup (Recommended Primary)
-------------------------------------------
- Log into your bank account
- Get your account and routing numbers
- Choose "STRIPE" or "ACH" as payment method
- Complete bank verification (takes 2-3 business days)
- Receive payouts every 2 business days

2. PayPal Setup (Recommended Backup)
----------------------------------
- Create/login to PayPal Business account
- Link to your bank account
- Choose "PAYPAL" as payment method
- Instant transfers available
- Good for international payments

3. Revenue Streams Setup
-----------------------
- Game Sales: 100% (minus payment processing)
- In-App Purchases: 70% (after platform fees)
- Creator Platform: 90% (as platform owner)
- Enterprise Licenses: 100% (net 30 terms)

4. Payout Schedules
------------------
- Game/In-App: Instant settlement
- Creator Platform: Daily rollup
- Enterprise: Monthly with net 30

5. Tax Information Required
-------------------------
- US Citizens: W-9 form
- Non-US: W-8BEN form
- EIN or SSN
- Valid government ID

6. Accounting Integration
------------------------
- QuickBooks/Xero integration available
- Automated revenue categorization
- Tax calculation and reporting
- Monthly financial statements

For immediate setup assistance:
1. Run: python3 setup_payment_account.py
2. Follow the prompts
3. Have your bank information ready

Support available 24/7 at support@epochcore.com
"""
        return instructions


# Example usage:
if __name__ == "__main__":
    processor = PaymentProcessor()

    # Get setup instructions
    print(processor.get_payment_instructions())

    # Example setup
    bank_info = {
        "account_number": "************1234",
        "routing_number": "************5678"
    }

    # Setup primary payment method
    account = processor.setup_payment_account("STRIPE", bank_info)
    print(f"Payment account setup: {account}")

    # Calculate example payout
    revenue = {
        "GAME_SALES": Decimal("10000.00"),
        "IN_APP": Decimal("5000.00"),
        "CREATOR_PLATFORM": Decimal("3000.00")
    }

    payout = processor.calculate_payout(revenue, "STRIPE")
    print(f"Monthly payout calculation: {payout}")
