"""
hippocampus/memory_export_tool.py

Tool for exporting and backing up user memory data in various formats.
"""

import logging
import json
import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from hippocampus.database import get_database_connection
from stem.current_user_context import get_current_user_ctx

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_memory_export(export_type: str = "json", include_topics: bool = True, date_range: str | None = None) -> dict:
    """
    Export user memory data in various formats for backup or analysis.
    
    Args:
        export_type (str): Export format. Options: "json", "csv", "summary"
        include_topics (bool): Whether to include topic information in the export
        date_range (str | None): Optional date range filter (e.g., "last_30_days", "2024-01-01:2024-12-31")
        
    Returns:
        dict: Status and export results or message.
    """
    try:
        user = get_current_user_ctx()
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        conn = get_database_connection(user.username)
        if not conn:
            return {"status": "error", "message": "Could not connect to user database"}
        
        cursor = conn.cursor()
        
        # Create export directory
        export_dir = Path("hippocampus") / "shortterm" / user.username / "exports"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"memory_export_{export_type}_{timestamp}"
        
        if export_type == "json":
            result = _export_to_json(cursor, export_dir, filename, include_topics, date_range)
        elif export_type == "csv":
            result = _export_to_csv(cursor, export_dir, filename, include_topics, date_range)
        elif export_type == "summary":
            result = _export_summary(cursor, export_dir, filename, date_range)
        else:
            return {"status": "error", "message": f"Unknown export type: {export_type}"}
        
        conn.close()
        
        if not result:
            return {
                "status": "success", 
                "data": {}, 
                "message": f"No data available for {export_type} export."
            }
        
        return {"status": "success", "data": result}
        
    except Exception as e:
        logger.error(f"Error performing memory export for {export_type}: {e}")
        return {"status": "error", "message": f"Memory export failed for export_type '{export_type}': {e}"}

def _export_to_json(cursor, export_dir: Path, filename: str, include_topics: bool, date_range: str | None) -> dict:
    """Export memory data to JSON format."""
    try:
        # Build date filter
        date_filter = _build_date_filter(date_range)
        
        # Get conversations
        cursor.execute(f"""
            SELECT id, title, start_time, last_activity, message_count
            FROM conversations
            {date_filter['conversation_where']}
            ORDER BY start_time DESC
        """, date_filter['conversation_params'])
        
        conversations = []
        for conv_id, title, start_time, last_activity, message_count in cursor.fetchall():
            conversation = {
                "id": conv_id,
                "title": title,
                "start_time": start_time,
                "last_activity": last_activity,
                "message_count": message_count,
                "memories": []
            }
            
            # Get memories for this conversation
            cursor.execute(f"""
                SELECT id, user_prompt, llm_reply, timestamp, topic
                FROM memories
                WHERE conversation_id = ?
                {date_filter['memory_where']}
                ORDER BY timestamp
            """, [conv_id] + date_filter['memory_params'])
            
            for mem_id, user_prompt, llm_reply, timestamp, topic in cursor.fetchall():
                memory = {
                    "id": mem_id,
                    "user_prompt": user_prompt,
                    "llm_reply": llm_reply,
                    "timestamp": timestamp,
                    "topic": topic
                }
                
                if include_topics:
                    # Get additional topic information
                    cursor.execute("""
                        SELECT t.name
                        FROM topics t
                        JOIN memory_topics mt ON t.id = mt.topic_id
                        WHERE mt.memory_id = ?
                    """, [mem_id])
                    topics = [row[0] for row in cursor.fetchall()]
                    memory["topics"] = topics
                
                conversation["memories"].append(memory)
            
            conversations.append(conversation)
        
        # Get standalone memories (not in conversations)
        cursor.execute(f"""
            SELECT id, user_prompt, llm_reply, timestamp, topic
            FROM memories
            WHERE conversation_id IS NULL
            {date_filter['memory_where']}
            ORDER BY timestamp
        """, date_filter['memory_params'])
        
        standalone_memories = []
        for mem_id, user_prompt, llm_reply, timestamp, topic in cursor.fetchall():
            memory = {
                "id": mem_id,
                "user_prompt": user_prompt,
                "llm_reply": llm_reply,
                "timestamp": timestamp,
                "topic": topic
            }
            
            if include_topics:
                cursor.execute("""
                    SELECT t.name
                    FROM topics t
                    JOIN memory_topics mt ON t.id = mt.topic_id
                    WHERE mt.memory_id = ?
                """, [mem_id])
                topics = [row[0] for row in cursor.fetchall()]
                memory["topics"] = topics
            
            standalone_memories.append(memory)
        
        # Create export data
        export_data = {
            "export_info": {
                "export_date": datetime.now().isoformat(),
                "export_type": "json",
                "include_topics": include_topics,
                "date_range": date_range,
                "total_conversations": len(conversations),
                "total_standalone_memories": len(standalone_memories)
            },
            "conversations": conversations,
            "standalone_memories": standalone_memories
        }
        
        # Write to file
        file_path = export_dir / f"{filename}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return {
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "total_conversations": len(conversations),
            "total_standalone_memories": len(standalone_memories)
        }
        
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        return {}

