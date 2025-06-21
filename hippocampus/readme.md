# hippocampus

This module manages all forms of persistent memory for Tatlock, including databases and long-term storage. It provides memory recall, storage, and retrieval functions to inform the agent's context and history, along with comprehensive user authentication and management.

## Core Components

### Database Management
- **longterm.db**: Stores conversations, topics, and system prompts
- **system.db**: Stores user authentication, roles, and groups

### Memory Functions

#### `database.py`
- **`get_base_instructions()`**: Retrieves enabled system prompts from `rise_and_shine` table
- **`query_personal_variables()`**: Looks up personal information by key
- **Database Connection Management**: Handles connections to both longterm and system databases

#### `remember.py`
- **`save_interaction()`**: Saves full conversation interactions with topics
- **`get_or_create_topic()`**: Manages topic creation and linking
- **User-Specific Storage**: Associates memories with specific users

#### `recall.py`
- **`recall_memories()`**: Search memories by keyword in prompts, replies, or topics
- **`recall_memories_with_time()`**: Search with temporal filtering (date ranges)
- **User-Specific Recall**: Filters memories by user for privacy and relevance

#### `dbutils.py`
- **`_execute_query()`**: Generic database query helper with error handling
- **Multi-Database Support**: Works with both longterm.db and system.db

## Database Schema

### longterm.db Tables
- **memories**: Stores conversation interactions with timestamps and user_id
- **topics**: Topic classification for conversations
- **memory_topics**: Links memories to topics
- **rise_and_shine**: System prompts and instructions for the LLM

### system.db Tables
- **users**: User accounts with hashed passwords, salts, and profile information
- **roles**: Available roles (user, admin, moderator)
- **groups**: Available groups (users, admins, moderators)
- **user_roles**: Links users to roles
- **user_groups**: Links users to groups

## System Prompts

**Important**: All future system prompts (base instructions) for the LLM should be stored as records in the `rise_and_shine` table, except for the current date, which is injected dynamically.

The `rise_and_shine` table contains:
- Tatlock's personality and behavior instructions
- Tool usage guidelines
- Silent tool execution directive
- Improvement suggestion instructions

## Memory Recall Features

- **Keyword Search**: Search across user prompts, AI replies, and topic names
- **Temporal Filtering**: Filter by date ranges ("yesterday", "last week", etc.)
- **Topic Classification**: Automatic topic assignment and retrieval
- **Full Context**: Access to complete conversation history including tool calls
- **User Isolation**: Each user's memories are isolated and private

## Security & Privacy

- **Password Hashing**: PBKDF2 with unique salts per user
- **Role-Based Access**: User roles and group management
- **Database Isolation**: Separate databases for memory and authentication
- **User Data Privacy**: Memories are associated with specific users
- **Input Validation**: All database operations use parameterized queries

## Integration with Authentication

- **User Context**: Memory operations respect user authentication
- **Personal Information**: Tools can access user-specific data through the authentication system
- **Memory Isolation**: Each user's conversations are stored and retrieved separately
- **Role-Based Access**: Memory access can be controlled by user roles

## Installation Support

The module includes database setup utilities in `stem/installation/database_setup.py`:
- **`create_system_db_tables()`**: Creates authentication database schema
- **`create_longterm_db_tables()`**: Creates memory database schema
- **`create_default_roles()`**: Sets up default user roles
- **`create_default_groups()`**: Sets up default user groups
- **`create_default_rise_and_shine()`**: Populates system prompts

## Performance Considerations

- **Indexed Queries**: Database queries are optimized with proper indexing
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Parameterized queries prevent SQL injection and improve performance
- **Memory Management**: Large result sets are handled efficiently
