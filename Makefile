all :

help :
	@echo "ApiConnectorLLM - Multi-AI Coordination System"
	@echo "=============================================="
	@echo "Quick Start (Other Qube Setup):"
	@echo "  make install    - Install Claude Code globally"
	@echo "  make start      - Start Claude Code with /init command ready"
	@echo ""
	@echo "Available Commands:" 
	@echo "  make bus        - Start BusDaemon for automated message routing"
	@echo "  make expert-llm - Test Expert LLM Manager (requires llama-cpp-python)"
	@echo ""
	@echo "After 'make start', use: /init to initialize the expert system"

install-coding-expert:
	sudo npm install -g @anthropic-ai/claude-code

start-coding-expert:
	@echo "🧠 Starting Claude Code..."
	@echo "💡 After startup, use: /init"
	@echo "   This will initialize the multi-AI expert system"
	@echo "================================================"
	claude

start : start-coding-expert

install : install-coding-expert

bus :
	(cd bus && python3 bus_daemon.py)

expert-llm:
	python3 expert_llm_manager.py

.PHONY : all help install-coding-expert start-coding-expert start install bus expert-llm

