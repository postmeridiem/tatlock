# Hippocampus

**Status: Production Ready - Complete Memory System**

The Hippocampus module manages all forms of persistent memory for Tatlock, including databases and long-term storage. Named after the brain's hippocampus responsible for memory formation and retrieval, this module provides memory recall, storage, and retrieval functions to inform the agent's context and history, along with comprehensive user authentication and management. Each user has their own isolated memory database for complete privacy and data separation.

## ✅ **Core Features**

### 🗄️ **Database Management**
- **{username}_longterm.db**: Per-user conversation memory, topics, and personal variables
- **system.db**: Stores user authentication, roles, groups, tools, and GLOBAL system prompts
- **Short-term Storage**: User-specific temporary file storage in `shortterm/{username}/`

### 🧠 **Memory Functions**

#### **Database Operations** (`database.py`)
- **`get_base_instructions()`**: Retrieves enabled system prompts from user's `rise_and_shine` table
- **`query_personal_variables()`**: Looks up personal information by key for the current user
- **Database Connection Management**: Handles connections to both user-specific longterm and shared system databases

#### **Memory Storage** (`remember.py`)
- **`save_interaction()`**: Saves full conversation interactions with topics to user's database
- **`get_or_create_topic()`**: Manages topic creation and linking within user's database
- **`create_or_update_conversation()`**: Creates and updates conversation records with metadata
- **User-Specific Storage**: Associates memories with specific users in isolated databases

#### **Memory Recall** (`recall.py`)
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

#### **User Database Management** (`user_database.py`)
- **`ensure_user_database()`**: Creates user-specific database if it doesn't exist
- **`get_database_connection()`**: Gets connection to user's specific database
- **`execute_user_query()`**: Executes queries on user's database with proper error handling
- **`get_user_image_path()`**: Manages user-specific image storage paths

## 🛠️ **Tool Integration**

### **Memory Tools** (Root directory)
All memory-related tools are organized in the root of the `hippocampus/` module:

#### **Core Memory Tools**
- **`find_personal_variables_tool.py`**: Look up personal information by key
- **`get_conversation_details_tool.py`**: Get detailed conversation information
- **`get_conversation_summary_tool.py`**: Get conversation summaries
- **`get_conversations_by_topic_tool.py`**: Find conversations by topic
- **`get_topic_statistics_tool.py`**: Get topic statistics across conversations
- **`get_topics_by_conversation_tool.py`**: Get topics in a conversation
- **`get_user_conversations_tool.py`**: List user conversations
- **`recall_memories_tool.py`**: Search memories by keyword
- **`recall_memories_with_time_tool.py`**: Search memories with temporal filtering
- **`search_conversations_tool.py`**: Search conversations by content

#### **Advanced Memory Analytics Tools**
- **`memory_insights_tool.py`**: Advanced analytics for conversation patterns and usage statistics
  - **Overview Analysis**: Total conversations, memories, topics, and averages
  - **Pattern Analysis**: Most active days, hours, and conversation length statistics
  - **Topic Analysis**: Trending topics and engagement metrics
  - **Temporal Analysis**: Usage patterns over time with day/hour breakdowns
  - **Usage**: `execute_memory_insights(analysis_type, similarity_threshold)`

- **`memory_cleanup_tool.py`**: Database health and maintenance utilities
  - **Duplicate Detection**: Find similar memories with configurable similarity thresholds
  - **Orphaned Records**: Identify and report orphaned database records
  - **Health Analysis**: Data quality assessment with health scores
  - **Database Statistics**: Comprehensive database health metrics
  - **Usage**: `execute_memory_cleanup(cleanup_type, similarity_threshold)`

- **`memory_export_tool.py`**: Data export capabilities in multiple formats
  - **JSON Export**: Full conversation and memory data with metadata
  - **CSV Export**: Spreadsheet-friendly format for analysis
  - **Summary Export**: Key statistics and insights report
  - **Date Filtering**: Configurable date ranges (last_7_days, last_30_days, custom)
  - **Topic Inclusion**: Optional topic data in exports
  - **Usage**: `execute_memory_export(export_type, include_topics, date_range)`

### **Tool Standards**
All tools follow the standardized pattern:
```python
import logging
from stem.logging import get_logger

logger = get_logger(__name__)

def execute_tool_name(parameters):
    """Tool description following developer.md standards."""
    try:
        # Tool implementation
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return {"status": "error", "message": str(e)}

### **Advanced Memory Tool Usage Examples**

#### **Memory Insights**
```python
# Get overview statistics
result = execute_memory_insights("overview")
# Returns: total conversations, memories, topics, averages, date ranges

# Analyze usage patterns
result = execute_memory_insights("patterns")
# Returns: most active days/hours, conversation length statistics

# Topic analysis
result = execute_memory_insights("topics")
# Returns: trending topics, engagement metrics, topic evolution
```

#### **Memory Cleanup**
```python
# Find duplicate memories (80% similarity threshold)
result = execute_memory_cleanup("duplicates", 0.8)
# Returns: duplicate groups, total duplicates, cleanup recommendations

