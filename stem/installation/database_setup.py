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
        migration_applied = cursor.fetchone()[0] > 0
        
        if not migration_applied:
            logger.info("Running users table migration...")
            migrate_users_table(cursor)
            
            # Mark migration as applied
            cursor.execute("INSERT INTO migrations (migration_name) VALUES (?)", 
                         ('users_password_separation',))
            
            conn.commit()
            logger.info("Migration completed and recorded")
        else:
            logger.info("Users table migration already applied")
        
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
        ('users', 'All users'),
        ('admins', 'Administrators'),
        ('moderators', 'Moderators')
    ]
    
    for group_name, description in groups:
        cursor.execute(
            "INSERT OR IGNORE INTO groups (group_name, description) VALUES (?, ?)",
            (group_name, description)
        )

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
    
    # Create default roles and groups
    create_default_roles(cursor)
    create_default_groups(cursor)
    
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