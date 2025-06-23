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
    Queries the system database to get all enabled base instructions for the system prompt.
    
    IMPORTANT: This function reads from the system database (hippocampus/system.db), 
    NOT from user databases. The rise_and_shine table contains global Tatlock prompts
    that all users share. These instructions define Tatlock's personality, behavior,
    and tool usage guidelines.
    
    Args:
        username (str): The username (not used, kept for compatibility).
    Returns:
        list[str]: Enabled instructions in order.
    """
    # Read from system database instead of user database
    system_db_path = "hippocampus/system.db"
    if not os.path.exists(system_db_path):
        raise FileNotFoundError(f"System database not found at {system_db_path}")
    
    conn = sqlite3.connect(system_db_path)
    cursor = conn.cursor()
    
    query = "SELECT instruction FROM rise_and_shine WHERE enabled = 1 ORDER BY id;"
    cursor.execute(query)
    results = cursor.fetchall()
    
    conn.close()
    
    instructions = [row[0] for row in results]
    # Add explicit guidance for topic analysis
    instructions.append(
        "When the user asks about what topics are discussed most, trending subjects, what we talk about a lot, or what are our main discussion themes, use the memory_insights tool with analysis_type='topics'."
    )
    return instructions


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