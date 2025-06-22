"""
hippocampus/get_conversation_details_tool.py

Tool for retrieving detailed information about a specific conversation.
"""

import logging
from hippocampus.recall import get_conversation_details

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_conversation_details(conversation_id: str, username: str = "admin") -> dict:
    """
    Get detailed information about a specific conversation including its topics and metadata.
    
    Args:
        conversation_id (str): The conversation ID to get details for.
        username (str, optional): The username whose database to search. Defaults to "admin".
        
    Returns:
        dict: Status and conversation details or message.
    """
    try:
        details = get_conversation_details(conversation_id, username)
        
        if not details:
            return {
                "status": "success", 
                "data": {}, 
                "message": f"Conversation '{conversation_id}' not found."
            }
        
        return {"status": "success", "data": details}
        
    except Exception as e:
        logger.error(f"Error getting details for conversation '{conversation_id}': {e}")
        return {"status": "error", "message": f"Conversation detail retrieval failed: {e}"} 