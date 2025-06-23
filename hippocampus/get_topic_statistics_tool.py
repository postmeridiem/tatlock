"""
hippocampus/get_topic_statistics_tool.py

Tool for retrieving topic statistics.
"""

import logging
from hippocampus.recall import get_topic_statistics
from stem.models import UserModel
from stem.security import current_user

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_topic_statistics() -> dict:
    """
    Get statistics about topics across all conversations, including frequency and conversation counts.
    
    Returns:
        dict: Status and topic statistics or message.
    """
    try:
        user = current_user
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        results = get_topic_statistics(user)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": "No topic statistics available."
            }
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error getting topic statistics: {e}")
        return {"status": "error", "message": f"Topic statistics retrieval failed: {e}"} 