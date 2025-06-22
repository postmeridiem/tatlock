"""
Tests for hippocampus.recall
"""
import pytest
from hippocampus.user_database import ensure_user_database, delete_user_database, execute_user_query
from hippocampus.remember import save_interaction
from hippocampus.recall import (
    recall_memories,
    recall_memories_with_time,
    get_conversations_by_topic,
    get_topics_by_conversation,
    get_conversation_summary
)
from stem.models import UserModel
from datetime import datetime

def setup_test_memories(username):
    ensure_user_database(username)
    
    # Save a few interactions with topics and conversation IDs
    save_interaction(
        user_prompt="What is the weather?",
        llm_reply="It's sunny.",
        full_llm_history=[],
        topic="weather",
        username=username,
        conversation_id="conv1"
    )
    save_interaction(
        user_prompt="Tell me a joke.",
        llm_reply="Why did the chicken cross the road?",
        full_llm_history=[],
        topic="jokes",
        username=username,
        conversation_id="conv2"
    )

def test_recall_memories():
    username = "testrecall"
    setup_test_memories(username)
    user = UserModel(
        username=username, 
        email=f"{username}@test.com", 
        first_name="Test", 
        last_name="User", 
        created_at="2024-01-01T00:00:00Z"
    )
    results = recall_memories(user, "weather")
    assert any("weather" in (r.get("topic_name") or "") for r in results)
    results = recall_memories(user, "joke")
    assert any("joke" in (r.get("user_prompt") or "") for r in results)
    delete_user_database(username)

def test_recall_memories_with_time():
    username = "testrecalltime"
    setup_test_memories(username)
    user = UserModel(
        username=username, 
        email=f"{username}@test.com", 
        first_name="Test", 
        last_name="User", 
        created_at="2024-01-01T00:00:00Z"
    )
    today = datetime.now().strftime("%Y-%m-%d")
    results = recall_memories_with_time(user, "weather", start_date=today)
    assert any("weather" in (r.get("topic_name") or "") for r in results)
    delete_user_database(username)

def test_get_conversations_by_topic():
    username = "testconvtopic"
    setup_test_memories(username)
    user = UserModel(
        username=username, 
        email=f"{username}@test.com", 
        first_name="Test", 
        last_name="User", 
        created_at="2024-01-01T00:00:00Z"
    )
    results = get_conversations_by_topic("weather", user)
    assert any(r.get("topic_name") == "weather" for r in results)
    delete_user_database(username)

def test_get_topics_by_conversation():
    username = "testtopicsconv"
    setup_test_memories(username)
    user = UserModel(
        username=username, 
        email=f"{username}@test.com", 
        first_name="Test", 
        last_name="User", 
        created_at="2024-01-01T00:00:00Z"
    )
    results = get_topics_by_conversation("conv1", user)
    assert any(r.get("topic_name") == "weather" for r in results)
    delete_user_database(username)

def test_get_conversation_summary():
    username = "testconvsum"
    setup_test_memories(username)
    user = UserModel(
        username=username, 
        email=f"{username}@test.com", 
        first_name="Test", 
        last_name="User", 
        created_at="2024-01-01T00:00:00Z"
    )
    summary = get_conversation_summary("conv1", user)
    assert summary.get("conversation_id") == "conv1"
    assert any(t.get("topic_name") == "weather" for t in summary.get("topics", []))
    delete_user_database(username) 