"""
stem/tools.py

Dynamic tool system for Tatlock.
Replaces the old static import system with dynamic loading for modular architecture.
Supports built-in tools, plugins, and external tool packages.
"""

import logging
from typing import Dict, Any, Callable, Optional
from stem.dynamic_tools import tool_registry, initialize_tool_system, get_tool_function
from hippocampus.reference_frame import get_enabled_tools_from_db

# Set up logging for this module
logger = logging.getLogger(__name__)

# Initialize the dynamic tool system
initialize_tool_system()

# The TOOLS list is still loaded from database for Ollama compatibility
TOOLS = get_enabled_tools_from_db()

def get_available_tools() -> Dict[str, Callable]:
    """
    Get all available tools as a dictionary mapping tool_key -> function.
    Only loads tools when they're actually requested.
    """
    available_tools = {}

    for tool_key in tool_registry.get_available_tools():
        tool_func = get_tool_function(tool_key)
        if tool_func:
            available_tools[tool_key] = tool_func

    return available_tools

def execute_tool(tool_key: str, **kwargs) -> Dict[str, Any]:
    """
    Execute a tool by key with dynamic loading.

    Args:
        tool_key: The tool identifier
        **kwargs: Tool arguments

    Returns:
        Tool execution result
    """
    tool_func = get_tool_function(tool_key)

    if not tool_func:
        return {
            "status": "error",
            "message": f"Tool '{tool_key}' not found or not available"
        }

    try:
        # Note: Tools get username from current_user global variable, not from parameters
        result = tool_func(**kwargs)

        # Ensure result is in the expected format
        if not isinstance(result, dict):
            result = {"status": "success", "data": result}

        return result

    except Exception as e:
        logger.error(f"Error executing tool '{tool_key}': {e}")
        return {
            "status": "error",
            "message": f"Tool execution failed: {str(e)}"
        }

# Backward compatibility: Create the AVAILABLE_TOOLS dictionary that agent.py expects
# But make it lazy-loaded
class LazyToolDict:
    """A dictionary that loads tools on demand."""

    def __init__(self):
        self._cache = {}

    def __getitem__(self, tool_key: str) -> Callable:
        if tool_key not in self._cache:
            tool_func = get_tool_function(tool_key)
            if tool_func is None:
                raise KeyError(f"Tool '{tool_key}' not found")
            self._cache[tool_key] = tool_func
        return self._cache[tool_key]

    def __contains__(self, tool_key: str) -> bool:
        return tool_key in tool_registry.get_available_tools()

    def get(self, tool_key: str, default=None):
        try:
            return self[tool_key]
        except KeyError:
            return default

    def keys(self):
        return tool_registry.get_available_tools()

    def copy(self):
        """Return a copy for unittest.mock.patch.dict compatibility."""
        # For testing: return empty dict so patch.dict can work
        # This allows tests to properly mock tools without loading from DB
        return {}

    def __iter__(self):
        """Make iterable for patch.dict compatibility."""
        return iter(self.keys())

    def items(self):
        """Return items for dict-like behavior."""
        return [(key, self[key]) for key in self.keys()]

    def values(self):
        """Return values for dict-like behavior."""
        return [self[key] for key in self.keys()]

    def __len__(self):
        """Return the number of available tools."""
        return len(self.keys())

    def __setitem__(self, tool_key: str, tool_func: Callable):
        """Allow setting tools (for testing)."""
        self._cache[tool_key] = tool_func

    def __delitem__(self, tool_key: str):
        """Allow deleting tools (for testing)."""
        if tool_key in self._cache:
            del self._cache[tool_key]

# Create the lazy-loaded tool dictionary for backward compatibility
AVAILABLE_TOOLS = LazyToolDict()

# Tool management functions
def reload_tool(tool_key: str) -> bool:
    """Reload a specific tool (useful for development)."""
    return tool_registry.reload_tool(tool_key)

def get_tool_info() -> Dict[str, Any]:
    """Get information about the tool system."""
    return tool_registry.get_tool_info()

def list_available_tools() -> Dict[str, str]:
    """List all available tools with their descriptions."""
    tools = {}
    for tool_key in tool_registry.get_available_tools():
        metadata = tool_registry.get_tool_metadata(tool_key)
        if metadata:
            tools[tool_key] = metadata.description
    return tools

def is_core_tool(tool_key: str) -> bool:
    """Check if a tool is a core tool."""
    return tool_key in tool_registry.get_core_tools()

# Legacy function stubs for any remaining imports (these were in the old tools.py)
# Now these become dynamic wrappers

def execute_web_search(query=None, **kwargs):
    """Legacy wrapper for web search tool."""
    if query is not None:
        kwargs['query'] = query
    return execute_tool('web_search', **kwargs)

