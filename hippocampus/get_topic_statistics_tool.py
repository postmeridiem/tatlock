"""
hippocampus/get_topic_statistics_tool.py

Topic statistics and analytics functionality.
"""

import logging
from hippocampus.recall import get_topic_statistics

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_topic_statistics(username: str = "admin") -> dict:
    """
    Get statistics about all topics across conversations, including frequency and conversation count.
    
    Args:
        username (str, optional): The username whose database to search. Defaults to "admin".
        
    Returns:
        dict: Status and topic statistics or message.
    """
    try:
        results = get_topic_statistics(username)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": "No topic statistics available."
            }
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error getting topic statistics for user '{username}': {e}")
        return {"status": "error", "message": f"Topic statistics retrieval failed: {e}"} 