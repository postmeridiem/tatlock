"""
hippocampus/recall_memories_tool.py

Tool for recalling memories from the user's database.
"""

import logging
from hippocampus.recall import recall_memories

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_recall_memories(keyword: str, username: str = "admin") -> dict:
    """
    Recall past conversations by searching for a keyword in the user's prompt, the AI's reply, or the topic name.
    
    Args:
        keyword (str): The keyword to search for in memory (user prompt, reply, or topic).
        username (str, optional): The username whose database to search. Defaults to "admin".
        
    Returns:
        dict: Status and recall results or message.
    """
    try:
        results = recall_memories(keyword, username)
        
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
        logger.error(f"Error recalling memories for '{keyword}': {e}")
        return {"status": "error", "message": f"Memory recall failed: {e}"} 