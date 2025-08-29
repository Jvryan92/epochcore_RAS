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


class JryanSoftware:
    """Personal software catalog for Jryan's products."""

    SOFTWARE_CATALOG = {
        "STRATEGY_DECK_PRO": {
            "name": "StrategyDECK Professional",
            "price": Decimal("15000"),  # 15,000 MESH
            "description": "Advanced strategy development and automation platform",
            "features": [
                "Quantum strategy engine",
                "Ethical reflection system",
                "Automated mesh topology",
                "Self-improvement protocols",
                "Full source code access"
            ],
            "license_period": 365  # days
        },
        "MESH_CREDIT_CORE": {
            "name": "MeshCredit Core System",
            "price": Decimal("25000"),  # 25,000 MESH
            "description": "Core MeshCredit implementation with emotional gravity",
            "features": [
                "21M MESH supply management",
                "Penny-backed stability",
                "Emotional gravity system",
                "Full transaction engine",
                "Investment tranches"
            ],
            "license_period": 365
        },
        "EPOCH_SUITE": {
            "name": "EPOCH Development Suite",
            "price": Decimal("20000"),  # 20,000 MESH
            "description": "Complete EPOCH development and runtime system",
            "features": [
                "EPOCH core runtime",
                "Agentic automation",
                "Manifest generation",
                "Drip chain management",
                "Development tools"
            ],
            "license_period": 365
        },
        "RAS_FRAMEWORK": {
            "name": "RAS Framework Enterprise",
            "price": Decimal("30000"),  # 30,000 MESH
            "description": "Enterprise RAS framework implementation",
            "features": [
                "Full RAS architecture",
                "Security hardening",
                "Compliance tools",
                "Performance monitoring",
                "Source code and docs"
            ],
            "license_period": 365
        }
    }

    def __init__(self):
        self.transfer = Transfer(MESH_KEY, LEDGER_PATH)

    def list_software(self) -> None:
        """Display Jryan's software catalog."""
        print("\n=== Jryan's Software Catalog ===\n")
        for sku, details in self.SOFTWARE_CATALOG.items():
            print(f"SKU: {sku}")
            print(f"Name: {details['name']}")
            print(f"Price: {details['price']:,} MESH")
            print(f"Description: {details['description']}")
            print("Features:")
            for feature in details['features']:
                print(f"  - {feature}")
            print(f"License Period: {details['license_period']} days\n")

    def purchase_software(
        self,
        wallet_id: str,
        sku: str
    ) -> Tuple[bool, Optional[Dict]]:
        """Purchase Jryan's software using MESH credits.

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
            "license_id": f"JRYAN-{sku}-{wallet_id[-8:]}",
            "sku": sku,
            "product_name": software["name"],
            "wallet_id": wallet_id,
            "purchase_amount": str(software["price"]),
            "license_period": software["license_period"],
            "features": software["features"]
        }

        # Record license
        license_path = f"{os.path.splitext(LEDGER_PATH)[0]}_licenses.jsonl"
        with open(license_path, "a") as f:
            f.write(json.dumps(license_details) + "\n")

        return True, license_details


def main():
    """Main execution function."""
    store = JryanSoftware()
    wallet_id = "MESH_JVRYAN92_1756445384"

    # Show balance
    balance = store.transfer.get_balance(wallet_id)
    print(f"\nWallet Balance: {balance:,} MESH")

    # Display your catalog
    store.list_software()

    # Purchase all enterprise products
    print("\n=== Enterprise Suite Purchase ===")

    # All top-tier SKUs
    # Top 3 highest-value products
    enterprise_skus = [
        "RAS_FRAMEWORK",      # 30,000 MESH
        "MESH_CREDIT_CORE",   # 25,000 MESH
        "EPOCH_SUITE"         # 20,000 MESH
    ]
    total_cost = sum(store.SOFTWARE_CATALOG[sku]["price"] for sku in enterprise_skus)

    print(f"Total Enterprise Suite Cost: {total_cost:,} MESH")
    print(f"Your Balance: {balance:,} MESH")

    if balance >= total_cost:
        licenses = []
        for sku in enterprise_skus:
            success, license_details = store.purchase_software(wallet_id, sku)
            if success:
                licenses.append(license_details)

        print("\n=== Purchase Summary ===")
        print("Enterprise Suite Activated!")
        print("\nLicenses Acquired:")
        for license in licenses:
            print(f"\n{license['product_name']}:")
            print(f"License ID: {license['license_id']}")
            print("Features:")
            for feature in license['features']:
                print(f"  - {feature}")

        final_balance = store.transfer.get_balance(wallet_id)
        print(f"\nRemaining balance: {final_balance:,} MESH")
    else:
        print("\nInsufficient balance for full enterprise suite.")


if __name__ == "__main__":
    main()