# Check for orphaned records
result = execute_memory_cleanup("orphans")
# Returns: orphaned memories, topics, conversation links

# Database health analysis
result = execute_memory_cleanup("analysis")
# Returns: data quality scores, completeness metrics, health assessment
```

#### **Memory Export**
```python
# Export all data as JSON
result = execute_memory_export("json", True, None)
# Returns: file path, size, total records exported

# Export recent conversations as CSV
result = execute_memory_export("csv", False, "last_7_days")
# Returns: CSV file with conversation data

# Export summary report
result = execute_memory_export("summary", True, "last_30_days")
# Returns: summary statistics and insights
```

## 📊 **Database Schema**

### **{username}_longterm.db Tables (Per User)**

#### **memories**
Stores conversation interactions with timestamps and conversation_id
```sql
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_prompt TEXT NOT NULL,
    llm_reply TEXT NOT NULL,
    full_llm_history TEXT NOT NULL,
    topic TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    conversation_id INTEGER,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

#### **topics**
Topic classification for conversations
```sql
CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### **memory_topics**
Links memories to topics
```sql
CREATE TABLE memory_topics (
    memory_id INTEGER,
    topic_id INTEGER,
    FOREIGN KEY (memory_id) REFERENCES memories(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);
```

#### **conversation_topics**
Links conversations to topics with metadata
```sql
CREATE TABLE conversation_topics (
    conversation_id INTEGER,
    topic_id INTEGER,
    first_mentioned DATETIME,
    last_mentioned DATETIME,
    mention_count INTEGER DEFAULT 1,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    FOREIGN KEY (topic_id) REFERENCES topics(id)
);
```

#### **conversations**
Conversation metadata including titles, start times, and message counts
```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0
);
```

#### **rise_and_shine** (GLOBAL - in system.db)
System prompts and instructions for the LLM (GLOBAL table, shared by all users)
```sql
CREATE TABLE rise_and_shine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instruction TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **system.db Tables (Shared)**

#### **users**
User accounts with profile information
```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### **passwords**
Separate table for password hashes and salts
```sql
CREATE TABLE passwords (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
);
```

#### **roles**
Available roles (user, admin, moderator)
```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### **groups**
Available groups (users, admins, moderators)
```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### **user_roles**
Links users to roles
```sql
CREATE TABLE user_roles (
    username TEXT,
    role_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, role_id),
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);
```

#### **user_groups**
Links users to groups
```sql
CREATE TABLE user_groups (
    username TEXT,
    group_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, group_id),
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
);
```

#### **tools**
Tool registry for the system
```sql
CREATE TABLE tools (
    tool_key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    module TEXT NOT NULL,
    function_name TEXT NOT NULL,
    enabled INTEGER DEFAULT 0 NOT NULL
);
```

#### **tool_parameters**
Tool parameter definitions
```sql
CREATE TABLE tool_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_key TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    is_required INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY (tool_key) REFERENCES tools (tool_key) ON DELETE CASCADE
);
```

## 🔧 **System Prompts**

### 🌟 **Global System Prompts (rise_and_shine)**
- **Location**: `hippocampus/system.db` (NOT in user databases)
- **Purpose**: Contains Tatlock's base instructions, personality, and tool usage guidelines
- **Scope**: Global - all users share the same system prompts
- **Content**: Tatlock's personality, behavior rules, tool usage instructions, and system guidelines
- **Access**: Retrieved by `get_base_instructions()` function for all users
- **Management**: Updated through system database operations, not per-user

**IMPORTANT**: The `rise_and_shine` table MUST remain in the system database. Moving it to user databases would break the system architecture and create inconsistencies across users.

## 🎯 **Memory Recall Features**

- **Keyword Search**: Search across user prompts, AI replies, and topic names (user-scoped)
- **Temporal Filtering**: Filter by date ranges ("yesterday", "last week", etc.) for current user
- **Topic Classification**: Automatic topic assignment and retrieval per user
- **Full Context**: Access to complete conversation history including tool calls
- **User Isolation**: Each user's memories are completely isolated and private
- **Conversation Management**: Track conversation metadata, titles, and statistics per user
- **Natural Language Date Parsing**: Understands relative time expressions

## 🛡️ **Security & Privacy**

- **Password Hashing**: PBKDF2 with unique salts per user
- **Role-Based Access**: User roles and group management
- **Database Isolation**: Separate databases for each user's memory and shared authentication
- **User Data Privacy**: Memories are associated with specific users in isolated databases
- **Input Validation**: All database operations use parameterized queries
- **Complete Data Separation**: No cross-user data access possible
- **SQL Injection Prevention**: All queries use parameterized statements

## 🔗 **Integration with Authentication**

- **User Context**: Memory operations respect user authentication and session data
- **Personal Information**: Tools can access user-specific data through the authentication system
- **Memory Isolation**: Each user's conversations are stored and retrieved from their own database
- **Role-Based Access**: Memory access can be controlled by user roles
- **Session Management**: Works with session-based authentication for user context

## 🚀 **Installation Support**

The module includes database setup utilities in `stem/installation/database_setup.py`:
- **`create_system_db_tables()`**: Creates shared authentication database schema
- **`create_longterm_db_tables()`**: Creates user memory database schema (template)
- **`create_default_roles()`**: Sets up default user roles
- **`create_default_groups()`**: Sets up default user groups
- **`create_default_rise_and_shine()`**: Populates system prompts (copied to each user's database)

## 📈 **Performance Considerations**

- **Indexed Queries**: Database queries are optimized with proper indexing
- **Connection Pooling**: Efficient database connection management per user
- **Query Optimization**: Parameterized queries prevent SQL injection and improve performance
- **Memory Management**: Large result sets are handled efficiently
- **User Database Creation**: User databases are created on-demand for efficient resource usage
- **Lazy Loading**: Database connections are established only when needed

## 🧪 **Testing**

### **Unit Tests**
```bash
# Run hippocampus-specific tests
python -m pytest tests/test_hippocampus_*.py -v

