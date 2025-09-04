#!/usr/bin/env python3
"""
Integration test for crypto signing feature flag functionality.
"""

import os
import time
import sys

# Enable crypto signing for this test
os.environ["FEATURE_CRYPTO_SIGNING"] = "true"

from zero_trust_architecture import ZeroTrustBus, Message, MessageType
from crypto.signing import sign_message, Signature

def test_crypto_integration():
    """Test crypto signing integration with zero trust bus."""
    print("Testing crypto signing integration...")
    
    bus = ZeroTrustBus()
    bus.register_component("claude_main", "test_key_1")
    bus.register_component("claude_code", "test_key_2")
    
    # Create message payload for signing
    message_payload = {
        "sender_id": "claude_main",
        "receiver_id": "claude_code", 
        "message_type": "execute",
        "content_reference": "crypto_test_message",
        "timestamp": time.time(),
        "nonce": "crypto_test_nonce_123"
    }
    
    # Sign the payload
    crypto_signature = sign_message(message_payload, "claude_main_key")
    
    # Create message with crypto signature
    message_with_crypto = Message(
        sender_id="claude_main",
        receiver_id="claude_code",
        message_type=MessageType.EXECUTE,
        content_reference="crypto_test_message",
        timestamp=message_payload["timestamp"],
        nonce="crypto_test_nonce_123",
        signature="legacy_signature",  # Keep legacy field
        signature_obj=crypto_signature  # New crypto signature
    )
    
    # Test message validation with crypto signature
    result = bus.route_message(message_with_crypto, "Testing crypto signature integration")
    print(f"Message with valid crypto signature routed: {result}")
    
    # Test message with invalid crypto signature
    invalid_signature = Signature(
        algorithm="INVALID_ALG",
        signature_data="invalid_signature_data",
        public_key_id="wrong_key",
        timestamp=time.time()
    )
    
    message_with_invalid_crypto = Message(
        sender_id="claude_main", 
        receiver_id="claude_code",
        message_type=MessageType.EXECUTE,
        content_reference="crypto_test_message_2",
        timestamp=time.time(),
        nonce="crypto_test_nonce_456",
        signature="legacy_signature",
        signature_obj=invalid_signature
    )
    
    result_invalid = bus.route_message(message_with_invalid_crypto, "Testing invalid crypto signature")
    print(f"Message with invalid crypto signature routed: {result_invalid}")
    
    # Check verifier status
    verifier_status = bus.get_verifier_status()
    print(f"Verifier status: {verifier_status}")
    
    # Test without crypto signature (should still work)
    message_no_crypto = Message(
        sender_id="claude_main",
        receiver_id="claude_code", 
        message_type=MessageType.EXECUTE,
        content_reference="no_crypto_test",
        timestamp=time.time(),
        nonce="no_crypto_nonce_789",
        signature="legacy_signature"
        # No signature_obj
    )
    
    result_no_crypto = bus.route_message(message_no_crypto, "Testing message without crypto signature")
    print(f"Message without crypto signature routed: {result_no_crypto}")
    
    print(f"Integration test complete. Expected: valid=True, invalid=False, no_crypto=True")
    print(f"Actual results: valid={result}, invalid={result_invalid}, no_crypto={result_no_crypto}")
    
    return result and not result_invalid and result_no_crypto

if __name__ == "__main__":
    success = test_crypto_integration()
    sys.exit(0 if success else 1)