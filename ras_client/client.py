"""
EpochCore RAS Client Library
Provides simple integration with the RAS API service
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests


class RASClient:
    """Client for interacting with RAS API"""

    def __init__(self, api_key: str, base_url: str = "https://api.ras.epochcore.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    def verify_security(self) -> Dict:
        """Run security verification"""
        response = self.session.post(f"{self.base_url}/api/v1/verify")
        response.raise_for_status()
        return response.json()

    def create_session(self) -> Dict:
        """Create a new security session"""
        response = self.session.post(f"{self.base_url}/api/v1/sessions")
        response.raise_for_status()
        return response.json()

    def verify_proof(self, block_data: str, block_index: int, proof: list) -> Dict:
        """Verify a cryptographic proof"""
        data = {
            "block_data": block_data,
            "block_index": block_index,
            "proof": proof
        }
        response = self.session.post(
            f"{self.base_url}/api/v1/proofs/verify",
            json=data
        )
        response.raise_for_status()
        return response.json()

    def get_status(self) -> Dict:
        """Get RAS system status"""
        response = self.session.get(f"{self.base_url}/api/v1/status")
        response.raise_for_status()
        return response.json()


# Example usage:
if __name__ == "__main__":
    # Initialize client
    api_key = os.getenv("RAS_API_KEY")
    client = RASClient(api_key)

    # Check system status
    status = client.get_status()
    print(f"System status: {status['status']}")

    # Run security verification
    result = client.verify_security()
    print(f"Security verification: {result['status']}")

    # Create session
    session = client.create_session()
    print(f"Session created, expires: {session['expires']}")

    # Verify proof
    proof_result = client.verify_proof(
        "test data",
        0,
        [{"hash": "abc", "position": "left"}]
    )
    print(f"Proof verification: {proof_result['valid']}")
