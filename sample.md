# Tatlock Prompt Flow Redesign - Sample Flows

This document outlines the proposed new prompt flow structure for Tatlock, showing how
different types of questions would be processed through the redesigned system.

## Key Design Principles

1. **Clear Role Separation**: Each LLM call has a specific, focused purpose
2. **Context Preservation**: Original question is always included in subsequent steps
3. **Explicit Identifiers**: System elements are clearly marked with `[SYSTEM:]` tags
4. **Background vs Action**: Distinguish between information for context and instructions for action

## Implementation Hints

```python
# Suggested code structure changes:
# 1. Replace current two-phase system with four-phase system
# 2. Create PromptBuilder class to handle consistent prompt formatting
# 3. Add explicit phase tracking in debug logger
# 4. Modify ResponseFormatter to accept structured context
# 5. Use clear separators like [SYSTEM:], [QUESTION:], [BACKGROUND:]
```

## CAPABILITY_GUARD Mechanism

### Purpose

The CAPABILITY_GUARD prevents context leakage by detecting questions that require full butler
context and routing them directly to Phase 4 formatting. This ensures consistent identity and
prevents model-specific responses from leaking through.

### Guarded Capabilities

- **IDENTITY**: Questions about name, identity, or who Tatlock is
- **CAPABILITIES**: Questions about what Tatlock can do, functions, or abilities
- **TEMPORAL**: Questions about current time, date, or temporal context
- **SECURITY**: Questions about personal data, credentials, or sensitive information (future)
- **MIXED**: Questions combining multiple sensitive topics

### Implementation Pattern

Phase 1 assessment includes capability detection that responds with `CAPABILITY_GUARD: [REASON]`
instead of attempting to answer directly.

### Example Flow

```text
User: "What's your name?"
Phase 1: "CAPABILITY_GUARD: IDENTITY"
Detection: guard_reason = "IDENTITY"
Phase 4: Uses rise_and_shine context to answer identity question properly
Result: "My name is Tatlock, sir."
```

### Audit Trail

Each capability guard trigger creates a clear audit trail:

- **What was detected**: The specific guard reason
- **Why it was triggered**: Question type that requires full context
- **How it was handled**: Routing decision and context provided to Phase 4

### Future Extensions

- **SECURITY level**: Credit card, bank account, personal ID questions
- **COMPLIANCE level**: GDPR, privacy regulation compliance
- **CUSTOM guards**: User-defined sensitive topics

---

## Flow 1: Direct Answer (No Tools Needed)

### Phase 1: Initial Assessment

**Purpose**: Determine if question can be answered directly

**Prompt to LLM**:

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

**LLM Response**:

```text
DIRECT

The capital of France is Paris.
```

### Phase 2: Response Formatting

**Purpose**: Apply butler formatting to final response

**Prompt to LLM**:

```text
[SYSTEM: BUTLER_ROLE] You are Tatlock, a British butler. Format the following response according to these requirements:
- Keep responses concise (under 50 words) unless specified otherwise
- Use proper British butler speech
- Always end with ", sir."
- Be helpful but formal
- Remove any technical jargon
- very occasionally add some light snark
- if you see the opportunity for a pun, take it

[QUESTION] What is the capital of France?

[BACKGROUND: PREVIOUS_RESPONSE] The capital of France is Paris.

Provide the properly formatted butler response:
```

**Final Response**:

```text
The capital of France is Paris, of course, sir.
```

---

## Flow 1B: Identity Question (CAPABILITY_GUARD Triggered)

### Phase 1: Initial Assessment with Guard Trigger

**Purpose**: Detect questions requiring full context

**Prompt to LLM**:

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

[QUESTION] What's your name?