def _export_to_csv(cursor, export_dir: Path, filename: str, include_topics: bool, date_range: str | None) -> dict:
    """Export memory data to CSV format."""
    try:
        # Build date filter
        date_filter = _build_date_filter(date_range)
        
        # Get all memories with conversation info
        cursor.execute(f"""
            SELECT m.id, m.user_prompt, m.llm_reply, m.timestamp, m.topic,
                   c.title as conversation_title, c.start_time as conversation_start
            FROM memories m
            LEFT JOIN conversations c ON m.conversation_id = c.id
            {date_filter['memory_where']}
            ORDER BY m.timestamp
        """, date_filter['memory_params'])
        
        memories = cursor.fetchall()
        
        if not memories:
            return {}
        
        # Write to CSV
        file_path = export_dir / f"{filename}.csv"
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'memory_id', 'conversation_title', 'conversation_start', 
                'timestamp', 'topic', 'user_prompt', 'llm_reply'
            ]
            
            if include_topics:
                fieldnames.append('additional_topics')
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for mem_id, user_prompt, llm_reply, timestamp, topic, conv_title, conv_start in memories:
                row = {
                    'memory_id': mem_id,
                    'conversation_title': conv_title or 'Standalone',
                    'conversation_start': conv_start,
                    'timestamp': timestamp,
                    'topic': topic,
                    'user_prompt': user_prompt or '',
                    'llm_reply': llm_reply or ''
                }
                
                if include_topics:
                    # Get additional topics
                    cursor.execute("""
                        SELECT t.name
                        FROM topics t
                        JOIN memory_topics mt ON t.id = mt.topic_id
                        WHERE mt.memory_id = ?
                    """, [mem_id])
                    additional_topics = [row[0] for row in cursor.fetchall()]
                    row['additional_topics'] = '; '.join(additional_topics)
                
                writer.writerow(row)
        
        return {
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "total_memories": len(memories)
        }
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        return {}

def _export_summary(cursor, export_dir: Path, filename: str, date_range: str | None) -> dict:
    """Export a summary report of memory data."""
    try:
        # Build date filter
        date_filter = _build_date_filter(date_range)
        
        # Get basic statistics
        cursor.execute(f"SELECT COUNT(*) FROM memories {date_filter['memory_where']}", date_filter['memory_params'])
        total_memories = cursor.fetchone()[0]
        
        cursor.execute(f"SELECT COUNT(*) FROM conversations {date_filter['conversation_where']}", date_filter['conversation_params'])
        total_conversations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM topics")
        total_topics = cursor.fetchone()[0]
        
        # Get top topics
        cursor.execute(f"""
            SELECT t.name, COUNT(mt.memory_id) as count
            FROM topics t
            JOIN memory_topics mt ON t.id = mt.topic_id
            JOIN memories m ON mt.memory_id = m.id
            {date_filter['memory_where']}
            GROUP BY t.id, t.name
            ORDER BY count DESC
            LIMIT 10
        """, date_filter['memory_params'])
        top_topics = cursor.fetchall()
        
        # Get conversation statistics
        cursor.execute(f"""
            SELECT title, message_count, start_time, last_activity
            FROM conversations
            {date_filter['conversation_where']}
            ORDER BY message_count DESC
            LIMIT 10
        """, date_filter['conversation_params'])
        top_conversations = cursor.fetchall()
        
        # Create summary data
        summary_data = {
            "export_info": {
                "export_date": datetime.now().isoformat(),
                "export_type": "summary",
                "date_range": date_range
            },
            "statistics": {
                "total_memories": total_memories,
                "total_conversations": total_conversations,
                "total_topics": total_topics
            },
            "top_topics": [
                {"topic": topic, "count": count}
                for topic, count in top_topics
            ],
            "top_conversations": [
                {
                    "title": title,
                    "message_count": message_count,
                    "start_time": start_time,
                    "last_activity": last_activity
                }
                for title, message_count, start_time, last_activity in top_conversations
            ]
        }
        
        # Write to file
        file_path = export_dir / f"{filename}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        return {
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "total_memories": total_memories,
            "total_conversations": total_conversations,
            "total_topics": total_topics
        }
        
    except Exception as e:
        logger.error(f"Error exporting summary: {e}")
        return {}

def _build_date_filter(date_range: str | None) -> dict:
    """Build date filter conditions and parameters."""
    if not date_range:
        return {
            'memory_where': '',
            'memory_params': [],
            'conversation_where': '',
            'conversation_params': []
        }
    
    try:
        if date_range == "last_30_days":
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            return {
                'memory_where': 'WHERE timestamp >= ?',
                'memory_params': [thirty_days_ago],
                'conversation_where': 'WHERE start_time >= ?',
                'conversation_params': [thirty_days_ago]
            }
        elif date_range == "last_7_days":
            seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            return {
                'memory_where': 'WHERE timestamp >= ?',
                'memory_params': [seven_days_ago],
                'conversation_where': 'WHERE start_time >= ?',
                'conversation_params': [seven_days_ago]
            }
        elif ":" in date_range:
            start_date, end_date = date_range.split(":", 1)
            return {
                'memory_where': 'WHERE timestamp BETWEEN ? AND ?',
                'memory_params': [start_date, end_date],
                'conversation_where': 'WHERE start_time BETWEEN ? AND ?',
                'conversation_params': [start_date, end_date]
            }
        else:
            # Single date
            return {
                'memory_where': 'WHERE DATE(timestamp) = ?',
                'memory_params': [date_range],
                'conversation_where': 'WHERE DATE(start_time) = ?',
                'conversation_params': [date_range]
            }
    except Exception as e:
        logger.error(f"Error building date filter: {e}")
        return {
            'memory_where': '',
            'memory_params': [],
            'conversation_where': '',
            'conversation_params': []
        } 