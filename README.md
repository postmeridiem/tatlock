# Tatlock

**Status: Production Ready - Brain-Inspired Conversational AI Platform**

Tatlock is a modular, brain-inspired conversational AI platform with built-in authentication, security, and comprehensive user management. It provides a context-aware, tool-using agent with persistent memory, extensible skills, and a modern web interface. All models run locally and the datastore is on disk.

## 🚀 Quick Start

### Prerequisites

- **Linux**: Ubuntu/Debian, CentOS/RHEL/Fedora, Arch Linux, or Bazzite (immutable)
- **macOS**: Intel or Apple Silicon (M1/M2/M3)
- Python 3.10 or higher
- Git
- Ollama (for local LLM inference)

### Installation

1. **Clone and Install**:

   ```bash
   git clone https://github.com/postmeridiem/tatlock.git
   cd tatlock
   chmod +x install_tatlock.sh
   ./install_tatlock.sh
   ```

   The installation script handles dependencies, Python packages, Ollama setup, and automatically selects the optimal LLM model based on your hardware.

2. **Update API Keys**:

   ```bash
   # Edit .env and update the following variables:
   # OPENWEATHER_API_KEY - Get from https://openweathermap.org/api
   # GOOGLE_API_KEY - Get from https://console.cloud.google.com/
   # GOOGLE_CSE_ID - Get from https://programmablesearchengine.google.com/
   ```

3. **Start the Application**:

   ```bash
   ./wakeup.sh
   ```

5. **Access the Interface**:
   - **Login Page**: `http://localhost:8000/login`
   - **Admin Dashboard**: `http://localhost:8000/admin/dashboard`
   - **User Profile**: `http://localhost:8000/profile`
   - **Conversation**: `http://localhost:8000/conversation`
   - **API Documentation**: `http://localhost:8000/docs`

   **Default Admin Credentials**: `admin` / `admin123` (change after first login)

## 🧠 Architecture Overview

Tatlock is organized into modules inspired by brain regions:

- **Cortex**: Core agent logic
- **Hippocampus**: Memory system
- **Stem**: Authentication, admin, tools
- **Parietal**: Hardware monitoring
- **Occipital**: Visual processing
- **Cerebellum**: External API tools
- **Temporal**: Language/voice (in development)
- **Thalamus**: Information routing (planned)
- **Amygdala**: Emotional context (planned)

### ✅ **Production Ready Modules**

- **🧠 Cortex**: Core agent logic with tool dispatch and agentic loop
- **🧠 Hippocampus**: Complete memory system with user-specific databases
- **🧠 Stem**: Authentication, admin dashboard, tools, and utilities
- **🧠 Parietal**: Hardware monitoring and performance analysis
- **🧠 Occipital**: Visual processing and screenshot testing
- **🧠 Cerebellum**: External API tools (web search, weather)

### 🔄 **In Development**

- **🧠 Temporal**: Language processing and temporal context
- **🧠 Thalamus**: Information routing and coordination

### 📋 **Planned Modules**

- **🧠 Amygdala**: Emotional processing and mood awareness

## ✨ Key Features

### 🤖 **AI Agent System**

- **Conversational AI**: Natural language processing with context awareness
- **Tool Integration**: Access to system information, weather, web search, and more
- **Memory System**: Persistent conversation history and user data
- **Multi-user Support**: Role-based access control and user management

### 🎤 **Voice Input System** ⚠️ **Not Available**

- **Microphone Button**: Click to start voice recording in the chat interface
- **Keyword Detection**: Say "Tatlock" followed by your command
- **Real-time Processing**: 5-second auto-pause with instant transcription
- **Temporal Context**: Time-aware language understanding and processing
- **WebSocket Streaming**: Low-latency audio processing
- **⚠️ Note**: Voice processing has been removed from this version. The system operates in text-only mode.

### 🔧 **System Management**

