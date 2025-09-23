# Cortex

**Status: Production Ready - Core Agent Logic**

The Cortex module contains the core agent logic for Tatlock, orchestrating all subsystems and exposing the FastAPI interface for chat interactions.

## Core Features

- Agentic loop with tool dispatch and execution
- LLM integration (Ollama) with context management
- Topic classification and conversation tracking
- Memory persistence to user-specific databases
- Session-based authentication integration

## Process Flow

1. Load base instructions from user's database
2. Build conversation context with history
3. Send to LLM with available tools
4. Execute requested tools with user context
5. Continue loop until final response (max 5 iterations)
6. Classify topic and save to memory
7. Return response with updated history

## Integration

- **Stem**: Authentication, tools, and utilities
- **Hippocampus**: Memory storage and retrieval
- **Cerebellum**: External API tools (web search, weather)
- **Occipital**: Visual processing tools
- **Main.py**: API endpoint exposure

## Standards & Patterns

All coding, tool, and security standards are defined in [AGENTS.md](../AGENTS.md). Refer to it for:

- Tool integration patterns
- Error handling and logging
- User context management
- Database operations

## See Also

- [Developer Guide](../AGENTS.md) – All standards and patterns
- [Module Docs](../README.md)
