# Temporal Module

The Temporal module provides time-aware language processing and voice interaction capabilities for Tatlock.

## Features

- **Temporal Context**: Time-aware conversation understanding and processing
- **Language Processing**: Intent extraction and natural language understanding
- **Voice Service**: Text-based command processing (voice transcription disabled)
- **WebSocket Support**: Real-time communication for voice/text commands

## Components

### Temporal Context (`temporal_context.py`)
- Maintains conversation history with temporal awareness
- Tracks interaction patterns and timing
- Provides context for language processing

### Language Processor (`language_processor.py`)
- Extracts intent from natural language
- Processes text with temporal context
- Categorizes commands and queries

### Voice Service (`voice_service.py`)
- Coordinates voice processing and temporal context
- Handles WebSocket connections for real-time communication
- Processes text commands (voice transcription not available)

## Usage

### Basic Voice Service
```python
from temporal.voice_service import VoiceService

# Initialize voice service
service = VoiceService()

# Process text command
response = await service.process_voice_command("What's the weather like today?")
print(response)
```

### WebSocket Server
```python
# Start WebSocket server
await service.start_websocket_server("localhost", 8765)

# Handle connections
# Note: Audio messages return error responses
# Text messages are processed normally
```

## Testing

Run the test suite:
```bash
python temporal/test_voice.py
```

Run integration example:
```bash
python temporal/integration_example.py
```

## Note

Voice processing (audio transcription) has been removed from this version. The system operates in text-only mode for command processing.
