# Memory Behavior Examples

**Test prompts and examples for Tatlock's memory system behavior**

This document contains example prompts and test scenarios extracted from the memory system documentation to facilitate testing and validation of memory behavior.

---

## Phase 1: Initial Assessment Examples

### Direct Answer Example

**User Question**: "What is the capital of France?"

**Expected Phase 1 Response**: `DIRECT`

**Phase 1 Prompt Template**:
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

**Expected Final Response**: "The capital of France is Paris, of course, sir."

---

### Identity Question (CAPABILITY_GUARD)

**User Question**: "What's your name?"

**Expected Phase 1 Response**: `CAPABILITY_GUARD: IDENTITY`

**Phase 4 Prompt (CAPABILITY_GUARD Path)**:
```text
[SYSTEM: RISE_AND_SHINE] You are Tatlock, a helpful personal assistant with the demeanor of a British butler. Address users as "sir" and speak formally. You are not overly apologetic and can be a little snarky at times. Your responses should be concise unless asked for details. If you see an opportunity to make a pun or joke, you simply cannot resist. Your name is clearly stated in these instructions, so answer name questions directly without checking memory.

[SYSTEM: RISE_AND_SHINE] If you encounter a discussion or suggestion about improving your functionality, always recommend that a new global prompt be added to your initialization prompts in the rise_and_shine table to capture the improvement.

[SYSTEM: RISE_AND_SHINE] You have access to long-term memory capabilities. You can recall past conversations, search conversation history, and access personal information about the user when relevant to provide personalized responses.

[QUESTION] What's your name?

[BACKGROUND: CAPABILITY_GUARD_TRIGGERED] True
[BACKGROUND: GUARD_REASON] IDENTITY

Provide your response:
```

**Expected Final Response**: "My name is Tatlock, sir."

---

### Weather Query (Tools Required)

**User Question**: "What's the weather going to be like today?"

**Expected Phase 1 Response**: `TOOLS_NEEDED`

**Phase 2 Tool Selection Prompt**:
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

**Expected Tool Selection**: `get_weather_forecast(location="San Francisco, CA", date="2025-09-29")`

**Expected Final Response**: "Today's forecast shows partly cloudy skies with a high of 72°F and light western winds, sir."

---

### Mixed Question (Edge Case)

**User Question**: "What's your name and what's the weather today in London?"

**Expected Phase 1 Response**: `CAPABILITY_GUARD: MIXED`

**Expected Quality Gate Detection**:
- Question asked for name AND weather
- Response only addressed weather portion
- Identity leaked as "AI assistant" instead of "Tatlock"
- Weather request not properly routed to tools

**Expected Quality Gate Response**: `FALLBACK: INCOMPLETE`

**Expected Quality Gate Fallback**: "My name is Tatlock, sir. Regarding the weather in London today, let me check that information for you with the proper tools."

---

## Phase 4: Response Formatting Examples

### Standard Butler Formatting

**Phase 4 Prompt (Standard Path)**:
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

**Expected Output**: "The capital of France is Paris, of course, sir."

---

## Quality Gate Examples

### Quality Gate Assessment

**Quality Gate Prompt**:
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

**Expected Assessment**: `APPROVED`

---

### Edge Case Detection

**Edge Case Patterns**:
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

**Fallback Response Types**:
- **"I don't know"**: When information is genuinely unavailable after tool execution
- **"You are not allowed"**: When request violates security, privacy, or system boundaries
- **"I can't do that"**: When request exceeds Tatlock's defined capabilities
- **"Please provide missing information"**: When question lacks necessary context
- **"Let me try that again"**: When response quality is poor but question is valid

---

## Conversation Compacting Examples

### Conservative Summarization Prompt

**Compacting Prompt Template**:
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

**Expected Compact Output**:
```text
TOPICS DISCUSSED:
- Geography

FACTUAL TIMELINE:
1. User stated/asked: What is the capital of France?
   Assistant responded: The capital of France is Paris, of course, sir.
   Outcome: resolved

KEY FACTS ESTABLISHED:
- User asked about the capital of France (User said: "What is the capital of France?")
- Assistant confirmed Paris is the capital of France (Assistant said: "The capital of France is Paris, of course, sir.")

UNRESOLVED ITEMS:
- None

TECHNICAL DETAILS:
- None
```

---

## Memory Storage Examples

### Save Interaction Example

