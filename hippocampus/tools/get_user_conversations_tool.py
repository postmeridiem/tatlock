"""
hippocampus/tools/get_user_conversations_tool.py

User conversation listing functionality.
"""

import logging
from hippocampus.recall import get_user_conversations

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_user_conversations(username: str = "admin", limit: int = 50) -> dict:
    """
    Get all conversations for the current user, ordered by most recent activity.
    
    Args:
        username (str, optional): The username whose database to search. Defaults to "admin".
        limit (int, optional): Maximum number of conversations to return. Defaults to 50.
        
    Returns:
        dict: Status and conversation list or message.
    """
    try:
        results = get_user_conversations(username, limit)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": "No conversations found."
            }
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error getting conversations for user '{username}': {e}")
        return {"status": "error", "message": f"User conversation retrieval failed: {e}"} 