"""
hippocampus/recall_memories_tool.py

Tool for recalling memories from the user's database.
"""

import logging
from hippocampus.recall import recall_memories
from stem.models import UserModel
from stem.current_user_context import get_current_user_ctx

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_recall_memories(keyword: str) -> dict:
    """
    Recall past conversations by searching for a keyword in the user's prompt, the AI's reply, or the topic name.
    
    Args:
        keyword (str): The keyword to search for in memory (user prompt, reply, or topic).
        
    Returns:
        dict: Status and recall results or message.
    """
    try:
        user = get_current_user_ctx()
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        results = recall_memories(user, keyword)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": f"No memories found for '{keyword}'."
            }
        
        # Truncate long text fields for readability
        for r in results:
            for k in ("user_prompt", "llm_reply"):
                if r[k] is None:
                    r[k] = ""
                elif len(r[k]) > 200:
                    r[k] = r[k][:200] + "..."
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error recalling memories for keyword '{keyword}': {e}")
        return {"status": "error", "message": f"Memory recall failed for keyword '{keyword}': {e}"} 