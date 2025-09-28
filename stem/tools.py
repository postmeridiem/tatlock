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
        # Add username to memory-related tools if not present
        if tool_key in ['recall_memories', 'recall_memories_with_time', 'find_personal_variables',
                       'get_conversations_by_topic', 'get_topics_by_conversation',
                       'get_conversation_summary', 'get_topic_statistics',
                       'get_user_conversations', 'get_conversation_details', 'search_conversations']:
            if 'username' not in kwargs:
                kwargs['username'] = 'admin'  # Default username

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

def execute_web_search(**kwargs):
    """Legacy wrapper for web search tool."""
    return execute_tool('web_search', **kwargs)

def execute_get_weather_forecast(**kwargs):
    """Legacy wrapper for weather forecast tool."""
    return execute_tool('get_weather_forecast', **kwargs)

def execute_find_personal_variables(**kwargs):
    """Legacy wrapper for personal variables tool."""
    return execute_tool('find_personal_variables', **kwargs)

def execute_recall_memories(**kwargs):
    """Legacy wrapper for recall memories tool."""
    return execute_tool('recall_memories', **kwargs)

def execute_recall_memories_with_time(**kwargs):
    """Legacy wrapper for recall memories with time tool."""
    return execute_tool('recall_memories_with_time', **kwargs)

def execute_get_conversations_by_topic(**kwargs):
    """Legacy wrapper for conversations by topic tool."""
    return execute_tool('get_conversations_by_topic', **kwargs)

def execute_get_topics_by_conversation(**kwargs):
    """Legacy wrapper for topics by conversation tool."""
    return execute_tool('get_topics_by_conversation', **kwargs)

def execute_get_conversation_summary(**kwargs):
    """Legacy wrapper for conversation summary tool."""
    return execute_tool('get_conversation_summary', **kwargs)

def execute_get_topic_statistics(**kwargs):
    """Legacy wrapper for topic statistics tool."""
    return execute_tool('get_topic_statistics', **kwargs)

def execute_get_user_conversations(**kwargs):
    """Legacy wrapper for user conversations tool."""
    return execute_tool('get_user_conversations', **kwargs)

def execute_get_conversation_details(**kwargs):
    """Legacy wrapper for conversation details tool."""
    return execute_tool('get_conversation_details', **kwargs)

def execute_search_conversations(**kwargs):
    """Legacy wrapper for search conversations tool."""
    return execute_tool('search_conversations', **kwargs)

def execute_screenshot_from_url(**kwargs):
    """Legacy wrapper for screenshot tool."""
    return execute_tool('screenshot_from_url', **kwargs)

def execute_analyze_file(**kwargs):
    """Legacy wrapper for analyze file tool."""
    return execute_tool('analyze_file', **kwargs)

def execute_get_temporal_info(**kwargs):
    """Execute temporal info tool with dynamic loading."""
    return execute_tool('get_temporal_info', **kwargs)