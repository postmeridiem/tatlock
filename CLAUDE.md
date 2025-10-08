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

## Git Commit Guidelines

**CRITICAL - NEVER VIOLATE THESE RULES:**

- **NEVER** add co-authored-by messages to commits unless explicitly requested by the user
- **NEVER** add "Generated with Claude Code" or similar attribution messages
- **NEVER** add emojis to commit messages unless explicitly requested
- Write clean, professional commit messages ONLY
- Follow conventional commit format when appropriate
- Commit messages should describe WHAT changed and WHY, nothing more

**Examples of FORBIDDEN commit footers:**
```
🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

**These additions are NOT requested and violate the principle of doing exactly what was asked, nothing more.**
