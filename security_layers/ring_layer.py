"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

Ring Signature Security Layer
"""

from datetime import datetime
from typing import Dict, List

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class RingSignatureLayer:
    """Implements ring signature security features."""

    def __init__(self, ring_size: int = 5):
        self.ring_size = ring_size
        self._generate_ring()

    def _generate_ring(self):
        """Generate a ring of public/private key pairs."""
        self.ring_keys = []
        for _ in range(self.ring_size):
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            self.ring_keys.append({
                'private': private_key,
                'public': private_key.public_key()
            })

    def _compute_ring_signature(self, message: bytes, signer_index: int) -> List[bytes]:
        """Compute ring signature for a message."""
        signatures = []
        hash_obj = hashes.Hash(hashes.SHA256())
        hash_obj.update(message)
        message_hash = hash_obj.finalize()

        # Sign with each key in the ring
        for i in range(self.ring_size):
            if i == signer_index:
                # Real signer
                signature = self.ring_keys[i]['private'].sign(
                    message_hash,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            else:
                # Generate random signature for non-signers
                dummy_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048
                )
                signature = dummy_key.sign(
                    message_hash,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )
            signatures.append(signature)

        return signatures

    def protect(self, data: Dict) -> Dict:
        """Apply ring signature protection to data."""
        # Convert data to bytes
        message = str(data).encode()

        # Choose random signer from ring
        signer_index = hash(str(datetime.now())) % self.ring_size

        # Generate ring signature
        signatures = self._compute_ring_signature(message, signer_index)

        return {
            'ring_protected_data': data,
            'ring_signatures': [sig.hex() for sig in signatures],
            'public_keys': [
                key['public'].public_numbers().n
                for key in self.ring_keys
            ],
            'timestamp': datetime.now().isoformat()
        }

    def verify(self, protected_data: Dict) -> bool:
        """Verify ring signature protection."""
        if not all(key in protected_data for key in
                   ['ring_protected_data', 'ring_signatures', 'public_keys']):
            return False

        message = str(protected_data['ring_protected_data']).encode()
        hash_obj = hashes.Hash(hashes.SHA256())
        hash_obj.update(message)
        message_hash = hash_obj.finalize()

        # Verify at least one signature is valid
        try:
            signatures = [bytes.fromhex(sig)
                          for sig in protected_data['ring_signatures']]
            valid_count = 0

            for sig, pub_key in zip(signatures, self.ring_keys):
                try:
                    pub_key['public'].verify(
                        sig,
                        message_hash,
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    valid_count += 1
                except Exception:
                    continue

            return valid_count > 0
        except Exception:
            return False
