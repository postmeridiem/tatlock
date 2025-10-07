# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT**: The `AGENTS.md` file contains the authoritative instruction set for all developers and LLMs working on this project. Please refer to `AGENTS.md` for:

- Complete project architecture and design patterns
- Development workflows and best practices
- Testing strategies and debugging techniques
- Module-specific implementation details
- Performance optimization guidelines
- Security considerations
- All other development guidance

Any conflicting guidance between this file and `AGENTS.md` should defer to `AGENTS.md`, which supersedes all other instruction files.

## Quick Reference

**Project**: Tatlock - Brain-inspired conversational AI platform with authentication, security, and persistent memory

**Key Commands**:
- Start application: `./wakeup.sh`
- Install/setup: `./install_tatlock.sh`
- Run tests: `python -m pytest tests/`
- Activate venv: `source .venv/bin/activate`

**Architecture**: Brain-inspired modules (cortex, hippocampus, stem, parietal, occipital, cerebellum, temporal)

**Documentation**:
- **Developer Guide**: See `AGENTS.md` for comprehensive developer guidance
- **Memory & Prompt System**: See `hippocampus/MEMORY_SYSTEM.md` for conversation, memory, and prompt architecture
