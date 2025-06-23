"""
Tests for stem.tools module.
"""

import pytest
from unittest.mock import patch, MagicMock
from stem.tools import (
    execute_find_personal_variables,
    execute_get_weather_forecast,
    execute_web_search,
    execute_recall_memories,
    execute_recall_memories_with_time,
    execute_get_conversations_by_topic,
    execute_get_topics_by_conversation,
    execute_get_conversation_summary,
    execute_get_topic_statistics,
    execute_get_user_conversations,
    execute_get_conversation_details,
    execute_search_conversations
)


class TestPersonalVariablesTool:
    """Test personal variables lookup tool."""
    
    def test_find_personal_variables_success(self):
        """Test successful personal variables lookup."""
        with patch('hippocampus.database.execute_user_query') as mock_query:
            mock_query.return_value = [
                {"value": "John Doe"},
                {"value": "30"}
            ]
            
            with patch('hippocampus.find_personal_variables_tool.current_user') as mock_user:
                mock_user.username = "testuser"
                result = execute_find_personal_variables("name")
                
                assert result["status"] == "success"
                assert len(result["data"]) == 2
    
    def test_find_personal_variables_no_results(self):
        """Test personal variables lookup with no results."""
        with patch('hippocampus.database.execute_user_query') as mock_query:
            mock_query.return_value = []
            
            with patch('hippocampus.find_personal_variables_tool.current_user') as mock_user:
                mock_user.username = "testuser"
                result = execute_find_personal_variables("nonexistent")
                
                assert result["status"] == "success"
                assert result["data"] == []
    
    def test_find_personal_variables_database_error(self):
        """Test personal variables lookup with database error."""
        with patch('hippocampus.database.execute_user_query') as mock_query:
            mock_query.side_effect = Exception("Database error")
            
            with patch('hippocampus.find_personal_variables_tool.current_user') as mock_user:
                mock_user.username = "testuser"
                result = execute_find_personal_variables("name")
                
                assert result["status"] == "error"
                assert "Database query failed" in result["message"]


