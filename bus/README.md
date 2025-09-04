# BusDaemon - Automated Zero-Trust Message Coordination

The BusDaemon automates the role of the human bus coordinator by providing automated, cryptographically-verified message processing and routing between AI components.

## Quick Start

```bash
# Start the daemon (watches inbox/ for messages)
python3 bus_daemon.py

# Show daemon status
python3 bus_daemon.py --status

# Run tests
python3 -m unittest tests.test_bus_daemon -v
```

## How It Works

1. **Drop messages** into `bus/inbox/` as JSON files
2. **Daemon processes** each message automatically
3. **Responses appear** in `bus/outbox/` (signed by daemon)
4. **Errors are logged** with detailed failure reports
5. **Original messages** are archived to `bus/archive/`

## Message Format

Messages use the `ComponentMessage` format:

```json
{
  "message_id": "unique_id",
  "sender_id": "component_name",
  "receiver_id": "target_component",
  "message_type": "execute|verification_request|plan|etc",
  "payload": {
    "content_reference": "what_to_do",
    "additional_fields": "as_needed"
  },
  "timestamp": 1693737600.0,
  "nonce": "unique_nonce",
  "signature": null | {Ed25519_signature_object}
}
```

## Security Features

- **Ed25519 signature verification** when signatures present
- **Constitutional autistic verifier protection** (cannot be bypassed)
- **Timestamp validation** (5-minute window for message freshness)
- **Message structure validation** (prevents malformed input)
- **Comprehensive audit logging** (all actions logged to bus_daemon.log)

## Directory Structure

```
bus/
├── bus_daemon.py           # Main daemon process
├── inbox/                  # Drop messages here
├── outbox/                 # Responses appear here  
├── archive/               # Processed messages
├── keys/                  # Daemon signing keys (0600 perms)
├── examples/              # Sample messages for testing
├── tests/                 # Unit and integration tests
└── bus_daemon.log         # Detailed processing log
```

## Example Usage

### 1. Basic Message

Create `bus/inbox/test_message.json`:
```json
{
  "message_id": "test_001",
  "sender_id": "claude_main",
  "receiver_id": "claude_code", 
  "message_type": "execute",
  "payload": {
    "content_reference": "implement_new_feature",
    "description": "Please implement the requested feature",
    "priority": "normal"
  },
  "timestamp": 1693737600.0,
  "nonce": "test_nonce_001",
  "signature": null
}
```

### 2. Check Results

After daemon processes the message:
- **Success**: `bus/outbox/test_001_response.json` (signed response)
- **Failure**: `bus/outbox/test_001_error.json` (detailed error)
- **Archive**: `bus/archive/test_message.json` (original moved)

### 3. Monitor Logs

```bash
tail -f bus_daemon.log
```

## Error Handling

The daemon handles several error types:

### Structure Errors
- **Missing required fields** (receiver_id, nonce, etc.)
- **Invalid JSON format**
- **Malformed ComponentMessage**

### Cryptographic Errors  
- **Invalid Ed25519 signatures**
- **Missing public keys for verification**
- **Signature format errors**

### Routing Errors
- **Timestamp outside 5-minute window** 
- **Autistic verifier violations**
- **Unknown component IDs**

All errors produce detailed responses in `outbox/` with:
- Error type and description
- Original message ID
- Verification status details
- Timestamp of failure

## Testing

### Run All Tests
```bash
python3 -m unittest tests.test_bus_daemon -v
```

### Test With Examples
```bash
# Copy example messages to inbox
cp examples/valid_guardian_message.json inbox/
cp examples/invalid_bad_signature.json inbox/

# Start daemon to process them
python3 bus_daemon.py
```

### Manual Testing
```bash
# Process a single message manually
python3 -c "
from bus_daemon import BusDaemon
daemon = BusDaemon()
result = daemon.process_message('inbox/test_message.json')
print(f'Result: {result.status}')
"
```

## Integration with Zero-Trust Architecture

The BusDaemon integrates directly with the zero-trust research components:

- **Zero-Trust Bus**: Routes messages through `ZeroTrustBus.route_message()`
- **Autistic Verifier**: Enforces constitutional protections
- **Ed25519 Crypto**: Validates signatures using production crypto system
- **Message Types**: Supports all `MessageType` values from architecture

## Security Model

### Filesystem Security
- Bus directories should have appropriate permissions
- Daemon keys stored with 0600 permissions  
- Process isolation (one daemon per directory)

### Cryptographic Security
- Ed25519 signatures validated when present
- Key fingerprint verification prevents key substitution
- Nonce uniqueness prevents replay attacks
- Timestamp validation prevents stale message processing

### Constitutional Security
- Autistic verifier violations cannot be bypassed
- All verification failures are permanently logged
- Consensus attacks are detected and reported
- Pattern consistency is enforced

## Future Enhancements

- **Real-time monitoring** dashboard
- **Component health** tracking and reporting
- **Message queue** persistence and replay
- **Distributed deployment** with multiple daemons
- **Web API** for remote message submission
- **Integration** with external message brokers

## Troubleshooting

### Daemon Won't Start
- Check directory permissions
- Verify Ed25519 crypto library available
- Check for existing daemon processes

### Messages Not Processed
- Verify JSON format validity
- Check message has all required fields
- Ensure timestamp is recent (within 5 minutes)
- Review `bus_daemon.log` for detailed errors

### Signature Verification Fails
- Confirm signature was created with matching private key
- Verify public key is discoverable by daemon
- Check signature algorithm is "Ed25519"
- Ensure payload exactly matches signed content

---

**Status**: Production Ready  
**Security Level**: High  
**Last Updated**: 2025-09-04