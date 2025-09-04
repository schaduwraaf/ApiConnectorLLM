#!/usr/bin/env python3
"""
Ed25519 Cryptographic Signing for Zero-Trust Message Validation.

This module provides production-ready Ed25519 digital signatures for
authenticating messages in the zero-trust architecture.
"""

import json
import time
import hashlib
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

from .keys import load_private_key, load_public_key, KeyManagementError


class SigningError(Exception):
    """Raised when signing operations fail."""
    pass


class VerificationError(Exception):
    """Raised when signature verification fails."""
    pass


@dataclass
class Signature:
    """
    Ed25519 signature container with metadata for verification.
    """
    algorithm: str
    signature_data: str  # Base64-encoded signature bytes
    public_key_id: str
    timestamp: float
    key_fingerprint: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize signature to dictionary."""
        result = {
            "algorithm": self.algorithm,
            "signature_data": self.signature_data,
            "public_key_id": self.public_key_id,
            "timestamp": self.timestamp
        }
        if self.key_fingerprint:
            result["key_fingerprint"] = self.key_fingerprint
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Signature':
        """Deserialize signature from dictionary."""
        return cls(
            algorithm=data["algorithm"],
            signature_data=data["signature_data"],
            public_key_id=data["public_key_id"],
            timestamp=data["timestamp"],
            key_fingerprint=data.get("key_fingerprint")
        )


def _canonicalize_payload(payload: Dict[str, Any]) -> bytes:
    """
    Create canonical representation of payload for signing.
    
    Args:
        payload: The message data to canonicalize
        
    Returns:
        Canonical bytes representation
    """
    # Sort keys and use compact JSON representation
    canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return canonical_json.encode('utf-8')


def sign_message(
    payload: Dict[str, Any], 
    private_key: Union[Ed25519PrivateKey, str],
    public_key_id: Optional[str] = None
) -> Signature:
    """
    Sign a message payload using Ed25519 digital signatures.
    
    Args:
        payload: The message data to sign
        private_key: Ed25519PrivateKey object or path to private key file
        public_key_id: Identifier for the public key (required if private_key is a path)
    
    Returns:
        Signature object with Ed25519 signature
        
    Raises:
        SigningError: If signing operation fails
    """
    try:
        # Load private key if path provided
        if isinstance(private_key, (str, Path)):
            if not public_key_id:
                raise SigningError("public_key_id is required when private_key is a file path")
            try:
                private_key_obj = load_private_key(str(private_key))
            except KeyManagementError as e:
                raise SigningError(f"Failed to load private key: {e}") from e
        else:
            private_key_obj = private_key
            if not public_key_id:
                # Generate default ID from key fingerprint
                public_key = private_key_obj.public_key()
                public_key_bytes = public_key.public_bytes_raw()
                public_key_id = hashlib.sha256(public_key_bytes).hexdigest()[:16]
        
        # Canonicalize the payload
        canonical_payload = _canonicalize_payload(payload)
        
        # Sign the canonical payload
        signature_bytes = private_key_obj.sign(canonical_payload)
        
        # Encode signature as base64 for JSON serialization
        import base64
        signature_b64 = base64.b64encode(signature_bytes).decode('ascii')
        
        # Get key fingerprint for verification
        public_key = private_key_obj.public_key()
        public_key_bytes = public_key.public_bytes_raw()
        key_fingerprint = hashlib.sha256(public_key_bytes).hexdigest()[:16]
        
        return Signature(
            algorithm="Ed25519",
            signature_data=signature_b64,
            public_key_id=public_key_id,
            timestamp=time.time(),
            key_fingerprint=key_fingerprint
        )
        
    except SigningError:
        raise  # Re-raise our own exceptions
    except Exception as e:
        raise SigningError(f"Ed25519 signing failed: {e}") from e


def verify_signature(
    payload: Dict[str, Any], 
    signature: Signature,
    public_key: Optional[Union[Ed25519PublicKey, str]] = None
) -> bool:
    """
    Verify an Ed25519 message signature.
    
    Args:
        payload: The original message data
        signature: The signature to verify
        public_key: Ed25519PublicKey object, path to public key file, or None to auto-discover
        
    Returns:
        True if signature is valid, False otherwise
        
    Raises:
        VerificationError: If verification operation fails (not invalid signature)
    """
    try:
        # Only handle Ed25519 signatures
        if signature.algorithm != "Ed25519":
            return False
        
        # Load or resolve public key
        if public_key is None:
            # Auto-discover public key based on public_key_id
            # In production, this would query a key registry
            # For now, try common key file patterns
            public_key_obj = _auto_discover_public_key(signature.public_key_id)
            if public_key_obj is None:
                raise VerificationError(f"Cannot find public key for ID: {signature.public_key_id}")
        elif isinstance(public_key, (str, Path)):
            try:
                public_key_obj = load_public_key(str(public_key))
            except KeyManagementError as e:
                raise VerificationError(f"Failed to load public key: {e}") from e
        else:
            public_key_obj = public_key
        
        # Verify key fingerprint if provided
        if signature.key_fingerprint:
            public_key_bytes = public_key_obj.public_bytes_raw()
            expected_fingerprint = hashlib.sha256(public_key_bytes).hexdigest()[:16]
            if signature.key_fingerprint != expected_fingerprint:
                return False
        
        # Canonicalize the payload (must match signing)
        canonical_payload = _canonicalize_payload(payload)
        
        # Decode signature from base64
        import base64
        try:
            signature_bytes = base64.b64decode(signature.signature_data)
        except Exception as e:
            raise VerificationError(f"Invalid base64 signature data: {e}") from e
        
        # Verify the signature
        try:
            public_key_obj.verify(signature_bytes, canonical_payload)
            return True
        except InvalidSignature:
            return False  # Invalid signature (not an error condition)
            
    except VerificationError:
        raise  # Re-raise our own exceptions
    except Exception as e:
        raise VerificationError(f"Ed25519 verification failed: {e}") from e


def _auto_discover_public_key(public_key_id: str) -> Optional[Ed25519PublicKey]:
    """
    Auto-discover public key by ID (simplified implementation).
    
    In production, this would query a proper key registry or database.
    For development, it tries common file patterns.
    
    Args:
        public_key_id: The public key identifier
        
    Returns:
        Ed25519PublicKey if found, None otherwise
    """
    # Try common key file patterns
    key_patterns = [
        f"keys/{public_key_id}.pub",
        f"keys/public/{public_key_id}.pem",
        f"/tmp/keys/{public_key_id}.pub",
        f".keys/{public_key_id}.pub"
    ]
    
    for pattern in key_patterns:
        key_path = Path(pattern)
        if key_path.exists():
            try:
                return load_public_key(str(key_path))
            except KeyManagementError:
                continue  # Try next pattern
    
    return None


def get_signing_capabilities() -> Dict[str, Any]:
    """
    Get current signing system capabilities and status.
    
    Returns:
        Dictionary describing available signing features
    """
    return {
        "algorithms_supported": ["Ed25519"],
        "production_ready": True,
        "stub_mode": False,
        "key_management": "filesystem",
        "security_level": "production",
        "features": {
            "canonical_payload": True,
            "key_fingerprints": True,
            "timestamp_metadata": True,
            "auto_discovery": True
        },
        "requirements": {
            "cryptography_library": True,
            "secure_file_permissions": True,
            "proper_randomness": True
        },
        "limitations": {
            "key_storage": "Local filesystem only (no KMS integration yet)",
            "key_discovery": "Simple file-based patterns only",
            "certificate_validation": "Not implemented"
        },
        "next_steps": [
            "Integrate with external KMS (Vault, AWS KMS)",
            "Implement proper public key registry/PKI",
            "Add certificate chain validation",
            "Add key rotation support",
            "Implement distributed key discovery"
        ]
    }


# Backward compatibility function for tests
def create_test_signature(payload: Dict[str, Any], key_id: str = "test_key") -> Signature:
    """
    Create a test signature using an ephemeral key (for testing only).
    
    Args:
        payload: The message data to sign
        key_id: Identifier for the test key
        
    Returns:
        Signature object with ephemeral Ed25519 signature
        
    Note:
        This function generates a new keypair each time and is only suitable
        for testing. Do not use in production.
    """
    from .keys import generate_keypair
    private_key, _ = generate_keypair()
    return sign_message(payload, private_key, key_id)