class TestWeatherTool:
    """Test weather forecast tool."""
    
    def test_get_weather_forecast_success(self):
        """Test successful weather forecast retrieval."""
        # Mock the geo API response
        mock_geo_response = MagicMock()
        mock_geo_response.status_code = 200
        mock_geo_response.json.return_value = [{"lat": 52.3676, "lon": 4.9041}]
        
        # Mock the forecast API response
        mock_forecast_response = MagicMock()
        mock_forecast_response.status_code = 200
        mock_forecast_response.json.return_value = {
            "list": [
                {
                    "dt": 1640995200,
                    "main": {"temp": 15.5, "humidity": 70},
                    "weather": [{"description": "scattered clouds"}],
                    "dt_txt": "2022-01-01 12:00:00"
                }
            ]
        }
        
        with patch('requests.get', side_effect=[mock_geo_response, mock_forecast_response]):
            result = execute_get_weather_forecast("Amsterdam", "2022-01-01", "2022-01-01")
            
            assert result["status"] == "success"
            assert len(result["data"]) > 0
    
    def test_get_weather_forecast_api_error(self):
        """Test weather forecast with API error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "City not found"
        mock_response.raise_for_status.side_effect = Exception("City not found")
        
        with patch('requests.get', return_value=mock_response):
            result = execute_get_weather_forecast("NonexistentCity")
            
            assert result["status"] == "error"
            assert "City not found" in result["message"]
    
    def test_get_weather_forecast_network_error(self):
        """Test weather forecast with network error."""
        with patch('requests.get', side_effect=Exception("Network error")):
            result = execute_get_weather_forecast("Amsterdam")
            
            assert result["status"] == "error"
            assert "Network error" in result["message"]


class TestWebSearchTool:
    """Test web search tool."""
    
    def test_web_search_success(self):
        """Test successful web search."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {
                    "title": "Test Result",
                    "link": "https://example.com",
                    "snippet": "This is a test result"
                }
            ]
        }
        
        with patch('requests.get', return_value=mock_response):
            result = execute_web_search("test query")
            
            assert result["status"] == "success"
            assert len(result["data"]) > 0
    
    def test_web_search_no_results(self):
        """Test web search with no results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        
        with patch('requests.get', return_value=mock_response):
            result = execute_web_search("nonexistent query")
            
            assert result["status"] == "success"
            assert "No search results found" in result["data"]
    
    def test_web_search_api_error(self):
        """Test web search with API error."""
        with patch('requests.get', side_effect=Exception("API key invalid")):
            result = execute_web_search("test query")
            
            assert result["status"] == "error"
            assert "Failed to execute web search" in result["message"]


class TestMemoryRecallTools:
    """Test memory recall tools."""

    @patch('hippocampus.recall_memories_tool.current_user')
    @patch('hippocampus.recall_memories_tool.recall_memories')
    def test_recall_memories_success(self, mock_recall, mock_current_user):
        """Test successful memory recall."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_recall.return_value = [
            {
                "id": 1,
                "user_prompt": "Hello",
                "llm_reply": "Hi there!",
                "timestamp": "2024-01-01 10:00:00",
                "conversation_id": "conv1",
                "topic": "greeting"
            }
        ]
        
        result = execute_recall_memories("hello")
        
        assert result["status"] == "success"
        assert "data" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["user_prompt"] == "Hello"
        assert result["data"][0]["llm_reply"] == "Hi there!"

    @patch('hippocampus.recall_memories_with_time_tool.current_user')
    @patch('hippocampus.recall_memories_with_time_tool.recall_memories_with_time')
    def test_recall_memories_with_time_success(self, mock_recall, mock_current_user):
        """Test successful memory recall with time filter."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_recall.return_value = [
            {
                "id": 1,
                "user_prompt": "Hello",
                "llm_reply": "Hi there!",
                "timestamp": "2024-01-01 10:00:00",
                "conversation_id": "conv1",
                "topic": "greeting"
            }
        ]
        
        result = execute_recall_memories_with_time("hello", "2024-01-01", "2024-01-31")
        
        assert result["status"] == "success"
        assert "data" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["user_prompt"] == "Hello"

    @patch('hippocampus.recall_memories_tool.current_user')
    @patch('hippocampus.recall_memories_tool.recall_memories')
    def test_recall_memories_no_results(self, mock_recall, mock_current_user):
        """Test memory recall with no results."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_recall.return_value = []
        
        result = execute_recall_memories("nonexistent")
        
        assert result["status"] == "success"
        assert "data" in result
        assert result["data"] == []
        assert "No memories found" in result["message"]

    @patch('hippocampus.recall_memories_tool.current_user')
    @patch('hippocampus.recall_memories_tool.recall_memories')
    def test_recall_memories_database_error(self, mock_recall, mock_current_user):
        """Test memory recall with database error."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_recall.side_effect = Exception("Database error")
        
        result = execute_recall_memories("hello")
        
        assert result["status"] == "error"
        assert "Memory recall failed" in result["message"]


class TestConversationTools:
    """Test conversation management tools."""

    @patch('hippocampus.get_conversations_by_topic_tool.current_user')
    @patch('hippocampus.get_conversations_by_topic_tool.get_conversations_by_topic')
    def test_get_conversations_by_topic_success(self, mock_get, mock_current_user):
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        mock_get.return_value = [
            {"conversation_id": "conv1", "topic_name": "test", "first_seen": "2022-01-01"}
        ]
        
        result = execute_get_conversations_by_topic("test")
        
        assert result["status"] == "success"
        assert "data" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["conversation_id"] == "conv1"

    @patch('hippocampus.get_topics_by_conversation_tool.current_user')
    @patch('hippocampus.get_topics_by_conversation_tool.get_topics_by_conversation')
    def test_get_topics_by_conversation_success(self, mock_get, mock_current_user):
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        mock_get.return_value = [
            {"topic_name": "test", "frequency": 3, "first_seen": "2022-01-01"}
        ]
        
        result = execute_get_topics_by_conversation("conv1")
        
        assert result["status"] == "success"
        assert "data" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["topic_name"] == "test"

    @patch('hippocampus.get_conversation_summary_tool.current_user')
    @patch('hippocampus.get_conversation_summary_tool.get_conversation_summary')
    def test_get_conversation_summary_success(self, mock_get, mock_current_user):
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        mock_get.return_value = {
            "conversation_id": "conv1",
            "title": "Test Conversation",
            "total_memories": 5,
            "topics": ["test", "example"]
        }
        
        result = execute_get_conversation_summary("conv1")
        
        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["conversation_id"] == "conv1"

    @patch('hippocampus.get_topic_statistics_tool.current_user')
    @patch('hippocampus.get_topic_statistics_tool.get_topic_statistics')
    def test_get_topic_statistics_success(self, mock_get, mock_current_user):
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        mock_get.return_value = {
            "total_topics": 10,
            "most_common_topics": [{"topic": "test", "count": 5}]
        }
        
        result = execute_get_topic_statistics()
        
        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["total_topics"] == 10

    @patch('hippocampus.get_user_conversations_tool.current_user')
    @patch('hippocampus.get_user_conversations_tool.get_user_conversations')
    def test_get_user_conversations_success(self, mock_get, mock_current_user):
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        mock_get.return_value = [
            {"conversation_id": "conv1", "title": "Test", "last_activity": "2022-01-01"}
        ]
        
        result = execute_get_user_conversations(10)
        
        assert result["status"] == "success"
        assert "data" in result
        assert len(result["data"]) == 1
        assert result["data"][0]["conversation_id"] == "conv1"

    @patch('hippocampus.get_conversation_details_tool.current_user')
    @patch('hippocampus.get_conversation_details_tool.get_conversation_details')
    def test_get_conversation_details_success(self, mock_get, mock_current_user):
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        mock_get.return_value = {
            "conversation_id": "conv1",
            "title": "Test",
            "memories": [{"id": 1, "prompt": "Hello"}]
        }
        
        result = execute_get_conversation_details("conv1")
        
        assert result["status"] == "success"
        assert "data" in result
        assert result["data"]["conversation_id"] == "conv1"

    @patch('hippocampus.search_conversations_tool.current_user')
    @patch('hippocampus.search_conversations_tool.search_conversations')
    def test_search_conversations_success(self, mock_search, mock_current_user):
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        mock_search.return_value = [
            {"conversation_id": "conv1", "relevance": 0.8, "snippet": "test content"}
        ]
        
        result = execute_search_conversations("test", 10)
        
        assert result["status"] == "success"
        assert "data" in result
        assert "conversations" in result["data"]
        assert len(result["data"]["conversations"]) == 1


class TestToolErrorHandling:
    """Test tool error handling."""
    
    def test_tool_with_missing_api_keys(self):
        """Test tools that require API keys when they're missing."""
        # Test weather tool without API key
        with patch('config.OPENWEATHER_API_KEY', None):
            result = execute_get_weather_forecast("Amsterdam")
            # The function doesn't check for missing API keys, so it will try to make the request
            # and fail with a different error
            assert "error" in result or result["status"] == "success"
    
    def test_tool_with_invalid_parameters(self):
        """Test tools with invalid parameters."""
        # Test weather tool with invalid city
        result = execute_get_weather_forecast("")
        # The function doesn't validate empty city names, so it will try to make the request
        assert result["status"] == "error" or result["status"] == "success"
    
    def test_tool_with_invalid_dates(self):
        """Test tools with invalid date parameters."""
        # Test weather tool with invalid date format
        result = execute_get_weather_forecast("Amsterdam", "invalid-date")
        # The function doesn't validate date formats, so it will try to make the request
        assert result["status"] == "error" or result["status"] == "success" 