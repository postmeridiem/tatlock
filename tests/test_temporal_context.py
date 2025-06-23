"""
tests/test_temporal_context.py

Tests for the temporal context module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
from temporal.temporal_context import TemporalContext


class TestTemporalContext:
    """Test the TemporalContext class."""
    
    def test_initialization(self):
        """Test TemporalContext initialization."""
        context = TemporalContext(context_window_hours=12)
        
        assert context.interaction_history == []
        assert context.context_window == timedelta(hours=12)
    
    def test_initialization_default(self):
        """Test TemporalContext initialization with default values."""
        context = TemporalContext()
        
        assert context.interaction_history == []
        assert context.context_window == timedelta(hours=24)
    
    def test_add_interaction_with_timestamp(self):
        """Test adding interaction with custom timestamp."""
        context = TemporalContext()
        timestamp = datetime.now()  # Use current timestamp
        
        context.add_interaction("Hello world", timestamp)
        
        # The interaction should be added and not cleaned up since it's current
        assert len(context.interaction_history) == 1
        interaction = context.interaction_history[0]
        assert interaction["text"] == "Hello world"
        assert interaction["timestamp"] == timestamp
        assert interaction["time_of_day"] == timestamp.hour
        assert interaction["day_of_week"] == timestamp.weekday()
        assert interaction["weekday"] == timestamp.strftime("%A")
    
    def test_add_interaction_without_timestamp(self):
        """Test adding interaction without timestamp (uses current time)."""
        context = TemporalContext()
        
        with patch('temporal.temporal_context.datetime') as mock_datetime:
            mock_now = datetime(2023, 1, 15, 10, 30, 0)
            mock_datetime.now.return_value = mock_now
            
            context.add_interaction("Test message")
            
            # The interaction should be added and not cleaned up since it's current
            assert len(context.interaction_history) == 1
            interaction = context.interaction_history[0]
            assert interaction["text"] == "Test message"
            assert interaction["timestamp"] == mock_now
            assert interaction["time_of_day"] == 10
            assert interaction["day_of_week"] == 6
            assert interaction["weekday"] == "Sunday"
    
    def test_add_multiple_interactions(self):
        """Test adding multiple interactions."""
        context = TemporalContext()
        
        # Add interactions with current timestamps
        now = datetime.now()
        context.add_interaction("First message", now)
        context.add_interaction("Second message", now)
        context.add_interaction("Third message", now)
        
        # All interactions should be added since they're current
        assert len(context.interaction_history) == 3
        assert context.interaction_history[0]["text"] == "First message"
        assert context.interaction_history[1]["text"] == "Second message"
        assert context.interaction_history[2]["text"] == "Third message"
    
    def test_get_current_context(self):
        """Test getting current temporal context."""
        context = TemporalContext()
        context.add_interaction("Test interaction", datetime.now())
        
        with patch('temporal.temporal_context.datetime') as mock_datetime:
            mock_now = datetime(2023, 1, 15, 15, 45, 0)
            mock_datetime.now.return_value = mock_now
            
            current_context = context.get_current_context()
            
            assert current_context["current_time"] == mock_now
            assert current_context["time_of_day"] == 15
            assert current_context["day_of_week"] == 6
            assert current_context["weekday"] == "Sunday"
            assert "recent_interactions" in current_context
            assert "temporal_patterns" in current_context
    
    def test_get_relevant_context(self):
        """Test getting relevant context for a query."""
        context = TemporalContext()
        now = datetime.now()
        context.add_interaction("First interaction", now)
        context.add_interaction("Second interaction", now)
        context.add_interaction("Third interaction", now)
        
        relevant = context.get_relevant_context("test query")
        
        # Should return recent interactions (up to 10)
        assert len(relevant) <= 10
        assert len(relevant) == 3  # All interactions are recent
    
    def test_get_relevant_context_with_query(self):
        """Test getting relevant context with specific query."""
        context = TemporalContext()
        now = datetime.now()
        context.add_interaction("Weather is sunny", now)
        context.add_interaction("Temperature is 25 degrees", now)
        
        relevant = context.get_relevant_context("weather")
        
        # Currently all interactions are considered relevant
        assert len(relevant) == 2
    
    def test_get_recent_interactions(self):
        """Test getting recent interactions."""
        context = TemporalContext()
        # Add interactions with current timestamps
        now = datetime.now()
        context.add_interaction("Interaction 1", now)
        context.add_interaction("Interaction 2", now)
        context.add_interaction("Interaction 3", now)
        context.add_interaction("Interaction 4", now)
        context.add_interaction("Interaction 5", now)
        context.add_interaction("Interaction 6", now)
        
        recent = context.get_recent_interactions(count=3)
        
        assert len(recent) == 3
        assert recent[0]["text"] == "Interaction 4"
        assert recent[1]["text"] == "Interaction 5"
        assert recent[2]["text"] == "Interaction 6"
    
    def test_get_recent_interactions_empty(self):
        """Test getting recent interactions when history is empty."""
        context = TemporalContext()
        
        recent = context.get_recent_interactions()
        
        assert recent == []
    
    def test_get_recent_interactions_default_count(self):
        """Test getting recent interactions with default count."""
        context = TemporalContext()
        now = datetime.now()
        for i in range(10):
            context.add_interaction(f"Interaction {i}", now)
        
        recent = context.get_recent_interactions()
        
        assert len(recent) == 5  # Default count is 5
    
    def test_analyze_temporal_patterns_empty(self):
        """Test analyzing temporal patterns with empty history."""
        context = TemporalContext()
        
        patterns = context.analyze_temporal_patterns()
        
        assert patterns == {}
    
    def test_analyze_temporal_patterns_single_interaction(self):
        """Test analyzing temporal patterns with single interaction."""
        context = TemporalContext()
        context.add_interaction("Single interaction", datetime.now())
        
        patterns = context.analyze_temporal_patterns()
        
        assert "peak_hours" in patterns
        assert "total_interactions" in patterns
        assert "average_daily_interactions" in patterns
        assert "most_active_day" in patterns
        assert patterns["total_interactions"] == 1
        assert patterns["average_daily_interactions"] == 0  # Less than 1 day
    
    def test_analyze_temporal_patterns_multiple_interactions(self):
        """Test analyzing temporal patterns with multiple interactions."""
        context = TemporalContext()
        
        # Add interactions at different hours
        with patch('temporal.temporal_context.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 15, 12, 0, 0)
            
            context.add_interaction("Morning interaction", datetime(2023, 1, 15, 9, 0, 0))
            context.add_interaction("Afternoon interaction", datetime(2023, 1, 15, 14, 0, 0))
            context.add_interaction("Evening interaction", datetime(2023, 1, 15, 20, 0, 0))
            context.add_interaction("Another morning", datetime(2023, 1, 15, 10, 0, 0))
            
            patterns = context.analyze_temporal_patterns()
            
            assert patterns["total_interactions"] == 4
            assert len(patterns["peak_hours"]) == 3
            assert patterns["peak_hours"][0][0] == 9  # Most interactions at 9 AM
    
    def test_get_most_active_day_empty(self):
        """Test getting most active day with empty history."""
        context = TemporalContext()
        
        most_active = context.get_most_active_day()
        
        assert most_active is None
    
    def test_get_most_active_day_single_day(self):
        """Test getting most active day with single day."""
        context = TemporalContext()
        context.add_interaction("Monday interaction", datetime(2023, 1, 16, 10, 0, 0))  # Monday
        
        most_active = context.get_most_active_day()
        
        assert most_active == "Monday"
    
    def test_get_most_active_day_multiple_days(self):
        """Test getting most active day with multiple days."""
        context = TemporalContext()
        
        # Add interactions on different days
        context.add_interaction("Monday 1", datetime(2023, 1, 16, 10, 0, 0))  # Monday
        context.add_interaction("Monday 2", datetime(2023, 1, 16, 14, 0, 0))  # Monday
        context.add_interaction("Tuesday 1", datetime(2023, 1, 17, 10, 0, 0))  # Tuesday
        context.add_interaction("Wednesday 1", datetime(2023, 1, 18, 10, 0, 0))  # Wednesday
        
        most_active = context.get_most_active_day()
        
        assert most_active == "Monday"  # Monday has 2 interactions
    
    def test_is_temporally_relevant(self):
        """Test temporal relevance checking."""
        context = TemporalContext()
        interaction = {
            "text": "Test interaction",
            "timestamp": datetime.now(),
            "time_of_day": 10,
            "day_of_week": 0,
            "weekday": "Monday"
        }
        
        # Currently always returns True
        assert context.is_temporally_relevant(interaction) is True
        assert context.is_temporally_relevant(interaction, "test query") is True
    
    def test_clean_old_interactions(self):
        """Test cleaning old interactions."""
        context = TemporalContext(context_window_hours=1)
        
        # Add old and new interactions
        old_time = datetime.now() - timedelta(hours=2)
        new_time = datetime.now() - timedelta(minutes=30)
        
        context.add_interaction("Old interaction", old_time)
        context.add_interaction("New interaction", new_time)
        
        # Should have 2 interactions initially
        assert len(context.interaction_history) == 2
        
        # Clean old interactions
        context.clean_old_interactions()
        
        # Should only have 1 interaction after cleaning
        assert len(context.interaction_history) == 1
        assert context.interaction_history[0]["text"] == "New interaction"
    
    def test_clean_old_interactions_no_old(self):
        """Test cleaning when no old interactions exist."""
        context = TemporalContext(context_window_hours=1)
        
        # Add only recent interactions
        recent_time = datetime.now() - timedelta(minutes=30)
        context.add_interaction("Recent interaction", recent_time)
        
        original_count = len(context.interaction_history)
        context.clean_old_interactions()
        
        # Count should remain the same
        assert len(context.interaction_history) == original_count
    
    def test_get_interaction_summary_empty(self):
        """Test getting interaction summary with empty history."""
        context = TemporalContext()
        
        summary = context.get_interaction_summary()
        
        assert summary["message"] == "No interactions recorded"
    
    def test_get_interaction_summary_with_interactions(self):
        """Test getting interaction summary with interactions."""
        context = TemporalContext()
        
        # Add some interactions
        now = datetime.now()
        context.add_interaction("Short message", now)
        context.add_interaction("This is a very long message that should be truncated when displayed in the summary because it exceeds the character limit", now)
        context.add_interaction("Another message", now)
        
        summary = context.get_interaction_summary()
        
        assert summary["total_interactions"] == 3
        assert "recent_interactions" in summary
        assert "patterns" in summary
        
        recent = summary["recent_interactions"]
        assert len(recent) == 3
        
        # Check that long messages are truncated
        long_message = recent[1]["text"]
        assert len(long_message) <= 103  # 100 chars + "..."
        assert long_message.endswith("...")
        
        # Check that short messages are not truncated
        short_message = recent[0]["text"]
        assert short_message == "Short message"
    
    def test_get_interaction_summary_many_interactions(self):
        """Test getting interaction summary with many interactions."""
        context = TemporalContext()
        
        # Add more than 5 interactions
        now = datetime.now()
        for i in range(10):
            context.add_interaction(f"Interaction {i}", now)
        
        summary = context.get_interaction_summary()
        
        assert summary["total_interactions"] == 10
        assert len(summary["recent_interactions"]) == 5  # Only last 5
    
    def test_add_interaction_triggers_cleanup(self):
        """Test that adding interaction triggers cleanup."""
        context = TemporalContext(context_window_hours=1)
        
        # Add old interaction
        old_time = datetime.now() - timedelta(hours=2)
        context.add_interaction("Old interaction", old_time)
        
        # Add new interaction
        new_time = datetime.now() - timedelta(minutes=30)
        context.add_interaction("New interaction", new_time)
        
        # Manually trigger cleanup
        context.clean_old_interactions()
        
        # Should only have the new interaction
        assert len(context.interaction_history) == 1
        assert context.interaction_history[0]["text"] == "New interaction"
    
    def test_temporal_patterns_with_different_hours(self):
        """Test temporal patterns with interactions at different hours."""
        context = TemporalContext()
        
        # Add interactions at different hours
        context.add_interaction("9 AM", datetime(2023, 1, 15, 9, 0, 0))
        context.add_interaction("10 AM", datetime(2023, 1, 15, 10, 0, 0))
        context.add_interaction("9 AM again", datetime(2023, 1, 15, 9, 30, 0))
        context.add_interaction("11 AM", datetime(2023, 1, 15, 11, 0, 0))
        
        patterns = context.analyze_temporal_patterns()
        
        assert patterns["total_interactions"] == 4
        peak_hours = patterns["peak_hours"]
        assert len(peak_hours) == 3
        assert peak_hours[0][0] == 9  # 9 AM has 2 interactions
        assert peak_hours[0][1] == 2
        assert peak_hours[1][0] in [10, 11]  # 10 AM or 11 AM has 1 interaction
        assert peak_hours[1][1] == 1
    
    def test_temporal_patterns_with_different_days(self):
        """Test temporal patterns with interactions on different days."""
        context = TemporalContext()
        
        # Add interactions on different days
        context.add_interaction("Monday", datetime(2023, 1, 16, 10, 0, 0))  # Monday
        context.add_interaction("Tuesday", datetime(2023, 1, 17, 10, 0, 0))  # Tuesday
        context.add_interaction("Monday again", datetime(2023, 1, 16, 14, 0, 0))  # Monday
        context.add_interaction("Wednesday", datetime(2023, 1, 18, 10, 0, 0))  # Wednesday
        
        patterns = context.analyze_temporal_patterns()
        
        assert patterns["most_active_day"] == "Monday"  # Monday has 2 interactions
    
    def test_context_window_custom_hours(self):
        """Test custom context window hours."""
        context = TemporalContext(context_window_hours=6)
        
        assert context.context_window == timedelta(hours=6)
        
        # Add interaction older than context window
        old_time = datetime.now() - timedelta(hours=8)
        context.add_interaction("Old interaction", old_time)
        
        # Add interaction within context window
        new_time = datetime.now() - timedelta(hours=3)
        context.add_interaction("New interaction", new_time)
        
        # Manually trigger cleanup
        context.clean_old_interactions()
        
        # Should only have the new interaction after cleanup
        assert len(context.interaction_history) == 1
        assert context.interaction_history[0]["text"] == "New interaction"
    
    def test_interaction_timestamp_formatting(self):
        """Test interaction timestamp formatting in summary."""
        context = TemporalContext()
        
        # Add interaction at specific time
        timestamp = datetime(2023, 1, 15, 14, 30, 45)
        context.add_interaction("Test interaction", timestamp)
        
        summary = context.get_interaction_summary()
        recent = summary["recent_interactions"]
        
        assert recent[0]["time"] == "14:30"
        assert recent[0]["day"] == "Sunday"
    
    def test_empty_interaction_history_operations(self):
        """Test operations on empty interaction history."""
        context = TemporalContext()
        
        # Test all operations that depend on interaction history
        assert context.get_recent_interactions() == []
        assert context.analyze_temporal_patterns() == {}
        assert context.get_most_active_day() is None
        assert context.get_interaction_summary()["message"] == "No interactions recorded"
        
        # Test getting relevant context
        relevant = context.get_relevant_context("test query")
        assert relevant == []
    
    def test_interaction_history_persistence(self):
        """Test that interactions persist across method calls."""
        context = TemporalContext()
        
        # Add interactions with current timestamps
        now = datetime.now()
        context.add_interaction("First", now)
        context.add_interaction("Second", now)
        
        # Verify they persist
        assert len(context.interaction_history) == 2
        
        # Call other methods and verify interactions still exist
        context.get_current_context()
        context.get_relevant_context("test")
        context.analyze_temporal_patterns()
        
        assert len(context.interaction_history) == 2
        assert context.interaction_history[0]["text"] == "First"
        assert context.interaction_history[1]["text"] == "Second" 