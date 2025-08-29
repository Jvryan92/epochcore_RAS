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
import os
import secrets
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional

from capsule_metadata import MerkleTree


class SecurityManager:
    """
    Enhanced security features for EPOCH5
    """

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = (secret_key or
                           os.getenv("EPOCH_SECRET_KEY") or
                           secrets.token_hex(32))
        self._session_cache: Dict[str, Dict] = {}
        self._key_hash = hashlib.sha256(self.secret_key.encode()).hexdigest()
        self.merkle_tree = MerkleTree([])

        # Initialize secure proof chain
        self._proof_chain = []
        self._chain_lock = threading.Lock()

    def generate_session_token(
            self,
            agent_did: str,
            expires_in: int = 3600
    ) -> Dict[str, str]:
        """Generate a secure session token for an agent"""
        timestamp = datetime.utcnow()
        expiry = timestamp + timedelta(seconds=expires_in)

        # Create token payload
        payload = f"{agent_did}:{timestamp.isoformat()}:{expiry.isoformat()}"

        # Generate HMAC
        signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        token = f"{payload}:{signature}"

        # Cache session
        self._session_cache[agent_did] = {
            "token": token,
            "expires": expiry
        }

        return {
            "token": token,
            "expires": expiry.isoformat()
        }

    def validate_session(self, agent_did: str, token: str) -> bool:
        """Validate a session token"""
        try:
            with self._chain_lock:
                # Check cache first
                cached = self._session_cache.get(agent_did)
                if not cached or cached["token"] != token:
                    return False

                if cached["expires"] < datetime.utcnow():
                    del self._session_cache[agent_did]
                    return False

                # Parse token
                if ":" not in token:
                    return False

                payload, signature = token.rsplit(":", 1)

                # Validate signature length
                if len(signature) != 64:  # SHA-256 = 32 bytes = 64 hex chars
                    return False

                # Validate HMAC with key rotation
                current_key = self.secret_key.encode()
                prev_key = self._get_prev_key().encode()

                expected_current = hmac.new(
                    current_key,
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()

                expected_prev = hmac.new(
                    prev_key,
                    payload.encode(),
                    hashlib.sha256
                ).hexdigest()

                # Compare against both current and previous key
                is_valid = (
                    hmac.compare_digest(signature, expected_current) or
                    hmac.compare_digest(signature, expected_prev)
                )

                if is_valid:
                    # Add to proof chain
                    self._proof_chain.append({
                        "agent": agent_did,
                        "timestamp": datetime.utcnow().isoformat(),
                        "hash": hashlib.sha256(token.encode()).hexdigest()
                    })

                return is_valid

        except Exception:
            return False

    def _get_prev_key(self) -> str:
        """Get previous rotation of secret key"""
        # Simple key rotation using hash chain
        return hashlib.sha256(self.secret_key.encode()).hexdigest()
