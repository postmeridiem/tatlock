# Database Migrations

This file tracks all database schema migrations for Tatlock.

## Migration Format

Each migration is tagged with version numbers and SQL blocks:

```
## Migration: [from_version] → [to_version]

**Date**: YYYY-MM-DD
**Description**: Brief description of changes

### System Database Changes

```sql
-- [system:from_version→to_version:start]

-- SQL statements for system.db
CREATE TABLE ...;
ALTER TABLE ...;

-- [system:from_version→to_version:end]
```

### User Database Changes

```sql
-- [user:from_version→to_version:start]

-- SQL statements for {username}_longterm.db
CREATE TABLE ...;
ALTER TABLE ...;

-- [user:from_version→to_version:end]
```
```

## Migration Rules

1. **Idempotent**: Use `IF NOT EXISTS`, `IF EXISTS`, `OR IGNORE` to allow safe re-runs
2. **Tagged**: All SQL blocks must have start/end tags with version numbers
3. **Ordered**: System database migrations run before user database migrations
4. **Atomic**: Each migration is a transaction - all succeed or all rollback
5. **Tested**: Test migrations on a copy of production data before deploying

---

## Migration History

### Baseline: 0.3.19

**Date**: 2025-10-03
**Description**: Initial schema baseline - all tables that existed before migration system

This represents the complete schema as it existed when the migration system was introduced.

#### System Database Schema (0.3.19)

```sql
-- [system:baseline→0.3.19:start]

CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS passwords (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_roles (
    username TEXT,
    role_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, role_id),
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_groups (
    username TEXT,
    group_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, group_id),
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tools (
    tool_key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    module TEXT NOT NULL,
    function_name TEXT NOT NULL,
    enabled INTEGER DEFAULT 0 NOT NULL,
    prompts TEXT
);

CREATE TABLE IF NOT EXISTS tool_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_key TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    is_required INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY (tool_key) REFERENCES tools (tool_key) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rise_and_shine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instruction TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_settings (
    setting_key TEXT PRIMARY KEY,
    setting_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS setting_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL,
    option_value TEXT NOT NULL,
    is_default INTEGER DEFAULT 0,
    enabled INTEGER DEFAULT 1,
    UNIQUE(setting_key, option_value),
    FOREIGN KEY (setting_key) REFERENCES system_settings (setting_key) ON DELETE CASCADE
);

-- [system:baseline→0.3.19:end]
```

#### User Database Schema (0.3.19)

```sql
-- [user:baseline→0.3.19:start]

CREATE TABLE IF NOT EXISTS memories (
    interaction_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    user_prompt TEXT NOT NULL,
    llm_reply TEXT NOT NULL,
    full_conversation_history TEXT
);

CREATE TABLE IF NOT EXISTS topics (
    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_topics (
    interaction_id TEXT,
    topic_id INTEGER,
    PRIMARY KEY (interaction_id, topic_id),
    FOREIGN KEY (interaction_id) REFERENCES memories (interaction_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conversation_topics (
    conversation_id TEXT,
    topic_id INTEGER,
    first_occurrence TEXT NOT NULL,
    last_occurrence TEXT NOT NULL,
    topic_count INTEGER DEFAULT 1,
    PRIMARY KEY (conversation_id, topic_id),
    FOREIGN KEY (conversation_id) REFERENCES memories (conversation_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    title TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS conversation_compacts (
    compact_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    compact_timestamp TEXT NOT NULL,
    messages_up_to INTEGER NOT NULL,
    compact_summary TEXT NOT NULL,
    topics_covered TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_compacts_conversation ON conversation_compacts(conversation_id);
CREATE INDEX IF NOT EXISTS idx_compacts_timestamp ON conversation_compacts(compact_timestamp);

CREATE TABLE IF NOT EXISTS personal_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS personal_variables_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS short_term_storage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    storage_key TEXT UNIQUE NOT NULL,
    storage_value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- [user:baseline→0.3.19:end]
```

---

## Active Migrations

### Migration: 0.3.19 → 0.3.20

**Date**: 2025-10-07
**Description**: Add conversation_messages table and schema versioning for memory system refactoring

#### System Database Changes

```sql
-- [system:0.3.19→0.3.20:start]

-- No system database changes for this migration

-- [system:0.3.19→0.3.20:end]
```

#### User Database Changes

```sql
-- [user:0.3.19→0.3.20:start]

-- Add conversation_messages table for new schema
CREATE TABLE IF NOT EXISTS conversation_messages (
    message_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    message_number INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_number
ON conversation_messages(conversation_id, message_number);

CREATE INDEX IF NOT EXISTS idx_messages_timestamp
ON conversation_messages(timestamp);

-- Add schema versioning to conversations table
-- schema_version = 1: uses memories table (old schema)
-- schema_version = 2: uses conversation_messages table (new schema)
ALTER TABLE conversations ADD COLUMN schema_version INTEGER DEFAULT 1;

-- Add compact tracking fields to conversations table
ALTER TABLE conversations ADD COLUMN compact_summary TEXT;
ALTER TABLE conversations ADD COLUMN compacted_up_to INTEGER DEFAULT 0;

-- [user:0.3.19→0.3.20:end]
```

---

## Future Migrations

### Migration: 0.3.20 → 0.3.21 (Planned)

**Description**: Drop full_conversation_history column after complete migration to conversation_messages

```sql
-- [user:0.3.20→0.3.21:start]
-- ALTER TABLE memories DROP COLUMN full_conversation_history;
-- [user:0.3.20→0.3.21:end]
```

### Migration: 0.3.21 → 0.3.22 (Planned)

**Description**: Drop conversation_compacts table after moving compacts to conversations table

```sql
-- [user:0.3.21→0.3.22:start]
-- DROP TABLE IF EXISTS conversation_compacts;
-- [user:0.3.21→0.3.22:end]
```

### Migration: 0.3.22 → 0.3.23 (Planned)

**Description**: Drop memories table after complete migration to conversation_messages

```sql
-- [user:0.3.22→0.3.23:start]
-- DROP TABLE IF EXISTS memories;
-- DROP TABLE IF EXISTS memory_topics;
-- [user:0.3.22→0.3.23:end]
```
