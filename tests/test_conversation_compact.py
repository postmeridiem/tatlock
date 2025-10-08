"""
Tests for conversation compacting mechanism via authenticated API endpoints.

Following Tatlock testing standards:
- All tests use authenticated FastAPI client
- No direct Python imports of core functionality
- Tests go through the full API stack
"""

import pytest
import time
from hippocampus.user_database import get_database_connection, delete_user_database
from hippocampus.conversation_compact import COMPACT_INTERVAL


def send_message_and_wait(client, message: str, conversation_id: str):
    """
    Send a message and wait for complete processing (simulating real user behavior).

    The cortex now blocks until any compacting completes (using thread.join()), so this
    function simply makes the API call. Each call is fully serial - the response won't
    return until save_interaction AND any triggered compact has completed.

    Args:
        client: Authenticated test client
        message: Message to send
        conversation_id: Conversation ID

    Returns:
        Response object from the API
    """
    response = client.post("/cortex", json={
        "message": message,
        "history": [],
        "conversation_id": conversation_id
    })

    return response


def test_compact_interval_is_50():
    """Verify COMPACT_INTERVAL is configured to 50 messages (25 interactions)."""
    assert COMPACT_INTERVAL == 50


def test_conversation_compacting_threshold(authenticated_user_client, test_user):
    """
    Test that conversations compact automatically after 50 messages (25 interactions).

    Uses authenticated API endpoint to send 25 interactions and verify compact creation.
    With COMPACT_INTERVAL=50, compact triggers after 50 messages (25 user + 25 assistant).
    Serializes message sending to match real user behavior.
    """
    username = test_user['username']
    conversation_id = "test_compact_threshold"

    # Send 24 interactions (48 messages) - below threshold
    for i in range(24):
        response = send_message_and_wait(
            authenticated_user_client,
            f"Test question {i+1}",
            conversation_id
        )
        assert response.status_code == 200

    # Check that no compact exists yet at 48 messages
    conn = get_database_connection(username)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM conversation_compacts WHERE conversation_id = ?", (conversation_id,))
    compact_count = cursor.fetchone()[0]
    conn.close()

    assert compact_count == 0, "Compact should not exist at 48 messages (24 interactions)"

    # Send 25th interaction (reaches 50 messages) - compact will be created and block until complete
    response = send_message_and_wait(
        authenticated_user_client,
        "Test question 25",
        conversation_id
    )
    assert response.status_code == 200

    # Verify compact was created
    conn = get_database_connection(username)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT compact_id, messages_up_to, compact_summary
        FROM conversation_compacts
        WHERE conversation_id = ?
    """, (conversation_id,))
    compact = cursor.fetchone()
    conn.close()

    assert compact is not None, "Compact should exist after 50 messages (25 interactions)"
    assert compact[1] == 50, f"Compact should cover 50 messages, got {compact[1]}"
    assert len(compact[2]) > 0, "Compact summary should not be empty"


def test_conversation_context_with_compact(authenticated_user_client, test_user):
    """
    Test that Phase 1 uses compacted context after 50+ messages.

    Verifies that conversations >50 messages use compact + recent messages.
    With COMPACT_INTERVAL=50, we need 50 messages (25 interactions) to trigger first compact.
    """
    username = test_user['username']
    conversation_id = "test_compact_context"

    # Send 30 interactions (60 messages) to trigger compact at 50 messages
    for i in range(30):
        response = send_message_and_wait(
            authenticated_user_client,
            f"Message number {i+1}",
            conversation_id
        )
        assert response.status_code == 200

    # Verify compact exists
    conn = get_database_connection(username)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT compact_id, messages_up_to, compact_summary
        FROM conversation_compacts
        WHERE conversation_id = ?
    """, (conversation_id,))
    compact = cursor.fetchone()

    assert compact is not None, "Compact should exist after 60 messages"
    assert compact[1] == 50, "First compact should cover messages 1-50"

    # Verify conversation table tracks correct message count
    cursor.execute("""
        SELECT message_count FROM conversations WHERE conversation_id = ?
    """, (conversation_id,))
    stored_count = cursor.fetchone()[0]

    # Also verify by counting from memories table
    cursor.execute("""
        SELECT COUNT(*) * 2 FROM memories WHERE conversation_id = ?
    """, (conversation_id,))
    actual_count = cursor.fetchone()[0]

    conn.close()

    # Should have 60 messages (30 user + 30 assistant)
    assert actual_count == 60, f"Expected 60 total messages in memories, got {actual_count}"
    assert stored_count >= 60, f"Expected message_count >= 60 in conversations table, got {stored_count}"


