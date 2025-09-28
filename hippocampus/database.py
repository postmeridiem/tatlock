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
    
    # LEAN SYSTEM: Separate core vs extended capabilities
    # Core tools (always available): memory, personal data
    # Extended tools (catalog-based): weather, web search, screenshots, etc.

    # Define core tools that should always be immediately accessible
    CORE_TOOLS = [
        'recall_memories',
        'recall_memories_with_time',
        'find_personal_variables',
        'get_temporal_info'
    ]

    # Get core tool prompts (always loaded for immediate access)
    placeholders = ','.join(['?' for _ in CORE_TOOLS])
    cursor.execute(f"""
        SELECT prompts FROM tools
        WHERE enabled = 1 AND prompts IS NOT NULL AND prompts != ''
        AND tool_key IN ({placeholders})
        ORDER BY tool_key
    """, CORE_TOOLS)
    core_tool_prompts = [row[0] for row in cursor.fetchall()]

    conn.close()

    # Add current timestamp for temporal context
    from datetime import datetime
    now = datetime.now()
    timestamp_prompt = f"Current date and time: {now.strftime('%A, %B %d, %Y at %I:%M %p')}"

    # Combine base prompts with core tool prompts and timestamp
    # This reduces overhead from 27 prompts to ~8 prompts (4 base + 3 core tools + timestamp)
    all_prompts = base_prompts + core_tool_prompts + [timestamp_prompt]

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