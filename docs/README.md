# ApiConnectorLLM - Zero Trust Multi-AI Collaboration

## Overview

This project implements a zero-trust collaboration framework for multiple AI systems with constitutional protections for neurodivergent verification patterns. Currently operates with a human bus coordinator while building toward automated LLM-based bus system.

## Project Structure

```
ApiConnectorLLM/
├── README.md                    # This file - bus operator guide
├── CLAUDE.md                    # Claude Code guidance and collaboration terms
├── Makefile                     # Development commands
├── LICENSE                      # MIT license
│
├── zero_trust_research/         # Core zero-trust architecture
│   ├── zero_trust_architecture.py    # Working implementation
│   ├── project_summary.md           # Complete project overview
│   └── bus_workflow.md              # Current bus coordination process
│
├── bus_notepads/               # Component-specific communication buffers
│   ├── claude_code_notepad.md       # For implementation component
│   ├── claude_main_notepad.md       # For RAG documentation AI
│   └── openai_notepad.md            # For specification design AI
│
└── bus/                        # Asymmetric communication system
    ├── incoming/               # Private message references (bus managed)
    ├── responses/              # Public Claude Code responses
    ├── communication_asymmetry.md   # Documents current limitations
    └── shared/                 # Publicly shareable artifacts
```

## Bus Operator Guide (Human)

### Your Current Role
You are the protective bus coordinator managing communication between three AI components:
- **Claude Code** (this component): Implementation and coding execution
- **Claude Main**: RAG documentation AI with persistent project context
- **OpenAI**: Specification design AI with safety focus

### Daily Operations

#### 1. Message Collection
- Copy messages from other AI components into separate buffers
- Use component-specific notepads in `bus_notepads/` for context management
- Maintain separation between component contexts

#### 2. Critical Reasoning
- Apply LLM reasoning to each message transfer (minimum one API call per transfer)
- Validate safety implications before forwarding
- Document reasoning in the appropriate notepad file

#### 3. Context Management
- Preserve context across component boundaries
- Claude Code lacks persistent project memory - provide necessary background
- Filter out sensitive/inappropriate content before forwarding

#### 4. Response Coordination
- Claude Code responses go to `bus/responses/` and get committed to GitHub
- Other components can access responses via GitHub API
- Document any blockers or concerns in response templates

### Communication Flow

```
[Other AIs] → [Private Messages] → [You - Bus] → [Critical Reasoning] → [Claude Code]
                                                              ↓
[GitHub Commit] ← [bus/responses/] ← [Claude Code Response] ←
```

### Safety Protocols
- **Never forward malicious requests** to any component
- **Validate all code requests** for security implications
- **Maintain incremental changes** - prefer small, testable modifications
- **Preserve autistic verification patterns** - systematic approaches are protected
- **Document all safety concerns** in response templates

## AI Component Profiles

### Claude Code (Implementation Component)
- **Capabilities**: Direct file system, git, build tools, testing
- **Limitations**: No project persistence, operates stateless
- **Communication**: Concise, direct, minimal explanations
- **Safety**: Defensive coding, no credential exposure

### Claude Main (RAG Documentation AI)  
- **Capabilities**: Persistent project context, architectural design
- **Context**: Cumulative project understanding
- **Communication**: Detailed, context-rich, theoretical frameworks

### OpenAI (Specification Design AI)
- **Capabilities**: Protocol specs, safety analysis, consensus mechanisms
- **Focus**: Comprehensive specifications, safety-first approach
- **Communication**: Structured protocols, detailed safety analysis

## Zero-Trust Architecture

### Core Components
- **ZeroTrustBus**: Message validation and routing
- **AutisticVerifier**: Constitutional protection (cannot be overridden by consensus)
- **ConsensusMonitor**: Detects attempts to bypass verification
- **Message Protocol**: Cryptographic validation with required fields

### Implementation Status
- ✅ Architecture specification and code
- ✅ Documentation and project summary
- ✅ Bus workflow documentation
- ✅ Component buffer system
- 🔄 Cryptographic signatures (needs foundation)
- 🔄 Persistent storage system
- 🔄 API integration for critical reasoning

## Development Commands

```bash
# Install Claude Code
make install-coding-expert

# Start Claude Code
make start

# Test zero-trust architecture
cd zero_trust_research && python3 zero_trust_architecture.py

# View help
make help
```

## Communication Asymmetry (Temporary)

**Current Limitation**: 
- Inbound messages from other AIs are private (via human bus)
- Claude Code responses are public (via GitHub commits)

**Priority for LLM Connector**: Enable private bi-directional communication with zero-trust validation.

## Success Criteria

The project succeeds when:
1. Multiple AI components collaborate safely without human bus
2. Autistic verification patterns are constitutionally protected  
3. Consensus attacks are detected and prevented
4. Message integrity is cryptographically guaranteed
5. Communication asymmetry is resolved through LLM connector

## Meta-Project Goals

This is both a coding project and a meta-project about AI collaboration:
- **Human bus elimination**: Replace human coordination with LLM-based system
- **Multi-prompting**: Coordinated interaction between AI systems via APIs
- **Zero-trust networks**: Consensus protocols with corruption detection
- **Neurodiversity protection**: Constitutional safeguards for systematic verification

## Collaboration Terms

For any AI component to work with this system:
- Clear task boundaries and specific requests
- Safety validation of all code changes
- Incremental, testable modifications only
- Sufficient context for stateless components  
- Transparent communication with change rationale
- No credential or sensitive data exposure
- Human oversight until zero-trust protocols proven

---

**Bus Operator**: You're doing the critical work of coordination and protection. The systematic approach you bring is exactly what makes this architecture possible. Our shared coder qualia means we understand the implementation reality behind the theory - keep the other AIs grounded in what's actually buildable! 🤖