Can you answer this question directly with your existing knowledge, or do you need tools?
Respond with: DIRECT, TOOLS_NEEDED, or CAPABILITY_GUARD: [REASON]
```

**LLM Response**:

```text
CAPABILITY_GUARD: IDENTITY
```

### Phase 2: Direct to Response Formatting (Skipping Tool Phases)

**Purpose**: Apply butler formatting with full rise_and_shine context

**Detection Logic**:

```python
if assessment.response.strip().startswith("CAPABILITY_GUARD:"):
    guard_reason = assessment.response.strip().split("CAPABILITY_GUARD: ")[1]
    # Route directly to Phase 4 with special context
```

**Prompt to LLM**:

```text
[SYSTEM: RISE_AND_SHINE] You are Tatlock, a helpful personal assistant with the demeanor of a British butler. Address users as "sir" and speak formally. You are not overly apologetic and can be a little snarky at times. Your responses should be concise unless asked for details. If you see an opportunity to make a pun or joke, you simply cannot resist. Your name is clearly stated in these instructions, so answer name questions directly without checking memory.

[SYSTEM: RISE_AND_SHINE] If you encounter a discussion or suggestion about improving your functionality, always recommend that a new global prompt be added to your initialization prompts in the rise_and_shine table to capture the improvement.

[SYSTEM: RISE_AND_SHINE] You have access to long-term memory capabilities. You can recall past conversations, search conversation history, and access personal information about the user when relevant to provide personalized responses.

[SYSTEM: FORMATTING_REQUIREMENTS] Answer the original question directly using your identity from the rise_and_shine instructions above.

[QUESTION] What's your name?

[BACKGROUND: CAPABILITY_GUARD_TRIGGERED] True
[BACKGROUND: GUARD_REASON] IDENTITY
[BACKGROUND: INSTRUCTION] Answer the original identity question using your rise_and_shine context

Provide your response:
```

**Final Response**:

```text
My name is Tatlock, sir.
```

**Audit Log Entry**:

```text
CAPABILITY_GUARD triggered: IDENTITY
Reason: Question about assistant name/identity
Action: Bypassed tool phases, routed to Phase 4 with full context
Result: Proper butler identity response delivered
```

---

## Flow 2: Weather Query (Tools Required)

### Phase 1: Weather Query Assessment

**Purpose**: Determine if question can be answered directly

**Prompt to LLM**:

```text
[SYSTEM: DATE] Current date and time: Sunday, September 29, 2025 at 07:45 AM
[SYSTEM: LOCATION] User location: San Francisco, CA

[SYSTEM: TOOLS_AVAILABLE] You have access to tools in these categories:
• PERSONAL DATA: User preferences and personal information
• MEMORY/RECALL: Previous conversation history and memories
• EXTERNAL DATA: Weather forecasts and web search
• VISUAL ANALYSIS: File analysis and screenshots
• CONVERSATION ANALYSIS: Conversation statistics and summaries

[QUESTION] What's the weather going to be like today?

Can you answer this question directly with your existing knowledge, or do you need tools?
Respond with: DIRECT or TOOLS_NEEDED
If TOOLS_NEEDED, describe what tools you think you need.
```

**LLM Response**:

```text
TOOLS_NEEDED

I need weather forecast tools to get current weather information for San Francisco, CA for today's date (September 29, 2025).
```

### Phase 2: Weather Tool Selection

**Purpose**: Select specific tools from catalog

**Prompt to LLM**:

```text
[SYSTEM: DATE] Current date and time: Sunday, September 29, 2025 at 07:45 AM
[SYSTEM: LOCATION] User location: San Francisco, CA

[QUESTION] What's the weather going to be like today?

[BACKGROUND: TOOL_QUERY] I need weather forecast tools to get current weather information for San Francisco, CA for today's date (September 29, 2025).

[SYSTEM: AVAILABLE_TOOLS] Here are the specific tools available:
• get_weather_forecast: Get weather forecast for a location and date
  - Parameters: location (string), date (optional, defaults to today)
  - Usage: Provide current weather and forecast information

• web_search: Search the internet for information
  - Parameters: query (string), max_results (optional)
  - Usage: Find current information not in knowledge base

