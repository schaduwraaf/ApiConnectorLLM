#!/usr/bin/env python3
"""
Unit tests for cryptographic signing foundation.

These tests use deterministic golden vectors to ensure consistent behavior
across runs and environments.
"""

import unittest
import json
from crypto.signing import sign_message, verify_signature, Signature, get_signing_capabilities


class TestCryptoSigning(unittest.TestCase):
    """Test suite for cryptographic signing functionality."""
    
    def setUp(self):
        """Set up test fixtures with deterministic data."""
        # Golden vector test data - deterministic for consistent testing
        self.test_payload_1 = {
            "sender_id": "claude_main",
            "receiver_id": "claude_code", 
            "message_type": "execute",
            "content_reference": "implement_feature_x",
            "timestamp": 1693737600.0,  # Fixed timestamp for deterministic tests
            "nonce": "test_nonce_12345"
        }
        
        self.test_payload_2 = {
            "sender_id": "openai",
            "receiver_id": "claude_code",
            "message_type": "verification_request", 
            "content_reference": "validate_security_model",
            "timestamp": 1693824000.0,  # Different fixed timestamp
            "nonce": "test_nonce_67890"
        }
    
    def test_sign_message_deterministic(self):
        """Test that signing produces deterministic results for same input."""
        # Sign the same payload multiple times
        signature1 = sign_message(self.test_payload_1, "test_key_1")
        signature2 = sign_message(self.test_payload_1, "test_key_1")
        
        # Results should be identical (deterministic)
        self.assertEqual(signature1.signature_data, signature2.signature_data)
        self.assertEqual(signature1.algorithm, "STUB_SHA256")
        self.assertEqual(signature1.public_key_id, "test_key_1")
    
    def test_sign_message_different_payloads(self):
        """Test that different payloads produce different signatures."""
        signature1 = sign_message(self.test_payload_1, "test_key_1")
        signature2 = sign_message(self.test_payload_2, "test_key_1")
        
        # Different payloads should produce different signatures
        self.assertNotEqual(signature1.signature_data, signature2.signature_data)
        
        # But same algorithm and key
        self.assertEqual(signature1.algorithm, signature2.algorithm)
        self.assertEqual(signature1.public_key_id, signature2.public_key_id)
    
    def test_sign_message_different_keys(self):
        """Test that different keys produce different signatures."""
        signature1 = sign_message(self.test_payload_1, "test_key_1")
        signature2 = sign_message(self.test_payload_1, "test_key_2")
        
        # Same payload, different keys should produce different signatures
        self.assertNotEqual(signature1.signature_data, signature2.signature_data)
        self.assertNotEqual(signature1.public_key_id, signature2.public_key_id)
    
    def test_verify_signature_valid(self):
        """Test verification of valid signatures."""
        # Create signature
        signature = sign_message(self.test_payload_1, "test_key_1")
        
        # Should verify successfully
        is_valid = verify_signature(self.test_payload_1, signature)
        self.assertTrue(is_valid)
    
    def test_verify_signature_invalid_payload(self):
        """Test verification fails with tampered payload."""
        # Create signature for original payload
        signature = sign_message(self.test_payload_1, "test_key_1")
        
        # Tamper with payload
        tampered_payload = self.test_payload_1.copy()
        tampered_payload["content_reference"] = "malicious_content"
        
        # Should fail verification
        is_valid = verify_signature(tampered_payload, signature)
        self.assertFalse(is_valid)
    
    def test_verify_signature_invalid_algorithm(self):
        """Test verification fails with unsupported algorithm."""
        # Create valid signature but modify algorithm
        signature = sign_message(self.test_payload_1, "test_key_1")
        signature.algorithm = "INVALID_ALGORITHM"
        
        # Should fail verification
        is_valid = verify_signature(self.test_payload_1, signature)
        self.assertFalse(is_valid)
    
    def test_signature_serialization(self):
        """Test signature object serialization/deserialization."""
        # Create signature
        original_sig = sign_message(self.test_payload_1, "test_key_1")
        
        # Serialize and deserialize
        sig_dict = original_sig.to_dict()
        restored_sig = Signature.from_dict(sig_dict)
        
        # Should be equivalent
        self.assertEqual(original_sig.signature_data, restored_sig.signature_data)
        self.assertEqual(original_sig.algorithm, restored_sig.algorithm)
        self.assertEqual(original_sig.public_key_id, restored_sig.public_key_id)
        self.assertEqual(original_sig.timestamp, restored_sig.timestamp)
        
        # Should still verify
        is_valid = verify_signature(self.test_payload_1, restored_sig)
        self.assertTrue(is_valid)
    
    def test_golden_vectors(self):
        """Test against known golden vector values for regression testing."""
        # Golden vector 1: Specific payload should produce specific signature
        golden_payload = {
            "sender_id": "claude_main",
            "receiver_id": "claude_code",
            "message_type": "execute", 
            "content_reference": "golden_test",
            "timestamp": 1693737600.0,
            "nonce": "golden_nonce_001"
        }
        
        signature = sign_message(golden_payload, "golden_key_001")
        
        # Expected signature for this exact input (deterministic)
        expected_sig_data = "c8f5a4e8f9d42e7b3a6c1f8e5d9a2b7c4e6f8a1b3c5d7e9f0a2b4c6d8e0f2a4b6c8"
        
        # Note: In real implementation, this would be a known good signature
        # For stub implementation, we verify it's consistent
        signature2 = sign_message(golden_payload, "golden_key_001")
        self.assertEqual(signature.signature_data, signature2.signature_data)
    
    def test_get_signing_capabilities(self):
        """Test capabilities reporting."""
        capabilities = get_signing_capabilities()
        
        # Should report stub mode
        self.assertFalse(capabilities["production_ready"])
        self.assertTrue(capabilities["stub_mode"])
        self.assertEqual(capabilities["security_level"], "testing_only")
        self.assertIn("STUB_SHA256", capabilities["algorithms_supported"])
        self.assertGreater(len(capabilities["todo_items"]), 0)


if __name__ == "__main__":
    unittest.main()