"""
stem/tools.py

Defines callable tools for the Tatlock agent, including weather, web search, recall, and personal variable lookup.
"""

import logging

# Import tools from their respective modules
from cerebellum.web_search_tool import execute_web_search
from cerebellum.weather_tool import execute_get_weather_forecast
from hippocampus.find_personal_variables_tool import execute_find_personal_variables
from hippocampus.recall_memories_tool import execute_recall_memories
from hippocampus.recall_memories_with_time_tool import execute_recall_memories_with_time
from hippocampus.get_conversations_by_topic_tool import execute_get_conversations_by_topic
from hippocampus.get_topics_by_conversation_tool import execute_get_topics_by_conversation
from hippocampus.get_conversation_summary_tool import execute_get_conversation_summary
from hippocampus.get_topic_statistics_tool import execute_get_topic_statistics
from hippocampus.get_user_conversations_tool import execute_get_user_conversations
from hippocampus.get_conversation_details_tool import execute_get_conversation_details
from hippocampus.search_conversations_tool import execute_search_conversations
from hippocampus.memory_insights_tool import execute_memory_insights
from hippocampus.memory_cleanup_tool import execute_memory_cleanup
from hippocampus.memory_export_tool import execute_memory_export
from occipital.take_screenshot_from_url_tool import execute_take_screenshot_from_url, analyze_screenshot_file
from hippocampus.reference_frame import get_enabled_tools_from_db

# Set up logging for this module
logger = logging.getLogger(__name__)

# The TOOLS list is now dynamically loaded from the database
TOOLS = get_enabled_tools_from_db()

# --- Tool Execution Wrappers ---
# These wrappers are necessary to align the function signatures with what the
# TOOL_REGISTRY expects, especially for passing the current user context.
# They are an intermediary between the agent's tool call and the underlying tool function.

async def execute_screenshot_from_url(url: str, session_id: str, username: str = "admin") -> dict:
    """
    Execute screenshot_from_url tool.
    """
    return await execute_take_screenshot_from_url(url, session_id, username)


def execute_analyze_file(session_id: str, original_prompt: str, username: str = "admin") -> dict:
    """
    Execute analyze_file tool.
    """
    return analyze_screenshot_file(session_id, original_prompt, username)


def get_conversation_details(conversation_id: str):
    """Get conversation details."""
    return execute_get_conversation_details(conversation_id)


def search_conversations(query: str, limit: int = 20):
    """Search conversations."""
    return execute_search_conversations(query=query, limit=limit)


# --- Tool Registry ---

# A master map of all possible tool functions in the system.
# This allows the TOOL_REGISTRY to be built dynamically based on which tools
# are enabled in the database.
ALL_TOOL_FUNCTIONS = {
    "get_weather_forecast": execute_get_weather_forecast,
    "web_search": execute_web_search,
    "find_personal_variables": execute_find_personal_variables,
    "recall_memories": execute_recall_memories,
    "recall_memories_with_time": execute_recall_memories_with_time,
    "get_conversations_by_topic": execute_get_conversations_by_topic,
    "get_topics_by_conversation": execute_get_topics_by_conversation,
    "get_conversation_summary": execute_get_conversation_summary,
    "get_topic_statistics": execute_get_topic_statistics,
    "get_user_conversations": execute_get_user_conversations,
    "get_conversation_details": get_conversation_details,
    "search_conversations": search_conversations,
    "memory_insights": execute_memory_insights,
    "memory_cleanup": execute_memory_cleanup,
    "memory_export": execute_memory_export,
    "screenshot_from_url": execute_screenshot_from_url,
    "analyze_file": execute_analyze_file,
}

# The TOOL_REGISTRY is now built dynamically from the database.
# It maps the enabled tool names to their function objects and full definitions.
TOOL_REGISTRY = {}
for tool_definition in TOOLS:
    tool_name = tool_definition.get("function", {}).get("name")
    if not tool_name:
        continue
        
    if tool_name in ALL_TOOL_FUNCTIONS:
        TOOL_REGISTRY[tool_name] = {
            "function": ALL_TOOL_FUNCTIONS[tool_name],
            "definition": tool_definition
        }
    else:
        logger.warning(
            f"Tool '{tool_name}' is enabled in the database but has no "
            f"corresponding function in ALL_TOOL_FUNCTIONS."
        )