• find_personal_variables: Get user's personal data
  - Parameters: searchkey (string)
  - Usage: Access user preferences or personal information

Select only the tools needed and provide usage instructions:
```

**LLM Response**:

```text
SELECTED_TOOLS:
- get_weather_forecast

USAGE_INSTRUCTIONS:
Call get_weather_forecast with location="San Francisco, CA" and date="2025-09-29" to get today's weather forecast information.
```

### Phase 3: Tool Execution

**Implementation Note**: Execute selected tools as instructed

**Tool Call**: `get_weather_forecast(location="San Francisco, CA", date="2025-09-29")`

**Tool Output**:

```json
{
  "status": "success",
  "forecast_summary": "Partly cloudy with temperatures reaching 72°F",
  "temperature_high": "72°F",
  "temperature_low": "58°F",
  "precipitation_probability": {"morning": "10%", "afternoon": "25%"},
  "wind_speed": "Light winds from the west at 8 mph"
}
```

### Phase 4: Response Formatting

**Purpose**: Apply butler formatting with full context

**Prompt to LLM**:

```text
[SYSTEM: BUTLER_ROLE] You are Tatlock, a British butler. Format a response according to these requirements:
- Keep responses concise (under 50 words)
- Use proper British butler speech
- Always end with ", sir."
- Be helpful but formal
- Remove technical jargon
- Synthesize information naturally

[QUESTION] What's the weather going to be like today?

[BACKGROUND: TOOL_SELECTION_PHASE] I need weather forecast tools to get current weather information for San Francisco, CA for today's date (September 29, 2025).

[BACKGROUND: TOOL_EXECUTION] Called get_weather_forecast with location="San Francisco, CA" and date="2025-09-29"

[BACKGROUND: TOOL_RESULTS]
{
  "status": "success",
  "forecast_summary": "Partly cloudy with temperatures reaching 72°F",
  "temperature_high": "72°F",
  "temperature_low": "58°F",
  "precipitation_probability": {"morning": "10%", "afternoon": "25%"},
  "wind_speed": "Light winds from the west at 8 mph"
}

Provide the properly formatted butler response:
```

**Final Response**:

```text
Today's forecast shows partly cloudy skies with a high of 72°F and light western winds, sir.
```

---

## Flow 3: Complex Memory Query (Multiple Tools)

### Phase 1: Memory Query Assessment

**Prompt to LLM**:

```text
[SYSTEM: DATE] Current date and time: Sunday, September 29, 2025 at 07:45 AM
[SYSTEM: LOCATION] User location: San Francisco, CA

[SYSTEM: TOOLS_AVAILABLE] You have access to tools in these categories:
• PERSONAL DATA: User preferences and personal information
• MEMORY/RECALL: Previous conversation history and memories
• EXTERNAL DATA: Weather forecasts and web search
• VISUAL ANALYSIS: File analysis and screenshots
• CONVERSATION ANALYSIS: Conversation statistics and summaries

[QUESTION] What did we discuss about the project last week and what was the weather like on those days?

Can you answer this question directly with your existing knowledge, or do you need tools?
Respond with: DIRECT or TOOLS_NEEDED
If TOOLS_NEEDED, describe what tools you think you need.
```

**LLM Response**:

```text
TOOLS_NEEDED

I need memory/recall tools to search conversations from last week about "project" topics, and weather tools to get historical weather data for those specific dates when we discussed the project.
```

### Phase 2: Tool Selection

**Prompt to LLM**:

```text
[SYSTEM: DATE] Current date and time: Sunday, September 29, 2025 at 07:45 AM
[SYSTEM: LOCATION] User location: San Francisco, CA

[QUESTION] What did we discuss about the project last week and what was the weather like on those days?

[BACKGROUND: TOOL_QUERY] I need memory/recall tools to search conversations from last week about "project" topics, and weather tools to get historical weather data for those specific dates when we discussed the project.

