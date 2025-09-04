#!/usr/bin/env python3
"""
Ed25519 Key Management for Zero-Trust Message Validation.

This module provides secure Ed25519 key generation, storage, and loading
with proper file permissions and error handling.
"""

import os
import stat
from pathlib import Path
from typing import Tuple, Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


class KeyManagementError(Exception):
    """Raised when key management operations fail."""
    pass


def generate_keypair() -> Tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """
    Generate a new Ed25519 keypair using secure OS entropy.
    
    Returns:
        Tuple of (private_key, public_key)
        
    Raises:
        KeyManagementError: If key generation fails
    """
    try:
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return private_key, public_key
    except Exception as e:
        raise KeyManagementError(f"Failed to generate Ed25519 keypair: {e}") from e


def save_private_key(private_key: Ed25519PrivateKey, filepath: str, password: Optional[bytes] = None) -> None:
    """
    Save Ed25519 private key to filesystem with secure permissions (0600).
    
    Args:
        private_key: The Ed25519 private key to save
        filepath: Path where to save the key
        password: Optional password to encrypt the key (None = no encryption)
        
    Raises:
        KeyManagementError: If save operation fails
    """
    try:
        # Determine encryption algorithm
        if password is not None:
            encryption_algorithm = serialization.BestAvailableEncryption(password)
        else:
            encryption_algorithm = serialization.NoEncryption()
        
        # Serialize private key
        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )
        
        # Create directory if it doesn't exist
        key_path = Path(filepath)
        key_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write key file with secure permissions
        with open(filepath, 'wb') as f:
            f.write(private_key_bytes)
        
        # Set restrictive permissions (owner read/write only)
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 0600
        
    except Exception as e:
        raise KeyManagementError(f"Failed to save private key to {filepath}: {e}") from e


def load_private_key(filepath: str, password: Optional[bytes] = None) -> Ed25519PrivateKey:
    """
    Load Ed25519 private key from filesystem with proper validation.
    
    Args:
        filepath: Path to the private key file
        password: Optional password to decrypt the key
        
    Returns:
        The loaded Ed25519 private key
        
    Raises:
        KeyManagementError: If load operation fails or file permissions are unsafe
    """
    try:
        key_path = Path(filepath)
        
        # Check if file exists
        if not key_path.exists():
            raise KeyManagementError(f"Private key file not found: {filepath}")
        
        # Check file permissions for security
        file_stat = key_path.stat()
        if file_stat.st_mode & (stat.S_IRGRP | stat.S_IROTH):
            raise KeyManagementError(
                f"Private key file {filepath} has unsafe permissions. "
                f"Expected 0600, got {oct(file_stat.st_mode)[-3:]}"
            )
        
        # Read and load the key
        with open(filepath, 'rb') as f:
            private_key_bytes = f.read()
        
        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=password
        )
        
        # Verify it's an Ed25519 key
        if not isinstance(private_key, Ed25519PrivateKey):
            raise KeyManagementError(f"Key file {filepath} is not an Ed25519 private key")
        
        return private_key
        
    except KeyManagementError:
        raise  # Re-raise our own exceptions
    except Exception as e:
        raise KeyManagementError(f"Failed to load private key from {filepath}: {e}") from e


def save_public_key(public_key: Ed25519PublicKey, filepath: str) -> None:
    """
    Save Ed25519 public key to filesystem.
    
    Args:
        public_key: The Ed25519 public key to save
        filepath: Path where to save the key
        
    Raises:
        KeyManagementError: If save operation fails
    """
    try:
        # Serialize public key
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        # Create directory if it doesn't exist
        key_path = Path(filepath)
        key_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write key file
        with open(filepath, 'wb') as f:
            f.write(public_key_bytes)
            
        # Set readable permissions for public key
        os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)  # 0644
        
    except Exception as e:
        raise KeyManagementError(f"Failed to save public key to {filepath}: {e}") from e


def load_public_key(filepath: str) -> Ed25519PublicKey:
    """
    Load Ed25519 public key from filesystem.
    
    Args:
        filepath: Path to the public key file
        
    Returns:
        The loaded Ed25519 public key
        
    Raises:
        KeyManagementError: If load operation fails
    """
    try:
        key_path = Path(filepath)
        
        # Check if file exists
        if not key_path.exists():
            raise KeyManagementError(f"Public key file not found: {filepath}")
        
        # Read and load the key
        with open(filepath, 'rb') as f:
            public_key_bytes = f.read()
        
        public_key = serialization.load_pem_public_key(public_key_bytes)
        
        # Verify it's an Ed25519 key
        if not isinstance(public_key, Ed25519PublicKey):
            raise KeyManagementError(f"Key file {filepath} is not an Ed25519 public key")
        
        return public_key
        
    except KeyManagementError:
        raise  # Re-raise our own exceptions
    except Exception as e:
        raise KeyManagementError(f"Failed to load public key from {filepath}: {e}") from e


def get_key_info(private_key: Ed25519PrivateKey) -> dict:
    """
    Get information about an Ed25519 private key.
    
    Args:
        private_key: The Ed25519 private key
        
    Returns:
        Dictionary with key information
    """
    public_key = private_key.public_key()
    
    # Get key fingerprint (SHA256 of public key bytes)
    import hashlib
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    fingerprint = hashlib.sha256(public_key_bytes).hexdigest()[:16]
    
    return {
        "algorithm": "Ed25519",
        "key_size": 256,  # Ed25519 uses 256-bit keys
        "fingerprint": fingerprint,
        "public_key_size": len(public_key_bytes),
        "curve": "Curve25519"
    }