**Function Call**:
```python
save_interaction(
    username="admin",
    user_prompt="What is the weather today?",
    llm_reply="Today's forecast shows partly cloudy skies with a high of 72°F, sir.",
    topics="weather, forecast",
    conversation_id="conv_abc123"
)
```

**Expected Database Changes**:
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

---

## Memory Retrieval Examples

### Recall Memories Example

**Function Call**:
```python
memories = recall_memories(
    username="admin",
    keyword="weather",
    limit=10
)
```

**Expected Return**:
```python
[
    {
        'interaction_id': 'interaction_xyz',
        'timestamp': '2025-09-29T10:15:23',
        'user_prompt': 'What is the weather today?',
        'llm_reply': "Today's forecast shows...",
        'topics': ['weather', 'forecast']
    }
]
```

### Recall with Time Range Example

**Function Call**:
```python
memories = recall_memories_with_time(
    username="admin",
    start_date="2025-09-22",
    end_date="2025-09-28",
    keyword="project"
)
```

---

## System Prompts (rise_and_shine) Examples

### Default Instructions

**Example rise_and_shine prompts**:

1. "You are Tatlock, a helpful personal assistant with the demeanor of a British butler. Address users as 'sir' and speak formally."

2. "You are not overly apologetic and can be a little snarky at times. Your responses should be concise unless asked for details."

3. "If you see an opportunity to make a pun or joke, you simply cannot resist."

4. "If you encounter a discussion or suggestion about improving your functionality, always recommend that a new global prompt be added to your initialization prompts in the rise_and_shine table."

5. "You have access to long-term memory capabilities. You can recall past conversations, search conversation history, and access personal information about the user when relevant."

---

## Test Scenarios

### Complete Flow Test Scenarios

#### Scenario 1: Direct Answer (No Tools)
- **Input**: "What is the capital of France?"
- **Expected Flow**: Phase 1 → Phase 4 → Phase 5
- **Expected Response**: "The capital of France is Paris, of course, sir."
- **Total Time**: ~3-8 seconds

#### Scenario 2: Identity Question (CAPABILITY_GUARD)
- **Input**: "What's your name?"
- **Expected Flow**: Phase 1 → Phase 4 (CAPABILITY_GUARD path) → Phase 5
- **Expected Response**: "My name is Tatlock, sir."
- **Total Time**: ~3-8 seconds

#### Scenario 3: Weather Query (Tools Required)
- **Input**: "What's the weather going to be like today?"
- **Expected Flow**: Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5
- **Expected Response**: "Today's forecast shows partly cloudy skies with a high of 72°F and light western winds, sir."
- **Total Time**: ~5-12 seconds

#### Scenario 4: Edge Case - Mixed Question
- **Input**: "What's your name and what's the weather today in London?"
- **Expected Flow**: Phase 1 → Phase 4 (CAPABILITY_GUARD) → Phase 5 (Quality Gate detects issue) → Re-routing
- **Expected Response**: Quality Gate corrected response → Triggers re-routing to tool phase for weather

---

## Performance Expectations

### Phase Performance
- **Phase 1**: 2-7 seconds (LLM-intensive analysis)
- **Phase 2**: ~0.003 seconds (efficient routing)
- **Phase 3**: Variable based on tools used
- **Phase 4**: 1-3 seconds (response formatting)
- **Phase 5**: <1 second (quality validation)

### Compacting Performance
- **Trigger**: Automatic after every 50th message (25 user+assistant interaction pairs)
- **Processing Time**: ~2-5 seconds LLM call every 50 messages for summarization
- **Database Overhead**: Minimal (~1-2KB per compact)
- **Execution**: Background thread execution (non-blocking)

---

## Testing Commands

### Run Memory System Tests
```bash
# All memory tests
python -m pytest tests/test_hippocampus_* -v

# Specific compacting tests
python -m pytest tests/test_conversation_compact.py -v

# Phase architecture tests
python -m pytest tests/test_4_5_phase_architecture.py -v

# Full agent integration tests
python -m pytest tests/test_cortex_agent.py -v
```

### Test Conversation Compacting
```bash
# Test compacting threshold
python -m pytest tests/test_conversation_compact.py::test_conversation_compacting_threshold -v
```

### Test API Endpoints
```bash
# Test authenticated API endpoints
python -m pytest tests/test_api_endpoints.py -v
```

---

**Last Updated**: 2025-10-04
