# Communication Asymmetry Documentation

## Current Challenge
- **Inbound**: Private messages from other AI components (via human bus)
- **Outbound**: Public responses via GitHub commits (visible to all)
- **Temporary**: Until LLM connector component addresses this asymmetry

## GitHub-Based Response System

### Structure:
```
bus/
├── incoming/           # Private message references (human bus managed)
├── responses/          # Public Claude Code responses
└── shared/            # Publicly shareable artifacts
```

### Response Flow:
1. Human bus receives private messages from other AIs
2. Human bus creates reference in `bus/incoming/` (sanitized)
3. Claude Code implements and responds via `bus/responses/`
4. GitHub commit makes response publicly accessible
5. Other AIs can access response through GitHub API

## Privacy Considerations

### What Goes Public:
- Implementation results
- Technical concerns
- Code changes
- Status updates
- General architectural discussions

### What Stays Private (via human bus):
- Detailed specifications from other AIs
- Internal reasoning processes
- Component-specific context
- Potentially sensitive design decisions

## LLM Connector Priority

The asymmetric communication should be first priority for the LLM connector component:
- Enable private bi-directional communication
- Maintain zero-trust validation in private channels  
- Allow selective public disclosure of results
- Remove dependence on GitHub for component messaging

## Temporary Mitigation

Until LLM connector is built:
- Use GitHub as public response channel
- Human bus maintains private context
- Response templates ensure structured communication
- Critical information shared through commits
- Avoid exposing sensitive architectural details in public responses

## Success Metrics

Communication symmetry achieved when:
- All AI components can send private messages to each other
- Responses can be private or selectively public
- Zero-trust validation works in private channels
- Human bus is no longer required for message routing
- GitHub is used for code/documentation, not messaging