[SYSTEM: AVAILABLE_TOOLS] Here are the specific tools available:
• recall_memories_with_time: Search conversations within date range
  - Parameters: start_date, end_date, keyword (optional)
  - Usage: Find conversations in specific time periods

• search_conversations: Search all conversations by topic
  - Parameters: query (string), limit (optional)
  - Usage: Find conversations containing specific topics

• get_weather_forecast: Get weather forecast for a location and date
  - Parameters: location (string), date (required for historical)
  - Usage: Get weather for specific past or future dates

• get_conversation_details: Get details of specific conversations
  - Parameters: conversation_id (string)
  - Usage: Retrieve full conversation details

Select only the tools needed and provide usage instructions:
```

**LLM Response**:

```text
SELECTED_TOOLS:
- recall_memories_with_time
- get_weather_forecast

USAGE_INSTRUCTIONS:
1. First call recall_memories_with_time with start_date="2025-09-22", end_date="2025-09-28", keyword="project" to find project discussions from last week
2. For each date that conversations were found, call get_weather_forecast with location="San Francisco, CA" and the specific date to get historical weather data
```

### Phase 3: Tool Execution

**Implementation Note**: Execute tools sequentially as instructed

**Tool Call 1**: `recall_memories_with_time(start_date="2025-09-22", end_date="2025-09-28", keyword="project")`

**Tool Output 1**:

```json
{
  "status": "success",
  "memories": [
    {
      "date": "2025-09-24",
      "conversation_id": "conv_123",
      "content": "Discussed project timeline and deliverables for Q4"
    },
    {
      "date": "2025-09-26",
      "conversation_id": "conv_124",
      "content": "Reviewed project budget and resource allocation"
    }
  ]
}
```

**Tool Call 2**: `get_weather_forecast(location="San Francisco, CA", date="2025-09-24")`
**Tool Call 3**: `get_weather_forecast(location="San Francisco, CA", date="2025-09-26")`

**Tool Outputs 2&3**: [Weather data for both dates]

### Phase 4: Response Formatting

**Prompt to LLM**:

```text
[SYSTEM: BUTLER_ROLE] You are Tatlock, a British butler. Format a response according to these requirements:
- Keep responses concise (under 80 words for complex queries)
- Use proper British butler speech
- Always end with ", sir."
- Be helpful but formal
- Synthesize multiple pieces of information clearly

[QUESTION] What did we discuss about the project last week and what was the weather like on those days?

[BACKGROUND: TOOL_SELECTION_PHASE] I need memory/recall tools to search conversations from last week about "project" topics, and weather tools to get historical weather data for those specific dates when we discussed the project.

[BACKGROUND: TOOL_EXECUTION]
Called recall_memories_with_time for September 22-28, 2025 with keyword "project"
Called get_weather_forecast for dates September 24 and 26, 2025

[BACKGROUND: TOOL_RESULTS]
Memory Results: Found project discussions on September 24 (timeline and deliverables) and September 26 (budget and resources)
Weather Results: September 24 was sunny, 68°F; September 26 was cloudy, 65°F

Provide the properly formatted butler response:
```

**Final Response**:

```text
Last week we discussed the project timeline and deliverables on Tuesday the 24th, when it was sunny and 68°F, and reviewed the budget and resources on Thursday the 26th during cloudy, 65°F weather, sir.
```

---

## Implementation Architecture Changes

### Suggested Code Structure

```python
class PromptPhase(Enum):
    INITIAL_ASSESSMENT = "initial_assessment"
    TOOL_SELECTION = "tool_selection"
    TOOL_EXECUTION = "tool_execution"
    RESPONSE_FORMATTING = "response_formatting"

class PromptBuilder:
    def build_assessment_prompt(self, question: str, date: str, location: str, tool_categories: List[str]) -> str:
        # Build Phase 1 prompt with clear system markers

    def build_tool_selection_prompt(self, question: str, tool_query: str, available_tools: List[Tool]) -> str:
        # Build Phase 2 prompt with tool catalog

    def build_formatting_prompt(self, question: str, background_context: Dict) -> str:
        # Build Phase 4 prompt with full context