def execute_get_weather_forecast(city=None, start_date=None, end_date=None, **kwargs):
    """Legacy wrapper for weather forecast tool."""
    if city is not None:
        kwargs['city'] = city
    if start_date is not None:
        kwargs['start_date'] = start_date
    if end_date is not None:
        kwargs['end_date'] = end_date
    return execute_tool('get_weather_forecast', **kwargs)

def execute_find_personal_variables(searchkey=None, username=None, **kwargs):
    """Legacy wrapper for personal variables tool."""
    # Note: username parameter is accepted for compatibility but ignored
    # Tool implementation uses current_user global for user context
    if searchkey is not None:
        kwargs['searchkey'] = searchkey
    return execute_tool('find_personal_variables', **kwargs)

def execute_recall_memories(keyword=None, username=None, **kwargs):
    """Legacy wrapper for recall memories tool."""
    # Note: username parameter is accepted for compatibility but ignored
    # Tool implementation uses current_user global for user context
    if keyword is not None:
        kwargs['keyword'] = keyword
    return execute_tool('recall_memories', **kwargs)

def execute_recall_memories_with_time(keyword=None, start_date=None, end_date=None, username=None, **kwargs):
    """Legacy wrapper for recall memories with time tool."""
    # Note: username parameter is accepted for compatibility but ignored
    # Tool implementation uses current_user global for user context
    if keyword is not None:
        kwargs['keyword'] = keyword
    if start_date is not None:
        kwargs['start_date'] = start_date
    if end_date is not None:
        kwargs['end_date'] = end_date
    return execute_tool('recall_memories_with_time', **kwargs)

def execute_get_conversations_by_topic(topic=None, username=None, **kwargs):
    """Legacy wrapper for conversations by topic tool."""
    # Note: username parameter is accepted for compatibility but ignored
    # Tool implementation uses current_user global for user context
    if topic is not None:
        kwargs['topic_name'] = topic
    return execute_tool('get_conversations_by_topic', **kwargs)

def execute_get_topics_by_conversation(conversation_id=None, username=None, **kwargs):
    """Legacy wrapper for topics by conversation tool."""
    # Note: username parameter is accepted for compatibility but ignored
    # Tool implementation uses current_user global for user context
    if conversation_id is not None:
        kwargs['conversation_id'] = conversation_id
    return execute_tool('get_topics_by_conversation', **kwargs)

def execute_get_conversation_summary(conversation_id=None, username=None, **kwargs):
    """Legacy wrapper for conversation summary tool."""
    # Note: username parameter is accepted for compatibility but ignored
    # Tool implementation uses current_user global for user context
    if conversation_id is not None:
        kwargs['conversation_id'] = conversation_id
    return execute_tool('get_conversation_summary', **kwargs)

def execute_get_topic_statistics(topic=None, username=None, **kwargs):
    """Legacy wrapper for topic statistics tool."""
    # Note: username parameter is accepted for compatibility but ignored
    # Tool implementation uses current_user global for user context
    if topic is not None:
        kwargs['topic'] = topic
    return execute_tool('get_topic_statistics', **kwargs)

def execute_get_user_conversations(limit=None, offset=None, username=None, **kwargs):
    """Legacy wrapper for user conversations tool."""
    # Note: username parameter is accepted for compatibility but ignored
    # Tool implementation uses current_user global for user context
    if limit is not None:
        kwargs['limit'] = limit
    if offset is not None:
        kwargs['offset'] = offset
    return execute_tool('get_user_conversations', **kwargs)

def execute_get_conversation_details(conversation_id=None, username=None, **kwargs):
    """Legacy wrapper for conversation details tool."""
    # Note: username parameter is accepted for compatibility but ignored
    # Tool implementation uses current_user global for user context
    if conversation_id is not None:
        kwargs['conversation_id'] = conversation_id
    return execute_tool('get_conversation_details', **kwargs)

def execute_search_conversations(query=None, limit=None, username=None, **kwargs):
    """Legacy wrapper for search conversations tool."""
    # Note: username parameter is accepted for compatibility but ignored
    # Tool implementation uses current_user global for user context
    if query is not None:
        kwargs['query'] = query
    if limit is not None:
        kwargs['limit'] = limit
    return execute_tool('search_conversations', **kwargs)

def execute_screenshot_from_url(url=None, **kwargs):
    """Legacy wrapper for screenshot tool."""
    if url is not None:
        kwargs['url'] = url
    return execute_tool('screenshot_from_url', **kwargs)

def execute_analyze_file(file_path=None, **kwargs):
    """Legacy wrapper for analyze file tool."""
    if file_path is not None:
        kwargs['file_path'] = file_path
    return execute_tool('analyze_file', **kwargs)

def execute_get_temporal_info(**kwargs):
    """Execute temporal info tool with dynamic loading."""
    return execute_tool('get_temporal_info', **kwargs)