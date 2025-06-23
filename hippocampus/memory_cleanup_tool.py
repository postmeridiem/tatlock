"""
hippocampus/memory_cleanup_tool.py

Tool for memory cleanup and management, including finding duplicate or similar memories.
"""

import logging
import sqlite3
from difflib import SequenceMatcher
from hippocampus.database import get_database_connection
from stem.security import current_user

# Set up logging for this module
logger = logging.getLogger(__name__)

def execute_memory_cleanup(cleanup_type: str = "duplicates", similarity_threshold: float = 0.8) -> dict:
    """
    Perform memory cleanup operations to maintain database health and remove duplicates.
    
    Args:
        cleanup_type (str): Type of cleanup to perform. Options: "duplicates", "orphans", "analysis"
        similarity_threshold (float): Threshold for considering memories similar (0.0 to 1.0). Defaults to 0.8.
        
    Returns:
        dict: Status and cleanup results or message.
    """
    try:
        user = current_user
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        conn = get_database_connection(user.username)
        if not conn:
            return {"status": "error", "message": "Could not connect to user database"}
        
        cursor = conn.cursor()
        
        if cleanup_type == "duplicates":
            results = _find_duplicate_memories(cursor, similarity_threshold)
        elif cleanup_type == "orphans":
            results = _find_orphaned_records(cursor)
        elif cleanup_type == "analysis":
            results = _analyze_memory_health(cursor)
        else:
            return {"status": "error", "message": f"Unknown cleanup type: {cleanup_type}"}
        
        conn.close()
        
        if not results:
            return {
                "status": "success", 
                "data": {}, 
                "message": f"No issues found for {cleanup_type} cleanup."
            }
        
        return {"status": "success", "data": results}
        
    except Exception as e:
        logger.error(f"Error performing memory cleanup for {cleanup_type}: {e}")
        return {"status": "error", "message": f"Memory cleanup failed for cleanup_type '{cleanup_type}': {e}"}

def _find_duplicate_memories(cursor, similarity_threshold: float) -> dict:
    """Find duplicate or very similar memories."""
    try:
        # Get all memories with their content
        cursor.execute("""
            SELECT id, user_prompt, llm_reply, timestamp, conversation_id
            FROM memories
            ORDER BY timestamp DESC
        """)
        memories = cursor.fetchall()
        
        duplicates = []
        processed = set()
        
        for i, (id1, prompt1, reply1, timestamp1, conv1) in enumerate(memories):
            if id1 in processed:
                continue
                
            similar_memories = []
            
            for j, (id2, prompt2, reply2, timestamp2, conv2) in enumerate(memories[i+1:], i+1):
                if id2 in processed:
                    continue
                
                # Calculate similarity scores
                prompt_similarity = SequenceMatcher(None, prompt1 or "", prompt2 or "").ratio()
                reply_similarity = SequenceMatcher(None, reply1 or "", reply2 or "").ratio()
                
                # Consider memories similar if either prompt or reply is very similar
                if prompt_similarity >= similarity_threshold or reply_similarity >= similarity_threshold:
                    similar_memories.append({
                        "id": id2,
                        "user_prompt": prompt2,
                        "llm_reply": reply2,
                        "timestamp": timestamp2,
                        "conversation_id": conv2,
                        "prompt_similarity": round(prompt_similarity, 3),
                        "reply_similarity": round(reply_similarity, 3)
                    })
                    processed.add(id2)
            
            if similar_memories:
                duplicates.append({
                    "original_memory": {
                        "id": id1,
                        "user_prompt": prompt1,
                        "llm_reply": reply1,
                        "timestamp": timestamp1,
                        "conversation_id": conv1
                    },
                    "similar_memories": similar_memories,
                    "total_similar": len(similar_memories) + 1
                })
                processed.add(id1)
        
        return {
            "duplicate_groups": duplicates,
            "total_duplicate_groups": len(duplicates),
            "total_duplicate_memories": sum(len(group["similar_memories"]) for group in duplicates)
        }
        
    except Exception as e:
        logger.error(f"Error finding duplicate memories: {e}")
        return {}

