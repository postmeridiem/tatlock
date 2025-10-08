# Memory System Dependency Analysis

**Created**: 2025-10-04
**Purpose**: Comprehensive analysis of current memory system dependencies and usage patterns to inform schema refactoring decisions.

---

## Executive Summary

The current memory system uses a **one-row-per-interaction** pattern where each `memories` table row contains both `user_prompt` and `llm_reply`. This creates complexity for message-level operations and causes data duplication through the `full_conversation_history` field.

**Key Findings:**

- **35 files** import or use hippocampus modules
- **6 files** directly query `memories` table (write operations)
- **10 files** directly query `conversations` table
- **4 files** use `conversation_compacts` table
- **13 tool files** depend on current schema for memory/conversation operations

**Refactoring Impact**: MEDIUM-HIGH - Multiple tools and core functions need updates, but abstraction layers exist that can minimize breaking changes.

---

## Table Structure Analysis

### Current `memories` Table Schema

```sql
CREATE TABLE memories (
    interaction_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    user_prompt TEXT NOT NULL,
    llm_reply TEXT NOT NULL,
    full_conversation_history TEXT  -- PROBLEM: Massive data duplication
);
```

**Problems:**

1. **One row = one interaction** (user + assistant pair)
   - Makes message-level queries awkward
   - Requires UNION ALL to get chronological message list
   - No sequential message numbering

2. **`full_conversation_history` field**
   - Stores entire conversation JSON in EVERY row
   - Causes exponential data duplication as conversations grow
   - 25-message conversation = ~625 duplicate message copies
   - Wasted disk space and query performance

3. **Message count calculations**
   - Requires `COUNT(*) * 2` because each row = 2 messages
   - Boundary calculations need manual index math
   - No direct "get messages 26-50" query

### Current `conversations` Table Schema

```sql
CREATE TABLE conversations (
    conversation_id TEXT PRIMARY KEY,
    title TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0
);
```

**Problems:**

1. `message_count` is manually updated - potential for drift
2. No compact summary storage - requires separate `conversation_compacts` table
3. No `compacted_up_to` tracking - requires querying separate table

### Current `conversation_compacts` Table Schema

```sql
CREATE TABLE conversation_compacts (
    compact_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    compact_timestamp TEXT NOT NULL,
    messages_up_to INTEGER NOT NULL,
    compact_summary TEXT NOT NULL,
    topics_covered TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);
```

**Problems:**

1. Separate table adds query complexity
2. One compact summary per conversation, yet stored in separate table
3. Requires JOIN to get conversation + compact in one query

---

## File Dependency Map

### Core Memory Functions

#### `hippocampus/remember.py`
**Purpose**: Save interactions to database

**Dependencies:**
- **WRITES to `memories`**: Line 82-85 (INSERT INTO memories)
- **WRITES to `conversations`**: Line 172-176 (INSERT OR REPLACE INTO conversations)
- **WRITES to `conversation_topics`**: Line 98-99, 138-148

**Key Functions:**
- `save_interaction()` - Main write function
- `create_or_update_conversation()` - Updates conversation metadata
- `update_conversation_topics()` - Manages topic relationships

**Refactoring Impact**: **HIGH** - Core write path, needs dual-write system

---

#### `hippocampus/recall.py`
**Purpose**: Query and retrieve memories

**Dependencies:**
- **READS from `memories`**: Lines 37-47, 74-94, 117-119, 172, 188, 249-252, 302-305, 374-389
- **READS from `conversations`**: Lines 242-261, 286-290, 340-361
- **JOINS `memories` + `topics`**: Multiple locations

**Key Functions:**
- `recall_memories()` - Keyword search across memories
- `recall_memories_with_time()` - Time-bound memory search
- `get_user_conversations()` - List all conversations with summaries
- `get_conversation_details()` - Full conversation metadata
- `search_conversations()` - Search by conversation title
- `get_conversation_messages()` - **UNION ALL query** to get chronological messages (Lines 369-391)

**Refactoring Impact**: **MEDIUM** - Read operations can use abstraction layer, but `get_conversation_messages()` needs complete rewrite

---

#### `hippocampus/forget.py`
**Purpose**: Delete memories and conversations

**Dependencies:**
- **DELETES from `memories`**: Lines 24, 58, 78
- **DELETES from `conversations`**: Line 59
- **DELETES from `conversation_topics`**: Line 30