- **Admin Dashboard**: User, role, and group management
- **System Monitoring**: Real-time hardware and performance metrics
- **Benchmark Tools**: LLM and tool performance testing
- **Debug Console**: Comprehensive logging and troubleshooting

### 🎨 **Modern Interface**

- **Material Design**: Clean, responsive web interface
- **Dark/Light Themes**: Customizable appearance
- **Mobile Responsive**: Works on desktop and mobile devices
- **Real-time Updates**: Live system status and chat interface
- **Jinja2 Templating**: Server-side rendering with shared components and layouts

### 🛡️ **Security & Privacy**

- **Complete User Isolation**: Each user has their own database for complete privacy
- **Session-Based Authentication**: Secure session management with cookies
- **Role-Based Access Control**: Fine-grained permissions and user management
- **Local Processing**: All AI processing done locally with Ollama
- **Hardware-Optimized Models**: Automatic selection of optimal LLM based on your system capabilities
- **No External Data Transmission**: Sensitive data stays within your system

## 🎯 Hardware-Optimized Model Selection

Tatlock automatically detects your hardware capabilities and selects the optimal language model for your system:

### 🏆 **High Performance** (8GB+ RAM, 4+ CPU cores, non-Apple Silicon)

- **Model**: `gemma3-cortex:latest` (Enhanced Gemma 3)
- **Features**: Maximum capability for complex reasoning and tool use
- **Best for**: Workstations and high-end systems

### ⚡ **Medium Performance** (4-8GB RAM, 2-4 CPU cores, or Apple Silicon)

- **Model**: `mistral:7b` (Mistral 7B)
- **Features**: Excellent tool calling with optimized Apple Silicon compatibility
- **Best for**: Most modern laptops and Apple M1/M2 systems

### 💡 **Low Performance** (<4GB RAM or limited CPU)

- **Model**: `phi4-mini:3.8b-q4_K_M` (Microsoft Phi-4 Mini Quantized)
- **Features**: Quantized model with tool support, optimized for speed and low memory usage
- **Best for**: Older hardware and resource-constrained environments

### 🔧 **Key Benefits**

- **Automatic Detection**: No manual configuration required
- **Apple Silicon Optimized**: Special handling for M1/M2/M3 compatibility with M1-specific low-tier classification
- **Tool Calling Focus**: All models selected for agent and function calling capabilities

### 🔧 **Manual Model Override (Advanced Users)**

For testing or specific use cases, you can manually override the automatic model selection by editing the `hardware_config.py` file:

```bash
# Switch to low-spec model for testing
echo 'RECOMMENDED_MODEL = "phi4-mini:3.8b-q4_K_M"' > hardware_config.py
echo 'PERFORMANCE_TIER = "low"' >> hardware_config.py

# Switch to high-spec model for maximum performance
echo 'RECOMMENDED_MODEL = "gemma3-cortex:latest"' > hardware_config.py
echo 'PERFORMANCE_TIER = "high"' >> hardware_config.py

# Restart application to use new model
./wakeup.sh
```

**Note**: Manual edits will be overwritten during the next installation. This feature is intended for testing and advanced configuration only.

## 📚 Documentation

- **[Developer Guide](AGENTS.md)** – Coding standards, tool patterns, and development practices (single source of truth)
- **[In-Depth Technical Information](moreinfo.md)** – Architecture and advanced features
- **[Troubleshooting](troubleshooting.md)** – Installation and runtime help
- **Module Docs**: See each module's `readme.md` for purpose and integration

## 🤝 Contributing

Tatlock is designed with a modular, brain-inspired architecture that makes it easy to extend and contribute to. See the [Developer Guide](AGENTS.md) for detailed information on:

- **Development Practices**: Coding standards, testing, and deployment
- **Tool Organization**: How to add new tools and integrate them
- **Module Development**: Guidelines for creating new brain modules
- **Testing**: Comprehensive test suite and testing practices

## 📄 License

This project is licensed under Unlicense License - see the LICENSE file for details.

Respect the Licenses of included packages and tools. This license only applies to the code and content in this git codebase.
