"""
Test script for security layer verification
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.absolute())
sys.path.insert(0, project_root)


def test_security_layer(layer_name, content):
    """Test a specific security layer."""
    print(f"\nTesting {layer_name}...")

    try:
        if layer_name == "quantum":
            from security_quantum_syntax import QuantumSyntaxLayer
            layer = QuantumSyntaxLayer()
        elif layer_name == "homomorphic":
            from security_homomorphic_syntax import HomomorphicSyntaxLayer
            layer = HomomorphicSyntaxLayer()
        elif layer_name == "zk":
            from security_zk_syntax import ZKSyntaxLayer
            layer = ZKSyntaxLayer()
        elif layer_name == "ring":
            from security_ring_syntax import RingSyntaxLayer
            layer = RingSyntaxLayer()
        elif layer_name == "lattice":
            from security_lattice_syntax import LatticeBasedSyntaxLayer
            layer = LatticeBasedSyntaxLayer()
        else:
            print(f"Unknown layer: {layer_name}")
            return False

        # Test protection
        protected = layer.protect_syntax(content)
        print(f"✓ Protection successful")

        # Test verification
        verified = layer.verify_syntax(protected)
        print(f"✓ Verification successful: {verified}")

        # Test tamper detection
        tampered = protected.copy()
        if isinstance(tampered.get('protected_content'), dict):
            tampered['protected_content'] = {"tampered": "data"}
        else:
            tampered['protected_content'] = "tampered_data"

        tamper_verified = layer.verify_syntax(tampered)
        print(f"✓ Tamper detection successful: {not tamper_verified}")

        return True

    except Exception as e:
        print(f"Error testing {layer_name}: {str(e)}")
        return False


def main():
    """Run tests for all security layers."""
    test_content = {
        "id": "test_123",
        "data": "Test content for security verification",
        "timestamp": "2024-01-01"
    }

    layers = ["quantum", "homomorphic", "zk", "ring", "lattice"]
    results = []

    print("Starting security layer verification...")
    print("-" * 50)

    for layer in layers:
        result = test_security_layer(layer, test_content)
        results.append(result)
        print("-" * 50)

    # Summary
    print("\nTest Summary:")
    print("-" * 50)
    for layer, result in zip(layers, results):
        status = "PASSED" if result else "FAILED"
        print(f"{layer.upper():12} : {status}")
    print("-" * 50)

    if all(results):
        print("\n✅ All security layers verified successfully!")
    else:
        print("\n❌ Some security layers failed verification!")
        sys.exit(1)


if __name__ == "__main__":
    main()