**Key Functions:**
- `purge_all_memories()` - Complete user data wipe
- `delete_conversation()` - Delete specific conversation
- `delete_memory_turn()` - Delete single interaction

**Refactoring Impact**: **LOW** - Delete operations are simple, easy to adapt

---

### Conversation Compacting System

#### `hippocampus/conversation_compact.py`
**Purpose**: Automatic conversation summarization every 25 messages

**Dependencies:**
- **READS from `memories`**: Lines 133-134 (get messages to compact)
- **READS from `conversation_compacts`**: Lines 117-123, 262-269
- **WRITES to `conversation_compacts`**: Lines 199-203
- **READS from `conversations`**: Lines 249-252, 275-280

**Key Functions:**
- `create_conversation_compact()` - Create new compact summary
- `get_conversation_context()` - Load compact + recent messages (CRITICAL for Phase 1)
- `should_compact_conversation()` - Check if 25-message threshold reached
- `trigger_compact_if_needed()` - Auto-trigger after save_interaction

**Current Logic:**
```python
# Count messages: each memories row = 2 messages
cursor.execute("SELECT COUNT(*) * 2 FROM memories WHERE conversation_id = ?")
total_messages = cursor.fetchone()[0]

# Calculate compact boundary
last_compact_boundary = (total_messages // 25) * 25
```

**Refactoring Impact**: **HIGH** - Core context loading for 4.5-phase architecture, needs careful migration

---

### Memory Tools (13 files)

All tools follow the pattern: query user database → return formatted results

**Tool Files:**
1. `find_personal_variables_tool.py` - No memories dependency
2. `get_conversation_details_tool.py` - Calls `recall.get_conversation_details()`
3. `get_conversation_summary_tool.py` - Calls `recall.get_conversation_summary()`
4. `get_conversations_by_topic_tool.py` - Calls `recall.get_conversations_by_topic()`
5. `get_topic_statistics_tool.py` - Calls `recall.get_topic_statistics()`
6. `get_topics_by_conversation_tool.py` - Calls `recall.get_topics_by_conversation()`
7. `get_user_conversations_tool.py` - Calls `recall.get_user_conversations()`
8. `memory_cleanup_tool.py` - Deletes old memories, queries `memories` table directly
9. `memory_export_tool.py` - Exports memories to JSON, queries `memories` table directly
10. `memory_insights_tool.py` - Analytics, queries `memories` + `conversations` tables
11. `recall_memories_tool.py` - Calls `recall.recall_memories()`
12. `recall_memories_with_time_tool.py` - Calls `recall.recall_memories_with_time()`
13. `search_conversations_tool.py` - Calls `recall.search_conversations()`

**Refactoring Impact**: **LOW-MEDIUM** - Most use abstraction layer (`recall.py` functions), only 3 query directly

---

### Core Application Integration

#### `cortex/tatlock.py`
**Purpose**: 4.5-phase prompt processor

**Dependencies:**
- **Calls `get_conversation_context()`**: Line 30 import, usage in `_build_context()` method
- **Calls `trigger_compact_if_needed()`**: Line 30 import, called after save_interaction
- **Calls `save_interaction()`**: Line 29 import

**Critical Integration Points:**
- Phase 1 prompt building uses compact summary
- Background compacting after each interaction

**Refactoring Impact**: **MEDIUM** - Uses high-level functions, minimal code changes needed

---

## Query Pattern Analysis

### Read Patterns

**Pattern 1: Get all memories for conversation**
```sql
-- Current (from recall.py get_conversation_messages)
SELECT interaction_id, 'user' as role, user_prompt as content, timestamp
FROM memories WHERE conversation_id = ?
UNION ALL
SELECT interaction_id, 'assistant' as role, llm_reply as content, timestamp
FROM memories WHERE conversation_id = ?
ORDER BY timestamp;
```
**Problem**: UNION ALL adds complexity, no message sequencing

**Proposed:**
```sql
SELECT message_id, role, content, timestamp, message_number
FROM conversation_messages
WHERE conversation_id = ?
ORDER BY message_number;
```

---

**Pattern 2: Get messages for compacting**
```sql
-- Current (from conversation_compact.py)
-- Step 1: Count total messages
SELECT COUNT(*) * 2 FROM memories WHERE conversation_id = ?

-- Step 2: Calculate boundary with division
last_compact_boundary = (total // 25) * 25

-- Step 3: Get all messages, filter in Python
SELECT role, content, timestamp FROM memories WHERE conversation_id = ?
-- Python: filter messages [start_from:start_from + 25]
```
**Problem**: Loads all messages into memory, filters in Python

