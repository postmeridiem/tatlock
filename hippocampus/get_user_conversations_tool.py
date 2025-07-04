"""
hippocampus/get_user_conversations_tool.py

Tool for retrieving user conversations.
"""

import logging
from hippocampus.recall import get_user_conversations
from stem.models import UserModel
from stem.security import current_user

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_user_conversations(limit: int = 50) -> dict:
    """
    List all conversations for the current user.
    
    Args:
        limit (int, optional): Maximum number of conversations to return. Defaults to 50.
        
    Returns:
        dict: Status and conversation list or message.
    """
    try:
        user = current_user
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        results = get_user_conversations(user, limit)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": "No conversations found."
            }
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error getting user conversations with limit {limit}: {e}")
        return {"status": "error", "message": f"User conversations retrieval failed with limit {limit}: {e}"} 