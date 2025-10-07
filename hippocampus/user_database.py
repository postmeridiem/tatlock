"""
hippocampus/user_database.py

User-specific database management for Tatlock longterm memory.
Handles creation, deletion, and access to per-user longterm databases.
"""

import sqlite3
import os
import logging
from typing import Optional, Set
from stem.installation.database_setup import create_longterm_db_tables, check_and_run_user_database_migrations

# Set up logging for this module
logger = logging.getLogger(__name__)

# Cache of users whose databases have been migrated this session
_migrated_users: Set[str] = set()


def get_user_database_path(username: str) -> str:
    """
    Get the database path for a specific user.
    Args:
        username (str): The username.
    Returns:
        str: Path to the user's longterm database.
    """
    longterm_dir = os.path.join("hippocampus", "longterm")
    return os.path.join(longterm_dir, f"{username}.db")


def ensure_user_database(username: str) -> str:
    """
    Ensure a user's longterm database exists, creating it if necessary.
    Runs migrations once per user session on first access.
    Args:
        username (str): The username.
    Returns:
        str: Path to the user's longterm database.
    """
    db_path = get_user_database_path(username)

    if not os.path.exists(db_path):
        # Create the database directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Create the database with all required tables
        create_longterm_db_tables(db_path)
        logger.debug(f"Created a new longterm memory database for user '{username}' at {db_path}")

        # Mark as migrated (new databases don't need migration)
        _migrated_users.add(username)
    elif username not in _migrated_users:
        # Run migrations on existing user database (once per session)
        check_and_run_user_database_migrations(db_path)
        _migrated_users.add(username)

    return db_path


def delete_user_database(username: str) -> bool:
    """
    Delete a user's longterm database.
    Args:
        username (str): The username.
    Returns:
        bool: True if deleted successfully, False otherwise.
    """
    db_path = get_user_database_path(username)
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            logger.debug(f"Deleted longterm database for user '{username}' at {db_path}")
            return True
        except OSError as e:
            logger.error(f"Error deleting database for user '{username}': {e}")
            return False
    
    return True  # Database doesn't exist, consider it "deleted"


def get_database_connection(username: str) -> Optional[sqlite3.Connection]:
    """
    Get a database connection for a specific user.
    Args:
        username (str): The username.
    Returns:
        sqlite3.Connection | None: Database connection or None if error.
    """
    try:
        db_path = ensure_user_database(username)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database for user '{username}': {e}")
        return None


def execute_user_query(username: str, query: str, params: tuple = ()) -> list[dict]:
    """
    Execute a query on a user's database.
    Args:
        username (str): The username.
        query (str): SQL query string.
        params (tuple): Query parameters.
    Returns:
        list[dict]: Query results as dictionaries.
    """
    conn = get_database_connection(username)
    if not conn:
        return []
    
    results = []
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        # If this is a data-modifying query, commit the changes
        if any(keyword in query.strip().upper() for keyword in ["INSERT", "UPDATE", "DELETE"]):
            conn.commit()
            
        rows = cursor.fetchall()
        results = [dict(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Database error for user '{username}': {e}")
    finally:
        conn.close()
    
    return results


def get_user_image_path(username: str, session_id: str, ext: str = 'png') -> str:
    """
    Get the per-user, per-session image storage path.
    Args:
        username (str): The username.
        session_id (str): The session ID.
        ext (str): File extension (default: 'png').
    Returns:
        str: Path to the image file for this user/session.
    """
    base_dir = os.path.join('hippocampus', 'shortterm', username, 'images')
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, f"{session_id}.{ext}") 