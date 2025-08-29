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
from decimal import Decimal
from typing import Dict, Optional, Tuple

from scripts.mesh.transfer import Transfer

MESH_KEY = b"meshcredit2024"
LEDGER_PATH = os.path.join(os.path.dirname(__file__), "mesh_transactions.jsonl")
SOFTWARE_WALLET = "MESH_SOFTWARE_STORE"


class SoftwarePurchase:
    """Handles software purchases using MeshCredit."""

    SOFTWARE_CATALOG = {
        "DEV_IDE_PRO": {
            "name": "Developer IDE Professional",
            "price": Decimal("5000"),  # 5,000 MESH
            "description": "Full IDE suite with AI pair programming",
            "license_period": 365  # days
        },
        "CLOUD_DEPLOY_SUITE": {
            "name": "Cloud Deployment Suite",
            "price": Decimal("3500"),  # 3,500 MESH
            "description": "Automated cloud deployment tools",
            "license_period": 365
        },
        "DATA_ANALYTICS_PRO": {
            "name": "Data Analytics Professional",
            "price": Decimal("4000"),  # 4,000 MESH
            "description": "Advanced data analysis toolkit",
            "license_period": 365
        },
        "SECURITY_SUITE": {
            "name": "Security Testing Suite",
            "price": Decimal("4500"),  # 4,500 MESH
            "description": "Complete security testing platform",
            "license_period": 365
        }
    }

    def __init__(self):
        self.transfer = Transfer(MESH_KEY, LEDGER_PATH)

    def list_software(self) -> None:
        """Display available software catalog."""
        print("\n=== Software Catalog ===\n")
        for sku, details in self.SOFTWARE_CATALOG.items():
            print(f"SKU: {sku}")
            print(f"Name: {details['name']}")
            print(f"Price: {details['price']:,} MESH")
            print(f"Description: {details['description']}")
            print(f"License Period: {details['license_period']} days\n")

    def purchase_software(
        self,
        wallet_id: str,
        sku: str
    ) -> Tuple[bool, Optional[Dict]]:
        """Purchase software using MESH credits.

        Args:
            wallet_id: Buyer's wallet ID
            sku: Software SKU to purchase

        Returns:
            (success, license_details)
        """
        if sku not in self.SOFTWARE_CATALOG:
            print(f"Invalid SKU: {sku}")
            return False, None

        software = self.SOFTWARE_CATALOG[sku]
        balance = self.transfer.get_balance(wallet_id)

        if balance < software["price"]:
            print(f"Insufficient balance: {balance:,} MESH")
            print(f"Required: {software['price']:,} MESH")
            return False, None

        # Execute purchase transfer
        success, error = self.transfer.transfer(
            from_wallet=wallet_id,
            to_wallet=SOFTWARE_WALLET,
            amount=software["price"],
            tx_type="software_purchase"
        )

        if not success:
            print(f"Purchase failed: {error}")
            return False, None

        # Generate license
        license_details = {
            "license_id": f"MESH-{sku}-{wallet_id[-8:]}",
            "sku": sku,
            "product_name": software["name"],
            "wallet_id": wallet_id,
            "purchase_amount": str(software["price"]),
            "license_period": software["license_period"]
        }

        # Record license
        license_path = f"{os.path.splitext(LEDGER_PATH)[0]}_licenses.jsonl"
        with open(license_path, "a") as f:
            f.write(json.dumps(license_details) + "\n")

        return True, license_details


def main():
    """Main execution function."""
    store = SoftwarePurchase()
    wallet_id = "MESH_JVRYAN92_1756445384"

    # Show balance
    balance = store.transfer.get_balance(wallet_id)
    print(f"\nWallet Balance: {balance:,} MESH")

    # Display catalog
    store.list_software()

    # Purchase example software
    print("\n=== Purchase Example ===")
    success, license_details = store.purchase_software(wallet_id, "DEV_IDE_PRO")

    if success:
        print("\nPurchase successful!")
        print(f"License ID: {license_details['license_id']}")
        print(f"Product: {license_details['product_name']}")
        print(f"Period: {license_details['license_period']} days")
        print(f"\nRemaining balance: {store.transfer.get_balance(wallet_id):,} MESH")


if __name__ == "__main__":
    main()
