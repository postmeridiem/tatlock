"""
hippocampus/find_personal_variables_tool.py

Tool for finding personal variables in the user's database.
"""

import logging
from hippocampus.database import query_personal_variables

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_find_personal_variables(searchkey: str, username: str = "admin") -> dict:
    """
    Find and retrieve personal properties of the current user by searching a local database.
    
    Args:
        searchkey (str): The key for the personal variable to find (e.g., 'name', 'hometown', 'age').
        username (str, optional): The username whose database to search. Defaults to "admin".
        
    Returns:
        dict: Status and data or message.
    """
    try:
        results = query_personal_variables(searchkey, username)
        
        if not results:
            return {
                "status": "success", 
                "data": [], 
                "message": f"I don't have any information about '{searchkey}'."
            }
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error finding personal variables for '{searchkey}' for user '{username}': {e}")
        return {"status": "error", "message": f"Database query failed for searchkey '{searchkey}' and user '{username}': {e}"} 