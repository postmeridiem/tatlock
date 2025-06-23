"""
hippocampus/get_topics_by_conversation_tool.py

Tool for retrieving topics by conversation.
"""

import logging
from hippocampus.recall import get_topics_by_conversation
from stem.models import UserModel
from stem.current_user_context import get_current_user_ctx

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_topics_by_conversation(conversation_id: str) -> dict:
    """
    Find all topics that appear in a specific conversation, with metadata about when they appeared.
    
    Args:
        conversation_id (str): The conversation ID to search for topics.
        
    Returns:
        dict: Status and topic results or message.
    """
    try:
        user = get_current_user_ctx()
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        results = get_topics_by_conversation(conversation_id, user)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": f"No topics found for conversation '{conversation_id}'."
            }
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error getting topics for conversation '{conversation_id}': {e}")
        return {"status": "error", "message": f"Conversation-based topic retrieval failed for conversation '{conversation_id}': {e}"} 