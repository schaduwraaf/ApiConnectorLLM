# Bus Daemon Example Messages

This directory contains example JSON messages for testing the BusDaemon functionality.

## Valid Messages

### `valid_guardian_message.json`
- **Purpose**: Guardian component requesting verification from autistic verifier
- **Expected Result**: Should be routed successfully (no signature required for unsigned messages in current implementation)
- **Usage**: Demonstrates basic message routing flow

### `claude_main_to_code.json` 
- **Purpose**: Claude Main component sending implementation request to Claude Code
- **Expected Result**: Should be routed successfully
- **Usage**: Demonstrates inter-component communication

## Invalid Messages

### `invalid_bad_signature.json`
- **Purpose**: Message with fake/invalid Ed25519 signature
- **Expected Result**: Should be rejected with signature verification failure
- **Usage**: Demonstrates cryptographic validation

### `invalid_missing_fields.json`
- **Purpose**: Message missing required fields (receiver_id, nonce)
- **Expected Result**: Should be rejected with validation error
- **Usage**: Demonstrates message structure validation

## Testing the Examples

Copy any example message to the `bus/inbox/` directory to test:

```bash
# Test valid message
cp bus/examples/valid_guardian_message.json bus/inbox/

# Test invalid signature
cp bus/examples/invalid_bad_signature.json bus/inbox/

# Test missing fields  
cp bus/examples/invalid_missing_fields.json bus/inbox/
```

Check `bus/outbox/` for processing results and `bus_daemon.log` for detailed logging.

## Message Format

All messages follow the ComponentMessage format:

```json
{
  "message_id": "unique_identifier",
  "sender_id": "component_name", 
  "receiver_id": "target_component",
  "message_type": "message_type_string",
  "payload": {
    "content_reference": "reference_string",
    ...additional_payload_fields
  },
  "timestamp": 1693737600.0,
  "nonce": "unique_nonce_string",
  "signature": {
    "algorithm": "Ed25519",
    "signature_data": "base64_encoded_signature",
    "public_key_id": "signer_key_id",
    "timestamp": 1693737600.0,
    "key_fingerprint": "optional_fingerprint"
  }
}
```

- `signature` field is optional for unsigned messages
- When present, signature must be valid Ed25519 signature
- All other fields are required