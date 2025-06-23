"""
tests/test_memory_tools.py

Tests for the new memory tools: memory_insights, memory_cleanup, and memory_export.
"""

import pytest
import sqlite3
import json
import csv
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from pathlib import Path
import os

from hippocampus.memory_insights_tool import execute_memory_insights
from hippocampus.memory_cleanup_tool import execute_memory_cleanup
from hippocampus.memory_export_tool import execute_memory_export


class TestMemoryInsightsTool:
    """Test the memory insights tool."""
    
    @patch('hippocampus.memory_insights_tool.current_user')
    @patch('hippocampus.memory_insights_tool.get_database_connection')
    def test_memory_insights_overview(self, mock_get_conn, mock_current_user):
        """Test memory insights overview analysis."""
        # Mock user
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock database results for overview
        mock_cursor.fetchone.side_effect = [
            (10,),  # total_conversations
            (100,), # total_memories
            (50,),  # total_topics
            ("2024-01-01", "2024-12-31")  # date_range
        ]
        
        result = execute_memory_insights("overview")
        
        assert result["status"] == "success"
        assert "data" in result
        data = result["data"]
        assert "total_conversations" in data
        assert "total_memories" in data
        assert "total_topics" in data
        assert "avg_memories_per_conversation" in data
        assert data["total_conversations"] == 10
        assert data["total_memories"] == 100
        assert data["total_topics"] == 50
        assert data["avg_memories_per_conversation"] == 10.0
        
        mock_conn.close.assert_called_once()
    
    @patch('hippocampus.memory_insights_tool.current_user')
    @patch('hippocampus.memory_insights_tool.get_database_connection')
    def test_memory_insights_patterns(self, mock_get_conn, mock_current_user):
        """Test memory insights pattern analysis."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock pattern analysis results
        mock_cursor.fetchall.side_effect = [
            [("1", 5), ("2", 3)],  # day_activity (day numbers, not names)
            [("14", 8), ("15", 6)],  # hour_activity
            [("conv1", 3), ("conv2", 2), ("conv3", 1)]  # conversation_lengths
        ]
        
        result = execute_memory_insights("patterns")
        
        assert result["status"] == "success"
        assert "data" in result
        data = result["data"]
        assert "most_active_days" in data
        assert "most_active_hours" in data
        assert "conversation_length_stats" in data
        
        mock_conn.close.assert_called_once()
    
    @patch('stem.security.current_user', None)
    def test_memory_insights_no_user(self):
        """Test memory insights with no authenticated user."""
        result = execute_memory_insights("overview")
        
        assert result["status"] == "error"
        assert "not authenticated" in result["message"]
    
    @patch('hippocampus.memory_insights_tool.current_user')
    @patch('hippocampus.memory_insights_tool.get_database_connection')
    def test_memory_insights_invalid_type(self, mock_get_conn, mock_current_user):
        """Test memory insights with invalid analysis type."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        result = execute_memory_insights("invalid_type")
        
        assert result["status"] == "error"
        assert "Unknown analysis type" in result["message"]

    @patch('hippocampus.memory_insights_tool.current_user')
    @patch('hippocampus.memory_insights_tool.get_database_connection')
    def test_memory_insights_topics(self, mock_get_conn, mock_current_user):
        """Test memory insights topics analysis."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock database results for topics
        mock_cursor.fetchall.side_effect = [
            [("weather", 12), ("music", 8)],  # top_topics
            [("weather", "2024-01-01", "2024-06-01", 12)],  # topic_evolution
            [("weather", 5), ("music", 3)]  # topics_by_conversation
        ]
        
        result = execute_memory_insights("topics")
        
        assert result["status"] == "success"
        assert "data" in result
        data = result["data"]
        assert "most_discussed_topics" in data
        assert "topic_evolution" in data
        assert "topics_by_conversation_frequency" in data
        assert data["most_discussed_topics"][0]["topic"] == "weather"
        assert data["most_discussed_topics"][0]["mentions"] == 12
        
        mock_conn.close.assert_called_once()


class TestMemoryCleanupTool:
    """Test the memory cleanup tool."""
    
    @patch('hippocampus.memory_cleanup_tool.current_user')
    @patch('hippocampus.memory_cleanup_tool.get_database_connection')
    def test_memory_cleanup_duplicates(self, mock_get_conn, mock_current_user):
        """Test memory cleanup duplicate detection."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock memories data
        mock_cursor.fetchall.return_value = [
            (1, "Hello", "Hi there", "2024-01-01", 1),
            (2, "Hello", "Hi there", "2024-01-02", 1),
            (3, "Different", "Response", "2024-01-03", 2)
        ]
        
        result = execute_memory_cleanup("duplicates", 0.8)
        
        assert result["status"] == "success"
        assert "data" in result
        data = result["data"]
        assert "duplicate_groups" in data
        assert "total_duplicate_groups" in data
        assert "total_duplicate_memories" in data
        
        mock_conn.close.assert_called_once()
    
    @patch('hippocampus.memory_cleanup_tool.current_user')
    @patch('hippocampus.memory_cleanup_tool.get_database_connection')
    def test_memory_cleanup_orphans(self, mock_get_conn, mock_current_user):
        """Test memory cleanup orphan detection."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock orphan detection results
        mock_cursor.fetchall.side_effect = [
            [(1, 999)],  # orphaned_memories
            [(1, 1)],    # orphaned_memory_topics
            [],          # orphaned_topic_links
            [],          # orphaned_conversation_topics
            []           # orphaned_conversation_topic_links
        ]
        
        result = execute_memory_cleanup("orphans")
        
        assert result["status"] == "success"
        assert "data" in result
        data = result["data"]
        assert "orphaned_memories" in data
        assert "total_orphaned_records" in data
        assert data["total_orphaned_records"] == 2
        
        mock_conn.close.assert_called_once()
    
    @patch('hippocampus.memory_cleanup_tool.current_user')
    @patch('hippocampus.memory_cleanup_tool.get_database_connection')
    def test_memory_cleanup_analysis(self, mock_get_conn, mock_current_user):
        """Test memory cleanup health analysis."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock health analysis results
        mock_cursor.fetchone.side_effect = [
            (100,),  # total_memories
            (10,),   # total_conversations
            (5,),    # total_topics
            (2,),    # null_prompts
            (1,),    # null_replies
            (0,),    # null_timestamps
            (0,),    # long_prompts
            (0,),    # long_replies
            (5,),    # untagged_memories
            (0,)     # empty_conversations
        ]
        
        result = execute_memory_cleanup("analysis")
        
        assert result["status"] == "success"
        assert "data" in result
        data = result["data"]
        assert "basic_stats" in data
        assert "data_quality_issues" in data
        assert "health_scores" in data
        assert data["health_scores"]["data_quality_score"] == 97.0
        assert data["health_scores"]["completeness_score"] == 95.0
        
        mock_conn.close.assert_called_once()
    
    @patch('stem.security.current_user', None)
    def test_memory_cleanup_no_user(self):
        """Test memory cleanup with no authenticated user."""
        result = execute_memory_cleanup("duplicates")
        
        assert result["status"] == "error"
        assert "not authenticated" in result["message"]
    
    @patch('hippocampus.memory_cleanup_tool.current_user')
    @patch('hippocampus.memory_cleanup_tool.get_database_connection')
    def test_memory_cleanup_invalid_type(self, mock_get_conn, mock_current_user):
        """Test memory cleanup with invalid cleanup type."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        result = execute_memory_cleanup("invalid_type")
        
        assert result["status"] == "error"
        assert "Unknown cleanup type" in result["message"]


class TestMemoryExportTool:
    """Test the memory export tool."""
    
    @patch('hippocampus.memory_export_tool.current_user')
    @patch('hippocampus.memory_export_tool.get_database_connection')
    def test_memory_export_json(self, mock_get_conn, mock_current_user):
        """Test memory export to JSON format."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock export data
        mock_cursor.fetchall.return_value = [
            (1, "Hello", "Hi there", "2024-01-01", 1)
        ]
        
        result = execute_memory_export("json")
        
        assert result["status"] == "success"
        assert "data" in result
        data = result["data"]
        assert "total_conversations" in data
        assert "total_standalone_memories" in data
        assert "file_path" in data
        assert data["total_conversations"] == 1
        assert data["total_standalone_memories"] == 1
        
        mock_conn.close.assert_called_once()
    
    @patch('hippocampus.memory_export_tool.current_user')
    @patch('hippocampus.memory_export_tool.get_database_connection')
    def test_memory_export_csv(self, mock_get_conn, mock_current_user):
        """Test memory export to CSV format."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock export data with correct number of columns
        mock_cursor.fetchall.return_value = [
            ("1", "Hello", "Hi there", "2024-01-01", "1", "Test Conv", "general")
        ]
        
        result = execute_memory_export("csv")
        
        assert result["status"] == "success"
        assert "data" in result
        data = result["data"]
        assert "total_memories" in data
        assert "file_path" in data
        assert data["total_memories"] == 1
        
        mock_conn.close.assert_called_once()
    
    @patch('hippocampus.memory_export_tool.current_user')
    @patch('hippocampus.memory_export_tool.get_database_connection')
    def test_memory_export_summary(self, mock_get_conn, mock_current_user):
        """Test memory export summary format."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock summary data
        mock_cursor.fetchone.side_effect = [
            (100,),  # total_memories
            (10,),   # total_conversations
            (5,)     # total_topics
        ]
        
        result = execute_memory_export("summary")
        
        assert result["status"] == "success"
        assert "data" in result
        data = result["data"]
        assert "total_memories" in data
        assert "total_conversations" in data
        assert "total_topics" in data
        assert data["total_memories"] == 100
        assert data["total_conversations"] == 10
        assert data["total_topics"] == 5
        
        mock_conn.close.assert_called_once()
    
    @patch('stem.security.current_user', None)
    def test_memory_export_no_user(self):
        """Test memory export with no authenticated user."""
        result = execute_memory_export("json")
        
        assert result["status"] == "error"
        assert "not authenticated" in result["message"]
    
    @patch('hippocampus.memory_export_tool.current_user')
    @patch('hippocampus.memory_export_tool.get_database_connection')
    def test_memory_export_invalid_type(self, mock_get_conn, mock_current_user):
        """Test memory export with invalid export type."""
        mock_user = MagicMock()
        mock_user.username = "testuser"
        mock_current_user.return_value = mock_user
        
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        result = execute_memory_export("invalid_type")
        
        assert result["status"] == "error"
        assert "Unknown export type" in result["message"]


