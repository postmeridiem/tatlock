"""
Tests for hippocampus.remember
"""
import sqlite3
from hippocampus.user_database import ensure_user_database, delete_user_database, get_database_connection
from hippocampus.remember import save_interaction, get_or_create_topic, create_or_update_conversation

def test_save_interaction_and_get_or_create_topic():
    username = "testremember"
    ensure_user_database(username)
    # Save an interaction
    interaction_id = save_interaction(
        user_prompt="What is the capital of France?",
        llm_reply="Paris is the capital of France.",
        full_llm_history=[],
        topic="geography",
        username=username,
        conversation_id="convgeo"
    )
    assert interaction_id is not None
    # Check that the topic exists
    conn = get_database_connection(username)
    topic_id = get_or_create_topic(conn, "geography")
    assert topic_id is not None
    conn.close()
    delete_user_database(username)

def test_create_or_update_conversation():
    username = "testconvupdate"
    ensure_user_database(username)
    # Create or update conversation
    result = create_or_update_conversation("convupdate1", username, title="Test Conversation")
    assert result is True
    # Check that the conversation exists
    conn = get_database_connection(username)
    cursor = conn.cursor()
    cursor.execute("SELECT conversation_id, title FROM conversations WHERE conversation_id = ?", ("convupdate1",))
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "convupdate1"
    assert row[1] == "Test Conversation"
    conn.close()
    delete_user_database(username) 