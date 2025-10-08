"""
Conversation Compacting Module

This module provides conservative conversation summarization to reduce token usage
while preserving critical context. Every 50 messages (25 user+assistant interaction pairs),
it creates a compact summary of the conversation history.

Key Features:
- Conservative summarization that preserves ALL facts, names, dates, numbers
- Non-overlapping compacting mechanism (1-50, 51-100, 101-150, etc.)
- Smart context loading that combines compact summaries with recent messages
- Automatic triggering after every 50 messages (COMPACT_INTERVAL=50)
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
import ollama

from config import OLLAMA_MODEL
from hippocampus.recall import get_conversation_messages

logger = logging.getLogger(__name__)

# Compact every N messages (50 = 25 interactions of user+assistant pairs)
COMPACT_INTERVAL = 50


def _build_conservative_compact_prompt(messages: List[Dict], conversation_id: str) -> str:
    """
    Build a CONSERVATIVE and DEFENSIVE prompt for compacting conversation history.

    STRICT RULES:
    - Preserve ALL facts, names, dates, numbers, technical details
    - NO interpretation or assumptions
    - NO speculation (avoid words like "probably", "might have", "seems")
    - Chronological order with clear attribution
    - Mark unresolved questions explicitly
    """

    messages_text = []
    for idx, msg in enumerate(messages, 1):
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        timestamp = msg.get('timestamp', 'unknown')
        messages_text.append(f"[Message {idx}] {role.upper()} ({timestamp}):\n{content}\n")

    messages_block = "\n".join(messages_text)

    prompt = f"""You are creating a CONSERVATIVE SUMMARY of a conversation. Your goal is to preserve ALL information without loss.

STRICT REQUIREMENTS:
1. Preserve EVERY fact, name, date, number, technical detail, and specific claim
2. DO NOT interpret, assume, or infer anything not explicitly stated
3. DO NOT use speculation words: "probably", "might", "seems", "appears", "likely"
4. Maintain chronological order
5. Attribute each fact to its source (User said X, Assistant said Y)
6. If a question was asked but not fully resolved, mark it as [UNRESOLVED]
7. Include ALL error messages, file names, code snippets, and technical details
8. If something is ambiguous, preserve the ambiguity - do not resolve it

CONVERSATION TO SUMMARIZE (Conversation ID: {conversation_id}):

{messages_block}

OUTPUT FORMAT:
Provide a chronological summary using this exact structure:

TOPICS DISCUSSED:
- [List each distinct topic]

FACTUAL TIMELINE:
1. User stated/asked: [exact claim or question]
   Assistant responded: [exact response or action taken]
   Outcome: [what happened - resolved/unresolved/pending]

2. [Continue for each interaction]

KEY FACTS ESTABLISHED:
- [Fact 1 with source attribution]
- [Fact 2 with source attribution]

UNRESOLVED ITEMS:
- [Any questions, issues, or tasks not fully completed]

TECHNICAL DETAILS:
- [File names, paths, versions, commands, error messages, etc.]

