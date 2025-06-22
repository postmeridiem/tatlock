"""
Integration Example: Temporal Voice with Tatlock

This example shows how to integrate the temporal voice system
with the existing Tatlock agent system.
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from temporal.voice_service import VoiceService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def integrate_with_tatlock():
    """Example integration with Tatlock agent system"""
    print("🧠 Temporal Voice Integration Example\n")
    
    # Initialize voice service
    voice_service = VoiceService(context_window_hours=24)
    
    # Initialize with Whisper (if available)
    whisper_available = await voice_service.initialize()
    if whisper_available:
        print("✅ Whisper model loaded successfully")
    else:
        print("⚠️  Whisper not available - using text-only mode")
    
    # Example voice commands
    test_commands = [
        "What's the weather like today?",
        "Set a reminder for tomorrow morning at 9 AM",
        "What time is it now?",
        "Tell me about yesterday's meeting",
        "Turn on the lights in the living room"
    ]
    
    print("\n📝 Processing voice commands:")
    print("=" * 50)
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. Processing: '{command}'")
        
        # Process through temporal voice system
        response = await voice_service.process_voice_command(command)
        
        # Extract key information
        intent = response.get("intent", {})
        processed_text = response.get("processed_text", "")
        agent_response = response.get("agent_response", "")
        
        print(f"   Intent: {intent.get('action', 'unknown')}")
        print(f"   Categories: {intent.get('categories', [])}")
        print(f"   Urgency: {intent.get('urgency', 'normal')}")
        print(f"   Processed: {processed_text}")
        print(f"   Agent Response: {agent_response}")
        
        # Simulate integration with Tatlock agent
        await simulate_tatlock_integration(command, intent, processed_text)
    
    # Show temporal context summary
    print("\n📊 Temporal Context Summary:")
    print("=" * 50)
    summary = voice_service.get_temporal_summary()
    print(f"Total Interactions: {summary.get('total_interactions', 0)}")
    print(f"Recent Interactions: {len(summary.get('recent_interactions', []))}")
    
    patterns = summary.get('patterns', {})
    if patterns:
        print(f"Peak Hours: {patterns.get('peak_hours', [])}")
        print(f"Most Active Day: {patterns.get('most_active_day', 'Unknown')}")
        print(f"Average Daily: {patterns.get('average_daily_interactions', 0):.1f}")

async def simulate_tatlock_integration(command: str, intent: dict, processed_text: str):
    """Simulate integration with Tatlock's agent system"""
    # This would integrate with the existing cortex agent
    action = intent.get("action")
    categories = intent.get("categories", [])
    
    if action == "query":
        if "weather" in categories:
            print("   🌤️  [Tatlock] Fetching weather data...")
        elif "time" in categories:
            print("   🕐 [Tatlock] Getting current time...")
        else:
            print("   🤖 [Tatlock] Processing general query...")
    elif action == "command":
        print("   🎛️  [Tatlock] Executing home automation command...")
    elif action == "reminder":
        print("   📅 [Tatlock] Setting up reminder...")
    else:
        print("   🤖 [Tatlock] Processing with AI agent...")

async def start_websocket_server():
    """Start WebSocket server for real-time voice input"""
    print("\n🌐 Starting WebSocket server for real-time voice...")
    
    voice_service = VoiceService()
    await voice_service.initialize()
    
    # Start WebSocket server
    await voice_service.start_websocket_server(host="localhost", port=8765)
    
    print("✅ WebSocket server started on ws://localhost:8765")
    print("   Connect with a WebSocket client to send voice commands")
    print("   Send audio data with 'audio:' prefix")
    print("   Send text with JSON format: {'type': 'text', 'text': 'command'}")
    
    # Keep server running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("\n🛑 Shutting down WebSocket server...")
        voice_service.stop_websocket_server()

async def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        # Start WebSocket server
        await start_websocket_server()
    else:
        # Run integration example
        await integrate_with_tatlock()

if __name__ == "__main__":
    asyncio.run(main()) 