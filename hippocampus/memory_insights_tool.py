"""
hippocampus/memory_insights_tool.py

Tool for providing insights and analytics about user's conversation patterns and memory usage.
"""

import logging
from datetime import datetime, timedelta
from hippocampus.recall import get_user_conversations, get_topic_statistics
from hippocampus.database import get_database_connection
from stem.current_user_context import get_current_user_ctx

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_memory_insights(analysis_type: str = "overview") -> dict:
    """
    Provide insights and analytics about the user's conversation patterns and memory usage.
    
    Args:
        analysis_type (str): Type of analysis to perform. Options: "overview", "patterns", "topics", "activity"
        
    Returns:
        dict: Status and insights data or message.
    """
    try:
        user = get_current_user_ctx()
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        conn = get_database_connection(user.username)
        if not conn:
            return {"status": "error", "message": "Could not connect to user database"}
        
        cursor = conn.cursor()
        
        if analysis_type == "overview":
            insights = _get_overview_insights(cursor)
        elif analysis_type == "patterns":
            insights = _get_pattern_insights(cursor)
        elif analysis_type == "topics":
            insights = _get_topic_insights(cursor)
        elif analysis_type == "activity":
            insights = _get_activity_insights(cursor)
        else:
            return {"status": "error", "message": f"Unknown analysis type: {analysis_type}"}
        
        conn.close()
        
        if not insights:
            return {
                "status": "success", 
                "data": {}, 
                "message": f"No data available for {analysis_type} analysis."
            }
        
        return {"status": "success", "data": insights}
        
    except Exception as e:
        logger.error(f"Error generating memory insights for {analysis_type}: {e}")
        return {"status": "error", "message": f"Memory insights generation failed for analysis_type '{analysis_type}': {e}"}

def _get_overview_insights(cursor) -> dict:
    """Get overview insights about the user's memory usage."""
    try:
        # Total conversations
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]
        
        # Total memories
        cursor.execute("SELECT COUNT(*) FROM memories")
        total_memories = cursor.fetchone()[0]
        
        # Total topics
        cursor.execute("SELECT COUNT(*) FROM topics")
        total_topics = cursor.fetchone()[0]
        
        # Date range
        cursor.execute("""
            SELECT MIN(timestamp), MAX(timestamp) 
            FROM memories 
            WHERE timestamp IS NOT NULL
        """)
        date_range = cursor.fetchone()
        
        # Average memories per conversation
        avg_memories = 0
        if total_conversations > 0:
            avg_memories = round(total_memories / total_conversations, 2)
        
        return {
            "total_conversations": total_conversations,
            "total_memories": total_memories,
            "total_topics": total_topics,
            "avg_memories_per_conversation": avg_memories,
            "date_range": {
                "first_memory": date_range[0] if date_range[0] else None,
                "last_memory": date_range[1] if date_range[1] else None
            }
        }
    except Exception as e:
        logger.error(f"Error getting overview insights: {e}")
        return {}

def _get_pattern_insights(cursor) -> dict:
    """Get insights about conversation patterns."""
    try:
        # Most active days of the week
        cursor.execute("""
            SELECT strftime('%w', timestamp) as day_of_week, COUNT(*) as count
            FROM memories 
            WHERE timestamp IS NOT NULL
            GROUP BY day_of_week
            ORDER BY count DESC
            LIMIT 3
        """)
        active_days = cursor.fetchall()
        
        # Most active hours
        cursor.execute("""
            SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
            FROM memories 
            WHERE timestamp IS NOT NULL
            GROUP BY hour
            ORDER BY count DESC
            LIMIT 5
        """)
        active_hours = cursor.fetchall()
        
        # Conversation length distribution
        cursor.execute("""
            SELECT conversation_id, COUNT(*) as message_count
            FROM memories 
            WHERE conversation_id IS NOT NULL
            GROUP BY conversation_id
            ORDER BY message_count DESC
        """)
        conversation_lengths = cursor.fetchall()
        
        # Calculate statistics
        if conversation_lengths:
            lengths = [row[1] for row in conversation_lengths]
            avg_length = round(sum(lengths) / len(lengths), 2)
            max_length = max(lengths)
            min_length = min(lengths)
        else:
            avg_length = max_length = min_length = 0
        
        return {
            "most_active_days": [
                {"day": _get_day_name(int(day)), "count": count} 
                for day, count in active_days
            ],
            "most_active_hours": [
                {"hour": f"{hour}:00", "count": count} 
                for hour, count in active_hours
            ],
            "conversation_length_stats": {
                "average": avg_length,
                "maximum": max_length,
                "minimum": min_length,
                "total_conversations": len(conversation_lengths)
            }
        }
    except Exception as e:
        logger.error(f"Error getting pattern insights: {e}")
        return {}