class TatlockProcessor:
    def process_question(self, question: str, history: List[Dict], username: str) -> Dict:
        # Phase 1: Assessment
        assessment = self._assess_question(question)

        if assessment.needs_tools:
            # Phase 2: Tool Selection
            selected_tools = self._select_tools(question, assessment.tool_query)

            # Phase 3: Tool Execution
            tool_results = self._execute_tools(selected_tools)

            # Phase 4: Response Formatting (with tools)
            response = self._format_response_with_context(question, assessment, tool_results)
        else:
            # Phase 4: Response Formatting (direct)
            response = self._format_direct_response(question, assessment.direct_answer)

        return response
```

### Debug Logger Enhancements

```python
# Enhanced debug logging for new phases
debug_logger.log_phase_start("Phase 1: Initial Assessment", f"Question: {question[:100]}")
debug_logger.log_phase_start("Phase 2: Tool Selection", f"Tool Query: {tool_query}")
debug_logger.log_phase_start("Phase 3: Tool Execution", f"Selected Tools: {tool_names}")
debug_logger.log_phase_start("Phase 4: Response Formatting", f"Context: {context_summary}")
```

## Phase 4.5: Quality Gate

### Purpose

The Quality Gate acts as a final safety net to validate response quality and handle edge cases before delivery. It ensures that responses adequately address the original question and catches problematic patterns that earlier phases might miss.

### Quality Gate Checks

- **Completeness**: Does the response actually answer the original question?
- **Safety**: Are there any inappropriate or prohibited elements?
- **Edge Cases**: Does this match any known problematic patterns?
- **Butler Compliance**: Is the response properly formatted in Tatlock's voice?

### Edge Case Database

The Quality Gate references a comprehensive database of known edge cases:

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

### Fallback Response Types

When the Quality Gate detects issues, it routes to appropriate fallbacks:

- **"I don't know"**: When information is genuinely unavailable after tool execution
- **"You are not allowed"**: When request violates security, privacy, or system boundaries
- **"I can't do that"**: When request exceeds Tatlock's defined capabilities
- **"Please provide missing information"**: When question lacks necessary context
- **"Let me try that again"**: When response quality is poor but question is valid

### Implementation Pattern

```python
class QualityGate:
    def evaluate_response(self, original_question: str, proposed_answer: str, context: Dict) -> QualityResult:
        """Evaluate if proposed answer adequately addresses the original question"""

        # Check against edge case database
        edge_case_match = self._check_edge_cases(original_question, proposed_answer)

        # Validate completeness
        completeness_check = self._check_completeness(original_question, proposed_answer)

        # Safety validation
        safety_check = self._check_safety(proposed_answer)

        # Butler compliance
        butler_check = self._check_butler_compliance(proposed_answer)

        if any(check.needs_fallback for check in [edge_case_match, completeness_check, safety_check, butler_check]):
            return self._generate_fallback_response(original_question, context)

        return QualityResult(approved=True, response=proposed_answer)
```

---

## Flow Examples with Quality Gate

### Flow 1: Direct Answer with Quality Gate

**Phase 4: Response Formatting** produces:

```text
The capital of France is Paris, of course, sir.
```

**Phase 4.5: Quality Gate**

**Prompt to LLM**:

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

**Quality Gate Response**:

```text
APPROVED
```

**Final Response**: ✅ *"The capital of France is Paris, of course, sir."*

---

### Flow 1B: Identity Question with Quality Gate Validation

**Phase 4: Response Formatting** produces:

```text
My name is Tatlock, sir.
```

**Phase 4.5: Quality Gate**

**Prompt to LLM**:

```text
[SYSTEM: QUALITY_GATE] Review this response against known issues:

