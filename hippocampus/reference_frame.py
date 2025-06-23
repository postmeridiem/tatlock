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