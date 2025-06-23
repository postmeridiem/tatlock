"""
hippocampus/get_conversation_summary_tool.py

Tool for retrieving conversation summaries.
"""

import logging
from hippocampus.recall import get_conversation_summary
from stem.models import UserModel
from stem.security import current_user

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_conversation_summary(conversation_id: str) -> dict:
    """
    Get a comprehensive summary of a conversation including its topics and key interactions.
    
    Args:
        conversation_id (str): The conversation ID to summarize.
        
    Returns:
        dict: Status and conversation summary or message.
    """
    try:
        user = current_user
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        summary = get_conversation_summary(conversation_id, user)
        
        if not summary:
            return {
                "status": "success", 
                "data": {}, 
                "message": f"No conversation found with ID '{conversation_id}'."
            }
        
        return {"status": "success", "data": summary}
        
    except Exception as e:
        logger.error(f"Error getting conversation summary for '{conversation_id}': {e}")
        return {"status": "error", "message": f"Conversation summary retrieval failed for conversation '{conversation_id}': {e}"} 