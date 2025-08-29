"""
AuditTrail-as-a-Service (ATaaS)
Immutable audit logging with cryptographic verification
"""

import base64
import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, List, Optional


class AuditTrail:
    def __init__(self, org_id: str, tier: str = "starter"):
        self.org_id = org_id
        self.tier = tier
        self.log_chain = []
        self.last_hash = None

    def log_event(self, event_type: str, data: Dict) -> Dict:
        """Log an event with cryptographic chaining"""
        timestamp = datetime.utcnow().isoformat()

        event = {
            "org_id": self.org_id,
            "event_type": event_type,
            "timestamp": timestamp,
            "data": data,
            "prev_hash": self.last_hash
        }

        # Create hash chain
        event_bytes = json.dumps(event, sort_keys=True).encode()
        event["hash"] = hashlib.sha256(event_bytes).hexdigest()
        self.last_hash = event["hash"]

        # Create proof capsule
        proof = self._create_proof_capsule(event)
        event["proof"] = proof

        self.log_chain.append(event)
        return event

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire log chain"""
        if not self.log_chain:
            return True

        for i in range(1, len(self.log_chain)):
            curr = self.log_chain[i]
            prev = self.log_chain[i-1]

            # Verify hash chain
            if curr["prev_hash"] != prev["hash"]:
                return False

            # Verify event hash
            event_copy = curr.copy()
            del event_copy["hash"]
            del event_copy["proof"]
            event_bytes = json.dumps(event_copy, sort_keys=True).encode()
            computed_hash = hashlib.sha256(event_bytes).hexdigest()

            if computed_hash != curr["hash"]:
                return False

        return True

    def export_logs(self, start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> List[Dict]:
        """Export logs within a time range"""
        if not start_time:
            start_time = datetime.min
        if not end_time:
            end_time = datetime.max

        return [
            event for event in self.log_chain
            if start_time <= datetime.fromisoformat(event["timestamp"]) <= end_time
        ]

    def _create_proof_capsule(self, event: Dict) -> str:
        """Create a proof capsule for an event"""
        # Create capsule with event data and metadata
        capsule = {
            "event_hash": event["hash"],
            "timestamp": event["timestamp"],
            "org_id": self.org_id,
            "tier": self.tier
        }

        # Sign capsule
        capsule_bytes = json.dumps(capsule, sort_keys=True).encode()
        signature = hmac.new(
            b"your-secret-key",  # In production, use proper key management
            capsule_bytes,
            hashlib.sha256
        ).digest()

        # Combine and encode
        proof = {
            "capsule": capsule,
            "signature": base64.b64encode(signature).decode()
        }

        return base64.b64encode(
            json.dumps(proof).encode()
        ).decode()


# Example usage
if __name__ == "__main__":
    # Initialize AuditTrail for an organization
    audit = AuditTrail("org_123", "business")

    # Log some events
    audit.log_event("user_login", {
        "user_id": "user_456",
        "ip": "192.168.1.1",
        "success": True
    })

    audit.log_event("data_access", {
        "user_id": "user_456",
        "resource": "customer_records",
        "action": "read"
    })

    # Verify chain
    is_valid = audit.verify_chain()
    print(f"Log chain valid: {is_valid}")

    # Export recent logs
    recent_logs = audit.export_logs(
        start_time=datetime.utcnow().replace(hour=0, minute=0)
    )
    print(f"Recent logs: {len(recent_logs)}")
