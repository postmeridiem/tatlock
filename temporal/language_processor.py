"""
Language Processor

Handles temporal reference resolution, intent extraction,
and language understanding for voice interactions.
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class LanguageProcessor:
    def __init__(self):
        self.temporal_keywords = {
            "now": "current_time",
            "today": "current_date", 
            "yesterday": "previous_date",
            "tomorrow": "next_date",
            "morning": "time_period",
            "afternoon": "time_period",
            "evening": "time_period",
            "night": "time_period",
            "tonight": "time_period",
            "this week": "time_period",
            "next week": "time_period",
            "last week": "time_period"
        }
        
        self.urgency_words = ["now", "immediately", "urgent", "asap", "quickly", "fast"]
        self.weather_keywords = ["weather", "temperature", "forecast", "rain", "sunny", "cloudy"]
        self.time_keywords = ["time", "clock", "schedule", "appointment", "meeting"]
        
        logger.info("LanguageProcessor initialized")
        
    def process_with_context(self, text: str, context: Dict[str, Any]) -> str:
        """Process text with temporal context"""
        # Replace temporal references
        processed_text = self.resolve_temporal_references(text, context)
        
        # Add context hints if temporal references found
        if self.has_temporal_references(text):
            time_hint = f"[Temporal Context: {context.get('time_of_day', 'unknown')}:00]"
            processed_text = f"{time_hint} {processed_text}"
            
        logger.debug(f"Processed text: '{text}' -> '{processed_text}'")
        return processed_text
        
    def extract_intent(self, text: str) -> Dict[str, Any]:
        """Extract intent and temporal information from text"""
        intent = {
            "action": None,
            "temporal_references": [],
            "entities": [],
            "urgency": "normal",
            "categories": []
        }
        
        text_lower = text.lower()
        
        # Detect temporal references
        for keyword, ref_type in self.temporal_keywords.items():
            if keyword.lower() in text_lower:
                intent["temporal_references"].append({
                    "keyword": keyword,
                    "type": ref_type
                })
                
        # Detect urgency
        if any(word in text_lower for word in self.urgency_words):
            intent["urgency"] = "high"
            
        # Detect categories
        if any(word in text_lower for word in self.weather_keywords):
            intent["categories"].append("weather")
            
        if any(word in text_lower for word in self.time_keywords):
            intent["categories"].append("time")
            
        # Detect basic actions
        action_patterns = {
            "query": r"\b(what|how|when|where|why|tell me|show me)\b",
            "command": r"\b(turn|switch|set|start|stop|open|close)\b",
            "reminder": r"\b(remind|remember|note|schedule)\b"
        }
        
        for action_type, pattern in action_patterns.items():
            if re.search(pattern, text_lower):
                intent["action"] = action_type
                break
                
        logger.debug(f"Extracted intent: {intent}")
        return intent
        
    def resolve_temporal_references(self, text: str, context: Dict[str, Any]) -> str:
        """Resolve temporal references in text"""
        now = context.get("current_time", datetime.now())
        
        # Replace "now" with current time
        text = re.sub(r'\bnow\b', f"at {now.strftime('%H:%M')}", text, flags=re.IGNORECASE)
        
        # Replace "today" with current date
        text = re.sub(r'\btoday\b', now.strftime('%Y-%m-%d'), text, flags=re.IGNORECASE)
        
        # Replace "yesterday" with previous date
        yesterday = now - timedelta(days=1)
        text = re.sub(r'\byesterday\b', yesterday.strftime('%Y-%m-%d'), text, flags=re.IGNORECASE)
        
        # Replace "tomorrow" with next date
        tomorrow = now + timedelta(days=1)
        text = re.sub(r'\btomorrow\b', tomorrow.strftime('%Y-%m-%d'), text, flags=re.IGNORECASE)
        
        # Replace time periods
        time_periods = {
            r'\bmorning\b': f"between 06:00 and 12:00 on {now.strftime('%Y-%m-%d')}",
            r'\bafternoon\b': f"between 12:00 and 18:00 on {now.strftime('%Y-%m-%d')}",
            r'\bevening\b': f"between 18:00 and 22:00 on {now.strftime('%Y-%m-%d')}",
            r'\bnight\b': f"between 22:00 and 06:00 on {now.strftime('%Y-%m-%d')}",
            r'\btonight\b': f"between 18:00 and 06:00 on {now.strftime('%Y-%m-%d')}"
        }
        
        for pattern, replacement in time_periods.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            
        return text
        
    def has_temporal_references(self, text: str) -> bool:
        """Check if text contains temporal references"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.temporal_keywords.keys())
        
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        entities = []
        
        # Extract time patterns
        time_patterns = [
            (r'\b\d{1,2}:\d{2}\b', 'time'),
            (r'\b\d{1,2} (am|pm)\b', 'time'),
            (r'\b\d{4}-\d{2}-\d{2}\b', 'date'),
            (r'\b\d{1,2}/\d{1,2}/\d{4}\b', 'date')
        ]
        
        for pattern, entity_type in time_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    "text": match.group(),
                    "type": entity_type,
                    "start": match.start(),
                    "end": match.end()
                })
                
        return entities 