def _find_orphaned_records(cursor) -> dict:
    """Find orphaned records that reference non-existent data."""
    try:
        orphans = {}
        
        # Find memories with non-existent conversation_id
        cursor.execute("""
            SELECT m.id, m.conversation_id
            FROM memories m
            LEFT JOIN conversations c ON m.conversation_id = c.id
            WHERE m.conversation_id IS NOT NULL AND c.id IS NULL
        """)
        orphaned_memories = cursor.fetchall()
        
        # Find memory_topics with non-existent memory_id
        cursor.execute("""
            SELECT mt.memory_id, mt.topic_id
            FROM memory_topics mt
            LEFT JOIN memories m ON mt.memory_id = m.id
            WHERE m.id IS NULL
        """)
        orphaned_memory_topics = cursor.fetchall()
        
        # Find memory_topics with non-existent topic_id
        cursor.execute("""
            SELECT mt.memory_id, mt.topic_id
            FROM memory_topics mt
            LEFT JOIN topics t ON mt.topic_id = t.id
            WHERE t.id IS NULL
        """)
        orphaned_topic_links = cursor.fetchall()
        
        # Find conversation_topics with non-existent conversation_id
        cursor.execute("""
            SELECT ct.conversation_id, ct.topic_id
            FROM conversation_topics ct
            LEFT JOIN conversations c ON ct.conversation_id = c.id
            WHERE c.id IS NULL
        """)
        orphaned_conversation_topics = cursor.fetchall()
        
        # Find conversation_topics with non-existent topic_id
        cursor.execute("""
            SELECT ct.conversation_id, ct.topic_id
            FROM conversation_topics ct
            LEFT JOIN topics t ON ct.topic_id = t.id
            WHERE t.id IS NULL
        """)
        orphaned_conversation_topic_links = cursor.fetchall()
        
        orphans["orphaned_memories"] = [
            {"memory_id": mem_id, "conversation_id": conv_id}
            for mem_id, conv_id in orphaned_memories
        ]
        
        orphans["orphaned_memory_topics"] = [
            {"memory_id": mem_id, "topic_id": topic_id}
            for mem_id, topic_id in orphaned_memory_topics
        ]
        
        orphans["orphaned_topic_links"] = [
            {"memory_id": mem_id, "topic_id": topic_id}
            for mem_id, topic_id in orphaned_topic_links
        ]
        
        orphans["orphaned_conversation_topics"] = [
            {"conversation_id": conv_id, "topic_id": topic_id}
            for conv_id, topic_id in orphaned_conversation_topics
        ]
        
        orphans["orphaned_conversation_topic_links"] = [
            {"conversation_id": conv_id, "topic_id": topic_id}
            for conv_id, topic_id in orphaned_conversation_topic_links
        ]
        
        # Calculate totals
        total_orphans = (
            len(orphans["orphaned_memories"]) +
            len(orphans["orphaned_memory_topics"]) +
            len(orphans["orphaned_topic_links"]) +
            len(orphans["orphaned_conversation_topics"]) +
            len(orphans["orphaned_conversation_topic_links"])
        )
        
        orphans["total_orphaned_records"] = total_orphans
        
        return orphans
        
    except Exception as e:
        logger.error(f"Error finding orphaned records: {e}")
        return {}

def _analyze_memory_health(cursor) -> dict:
    """Analyze overall memory database health."""
    try:
        # Get basic statistics
        cursor.execute("SELECT COUNT(*) FROM memories")
        total_memories = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        total_conversations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM topics")
        total_topics = cursor.fetchone()[0]
        
        # Check for null values
        cursor.execute("SELECT COUNT(*) FROM memories WHERE user_prompt IS NULL OR user_prompt = ''")
        null_prompts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM memories WHERE llm_reply IS NULL OR llm_reply = ''")
        null_replies = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM memories WHERE timestamp IS NULL")
        null_timestamps = cursor.fetchone()[0]
        
        # Check for very long content (potential issues)
        cursor.execute("SELECT COUNT(*) FROM memories WHERE LENGTH(user_prompt) > 10000")
        long_prompts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM memories WHERE LENGTH(llm_reply) > 10000")
        long_replies = cursor.fetchone()[0]
        
        # Check for memories without topics
        cursor.execute("""
            SELECT COUNT(*) FROM memories m
            LEFT JOIN memory_topics mt ON m.id = mt.memory_id
            WHERE mt.memory_id IS NULL
        """)
        untagged_memories = cursor.fetchone()[0]
        
        # Check for conversations without memories
        cursor.execute("""
            SELECT COUNT(*) FROM conversations c
            LEFT JOIN memories m ON c.id = m.conversation_id
            WHERE m.conversation_id IS NULL
        """)
        empty_conversations = cursor.fetchone()[0]
        
        # Calculate health scores
        data_quality_score = 100
        if total_memories > 0:
            data_quality_score -= (null_prompts + null_replies + null_timestamps) / total_memories * 100
        
        completeness_score = 100
        if total_memories > 0:
            completeness_score -= untagged_memories / total_memories * 100
        
        return {
            "basic_stats": {
                "total_memories": total_memories,
                "total_conversations": total_conversations,
                "total_topics": total_topics
            },
            "data_quality_issues": {
                "null_prompts": null_prompts,
                "null_replies": null_replies,
                "null_timestamps": null_timestamps,
                "long_prompts": long_prompts,
                "long_replies": long_replies
            },
            "structural_issues": {
                "untagged_memories": untagged_memories,
                "empty_conversations": empty_conversations
            },
            "health_scores": {
                "data_quality_score": round(max(0, data_quality_score), 1),
                "completeness_score": round(max(0, completeness_score), 1)
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing memory health: {e}")
        return {} 