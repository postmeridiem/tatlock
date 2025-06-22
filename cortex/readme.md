# Cortex

**Status: Production Ready - Core Agent Logic**

The Cortex module contains the core agent logic for Tatlock. Named after the brain's cerebral cortex responsible for higher-order thinking and decision-making, this module orchestrates all subsystems and exposes the FastAPI interface for chat interactions with comprehensive session-based authentication and security.

## ✅ **Core Features**

### 🧠 **Agent Logic** (`agent.py`)
The main agent processing function handles the entire chat logic flow with an agentic loop for sequential tool calls:

```python
def process_chat_interaction(
    user_message: str, 
    history: list[dict], 
    username: str = "admin", 
    conversation_id: str | None = None
) -> dict
```

**Features:**
- **Agentic Loop**: Supports up to 5 iterations of tool calls per user message
- **Tool Integration**: Automatically calls available tools when needed
- **Context Management**: Maintains full conversation history including tool calls
- **Topic Classification**: Automatically classifies conversation topics using LLM
- **Memory Persistence**: Saves all interactions to the user's hippocampus database
- **Authentication Integration**: Works with the session-based authentication system for user context
- **Conversation Tracking**: Creates and updates conversation records with metadata
- **Error Handling**: Comprehensive error handling for tool execution and LLM responses

### 🛠️ **Available Tools**
The agent has access to all tools defined in the system:

#### **External API Tools** (from cerebellum/)
- **`web_search`**: Search the web for current information using Google Custom Search API
- **`get_weather_forecast`**: Get weather forecasts for specific cities and dates using OpenWeather API

#### **Memory Tools** (from hippocampus/tools/)
- **`find_personal_variables`**: Look up personal information about the user from their database
- **`recall_memories`**: Search conversation history by keyword (user-scoped)
- **`recall_memories_with_time`**: Search conversation history with temporal filtering (user-scoped)
- **`get_user_conversations`**: List all conversations for the current user
- **`get_conversation_details`**: Get detailed information about a specific conversation
- **`search_conversations`**: Search conversations by title or content
- **`get_conversations_by_topic`**: Find conversations containing specific topics
- **`get_topics_by_conversation`**: Get all topics in a specific conversation
- **`get_conversation_summary`**: Get comprehensive conversation summaries
- **`get_topic_statistics`**: Get statistics about topics across conversations

#### **Visual Tools** (from occipital/)
- **`screenshot_from_url`**: Take screenshots of web pages
- **`analyze_file`**: Analyze and interpret image files

## 🔄 **Process Flow**

1. **Load Base Instructions**: Retrieves system prompts from user's `rise_and_shine` table
2. **Build Context**: Constructs conversation context with system prompts and history
3. **LLM Processing**: Sends to LLM (Ollama) with available tools
4. **Tool Execution**: Executes any requested tools silently with user context
5. **Iteration Loop**: Continues loop until final response or max iterations (5)
6. **Topic Classification**: Classifies topic using LLM
7. **Memory Storage**: Saves interaction to user's memory database
8. **Conversation Update**: Creates or updates conversation record with metadata
9. **Response Return**: Returns response, topic, and updated history

## 🌐 **API Integration**

The cortex module is integrated with FastAPI in `main.py` through the `/cortex` endpoint:

### **Endpoint Details**
- **Path**: `/cortex`
- **Method**: `POST`
- **Authentication**: Requires session-based authentication
- **Request**: `ChatRequest` with message, history, and optional conversation_id
- **Response**: `ChatResponse` with AI response, topic, and updated history

### **Authentication Flow**
1. **Session Authentication**: All requests require valid session cookies
2. **User Context**: The authenticated user's information is available for personalization
3. **Tool Access**: Tools can access user-specific information through the authentication system
4. **Memory Isolation**: Each user's conversations are stored separately in their own database
5. **Conversation Tracking**: Conversations are tracked per user with metadata

## 🤖 **LLM Integration**

### **Model Configuration**
- **Default Model**: `gemma3-cortex:latest` (configurable via `OLLAMA_MODEL` environment variable)
- **Provider**: Ollama for local inference
- **Tool Calling**: Supports both structured tool calls and legacy JSON tool calls
- **Context Management**: Optimized context building for efficient token usage

### **Tool Call Processing**
The agent handles two types of tool call formats:

#### **Structured Tool Calls**
Modern Ollama tool calling format with proper function definitions:
```json
{
  "tool_calls": [
    {
      "id": "call_123",
      "type": "function",
      "function": {
        "name": "web_search",
        "arguments": "{\"query\": \"Python programming\"}"
      }
    }
  ]
}
```

