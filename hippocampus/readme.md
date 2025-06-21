# hippocampus

This module manages all forms of persistent memory for Tatlock, including databases and long-term storage. It provides memory recall, storage, and retrieval functions to inform the agent's context and history, along with comprehensive user authentication and management. Each user has their own isolated memory database for complete privacy and data separation.

## Core Components

### Database Management
- **{username}_longterm.db**: Per-user conversation memory, topics, and system prompts
- **system.db**: Stores user authentication, roles, and groups (shared across all users)

### Memory Functions

#### `database.py`
- **`get_base_instructions()`**: Retrieves enabled system prompts from user's `rise_and_shine` table
- **`query_personal_variables()`**: Looks up personal information by key for the current user
- **Database Connection Management**: Handles connections to both user-specific longterm and shared system databases

#### `remember.py`
- **`save_interaction()`**: Saves full conversation interactions with topics to user's database
- **`get_or_create_topic()`**: Manages topic creation and linking within user's database
- **`create_or_update_conversation()`**: Creates and updates conversation records with metadata
- **User-Specific Storage**: Associates memories with specific users in isolated databases

#### `recall.py`
- **`recall_memories()`**: Search memories by keyword in prompts, replies, or topics (user-scoped)
- **`recall_memories_with_time()`**: Search with temporal filtering (date ranges) for current user
- **`get_user_conversations()`**: List all conversations for the current user
- **`get_conversation_details()`**: Get detailed conversation information for current user
- **`search_conversations()`**: Search conversations by title or content for current user
- **`get_conversations_by_topic()`**: Find conversations containing specific topics for current user
- **`get_topics_by_conversation()`**: Get all topics in a specific conversation for current user
- **`get_conversation_summary()`**: Get comprehensive conversation summaries for current user
- **`get_topic_statistics()`**: Get statistics about topics across conversations for current user
- **User-Specific Recall**: All memory operations are scoped to the current user for privacy

#### `user_database.py`
- **`ensure_user_database()`**: Creates user-specific database if it doesn't exist
- **`get_database_connection()`**: Gets connection to user's specific database
- **`execute_user_query()`**: Executes queries on user's database with proper error handling

## Database Schema

### {username}_longterm.db Tables (Per User)
- **memories**: Stores conversation interactions with timestamps and conversation_id
  - `id`: Primary key
  - `user_prompt`: The user's message
  - `llm_reply`: The AI's response
  - `full_llm_history`: Complete conversation context including tool calls
  - `topic`: Topic classification
  - `timestamp`: When the interaction occurred
  - `conversation_id`: Links interactions to conversations

- **topics**: Topic classification for conversations
  - `id`: Primary key
  - `name`: Topic name (e.g., "weather", "personal_info")
  - `created_at`: When the topic was created

- **memory_topics**: Links memories to topics
  - `memory_id`: Foreign key to memories table
  - `topic_id`: Foreign key to topics table

- **conversation_topics**: Links conversations to topics with metadata
  - `conversation_id`: Foreign key to conversations table
  - `topic_id`: Foreign key to topics table
  - `first_mentioned`: When the topic was first mentioned in the conversation
  - `last_mentioned`: When the topic was last mentioned in the conversation
  - `mention_count`: How many times the topic was mentioned

- **conversations**: Conversation metadata including titles, start times, and message counts
  - `id`: Primary key (conversation_id)
  - `title`: Generated conversation title
  - `start_time`: When the conversation started
  - `last_activity`: When the conversation was last active
  - `message_count`: Total number of messages in the conversation

