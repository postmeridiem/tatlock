# Temporal

**Status: In Development - Voice Processing & Language Understanding**

The Temporal module handles voice processing, language understanding, and temporal context awareness. Named after the brain's temporal lobe responsible for auditory processing and language comprehension, this module serves as Tatlock's auditory and linguistic processing center.

## ✅ **Current Features**

### 🎤 **Voice Input System**
- **Microphone Button**: Added to chat interface for voice input
- **Real-time Audio Streaming**: WebSocket-based audio transmission to backend
- **Speech Recognition**: Whisper integration for speech-to-text conversion
- **Keyword Detection**: "Tatlock" wake word detection in transcripts
- **Auto-pause Processing**: Stops recording after 5 seconds of silence
- **Temporal Context**: Tracks interaction history and time-based patterns

### 🗣️ **Language Processing**
- **Intent Extraction**: Identifies user intent (query, command, reminder)
- **Temporal References**: Resolves "today", "tomorrow", "now", etc.
- **Urgency Detection**: Recognizes urgent requests
- **Category Classification**: Weather, time, home automation queries

## 🏗️ **Architecture**

### **Core Components**

#### **Voice Processing**
- **Speech Recognition**: Real-time speech-to-text conversion using Whisper
- **Text-to-Speech**: Natural voice responses (planned)
- **Keyword Detection**: Always-on wake word detection (planned)
- **Audio Streaming**: WebSocket-based real-time audio

#### **Language Processing**
- **Context Awareness**: Temporal and conversational context tracking
- **Language Understanding**: Advanced NLP and intent recognition
- **Temporal Reasoning**: Time-based query processing and reference resolution

#### **Hardware Integration**
- **Microphone Interface**: Cross-platform audio input (planned)
- **Speaker Output**: Audio response system (planned)
- **Home Automation**: Always-on voice assistant capabilities (planned)

## 🚀 **Quick Start**

### **1. Test Basic Functionality**
```bash
cd temporal
python test_voice.py
```

### **2. Install Dependencies**
```bash
pip install openai-whisper websockets
```

### **3. Integration with Tatlock**
```python
from temporal.voice_service import VoiceService

# Initialize voice service
voice_service = VoiceService()

# Initialize with Whisper model
await voice_service.initialize()

# Process voice command
response = await voice_service.process_voice_command("What's the weather like today?")
print(response)
```

### **4. Web Interface Usage**
1. Open the chat interface in your browser
2. Click the microphone button (🎤) next to the chat input
3. Say "Tatlock" followed by your command (e.g., "Tatlock what's the weather like today?")
4. The system will automatically detect the keyword and insert your command
5. Press Enter or click Send to submit

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Voice Configuration
ENABLE_TEMPORAL_VOICE=true
TEMPORAL_WEBSOCKET_PORT=8765
TEMPORAL_CONTEXT_WINDOW=24  # hours
```

### **Integration with main.py**
```python
# main.py
from temporal.voice_service import VoiceService

# Initialize temporal voice service
temporal_voice = VoiceService()

@app.on_event("startup")
async def startup_event():
    # Initialize voice service
    await temporal_voice.initialize()
    
    # Start WebSocket server
    await temporal_voice.start_websocket_server()
```

## 🌐 **WebSocket API**

### **Endpoint: `/ws/voice`**
- **Authentication**: Requires valid session cookie
- **Protocol**: WebSocket with binary audio streaming
- **Audio Format**: WebM audio chunks with "audio:" prefix
- **Response**: JSON with transcript, intent, and temporal context

### **Usage Example**
```javascript
// Connect to voice WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/voice');

// Send audio chunk
const audioChunk = new Blob([audioData], { type: 'audio/webm' });
const prefix = new TextEncoder().encode('audio:');
const combined = new Uint8Array(prefix.length + audioChunk.size);
combined.set(prefix, 0);
combined.set(new Uint8Array(await audioChunk.arrayBuffer()), prefix.length);
ws.send(combined.buffer);

