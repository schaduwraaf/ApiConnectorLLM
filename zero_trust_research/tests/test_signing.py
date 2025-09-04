#!/usr/bin/env python3
"""
Unit tests for Ed25519 cryptographic signing.

These tests verify the production Ed25519 implementation works correctly
with real cryptographic operations.
"""

import unittest
import json
import tempfile
import os
from pathlib import Path

from crypto.signing import (
    sign_message, verify_signature, Signature, get_signing_capabilities,
    create_test_signature, SigningError, VerificationError
)
from crypto.keys import generate_keypair, save_private_key, save_public_key, KeyManagementError


class TestEd25519Signing(unittest.TestCase):
    """Test suite for Ed25519 cryptographic signing functionality."""
    
    def setUp(self):
        """Set up test fixtures with real Ed25519 keys."""
        # Generate test keypairs
        self.private_key1, self.public_key1 = generate_keypair()
        self.private_key2, self.public_key2 = generate_keypair()
        
        # Test payloads
        self.test_payload_1 = {
            "sender_id": "claude_main",
            "receiver_id": "claude_code", 
            "message_type": "execute",
            "content_reference": "implement_feature_x",
            "timestamp": 1693737600.0,
            "nonce": "test_nonce_12345"
        }
        
        self.test_payload_2 = {
            "sender_id": "openai",
            "receiver_id": "claude_code",
            "message_type": "verification_request", 
            "content_reference": "validate_security_model",
            "timestamp": 1693824000.0,
            "nonce": "test_nonce_67890"
        }
    
    def test_sign_message_with_key_object(self):
        """Test signing with Ed25519PrivateKey object."""
        signature = sign_message(self.test_payload_1, self.private_key1, "test_key_1")
        
        self.assertEqual(signature.algorithm, "Ed25519")
        self.assertEqual(signature.public_key_id, "test_key_1")
        self.assertIsNotNone(signature.signature_data)
        self.assertIsNotNone(signature.key_fingerprint)
        self.assertGreater(signature.timestamp, 0)
    
    def test_sign_message_auto_key_id(self):
        """Test signing with automatic key ID generation."""
        signature = sign_message(self.test_payload_1, self.private_key1)
        
        self.assertEqual(signature.algorithm, "Ed25519")
        self.assertIsNotNone(signature.public_key_id)
        self.assertEqual(len(signature.public_key_id), 16)  # SHA256 truncated to 16 chars
    
    def test_verify_signature_valid(self):
        """Test verification of valid Ed25519 signatures."""
        signature = sign_message(self.test_payload_1, self.private_key1, "test_key_1")
        
        # Should verify with corresponding public key
        is_valid = verify_signature(self.test_payload_1, signature, self.public_key1)
        self.assertTrue(is_valid)
    
    def test_verify_signature_invalid_key(self):
        """Test verification fails with wrong public key."""
        signature = sign_message(self.test_payload_1, self.private_key1, "test_key_1")
        
        # Should fail with different public key
        is_valid = verify_signature(self.test_payload_1, signature, self.public_key2)
        self.assertFalse(is_valid)
    
    def test_verify_signature_tampered_payload(self):
        """Test verification fails with tampered payload."""
        signature = sign_message(self.test_payload_1, self.private_key1, "test_key_1")
        
        # Tamper with payload
        tampered_payload = self.test_payload_1.copy()
        tampered_payload["content_reference"] = "malicious_content"
        
        # Should fail verification
        is_valid = verify_signature(tampered_payload, signature, self.public_key1)
        self.assertFalse(is_valid)
    
    def test_verify_signature_invalid_algorithm(self):
        """Test verification fails with unsupported algorithm."""
        signature = sign_message(self.test_payload_1, self.private_key1, "test_key_1")
        signature.algorithm = "INVALID_ALGORITHM"
        
        # Should fail verification
        is_valid = verify_signature(self.test_payload_1, signature, self.public_key1)
        self.assertFalse(is_valid)
    
    def test_signature_serialization(self):
        """Test signature object serialization/deserialization."""
        original_sig = sign_message(self.test_payload_1, self.private_key1, "test_key_1")
        
        # Serialize and deserialize
        sig_dict = original_sig.to_dict()
        restored_sig = Signature.from_dict(sig_dict)
        
        # Should be equivalent
        self.assertEqual(original_sig.signature_data, restored_sig.signature_data)
        self.assertEqual(original_sig.algorithm, restored_sig.algorithm)
        self.assertEqual(original_sig.public_key_id, restored_sig.public_key_id)
        self.assertEqual(original_sig.key_fingerprint, restored_sig.key_fingerprint)
        
        # Should still verify
        is_valid = verify_signature(self.test_payload_1, restored_sig, self.public_key1)
        self.assertTrue(is_valid)
    
    def test_different_payloads_different_signatures(self):
        """Test that different payloads produce different signatures."""
        signature1 = sign_message(self.test_payload_1, self.private_key1, "test_key_1")
        signature2 = sign_message(self.test_payload_2, self.private_key1, "test_key_1")
        
        # Different payloads should produce different signatures
        self.assertNotEqual(signature1.signature_data, signature2.signature_data)
        
        # But same algorithm and key
        self.assertEqual(signature1.algorithm, signature2.algorithm)
        self.assertEqual(signature1.public_key_id, signature2.public_key_id)
        self.assertEqual(signature1.key_fingerprint, signature2.key_fingerprint)
    
    def test_different_keys_different_signatures(self):
        """Test that different keys produce different signatures."""
        signature1 = sign_message(self.test_payload_1, self.private_key1, "test_key_1")
        signature2 = sign_message(self.test_payload_1, self.private_key2, "test_key_2")
        
        # Same payload, different keys should produce different signatures
        self.assertNotEqual(signature1.signature_data, signature2.signature_data)
        self.assertNotEqual(signature1.public_key_id, signature2.public_key_id)
        self.assertNotEqual(signature1.key_fingerprint, signature2.key_fingerprint)
    
    def test_key_fingerprint_validation(self):
        """Test that key fingerprint validation works."""
        signature = sign_message(self.test_payload_1, self.private_key1, "test_key_1")
        
        # Tamper with fingerprint
        signature.key_fingerprint = "wrong_fingerprint"
        
        # Should fail verification
        is_valid = verify_signature(self.test_payload_1, signature, self.public_key1)
        self.assertFalse(is_valid)
    
    def test_create_test_signature(self):
        """Test ephemeral signature creation for testing."""
        signature = create_test_signature(self.test_payload_1, "ephemeral_key")
        
        self.assertEqual(signature.algorithm, "Ed25519")
        self.assertEqual(signature.public_key_id, "ephemeral_key")
        self.assertIsNotNone(signature.signature_data)
        
        # Note: Can't verify without the ephemeral public key since it's discarded
    
    def test_file_based_key_operations(self):
        """Test signing and verification with file-based keys."""
        with tempfile.TemporaryDirectory() as temp_dir:
            private_key_path = os.path.join(temp_dir, "test_private.pem")
            public_key_path = os.path.join(temp_dir, "test_public.pem")
            
            # Save keys to files
            save_private_key(self.private_key1, private_key_path)
            save_public_key(self.public_key1, public_key_path)
            
            # Sign with private key file
            signature = sign_message(self.test_payload_1, private_key_path, "file_key_1")
            
            # Verify with public key file
            is_valid = verify_signature(self.test_payload_1, signature, public_key_path)
            self.assertTrue(is_valid)
    
    def test_signing_error_handling(self):
        """Test error handling in signing operations."""
        # Test with invalid key file path
        with self.assertRaises(SigningError):
            sign_message(self.test_payload_1, "/nonexistent/path.pem", "test_key")
        
        # Test without public_key_id for file path
        with self.assertRaises(SigningError):
            sign_message(self.test_payload_1, "/tmp/key.pem")  # No public_key_id
    
    def test_verification_error_handling(self):
        """Test error handling in verification operations."""
        signature = sign_message(self.test_payload_1, self.private_key1, "test_key_1")
        
        # Test with invalid key file path
        with self.assertRaises(VerificationError):
            verify_signature(self.test_payload_1, signature, "/nonexistent/path.pem")
        
        # Test with invalid signature data
        signature.signature_data = "invalid_base64_data"
        with self.assertRaises(VerificationError):
            verify_signature(self.test_payload_1, signature, self.public_key1)
    
    def test_get_signing_capabilities(self):
        """Test capabilities reporting for Ed25519."""
        capabilities = get_signing_capabilities()
        
        # Should report production ready
        self.assertTrue(capabilities["production_ready"])
        self.assertFalse(capabilities["stub_mode"])
        self.assertEqual(capabilities["security_level"], "production")
        self.assertIn("Ed25519", capabilities["algorithms_supported"])
        self.assertEqual(capabilities["key_management"], "filesystem")
        self.assertTrue(capabilities["features"]["canonical_payload"])
        self.assertTrue(capabilities["features"]["key_fingerprints"])
    
    def test_canonical_payload_consistency(self):
        """Test that payload canonicalization is consistent."""
        # Different JSON representations of same data should produce same signature
        payload1 = {"a": 1, "b": 2, "c": 3}
        payload2 = {"c": 3, "b": 2, "a": 1}  # Different order
        payload3 = {"a": 1, "b": 2, "c": 3}  # Same as payload1
        
        sig1 = sign_message(payload1, self.private_key1, "test_key")
        sig2 = sign_message(payload2, self.private_key1, "test_key")
        sig3 = sign_message(payload3, self.private_key1, "test_key")
        
        # All should produce the same signature (canonical form)
        self.assertEqual(sig1.signature_data, sig2.signature_data)
        self.assertEqual(sig1.signature_data, sig3.signature_data)
    
    def test_ed25519_vectors(self):
        """Test with known Ed25519 properties."""
        # Ed25519 signatures should be exactly 64 bytes when decoded
        signature = sign_message(self.test_payload_1, self.private_key1, "test_key")
        
        import base64
        sig_bytes = base64.b64decode(signature.signature_data)
        self.assertEqual(len(sig_bytes), 64)  # Ed25519 signature length
        
        # Key fingerprint should be consistent
        signature2 = sign_message(self.test_payload_2, self.private_key1, "test_key")
        self.assertEqual(signature.key_fingerprint, signature2.key_fingerprint)


if __name__ == "__main__":
    unittest.main()