**Proposed:**
```sql
-- Direct range query
SELECT role, content, timestamp, message_number
FROM conversation_messages
WHERE conversation_id = ? AND message_number BETWEEN ? AND ?
ORDER BY message_number;
```

---

**Pattern 3: Get conversation context (compact + recent)**
```sql
-- Current (from conversation_compact.py)
-- Get compact from separate table
SELECT compact_summary, messages_up_to
FROM conversation_compacts
WHERE conversation_id = ?
ORDER BY compact_timestamp DESC LIMIT 1;

-- Get messages after compact boundary (complex Python logic)
SELECT role, content FROM memories WHERE conversation_id = ?
-- Python: filter idx > messages_up_to
```

**Proposed:**
```sql
-- Single query with compact in conversations table
SELECT
    compact_summary,
    compacted_up_to,
    (SELECT json_group_array(json_object(
        'role', role,
        'content', content,
        'timestamp', timestamp
    ))
    FROM conversation_messages
    WHERE conversation_id = c.conversation_id
      AND message_number > c.compacted_up_to
    ) as recent_messages
FROM conversations c
WHERE conversation_id = ?;
```

---

### Write Patterns

**Pattern 1: Save interaction**
```sql
-- Current (from remember.py)
INSERT INTO memories (interaction_id, conversation_id, timestamp, user_prompt, llm_reply, full_conversation_history)
VALUES (?, ?, ?, ?, ?, ?);  -- full_conversation_history = HUGE JSON blob

UPDATE conversations SET message_count = message_count + 2, last_activity = ? WHERE conversation_id = ?;
```
**Problem**: `full_conversation_history` duplicates all messages in every row

**Proposed:**
```sql
-- Get current max message_number
SELECT COALESCE(MAX(message_number), 0) FROM conversation_messages WHERE conversation_id = ?;

-- Insert user message
INSERT INTO conversation_messages (message_id, conversation_id, message_number, role, content, timestamp)
VALUES (?, ?, ?, 'user', ?, ?);

-- Insert assistant message
INSERT INTO conversation_messages (message_id, conversation_id, message_number, role, content, timestamp)
VALUES (?, ?, ?, 'assistant', ?, ?);

-- Update conversation (automatic message_count from subquery)
UPDATE conversations SET last_activity = ? WHERE conversation_id = ?;
```

---

## Abstraction Layer Assessment

### Well-Abstracted Components

**Strengths:**
- Most tools call `recall.py` functions instead of direct SQL
- `cortex/tatlock.py` uses high-level `get_conversation_context()`
- User database isolation through `ensure_user_database()` and `execute_user_query()`

**Implications:**
- Can update `recall.py` functions internally without breaking tool code
- Dual-write system can be implemented in `remember.py` without touching tools
- Migration can happen behind abstraction layer

### Directly Coupled Components

**Need Attention:**
1. `memory_cleanup_tool.py` - Direct DELETE queries
2. `memory_export_tool.py` - Direct SELECT queries
3. `memory_insights_tool.py` - Direct analytics queries
4. `conversation_compact.py` - Complex query logic for boundary calculations

**Implications:**
- These 4 files need explicit schema awareness updates
- Test coverage critical for these files

---

## Data Migration Considerations

### Current Data Duplication Issue

**Example**: 25-message conversation

**Current Storage:**
```
Row 1: interaction_1, user_prompt_1, llm_reply_1, full_history[1-2]      (2 messages stored)
Row 2: interaction_2, user_prompt_2, llm_reply_2, full_history[1-4]      (4 messages stored)
Row 3: interaction_3, user_prompt_3, llm_reply_3, full_history[1-6]      (6 messages stored)
...
Row 12: interaction_12, user_prompt_12, llm_reply_12, full_history[1-24] (24 messages stored)
Row 13: interaction_13, user_prompt_13, llm_reply_13, full_history[1-26] (26 messages stored - COMPACT TRIGGERED)
```

**Total messages stored**: 2 + 4 + 6 + ... + 24 + 26 = **364 message copies** for 26 actual messages!

**New Storage:**
```
message_1, message_2, message_3, ..., message_26
```

**Total messages stored**: **26 message copies** (one per actual message)

**Space Savings**: ~93% reduction in message duplication

### Migration Complexity

