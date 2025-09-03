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
    get_conversation_summary,
    get_user_conversations,
    get_conversation_details,
    search_conversations
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

def test_get_conversation_details_with_summary():
    """Test conversation details extraction with summary from first user prompt."""
    username = "testdetailssum"
    ensure_user_database(username)
    
    # Save interactions with explicit user prompts
    save_interaction(
        user_prompt="What's the weather like?",
        llm_reply="It's sunny and warm.",
        full_llm_history=[],
        topic="weather",
        username=username,
        conversation_id="conv_detail_1"
    )
    save_interaction(
        user_prompt="Any rain expected?",
        llm_reply="No rain expected today.",
        full_llm_history=[],
        topic="weather",
        username=username,
        conversation_id="conv_detail_1"
    )
    
    user = UserModel(
        username=username, 
        email=f"{username}@test.com", 
        first_name="Test", 
        last_name="User", 
        created_at="2024-01-01T00:00:00Z"
    )
    
    details = get_conversation_details("conv_detail_1", user)
    
    assert details is not None
    assert details['conversation_id'] == "conv_detail_1"
    assert details['summary'] == "What's the weather like?"  # First user prompt
    assert len(details['topics']) > 0
    
    delete_user_database(username)

def test_get_conversation_details_no_prompts():
    """Test conversation details when no user prompts exist."""
    username = "testdetailsnoprompt"
    ensure_user_database(username)
    
    # Create a conversation with no user prompts (edge case)
    execute_user_query(username, """
        INSERT INTO conversations (conversation_id, title, started_at, last_activity, message_count)
        VALUES (?, ?, datetime('now'), datetime('now'), 0)
    """, ("conv_no_prompt", "Empty Conversation"))
    
    user = UserModel(
        username=username, 
        email=f"{username}@test.com", 
        first_name="Test", 
        last_name="User", 
        created_at="2024-01-01T00:00:00Z"
    )
    
    details = get_conversation_details("conv_no_prompt", user)
    
    assert details is not None
    assert details['conversation_id'] == "conv_no_prompt"
    assert details['summary'] == "No summary available."
    
    delete_user_database(username)

def test_get_user_conversations_with_summaries():
    """Test retrieving user conversations with summaries included."""
    username = "testuserconvsum"
    ensure_user_database(username)
    
    # Save multiple conversations with different prompts
    save_interaction(
        user_prompt="Tell me about AI",
        llm_reply="AI is artificial intelligence.",
        full_llm_history=[],
        topic="technology",
        username=username,
        conversation_id="conv_ai"
    )
    save_interaction(
        user_prompt="How's the weather?",
        llm_reply="It's sunny today.",
        full_llm_history=[],
        topic="weather",
        username=username,
        conversation_id="conv_weather"
    )
    
    user = UserModel(
        username=username, 
        email=f"{username}@test.com", 
        first_name="Test", 
        last_name="User", 
        created_at="2024-01-01T00:00:00Z"
    )
    
    conversations = get_user_conversations(user, limit=10)
    
    assert len(conversations) >= 2
    
    # Check that summaries are included
    conv_summaries = [c['summary'] for c in conversations if c.get('summary')]
    assert "Tell me about AI" in conv_summaries or "How's the weather?" in conv_summaries
    
    # Check that topics are included
    conv_topics = [c.get('topic') for c in conversations if c.get('topic')]
    assert any(topic in ['technology', 'weather'] for topic in conv_topics)
    
    delete_user_database(username)

def test_search_conversations_with_summaries():
    """Test searching conversations with summaries functionality."""
    username = "testsearchsum"
    ensure_user_database(username)
    
    # Save conversations with searchable titles
    save_interaction(
        user_prompt="What are machine learning algorithms?",
        llm_reply="ML algorithms are computational methods.",
        full_llm_history=[],
        topic="technology",
        username=username,
        conversation_id="conv_ml"
    )
    save_interaction(
        user_prompt="Explain weather patterns",
        llm_reply="Weather patterns are influenced by many factors.",
        full_llm_history=[],
        topic="weather",
        username=username,
        conversation_id="conv_patterns"
    )
    
    # Update conversation titles to make them searchable
    execute_user_query(username, """
        UPDATE conversations SET title = ? WHERE conversation_id = ?
    """, ("Machine Learning Discussion", "conv_ml"))
    
    execute_user_query(username, """
        UPDATE conversations SET title = ? WHERE conversation_id = ?
    """, ("Weather Patterns Chat", "conv_patterns"))
    
    user = UserModel(
        username=username, 
        email=f"{username}@test.com", 
        first_name="Test", 
        last_name="User", 
        created_at="2024-01-01T00:00:00Z"
    )
    
    # Search for machine learning
    ml_results = search_conversations(user, "machine", limit=10)
    
    assert len(ml_results) >= 1
    ml_conv = next((c for c in ml_results if c['conversation_id'] == 'conv_ml'), None)
    assert ml_conv is not None
    assert ml_conv['summary'] == "What are machine learning algorithms?"
    assert ml_conv.get('topic') == "technology"
    
    # Search for weather
    weather_results = search_conversations(user, "weather", limit=10)
    
    assert len(weather_results) >= 1
    weather_conv = next((c for c in weather_results if c['conversation_id'] == 'conv_patterns'), None)
    assert weather_conv is not None
    assert weather_conv['summary'] == "Explain weather patterns"
    
    delete_user_database(username)

def test_conversation_summary_edge_cases():
    """Test edge cases for conversation summaries."""
    username = "testesummedge"
    ensure_user_database(username)
    
    # Test conversation with empty user prompt
    save_interaction(
        user_prompt="",
        llm_reply="I'm here to help.",
        full_llm_history=[],
        topic="general",
        username=username,
        conversation_id="conv_empty"
    )
    
    # Test conversation with only whitespace prompt
    save_interaction(
        user_prompt="   ",
        llm_reply="What can I help you with?",
        full_llm_history=[],
        topic="general",
        username=username,
        conversation_id="conv_whitespace"
    )
    
    # Test conversation with valid prompt after empty ones
    save_interaction(
        user_prompt="",
        llm_reply="Empty prompt.",
        full_llm_history=[],
        topic="general",
        username=username,
        conversation_id="conv_mixed"
    )
    save_interaction(
        user_prompt="What is Python?",
        llm_reply="Python is a programming language.",
        full_llm_history=[],
        topic="programming",
        username=username,
        conversation_id="conv_mixed"
    )
    
    user = UserModel(
        username=username, 
        email=f"{username}@test.com", 
        first_name="Test", 
        last_name="User", 
        created_at="2024-01-01T00:00:00Z"
    )
    
    # Test empty prompt conversation
    empty_details = get_conversation_details("conv_empty", user)
    assert empty_details['summary'] == "No summary available."
    
    # Test whitespace prompt conversation  
    whitespace_details = get_conversation_details("conv_whitespace", user)
    assert whitespace_details['summary'] == "No summary available."
    
    # Test mixed conversation - should get first valid prompt
    mixed_details = get_conversation_details("conv_mixed", user)
    assert mixed_details['summary'] == "What is Python?"
    
    delete_user_database(username) 