class TestMemoryToolsIntegration:
    """Integration tests for memory tools with real database operations."""
    
    def test_memory_insights_day_name_conversion(self):
        """Test the day name conversion function."""
        from hippocampus.memory_insights_tool import _get_day_name
        
        assert _get_day_name(0) == "Sunday"
        assert _get_day_name(1) == "Monday"
        assert _get_day_name(6) == "Saturday"
        assert _get_day_name(7) == "Unknown"
        assert _get_day_name(-1) == "Unknown"
    
    def test_memory_export_date_filter(self):
        """Test the date filter building function."""
        from hippocampus.memory_export_tool import _build_date_filter
        
        # Test last_30_days
        filter_30 = _build_date_filter("last_30_days")
        assert "WHERE timestamp >=" in filter_30['memory_where']
        assert len(filter_30['memory_params']) == 1
        
        # Test last_7_days
        filter_7 = _build_date_filter("last_7_days")
        assert "WHERE timestamp >=" in filter_7['memory_where']
        assert len(filter_7['memory_params']) == 1
        
        # Test date range
        filter_range = _build_date_filter("2024-01-01:2024-12-31")
        assert "WHERE timestamp BETWEEN" in filter_range['memory_where']
        assert len(filter_range['memory_params']) == 2
        assert filter_range['memory_params'] == ["2024-01-01", "2024-12-31"]
        
        # Test single date
        filter_single = _build_date_filter("2024-01-01")
        assert "WHERE DATE(timestamp) = ?" in filter_single['memory_where']
        assert filter_single['memory_params'] == ["2024-01-01"]
        
        # Test no filter
        filter_none = _build_date_filter(None)
        assert filter_none['memory_where'] == ""
        assert filter_none['memory_params'] == [] 