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
    Queries the database to get all enabled base instructions for the system prompt.
    Args:
        username (str): The username whose database to query. Defaults to "admin".
    Returns:
        list[str]: Enabled instructions in order.
    """
    if username == "":
        raise ValueError("Username is required")
    query = "SELECT instruction FROM rise_and_shine WHERE enabled = 1 ORDER BY id;"
    
    results = execute_user_query(username, query)
    instructions = [row['instruction'] for row in results]
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