Remember: CONSERVATIVE means preserving MORE detail, not less. When in doubt, include it."""

    return prompt


def create_conversation_compact(
    username: str,
    conversation_id: str,
    db_path: str
) -> Optional[Dict]:
    """
    Create a compact summary of conversation messages using LLM.

    Args:
        username: User whose conversation to compact
        conversation_id: Conversation to compact
        db_path: Path to user's database

    Returns:
        Dict with compact_id, summary, topics, and message count, or None on failure
    """
    try:
        # Find the last compact to determine which messages to summarize
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get total message count first to calculate target boundary
        cursor.execute("""
            SELECT COUNT(*) FROM conversation_messages WHERE conversation_id = ?
        """, (conversation_id,))
        total_messages = cursor.fetchone()[0]
        target_boundary = (total_messages // COMPACT_INTERVAL) * COMPACT_INTERVAL

        # Check if compact already exists for this boundary (prevent race conditions)
        cursor.execute("""
            SELECT compact_id FROM conversation_compacts
            WHERE conversation_id = ? AND messages_up_to = ?
        """, (conversation_id, target_boundary))

        if cursor.fetchone() is not None:
            logger.info(f"Compact already exists for conversation {conversation_id} at boundary {target_boundary}")
            conn.close()
            return None

        cursor.execute("""
            SELECT messages_up_to
            FROM conversation_compacts
            WHERE conversation_id = ?
            ORDER BY compact_timestamp DESC
            LIMIT 1
        """, (conversation_id,))

        last_compact = cursor.fetchone()
        start_from = last_compact[0] + 1 if last_compact else 1

        # Get messages to compact from conversation_messages table
        cursor.execute("""
            SELECT role, content, timestamp
            FROM conversation_messages
            WHERE conversation_id = ?
            ORDER BY message_number ASC
        """, (conversation_id,))

        all_messages = cursor.fetchall()

        logger.info(f"Compact creation: conversation_id={conversation_id}, start_from={start_from}, total_messages={len(all_messages)}, COMPACT_INTERVAL={COMPACT_INTERVAL}")

        # Convert to list of dicts and slice to get messages for this compact
        messages_to_compact = [
            {
                'role': msg[0],
                'content': msg[1],
                'timestamp': msg[2]
            }
            for idx, msg in enumerate(all_messages, 1)
            if start_from <= idx < start_from + COMPACT_INTERVAL
        ]

        if not messages_to_compact:
            logger.warning(f"No messages to compact for conversation {conversation_id}: start_from={start_from}, total_messages={len(all_messages)}, COMPACT_INTERVAL={COMPACT_INTERVAL}")
            conn.close()
            return None

        messages_up_to = start_from + len(messages_to_compact) - 1

        # Build conservative prompt
        prompt = _build_conservative_compact_prompt(messages_to_compact, conversation_id)

        # Call LLM for summarization using ollama library
        try:
            logger.info(f"Calling LLM for summarization: model={OLLAMA_MODEL}, message_count={len(messages_to_compact)}")

            # Use ollama with timeout via options
            response = ollama.chat(
                model=OLLAMA_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"num_predict": 2000}  # Limit response length to ensure faster completion
            )

            logger.info(f"LLM call completed, processing response...")
            compact_summary = response.get('message', {}).get('content', '')

            if not compact_summary:
                logger.error(f"Empty summary returned from LLM for conversation {conversation_id}")
                conn.close()
                return None

            logger.info(f"LLM summarization succeeded: summary_length={len(compact_summary)}")

        except Exception as e:
            logger.error(f"LLM summarization failed for conversation {conversation_id}: {e}", exc_info=True)
            conn.close()
            return None

        # Extract topics from summary (look for "TOPICS DISCUSSED:" section)
        topics = []
        if "TOPICS DISCUSSED:" in compact_summary:
            lines = compact_summary.split('\n')
            in_topics = False
            for line in lines:
                if "TOPICS DISCUSSED:" in line:
                    in_topics = True
                    continue
                if in_topics:
                    if line.strip().startswith('-'):
                        topics.append(line.strip()[1:].strip())
                    elif line.strip() and not line.strip().startswith('-'):
                        break  # End of topics section

        topics_str = ", ".join(topics) if topics else "General conversation"

        # Save compact to database
        compact_id = str(uuid.uuid4())
        compact_timestamp = datetime.utcnow().isoformat()

        cursor.execute("""
            INSERT INTO conversation_compacts
            (compact_id, conversation_id, compact_timestamp, messages_up_to, compact_summary, topics_covered)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (compact_id, conversation_id, compact_timestamp, messages_up_to, compact_summary, topics_str))

        conn.commit()
        conn.close()

        logger.info(f"Created compact {compact_id} for conversation {conversation_id} (messages 1-{messages_up_to})")

        return {
            'compact_id': compact_id,
            'compact_summary': compact_summary,
            'topics_covered': topics_str,
            'messages_up_to': messages_up_to
        }

    except Exception as e:
        logger.error(f"Error creating conversation compact: {e}")
        return None


