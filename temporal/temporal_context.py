"""
Temporal Context Processor

Handles time-based context awareness, interaction history,
and temporal pattern analysis for voice interactions.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class TemporalContext:
    def __init__(self, context_window_hours: int = 24):
        self.interaction_history: List[Dict[str, Any]] = []
        self.context_window = timedelta(hours=context_window_hours)
        logger.debug(f"TemporalContext initialized with {context_window_hours}h context window")
        
    def add_interaction(self, text: str, timestamp: Optional[datetime] = None) -> None:
        """Add new interaction to temporal context"""
        if timestamp is None:
            timestamp = datetime.now()
            
        interaction = {
            "text": text,
            "timestamp": timestamp,
            "time_of_day": timestamp.hour,
            "day_of_week": timestamp.weekday(),
            "weekday": timestamp.strftime("%A")
        }
        
        self.interaction_history.append(interaction)
        logger.debug(f"Added interaction: {text[:50]}... at {timestamp}")
        
    def get_current_context(self) -> Dict[str, Any]:
        """Get current temporal context"""
        now = datetime.now()
        return {
            "current_time": now,
            "time_of_day": now.hour,
            "day_of_week": now.weekday(),
            "weekday": now.strftime("%A"),
            "recent_interactions": self.get_recent_interactions(),
            "temporal_patterns": self.analyze_temporal_patterns()
        }
        
    def get_relevant_context(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get context relevant to current query"""
        # Filter interactions based on temporal relevance
        relevant = []
        for interaction in self.interaction_history[-10:]:  # Last 10 interactions
            if self.is_temporally_relevant(interaction, query):
                relevant.append(interaction)
        return relevant
        
    def get_recent_interactions(self, count: int = 5) -> List[Dict[str, Any]]:
        """Get the most recent interactions"""
        return self.interaction_history[-count:] if self.interaction_history else []
        
    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in interactions"""
        if not self.interaction_history:
            return {}
            
        # Analyze time-of-day patterns
        hour_counts = {}
        for interaction in self.interaction_history:
            hour = interaction["time_of_day"]
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
            
        # Calculate average daily interactions
        if len(self.interaction_history) > 1:
            first_interaction = self.interaction_history[0]["timestamp"]
            days_since_first = (datetime.now() - first_interaction).days
            avg_daily = len(self.interaction_history) / max(1, days_since_first)
        else:
            avg_daily = 0
            
        return {
            "peak_hours": sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            "total_interactions": len(self.interaction_history),
            "average_daily_interactions": avg_daily,
            "most_active_day": self.get_most_active_day()
        }
        
    def get_most_active_day(self) -> Optional[str]:
        """Get the most active day of the week"""
        if not self.interaction_history:
            return None
            
        day_counts = {}
        for interaction in self.interaction_history:
            day = interaction["weekday"]
            day_counts[day] = day_counts.get(day, 0) + 1
            
        if day_counts:
            return max(day_counts.items(), key=lambda x: x[1])[0]
        return None
        
    def is_temporally_relevant(self, interaction: Dict[str, Any], query: Optional[str] = None) -> bool:
        """Check if interaction is temporally relevant to current query"""
        # For now, consider recent interactions relevant
        # This can be enhanced with semantic similarity later
        return True
        
    def clean_old_interactions(self) -> None:
        """Remove interactions older than context window"""
        cutoff_time = datetime.now() - self.context_window
        original_count = len(self.interaction_history)
        
        self.interaction_history = [
            interaction for interaction in self.interaction_history
            if interaction["timestamp"] > cutoff_time
        ]
        
        removed_count = original_count - len(self.interaction_history)
        if removed_count > 0:
            logger.debug(f"Cleaned {removed_count} old interactions from temporal context")
            
    def get_interaction_summary(self) -> Dict[str, Any]:
        """Get a summary of recent interactions"""
        if not self.interaction_history:
            return {"message": "No interactions recorded"}
            
        recent = self.interaction_history[-5:]  # Last 5 interactions
        return {
            "total_interactions": len(self.interaction_history),
            "recent_interactions": [
                {
                    "text": interaction["text"][:100] + "..." if len(interaction["text"]) > 100 else interaction["text"],
                    "time": interaction["timestamp"].strftime("%H:%M"),
                    "day": interaction["weekday"]
                }
                for interaction in recent
            ],
            "patterns": self.analyze_temporal_patterns()
        } 