"""
hippocampus/recall.py

Memory recall and search functions for Tatlock. Supports keyword and temporal queries.
Now supports user-specific databases and conversation-topic relationships.
"""

import sqlite3
import os
import logging
from typing import Optional
from hippocampus.user_database import execute_user_query, get_database_connection, ensure_user_database
from datetime import datetime, timedelta
from config import SYSTEM_DB_PATH
from stem.timeawareness import parse_natural_date_range
from stem.models import UserModel
# Import any date helpers from stem.timeawareness if needed

# Set up logging for this module
logger = logging.getLogger(__name__)


def recall_memories(user: UserModel, keyword: str | None = None) -> list[dict]:
    """
    Search memories for a keyword in user_prompt, llm_reply, or topic name.
    Args:
        user (UserModel): The user whose database to search.
        keyword (str | None): The keyword to search for. Defaults to None (empty search).
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
    results = execute_user_query(user.username, query, (like_kw, like_kw, like_kw))
    
    return results


def recall_memories_with_time(user: UserModel, keyword: str | None = None, start_date: str | None = None, end_date: str | None = None) -> list[dict]:
    """
    Search memories for a keyword in user_prompt, llm_reply, or topic name, limited to a date or date range.
    Args:
        user (UserModel): The user whose database to search.
        keyword (str | None): The keyword to search for. Defaults to None (empty search).
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
    
    results = execute_user_query(user.username, query, tuple(params))
    return results


def get_conversations_by_topic(topic_name: str, user: UserModel) -> list[dict]:
    """
    Get all conversations that contain a specific topic.
    Args:
        topic_name (str): The topic name to search for.
        user (UserModel): The user whose database to search.
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
    results = execute_user_query(user.username, query, (like_topic,))
    return results


def get_topics_by_conversation(conversation_id: str, user: UserModel) -> list[dict]:
    """
    Get all topics that appear in a specific conversation.
    Args:
        conversation_id (str): The conversation ID to search for.
        user (UserModel): The user whose database to search.
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
    
    results = execute_user_query(user.username, query, (conversation_id,))
    return results


def get_conversation_summary(conversation_id: str, user: UserModel) -> dict:
    """
    Get a summary of a conversation including its topics and key interactions.
    Args:
        conversation_id (str): The conversation ID to summarize.
        user (UserModel): The user whose database to search.
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
    
    metadata = execute_user_query(user.username, query, (conversation_id,))
    
    if not metadata:
        return {}
    
    # Get topics for this conversation
    topics = get_topics_by_conversation(conversation_id, user)
    
    # Get first and last interactions
    query = '''
    SELECT user_prompt, llm_reply, timestamp
    FROM memories
    WHERE conversation_id = ?
    ORDER BY timestamp ASC
    LIMIT 1
    '''
    first_interaction = execute_user_query(user.username, query, (conversation_id,))
    
    query = '''
    SELECT user_prompt, llm_reply, timestamp
    FROM memories
    WHERE conversation_id = ?
    ORDER BY timestamp DESC
    LIMIT 1
    '''
    last_interaction = execute_user_query(user.username, query, (conversation_id,))
    
    summary = metadata[0]
    summary['topics'] = topics
    summary['first_interaction'] = first_interaction[0] if first_interaction else None
    summary['last_interaction'] = last_interaction[0] if last_interaction else None
    
    return summary


def get_topic_statistics(user: UserModel) -> list[dict]:
    """
    Get statistics about topics across all conversations.
    Args:
        user (UserModel): The user whose database to search.
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
    
    results = execute_user_query(user.username, query)
    return results


# New conversation management functions
def get_user_conversations(user: UserModel, limit: int = 50) -> list:
    """
    Retrieves all conversations for a specific user, including topics.
    """
    query = """
        SELECT conversation_id
        FROM conversations
        ORDER BY last_activity DESC
        LIMIT ?;
    """
    conversation_ids = execute_user_query(user.username, query, (limit,))
    
    conversations = []
    for row in conversation_ids:
        conversation_id = row['conversation_id']
        details = get_conversation_details(conversation_id, user)
        if details:
            # For the main list, we only need the primary topic, not all of them.
            # Let's say the primary topic is the first one in the list.
            primary_topic = details['topics'][0]['topic_name'] if details['topics'] else None
            details['topic'] = primary_topic
            conversations.append(details)
            
    return conversations


def get_conversation_details(conversation_id: str, user: UserModel) -> dict | None:
    """
    Get detailed information about a specific conversation.
    Args:
        conversation_id (str): The conversation ID.
        user (UserModel): The user.
    Returns:
        dict | None: Conversation details or None if not found.
    """
    try:
        # Get from user's longterm database
        db_path = ensure_user_database(user.username)
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


def search_conversations(user: UserModel, search_term: str, limit: int = 50) -> list:
    """
    Searches conversations by title for a specific user.
    """
    query = """
        SELECT conversation_id, started_at, last_activity, title, message_count
        FROM conversations
        WHERE title LIKE ?
        ORDER BY last_activity DESC
        LIMIT ?;
    """
    like_term = f"%{search_term}%"
    return execute_user_query(user.username, query, (like_term, limit))


def get_conversation_messages(user: UserModel, conversation_id: str) -> list:
    """
    Retrieves all messages for a specific conversation.
    """
    query = """
        SELECT 
            interaction_id as id,
            'user' as role,
            user_prompt as content,
            timestamp
        FROM memories 
        WHERE conversation_id = ? 
        UNION ALL
        SELECT 
            interaction_id as id,
            'assistant' as role,
            llm_reply as content,
            timestamp
        FROM memories 
        WHERE conversation_id = ?
        ORDER BY timestamp;
    """
    return execute_user_query(user.username, query, (conversation_id, conversation_id))