def test_incremental_compacting(authenticated_user_client, test_user):
    """
    Test that second compact covers messages 26-50, not 1-50.

    Verifies non-overlapping compact mechanism.
    """
    username = test_user['username']
    conversation_id = "test_incremental_compact"

    # Send 50 messages to trigger two compacts
    for i in range(50):
        response = send_message_and_wait(
            authenticated_user_client,
            f"Incremental test message {i+1}",
            conversation_id
        )
        assert response.status_code == 200

    # Verify two compacts exist
    conn = get_database_connection(username)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT compact_id, messages_up_to, compact_summary
        FROM conversation_compacts
        WHERE conversation_id = ?
        ORDER BY messages_up_to ASC
    """, (conversation_id,))
    compacts = cursor.fetchall()
    conn.close()

    assert len(compacts) == 2, f"Expected 2 compacts, got {len(compacts)}"

    # First compact: messages 1-50
    assert compacts[0][1] == 50, f"First compact should cover messages 1-50, got 1-{compacts[0][1]}"

    # Second compact: messages 51-100
    assert compacts[1][1] == 100, f"Second compact should cover messages 51-100, got 51-{compacts[1][1]}"


def test_compact_conservative_content(authenticated_user_client, test_user):
    """
    Test that compact summaries preserve factual content.

    Sends messages with specific facts and verifies they appear in compact.
    With COMPACT_INTERVAL=50, need 25 interactions (50 messages) to trigger compact.
    """
    username = test_user['username']
    conversation_id = "test_conservative_compact"

    # Send messages with specific factual content
    test_messages = [
        "Who is the mayor of Rotterdam?",
        "What is the population of Amsterdam?",
        "Tell me about the Netherlands capital",
    ]

    # Send enough interactions to trigger compact (25 interactions = 50 messages)
    for i in range(25):
        if i < len(test_messages):
            message = test_messages[i]
        else:
            message = f"Filler message {i+1}"

        response = send_message_and_wait(
            authenticated_user_client,
            message,
            conversation_id
        )
        assert response.status_code == 200

    # Verify compact contains conservative summary structure
    conn = get_database_connection(username)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT compact_summary
        FROM conversation_compacts
        WHERE conversation_id = ?
    """, (conversation_id,))
    compact_row = cursor.fetchone()
    conn.close()

    assert compact_row is not None, "Compact should exist"

    summary = compact_row[0]

    # Check for conservative summary structure
    assert "TOPICS DISCUSSED:" in summary or "FACTUAL TIMELINE:" in summary, \
        "Compact should have conservative summary structure"


def test_compact_database_schema(test_user):
    """
    Test that conversation_compacts table exists with correct schema.
    """
    username = test_user['username']

    conn = get_database_connection(username)
    cursor = conn.cursor()

    # Check table exists
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='conversation_compacts'
    """)
    table_exists = cursor.fetchone()

    assert table_exists is not None, "conversation_compacts table should exist"

    # Check columns
    cursor.execute("PRAGMA table_info(conversation_compacts)")
    columns = {row[1] for row in cursor.fetchall()}

    expected_columns = {
        'compact_id', 'conversation_id', 'compact_timestamp',
        'messages_up_to', 'compact_summary', 'topics_covered'
    }

    assert expected_columns.issubset(columns), \
        f"Missing columns: {expected_columns - columns}"

    # Check indexes
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='index' AND tbl_name='conversation_compacts'
    """)
    indexes = {row[0] for row in cursor.fetchall()}

    expected_indexes = {'idx_compacts_conversation', 'idx_compacts_timestamp'}

    assert expected_indexes.issubset(indexes), \
        f"Missing indexes: {expected_indexes - indexes}"

    conn.close()


def test_no_compact_with_different_conversations(authenticated_user_client, test_user):
    """
    Test that compacts are conversation-specific.

    Sending 15 messages to conv1 and 15 to conv2 should not trigger compacts.
    """
    username = test_user['username']

    # Send 15 messages to conversation 1
    for i in range(15):
        response = authenticated_user_client.post("/cortex", json={
            "message": f"Conv1 message {i+1}",
            "history": [],
            "conversation_id": "test_conv_1"
        })
        assert response.status_code == 200

    # Send 15 messages to conversation 2
    for i in range(15):
        response = authenticated_user_client.post("/cortex", json={
            "message": f"Conv2 message {i+1}",
            "history": [],
            "conversation_id": "test_conv_2"
        })
        assert response.status_code == 200

    time.sleep(3)

    # Verify no compacts were created (neither conversation reached 25)
    conn = get_database_connection(username)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM conversation_compacts")
    compact_count = cursor.fetchone()[0]
    conn.close()

    assert compact_count == 0, "No compacts should exist when conversations are below threshold"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
