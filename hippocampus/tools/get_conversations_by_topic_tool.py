"""
hippocampus/tools/get_conversations_by_topic_tool.py

Topic-based conversation retrieval functionality.
"""

import logging
from hippocampus.recall import get_conversations_by_topic

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_conversations_by_topic(topic_name: str, username: str = "admin") -> dict:
    """
    Find all conversations that contain a specific topic, with metadata about when the topic appeared.
    
    Args:
        topic_name (str): The topic name to search for conversations.
        username (str, optional): The username whose database to search. Defaults to "admin".
        
    Returns:
        dict: Status and topic results or message.
    """
    try:
        results = get_conversations_by_topic(topic_name, username)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": f"No conversations found for topic '{topic_name}'."
            }
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error getting conversations for topic '{topic_name}': {e}")
        return {"status": "error", "message": f"Topic-based conversation retrieval failed: {e}"} 