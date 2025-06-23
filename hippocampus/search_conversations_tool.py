"""
hippocampus/search_conversations_tool.py

Tool for searching conversations in the user's database.
"""

import logging
from hippocampus.recall import search_conversations
from stem.security import current_user

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_search_conversations(query: str, limit: int = 20) -> dict:
    """
    Search conversations by title or conversation ID for the current user.
    
    Args:
        query (str): The search query to match against conversation titles or IDs.
        limit (int, optional): Maximum number of results to return. Defaults to 20.
        
    Returns:
        dict: Status and search results or error message.
    """
    try:
        user = current_user
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        results = search_conversations(user, query, limit)
        
        return {
            "status": "success",
            "data": {
                "conversations": results,
                "count": len(results)
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching conversations for query '{query}' with limit {limit}: {e}")
        return {"status": "error", "message": f"Conversation search failed for query '{query}' with limit {limit}: {e}"} 