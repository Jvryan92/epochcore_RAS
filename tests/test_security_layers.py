"""
PROTECTED FILE - EPOCHCORE RAS
Copyright (c) 2024 John Ryan, EpochCore Business, Charlotte NC
All Rights Reserved

Test suite for enhanced security layers.
"""

import json

import pytest

from security_enhanced_syntax import EnhancedSyntaxProtection
from security_homomorphic_syntax import HomomorphicSyntaxLayer
from security_lattice_syntax import LatticeBasedSyntaxLayer
from security_quantum_syntax import QuantumSyntaxLayer
from security_ring_syntax import RingSyntaxLayer
from security_zk_syntax import ZKSyntaxLayer


def test_quantum_layer():
    """Test quantum-resistant protection layer."""
    layer = QuantumSyntaxLayer()
    test_content = {"test": "data"}

    # Test protection
    protected = layer.protect_syntax(test_content)
    assert isinstance(protected, dict)
    assert 'quantum_signature' in protected
    assert 'salt' in protected
    assert 'iterations' in protected

    # Test verification
    assert layer.verify_syntax(protected)

    # Test tamper detection
    tampered = protected.copy()
    tampered['protected_content'] = {"tampered": "data"}
    assert not layer.verify_syntax(tampered)


def test_homomorphic_layer():
    """Test homomorphic encryption layer."""
    layer = HomomorphicSyntaxLayer()
    test_content = {"test": "data"}

    # Test protection
    protected = layer.protect_syntax(test_content)
    assert isinstance(protected, dict)
    assert 'encrypted_content' in protected
    assert 'homomorphic_signature' in protected
    assert 'key_id' in protected

    # Test verification
    assert layer.verify_syntax(protected)

    # Test tamper detection
    tampered = protected.copy()
    tampered['encrypted_content'] = "invalid_content"
    assert not layer.verify_syntax(tampered)


def test_zk_layer():
    """Test zero-knowledge proof layer."""
    layer = ZKSyntaxLayer()
    test_content = {"test": "data"}

    # Test protection
    protected = layer.protect_syntax(test_content)
    assert isinstance(protected, dict)
    assert 'commitment' in protected
    assert 'challenge' in protected
    assert 'response' in protected

    # Test verification
    assert layer.verify_syntax(protected)

    # Test tamper detection
    tampered = protected.copy()
    tampered['protected_content'] = {"tampered": "data"}
    assert not layer.verify_syntax(tampered)


def test_ring_layer():
    """Test ring signature layer."""
    layer = RingSyntaxLayer()
    test_content = {"test": "data"}

    # Test protection
    protected = layer.protect_syntax(test_content)
    assert isinstance(protected, dict)
    assert 'ring_signatures' in protected
    assert 'master_signature' in protected
    assert len(protected['ring_signatures']) == layer.ring_size

    # Test verification
    assert layer.verify_syntax(protected)

    # Test tamper detection
    tampered = protected.copy()
    tampered['ring_signatures'] = tampered['ring_signatures'][:-1] + ['invalid']
    assert not layer.verify_syntax(tampered)


def test_lattice_layer():
    """Test lattice-based protection layer."""
    layer = LatticeBasedSyntaxLayer()
    test_content = {"test": "data"}

    # Test protection
    protected = layer.protect_syntax(test_content)
    assert isinstance(protected, dict)
    assert 'encrypted_vector' in protected
    assert 'basis_signature' in protected
    assert 'lattice_proof' in protected
    assert len(protected['encrypted_vector']) == layer.dimension

    # Test verification
    assert layer.verify_syntax(protected)

    # Test tamper detection
    tampered = protected.copy()
    tampered['encrypted_vector'] = [0] * layer.dimension
    assert not layer.verify_syntax(tampered)


def test_enhanced_protection():
    """Test complete enhanced protection system."""
    system = EnhancedSyntaxProtection()
    test_content = {
        "id": "test_123",
        "data": "sensitive information",
        "metadata": {
            "timestamp": "2024-01-01",
            "version": "1.0"
        }
    }

    # Test full protection chain
    protected = system.protect_content(test_content)
    assert isinstance(protected, dict)
    assert all(key in protected for key in [
        'quantum_layer',
        'homomorphic_layer',
        'zk_layer',
        'ring_layer',
        'lattice_layer',
        'final_protected_content'
    ])

    # Test full verification chain
    assert system.verify_content(protected)

    # Test tamper detection at each layer
    tampered = protected.copy()
    for layer in ['quantum_layer', 'homomorphic_layer', 'zk_layer',
                  'ring_layer', 'lattice_layer']:
        tampered_copy = tampered.copy()
        if layer in tampered_copy:
            tampered_copy[layer] = {"invalid": "data"}
            assert not system.verify_content(tampered_copy)


def test_integration():
    """Test integration between all layers."""
    system = EnhancedSyntaxProtection()
    test_data = [
        {"type": "string", "content": "test string"},
        {"type": "number", "content": 12345},
        {"type": "object", "content": {"nested": "data"}},
        {"type": "array", "content": [1, 2, 3, 4, 5]},
        {"type": "complex", "content": {
            "id": "test_456",
            "data": [{"key": "value"}, {"key2": "value2"}],
            "metadata": {"timestamp": "2024-01-01"}
        }}
    ]

    for test_item in test_data:
        # Protect content
        protected = system.protect_content(test_item)

        # Verify all layers are present
        assert all(key in protected for key in [
            'quantum_layer',
            'homomorphic_layer',
            'zk_layer',
            'ring_layer',
            'lattice_layer'
        ])

        # Verify protection chain
        assert system.verify_content(protected)

        # Verify content preservation
        assert protected['final_protected_content'] == test_item
