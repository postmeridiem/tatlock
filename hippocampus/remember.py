"""
hippocampus/remember.py

Functions for saving and linking interactions and topics in Tatlock's persistent memory.
Now supports user-specific databases and conversation IDs.
"""

import sqlite3
import json
import logging
from datetime import datetime
import uuid
import os
from hippocampus.user_database import get_database_connection, ensure_user_database, execute_user_query
from config import SYSTEM_DB_PATH

# Set up logging for this module
logger = logging.getLogger(__name__)


def get_or_create_topic(conn: sqlite3.Connection, topic_name: str) -> int | None:
    """
    Get the ID of a topic, creating it if it doesn't exist.
    Args:
        conn (sqlite3.Connection): Database connection.
        topic_name (str): The topic name.
    Returns:
        int | None: The topic ID, or None if not found/created.
    """
    cursor = conn.cursor()
    try:
        # INSERT OR IGNORE is an efficient way to handle this "get or create" logic
        cursor.execute("INSERT OR IGNORE INTO topics (topic_name) VALUES (?)", (topic_name,))

        # Now, fetch the ID, which is guaranteed to exist
        cursor.execute("SELECT topic_id FROM topics WHERE topic_name = ?", (topic_name,))
        row = cursor.fetchone()

        return row[0] if row else None
    except sqlite3.Error as e:
        logger.error(f"Error getting or creating topic '{topic_name}': {e}")
        return None


def save_interaction(user_prompt: str, llm_reply: str, full_llm_history: list[dict], topic: str, username: str = "admin", conversation_id: str | None = None) -> str | None:
    """
    Save a full interaction, get or create the topic, and link them.
    Args:
        user_prompt (str): The user's prompt.
        llm_reply (str): The LLM's reply.
        full_llm_history (list[dict]): Full conversation history.
        topic (str): The topic name.
        username (str): The username whose database to use. Defaults to "admin".
        conversation_id (str | None): Conversation ID for grouping. If None, generates from current time.
    Returns:
        str | None: The interaction ID, or None on error.
    """
    interaction_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Generate conversation_id if not provided
    if conversation_id is None:
        conversation_id = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    
    # Create or update conversation record
    create_or_update_conversation(conversation_id, username, title=f"Conversation about {topic}")
    
    conn = None

    try:
        # Get user-specific database connection
        db_path = ensure_user_database(username)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        history_json = json.dumps(full_llm_history, indent=2)

        # Step 1: Save the main memory
        query = """
        INSERT INTO memories (interaction_id, conversation_id, timestamp, user_prompt, llm_reply, full_conversation_history)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (interaction_id, conversation_id, timestamp, user_prompt, llm_reply, history_json))

        # Step 2: Get or Create the Topic
        topic_id = get_or_create_topic(conn, topic)
        if not topic_id:
            logger.warning(f"Warning: Could not get or create topic ID for '{topic}' in user '{username}' database.")
            conn.commit()
            return interaction_id

        # Step 3: Link Memory and Topic
        cursor.execute("INSERT OR IGNORE INTO memory_topics (interaction_id, topic_id) VALUES (?, ?)",
                       (interaction_id, topic_id))

        # Step 4: Update conversation_topics relationship
        update_conversation_topics(conn, conversation_id, topic_id, timestamp)

        conn.commit()
        return interaction_id

    except sqlite3.Error as e:
        # This will now catch errors if the tables are missing
        logger.error(f"Error during save_interaction for user '{username}': {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def update_conversation_topics(conn: sqlite3.Connection, conversation_id: str, topic_id: int, timestamp: str):
    """
    Update the conversation_topics relationship when a new interaction is saved.
    Args:
        conn (sqlite3.Connection): Database connection.
        conversation_id (str): The conversation ID.
        topic_id (int): The topic ID.
        timestamp (str): The timestamp of the interaction.
    """
    cursor = conn.cursor()
    try:
        # Check if this conversation-topic relationship already exists
        cursor.execute("""
            SELECT first_occurrence, last_occurrence, topic_count 
            FROM conversation_topics 
            WHERE conversation_id = ? AND topic_id = ?
        """, (conversation_id, topic_id))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing relationship
            first_occurrence = min(existing[0], timestamp)
            last_occurrence = max(existing[1], timestamp)
            topic_count = existing[2] + 1
            
            cursor.execute("""
                UPDATE conversation_topics 
                SET first_occurrence = ?, last_occurrence = ?, topic_count = ?
                WHERE conversation_id = ? AND topic_id = ?
            """, (first_occurrence, last_occurrence, topic_count, conversation_id, topic_id))
        else:
            # Create new relationship
            cursor.execute("""
                INSERT INTO conversation_topics (conversation_id, topic_id, first_occurrence, last_occurrence, topic_count)
                VALUES (?, ?, ?, ?, 1)
            """, (conversation_id, topic_id, timestamp, timestamp))
            
    except sqlite3.Error as e:
        logger.error(f"Error updating conversation_topics: {e}")
        raise


def create_or_update_conversation(conversation_id: str, username: str, title: str | None = None) -> bool:
    """
    Create or update a conversation record in the user's longterm database.
    Args:
        conversation_id (str): The conversation ID.
        username (str): The username.
        title (str | None): Optional conversation title.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Update user's longterm.db conversations table
        db_path = ensure_user_database(username)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO conversations 
            (conversation_id, title, started_at, last_activity, message_count)
            VALUES (?, ?, COALESCE((SELECT started_at FROM conversations WHERE conversation_id = ?), CURRENT_TIMESTAMP), CURRENT_TIMESTAMP,
                   COALESCE((SELECT message_count FROM conversations WHERE conversation_id = ?), 0) + 1)
        """, (conversation_id, title, conversation_id, conversation_id))
        
        conn.commit()
        conn.close()
        
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Error updating longterm.db conversation record: {e}")
        return False
