# cortex

This module contains the core agent logic for Tatlock. It orchestrates all subsystems and exposes the FastAPI interface for chat interactions with comprehensive authentication and security.

## Core Functions

### `process_chat_interaction(user_message: str, history: list[dict]) -> dict`
Handles the entire chat logic flow with an agentic loop for sequential tool calls.

**Features:**
- **Agentic Loop**: Supports up to 5 iterations of tool calls per user message
- **Tool Integration**: Automatically calls available tools when needed
- **Context Management**: Maintains full conversation history including tool calls
- **Topic Classification**: Automatically classifies conversation topics
- **Memory Persistence**: Saves all interactions to the hippocampus database
- **Authentication Integration**: Works with the authentication system for user context

**Available Tools:**
- `web_search`: Search the web for current information
- `find_personal_variables`: Look up personal information about the user
- `get_weather_forecast`: Get weather forecasts for specific cities and dates
- `recall_memories`: Search conversation history by keyword
- `recall_memories_with_time`: Search conversation history with temporal filtering

**Process Flow:**
1. Loads base instructions from the `rise_and_shine` table
2. Builds conversation context with system prompts and history
3. Sends to LLM with available tools
4. Executes any requested tools silently
5. Continues loop until final response or max iterations
6. Classifies topic and saves interaction to memory
7. Returns response, topic, and updated history

## API Integration

The cortex module is integrated with FastAPI in `main.py` through the `/cortex` endpoint, which:
- Requires authentication via HTTP Basic Auth
- Accepts `ChatRequest` with message and history
- Returns `ChatResponse` with AI response, topic, and updated history
- Integrates with the user management system for personalized responses

### Authentication Flow
1. **User Authentication**: All requests require valid HTTP Basic Auth credentials
2. **User Context**: The authenticated user's information is available for personalization
3. **Tool Access**: Tools can access user-specific information through the authentication system
4. **Memory Isolation**: Each user's conversations are stored separately in the database

## Dependencies

- **hippocampus.database**: For base instructions and memory storage
- **hippocampus.remember**: For saving interactions
- **stem.tools**: For tool definitions and execution
- **stem.security**: For user authentication and context
- **config**: For LLM model configuration

## Security Considerations

- **User Isolation**: Each user's conversations and memories are isolated
- **Tool Access Control**: Tools respect user permissions and data access
- **Input Validation**: All inputs are validated through Pydantic models
- **Error Handling**: Comprehensive error handling prevents information leakage

## Integration with Other Modules

- **stem.security**: Provides user authentication and context
- **hippocampus**: Stores and retrieves conversation memory
- **stem.tools**: Executes external tool calls
- **main.py**: Exposes the API endpoint with authentication middleware
