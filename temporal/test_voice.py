"""
Test script for Temporal Voice components

Tests the basic functionality without requiring external dependencies.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from temporal.temporal_context import TemporalContext
from temporal.language_processor import LanguageProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_temporal_context():
    """Test temporal context functionality"""
    print("=== Testing Temporal Context ===")
    
    context = TemporalContext(context_window_hours=24)
    
    # Add some test interactions
    context.add_interaction("What's the weather like today?")
    context.add_interaction("Set a reminder for tomorrow morning")
    context.add_interaction("What time is it now?")
    
    # Get current context
    current_context = context.get_current_context()
    print(f"Current context: {current_context}")
    
    # Get summary
    summary = context.get_interaction_summary()
    print(f"Interaction summary: {summary}")
    
    return context

def test_language_processor():
    """Test language processor functionality"""
    print("\n=== Testing Language Processor ===")
    
    processor = LanguageProcessor()
    
    # Test temporal reference resolution
    test_texts = [
        "What's the weather like today?",
        "Set a reminder for tomorrow morning",
        "What time is it now?",
        "Tell me about yesterday's meeting"
    ]
    
    context = {"current_time": datetime.now()}
    
    for text in test_texts:
        processed = processor.process_with_context(text, context)
        intent = processor.extract_intent(text)
        print(f"Original: {text}")
        print(f"Processed: {processed}")
        print(f"Intent: {intent}")
        print()

async def test_voice_service_basic():
    """Test basic voice service functionality without external dependencies"""
    print("\n=== Testing Voice Service (Basic) ===")
    
    from temporal.voice_service import VoiceService
    
    voice_service = VoiceService()
    
    # Test without initialization (no Whisper)
    test_text = "What's the weather like today?"
    response = await voice_service.process_voice_command(test_text)
    
    print(f"Voice command response: {response}")
    
    # Test temporal summary
    summary = voice_service.get_temporal_summary()
    print(f"Temporal summary: {summary}")

async def main():
    """Run all tests"""
    print("🧠 Testing Temporal Voice Components\n")
    
    # Test temporal context
    context = await test_temporal_context()
    
    # Test language processor
    test_language_processor()
    
    # Test voice service (basic)
    await test_voice_service_basic()
    
    print("\n✅ All basic tests completed!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install openai-whisper websockets")
    print("2. Test with real audio input")
    print("3. Integrate with existing Tatlock agent system")

if __name__ == "__main__":
    asyncio.run(main()) 