"""
hippocampus/recall.py

Memory recall and search functions for Tatlock. Supports keyword and temporal queries.
Now supports user-specific databases and conversation-topic relationships.
"""

import sqlite3
import os
import logging
from hippocampus.user_database import execute_user_query, get_database_connection, ensure_user_database
from datetime import datetime, timedelta
from config import SYSTEM_DB_PATH
from stem.timeawareness import parse_natural_date_range
# Import any date helpers from stem.timeawareness if needed

# Set up logging for this module
logger = logging.getLogger(__name__)


def recall_memories(keyword: str | None = None, username: str = "admin") -> list[dict]:
    """
    Search memories for a keyword in user_prompt, llm_reply, or topic name.
    Args:
        keyword (str | None): The keyword to search for. Defaults to None (empty search).
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        list[dict]: Summaries of matching memories.
    """
    if keyword is None:
        keyword = ""
        
    # Join with topics via memory_topics to allow topic search
    query = '''
    SELECT m.timestamp, m.user_prompt, m.llm_reply, m.conversation_id, t.topic_name
    FROM memories m
    LEFT JOIN memory_topics mt ON m.interaction_id = mt.interaction_id
    LEFT JOIN topics t ON mt.topic_id = t.topic_id
    WHERE (
        m.user_prompt LIKE ?
        OR m.llm_reply LIKE ?
        OR t.topic_name LIKE ?
    )
    ORDER BY m.timestamp DESC
    LIMIT 20
    '''
    like_kw = f"%{keyword}%"
    results = execute_user_query(username, query, (like_kw, like_kw, like_kw))
    
    return results


def recall_memories_with_time(keyword: str | None = None, username: str = "admin", start_date: str | None = None, end_date: str | None = None) -> list[dict]:
    """
    Search memories for a keyword in user_prompt, llm_reply, or topic name, limited to a date or date range.
    Args:
        keyword (str | None): The keyword to search for. Defaults to None (empty search).
        username (str): The username whose database to search. Defaults to "admin".
        start_date (str | None, optional): Start date (YYYY-MM-DD).
        end_date (str | None, optional): End date (YYYY-MM-DD).
    Returns:
        list[dict]: Summaries of matching memories within the date range.
    """
    if keyword is None:
        keyword = ""
    if start_date is not None and not isinstance(start_date, str):
        start_date = str(start_date)
    if end_date is not None and not isinstance(end_date, str):
        end_date = str(end_date)

    query = '''
    SELECT m.timestamp, m.user_prompt, m.llm_reply, m.conversation_id, t.topic_name
    FROM memories m
    LEFT JOIN memory_topics mt ON m.interaction_id = mt.interaction_id
    LEFT JOIN topics t ON mt.topic_id = t.topic_id
    WHERE (
        m.user_prompt LIKE ?
        OR m.llm_reply LIKE ?
        OR t.topic_name LIKE ?
    )
    '''
    params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
    
    # Add date filtering
    if start_date and end_date:
        query += " AND date(m.timestamp) BETWEEN date(?) AND date(?)"
        params.extend([start_date, end_date])
    elif start_date:
        query += " AND date(m.timestamp) = date(?)"
        params.append(start_date)
    
    query += " ORDER BY m.timestamp DESC LIMIT 20"
    
    results = execute_user_query(username, query, tuple(params))
    return results


def get_conversations_by_topic(topic_name: str, username: str = "admin") -> list[dict]:
    """
    Get all conversations that contain a specific topic.
    Args:
        topic_name (str): The topic name to search for.
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        list[dict]: Conversations with the specified topic, including metadata.
    """
    query = '''
    SELECT 
        ct.conversation_id,
        t.topic_name,
        ct.first_occurrence,
        ct.last_occurrence,
        ct.topic_count,
        COUNT(m.interaction_id) as total_interactions
    FROM conversation_topics ct
    JOIN topics t ON ct.topic_id = t.topic_id
    JOIN memories m ON ct.conversation_id = m.conversation_id
    WHERE t.topic_name LIKE ?
    GROUP BY ct.conversation_id, t.topic_id
    ORDER BY ct.last_occurrence DESC
    '''
    
    like_topic = f"%{topic_name}%"
    results = execute_user_query(username, query, (like_topic,))
    return results


def get_topics_by_conversation(conversation_id: str, username: str = "admin") -> list[dict]:
    """
    Get all topics that appear in a specific conversation.
    Args:
        conversation_id (str): The conversation ID to search for.
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        list[dict]: Topics in the specified conversation, including metadata.
    """
    query = '''
    SELECT 
        t.topic_name,
        ct.first_occurrence,
        ct.last_occurrence,
        ct.topic_count
    FROM conversation_topics ct
    JOIN topics t ON ct.topic_id = t.topic_id
    WHERE ct.conversation_id = ?
    ORDER BY ct.topic_count DESC, ct.last_occurrence DESC
    '''
    
    results = execute_user_query(username, query, (conversation_id,))
    return results


