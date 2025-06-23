"""
hippocampus/forget.py

Memory deletion and forgetting functions for Tatlock longterm memory.
Handles purging and deleting memories, conversations, and topics.
"""

import sqlite3
import logging
from stem.models import UserModel
from .user_database import execute_user_query

# Set up logging for this module
logger = logging.getLogger(__name__)


def purge_all_memories(user: UserModel) -> None:
    """
    Purges all memories, topics, and conversations for a specific user.
    This is a destructive operation that cannot be undone.
    """
    try:
        # Delete all memories first (they reference conversations and topics)
        execute_user_query(user.username, "DELETE FROM memories")
        
        # Delete all memory-topic relationships
        execute_user_query(user.username, "DELETE FROM memory_topics")
        
        # Delete all conversation-topic relationships
        execute_user_query(user.username, "DELETE FROM conversation_topics")
        
        # Delete all conversations
        execute_user_query(user.username, "DELETE FROM conversations")
        
        # Delete all topics
        execute_user_query(user.username, "DELETE FROM topics")
        
        # Reset auto-increment counters for all cleared tables
        execute_user_query(user.username, "DELETE FROM sqlite_sequence WHERE name IN ('memories', 'conversations', 'topics', 'conversation_topics', 'memory_topics')")
        
        logger.debug(f"Successfully purged all memories for user: {user.username}")
        
    except Exception as e:
        logger.error(f"Error purging all memories for user '{user.username}': {e}")
        raise ValueError(f"Failed to purge all memories: {e}")


def delete_conversation(user: UserModel, conversation_id: str) -> None:
    """
    Deletes a conversation and its related messages for a specific user.
    """
    # First, verify the conversation belongs to the user to prevent unauthorized deletion
    convo_check = execute_user_query(user.username, "SELECT conversation_id FROM conversations WHERE conversation_id = ?", (conversation_id,))
    if not convo_check:
        raise ValueError("Conversation not found or access denied.")

    # Delete messages and then the conversation entry (no fetch needed)
    execute_user_query(user.username, "DELETE FROM memories WHERE conversation_id = ?", (conversation_id,))
    execute_user_query(user.username, "DELETE FROM conversations WHERE conversation_id = ?", (conversation_id,)) 