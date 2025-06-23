"""
hippocampus/get_conversations_by_topic_tool.py

Tool for retrieving conversations by topic.
"""

import logging
from hippocampus.recall import get_conversations_by_topic
from stem.models import UserModel
from stem.security import current_user

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_get_conversations_by_topic(topic_name: str) -> dict:
    """
    Find all conversations that contain a specific topic, with metadata about when the topic appeared.
    
    Args:
        topic_name (str): The topic name to search for conversations.
        
    Returns:
        dict: Status and topic results or message.
    """
    try:
        user = current_user
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        results = get_conversations_by_topic(topic_name, user)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": f"No conversations found for topic '{topic_name}'."
            }
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error getting conversations for topic '{topic_name}': {e}")
        return {"status": "error", "message": f"Topic-based conversation retrieval failed for topic '{topic_name}': {e}"} 