**Extracting Messages from Memories Table:**

```python
def migrate_memories_to_conversation_messages(conversation_id):
    # Get all interactions in order
    cursor.execute("""
        SELECT interaction_id, timestamp, user_prompt, llm_reply
        FROM memories
        WHERE conversation_id = ?
        ORDER BY timestamp ASC
    """, (conversation_id,))

    interactions = cursor.fetchall()
    message_number = 1

    for interaction in interactions:
        # User message
        cursor.execute("""
            INSERT INTO conversation_messages
            (message_id, conversation_id, message_number, role, content, timestamp)
            VALUES (?, ?, ?, 'user', ?, ?)
        """, (f"{interaction[0]}_user", conversation_id, message_number, interaction[2], interaction[1]))
        message_number += 1

        # Assistant message
        cursor.execute("""
            INSERT INTO conversation_messages
            (message_id, conversation_id, message_number, role, content, timestamp)
            VALUES (?, ?, ?, 'assistant', ?, ?)
        """, (f"{interaction[0]}_assistant", conversation_id, message_number, interaction[3], interaction[1]))
        message_number += 1
```

**Challenges:**
- Need to preserve exact timestamps
- Need to generate sequential message_number
- Need to link interaction_id to new message_ids for topic relationships
- Migration should be idempotent (can run multiple times safely)

---

## Breaking Changes Identified

### HIGH IMPACT (Require Code Changes)

1. **`get_conversation_messages()` in recall.py**
   - Current: UNION ALL query on memories table
   - New: Direct SELECT from conversation_messages
   - **Impact**: API stays same, implementation changes completely

2. **`get_conversation_context()` in conversation_compact.py**
   - Current: Complex Python logic with COUNT(*) * 2
   - New: Simple range query on message_number
   - **Impact**: Logic simplification, same output format

3. **`save_interaction()` in remember.py**
   - Current: Single INSERT with both user_prompt and llm_reply
   - New: Two INSERTs for separate messages
   - **Impact**: Must track message_number sequence

4. **`create_conversation_compact()` in conversation_compact.py**
   - Current: INSERT into conversation_compacts table
   - New: UPDATE conversations.compact_summary
   - **Impact**: Table change, simpler queries

### MEDIUM IMPACT (Abstraction Layer Protects)

5. **Memory tools** (13 files)
   - Most call recall.py functions
   - Only 3 tools (cleanup, export, insights) have direct queries
   - **Impact**: Minimal if recall.py maintains API compatibility

6. **Conversation analytics**
   - `memory_insights_tool.py` counts from memories table
   - Easy to switch to conversation_messages
   - **Impact**: One-line query changes

### LOW IMPACT (No Changes Needed)

7. **Topic system** (topics, memory_topics, conversation_topics)
   - No schema changes planned
   - Links to interaction_id, not message_id
   - **Impact**: Could maintain compatibility OR add message_id links

8. **Phase 1 integration** in cortex/tatlock.py
   - Uses `get_conversation_context()` abstraction
   - No awareness of internal schema
   - **Impact**: Zero changes if function API maintained

---

## Backward Compatibility Strategy

### Option A: Dual-Read System (Recommended)

Keep both tables during transition:

```python
def get_conversation_messages_v2(username, conversation_id):
    # Try new schema first
    new_messages = query_conversation_messages_table(username, conversation_id)

    if new_messages:
        return new_messages

    # Fallback to old schema
    return query_memories_table_union_all(username, conversation_id)
```

**Pros:**
- Zero downtime
- Gradual migration
- Easy rollback

**Cons:**
- Temporary code complexity
- Need to maintain both code paths

### Option B: Dual-Write System

Write to both schemas simultaneously:

```python
def save_interaction_v2(username, user_prompt, llm_reply, topics, conversation_id):
    # Write to OLD schema
    save_to_memories_table(...)

    # Write to NEW schema
    save_to_conversation_messages_table(...)

    # Both writes succeed or both rollback
```

**Pros:**
- Data stays synchronized
- Can verify new schema correctness
- Allows comparison testing

**Cons:**
- Double write cost (temporary)
- Transaction complexity

### Option C: Flag-Based Migration

Add `migrated` flag to conversations table:

```sql
ALTER TABLE conversations ADD COLUMN schema_version INTEGER DEFAULT 1;
-- schema_version = 1: old memories table
-- schema_version = 2: new conversation_messages table
```

