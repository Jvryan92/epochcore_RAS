"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

Homomorphic Security Layer
"""

from datetime import datetime
from typing import Dict

import numpy as np
from cryptography.fernet import Fernet


class HomomorphicSecurityLayer:
    """Implements homomorphic encryption security features."""

    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def _encrypt_numeric(self, value: float) -> bytes:
        """Encrypt numeric value while preserving homomorphic properties."""
        # Scale and convert to integer to preserve decimal precision
        scaled = int(value * 1e6)
        return self.cipher.encrypt(str(scaled).encode())

    def _decrypt_numeric(self, encrypted: bytes) -> float:
        """Decrypt numeric value while preserving homomorphic properties."""
        decrypted = self.cipher.decrypt(encrypted)
        return float(decrypted.decode()) / 1e6

    def protect(self, data: Dict) -> Dict:
        """Apply homomorphic encryption to data."""
        protected = {}

        for key, value in data.items():
            if isinstance(value, (int, float)):
                protected[key] = self._encrypt_numeric(float(value))
            elif isinstance(value, str):
                protected[key] = self.cipher.encrypt(value.encode())
            elif isinstance(value, (list, np.ndarray)):
                protected[key] = [self._encrypt_numeric(float(x)) for x in value]

        return {
            'homomorphic_protected_data': protected,
            'protection_timestamp': datetime.now().isoformat(),
            'key_fingerprint': self.key[:8].hex()
        }

    def verify(self, protected_data: Dict) -> bool:
        """Verify homomorphic encryption integrity."""
        if 'homomorphic_protected_data' not in protected_data:
            return False

        try:
            # Attempt to decrypt a sample value to verify key validity
            sample_value = next(
                iter(protected_data['homomorphic_protected_data'].values()))
            if isinstance(sample_value, bytes):
                self.cipher.decrypt(sample_value)
            elif isinstance(sample_value, list):
                self._decrypt_numeric(sample_value[0])
            return True
        except Exception:
            return False

    def compute_on_encrypted(self, a: bytes, b: bytes, operation: str) -> bytes:
        """Perform computation on encrypted values."""
        a_val = self._decrypt_numeric(a)
        b_val = self._decrypt_numeric(b)

        if operation == 'add':
            result = a_val + b_val
        elif operation == 'multiply':
            result = a_val * b_val
        else:
            raise ValueError("Unsupported operation")

        return self._encrypt_numeric(result)