def get_conversation_summary(conversation_id: str, username: str = "admin") -> dict:
    """
    Get a summary of a conversation including its topics and key interactions.
    Args:
        conversation_id (str): The conversation ID to summarize.
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        dict: Summary of the conversation including topics and interaction count.
    """
    # Get conversation metadata
    query = '''
    SELECT 
        m.conversation_id,
        MIN(m.timestamp) as start_time,
        MAX(m.timestamp) as end_time,
        COUNT(m.interaction_id) as total_interactions
    FROM memories m
    WHERE m.conversation_id = ?
    GROUP BY m.conversation_id
    '''
    
    metadata = execute_user_query(username, query, (conversation_id,))
    
    if not metadata:
        return {}
    
    # Get topics for this conversation
    topics = get_topics_by_conversation(conversation_id, username)
    
    # Get first and last interactions
    query = '''
    SELECT user_prompt, llm_reply, timestamp
    FROM memories
    WHERE conversation_id = ?
    ORDER BY timestamp ASC
    LIMIT 1
    '''
    first_interaction = execute_user_query(username, query, (conversation_id,))
    
    query = '''
    SELECT user_prompt, llm_reply, timestamp
    FROM memories
    WHERE conversation_id = ?
    ORDER BY timestamp DESC
    LIMIT 1
    '''
    last_interaction = execute_user_query(username, query, (conversation_id,))
    
    summary = metadata[0]
    summary['topics'] = topics
    summary['first_interaction'] = first_interaction[0] if first_interaction else None
    summary['last_interaction'] = last_interaction[0] if last_interaction else None
    
    return summary


def get_topic_statistics(username: str = "admin") -> list[dict]:
    """
    Get statistics about topics across all conversations.
    Args:
        username (str): The username whose database to search. Defaults to "admin".
    Returns:
        list[dict]: Topic statistics including conversation count and total occurrences.
    """
    query = '''
    SELECT 
        t.topic_name,
        COUNT(DISTINCT ct.conversation_id) as conversation_count,
        SUM(ct.topic_count) as total_occurrences,
        MIN(ct.first_occurrence) as first_seen,
        MAX(ct.last_occurrence) as last_seen
    FROM topics t
    LEFT JOIN conversation_topics ct ON t.topic_id = ct.topic_id
    GROUP BY t.topic_id, t.topic_name
    ORDER BY conversation_count DESC, total_occurrences DESC
    '''
    
    results = execute_user_query(username, query)
    return results


# New conversation management functions
def get_user_conversations(username: str, limit: int = 50) -> list[dict]:
    """
    Get all conversations for a user from their longterm database.
    Args:
        username (str): The username.
        limit (int): Maximum number of conversations to return.
    Returns:
        list[dict]: List of conversation records.
    """
    try:
        db_path = ensure_user_database(username)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, title, started_at, last_activity, message_count
            FROM conversations 
            ORDER BY last_activity DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conversations = []
        
        for row in rows:
            conversations.append({
                'conversation_id': row[0],
                'title': row[1],
                'started_at': row[2],
                'last_activity': row[3],
                'message_count': row[4]
            })
        
        conn.close()
        return conversations
        
    except sqlite3.Error as e:
        logger.error(f"Error getting conversations for user '{username}': {e}")
        return []


def get_conversation_details(conversation_id: str, username: str) -> dict | None:
    """
    Get detailed information about a specific conversation.
    Args:
        conversation_id (str): The conversation ID.
        username (str): The username.
    Returns:
        dict | None: Conversation details or None if not found.
    """
    try:
        # Get from user's longterm database
        db_path = ensure_user_database(username)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, title, started_at, last_activity, message_count
            FROM conversations 
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        # Get conversation topics from the same database
        cursor.execute("""
            SELECT t.topic_name, ct.topic_count, ct.first_occurrence, ct.last_occurrence
            FROM conversation_topics ct
            JOIN topics t ON ct.topic_id = t.topic_id
            WHERE ct.conversation_id = ?
            ORDER BY ct.topic_count DESC
        """, (conversation_id,))
        
        topics = []
        for topic_row in cursor.fetchall():
            topics.append({
                'topic_name': topic_row[0],
                'count': topic_row[1],
                'first_occurrence': topic_row[2],
                'last_occurrence': topic_row[3]
            })
        
        conn.close()
        
        return {
            'conversation_id': row[0],
            'title': row[1],
            'started_at': row[2],
            'last_activity': row[3],
            'message_count': row[4],
            'topics': topics
        }
        
    except sqlite3.Error as e:
        logger.error(f"Error getting conversation details for '{conversation_id}': {e}")
        return None


def search_conversations(username: str, query: str, limit: int = 20) -> list[dict]:
    """
    Search conversations by title or content.
    Args:
        username (str): The username.
        query (str): Search query.
        limit (int): Maximum number of results.
    Returns:
        list[dict]: List of matching conversations.
    """
    try:
        # Search in user's longterm database by title
        db_path = ensure_user_database(username)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT conversation_id, title, started_at, last_activity, message_count
            FROM conversations 
            WHERE (title LIKE ? OR conversation_id LIKE ?)
            ORDER BY last_activity DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', limit))
        
        rows = cursor.fetchall()
        conversations = []
        
        for row in rows:
            conversations.append({
                'conversation_id': row[0],
                'title': row[1],
                'started_at': row[2],
                'last_activity': row[3],
                'message_count': row[4]
            })
        
        conn.close()
        return conversations
        
    except sqlite3.Error as e:
        logger.error(f"Error searching conversations for user '{username}': {e}")
        return []