```python
def get_conversation_messages(username, conversation_id):
    schema_version = get_schema_version(conversation_id)

    if schema_version == 2:
        return query_conversation_messages_table(...)
    else:
        return query_memories_table(...)
```

**Pros:**
- Per-conversation migration tracking
- No need to maintain dual-write forever
- Clear migration state

**Cons:**
- Need migration job to convert old conversations
- Query routing complexity

---

## Recommended Migration Path

### Phase 1: Add New Schema (No Behavior Changes)

1. Add `conversation_messages` table to schema
2. Add `compact_summary` and `compacted_up_to` to conversations table
3. Add `schema_version` flag to conversations table
4. Deploy schema changes via migration

**Risk**: LOW - Only adds tables/columns, doesn't change behavior

### Phase 2: Implement Dual-Write (Hidden Migration)

1. Update `save_interaction()` to write to BOTH schemas
2. Set `schema_version = 2` for new conversations
3. Keep reading from old schema for existing conversations

**Risk**: MEDIUM - Write path changes, but reads unchanged

### Phase 3: Background Migration Job

1. Create migration worker to convert old conversations
2. Process conversations in batches (e.g., 100 at a time)
3. Mark migrated conversations with `schema_version = 2`
4. Monitor migration progress

**Risk**: LOW - Background process, doesn't affect active system

### Phase 4: Dual-Read with Fallback

1. Update `get_conversation_messages()` to check `schema_version`
2. Read from conversation_messages for v2, memories for v1
3. Update conversation_compact functions similarly
4. Test extensively with both schemas

**Risk**: MEDIUM - Read path changes, need comprehensive testing

### Phase 5: Deprecate Old Schema

1. After ALL conversations migrated (schema_version = 2)
2. Remove old query code paths
3. Drop `full_conversation_history` column (keep memories table for now)
4. Remove dual-write code

**Risk**: LOW - Only after full migration verified

### Phase 6: Complete Cleanup

1. Optionally drop `memories` table entirely
2. Drop `conversation_compacts` table
3. Remove `schema_version` flag (no longer needed)

**Risk**: LOW - Final cleanup

---

## Testing Requirements

### Unit Tests Needed

1. **Dual-write correctness**
   - Verify both schemas get same data
   - Test transaction rollback
   - Test message_number sequencing

2. **Dual-read correctness**
   - Verify same results from both schemas
   - Test schema_version routing
   - Test fallback behavior

3. **Migration correctness**
   - Verify exact message ordering preserved
   - Test timestamp preservation
   - Test topic link preservation

### Integration Tests Needed

1. **Compacting with new schema**
   - Test 25-message boundary detection
   - Test compact summary update
   - Test conversation_messages range queries

2. **Phase 1 context loading**
   - Test compact + recent messages
   - Test non-overlapping guarantee
   - Test with 3, 25, 50, 100 message conversations

3. **Tool compatibility**
   - Test all 13 memory tools with new schema
   - Test recall functions
   - Test analytics functions

---

## Performance Implications

### Expected Improvements

1. **Storage reduction**: ~93% less data duplication
2. **Query simplification**: Direct range queries vs UNION ALL + Python filtering
3. **Index efficiency**: Simple message_number index for range scans

### Potential Regressions

1. **Write operations**: Two INSERTs instead of one (minor)
2. **Dual-write period**: Temporary write amplification
3. **Migration load**: Background job resource usage

### Mitigation Strategies

1. Use indexed message_number for fast range scans
2. Batch migration during low-traffic periods
3. Monitor query performance before/after migration

---

## Conclusion

**Refactoring Recommendation**: PROCEED with conversation_messages schema

**Key Reasons:**

1. **Data duplication problem is severe** - 93% waste is unsustainable
2. **Good abstraction layers exist** - Most code isolated from schema details
3. **Clear migration path** - Dual-write → background migration → dual-read → cleanup
4. **Significant benefits** - Simpler queries, better performance, cleaner architecture

**Estimated Effort:**
- Schema design: 1-2 hours (mostly done in MEMORY_SYSTEM.md)
- Dual-write implementation: 4-6 hours
- Migration job: 4-6 hours
- Dual-read implementation: 6-8 hours
- Testing: 8-12 hours
- Documentation: 2-4 hours

**Total**: ~25-40 hours of careful implementation

**Risk Level**: MEDIUM - Requires careful testing but has clear rollback path

**Recommendation**: Proceed with phased migration starting with Phase 1 (schema changes only)
