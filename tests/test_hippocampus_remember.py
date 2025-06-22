"""
Tests for hippocampus.remember
"""
import sqlite3
from hippocampus.user_database import ensure_user_database, delete_user_database, get_database_connection
from hippocampus.remember import save_interaction, get_or_create_topic, create_or_update_conversation
from stem.models import UserModel

def make_test_user(username: str) -> UserModel:
    return UserModel(
        username=username,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        created_at="2024-01-01T00:00:00",
        roles=[],
        groups=[]
    )

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
    assert conn is not None
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
    assert conn is not None
    cursor = conn.cursor()
    cursor.execute("SELECT conversation_id, title FROM conversations WHERE conversation_id = ?", ("convupdate1",))
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "convupdate1"
    assert row[1] == "Test Conversation"
    conn.close()
    delete_user_database(username)

def test_update_conversation_topics_after_save_interaction():
    username = "testtopiclink"
    ensure_user_database(username)
    topic = "unique_test_topic"
    conversation_id = "convtopiclink1"
    # Save an interaction with the topic
    interaction_id = save_interaction(
        user_prompt="Tell me about the unique test topic.",
        llm_reply="This is a reply about the unique test topic.",
        full_llm_history=[],
        topic=topic,
        username=username,
        conversation_id=conversation_id
    )
    assert interaction_id is not None
    # Check that the topic is linked in conversation_topics
    conn = get_database_connection(username)
    assert conn is not None
    cursor = conn.cursor()
    # Get topic_id
    cursor.execute("SELECT topic_id FROM topics WHERE topic_name = ?", (topic,))
    topic_row = cursor.fetchone()
    assert topic_row is not None
    topic_id = topic_row[0]
    # Check conversation_topics link
    cursor.execute(
        "SELECT conversation_id, topic_id FROM conversation_topics WHERE conversation_id = ? AND topic_id = ?",
        (conversation_id, topic_id)
    )
    link_row = cursor.fetchone()
    assert link_row is not None
    assert link_row[0] == conversation_id
    assert link_row[1] == topic_id
    conn.close()
    delete_user_database(username) 