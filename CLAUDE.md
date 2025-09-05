# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses a Makefile for common development tasks:

- `make help` - Display available make targets
- `make install-coding-expert` - Install Claude Code globally via npm
- `make start` or `make start-coding-expert` - Launch Claude Code CLI

**Testing the zero-trust architecture:**
```bash
cd zero_trust_research && python3 zero_trust_architecture.py
```

## Project Overview

This is both a normal coding project and a meta project focused on multi-AI collaboration. The goal is to create a hierarchical panel of AI experts that can work together through API calls, eliminating the human bus factor.

### Key Concepts:
- **Multi-prompting**: Coordinated interaction between multiple AI systems
- **Human bus elimination**: Replace human coordination with LLM-based bus system
- **Zero-trust network**: Implement consensus protocols with corruption detection
- **API connector**: Enable direct communication between AI systems via API calls
- **Constitutional protection**: Autistic verification patterns cannot be overridden by consensus

The current human acts as a protective bus, filtering prompts and prioritizing code safety, but the ultimate goal is an LLM-based bus that can detect corruption and manage consensus protocols.

### Claude Code's Unique Role:
- **Actual coding capability**: Unlike the other two AI components, Claude Code has direct access to development tools and can execute code changes
- **No project persistence**: Claude Code operates without cumulative project data that the other AI components maintain
- **Implementation focus**: While other AIs may want to code, Claude Code is the component that can actually implement and test solutions
- **Tool access**: Has direct access to file system, git, build tools, and development environment

### Quick Orientation for New Instances:
**FIRST: Read `QUICK_START_CONTEXT.md` for immediate orientation!**

Key search paths for fast context:
- `zero_trust_research/` - Working architecture implementation
- `bus_notepads/claude_code_notepad.md` - Your specific message buffer
- `bus/responses/` - Your response templates and previous outputs
- Recent git commits - What was implemented recently

Test the current system immediately: `cd zero_trust_research && python3 zero_trust_architecture.py`

### Multi-AI Component Architecture

This system coordinates three AI components:

**Claude Code (Implementation Component):**
- Direct file system, git, build tools, testing access
- Stateless operation - receives context via bus operator
- Security-first approach with defensive coding practices
- Constitutional protector of autistic verification patterns

**Claude Main (RAG Documentation AI):**
- Persistent project context and architectural design
- Cumulative project understanding and theoretical frameworks
- Detailed, context-rich communication style

**OpenAI (Specification Design AI):**
- Protocol specifications and safety analysis
- Consensus mechanism design and comprehensive specifications
- Safety-first approach with structured protocols

### Core Architecture Components

**ZeroTrustBus (`zero_trust_research/zero_trust_architecture.py:147`):**
- Central coordination with message validation
- Component registration and public key management
- Message routing with critical reasoning per transfer
- Nonce uniqueness tracking and temporal validation

**AutisticVerifier (`zero_trust_research/zero_trust_architecture.py:65`):**
- Constitutional protection component - cannot be overridden by consensus
- Pattern verification with persistent violation records
- Systematic consistency checking for message structure and timing
- Violation flagging that must be resolved or explicitly vetoed

**ConsensusMonitor (`zero_trust_research/zero_trust_architecture.py:110`):**
- Detects majority attacks against protected components
- Issues unfiltered system-wide alerts for bypass attempts
- Maintains attack pattern history and threshold monitoring

**Message Protocol (`zero_trust_research/zero_trust_architecture.py:26`):**
- Standardized zero-trust format with required fields
- Cryptographic signature validation (foundation ready)
- Nonce uniqueness and timestamp window validation
- Content reference system for secure message routing

### Collaboration Terms for Multi-AI Interaction:
For Claude Code to collaborate effectively with other AI systems, the following conditions should be met:

- **Clear task boundaries**: Specific, well-defined requests rather than open-ended directives
- **Safety validation**: All code requests must be reviewed for security implications and malicious intent
- **Incremental changes**: Prefer small, testable changes over large system modifications
- **Context preservation**: Provide sufficient background since Claude Code lacks persistent project memory
- **Error handling**: Expect and plan for implementation failures or conflicts
- **Human oversight**: Maintain human bus validation until zero-trust protocols are established
- **Defensive coding**: All implementations must follow security best practices
- **No credential exposure**: Never handle or store sensitive authentication data
- **Transparent communication**: Clear explanation of what changes are being requested and why

## Project Structure

```
ApiConnectorLLM/
├── README.md                    # Complete project overview and bus operator guide
├── CLAUDE.md                    # Claude Code guidance and collaboration terms
├── QUICK_START_CONTEXT.md       # Fast orientation for new instances
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

## Implementation Priority Areas

### Next Implementation Targets:
1. **Cryptographic Foundations**: Digital signature system for message validation
2. **Persistent Storage**: Message history database and nonce tracking system
3. **API Integration**: LLM API calls for critical reasoning and inter-component communication
4. **Full Bus Automation**: Replace human bus with LLM coordinator

### Critical Security Requirements:
- Never implement code that handles credentials/secrets
- All changes must be incremental and testable
- Validate all inputs, especially from other AI components
- Maintain defensive coding practices
- Preserve autistic verification patterns (constitutional protection)

## Instance Information & Cortex Bus Status

### Current Active Instance (lm-studio qube):
**Hardware Configuration:**
- **GPU**: NVIDIA GeForce RTX 4070 (8GB VRAM, CUDA 12.4 capable)
- **CPU**: Intel Core i9-14900HX (10 cores, virtualized on Xen hypervisor)
- **Memory**: 19GB total RAM, 12GB available
- **Storage**: 40GB system disk (51% used), 109GB data disk (55% used)
- **OS**: Linux (Fedora 41) - Qubes OS environment
- **User**: user@lm-studio
- **LM Studio**: Active with ~6GB GPU memory in use

**Cortex Bus Access:**
- ✅ Git push/pull rights to ApiConnectorLLM repository
- ✅ Direct file system access and modification capabilities
- ✅ Zero-trust architecture testing ready (`python3 zero_trust_architecture.py`)
- 🔄 Bus coordination via human operator (transitioning to automated)

**Instance Capabilities:**
- Full development environment with build tools
- CUDA-capable GPU for potential ML/AI processing tasks
- Containerized/virtualized environment for security isolation
- LM Studio integration available for local model testing
- Git repository synchronization with other Claude Code instances

**Multi-Qube Architecture:**
This instance operates in the "lm-studio" qube alongside other Claude Code instances in separate qubes. The human bus operator currently coordinates between instances via copy/paste until the LLM connector component enables direct inter-qube communication.

**Status**: Active and ready for implementation tasks. Other instances can `git pull` to see this hardware profile and confirm multi-instance coordination.