#### **Legacy JSON Tool Calls**
Parsed from content using regex patterns for backward compatibility:
```json
{
  "tool_calls": [
    {
      "name": "web_search",
      "arguments": {"query": "Python programming"}
    }
  ]
}
```

### **Topic Classification**
- Uses the same LLM model for topic classification
- Generates single-word topics (e.g., "weather", "personal_info", "planning")
- Falls back to "general" if classification fails
- Automatic topic assignment for all conversations

## 🔗 **Dependencies**

### **Internal Modules**
- **hippocampus.database**: For base instructions and memory storage
- **hippocampus.remember**: For saving interactions and conversation tracking
- **stem.tools**: For tool definitions and execution
- **stem.security**: For user authentication and context
- **config**: For LLM model configuration

### **External Dependencies**
- **ollama**: For LLM inference
- **nest_asyncio**: For async tool execution in sync context

## 🛡️ **Security Considerations**

- **User Isolation**: Each user's conversations and memories are completely isolated
- **Tool Access Control**: Tools respect user permissions and data access
- **Input Validation**: All inputs are validated through Pydantic models
- **Error Handling**: Comprehensive error handling prevents information leakage
- **Session Security**: Secure session management with proper cookie handling
- **SQL Injection Prevention**: All database queries use parameterized queries

## 🔗 **Integration with Other Modules**

- **Stem**: Provides user authentication, tools, and utilities
- **Hippocampus**: Stores and retrieves conversation memory per user
- **Cerebellum**: External API tools (web search, weather)
- **Occipital**: Visual processing tools (screenshots, image analysis)
- **Main.py**: Exposes the API endpoint with session middleware

## ⚠️ **Error Handling**

### **Tool Execution Errors**
- Invalid tool names are logged and ignored
- Tool execution failures are reported back to the LLM
- Graceful degradation when tools are unavailable
- Comprehensive error logging for debugging

### **LLM Errors**
- Connection errors to Ollama are handled gracefully
- Invalid responses are logged and fallback responses provided
- Topic classification failures default to "general"
- Retry logic for transient connection issues

### **Database Errors**
- Memory save failures are logged but don't break the conversation flow
- Database connection issues are handled gracefully
- User database creation on-demand for new users
- Transaction rollback on critical errors

## 📈 **Performance Considerations**

- **Tool Call Limits**: Maximum 5 iterations per user message to prevent infinite loops
- **Memory Management**: Efficient handling of conversation history
- **Database Connections**: Proper connection management for user databases
- **LLM Context**: Optimized context building for efficient token usage
- **Async Tool Execution**: Non-blocking tool execution for better performance

## 🧪 **Testing**

### **Unit Tests**
```bash
# Run cortex-specific tests
python -m pytest tests/test_cortex_agent.py -v
```

### **Integration Tests**
```bash
# Test agent with tools
python -c "from cortex.agent import process_chat_interaction; print('Agent imported successfully')"
```

## 🔮 **Future Enhancements**

### **Planned Improvements**
- **Streaming Responses**: Real-time response streaming for better UX
- **Tool Result Caching**: Cache tool results to reduce API calls
- **Advanced Topic Classification**: Multi-label topic classification
- **Conversation Summarization**: Automatic conversation summarization
- **Tool Usage Analytics**: Track and optimize tool usage patterns

### **Potential New Tools**
- **File Operations**: Read and write file operations
- **Calendar Integration**: Schedule and event management
- **Email Integration**: Send and receive emails
- **Code Execution**: Safe code execution environment
- **Image Processing**: Image analysis and generation

### **Performance Optimizations**
- **Response Caching**: Cache common responses for faster replies
- **Context Optimization**: Smarter context truncation for long conversations
- **Parallel Tool Execution**: Execute independent tools in parallel
- **Memory Compression**: Automatic summarization of old conversation context

## 📚 **Related Documentation**

- **[README.md](../README.md)** - General overview and installation
- **[developer.md](../developer.md)** - Developer guide and practices
- **[moreinfo.md](../moreinfo.md)** - In-depth technical information
- **[hippocampus/readme.md](../hippocampus/readme.md)** - Memory system documentation
- **[stem/readme.md](../stem/readme.md)** - Core utilities and infrastructure
- **[parietal/readme.md](../parietal/readme.md)** - Hardware monitoring and performance