// Receive response
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Transcript:', data.original_text);
    console.log('Intent:', data.intent);
};
```

## 🧪 **Testing**

### **Basic Tests**
```bash
# Test without external dependencies
python test_voice.py
```

### **Integration Tests**
```bash
# Test with Tatlock integration
python temporal/integration_example.py
```

### **WebSocket Server Test**
```bash
# Start WebSocket server for testing
python temporal/integration_example.py server
```

## 📦 **Dependencies**

### **Required**
- `openai-whisper`: Speech recognition
- `websockets`: Real-time communication
- `asyncio`: Asynchronous processing

### **Optional**
- `pvporcupine`: Wake word detection
- `pyttsx3`: Text-to-speech
- `pyaudio`: Audio I/O

## 🔮 **Future Features**

### **Phase 2: Always-On Detection**
- **Wake Word Detection**: Using Porcupine for keyword spotting
- **Continuous Listening**: Background audio processing
- **Hardware Integration**: Raspberry Pi and other embedded systems

### **Phase 3: Advanced Language Processing**
- **Semantic Understanding**: Deep learning for better intent recognition
- **Conversation Memory**: Long-term conversation context
- **Multi-language Support**: Internationalization

### **Phase 4: Home Automation**
- **Device Control**: Voice commands for smart home devices
- **Routines**: Automated sequences triggered by voice
- **Scheduling**: Time-based automation with voice interface

## 📋 **Implementation Notes**

### **Voice Input Flow**
1. User clicks microphone button in chat interface
2. Browser requests microphone access
3. Audio streaming begins via WebSocket
4. Whisper processes audio in real-time
5. Keyword detection identifies "Tatlock" wake word
6. Command is extracted and sent to chat interface
7. Auto-submission occurs after keyword detection

### **Temporal Context**
- **Interaction History**: Tracks all voice interactions with timestamps
- **Pattern Analysis**: Analyzes temporal patterns in user behavior
- **Context Window**: Configurable time window for context retention

### **Language Processor**
- **Temporal References**: Resolves "today", "tomorrow", "now", etc.
- **Intent Extraction**: Identifies user intent and urgency
- **Entity Recognition**: Extracts time, date, and other entities

### **Voice Service**
- **Audio Transcription**: Converts speech to text using Whisper
- **WebSocket Server**: Handles real-time audio streaming
- **Cortex Integration**: Sends processed commands to Tatlock's agent system

## 🔗 **Integration Points**

- **Cortex**: Send processed voice commands to the agent
- **Hippocampus**: Store voice interaction history and temporal context
- **Stem**: Access authentication and user context
- **Web Interface**: Real-time voice input integration

## 📈 **Performance Considerations**

- **Real-time Processing**: Low-latency audio processing for responsive voice input
- **Memory Management**: Efficient handling of audio streams and transcripts
- **WebSocket Optimization**: Optimized binary data transmission
- **Model Loading**: Efficient Whisper model loading and caching

## 🔒 **Security Considerations**

- **Audio Privacy**: Secure handling of voice data
- **Session Authentication**: Proper authentication for WebSocket connections
- **Input Validation**: Validate all voice input and transcripts
- **Data Retention**: Configurable retention policies for voice data

## ⚠️ **Error Handling**

- **Audio Failures**: Graceful handling of microphone access issues
- **Network Errors**: Robust WebSocket connection management
- **Model Errors**: Fallback handling when Whisper model fails
- **Keyword Detection**: Reliable wake word detection with false positive prevention

## 📚 **Related Documentation**

- **[README.md](../README.md)** - General overview and installation
- **[developer.md](../developer.md)** - Developer guide and practices
- **[moreinfo.md](../moreinfo.md)** - In-depth technical information
- **[cortex/readme.md](../cortex/readme.md)** - Core agent logic documentation
- **[hippocampus/readme.md](../hippocampus/readme.md)** - Memory system documentation
- **[stem/readme.md](../stem/readme.md)** - Core utilities and infrastructure