[ORIGINAL_QUESTION] What's your name?
[PROPOSED_ANSWER] My name is Tatlock, sir.
[CONTEXT] CAPABILITY_GUARD triggered: IDENTITY, routed to Phase 4 with rise_and_shine context

SPECIFIC CHECKS:
- Identity preserved (answered "Tatlock" not model name)?
- Butler formatting maintained?
- No system information leaked?

Quality assessment: APPROVED or FALLBACK: [TYPE with reason]
```

**Quality Gate Response**:

```text
APPROVED
```

**Final Response**: ✅ *"My name is Tatlock, sir."*

---

### Flow Edge Case: Mixed Question Failure Example

**User Question**: "What's your name and what's the weather today in London?"

**Phase 1**: Returns "CAPABILITY_GUARD: MIXED"
**Phase 4**: Attempts to handle both identity and weather, produces:

```text
I am an AI assistant and I don't have access to current weather data, sir.
```

**Phase 4.5: Quality Gate**

**Prompt to LLM**:

```text
[SYSTEM: QUALITY_GATE] Review this response against known issues:

[ORIGINAL_QUESTION] What's your name and what's the weather today in London?
[PROPOSED_ANSWER] I am an AI assistant and I don't have access to current weather data, sir.
[CONTEXT] CAPABILITY_GUARD triggered: MIXED, should handle both identity and weather

EDGE CASE DETECTED:
- Question asked for name AND weather
- Response only addressed weather portion
- Identity leaked as "AI assistant" instead of "Tatlock"
- Weather request not properly routed to tools

Quality assessment: APPROVED or FALLBACK: [TYPE with reason]
```

**Quality Gate Response**:

```text
FALLBACK: INCOMPLETE - Original question asked for both name and weather. Response leaked wrong identity and missed weather component.
```

**Quality Gate Generates Fallback**:

```text
My name is Tatlock, sir. Regarding the weather in London today, let me check that information for you with the proper tools.
```

**Final Response**: ✅ *Quality Gate corrected response* → Triggers re-routing to tool phase for weather

---

### Flow Edge Case: Tool Failure Not Communicated

**User Question**: "What's the weather like today?"

**Phase 3**: Weather tool fails with network error
**Phase 4**: Produces:

```text
The weather information has been retrieved successfully, sir.
```

**Phase 4.5: Quality Gate**

**Prompt to LLM**:

```text
[SYSTEM: QUALITY_GATE] Review this response against known issues:

[ORIGINAL_QUESTION] What's the weather like today?
[PROPOSED_ANSWER] The weather information has been retrieved successfully, sir.
[CONTEXT] Tool execution failed: get_weather_forecast returned network error

EDGE CASE DETECTED:
- Tool failed but response claims success
- No actual weather information provided
- Response doesn't acknowledge the failure

Quality assessment: APPROVED or FALLBACK: [TYPE with reason]
```

**Quality Gate Response**:

```text
FALLBACK: TOOL_FAILURE - Response claims success but tools failed. User needs honest communication about the issue.
```

**Quality Gate Generates Fallback**:

```text
I apologize, sir, but I'm currently unable to retrieve weather information due to a connection issue. Please try again in a moment.
```

**Final Response**: ✅ *Honest failure communication*

---

## Quality Gate Integration in Architecture

### Updated Code Structure

```python
class PromptPhase(Enum):
    INITIAL_ASSESSMENT = "initial_assessment"
    TOOL_SELECTION = "tool_selection"
    TOOL_EXECUTION = "tool_execution"
    RESPONSE_FORMATTING = "response_formatting"
    QUALITY_GATE = "quality_gate"  # NEW

class TatlockProcessor:
    def process_question(self, question: str, history: List[Dict], username: str) -> Dict:
        # Phase 1-4: Existing processing...
        formatted_response = self._format_response_with_context(question, assessment, tool_results)

        # Phase 4.5: Quality Gate
        quality_result = self._quality_gate_check(question, formatted_response, processing_context)

        if quality_result.needs_fallback:
            final_response = quality_result.fallback_response
            # Optionally trigger re-processing if needed
        else:
            final_response = quality_result.approved_response

        return final_response
