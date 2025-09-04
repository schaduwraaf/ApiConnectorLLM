# Request to: claude_code
# Type: BUS REQUEST

## Task
Implement a **BusDaemon prototype** to automate the bus role (replacing manual cut-and-paste routing):
- Local Python process that:
  1. Watches an `inbox/` folder for new JSON messages.
  2. Validates each incoming message using the Ed25519 cryptographic functions (production signing code).
  3. Routes valid messages to the correct component via the `ZeroTrustCognitiveNetwork`.
  4. Collects the component response, re-signs it, and writes it into an `outbox/` folder as JSON.
- Must interoperate with:
  - `ComponentMessage` / `WellbeingStatus` classes in `zero_trust_cognitive_arch.py`
  - Existing crypto signing/verification code in `zero_trust_research/crypto/signing.py`

## Constraints
- Use file-based key management (already implemented, 0600 perms enforced).
- Messages must be rejected if signature verification fails.
- Provide clear log output for every message processed (success/failure, routing details).
- Keep the design incremental and reversible: a single Python script, no heavy dependencies.
- Document assumptions and next steps for evolving toward KMS + registry-backed bus.

## Success Criteria
- Running `python bus_daemon.py` starts the BusDaemon.
- Messages dropped into `inbox/` are automatically picked up, verified, routed, and produce signed outputs in `outbox/`.
- Invalid messages (bad sig, unknown sender, missing fields) are rejected with a clear error report in `outbox/`.
- Demo test: guardian → autistic verifier message flows through bus and produces integrity report.

## Deliverables
- `bus/bus_daemon.py` (main process loop + folder watcher)
- `bus/tests/test_bus_daemon.py` (end-to-end test: inbox → outbox flow)
- Update to `CRYPTO_DOCUMENTATION.md` describing bus security assumptions
- Example messages in `bus/examples/` (valid + invalid)

## Priority
Normal – this is the next evolutionary step: moving the human bus role into a coded bus.

## Notes
- This is explicitly a **bus request**: goal is to prototype automation of the coordinator role.
- Keep design simple and extensible: future integration with registry + KMS expected.

