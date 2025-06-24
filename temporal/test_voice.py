#!/usr/bin/env python3
"""
Test voice processing functionality
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from temporal.voice_service import VoiceService
from temporal.temporal_context import TemporalContext
from temporal.language_processor import LanguageProcessor


async def test_basic_functionality():
    """Test basic voice service functionality"""
    print("Testing basic voice service functionality...")
    
    # Create voice service
    service = VoiceService()
    
    # Test initialization
    result = await service.initialize()
    print(f"Initialization result: {result}")
    
    # Test text processing
    response = await service.process_voice_command("Hello, how are you?")
    print(f"Text processing response: {response}")
    
    # Test temporal context
    summary = service.get_temporal_summary()
    print(f"Temporal summary: {summary}")
    
    print("✅ Basic functionality test completed")


async def test_language_processing():
    """Test language processing functionality"""
    print("\nTesting language processing...")
    
    processor = LanguageProcessor()
    
    # Test intent extraction
    intent = processor.extract_intent("What's the weather like today?")
    print(f"Weather intent: {intent}")
    
    intent = processor.extract_intent("What time is it?")
    print(f"Time intent: {intent}")
    
    intent = processor.extract_intent("This is urgent!")
    print(f"Urgent intent: {intent}")
    
    print("✅ Language processing test completed")


async def test_temporal_context():
    """Test temporal context functionality"""
    print("\nTesting temporal context...")
    
    context = TemporalContext()
    
    # Add some interactions
    context.add_interaction("Hello")
    context.add_interaction("How are you?")
    context.add_interaction("What's the weather?")
    
    # Get current context
    current_context = context.get_current_context()
    print(f"Current context: {current_context}")
    
    # Get summary
    summary = context.get_interaction_summary()
    print(f"Interaction summary: {summary}")
    
    print("✅ Temporal context test completed")


async def test_voice_service_integration():
    """Test voice service integration"""
    print("\nTesting voice service integration...")
    
    service = VoiceService()
    
    # Test without initialization (no voice processing)
    result = await service.initialize()
    print(f"Service initialization: {result}")
    
    # Test text command processing
    response = await service.process_voice_command("Tell me about the weather")
    print(f"Command response: {response}")
    
    # Test cortex integration
    cortex_response = await service.send_to_cortex("Weather query", {
        "urgency": "normal",
        "categories": ["weather"]
    })
    print(f"Cortex response: {cortex_response}")
    
    print("✅ Voice service integration test completed")


async def main():
    """Main test function"""
    print("🎤 Voice Processing Test Suite")
    print("=" * 50)
    
    try:
        await test_basic_functionality()
        await test_language_processing()
        await test_temporal_context()
        await test_voice_service_integration()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print("\nNote: Voice processing (audio transcription) is not available in this version.")
        print("The service operates in text-only mode.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    print("Voice Processing Test Suite")
    print("=" * 50)
    print("This test suite verifies the voice processing functionality.")
    print("Note: Voice processing (audio transcription) is not available.")
    print("The service operates in text-only mode.")
    print()
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 