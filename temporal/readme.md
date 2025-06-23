# Temporal

**Status: In Development - Voice Processing & Language Understanding**

The Temporal module handles voice processing, language understanding, and temporal context awareness. Named after the brain's temporal lobe responsible for auditory processing and language comprehension, this module serves as Tatlock's auditory and linguistic processing center.

## Current Features
- **Voice Input System**: Microphone button with real-time audio streaming
- **Speech Recognition**: Whisper integration for speech-to-text conversion
- **Keyword Detection**: "Tatlock" wake word detection in transcripts
- **Language Processing**: Intent extraction and temporal reference resolution
- **WebSocket API**: Real-time audio processing with session authentication

## Architecture
- **Voice Processing**: Real-time speech-to-text using Whisper
- **Language Understanding**: Intent recognition and temporal reasoning
- **Hardware Integration**: Cross-platform audio input (planned)

## Integration
- **Cortex**: Provide voice input and temporal context
- **Hippocampus**: Store voice interaction patterns
- **Stem**: Session authentication for WebSocket connections

## Standards & Patterns
All coding and security standards are defined in [developer.md](../developer.md). Refer to it for:
- WebSocket implementation patterns
- Error handling and logging
- User context management
- Security considerations

## See Also
- [Developer Guide](../developer.md) – All standards and patterns
- [Module Docs](../README.md)
