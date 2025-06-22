"""
hippocampus/search_conversations_tool.py

Tool for searching conversations in the user's database.
"""

import logging
from hippocampus.recall import search_conversations

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_search_conversations(query: str, username: str = "admin", limit: int = 20) -> dict:
    """
    Search conversations by title or conversation ID for the current user.
    
    Args:
        query (str): The search query to match against conversation titles or IDs.
        username (str, optional): The username whose database to search. Defaults to "admin".
        limit (int, optional): Maximum number of results to return. Defaults to 20.
        
    Returns:
        dict: Status and search results or error message.
    """
    try:
        results = search_conversations(query, username, limit)
        
        return {
            "status": "success",
            "data": {
                "conversations": results,
                "count": len(results)
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching conversations for '{query}': {e}")
        return {
            "status": "error", 
            "message": f"Conversation search failed: {e}",
            "data": {"conversations": [], "count": 0}
        } 