"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

Lattice-based Security Layer
"""

import hashlib
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np


class LatticeSecurityLayer:
    """Implements lattice-based encryption security features."""

    def __init__(self, dimension: int = 64, q: int = 251):  # Using smaller dimension and prime
        self.dimension = dimension  # Reduced lattice dimension for better compatibility
        self.q = q  # Using Mersenne prime 2^8-5 = 251 for uint8 compatibility
        self._generate_keys()

    def _generate_keys(self):
        """Generate lattice-based public/private key pair."""
        # Initialize with fixed shape arrays
        s_shape = (self.dimension,)
        A_shape = (self.dimension, self.dimension)
        e_shape = (self.dimension,)

        # Generate private key
        self.s = np.zeros(s_shape, dtype=int)
        temp_s = np.random.normal(0, 0.5, s_shape)
        np.clip(temp_s, -4, 4, out=temp_s)  # Limit range
        self.s = temp_s.astype(int) % self.q

        # Generate public key
        A = np.random.randint(0, self.q, size=A_shape, dtype=int)
        e = np.zeros(e_shape, dtype=int)
        temp_e = np.random.normal(0, 0.5, e_shape)
        np.clip(temp_e, -4, 4, out=temp_e)  # Limit range
        e = temp_e.astype(int) % self.q

        # Ensure compatible shapes for matrix multiplication
        result = np.zeros(self.dimension, dtype=int)
        for i in range(self.dimension):
            result[i] = np.sum(A[i] * self.s) % self.q

        self.public_key = {
            'A': A,
            'b': (result + e) % self.q
        }

    def _encode_message(self, message: str) -> np.ndarray:
        """Encode message into lattice points."""
        # Hash message to fixed length
        hash_obj = hashlib.sha256(message.encode())
        hash_bytes = hash_obj.digest()

        # Convert hash to fixed-size array
        arr = np.frombuffer(hash_bytes, dtype=np.uint8)

        # Ensure array has exactly dimension elements
        if len(arr) > self.dimension:
            arr = arr[:self.dimension]
        elif len(arr) < self.dimension:
            # Pad with consistent values
            pad_length = self.dimension - len(arr)
            arr = np.concatenate([arr, np.full(pad_length, 0xff, dtype=np.uint8)])

        # Ensure type and shape
        arr = arr.astype(np.int64)
        arr = arr.reshape(self.dimension)

        return arr % self.q

    def _decode_message(self, lattice_points: np.ndarray) -> str:
        """Decode message from lattice points."""
        bytes_data = (lattice_points % 256).astype(np.uint8).tobytes()
        return bytes_data.decode().rstrip('\0')

    def _encrypt_lattice(self, m: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Encrypt using lattice-based scheme."""
        r = np.random.normal(0, 1, self.dimension).astype(int) % self.q
        e1 = np.random.normal(0, 1, self.dimension).astype(int) % self.q
        e2 = np.random.normal(0, 1, self.dimension).astype(int) % self.q

        u = (self.public_key['A'].T @ r + e1) % self.q
        v = (r @ self.public_key['b'] + e2 + (self.q // 2) * m) % self.q

        return u, v

    def _decrypt_lattice(self, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        """Decrypt using lattice-based scheme."""
        # Validate array shapes
        if u.shape != (self.dimension,) or v.shape != (self.dimension,):
            raise ValueError("Invalid array shapes for decryption")

        # Cast to int64 to prevent overflow
        u = u.astype(np.int64)
        v = v.astype(np.int64)
        s = self.s.astype(np.int64)

        # Perform decryption with modulo operations
        w = (v - np.sum(u * s)) % self.q
        result = ((w * 2 + self.q // 2) // self.q) % 2

        return result.reshape(self.dimension)

    def protect(self, data: Dict) -> Dict:
        """Apply lattice-based protection to data."""
        message = str(data)
        encoded = self._encode_message(message)
        u, v = self._encrypt_lattice(encoded)

        return {
            'lattice_protected_data': {
                'u': u.tolist(),
                'v': v.tolist()
            },
            'public_key_hash': hash(str(self.public_key['b'].tobytes())),
            'timestamp': datetime.now().isoformat()
        }

    def verify(self, protected_data: Dict) -> bool:
        """Verify lattice-based protection."""
        if 'lattice_protected_data' not in protected_data:
            return False

        try:
            # Convert to numpy arrays with explicit type
            u = np.array(protected_data['lattice_protected_data']['u'], dtype=np.int64)
            v = np.array(protected_data['lattice_protected_data']['v'], dtype=np.int64)

            # Check shapes and ranges
            def check_array(x):
                if x.shape != (self.dimension,):
                    return False
                return np.all((0 <= x) & (x < self.q))

            if not (check_array(u) and check_array(v)):
                return False

            # Decrypt and verify format
            try:
                decrypted = self._decrypt_lattice(u, v)
                decoded = self._decode_message(decrypted)
                return isinstance(decoded, str) and len(decoded) > 0
            except (UnicodeDecodeError, ValueError):
                return False

        except Exception as e:
            print(f"Lattice verification error: {str(e)}")
            return False
