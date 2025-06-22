"""
hippocampus/recall_memories_with_time_tool.py

Tool for recalling memories with time-based filtering.
"""

import logging
from hippocampus.recall import recall_memories_with_time

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_recall_memories_with_time(keyword: str, username: str = "admin", start_date: str | None = None, end_date: str | None = None) -> dict:
    """
    Recall past conversations by searching for a keyword and limiting to a date or date range.
    
    Args:
        keyword (str): The keyword to search for in memory (user prompt, reply, or topic).
        username (str, optional): The username whose database to search. Defaults to "admin".
        start_date (str | None, optional): Start date (YYYY-MM-DD) to limit the search. Defaults to None.
        end_date (str | None, optional): End date (YYYY-MM-DD) to limit the search. Defaults to None.
        
    Returns:
        dict: Status and recall results or message.
    """
    try:
        results = recall_memories_with_time(keyword, username, start_date, end_date)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": f"No memories found for '{keyword}' in the specified time range."
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
        logger.error(f"Error recalling memories with time for '{keyword}': {e}")
        return {"status": "error", "message": f"Time-based memory recall failed: {e}"} 