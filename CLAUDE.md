# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses a Makefile for common development tasks:

- `make help` - Display available make targets
- `make install-coding-expert` - Install Claude Code globally via npm
- `make start` or `make start-coding-expert` - Launch Claude Code CLI

## Project Overview

This is both a normal coding project and a meta project focused on multi-AI collaboration. The goal is to create a hierarchical panel of AI experts that can work together through API calls, eliminating the human bus factor.

### Key Concepts:
- **Multi-prompting**: Coordinated interaction between multiple AI systems
- **Human bus elimination**: Replace human coordination with LLM-based bus system
- **Zero-trust network**: Implement consensus protocols with corruption detection
- **API connector**: Enable direct communication between AI systems via API calls

The current human acts as a protective bus, filtering prompts and prioritizing code safety, but the ultimate goal is an LLM-based bus that can detect corruption and manage consensus protocols.

### Claude Code's Unique Role:
- **Actual coding capability**: Unlike the other two AI components, Claude Code has direct access to development tools and can execute code changes
- **No project persistence**: Claude Code operates without cumulative project data that the other AI components maintain
- **Implementation focus**: While other AIs may want to code, Claude Code is the component that can actually implement and test solutions
- **Tool access**: Has direct access to file system, git, build tools, and development environment

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

This repository contains:

- Basic Makefile with Claude Code installation and startup commands
- LICENSE file
- README.md with initialization message
- CLAUDE.md (this file) with project context

The repository is in its initial state. Future development will involve building API connector functionality to enable secure, direct communication between AI systems.