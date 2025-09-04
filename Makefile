all :

help :
	@grep PHONY Makefile | grep -v grep

install-coding-expert:
	sudo npm install -g @anthropic-ai/claude-code

start-coding-expert:
	claude

start : start-coding-expert

install : install-coding-expert

.PHONY : all help install-coding-expert start-coding-expert start install

