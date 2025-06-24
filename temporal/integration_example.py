#!/usr/bin/env python3
"""
Integration example for Temporal Voice Service

This example demonstrates how to integrate the voice service
with the Tatlock system. Note that voice processing (audio transcription)
is not available in this version.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from temporal.voice_service import VoiceService


async def main():
    """Main integration example"""
    print("🎤 Temporal Voice Service Integration Example")
    print("=" * 60)
    
    # Initialize voice service
    voice_service = VoiceService()
    
    # Initialize (voice processing not available)
    whisper_available = await voice_service.initialize()
    if whisper_available:
        print("✅ Voice processing available")
    else:
        print("⚠️  Voice processing not available - using text-only mode")
    
    # Test text command processing
    print("\n📝 Testing text command processing...")
    
    commands = [
        "What's the weather like today?",
        "Set a reminder for tomorrow morning",
        "What time is it now?",
        "This is an urgent request!"
    ]
    
    for command in commands:
        print(f"\nCommand: {command}")
        response = await voice_service.process_voice_command(command)
        print(f"Response: {response}")
    
    # Test temporal context
    print("\n⏰ Testing temporal context...")
    summary = voice_service.get_temporal_summary()
    print(f"Temporal summary: {summary}")
    
    print("\n" + "=" * 60)
    print("✅ Integration example completed!")
    print("\nNote: Voice processing (audio transcription) is not available.")
    print("The service operates in text-only mode for text-based commands.")


async def server_example():
    """WebSocket server example"""
    print("🌐 WebSocket Server Example")
    print("=" * 40)
    
    voice_service = VoiceService()
    
    # Start WebSocket server
    await voice_service.start_websocket_server("localhost", 8765)
    
    print("WebSocket server started on localhost:8765")
    print("Note: Voice processing is not available.")
    print("Audio messages will return error responses.")
    print("Text messages will be processed normally.")
    
    try:
        # Keep server running
        await asyncio.sleep(30)
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        voice_service.stop_websocket_server()
        print("Server stopped.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        print("Starting WebSocket server...")
        asyncio.run(server_example())
    else:
        print("Running integration example...")
        asyncio.run(main()) 