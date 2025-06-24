"""
hippocampus/database.py

Database access functions for Tatlock persistent memory and personal variables.
Now supports user-specific databases.
"""

import sqlite3
import os
from hippocampus.user_database import execute_user_query, get_database_connection


def get_base_instructions(username: str = "") -> list[str]:
    """
    Gets the complete system instructions by combining base prompts with enabled tool prompts.
    
    IMPORTANT: This function reads from the system database (hippocampus/system.db), 
    NOT from user databases. The system prompts include base instructions from rise_and_shine
    plus dynamic prompts from enabled tools in the tools table.
    
    Args:
        username (str): The username (not used, kept for compatibility).
    Returns:
        list[str]: Complete system instructions including base prompts and enabled tool prompts.
    """
    # Read from system database instead of user database
    system_db_path = "hippocampus/system.db"
    if not os.path.exists(system_db_path):
        raise FileNotFoundError(f"System database not found at {system_db_path}")
    
    conn = sqlite3.connect(system_db_path)
    cursor = conn.cursor()
    
    # Get base system prompts from rise_and_shine table
    cursor.execute("""
        SELECT instruction 
        FROM rise_and_shine 
        WHERE enabled = 1 
        ORDER BY id
    """)
    base_prompts = [row[0] for row in cursor.fetchall()]
    
    # Get enabled tool prompts
    cursor.execute("""
        SELECT prompts 
        FROM tools 
        WHERE enabled = 1 AND prompts IS NOT NULL AND prompts != ''
        ORDER BY tool_key
    """)
    tool_prompts = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    # Combine all prompts
    all_prompts = base_prompts + tool_prompts
    
    # Add explicit guidance for topic analysis
    all_prompts.append(
        "When the user asks about what topics are discussed most, trending subjects, what we talk about a lot, or what are our main discussion themes, use the memory_insights tool with analysis_type='topics'."
    )
    
    return all_prompts


def query_personal_variables(searchkey: str, username: str = "") -> list[dict]:
    """
    Finds a personal variable by its alias/key.
    Args:
        searchkey (str): The key to search for.
        username (str): The username whose database to query. Defaults to "admin".
    Returns:
        list[dict]: Matching personal variable values.
    """
    if username == "":
        raise ValueError("Username is required")
    query = ("SELECT pv.value FROM personal_variables AS pv "
             "JOIN personal_variables_join AS pvj ON pv.id = pvj.variable_id "
             "JOIN personal_variables_keys AS pvk ON pvj.key_id = pvk.id "
             "WHERE pvk.key = ?;")
    return execute_user_query(username, query, (searchkey,))