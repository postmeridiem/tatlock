# Hippocampus

**Status: Production Ready - Complete Memory System**

The Hippocampus module manages all forms of persistent memory for Tatlock, including databases and long-term storage. Named after the brain's hippocampus responsible for memory formation and retrieval, this module provides memory recall, storage, and retrieval functions to inform the agent's context and history. Each user has their own isolated memory database for complete privacy and data separation.

## Core Features
- **Database Management**: Per-user conversation memory, topics, and personal variables
- **Memory Functions**: Storage, recall, and retrieval of conversation data
- **Tool Integration**: Memory tools for the AI agent (see developer.md for patterns)
- **Advanced Analytics**: Memory insights, cleanup, and export capabilities

## Database Architecture
- **{username}_longterm.db**: Per-user conversation memory and topics
- **system.db**: Shared authentication, roles, groups, tools, and global system prompts
- **Short-term Storage**: User-specific temporary file storage

## Memory Tools
All memory tools follow the patterns defined in [developer.md](../developer.md):
- **Core Tools**: Personal variables, conversation management, memory recall
- **Analytics Tools**: Memory insights, cleanup, and export capabilities
- **User Isolation**: All operations scoped to current user for privacy

## Integration
- **Cortex**: Memory storage and retrieval for agent context
- **Stem**: Tool registration and user authentication
- **Occipital**: Screenshot storage in short-term memory

## Standards & Patterns
All coding, tool, and database standards are defined in [developer.md](../developer.md). Refer to it for:
- Tool implementation patterns
- Database operations and user isolation
- Error handling and logging
- Security considerations

## See Also
- [Developer Guide](../developer.md) – All standards and patterns
- [Module Docs](../README.md)
