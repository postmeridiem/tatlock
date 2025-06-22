# Tatlock

Tatlock is a modular, brain-inspired conversational AI platform with built-in authentication, security, and comprehensive user management. It provides a context-aware, tool-using agent with persistent memory, extensible skills, and a modern web interface with Material Design aesthetics. It is intended to be used as a privacy minded solution for home automation, since all models run locally and the datastore is on disk.

## Features

### 🤖 **AI Agent System**
- **Conversational AI**: Natural language processing with context awareness
- **Tool Integration**: Access to system information, weather, and more
- **Memory System**: Persistent conversation history and user data
- **Multi-user Support**: Role-based access control and user management

### 🎤 **Voice Input System** *(New!)*
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

## Brain-Inspired Architecture

Tatlock's architecture is inspired by the human brain, with each module representing a specific brain region:

### Fully Implemented Modules
- **🧠 Cortex**: Core agent logic with tool dispatch and agentic loop
- **🧠 Hippocampus**: Complete memory system with user-specific databases
- **🧠 Stem**: Authentication, admin dashboard, tools, and utilities
- **🧠 Parietal**: Hardware monitoring and performance analysis

### Planned Modules (Future Development)
- **🧠 Amygdala**: Emotional processing and mood awareness
- **🧠 Cerebellum**: Procedural memory and task automation
- **🧠 Occipital**: Visual processing and image analysis
- **🧠 Temporal**: Language processing and temporal context
- **🧠 Thalamus**: Information routing and coordination

## Installation

### Prerequisites
- **Linux**: Ubuntu/Debian-based system (apt), CentOS/RHEL/Fedora (yum), or Arch Linux (pacman)
- **macOS**: Intel or Apple Silicon (M1/M2) with Homebrew
- Python 3.10 or higher
- Git
- Ollama (for local LLM inference)

### Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/postmeridiem/tatlock.git
   cd tatlock
   ```

2. Run the installation script:
   ```bash
   chmod +x install_tatlock.sh
   ./install_tatlock.sh
   ```

   **Note**: The installation script supports apt-based systems (Ubuntu/Debian), yum-based systems (CentOS/RHEL/Fedora), macOS (Intel/Apple Silicon), and Arch Linux. For other distributions, manual installation of dependencies may be required.

   The script will automatically:
   - **Configure server settings**: Prompt for HOSTNAME and PORT (defaults to localhost:8000)
   - Create a `.env` file with all required environment variables and generate a secure `STARLETTE_SECRET` key
   - **Handle existing `.env` files intelligently**: Offers to update HOSTNAME and PORT even when keeping existing configuration
   - Create a Python virtual environment in the `.venv` directory for isolated dependency management
   - Safely handle existing virtual environments (only recreates if explicitly requested or corrupted)
   - Make `wakeup.sh` executable for easy application startup
   - **Intelligently handle admin user creation**: If an admin user already exists, you can choose to keep it or replace it with new credentials
   - **Provide detailed debugging**: Enhanced error reporting and system diagnostics
   - **Clean up existing services**: If you choose not to install as a service, any existing Tatlock services are automatically stopped and removed
   - Optionally install Tatlock as an auto-starting service for automatic startup on system boot

3. Install and start Ollama:
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Start Ollama service
   ollama serve
   
   # Pull the required model (in another terminal)
   ollama pull gemma3-cortex:latest
   ```

4. Update your API keys:
   ```bash
   # Edit .env and update the following variables with your actual API keys:
   # OPENWEATHER_API_KEY - Get from https://openweathermap.org/api
   # GOOGLE_API_KEY - Get from https://console.cloud.google.com/
   # GOOGLE_CSE_ID - Get from https://programmablesearchengine.google.com/
   ```

5. Start the application:
   ```bash
   # Start the application (automatically activates virtual environment)
   ./wakeup.sh
   ```

   **Note**: If you installed Tatlock as an auto-starting service, see the [Service Management](#service-management) section below for commands to start, stop, and manage the service.

6. Access the interface:
   - **Login Page**: `http://localhost:8000/login` (or your configured HOSTNAME:PORT)
   - **Admin Dashboard**: `http://localhost:8000/admin/dashboard`
   - **User Profile**: `http://localhost:8000/profile`
   - **Debug Console**: `http://localhost:8000/chat`
   - **API Documentation**: `http://localhost:8000/docs`

   **Default Admin Credentials**: If you kept the existing admin user during installation, use:
   - **Username**: `admin`
   - **Password**: `admin123`

   **Note**: The default configuration is localhost:8000. You can change this by modifying the `HOSTNAME` and `PORT` variables in your `.env` file or during installation.

### Service Management

If you installed Tatlock as an auto-starting service during installation, you can manage it using the following commands:

#### Linux (systemd)

**Check service status:**
```bash
sudo systemctl status tatlock
```

**Start the service:**
```bash
sudo systemctl start tatlock
```

**Stop the service:**
```bash
sudo systemctl stop tatlock
```

## Documentation

### Core Documentation
- **[Developer Guide](developer.md)** - Developer-specific information, logging, debugging, and development practices
- **[In-Depth Technical Information](moreinfo.md)** - Detailed architecture, implementation details, and advanced features
- **[Troubleshooting](troubleshooting.md)** - Common installation issues and solutions

### Module Documentation
- **[Cortex](cortex/readme.md)** - Core agent logic and decision-making
- **[Hippocampus](hippocampus/readme.md)** - Memory system and storage
- **[Stem](stem/readme.md)** - Authentication, utilities, and core services
- **[Parietal](parietal/readme.md)** - Hardware monitoring and performance analysis

### Planned Module Documentation
- **[Amygdala](amygdala/readme.md)** - Emotional processing and mood awareness (planned)
- **[Cerebellum](cerebellum/readme.md)** - Procedural memory and task automation (planned)
- **[Occipital](occipital/readme.md)** - Visual processing and image analysis (planned)
- **[Temporal](temporal/readme.md)** - Language processing and temporal context (planned)
- **[Thalamus](thalamus/readme.md)** - Information routing and coordination (planned)

## Key Features

### Modular Architecture
- **Brain-Inspired Design**: Codebase organized into modules inspired by brain regions
- **Extensible Tools**: Easily add new tools and skills for the agent to use
- **Offline Capability**: Material Icons and static assets work without internet connection
- **Service Management**: Optional auto-starting service for production deployments
- **Jinja2 Templating**: Server-side rendering with shared components and layouts

### Security & Privacy
- **Complete User Isolation**: Each user has their own database for complete privacy
- **Session-Based Authentication**: Secure session management with cookies
- **Role-Based Access Control**: Fine-grained permissions and user management
- **Local Processing**: All AI processing done locally with Ollama
- **No External Data Transmission**: Sensitive data stays within your system

### Performance & Monitoring
- **Real-time System Monitoring**: Hardware and performance metrics
- **Benchmark Tools**: LLM and tool performance testing
- **Debug Console**: Comprehensive logging and troubleshooting
- **Service Management**: Optional systemd/LaunchAgent integration

## Contributing

Tatlock is designed with a modular, brain-inspired architecture that makes it easy to extend and contribute to. See the [Developer Guide](developer.md) for detailed information on development practices, coding standards, and how to add new features.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
