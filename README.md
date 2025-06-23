# Tatlock

**Status: Production Ready - Brain-Inspired Conversational AI Platform**

Tatlock is a modular, brain-inspired conversational AI platform with built-in authentication, security, and comprehensive user management. It provides a context-aware, tool-using agent with persistent memory, extensible skills, and a modern web interface with Material Design aesthetics. Designed as a privacy-minded solution for home automation, all models run locally and the datastore is on disk.

## 🚀 Quick Start

### Prerequisites
- **Linux**: Ubuntu/Debian-based system (apt), CentOS/RHEL/Fedora (yum), or Arch Linux (pacman)
- **macOS**: Intel or Apple Silicon (M1/M2) with Homebrew
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
   The installation script will handle system dependencies, Python packages, and the automatic setup of Ollama.

2. **Update API Keys**:
   ```bash
   # Edit .env and update the following variables:
   # OPENWEATHER_API_KEY - Get from https://openweathermap.org/api
   # GOOGLE_API_KEY - Get from https://console.cloud.google.com/
   # GOOGLE_CSE_ID - Get from https://programmablesearchengine.google.com/
   ```

4. **Start the Application**:
   ```bash
   ./wakeup.sh
   ```

5. **Access the Interface**:
   - **Login Page**: `http://localhost:8000/login`
   - **Admin Dashboard**: `http://localhost:8000/admin/dashboard`
   - **User Profile**: `http://localhost:8000/profile`
   - **Debug Console**: `http://localhost:8000/chat`
   - **API Documentation**: `http://localhost:8000/docs`

   **Default Admin Credentials**: `admin` / `admin123` - CHANGE THESE

## 🧠 Brain-Inspired Architecture

Tatlock's architecture is inspired by the human brain, with each module representing a specific brain region:

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

### 🎤 **Voice Input System**
- **Microphone Button**: Click to start voice recording in the chat interface
- **Keyword Detection**: Say "Tatlock" followed by your command
- **Real-time Processing**: 5-second auto-pause with instant transcription
- **Temporal Context**: Time-aware language understanding and processing
- **WebSocket Streaming**: Low-latency audio processing with Whisper

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
- **No External Data Transmission**: Sensitive data stays within your system

## 📚 Documentation

### **Core Documentation**
- **[Developer Guide](developer.md)** - Developer-specific information, logging, debugging, and development practices
- **[In-Depth Technical Information](moreinfo.md)** - Detailed architecture, implementation details, and advanced features
- **[Troubleshooting](troubleshooting.md)** - Common installation issues and solutions

### **Module Documentation**
- **[Cortex](cortex/readme.md)** - Core agent logic and decision-making
- **[Hippocampus](hippocampus/readme.md)** - Memory system and storage
- **[Stem](stem/readme.md)** - Authentication, utilities, and core services
- **[Parietal](parietal/readme.md)** - Hardware monitoring and performance analysis
- **[Occipital](occipital/readme.md)** - Visual processing and screenshot testing
- **[Cerebellum](cerebellum/readme.md)** - External API tools and utilities

### **Planned Module Documentation**
- **[Amygdala](amygdala/readme.md)** - Emotional processing and mood awareness (planned)
- **[Temporal](temporal/readme.md)** - Language processing and temporal context (in development)
- **[Thalamus](thalamus/readme.md)** - Information routing and coordination (in development)

## 🔧 Service Management

If you installed Tatlock as an auto-starting service, you can manage it using the interactive service manager script. This script provides options to check the status, start, stop, restart, and view live logs for the service.

```bash
./manage-service.sh
```

## 🤝 Contributing

Tatlock is designed with a modular, brain-inspired architecture that makes it easy to extend and contribute to. See the [Developer Guide](developer.md) for detailed information on:

- **Development Practices**: Coding standards, testing, and deployment
- **Tool Organization**: How to add new tools and integrate them
- **Module Development**: Guidelines for creating new brain modules
- **Testing**: Comprehensive test suite and testing practices

## 📄 License

This project is licensed under Unlicense License - see the LICENSE file for details.

Respect the Licenses of included packages and tools. This license only applies to the code and content in this git codebase.
