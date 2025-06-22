"""
hippocampus/tools/get_topics_by_conversation_tool.py

Conversation topic analysis functionality.
"""

import logging
from hippocampus.recall import get_topics_by_conversation

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_topics_by_conversation(conversation_id: str, username: str = "admin") -> dict:
    """
    Get all topics that appear in a specific conversation, with metadata about topic frequency.
    
    Args:
        conversation_id (str): The conversation ID to analyze for topics.
        username (str, optional): The username whose database to search. Defaults to "admin".
        
    Returns:
        dict: Status and topic results or message.
    """
    try:
        results = get_topics_by_conversation(conversation_id, username)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": f"No topics found for conversation '{conversation_id}'."
            }
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error getting topics for conversation '{conversation_id}': {e}")
        return {"status": "error", "message": f"Conversation topic analysis failed: {e}"} 