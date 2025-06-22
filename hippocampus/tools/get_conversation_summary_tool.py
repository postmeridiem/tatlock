"""
hippocampus/tools/get_conversation_summary_tool.py

Conversation summary generation functionality.
"""

import logging
from hippocampus.recall import get_conversation_summary

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_conversation_summary(conversation_id: str, username: str = "admin") -> dict:
    """
    Get a comprehensive summary of a conversation including its topics, duration, and key interactions.
    
    Args:
        conversation_id (str): The conversation ID to summarize.
        username (str, optional): The username whose database to search. Defaults to "admin".
        
    Returns:
        dict: Status and conversation summary or message.
    """
    try:
        summary = get_conversation_summary(conversation_id, username)
        
        if not summary:
            return {
                "status": "success", 
                "data": {}, 
                "message": f"Conversation '{conversation_id}' not found."
            }
        
        return {"status": "success", "data": summary}
        
    except Exception as e:
        logger.error(f"Error getting summary for conversation '{conversation_id}': {e}")
        return {"status": "error", "message": f"Conversation summary generation failed: {e}"} 