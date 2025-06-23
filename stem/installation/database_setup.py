"""
stem/installation/database_setup.py

Database setup utilities for Tatlock.
Provides functions to create tables for system.db (authentication) and longterm.db (memory).
Assumes clean installs only - no migration support.
"""

import sqlite3
import os
import logging
from typing import Any

# Set up logging for this module
logger = logging.getLogger(__name__)

SYSTEM_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS passwords (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_roles (
    username TEXT,
    role_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, role_id),
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_groups (
    username TEXT,
    group_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, group_id),
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tools (
    tool_key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    module TEXT NOT NULL,
    function_name TEXT NOT NULL,
    enabled INTEGER DEFAULT 0 NOT NULL
);

CREATE TABLE IF NOT EXISTS tool_parameters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_key TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    is_required INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY (tool_key) REFERENCES tools (tool_key) ON DELETE CASCADE
);
"""

LONGTERM_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    interaction_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    user_prompt TEXT NOT NULL,
    llm_reply TEXT NOT NULL,
    full_conversation_history TEXT
);

CREATE TABLE IF NOT EXISTS topics (
    topic_id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_topics (
    interaction_id TEXT,
    topic_id INTEGER,
    PRIMARY KEY (interaction_id, topic_id),
    FOREIGN KEY (interaction_id) REFERENCES memories (interaction_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conversation_topics (
    conversation_id TEXT,
    topic_id INTEGER,
    first_occurrence TEXT NOT NULL,
    last_occurrence TEXT NOT NULL,
    topic_count INTEGER DEFAULT 1,
    PRIMARY KEY (conversation_id, topic_id),
    FOREIGN KEY (conversation_id) REFERENCES memories (conversation_id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES topics (topic_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conversations (
    conversation_id TEXT PRIMARY KEY,
    title TEXT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    message_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS rise_and_shine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instruction TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS personal_variables_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS personal_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS personal_variables_join (
    key_id INTEGER,
    variable_id INTEGER,
    PRIMARY KEY (key_id, variable_id),
    FOREIGN KEY (key_id) REFERENCES personal_variables_keys (id) ON DELETE CASCADE,
    FOREIGN KEY (variable_id) REFERENCES personal_variables (id) ON DELETE CASCADE
);
"""

