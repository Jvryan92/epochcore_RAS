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
from typing import Dict, List, Optional

import requests


class CoinbaseWalletBridge:
    """Bridge between Coinbase wallet and MeshCredit system."""

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.coinbase.com/v2"

    def get_wallet_info(self) -> Optional[Dict]:
        """Get Coinbase wallet information."""
        endpoint = "/user/auth"
        response = self._make_request("GET", endpoint)

        if response and "data" in response:
            return {
                "wallet_id": response["data"]["id"],
                "name": response["data"]["name"],
                "native_currency": response["data"]["native_currency"]
            }
        return None

    def get_accounts(self) -> List[Dict]:
        """Get list of Coinbase accounts/wallets."""
        endpoint = "/accounts"
        response = self._make_request("GET", endpoint)

        if response and "data" in response:
            return [{
                "id": acct["id"],
                "name": acct["name"],
                "currency": acct["currency"],
                "balance": Decimal(acct["balance"]["amount"]),
                "type": acct["type"]
            } for acct in response["data"]]
        return []

    def get_transactions(self, account_id: str) -> List[Dict]:
        """Get transaction history for an account."""
        endpoint = f"/accounts/{account_id}/transactions"
        response = self._make_request("GET", endpoint)

        if response and "data" in response:
            return [{
                "id": tx["id"],
                "type": tx["type"],
                "amount": Decimal(tx["amount"]["amount"]),
                "currency": tx["amount"]["currency"],
                "status": tx["status"],
                "timestamp": tx["created_at"]
            } for tx in response["data"]]
        return []

    def link_to_mesh(
        self,
        coinbase_account_id: str,
        mesh_wallet_id: str
    ) -> bool:
        """Link Coinbase account to MeshCredit wallet."""
        # Store wallet linking
        links_path = os.path.join(
            os.path.dirname(__file__),
            "wallet_links.jsonl"
        )

        link_data = {
            "coinbase_id": coinbase_account_id,
            "mesh_wallet": mesh_wallet_id,
            "timestamp": self._get_timestamp()
        }

        with open(links_path, "a") as f:
            f.write(json.dumps(link_data) + "\n")

        return True

    def _make_request(self, method: str, endpoint: str) -> Optional[Dict]:
        """Make authenticated request to Coinbase API."""
        timestamp = self._get_timestamp()
        url = f"{self.base_url}{endpoint}"

        # Create signature
        message = f"{timestamp}{method}{endpoint}"
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        headers = {
            "CB-ACCESS-KEY": self.api_key,
            "CB-ACCESS-SIGN": signature,
            "CB-ACCESS-TIMESTAMP": timestamp
        }

        try:
            response = requests.request(method, url, headers=headers)
            return response.json() if response.ok else None
        except Exception as e:
            print(f"API request failed: {str(e)}")
            return None

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()


def main():
    """Main execution function."""
    # Example usage
    api_key = "YOUR_COINBASE_API_KEY"
    api_secret = "YOUR_COINBASE_API_SECRET"

    bridge = CoinbaseWalletBridge(api_key, api_secret)

    # Get wallet info
    wallet_info = bridge.get_wallet_info()
    if wallet_info:
        print("\n=== Coinbase Wallet Info ===")
        print(f"Wallet ID: {wallet_info['wallet_id']}")
        print(f"Name: {wallet_info['name']}")
        print(f"Currency: {wallet_info['native_currency']}")

    # Get accounts
    accounts = bridge.get_accounts()
    if accounts:
        print("\n=== Coinbase Accounts ===")
        for acct in accounts:
            print(f"\nAccount: {acct['name']}")
            print(f"Currency: {acct['currency']}")
            print(f"Balance: {acct['balance']}")

            # Get transactions
            txs = bridge.get_transactions(acct['id'])
            if txs:
                print("\nRecent Transactions:")
                for tx in txs[:5]:  # Show last 5
                    print(f"- {tx['type']}: {tx['amount']} {tx['currency']}")


if __name__ == "__main__":
    main()