- **rise_and_shine**: System prompts and instructions for the LLM (copied to each user's database)
  - `id`: Primary key
  - `instruction`: The system instruction
  - `enabled`: Whether the instruction is active
  - `created_at`: When the instruction was created

### system.db Tables (Shared)
- **users**: User accounts with hashed passwords, salts, and profile information
  - `username`: Primary key
  - `password_hash`: PBKDF2 hashed password
  - `salt`: Unique salt for password hashing
  - `first_name`: User's first name
  - `last_name`: User's last name
  - `email`: User's email address
  - `created_at`: When the account was created
  - `last_login`: When the user last logged in

- **roles**: Available roles (user, admin, moderator)
  - `id`: Primary key
  - `name`: Role name
  - `description`: Role description
  - `created_at`: When the role was created

- **groups**: Available groups (users, admins, moderators)
  - `id`: Primary key
  - `name`: Group name
  - `description`: Group description
  - `created_at`: When the group was created

- **user_roles**: Links users to roles
  - `username`: Foreign key to users table
  - `role_id`: Foreign key to roles table

- **user_groups**: Links users to groups
  - `username`: Foreign key to users table
  - `group_id`: Foreign key to groups table

## System Prompts

**Important**: All future system prompts (base instructions) for the LLM should be stored as records in the `rise_and_shine` table, except for the current date, which is injected dynamically. Each user gets their own copy of system prompts in their database.

The `rise_and_shine` table contains:
- Tatlock's personality and behavior instructions
- Tool usage guidelines
- Silent tool execution directive
- Improvement suggestion instructions

## Memory Recall Features

- **Keyword Search**: Search across user prompts, AI replies, and topic names (user-scoped)
- **Temporal Filtering**: Filter by date ranges ("yesterday", "last week", etc.) for current user
- **Topic Classification**: Automatic topic assignment and retrieval per user
- **Full Context**: Access to complete conversation history including tool calls
- **User Isolation**: Each user's memories are completely isolated and private
- **Conversation Management**: Track conversation metadata, titles, and statistics per user
- **Natural Language Date Parsing**: Understands relative time expressions

## Security & Privacy

- **Password Hashing**: PBKDF2 with unique salts per user
- **Role-Based Access**: User roles and group management
- **Database Isolation**: Separate databases for each user's memory and shared authentication
- **User Data Privacy**: Memories are associated with specific users in isolated databases
- **Input Validation**: All database operations use parameterized queries
- **Complete Data Separation**: No cross-user data access possible
- **SQL Injection Prevention**: All queries use parameterized statements

## Integration with Authentication

- **User Context**: Memory operations respect user authentication and session data
- **Personal Information**: Tools can access user-specific data through the authentication system
- **Memory Isolation**: Each user's conversations are stored and retrieved from their own database
- **Role-Based Access**: Memory access can be controlled by user roles
- **Session Management**: Works with session-based authentication for user context

## Installation Support

The module includes database setup utilities in `stem/installation/database_setup.py`:
- **`create_system_db_tables()`**: Creates shared authentication database schema
- **`create_longterm_db_tables()`**: Creates user memory database schema (template)
- **`create_default_roles()`**: Sets up default user roles
- **`create_default_groups()`**: Sets up default user groups
- **`create_default_rise_and_shine()`**: Populates system prompts (copied to each user's database)

## Performance Considerations

- **Indexed Queries**: Database queries are optimized with proper indexing
- **Connection Pooling**: Efficient database connection management per user
- **Query Optimization**: Parameterized queries prevent SQL injection and improve performance
- **Memory Management**: Large result sets are handled efficiently
- **User Database Creation**: User databases are created on-demand for efficient resource usage
- **Lazy Loading**: Database connections are established only when needed

## Error Handling

### Database Errors
- **Connection Failures**: Graceful handling of database connection issues
- **Query Errors**: Comprehensive error logging and fallback responses
- **User Database Creation**: Automatic creation of user databases on first use
- **Transaction Management**: Proper transaction handling for data consistency

### Memory Operations
- **Save Failures**: Memory save errors are logged but don't break conversation flow
- **Recall Failures**: Graceful degradation when memory recall fails
- **Topic Classification**: Fallback to "general" topic when classification fails

## Future Enhancements

### Planned Features
- **Memory Compression**: Automatic summarization of old conversations
- **Memory Expiration**: Configurable retention policies for old memories
- **Memory Search**: Full-text search capabilities across all user data
- **Memory Analytics**: Usage statistics and insights
- **Memory Export**: User data export functionality
- **Memory Backup**: Automatic backup and restore capabilities

### Performance Improvements
- **Database Indexing**: Additional indexes for faster queries
- **Query Optimization**: More efficient query patterns
- **Connection Pooling**: Enhanced connection management
- **Caching**: Memory result caching for frequently accessed data