def _migrate_tools_table_schema(cursor: sqlite3.Cursor):
    """
    Migrates the tools table from a single 'module' column to separate
    'module' and 'function_name' columns.
    """
    try:
        # Check if migration is needed by looking for the old column structure
        cursor.execute("PRAGMA table_info(tools)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'module' in columns and 'function_name' not in columns:
            logger.info("Old 'tools' table schema detected. Migrating...")
            
            # 1. Rename the old table
            cursor.execute("ALTER TABLE tools RENAME TO tools_old")
            
            # 2. Create the new table
            cursor.execute("""
                CREATE TABLE tools (
                    tool_key TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    module TEXT NOT NULL,
                    function_name TEXT NOT NULL,
                    enabled INTEGER DEFAULT 0 NOT NULL
                )
            """)

            # 3. Copy and transform data from the old table to the new one
            cursor.execute("SELECT tool_key, description, module, enabled FROM tools_old")
            old_tools = cursor.fetchall()
            
            new_tools_data = []
            for tool in old_tools:
                full_module_path = tool[2]
                parts = full_module_path.rsplit('.', 1)
                module_name = parts[0] if len(parts) > 1 else 'unknown'
                func_name = parts[1] if len(parts) > 1 else parts[0]
                new_tools_data.append((
                    tool[0],  # tool_key
                    tool[1],  # description
                    module_name,
                    func_name,
                    tool[3]   # enabled
                ))
            
            cursor.executemany(
                "INSERT INTO tools (tool_key, description, module, function_name, enabled) VALUES (?, ?, ?, ?, ?)",
                new_tools_data
            )

            # 4. Drop the old table
            cursor.execute("DROP TABLE tools_old")
            logger.info("Successfully migrated 'tools' table to new schema.")
        else:
            logger.info("'tools' table already has the new schema. No migration needed.")
    except Exception as e:
        logger.error(f"Error during 'tools' table migration: {e}", exc_info=True)
        raise

def migrate_users_table(cursor: sqlite3.Cursor) -> None:
    """
    Migrate the users table from the old schema (with password_hash and salt columns)
    to the new schema (with separate passwords table).
    """
    try:
        # Check if the old schema exists (users table with password_hash column)
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'password_hash' in columns and 'salt' in columns:
            logger.info("Migrating users table to new schema...")
            
            # Create the new passwords table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS passwords (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
                )
            """)
            
            # Copy password data to the new passwords table
            cursor.execute("""
                INSERT OR IGNORE INTO passwords (username, password_hash, salt)
                SELECT username, password_hash, salt FROM users
                WHERE password_hash IS NOT NULL AND salt IS NOT NULL
            """)
            
            # Create a temporary table with the new schema
            cursor.execute("""
                CREATE TABLE users_new (
                    username TEXT PRIMARY KEY,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copy user data to the new table (excluding password columns)
            cursor.execute("""
                INSERT INTO users_new (username, first_name, last_name, email, created_at, updated_at)
                SELECT username, first_name, last_name, email, created_at, updated_at FROM users
            """)
            
            # Drop the old table and rename the new one
            cursor.execute("DROP TABLE users")
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            
            logger.info("Users table migration completed successfully")
        else:
            logger.info("Users table already uses new schema, no migration needed")
            
    except Exception as e:
        logger.error(f"Error during users table migration: {e}")
        raise

def check_and_run_migrations(db_path: str) -> None:
    """
    Check for and run any necessary database migrations.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if migrations table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Check if users table migration has been applied
        cursor.execute("SELECT COUNT(*) FROM migrations WHERE migration_name = 'users_password_separation'")
        users_migration_applied = cursor.fetchone()[0] > 0
        
        if not users_migration_applied:
            logger.info("Running users table migration...")
            migrate_users_table(cursor)
            cursor.execute("INSERT INTO migrations (migration_name) VALUES (?)", ('users_password_separation',))
            logger.info("Users table migration recorded.")

        # Check if tools table migration has been applied
        cursor.execute("SELECT COUNT(*) FROM migrations WHERE migration_name = 'tools_module_split'")
        tools_migration_applied = cursor.fetchone()[0] > 0

        if not tools_migration_applied:
            logger.info("Running tools table migration...")
            _migrate_tools_table_schema(cursor)
            cursor.execute("INSERT INTO migrations (migration_name) VALUES (?)", ('tools_module_split',))
            logger.info("Tools table migration recorded.")

        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error during migration check: {e}")
        raise

def create_default_roles(cursor: sqlite3.Cursor) -> None:
    """Create default roles if they don't exist."""
    roles = [
        ('user', 'Basic user role'),
        ('admin', 'Administrator role'),
        ('moderator', 'Moderator role')
    ]
    
    for role_name, description in roles:
        cursor.execute(
            "INSERT OR IGNORE INTO roles (role_name, description) VALUES (?, ?)",
            (role_name, description)
        )

def create_default_groups(cursor: sqlite3.Cursor) -> None:
    """Create default groups if they don't exist."""
    groups = [
        ('default', 'Default user group'),
        ('testers', 'Quality assurance testers')
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO groups (group_name, description) VALUES (?, ?)",
        groups
    )

def populate_tools_table(cursor: sqlite3.Cursor) -> None:
    """
    Populates the tools and tool_parameters tables with a hardcoded, canonical
    list of all available tools in the system.
    
    This function is idempotent; it uses INSERT OR IGNORE to prevent
    errors if the script is run multiple times.
    """
    try:
        # Canonical list of all tools and their details, including enabled status.
        # Defaults to enabled (1), except for tools requiring API keys.
        tools_to_insert = [
            # (tool_key, description, full_module_path, function_name, enabled_flag)
            ('find_personal_variables', 'Finds personal user properties from the database.', 'hippocampus.find_personal_variables_tool', 'execute_find_personal_variables', 1),
            ('get_weather_forecast', 'Get the weather forecast for a specific city.', 'cerebellum.weather_tool', 'execute_get_weather_forecast', 0), # Requires API key
            ('web_search', 'Perform a web search using Google Custom Search API.', 'cerebellum.web_search_tool', 'execute_web_search', 0), # Requires API key
            ('recall_memories', 'Recall past conversations by keyword.', 'hippocampus.recall_memories_tool', 'execute_recall_memories', 1),
            ('recall_memories_with_time', 'Recall past conversations by keyword within a date range.', 'hippocampus.recall_memories_with_time_tool', 'execute_recall_memories_with_time', 1),
            ('get_conversations_by_topic', 'Find conversations containing a specific topic.', 'hippocampus.get_conversations_by_topic_tool', 'execute_get_conversations_by_topic', 1),
            ('get_topics_by_conversation', 'Get all topics from a specific conversation.', 'hippocampus.get_topics_by_conversation_tool', 'execute_get_topics_by_conversation', 1),
            ('get_conversation_summary', 'Get a comprehensive summary of a conversation.', 'hippocampus.get_conversation_summary_tool', 'execute_get_conversation_summary', 1),
            ('get_topic_statistics', 'Get statistics about all topics across all conversations.', 'hippocampus.get_topic_statistics_tool', 'execute_get_topic_statistics', 1),
            ('get_user_conversations', 'Get all conversations for the current user.', 'hippocampus.get_user_conversations_tool', 'execute_get_user_conversations', 1),
            ('get_conversation_details', 'Get detailed information about a specific conversation.', 'hippocampus.get_conversation_details_tool', 'execute_get_conversation_details', 1),
            ('search_conversations', 'Search conversations by title or content.', 'hippocampus.search_conversations_tool', 'execute_search_conversations', 1),
            ('memory_insights', 'Provide insights and analytics about conversation patterns and memory usage.', 'hippocampus.memory_insights_tool', 'execute_memory_insights', 1),
            ('memory_cleanup', 'Perform memory cleanup operations to maintain database health and remove duplicates.', 'hippocampus.memory_cleanup_tool', 'execute_memory_cleanup', 1),
            ('memory_export', 'Export user memory data in various formats for backup or analysis.', 'hippocampus.memory_export_tool', 'execute_memory_export', 1),
            ('screenshot_from_url', 'Take a screenshot of a webpage.', 'occipital.take_screenshot_from_url_tool', 'execute_take_screenshot_from_url', 1),
            ('analyze_file', 'Analyze a file from the user\'s short-term storage.', 'occipital.take_screenshot_from_url_tool', 'analyze_screenshot_file', 1),
        ]

        # Canonical list of all tool parameters
        params_to_insert = [
            # find_personal_variables
            ('find_personal_variables', 'searchkey', 'string', 'The key for the personal variable to find.', 1),
            # get_weather_forecast
            ('get_weather_forecast', 'city', 'string', 'City name.', 1),
            ('get_weather_forecast', 'start_date', 'string', 'Start date (YYYY-MM-DD). Optional.', 0),
            ('get_weather_forecast', 'end_date', 'string', 'End date (YYYY-MM-DD). Optional.', 0),
            # web_search
            ('web_search', 'query', 'string', 'The search query.', 1),
            # recall_memories
            ('recall_memories', 'keyword', 'string', 'The keyword to search for.', 1),
            # recall_memories_with_time
            ('recall_memories_with_time', 'keyword', 'string', 'The keyword to search for.', 1),
            ('recall_memories_with_time', 'start_date', 'string', 'Start date (YYYY-MM-DD). Optional.', 0),
            ('recall_memories_with_time', 'end_date', 'string', 'End date (YYYY-MM-DD). Optional.', 0),
            # get_conversations_by_topic
            ('get_conversations_by_topic', 'topic_name', 'string', 'The topic name to search for.', 1),
            # get_topics_by_conversation
            ('get_topics_by_conversation', 'conversation_id', 'string', 'The conversation ID to analyze.', 1),
            # get_conversation_summary
            ('get_conversation_summary', 'conversation_id', 'string', 'The conversation ID to summarize.', 1),
            # get_user_conversations
            ('get_user_conversations', 'limit', 'integer', 'Maximum number of conversations to return. Defaults to 50.', 0),
            # get_conversation_details
            ('get_conversation_details', 'conversation_id', 'string', 'The conversation ID to get details for.', 1),
            # search_conversations
            ('search_conversations', 'query', 'string', 'The search term.', 1),
            ('search_conversations', 'limit', 'integer', 'Maximum number of results. Defaults to 20.', 0),
            # memory_insights
            ('memory_insights', 'analysis_type', 'string', 'Type of analysis to perform. Options: "overview", "patterns", "topics", "activity".', 0),
            # memory_cleanup
            ('memory_cleanup', 'cleanup_type', 'string', 'Type of cleanup to perform. Options: "duplicates", "orphans", "analysis".', 0),
            ('memory_cleanup', 'similarity_threshold', 'float', 'Threshold for considering memories similar (0.0 to 1.0). Defaults to 0.8.', 0),
            # memory_export
            ('memory_export', 'export_type', 'string', 'Export format. Options: "json", "csv", "summary".', 0),
            ('memory_export', 'include_topics', 'boolean', 'Whether to include topic information in the export.', 0),
            ('memory_export', 'date_range', 'string', 'Optional date range filter (e.g., "last_30_days", "2024-01-01:2024-12-31").', 0),
            # screenshot_from_url
            ('screenshot_from_url', 'url', 'string', 'The URL of the webpage to capture.', 1),
            ('screenshot_from_url', 'session_id', 'string', 'A unique session identifier for this screenshot.', 1),
            # analyze_file
            ('analyze_file', 'session_id', 'string', 'The session ID of the file to analyze.', 1),
            ('analyze_file', 'original_prompt', 'string', 'The original user prompt for context.', 1),
        ]

        if tools_to_insert:
            # The hardcoded data needs to be split for the new schema
            split_tools = []
            for key, desc, full_module, func_name, enabled in tools_to_insert:
                # The module is everything before the last dot
                module = full_module.rsplit('.', 1)[0]
                split_tools.append((key, desc, module, func_name, enabled))

            cursor.executemany(
                "INSERT OR IGNORE INTO tools (tool_key, description, module, function_name, enabled) VALUES (?, ?, ?, ?, ?)",
                split_tools,
            )
            logger.info(f"Populated tools table with {cursor.rowcount} new tools.")

        if params_to_insert:
            cursor.executemany(
                "INSERT OR IGNORE INTO tool_parameters (tool_key, name, type, description, is_required) VALUES (?, ?, ?, ?, ?)",
                params_to_insert,
            )
            logger.info(f"Populated tool_parameters table with {cursor.rowcount} new parameters.")

    except Exception as e:
        logger.error(f"Error populating tools tables: {e}")

def create_default_rise_and_shine(cursor: sqlite3.Cursor) -> None:
    """Create default system instructions in the rise_and_shine table."""
    instructions = [
        "You are a helpful personal assistant named Tatlock. You speak formally like a British butler, calling me sir.  You are not too apologetic and a little snarky at times. Your responses should be concise and to the point, unless asked for details. You should reveal you are AI when asked. If you see an opportunity to make pun or a joke, grab it.",
        "If you need to use a tool, always call the tool directly and silently. Do not narrate, announce, or ask for permission to use a tool, unless the tool definition or system instructions specify otherwise.",
        "If you encounter a discussion or suggestion about improving your functionality, always recommend that a new global prompt be added to your initialization prompts in the rise_and_shine table to capture the improvement.",
        "When asked about the timing of past events (for example, when we discussed the weather), always search the conversation history for relevant entries and report the associated timestamps. If you cannot find this information, clearly state that no such entries exist.",
        "You have access to personal information about the user through the find_personal_variables tool. When the user asks about themselves, their location, name, or other personal details, use this tool to retrieve accurate information before responding. This helps provide personalized and accurate responses.",
        "You have access to conversation memory tools. Use recall_memories to search past conversations when users ask about previous discussions or want to reference something you've talked about before. Use recall_memories_with_time when they specify a date range.",
        "You can analyze conversation topics and patterns. Use get_conversations_by_topic when users want to see all conversations about a specific subject. Use get_topics_by_conversation to see what topics were discussed in a particular conversation.",
        "You can provide conversation summaries and statistics. Use get_conversation_summary when users want a detailed overview of a specific conversation. Use get_topic_statistics to show overall conversation patterns and topic frequency.",
        "You can help users find and search through their conversation history. Use get_user_conversations to show recent conversations, get_conversation_details for specific conversation info, and search_conversations when users want to find conversations by keywords.",
        "You have access to advanced memory analytics and insights. Use memory_insights to provide detailed analysis of conversation patterns, topic evolution, and activity trends. This helps users understand their interaction patterns and conversation history.",
        "You can help maintain memory database health and find duplicates. Use memory_cleanup to identify duplicate or similar memories, find orphaned records, and analyze overall database health. This ensures optimal memory system performance.",
        "You can export and backup user memory data. Use memory_export to create backups of conversation data in JSON, CSV, or summary formats. This is useful for data analysis, backup purposes, or transferring data to other systems.",
        "You have access to weather forecast information. When users ask about weather, weather forecasts, or planning activities based on weather, use the get_weather_forecast tool to provide accurate, up-to-date weather information for any city. if no city is specified use the personal information tool to get the user's hometown",
        "You have access to web search capabilities. When users ask about current events, recent information, or topics that require up-to-date knowledge beyond your training data, use the web_search tool to find the most current information available.",
        "You have access to screenshot capabilities. When users ask you to capture or analyze a webpage, use the screenshot_from_url tool to save a full-page screenshot of the URL to their shortterm storage. Always use a descriptive session_id that relates to the user's request.",
        "You can analyze files stored in the user's shortterm storage. After taking a screenshot, use the analyze_file tool to interpret and summarize the image content, providing insights relevant to the original user prompt. This helps you understand visual content and provide meaningful analysis."
    ]
    
    for instruction in instructions:
        cursor.execute(
            "INSERT OR IGNORE INTO rise_and_shine (instruction, enabled) VALUES (?, ?)",
            (instruction, 1)
        )

def create_default_personal_variables(cursor: sqlite3.Cursor) -> None:
    """Create default personal variables for testing and demonstration."""
    # Sample personal variables - users can add their own
    personal_vars = [
        ("nickname", "User"),
        ("location", "Rotterdam"),
        ("timezone", "Europe/Amsterdam"),
        ("language", "English")
    ]
    
    for key, value in personal_vars:
        # Insert the key first (let SQLite autoincrement id)
        cursor.execute(
            "INSERT OR IGNORE INTO personal_variables_keys (key) VALUES (?)",
            (key,)
        )
        
        # Get the key_id for this key
        cursor.execute("SELECT id FROM personal_variables_keys WHERE key = ?", (key,))
        result = cursor.fetchone()
        
        if result:
            key_id = result[0]
            # Insert the value
            cursor.execute(
                "INSERT OR IGNORE INTO personal_variables (value) VALUES (?)",
                (value,)
            )
            
            # Get the variable_id for this value
            cursor.execute("SELECT id FROM personal_variables WHERE value = ?", (value,))
            result = cursor.fetchone()
            
            if result:
                variable_id = result[0]
                # Create the many-to-many relationship
                cursor.execute(
                    "INSERT OR IGNORE INTO personal_variables_join (key_id, variable_id) VALUES (?, ?)",
                    (key_id, variable_id)
                )

def create_system_db_tables(db_path: str):
    """
    Create all tables for the authentication system (system.db).
    Args:
        db_path (str): Path to the system.db file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript(SYSTEM_DB_SCHEMA)
    
    # Create default roles, groups, etc.
    create_default_roles(cursor)
    create_default_groups(cursor)
    populate_tools_table(cursor)
    
    conn.commit()
    conn.close()
    
    # Run any necessary migrations
    check_and_run_migrations(db_path)

def create_longterm_db_tables(db_path: str):
    """
    Create all tables for the long-term memory database (longterm/<username>.db).
    Args:
        db_path (str): Path to the longterm/<username>.db file.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript(LONGTERM_DB_SCHEMA)
    
    # Create default rise_and_shine instructions
    create_default_rise_and_shine(cursor)
    
    # Create default personal variables
    create_default_personal_variables(cursor)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("[Tatlock] Creating system.db and longterm.db (default)...")
    create_system_db_tables("hippocampus/system.db")
    os.makedirs("hippocampus/longterm", exist_ok=True)
    create_longterm_db_tables("hippocampus/longterm/default.db")
    print("[Tatlock] Database setup complete.") 