# Run new memory tools tests
python -m pytest tests/test_memory_tools.py -v
```

### **Database Tests**
```bash
# Test database operations
python -m pytest tests/test_hippocampus_database.py -v
python -m pytest tests/test_hippocampus_recall.py -v
python -m pytest tests/test_hippocampus_remember.py -v

# Test new memory tools
python -m pytest tests/test_memory_tools.py::TestMemoryInsightsTool -v
python -m pytest tests/test_memory_tools.py::TestMemoryCleanupTool -v
python -m pytest tests/test_memory_tools.py::TestMemoryExportTool -v
```

### **Test Coverage**
The memory tools include comprehensive test coverage:
- **16 test cases** covering all tool functionality
- **Unit tests** for individual tool features
- **Integration tests** for helper functions
- **Error handling** and edge case testing
- **Mock database** and file operations for reliable testing

## ⚠️ **Error Handling**

### **Database Errors**
- **Connection Failures**: Graceful handling of database connection issues
- **Query Errors**: Comprehensive error logging and fallback responses
- **User Database Creation**: Automatic creation of user databases on first use
- **Transaction Management**: Proper transaction handling for data consistency

### **Memory Operations**
- **Save Failures**: Memory save errors are logged but don't break conversation flow
- **Recall Failures**: Graceful degradation when memory recall fails
- **Topic Classification**: Fallback to "general" topic when classification fails

## 🔮 **Future Enhancements**

### **Planned Features**
- **Memory Compression**: Automatic summarization of old conversations
- **Memory Expiration**: Configurable retention policies for old memories
- **Memory Search**: Full-text search capabilities across all user data
- **Memory Backup**: Automatic backup and restore capabilities
- **Memory Visualization**: Interactive charts and graphs for analytics
- **Memory Recommendations**: AI-powered suggestions for conversation topics

### **Recently Implemented** ✅
- **Memory Analytics**: Usage statistics and insights (`memory_insights_tool.py`)
- **Memory Export**: User data export functionality (`memory_export_tool.py`)
- **Memory Cleanup**: Database health and maintenance utilities (`memory_cleanup_tool.py`)

### **Performance Improvements**
- **Database Indexing**: Additional indexes for faster queries
- **Query Optimization**: More efficient query patterns
- **Connection Pooling**: Enhanced connection management
- **Caching**: Memory result caching for frequently accessed data

## 📚 **Related Documentation**

- **[README.md](../README.md)** - General overview and installation
- **[developer.md](../developer.md)** - Developer guide and practices
- **[moreinfo.md](../moreinfo.md)** - In-depth technical information
- **[cortex/readme.md](../cortex/readme.md)** - Core agent logic documentation
- **[stem/readme.md](../stem/readme.md)** - Core utilities and infrastructure
- **[parietal/readme.md](../parietal/readme.md)** - Hardware monitoring and performance

## 🧑‍💻 User Context and Authentication

Tatlock now uses a context-based, per-request user model for all authentication and user info access, as described in the main developer documentation. All memory and user operations in the Hippocampus module are type-safe and use the current user context, which is set automatically for each request.

- The current user is available as a Pydantic `UserModel` via:
  ```python
  from stem.current_user_context import get_current_user_ctx
  user = get_current_user_ctx()
  if user is None:
      raise HTTPException(status_code=401, detail="Not authenticated")
  # Access fields as attributes, e.g. user.username
  ```
- All memory and recall functions are scoped to the current user, ensuring privacy and isolation.
- When passing the user to templates or tools, use `user.model_dump()` to convert to a dict if needed.
- See the [developer.md](../developer.md) for full details and examples of the context-based user pattern.

**Note:** All legacy patterns using `current_user` as a dict have been removed. Always use the context-based UserModel for user access in new code.