def _get_topic_insights(cursor) -> dict:
    """Get insights about topic usage and patterns."""
    try:
        # Most discussed topics
        cursor.execute("""
            SELECT t.name, COUNT(mt.memory_id) as mention_count
            FROM topics t
            JOIN memory_topics mt ON t.id = mt.topic_id
            GROUP BY t.id, t.name
            ORDER BY mention_count DESC
            LIMIT 10
        """)
        top_topics = cursor.fetchall()
        
        # Topic evolution over time
        cursor.execute("""
            SELECT t.name, 
                   MIN(m.timestamp) as first_mention,
                   MAX(m.timestamp) as last_mention,
                   COUNT(mt.memory_id) as total_mentions
            FROM topics t
            JOIN memory_topics mt ON t.id = mt.topic_id
            JOIN memories m ON mt.memory_id = m.id
            WHERE m.timestamp IS NOT NULL
            GROUP BY t.id, t.name
            ORDER BY first_mention DESC
            LIMIT 10
        """)
        topic_evolution = cursor.fetchall()
        
        # Topics by conversation frequency
        cursor.execute("""
            SELECT t.name, COUNT(DISTINCT ct.conversation_id) as conversation_count
            FROM topics t
            JOIN conversation_topics ct ON t.id = ct.topic_id
            GROUP BY t.id, t.name
            ORDER BY conversation_count DESC
            LIMIT 10
        """)
        topics_by_conversation = cursor.fetchall()
        
        return {
            "most_discussed_topics": [
                {"topic": topic, "mentions": count} 
                for topic, count in top_topics
            ],
            "topic_evolution": [
                {
                    "topic": topic,
                    "first_mention": first_mention,
                    "last_mention": last_mention,
                    "total_mentions": total_mentions
                }
                for topic, first_mention, last_mention, total_mentions in topic_evolution
            ],
            "topics_by_conversation_frequency": [
                {"topic": topic, "conversations": count} 
                for topic, count in topics_by_conversation
            ]
        }
    except Exception as e:
        logger.error(f"Error getting topic insights: {e}")
        return {}

def _get_activity_insights(cursor) -> dict:
    """Get insights about user activity patterns."""
    try:
        # Recent activity (last 30 days)
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM memories 
            WHERE timestamp >= ?
        """, (thirty_days_ago,))
        recent_memories = cursor.fetchone()[0]
        
        # Activity by month
        cursor.execute("""
            SELECT strftime('%Y-%m', timestamp) as month, COUNT(*) as count
            FROM memories 
            WHERE timestamp IS NOT NULL
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
        """)
        monthly_activity = cursor.fetchall()
        
        # Longest conversation streak
        cursor.execute("""
            SELECT conversation_id, COUNT(*) as message_count
            FROM memories 
            WHERE conversation_id IS NOT NULL
            GROUP BY conversation_id
            ORDER BY message_count DESC
            LIMIT 1
        """)
        longest_conversation = cursor.fetchone()
        
        # Most recent conversations
        cursor.execute("""
            SELECT id, title, last_activity, message_count
            FROM conversations
            ORDER BY last_activity DESC
            LIMIT 5
        """)
        recent_conversations = cursor.fetchall()
        
        return {
            "recent_activity": {
                "memories_last_30_days": recent_memories,
                "avg_daily_memories": round(recent_memories / 30, 2) if recent_memories > 0 else 0
            },
            "monthly_activity": [
                {"month": month, "count": count} 
                for month, count in monthly_activity
            ],
            "longest_conversation": {
                "conversation_id": longest_conversation[0] if longest_conversation else None,
                "message_count": longest_conversation[1] if longest_conversation else 0
            },
            "recent_conversations": [
                {
                    "id": conv_id,
                    "title": title,
                    "last_activity": last_activity,
                    "message_count": message_count
                }
                for conv_id, title, last_activity, message_count in recent_conversations
            ]
        }
    except Exception as e:
        logger.error(f"Error getting activity insights: {e}")
        return {}

def _get_day_name(day_num: int) -> str:
    """Convert day number to day name."""
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    return days[day_num] if 0 <= day_num <= 6 else "Unknown" 