import hmac
import hashlib
import secrets
from typing import Dict, Optional
from datetime import datetime, timedelta


class SecurityManager:
    """
    Enhanced security features for EPOCH5
    """

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or secrets.token_hex(32)
        self._session_cache: Dict[str, Dict] = {}

    def generate_session_token(
        self, agent_did: str, expires_in: int = 3600
    ) -> Dict[str, str]:
        """Generate a secure session token for an agent"""
        timestamp = datetime.utcnow()
        expiry = timestamp + timedelta(seconds=expires_in)

        # Create token payload
        payload = f"{agent_did}:{timestamp.isoformat()}:{expiry.isoformat()}"

        # Generate HMAC
        signature = hmac.new(
            self.secret_key.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

        token = f"{payload}:{signature}"

        # Cache session
        self._session_cache[agent_did] = {"token": token, "expires": expiry}

        return {"token": token, "expires": expiry.isoformat()}

    def validate_session(self, agent_did: str, token: str) -> bool:
        """Validate a session token"""
        try:
            # Check cache first
            cached = self._session_cache.get(agent_did)
            if not cached or cached["token"] != token:
                return False

            if cached["expires"] < datetime.utcnow():
                del self._session_cache[agent_did]
                return False

            # Validate HMAC
            payload, signature = token.rsplit(":", 1)
            expected_signature = hmac.new(
                self.secret_key.encode(), payload.encode(), hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        except Exception:
            return False
