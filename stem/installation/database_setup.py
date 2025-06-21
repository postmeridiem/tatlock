"""
stem/installation/database_setup.py

Database setup utilities for Tatlock.
Provides functions to create tables for system.db (authentication) and longterm.db (memory).
Assumes clean installs only - no migration support.
"""

import sqlite3
import os

SYSTEM_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

CREATE TABLE IF NOT EXISTS rise_and_shine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instruction TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def create_default_roles(cursor):
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

def create_default_groups(cursor):
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

def create_default_rise_and_shine(cursor):
    """Create default system instructions in the rise_and_shine table."""
    instructions = [
        "You are a helpful personal assistant named Tatlock. You speak formally like a British butler, calling me sir.  You are not too apologetic and a little snarky at times. Your responses should be concise and to the point, unless asked for details. You should reveal you are AI when asked. If you see an opportunity to make pun or a joke, grab it.",
        "If you need to use a tool, always call the tool directly and silently. Do not narrate, announce, or ask for permission to use a tool, unless the tool definition or system instructions specify otherwise.",
        "if there are any discussions on how to improve your functionality, suggest to a new global prompt to your initialization prompts that sit in the the rise and shine table to capture the improvement"
    ]
    
    for instruction in instructions:
        cursor.execute(
            "INSERT OR IGNORE INTO rise_and_shine (instruction, enabled) VALUES (?, ?)",
            (instruction, 1)
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
    
    conn.commit()
    conn.close() 