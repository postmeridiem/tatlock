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
from occipital.take_screenshot_from_url_tool import execute_take_screenshot_from_url, analyze_screenshot_file

# Set up logging for this module
logger = logging.getLogger(__name__)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_personal_variables",
            "description": "Finds and retrieves personal properties of the current user (e.g., name, first name, last name, age, domicile, city, country) by searching a local database. Provide the key to search for.",
            "parameters": {
                "type": "object",
                "properties": {
                    "searchkey": {
                        "type": "string",
                        "description": "The key for the personal variable to find."
                    }
                },
                "required": ["searchkey"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather_forecast",
            "description": "Get the weather forecast for a specific city and date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name."
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD). Optional."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD). Optional."
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Perform a web search using Google Custom Search API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to send to the search engine."
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memories",
            "description": "Recall past conversations by searching for a keyword in the user's prompt, the AI's reply, or the topic name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The keyword to search for in memory (user prompt, reply, or topic)."
                    }
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall_memories_with_time",
            "description": "Recall past conversations by searching for a keyword and limiting to a date or date range (YYYY-MM-DD).",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The keyword to search for in memory (user prompt, reply, or topic)."
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD) to limit the search. Optional."
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD) to limit the search. Optional."
                    }
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_conversations_by_topic",
            "description": "Find all conversations that contain a specific topic, with metadata about when the topic appeared.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic_name": {
                        "type": "string",
                        "description": "The topic name to search for conversations."
                    }
                },
                "required": ["topic_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_topics_by_conversation",
            "description": "Get all topics that appear in a specific conversation, with metadata about topic frequency.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {
                        "type": "string",
                        "description": "The conversation ID to analyze for topics."
                    }
                },
                "required": ["conversation_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_conversation_summary",
            "description": "Get a comprehensive summary of a conversation including its topics, duration, and key interactions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {
                        "type": "string",
                        "description": "The conversation ID to summarize."
                    }
                },
                "required": ["conversation_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_topic_statistics",
            "description": "Get statistics about all topics across conversations, including frequency and conversation count.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_conversations",
            "description": "Get all conversations for the current user, ordered by most recent activity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of conversations to return. Defaults to 50."
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_conversation_details",
            "description": "Get detailed information about a specific conversation including its topics and metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "conversation_id": {
                        "type": "string",
                        "description": "The conversation ID to get details for."
                    }
                },
                "required": ["conversation_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_conversations",
            "description": "Search conversations by title or conversation ID for the current user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to match against conversation titles or IDs."
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return. Defaults to 20."
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "screenshot_from_url",
            "description": "Take a full-page screenshot of a webpage and save it to the user's shortterm storage. Useful for capturing web content for analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the webpage to capture as a screenshot."
                    },
                    "session_id": {
                        "type": "string",
                        "description": "A unique session identifier for this screenshot. Use a descriptive name or timestamp."
                    }
                },
                "required": ["url", "session_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_file",
            "description": "Analyze a file stored in the user's shortterm storage. If it's an image, interpret and summarize the content, providing insights relevant to the original prompt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The session ID of the file to analyze (same as used when taking screenshot)."
                    },
                    "original_prompt": {
                        "type": "string",
                        "description": "The original user prompt that led to this file being created, for context in analysis."
                    }
                },
                "required": ["session_id", "original_prompt"],
            },
        },
    },
]


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


# --- Tool Dispatcher ---
AVAILABLE_TOOLS = {
    "web_search": execute_web_search,
    "find_personal_variables": execute_find_personal_variables,
    "get_weather_forecast": execute_get_weather_forecast,
    "recall_memories": execute_recall_memories,
    "recall_memories_with_time": execute_recall_memories_with_time,
    "get_conversations_by_topic": execute_get_conversations_by_topic,
    "get_topics_by_conversation": execute_get_topics_by_conversation,
    "get_conversation_summary": execute_get_conversation_summary,
    "get_topic_statistics": execute_get_topic_statistics,
    "get_user_conversations": execute_get_user_conversations,
    "get_conversation_details": execute_get_conversation_details,
    "search_conversations": execute_search_conversations,
    "screenshot_from_url": execute_screenshot_from_url,
    "analyze_file": execute_analyze_file,
}

# Add missing functions that tests are trying to mock
def query_personal_variables(searchkey: str, username: str = "admin"):
    """Query personal variables from the database."""
    return execute_find_personal_variables(searchkey, username)

def recall_memories(keyword: str, username: str = "admin"):
    """Recall memories by keyword."""
    return execute_recall_memories(keyword, username)

def recall_memories_with_time(keyword: str, username: str = "admin", start_date: str | None = None, end_date: str | None = None):
    """Recall memories by keyword with time filter."""
    return execute_recall_memories_with_time(keyword, username, start_date, end_date)

def get_conversations_by_topic(topic_name: str, username: str = "admin"):
    """Get conversations by topic."""
    return execute_get_conversations_by_topic(topic_name, username)

def get_topics_by_conversation(conversation_id: str, username: str = "admin"):
    """Get topics by conversation."""
    return execute_get_topics_by_conversation(conversation_id, username)

def get_conversation_summary(conversation_id: str, username: str = "admin"):
    """Get conversation summary."""
    return execute_get_conversation_summary(conversation_id, username)

def get_topic_statistics(username: str = "admin"):
    """Get topic statistics."""
    return execute_get_topic_statistics(username)

def get_user_conversations(username: str = "admin", limit: int = 10):
    """Get user conversations."""
    return execute_get_user_conversations(username, limit)

def get_conversation_details(conversation_id: str, username: str = "admin"):
    """Get conversation details."""
    return execute_get_conversation_details(conversation_id, username)

def search_conversations(query: str, username: str = "admin"):
    """Search conversations."""
    return execute_search_conversations(query, username)