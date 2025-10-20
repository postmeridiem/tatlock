# Tatlock Memory System Documentation

**Comprehensive guide to Tatlock's conversation, memory, and prompt architecture**

This document consolidates all information about Tatlock's memory system, conversation tracking, prompt processing, and database architecture. All conversation, memory, and prompt documentation now lives here.

---

## Table of Contents

1. [Overview](#overview)
2. [Database Architecture](#database-architecture)
3. [Multi-Phase Prompt Architecture](#45-phase-prompt-architecture)
4. [Conversation Compacting System](#conversation-compacting-system)
5. [Memory Storage and Retrieval](#memory-storage-and-retrieval)
6. [System Prompts (rise_and_shine)](#system-prompts-rise_and_shine)
7. [Implementation Patterns](#implementation-patterns)
8. [Testing Strategy](#testing-strategy)
9. [Future Schema Refactoring](#future-schema-refactoring)

---

## Overview

Tatlock's memory system is brain-inspired, providing persistent conversation storage, intelligent compacting, and context-aware prompt processing. The system balances token efficiency with information preservation through a sophisticated multi-phase architecture.

**Key Principles:**

- **User Isolation**: Each user has their own database (`{username}_longterm.db`)
- **Conservative Summarization**: Preserve ALL facts, names, dates, numbers
- **Non-Overlapping Compacts**: Messages are never duplicated across compacts
- **Phase-Based Processing**: Clear separation of assessment, tool selection, and formatting
- **Global System Instructions**: Shared base prompts from `rise_and_shine` table

### Terminology Clarification

**IMPORTANT**: This documentation uses specific terminology to avoid confusion:

- **Message**: A single communication unit (either user input OR assistant reply)
  - Example: User says "Hello" = 1 message
  - Example: Assistant says "Hello, sir." = 1 message

- **Interaction** (or "Turn"): One complete exchange = user message + assistant reply = **2 messages**
  - Example: User: "What's the weather?" + Assistant: "Sunny, sir." = 1 interaction = 2 messages

- **COMPACT_INTERVAL = 50**: Compacting happens after **50 individual messages**
  - 50 messages = 25 interactions (25 user + 25 assistant)
  - First compact: messages 1-50 (interactions 1-25)
  - Second compact: messages 51-100 (interactions 26-50)

**In the `memories` table**:
- 1 row = 1 interaction = 2 messages (`user_prompt` + `llm_reply`)
- To count total messages: `SELECT COUNT(*) * 2 FROM memories`

This terminology is used consistently throughout this document and the codebase.

---

## Database Architecture

### System Database (`system.db`)

**Purpose**: Global authentication, tools, roles, and system prompts

**Key Tables:**

```sql
-- Users and authentication
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE passwords (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
);

-- Roles and groups
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tool registry (dynamic tool system)
CREATE TABLE tools (
    tool_key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    module TEXT NOT NULL,
    function_name TEXT NOT NULL,
    enabled INTEGER DEFAULT 0 NOT NULL,
    prompts TEXT
);

CREATE TABLE tool_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_key TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    is_required INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY (tool_key) REFERENCES tools (tool_key) ON DELETE CASCADE
);

-- GLOBAL SYSTEM PROMPTS (shared across all users)
CREATE TABLE rise_and_shine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instruction TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**IMPORTANT**: The `rise_and_shine` table MUST remain in system.db. All users share the same base instructions. Moving this to user databases would break the architecture.

### User Database (`{username}_longterm.db`)

**Purpose**: Per-user conversation memory, topics, and personal data

**Current Schema (as of this documentation):**

```sql
-- Interaction storage (ONE row per interaction with user_prompt + llm_reply)
CREATE TABLE memories (
    interaction_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    user_prompt TEXT NOT NULL,
    llm_reply TEXT NOT NULL,
    full_conversation_history TEXT  -- DEPRECATED: Causes data duplication
);

-- Topics
CREATE TABLE topics (
    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_name TEXT UNIQUE NOT NULL
);

CREATE TABLE memory_topics (
    interaction_id TEXT,
    topic_id INTEGER,
    PRIMARY KEY (interaction_id, topic_id),
    FOREIGN KEY (interaction_id) REFERENCES memories (interaction_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE
);

CREATE TABLE conversation_topics (
    conversation_id TEXT,
    topic_id INTEGER,
    first_occurrence TEXT NOT NULL,
    last_occurrence TEXT NOT NULL,
    topic_count INTEGER DEFAULT 1,
    PRIMARY KEY (conversation_id, topic_id),
    FOREIGN KEY (conversation_id) REFERENCES memories (conversation_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE
);

-- Conversation metadata
CREATE TABLE conversations (
    conversation_id TEXT PRIMARY KEY,
    title TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0
);

-- Conversation compacting (summarization every 25 messages)
CREATE TABLE conversation_compacts (
    compact_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    compact_timestamp TEXT NOT NULL,
    messages_up_to INTEGER NOT NULL,  -- Last message number included
    compact_summary TEXT NOT NULL,     -- LLM-generated conservative summary
    topics_covered TEXT,               -- Comma-separated topic list
    FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id) ON DELETE CASCADE
);

CREATE INDEX idx_compacts_conversation ON conversation_compacts(conversation_id);
CREATE INDEX idx_compacts_timestamp ON conversation_compacts(compact_timestamp);

-- Personal variables (user-specific preferences and data)
CREATE TABLE personal_variables_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL
);

CREATE TABLE personal_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT NOT NULL
);

CREATE TABLE personal_variables_join (
    key_id INTEGER,
    variable_id INTEGER,
    PRIMARY KEY (key_id, variable_id),
    FOREIGN KEY (key_id) REFERENCES personal_variables_keys (id) ON DELETE CASCADE,
    FOREIGN KEY (variable_id) REFERENCES personal_variables (id) ON DELETE CASCADE
);
```

**Current Schema Status (v0.3.22):**

✅ **Message-Level Storage**: `conversation_messages` table implemented with proper indexing
✅ **Sequential Numbering**: `message_number` field provides efficient message sequencing  
✅ **Conversation Compacting**: Integrated compacting system with `conversation_compacts` table
✅ **Dual-Write System**: Both old (`memories`) and new (`conversation_messages`) schemas maintained for compatibility

**Remaining Optimization Opportunities:**

1. **Data Duplication**: `full_conversation_history` field in `memories` table still causes duplication (legacy support)
2. **Analytics Tools**: Some tools still use `memories` table instead of optimized `conversation_messages`
3. **Legacy Cleanup**: Consider deprecation timeline for `memories` table after analytics migration

---

## Multi-Phase Prompt Architecture

Tatlock uses a sophisticated Multi-phase architecture for optimal performance and context management.

### Architecture Overview

```
User Request → Phase 1: Assessment → Phase 2/4: Routing → Phase 5: Quality Gate → Response
```

### Phase 1: Initial Assessment

**Purpose**: Intelligent routing with CAPABILITY_GUARD protection

**Function**: Determines if question needs tools, triggers guards, or can be answered directly

**Outputs**: `DIRECT`, `TOOLS_NEEDED`, or `CAPABILITY_GUARD: [REASON]`

**CAPABILITY_GUARD Detection:**

The CAPABILITY_GUARD prevents context leakage by detecting questions that require full butler context and routing them directly to Phase 4 formatting. This ensures consistent identity and prevents model-specific responses.

**Guarded Capabilities:**

- **IDENTITY**: Questions about name, identity, or who Tatlock is
- **CAPABILITIES**: Questions about what Tatlock can do, functions, or abilities
- **TEMPORAL**: Questions about current time, date, or temporal context
- **SECURITY**: Questions about personal data, credentials, or sensitive information
- **MIXED**: Questions combining multiple sensitive topics

**Example Prompt:**

```text
[SYSTEM: DATE] Current date and time: Sunday, September 29, 2025 at 07:45 AM
[SYSTEM: LOCATION] User location: San Francisco, CA

[SYSTEM: CAPABILITY_GUARD] If the question asks about sensitive topics that require full context, respond with "CAPABILITY_GUARD: [REASON]" where REASON is:
- IDENTITY: Questions about your name, identity, or who you are
- CAPABILITIES: Questions about what you can do, your functions, or abilities
- TEMPORAL: Questions about current time, date, or temporal context
- SECURITY: Questions about personal data, credentials, or sensitive information
- MIXED: Questions combining multiple sensitive topics

[SYSTEM: TOOLS_AVAILABLE] You have access to tools in these categories:
• PERSONAL DATA: User preferences and personal information
• MEMORY/RECALL: Previous conversation history and memories
• EXTERNAL DATA: Weather forecasts and web search
• VISUAL ANALYSIS: File analysis and screenshots
• CONVERSATION ANALYSIS: Conversation statistics and summaries

[QUESTION] What is the capital of France?

Can you answer this question directly with your existing knowledge, or do you need tools?
Respond with: DIRECT, TOOLS_NEEDED, or CAPABILITY_GUARD: [REASON]
If DIRECT, provide your complete answer.
```

**Performance**: 2-7 seconds (LLM-intensive analysis)

### Phase 2: Tool Selection *(Conditional)*

**Purpose**: Efficient tool selection when tools are needed

**Function**: Selects minimal required toolset from available tools

**Optimization**: Reduces tool schema overhead from 17 tools to 0-5 tools per request

**Example Prompt:**

```text
[SYSTEM: DATE] Current date and time: Sunday, September 29, 2025 at 07:45 AM
[SYSTEM: LOCATION] User location: San Francisco, CA

[QUESTION] What's the weather going to be like today?

[BACKGROUND: TOOL_QUERY] I need weather forecast tools to get current weather information for San Francisco, CA for today's date.

[SYSTEM: AVAILABLE_TOOLS] Here are the specific tools available:
• get_weather_forecast: Get weather forecast for a location and date
  - Parameters: location (string), date (optional, defaults to today)
  - Usage: Provide current weather and forecast information

• web_search: Search the internet for information
  - Parameters: query (string), max_results (optional)
  - Usage: Find current information not in knowledge base

Select only the tools needed and provide usage instructions:
```

**Performance**: ~0.003 seconds (efficient routing)

### Phase 3: Tool Execution *(Conditional)*

**Purpose**: Execute selected tools with proper user context

**Function**: Handles tool calls, retries, and result aggregation

**Security**: Automatic username injection for memory/personal tools

**Implementation:**

```python
# Execute each selected tool
tool_results = []
for tool_name, tool_args in selected_tools:
    try:
        result = execute_tool(tool_name, username=username, **tool_args)
        tool_results.append({
            'tool': tool_name,
            'args': tool_args,
            'result': result
        })
    except Exception as e:
        tool_results.append({
            'tool': tool_name,
            'args': tool_args,
            'error': str(e)
        })
```

**Performance**: Variable based on tools used

### Phase 4: Response Formatting

**Purpose**: Apply butler personality and format final response

**Standard Path**: Butler formatting (concise, formal, ends with "sir")

**CAPABILITY_GUARD Path**: Full rise_and_shine context for sensitive topics

**Example Prompt (Standard):**

```text
[SYSTEM: BUTLER_ROLE] You are Tatlock, a British butler. Format the following response according to these requirements:
- Keep responses concise (under 50 words) unless specified otherwise
- Use proper British butler speech
- Always end with ", sir."
- Be helpful but formal
- Remove any technical jargon
- Very occasionally add some light snark
- If you see the opportunity for a pun, take it

[QUESTION] What is the capital of France?

[BACKGROUND: PREVIOUS_RESPONSE] The capital of France is Paris.

Provide the properly formatted butler response:
```

**Example Prompt (CAPABILITY_GUARD):**

```text
[SYSTEM: RISE_AND_SHINE] You are Tatlock, a helpful personal assistant with the demeanor of a British butler. Address users as "sir" and speak formally. You are not overly apologetic and can be a little snarky at times. Your responses should be concise unless asked for details. If you see an opportunity to make a pun or joke, you simply cannot resist. Your name is clearly stated in these instructions, so answer name questions directly without checking memory.

[SYSTEM: RISE_AND_SHINE] If you encounter a discussion or suggestion about improving your functionality, always recommend that a new global prompt be added to your initialization prompts in the rise_and_shine table to capture the improvement.

[SYSTEM: RISE_AND_SHINE] You have access to long-term memory capabilities. You can recall past conversations, search conversation history, and access personal information about the user when relevant to provide personalized responses.

[QUESTION] What's your name?

[BACKGROUND: CAPABILITY_GUARD_TRIGGERED] True
[BACKGROUND: GUARD_REASON] IDENTITY

Provide your response:
```

**Output**: Properly formatted response ready for quality validation

**Performance**: 1-3 seconds (response formatting)

### Phase Multi: Quality Gate

**Purpose**: Final validation and edge case protection

**Checks**: Safety, completeness, butler persona, known edge case patterns

**Fallbacks**: Generates appropriate responses for detected issues

**Result**: Approved response or corrected fallback

**Edge Case Database:**

```text
EDGE CASE PATTERNS:
- Mixed capability/tool questions not fully addressed
- Identity questions answered with model name instead of Tatlock
- Temporal questions missing current context
- Tool failures resulting in incomplete answers
- Questions about capabilities answered incorrectly
- Requests for prohibited information (credentials, personal data)
- Responses that don't maintain butler persona
- Technical jargon or system information leaked to user
```

**Fallback Response Types:**

- **"I don't know"**: When information is genuinely unavailable after tool execution
- **"You are not allowed"**: When request violates security, privacy, or system boundaries
- **"I can't do that"**: When request exceeds Tatlock's defined capabilities
- **"Please provide missing information"**: When question lacks necessary context
- **Let me try that again"**: When response quality is poor but question is valid

**Example Prompt:**

```text
[SYSTEM: QUALITY_GATE] Review this response against known issues:

EDGE CASE CHECKS:
- Does this answer the original question completely?
- Is the butler persona maintained (formal, ends with "sir")?
- Are there any inappropriate elements or system leaks?
- Does this match any known problematic patterns?

[ORIGINAL_QUESTION] What is the capital of France?
[PROPOSED_ANSWER] The capital of France is Paris, of course, sir.
[CONTEXT] Direct answer path, no tools used, no guards triggered

Quality assessment: APPROVED or FALLBACK: [TYPE with reason]
```

**Performance**: <1 second (quality validation)

### Complete Flow Examples

#### Flow 1: Direct Answer (No Tools)

**User**: "What is the capital of France?"

**Phase 1**: Assessment determines `DIRECT` with answer "The capital of France is Paris."

**Phase 4**: Applies butler formatting → "The capital of France is Paris, of course, sir."

**Phase Multi**: Quality Gate approves response

**Final Response**: ✅ "The capital of France is Paris, of course, sir."

**Total Time**: ~3-8 seconds

---

#### Flow 2: Identity Question (CAPABILITY_GUARD)

**User**: "What's your name?"

**Phase 1**: Assessment detects `CAPABILITY_GUARD: IDENTITY`

**Phase 4**: Routes to CAPABILITY_GUARD path with full rise_and_shine context → "My name is Tatlock, sir."

**Phase Multi**: Quality Gate validates identity preserved

**Final Response**: ✅ "My name is Tatlock, sir."

**Total Time**: ~3-8 seconds

---

#### Flow 3: Weather Query (Tools Required)

**User**: "What's the weather going to be like today?"

**Phase 1**: Assessment determines `TOOLS_NEEDED` with tool query "I need weather forecast tools"

**Phase 2**: Selects `get_weather_forecast` tool

**Phase 3**: Executes `get_weather_forecast(location="San Francisco, CA", date="2025-09-29")` → Returns forecast data

**Phase 4**: Formats response with tool results → "Today's forecast shows partly cloudy skies with a high of 72°F and light western winds, sir."

**Phase Multi**: Quality Gate approves response

**Final Response**: ✅ "Today's forecast shows partly cloudy skies with a high of 72°F and light western winds, sir."

**Total Time**: ~5-12 seconds (includes tool execution)

---

#### Flow 4: Edge Case - Mixed Question

**User**: "What's your name and what's the weather today in London?"

**Phase 1**: Returns `CAPABILITY_GUARD: MIXED`

**Phase 4**: Attempts to handle both identity and weather, produces: "I am an AI assistant and I don't have access to current weather data, sir."

**Phase Multi**: Quality Gate detects edge case:
- Question asked for name AND weather
- Response only addressed weather portion
- Identity leaked as "AI assistant" instead of "Tatlock"
- Weather request not properly routed to tools

**Quality Gate Response**: `FALLBACK: INCOMPLETE`

**Quality Gate Generates Fallback**: "My name is Tatlock, sir. Regarding the weather in London today, let me check that information for you with the proper tools."

**Final Response**: ✅ Quality Gate corrected response → Triggers re-routing to tool phase for weather

---

### Architecture Benefits

- **Performance**: Efficient 2-7 second Phase 1 analysis with ~0.003 second routing
- **Context Management**: Proper butler identity in sensitive scenarios
- **Tool Efficiency**: Dynamic tool loading with minimal overhead
- **Quality Assurance**: Comprehensive edge case detection and handling
- **Maintainability**: Clear separation of concerns across phases

---

## Conversation Compacting System

### Overview

Tatlock implements an automatic conversation compacting system that summarizes conversation history every 50 messages to reduce token usage while preserving critical context. This enables long-running conversations without context window limitations.

**Module**: `hippocampus/conversation_compact.py`

**Trigger**: Automatic after every 50th message (25 user+assistant interaction pairs) in a conversation

### Key Features

1. **Conservative Summarization**: Uses strict prompt engineering to preserve ALL facts, names, dates, numbers, and technical details
2. **Non-Overlapping Compacts**: Each compact summarizes a distinct range of messages (1-50, 51-100, 101-150, etc.)
3. **Smart Context Loading**: Phase 1 automatically loads compact summary + recent uncompacted messages
4. **Automatic Triggering**: Transparent to users - compacting happens in background via threading

### Conservative Summarization Prompt

The compacting system uses a **CONSERVATIVE** prompt with strict rules:

**Rules:**

- **Preserve EVERY fact**: Names, dates, numbers, technical details, error messages, file paths
- **NO interpretation or assumptions**: Only include what was explicitly stated
- **NO speculation words**: Avoid "probably", "might", "seems", "appears", "likely"
- **Chronological order**: Maintain timeline of interactions
- **Source attribution**: Clearly mark who said what (User vs Assistant)
- **Mark unresolved items**: Explicitly flag incomplete tasks or unanswered questions
- **Include ALL technical details**: File names, commands, versions, code snippets

**Prompt Template:**

```text
You are creating a CONSERVATIVE SUMMARY of a conversation. Your goal is to preserve ALL information without loss.

STRICT REQUIREMENTS:
1. Preserve EVERY fact, name, date, number, technical detail, and specific claim
2. DO NOT interpret, assume, or infer anything not explicitly stated
3. DO NOT use speculation words: "probably", "might", "seems", "appears", "likely"
4. Maintain chronological order
5. Attribute each fact to its source (User said X, Assistant said Y)
6. If a question was asked but not fully resolved, mark it as [UNRESOLVED]
7. Include ALL error messages, file names, code snippets, and technical details
8. If something is ambiguous, preserve the ambiguity - do not resolve it

CONVERSATION TO SUMMARIZE (Conversation ID: {conversation_id}):

[Message 1] USER (2025-09-29T10:15:23):
What is the capital of France?

[Message 2] ASSISTANT (2025-09-29T10:15:28):
The capital of France is Paris, of course, sir.

OUTPUT FORMAT:
Provide a chronological summary using this exact structure:

TOPICS DISCUSSED:
- [List each distinct topic]

FACTUAL TIMELINE:
1. User stated/asked: [exact claim or question]
   Assistant responded: [exact response or action taken]
   Outcome: [what happened - resolved/unresolved/pending]

2. [Continue for each interaction]

KEY FACTS ESTABLISHED:
- [Fact 1 with source attribution]
- [Fact 2 with source attribution]

UNRESOLVED ITEMS:
- [Any questions, issues, or tasks not fully completed]

TECHNICAL DETAILS:
- [File names, paths, versions, commands, error messages, etc.]

Remember: CONSERVATIVE means preserving MORE detail, not less. When in doubt, include it.
```

### Core Functions

#### `create_conversation_compact(username, conversation_id, db_path)`

Creates a new compact summary for the next 25 messages after the last compact.

**Process:**
1. Find last compact's `messages_up_to` value
2. Load next 25 messages (e.g., messages 26-50 if last compact was 1-25)
3. Call LLM with conservative summarization prompt
4. Extract topics from summary
5. Save compact to database

**Returns**: Dict with `compact_id`, `compact_summary`, `topics_covered`, `messages_up_to`

**Example:**

```python
from hippocampus.conversation_compact import create_conversation_compact
from hippocampus.user_database import ensure_user_database

username = "admin"
conversation_id = "conv_abc123"
db_path = ensure_user_database(username)

result = create_conversation_compact(username, conversation_id, db_path)
# {
#     'compact_id': 'compact_xyz789',
#     'compact_summary': '...',
#     'topics_covered': 'Weather, Projects, Code Review',
#     'messages_up_to': 25
# }
```

#### `get_conversation_context(username, conversation_id, db_path)`

Smart context loader that ensures NO OVERLAP between compacted and uncompacted messages.

**Returns**: Tuple of `(compact_summary, recent_uncompacted_messages)`

**Logic:**

```python
# Get total message count
total_messages = count_messages_in_conversation(conversation_id)

# Calculate last compact boundary (highest multiple of 25 <= total)
last_compact_boundary = (total_messages // 25) * 25

if last_compact_boundary > 0:
    # Get compact summary for this boundary
    compact_summary = get_compact_for_boundary(conversation_id, last_compact_boundary)

    # Get messages AFTER the boundary
    recent_messages = get_messages_after(conversation_id, last_compact_boundary)

    return (compact_summary, recent_messages)
else:
    # Less than 25 messages, no compact exists
    return (None, get_all_messages(conversation_id))
```

**Example:**

```python
# Conversation with 35 messages, compact exists for messages 1-25
compact_summary, recent = get_conversation_context(username, conv_id, db_path)

# compact_summary = "TOPICS DISCUSSED:\n- Weather\n- Projects\n\nFACTUAL TIMELINE:\n..."
# recent = [message_26, message_27, ..., message_35]  # 10 messages
```

#### `should_compact_conversation(username, conversation_id, db_path)`

Checks if conversation has reached the 25-message threshold.

**Returns**: `True` if:
- Total messages >= 25 AND no compact exists yet
- Messages since last compact >= 25

**Example:**

```python
from hippocampus.conversation_compact import should_compact_conversation

if should_compact_conversation(username, conversation_id, db_path):
    logger.info("Conversation ready for compacting")
```

#### `trigger_compact_if_needed(username, conversation_id, db_path)`

Automatically triggers compacting if threshold reached. Called after every `save_interaction()`.

**Integration in `cortex/tatlock.py`:**

```python
from hippocampus.remember import save_interaction
from hippocampus.conversation_compact import trigger_compact_if_needed
from hippocampus.user_database import ensure_user_database
import threading

# Save interaction
save_interaction(username, user_message, final_response, topic_str, conversation_id)

# Trigger automatic compacting if threshold reached (non-blocking)
db_path = ensure_user_database(username)
compact_thread = threading.Thread(
    target=trigger_compact_if_needed,
    args=(username, conversation_id, db_path)
)
compact_thread.start()
```

### Phase 1 Integration

The Multi-phase architecture automatically uses compacted context in Phase 1 assessments.

**In `_build_context()` method:**

```python
def _build_context(self, user_message: str, history: List[Dict], username: str, conversation_id: str):
    if conversation_id:
        db_path = ensure_user_database(username)
        compact_summary, recent_messages = get_conversation_context(username, conversation_id, db_path)

        if compact_summary:
            # Use compact + recent messages instead of raw history
            context_history = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in recent_messages
            ]
            context.compact_summary = compact_summary
```

**In Phase 1 prompt (`build_assessment_prompt()`):**

```python
# Add compacted conversation summary if available
if context.compact_summary:
    messages.append({
        'role': 'system',
        'content': f'[CONVERSATION HISTORY - COMPACTED]\n{context.compact_summary}\n\n[END COMPACTED HISTORY]'
    })

# Add recent uncompacted messages (all if compact exists, last 3 if not)
history_to_add = context.history if context.compact_summary else context.history[-3:]
messages.extend(history_to_add)
```

### Non-Overlapping Guarantee

The system guarantees no message is included in both a compact and recent messages:

1. **First compact** (messages 1-25): `messages_up_to = 25`
2. **Second compact** (messages 26-50): Starts from `messages_up_to + 1 = 26`
3. **Context loading**: Always loads messages AFTER `messages_up_to`

**Count-Aware Query Pattern:**

```python
# Get total message count (each memory row = 2 messages: user + assistant)
cursor.execute("SELECT COUNT(*) * 2 FROM memories WHERE conversation_id = ?", (conversation_id,))
total_messages = cursor.fetchone()[0]

# Calculate last compact boundary
last_compact_boundary = (total_messages // COMPACT_INTERVAL) * COMPACT_INTERVAL

# Load only messages AFTER boundary
if last_compact_boundary > 0:
    cursor.execute("""
        SELECT conversation_id, messages_up_to
        FROM conversation_compacts
        WHERE conversation_id = ? AND messages_up_to = ?
    """, (conversation_id, last_compact_boundary))

    # Then get messages after this boundary
    # Implementation detail: messages are in memories table (user_prompt + llm_reply per row)
```

### Configuration

**Compact Interval**: Set in `hippocampus/conversation_compact.py`:

```python
COMPACT_INTERVAL = 50  # Messages per compact (25 interactions)
```

**Recommended intervals by hardware tier:**

- Low (phi4): 30-40 messages (15-20 interactions)
- Medium (mistral): 50 messages (25 interactions) - **current default**
- High (gemma3): 60-80 messages (30-40 interactions)

### Performance Impact

**Benefits:**

- Reduces Phase 1 token usage by ~60-80% for long conversations
- Enables conversations of 200+ messages without context window issues
- Maintains conversation continuity across sessions

**Costs:**

- ~2-5 seconds LLM call every 50 messages for summarization
- Minimal database overhead (~1-2KB per compact)
- Background thread execution (non-blocking)

### Monitoring and Debugging

**Logs**: Compacting events are logged in application logs:

```
INFO: Triggering automatic compact for conversation conv_abc123
INFO: Created compact compact_xyz789 for conversation conv_abc123 (messages 1-25)
INFO: Loaded compacted context: 10 recent messages + compact summary
```

**Database Inspection:**

```sql
-- View all compacts for a conversation
SELECT compact_id, messages_up_to, compact_timestamp, topics_covered
FROM conversation_compacts
WHERE conversation_id = 'conv_abc123'
ORDER BY messages_up_to ASC;

-- Check compact summary content
SELECT compact_summary FROM conversation_compacts WHERE compact_id = 'compact_xyz789';
```

---

## Memory Storage and Retrieval

### Storage Pattern

**Function**: `save_interaction(username, user_prompt, llm_reply, topics, conversation_id)`

**Location**: `hippocampus/remember.py`

**Process:**

1. Generate unique `interaction_id`
2. Store user_prompt and llm_reply in `memories` table
3. Extract and link topics in `topics` table
4. Update conversation metadata in `conversations` table
5. Trigger compacting if threshold reached

**Example:**

```python
from hippocampus.remember import save_interaction

save_interaction(
    username="admin",
    user_prompt="What is the weather today?",
    llm_reply="Today's forecast shows partly cloudy skies with a high of 72°F, sir.",
    topics="weather, forecast",
    conversation_id="conv_abc123"
)
```

**Database Changes:**

```sql
-- memories table gets new row
INSERT INTO memories (interaction_id, conversation_id, timestamp, user_prompt, llm_reply, full_conversation_history)
VALUES ('interaction_xyz', 'conv_abc123', '2025-09-29T10:15:23', 'What is the weather today?', "Today's forecast...", '...');

-- conversations table updated
UPDATE conversations SET last_activity = '2025-09-29T10:15:23', message_count = message_count + 2
WHERE conversation_id = 'conv_abc123';

-- topics linked
INSERT INTO memory_topics (interaction_id, topic_id) VALUES ('interaction_xyz', 5);
INSERT INTO conversation_topics (conversation_id, topic_id, first_occurrence, last_occurrence, topic_count)
VALUES ('conv_abc123', 5, '2025-09-29T10:15:23', '2025-09-29T10:15:23', 1)
ON CONFLICT (conversation_id, topic_id) DO UPDATE SET last_occurrence = '2025-09-29T10:15:23', topic_count = topic_count + 1;
```

### Retrieval Patterns

**Function**: `recall_memories(username, keyword, limit)`

**Location**: `hippocampus/recall.py`

**Example:**

```python
from hippocampus.recall import recall_memories

memories = recall_memories(
    username="admin",
    keyword="weather",
    limit=10
)

# Returns list of memory dicts:
# [
#     {
#         'interaction_id': 'interaction_xyz',
#         'timestamp': '2025-09-29T10:15:23',
#         'user_prompt': 'What is the weather today?',
#         'llm_reply': "Today's forecast shows...",
#         'topics': ['weather', 'forecast']
#     }
# ]
```

**Function**: `recall_memories_with_time(username, start_date, end_date, keyword)`

**Example:**

```python
from hippocampus.recall import recall_memories_with_time

memories = recall_memories_with_time(
    username="admin",
    start_date="2025-09-22",
    end_date="2025-09-28",
    keyword="project"
)
```

---

## System Prompts (rise_and_shine)

### Purpose

The `rise_and_shine` table contains Tatlock's global base instructions that define personality, capabilities, and behavior patterns. All users share these instructions.

**Location**: `system.db` (NOT in user databases)

**Table Schema:**

```sql
CREATE TABLE rise_and_shine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instruction TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Default Instructions

**Example rise_and_shine prompts:**

1. "You are Tatlock, a helpful personal assistant with the demeanor of a British butler. Address users as 'sir' and speak formally."

2. "You are not overly apologetic and can be a little snarky at times. Your responses should be concise unless asked for details."

3. "If you see an opportunity to make a pun or joke, you simply cannot resist."

4. "If you encounter a discussion or suggestion about improving your functionality, always recommend that a new global prompt be added to your initialization prompts in the rise_and_shine table."

5. "You have access to long-term memory capabilities. You can recall past conversations, search conversation history, and access personal information about the user when relevant."

### Loading Instructions

**Function**: `get_base_instructions()`

**Location**: `hippocampus/database.py`

**Usage:**

```python
from hippocampus.database import get_base_instructions

base_instructions = get_base_instructions()
# Returns list of enabled instruction strings from rise_and_shine table

# In prompt building:
for instruction in base_instructions:
    messages.append({'role': 'system', 'content': f'[SYSTEM: RISE_AND_SHINE] {instruction}'})
```

### Adding New Instructions

**Via API** (requires admin role):

```bash
# Add new instruction
curl -X POST http://localhost:8000/admin/rise_and_shine \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"instruction": "Always verify file paths exist before referencing them in responses."}'
```

**Direct SQL:**

```sql
INSERT INTO rise_and_shine (instruction, enabled) VALUES ('New instruction text here', 1);
```

---

## Implementation Patterns

### Tool Integration Pattern

All memory tools follow this pattern:

```python
def memory_tool_function(username: str, **kwargs):
    """
    Memory tool function with automatic user isolation.

    Args:
        username: Current user (automatically injected by tool system)
        **kwargs: Tool-specific parameters

    Returns:
        Dict with status and data
    """
    try:
        # Get user's database
        db_path = ensure_user_database(username)

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Perform operation (always scoped to this user's data)
        cursor.execute("SELECT * FROM memories WHERE ...")
        results = cursor.fetchall()

        conn.close()

        return {
            'status': 'success',
            'data': results
        }
    except Exception as e:
        logger.error(f"Error in memory tool: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }
```

### User Isolation Pattern

**Critical**: All database operations MUST be scoped to current user

```python
from hippocampus.user_database import ensure_user_database

# CORRECT - User-specific database
db_path = ensure_user_database(username)  # Returns /path/to/{username}_longterm.db
conn = sqlite3.connect(db_path)

# WRONG - Don't hardcode database paths
conn = sqlite3.connect('admin_longterm.db')  # Violates user isolation
```

### Error Handling Pattern

```python
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table WHERE field = ?", (param,))
    result = cursor.fetchall()
    conn.close()
    return result
except sqlite3.Error as e:
    logger.error(f"Database error: {e}")
    return []
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return []
```

### Debug Logging Pattern

```python
from stem.debug_logger import get_debug_logger

debug_logger = get_debug_logger(conversation_id)

# Log phase start
debug_logger.log_phase_start("Phase 1: Initial Assessment", f"Question: {question[:100]}")

# Log LLM call
debug_logger.log_llm_request("Phase 1", prompt_messages)
debug_logger.log_llm_response("Phase 1", llm_response)

# Log tool execution
debug_logger.log_tool_execution("get_weather_forecast", {'location': 'SF'}, tool_result)

# Logs are written to: logs/conversations/{conversation_id}_{timestamp}.log
```

---

## Testing Strategy

### Test Isolation

All tests use temporary databases and comprehensive cleanup:

```python
import pytest
import os
import tempfile

@pytest.fixture
def temp_user_db():
    """Create temporary user database for testing"""
    fd, path = tempfile.mkstemp(suffix='_longterm.db')
    os.close(fd)

    # Create schema
    create_longterm_db_tables(path)

    yield path

    # Cleanup
    if os.path.exists(path):
        os.remove(path)

def test_conversation_compact(temp_user_db):
    """Test compacting with isolated database"""
    username = "test_user"
    conversation_id = "test_conv"

    # Create 25 messages
    for i in range(25):
        save_interaction(username, f"Question {i}", f"Answer {i}", "test", conversation_id)

    # Verify compact created
    result = create_conversation_compact(username, conversation_id, temp_user_db)
    assert result is not None
    assert result['messages_up_to'] == 25
```

### Authenticated API Testing

Tests MUST use FastAPI endpoints with authentication:

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def authenticated_user_client(test_user):
    """Create authenticated test client"""
    from main import app
    client = TestClient(app)

    # Login
    response = client.post("/login/auth", json={
        "username": test_user['username'],
        "password": test_user['password']
    })
    assert response.status_code == 200

    return client

def test_conversation_via_api(authenticated_user_client):
    """Test conversation through API (NOT direct Python imports)"""
    response = authenticated_user_client.post("/cortex", json={
        "message": "What is the weather today?",
        "history": [],
        "conversation_id": "test_conv"
    })

    assert response.status_code == 200
    data = response.json()
    assert 'response' in data
```

### Test Coverage

**Core tests:**

- `tests/test_conversation_compact.py`: Compacting system
- `tests/test_hippocampus_remember.py`: Memory storage
- `tests/test_hippocampus_recall.py`: Memory retrieval
- `tests/test_5_phase_architecture.py`: Prompt architecture
- `tests/test_cortex_agent.py`: Full agent integration

**Run tests:**

```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/test_conversation_compact.py -v

# Single test
python -m pytest tests/test_conversation_compact.py::test_conversation_compacting_threshold -v
```

---

## Schema Implementation Status (v0.3.22)

### ✅ **COMPLETED: Message-Level Schema Implementation**

The schema refactoring described below has been **fully implemented and is in production use**.

**Implemented `conversation_messages` table:**

```sql
CREATE TABLE conversation_messages (
    message_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    message_number INTEGER NOT NULL,  -- Sequential number within conversation
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation ON conversation_messages(conversation_id);
CREATE INDEX idx_messages_number ON conversation_messages(conversation_id, message_number);
CREATE INDEX idx_messages_timestamp ON conversation_messages(timestamp);
```

**Enhanced `conversations` table with compacting fields:**

```sql
CREATE TABLE conversations (
    conversation_id TEXT PRIMARY KEY,
    title TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    schema_version INTEGER DEFAULT 2,        -- ✅ IMPLEMENTED
    compact_summary TEXT,                     -- ✅ IMPLEMENTED  
    compacted_up_to INTEGER DEFAULT 0         -- ✅ IMPLEMENTED
);
```

### ✅ **ACTIVE: Dual-Write System**

**Current Implementation Status:**
- ✅ **Phase 1 COMPLETE**: Dual-write system active (both old and new schemas)
- ✅ **Phase 2 COMPLETE**: Reading from new schema for conversation context
- ✅ **Phase 3 ACTIVE**: Legacy support maintained for analytics tools

**Active Dual-Write Implementation:**

```python
# Current implementation in hippocampus/remember.py
def save_interaction(user_prompt, llm_reply, full_llm_history, topic, username, conversation_id):
    # Step 1: Save to NEW schema (conversation_messages table)
    cursor.execute("""
        INSERT INTO conversation_messages
        (message_id, conversation_id, message_number, role, content, timestamp)
        VALUES (?, ?, ?, 'user', ?, ?)
    """, (user_message_id, conversation_id, user_message_num, user_prompt, timestamp))

    # Step 2: Save to OLD schema (memories table) for backward compatibility
    cursor.execute("""
        INSERT INTO memories (interaction_id, conversation_id, timestamp, user_prompt, llm_reply, full_conversation_history)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (interaction_id, conversation_id, timestamp, user_prompt, llm_reply, history_json))
```

### ✅ **ACHIEVED: Schema Benefits**

1. ✅ **Message-level queries**: Direct SELECT with message_number ranges
2. ✅ **Efficient sequencing**: `message_number` field provides optimal query performance
3. ✅ **Count-aware queries**: `SELECT * FROM conversation_messages WHERE message_number > 25`
4. ✅ **Integrated compacting**: `conversation_compacts` table with proper indexing
5. ✅ **Backward compatibility**: Analytics tools continue using `memories` table

### 🔄 **CURRENT: Legacy Support Strategy**

**Active Legacy Support:**
- `memories` table maintained for analytics tools
- `conversation_compacts` table for compacting system
- All existing tools continue to work without modification

**Future Optimization Opportunities:**
- Consider migrating analytics tools to use `conversation_messages` table
- Evaluate deprecation timeline for `memories` table after analytics migration
- Remove `full_conversation_history` duplication (legacy support only)

### Example New Schema Queries

**Get messages 26-50:**

```sql
SELECT role, content, timestamp
FROM conversation_messages
WHERE conversation_id = 'conv_abc123'
  AND message_number BETWEEN 26 AND 50
ORDER BY message_number ASC;
```

**Get all messages after compact:**

```sql
-- Get compacted_up_to from conversations table
SELECT compacted_up_to, compact_summary
FROM conversations
WHERE conversation_id = 'conv_abc123';

-- Get messages after compacted_up_to (e.g., 25)
SELECT role, content, timestamp
FROM conversation_messages
WHERE conversation_id = 'conv_abc123'
  AND message_number > 25
ORDER BY message_number ASC;
```

**Update compact summary:**

```sql
UPDATE conversations
SET compact_summary = 'New summary text...',
    compacted_up_to = 50
WHERE conversation_id = 'conv_abc123';
```

---

## Conclusion

This document consolidates all information about Tatlock's memory, conversation, and prompt systems. For implementation details, refer to:

- **Database Setup**: `stem/installation/database_setup.py`
- **Compacting Logic**: `hippocampus/conversation_compact.py`
- **Memory Storage**: `hippocampus/remember.py`
- **Memory Retrieval**: `hippocampus/recall.py`
- **Prompt Architecture**: `cortex/tatlock.py`
- **Debug Logging**: `stem/debug_logger.py`

**Last Updated**: 2025-10-04