def get_conversation_context(
    username: str,
    conversation_id: str,
    db_path: str
) -> Tuple[Optional[str], List[Dict]]:
    """
    Smart context loader that returns (compact_summary, recent_uncompacted_messages).

    This ensures NO OVERLAP between compacted and uncompacted messages:
    - Loads the most recent compact summary (if exists)
    - Loads ONLY messages since the last compact interval boundary
    - Calculates which messages to load based on total count / COMPACT_INTERVAL

    Args:
        username: User requesting context
        conversation_id: Conversation to load
        db_path: Path to user's database

    Returns:
        Tuple of (compact_summary_text, list_of_recent_messages)
        compact_summary_text is None if no compact exists yet
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get total message count for this conversation
        cursor.execute("""
            SELECT COUNT(*) FROM conversation_messages WHERE conversation_id = ?
        """, (conversation_id,))
        total_messages = cursor.fetchone()[0]

        if total_messages == 0:
            conn.close()
            return (None, [])

        # Calculate the last compact boundary (highest multiple of COMPACT_INTERVAL <= total)
        last_compact_boundary = (total_messages // COMPACT_INTERVAL) * COMPACT_INTERVAL

        if last_compact_boundary > 0:
            # Get the compact for this boundary
            cursor.execute("""
                SELECT compact_summary, messages_up_to
                FROM conversation_compacts
                WHERE conversation_id = ? AND messages_up_to = ?
                ORDER BY compact_timestamp DESC
                LIMIT 1
            """, (conversation_id, last_compact_boundary))

            compact_row = cursor.fetchone()
            compact_summary = compact_row[0] if compact_row else None

            # Load messages AFTER the last compact boundary
            cursor.execute("""
                SELECT role, content, timestamp
                FROM conversation_messages
                WHERE conversation_id = ? AND message_number > ?
                ORDER BY message_number ASC
            """, (conversation_id, last_compact_boundary))

            uncompacted_rows = cursor.fetchall()

            # Convert to list of dicts
            uncompacted_messages = [
                {
                    'role': msg[0],
                    'content': msg[1],
                    'timestamp': msg[2]
                }
                for msg in uncompacted_rows
            ]

            conn.close()
            return (compact_summary, uncompacted_messages)
        else:
            # Less than COMPACT_INTERVAL messages, no compact exists
            # Get all messages
            cursor.execute("""
                SELECT role, content, timestamp
                FROM conversation_messages
                WHERE conversation_id = ?
                ORDER BY message_number ASC
            """, (conversation_id,))

            all_messages = cursor.fetchall()
            recent_messages = [
                {
                    'role': msg[0],
                    'content': msg[1],
                    'timestamp': msg[2]
                }
                for msg in all_messages
            ]

            conn.close()
            return (None, recent_messages)

    except Exception as e:
        logger.error(f"Error loading conversation context: {e}")
        return (None, [])


def should_compact_conversation(username: str, conversation_id: str, db_path: str) -> bool:
    """
    Check if conversation has reached the compacting threshold.

    Returns True if:
    - Total messages >= COMPACT_INTERVAL
    - Messages since last compact >= COMPACT_INTERVAL
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get total message count
        cursor.execute("""
            SELECT COUNT(*) FROM conversation_messages WHERE conversation_id = ?
        """, (conversation_id,))
        total_count = cursor.fetchone()[0]

        # Get last compact
        cursor.execute("""
            SELECT messages_up_to
            FROM conversation_compacts
            WHERE conversation_id = ?
            ORDER BY compact_timestamp DESC
            LIMIT 1
        """, (conversation_id,))

        last_compact = cursor.fetchone()
        conn.close()

        if last_compact:
            messages_since_compact = total_count - last_compact[0]
            return messages_since_compact >= COMPACT_INTERVAL
        else:
            return total_count >= COMPACT_INTERVAL

    except Exception as e:
        logger.error(f"Error checking compact threshold: {e}")
        return False


def trigger_compact_if_needed(username: str, conversation_id: str, db_path: str) -> bool:
    """
    Automatically trigger compacting if threshold is reached.

    Call this after saving each interaction.

    Returns:
        True if compact was created, False otherwise
    """
    if should_compact_conversation(username, conversation_id, db_path):
        logger.info(f"Triggering automatic compact for conversation {conversation_id}")
        result = create_conversation_compact(username, conversation_id, db_path)
        return result is not None
    return False
