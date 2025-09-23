"""
hippocampus/reference_frame.py

Handles fetching dynamic configuration data from the system database,
such as the list of enabled tools. This acts as a "frame of reference"
for the agent's capabilities at any given time.
"""
import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

# The system database path should be consistent
SYSTEM_DB_PATH = "hippocampus/system.db"

def get_system_db_connection() -> sqlite3.Connection | None:
    """Establishes a connection to the system database."""
    try:
        if not os.path.exists(SYSTEM_DB_PATH):
            logger.error(f"System database not found at {SYSTEM_DB_PATH}")
            return None
        conn = sqlite3.connect(SYSTEM_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Error connecting to system database: {e}")
        return None

def get_enabled_tools_from_db() -> list[dict]:
    """
    Fetches all enabled tools from the database and reconstructs them
    into the JSON-like structure required by the agent.
    """
    conn = get_system_db_connection()
    if not conn:
        return []

    tools_list = []
    try:
        cursor = conn.cursor()
        
        # Fetch all tools marked as enabled
        cursor.execute("SELECT tool_key, description FROM tools WHERE enabled = 1")
        enabled_tools = cursor.fetchall()

        for tool_row in enabled_tools:
            tool_key = tool_row['tool_key']
            
            # Fetch all parameters for the current tool
            cursor.execute(
                "SELECT name, type, description, is_required FROM tool_parameters WHERE tool_key = ?", 
                (tool_key,)
            )
            params = cursor.fetchall()
            
            properties = {}
            required = []
            for param_row in params:
                properties[param_row['name']] = {
                    "type": param_row['type'],
                    "description": param_row['description']
                }
                if param_row['is_required'] == 1:
                    required.append(param_row['name'])
            
            # Reconstruct the tool definition to match the required format
            tool_definition = {
                "type": "function",
                "function": {
                    "name": tool_key,
                    "description": tool_row['description'],
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            }
            tools_list.append(tool_definition)

    except sqlite3.Error as e:
        logger.error(f"Database error while fetching enabled tools: {e}")
    finally:
        if conn:
            conn.close()
            
    logger.debug(f"Loaded {len(tools_list)} enabled tools from the database.")
    return tools_list

def get_tool_catalog_for_selection() -> dict:
    """
    Get a simplified tool catalog organized by category for LLM tool selection.
    Returns tools grouped by functionality with brief descriptions.
    """
    conn = get_system_db_connection()
    if not conn:
        return {}

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT tool_key, description FROM tools WHERE enabled = 1 ORDER BY tool_key")
        enabled_tools = cursor.fetchall()

        # Group tools by category for better organization
        catalog = {
            "personal_data": [],
            "memory_recall": [],
            "external_data": [],
            "visual_analysis": [],
            "conversation_analysis": []
        }

        for tool in enabled_tools:
            tool_key = tool['tool_key']
            description = tool['description']

            # Categorize tools based on their function
            if 'personal' in tool_key or 'variable' in tool_key:
                catalog["personal_data"].append({"key": tool_key, "desc": description})
            elif any(x in tool_key for x in ['recall', 'memory', 'search_conversations']):
                catalog["memory_recall"].append({"key": tool_key, "desc": description})
            elif any(x in tool_key for x in ['weather', 'web_search']):
                catalog["external_data"].append({"key": tool_key, "desc": description})
            elif any(x in tool_key for x in ['screenshot', 'analyze_file']):
                catalog["visual_analysis"].append({"key": tool_key, "desc": description})
            elif any(x in tool_key for x in ['conversation', 'topic']):
                catalog["conversation_analysis"].append({"key": tool_key, "desc": description})

        return catalog

    except sqlite3.Error as e:
        logger.error(f"Database error while fetching tool catalog: {e}")
        return {}
    finally:
        if conn:
            conn.close()

def get_selected_tools(tool_keys: list[str]) -> list[dict]:
    """
    Get full tool definitions for specified tool keys only.
    This is used for the second phase after LLM selects which tools it needs.
    """
    conn = get_system_db_connection()
    if not conn:
        return []

    tools_list = []
    try:
        cursor = conn.cursor()

        # Create placeholders for the IN clause
        placeholders = ','.join('?' for _ in tool_keys)
        query = f"SELECT tool_key, description FROM tools WHERE enabled = 1 AND tool_key IN ({placeholders})"

        cursor.execute(query, tool_keys)
        selected_tools = cursor.fetchall()

        for tool_row in selected_tools:
            tool_key = tool_row['tool_key']

            # Fetch parameters for this specific tool
            cursor.execute(
                "SELECT name, type, description, is_required FROM tool_parameters WHERE tool_key = ?",
                (tool_key,)
            )
            params = cursor.fetchall()

            properties = {}
            required = []
            for param_row in params:
                properties[param_row['name']] = {
                    "type": param_row['type'],
                    "description": param_row['description']
                }
                if param_row['is_required'] == 1:
                    required.append(param_row['name'])

            # Build tool definition
            tool_definition = {
                "type": "function",
                "function": {
                    "name": tool_key,
                    "description": tool_row['description'],
                    "parameters": {
                        "type": "object",
                        "properties": properties,
                        "required": required
                    }
                }
            }
            tools_list.append(tool_definition)

    except sqlite3.Error as e:
        logger.error(f"Database error while fetching selected tools: {e}")
    finally:
        if conn:
            conn.close()

    logger.debug(f"Loaded {len(tools_list)} selected tools from database.")
    return tools_list 