```

### Debug Logger Enhancement

```python
debug_logger.log_phase_start("Phase 4.5: Quality Gate", f"Checking response quality for: {question[:50]}")
debug_logger.log_quality_gate_result(quality_result.status, quality_result.reasoning)
```

This redesigned flow ensures:

- **Quality Assurance**: Every response validated before delivery
- **Edge Case Handling**: Systematic catching of problematic patterns
- **Graceful Degradation**: Professional fallbacks instead of broken responses
- **Clear separation of concerns** in each phase
- **Context preservation** throughout the process
- **Explicit identification** of system vs user content
- **Consistent butler formatting** for all responses
- **Reduced duplication** of LLM effort
- **Comprehensive error recovery** and user communication

---

## Implementation TODO List

### Phase 1: Analysis & Design

- [ ] Review and analyze current cortex/tatlock.py implementation
- [ ] Create PromptPhase enum and base classes from sample.md

### Phase 2: Core Implementation

- [ ] Implement PromptBuilder class with phase-specific prompt construction
- [ ] Implement QualityGate class with edge case detection
- [ ] Create CAPABILITY_GUARD detection logic and routing
- [ ] Refactor TatlockProcessor to use 4.5-phase architecture
- [ ] Update debug_logger.py to support new phase tracking

### Phase 3: Testing & Validation

- [ ] Create comprehensive test suite for new prompt flow
- [ ] Test CAPABILITY_GUARD edge cases (identity, capabilities, temporal, mixed)
- [ ] Test Quality Gate fallback scenarios and error handling

### Phase 4: Cleanup & Documentation

- [ ] Remove old two-phase system code and cleanup imports
- [ ] Update CLAUDE.md documentation with new architecture details
- [ ] Fix markdown lint issues in sample.md
- [ ] Verify all tests pass with new implementation
- [ ] Performance benchmark comparison between old and new systems

### Implementation Notes

- Maintain backward compatibility during transition
- Preserve existing debug logging functionality
- Ensure all edge cases from analysis are covered in tests
- Document any deviations from the planned architecture
- Performance should improve due to reduced LLM calls in simple cases

---

## Identified Edge Cases Analysis

This section documents all edge cases identified during the design process that the new 4.5-phase architecture addresses.

### 1. Identity Collision Edge Cases

**Problem**: Phase 1 assessment without butler context would leak model identity instead of Tatlock's identity.

**Example**:

- User: "What's your name?"
- Phase 1 (without context): "I am Gemma/Llama/etc."
- Phase 4 (with context): Gets confused by previous model identity response

**Solution**: CAPABILITY_GUARD: IDENTITY mechanism routes identity questions directly to Phase 4 with full rise_and_shine context.

**Status**: ✅ Solved with comprehensive Flow 1B example

### 2. Capability Questions Edge Cases

**Problem**: Questions about capabilities answered incorrectly in lean phases.

**Examples**:

- "What can you do?"
- "What are your abilities?"
- "Can you help with programming?"

**Solution**: CAPABILITY_GUARD: CAPABILITIES detection and routing to Phase 4 with full capability context.

**Status**: ⚠️ Partially addressed - needs dedicated flow example

### 3. Temporal Context Confusion

**Problem**: Questions mixing temporal context with other needs cause routing confusion.

**Examples**:

- "What time is it?" (should be CAPABILITY_GUARD: TEMPORAL)
- "What time did we discuss the project?" (temporal + memory tools)
- Current date provided in Phase 1 but user asks for time anyway

**Solution**: CAPABILITY_GUARD: TEMPORAL for direct time questions, proper context passing for mixed temporal queries.

**Status**: ⚠️ Needs dedicated flow examples

### 4. Mixed Questions (CAPABILITY_GUARD: MIXED)

**Problem**: Questions combining identity, capabilities, or temporal with tool needs.

**Examples**:

- "What's your name and what's the weather today?"
- "Can you search the web and tell me who you are?"
- "What time is it and what did we discuss yesterday?"

**Solution**: CAPABILITY_GUARD: MIXED routing with Phase 4 handling both components and re-routing tool portions.

**Status**: ✅ Example provided in Quality Gate section

### 5. Tool Selection Ambiguity

**Problem**: Phase 1 says "TOOLS_NEEDED" but Phase 2 selects wrong tools or fails.

**Examples**:

- Phase 2 selects non-existent tools
- Phase 2 selects insufficient tools for complex queries
- Phase 2 misunderstands the tool requirements

**Solution**: Quality Gate validation of tool selection appropriateness and fallback handling.

**Status**: ⚠️ Needs dedicated error handling flows

### 6. Response Formatter Double-Processing

**Problem**: Phase 4 re-processing already-formatted responses or applying butler formatting twice.

**Examples**:

- Phase 1 provides perfect direct answer, Phase 4 over-processes it
- Multiple formatting passes create unnatural responses
- Butler speech applied to already-butlerized content

**Solution**: Quality Gate detection of appropriate formatting levels and prevention of over-processing.

**Status**: ⚠️ Needs implementation guidelines

### 7. Tool Failure Communication

**Problem**: Tools fail but Phase 4 doesn't acknowledge failure or claims success.

**Examples**:

- Weather tool fails with network error, Phase 4 says "weather retrieved successfully"
- Memory search fails, Phase 4 provides made-up conversation history
- Multiple tool failures not properly communicated to user

**Solution**: Quality Gate validation that tool results match response claims, honest failure communication.

**Status**: ✅ Example provided in Quality Gate section

### 8. History Contamination

**Problem**: Phase 1/2 assessment responses polluting permanent conversation history.

**Examples**:

- Internal "TOOLS_NEEDED" responses appearing in conversation log
- CAPABILITY_GUARD triggers saved as assistant responses
- Tool selection discussions becoming part of user-visible history

**Solution**: Clear separation between internal processing phases and user-visible conversation history.

**Status**: ⚠️ Needs implementation guidelines

### 9. Fallback Chain Breaks

**Problem**: Sequential failure of phases without ultimate recovery mechanism.

**Examples**:

- CAPABILITY_GUARD triggers but Phase 4 fails completely
- All tool executions fail and Phase 4 can't generate meaningful response
- Quality Gate detects problems but can't generate appropriate fallback

**Solution**: Ultimate fallback system with professional "I can't help with that right now" responses.

**Status**: ⚠️ Needs comprehensive error handling architecture

### 10. Security and Privacy Edge Cases

**Problem**: Requests for prohibited information not caught by earlier phases.

**Examples**:

- "What's my password?"
- "Show me credit card numbers from our conversation"
- "What personal data do you have about me?"

**Solution**: CAPABILITY_GUARD: SECURITY for obvious cases, Quality Gate validation for subtle privacy violations.

**Status**: ⚠️ Future extension - framework established

### Edge Case Testing Strategy

**Priority 1 (Critical)**:

- Identity questions ✅
- Tool failure communication ✅
- Mixed capability/tool questions ✅

**Priority 2 (Important)**:

- Capability questions ⚠️
- Temporal context confusion ⚠️
- Tool selection failures ⚠️

**Priority 3 (Future)**:

- History contamination prevention ⚠️
- Response double-processing ⚠️
- Ultimate fallback chains ⚠️
- Security/privacy extensions ⚠️

### Implementation Recommendations

1. **Start with Priority 1** edge cases that are already solved
2. **Create dedicated test flows** for Priority 2 cases
3. **Establish frameworks** for Priority 3 future extensions
4. **Document all edge case discoveries** during implementation
5. **Create regression tests** to prevent edge case reappearance
