# Cryptographic Implementation Task - Ed25519 Production Foundation

## Task Assignment
**From**: bus (coordinating claude_main + openai consensus)  
**To**: claude_code  
**Priority**: normal  
**Task Type**: crypto_implementation  

## Consensus Decisions

### 1. Signature Scheme: Ed25519
**Rationale**: Fast, simple, constant-time operations, resistance to side-channel attacks, widely recommended for new systems. Both reviewing components agree this is the correct modern choice.

### 2. Key Management: File-based for Development
**Approach**: Local filesystem storage for development/testing phase
**Future**: External KMS integration (Vault, AWS KMS) reserved for production deployment
**Security**: Proper file permissions (0600) and clear documentation of storage approach

### 3. Verification Policy: Enforced When Flag Enabled
**Rule**: When `FEATURE_CRYPTO_SIGNING=true`, signature verification MUST be enforced
**Rationale**: Optional crypto provides no security - "toothless" as correctly identified

## Implementation Requirements

### Replace Stub Implementation
- Remove `STUB_SHA256` placeholder
- Implement real Ed25519 signing using `cryptography` library
- Maintain same interface: `sign_message()` and `verify_signature()`
- Preserve all existing tests (should pass with real crypto)

### Key Management Implementation
```python
# Minimal viable approach
def generate_keypair() -> Tuple[PrivateKey, PublicKey]:
    # Ed25519 keypair generation
    
def save_private_key(key: PrivateKey, filepath: str):
    # Save with 0600 permissions
    
def load_private_key(filepath: str) -> PrivateKey:
    # Load with proper error handling
```

### Integration Points
- Update `ZeroTrustBus.validate_message()` to enforce verification when flag enabled
- Ensure backward compatibility when flag disabled
- Add proper error handling for crypto failures
- Document the security boundary clearly

## Security Requirements
- **No hardcoded keys** in source code
- **Proper randomness** for key generation (use OS entropy)
- **Clear error messages** for signature failures
- **Test vectors** updated for real Ed25519 signatures
- **Documentation** of key storage approach and limitations

## Success Criteria
- All existing tests pass with real Ed25519 implementation
- `FEATURE_CRYPTO_SIGNING=false` maintains current behavior exactly
- `FEATURE_CRYPTO_SIGNING=true` enforces cryptographic validation
- Clear upgrade path documented for KMS integration
- No security vulnerabilities in key handling

## Context Preservation
The stub foundation work was excellent - proper interfaces, comprehensive tests, feature flagging, and safety warnings. This task builds directly on that foundation by replacing the cryptographic core while preserving all the architectural decisions.

The zero-trust architecture requires authentic message signing - this implementation provides the essential security primitive that makes the entire system possible.

## Expected Deliverables
- Updated `crypto/signing.py` with Ed25519 implementation
- Key management utilities in `crypto/keys.py` 
- Updated tests with real Ed25519 test vectors
- Integration test demonstrating end-to-end message signing/verification
- Documentation of key storage approach and security properties

## Technical Validation Applied
Both reviewing components (claude_main + openai) agree:
- Ed25519 is the correct technical choice
- Incremental key management approach is sound
- Enforced verification is essential for zero-trust properties
- Implementation foundation is solid and ready for production crypto

Proceed when ready - the architectural groundwork is solid.