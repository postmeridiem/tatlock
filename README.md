# Tatlock

Tatlock is a modular, brain-inspired conversational AI platform with built-in authentication, security, and comprehensive user management. It provides a context-aware, tool-using agent with persistent memory, extensible skills, and a modern web interface with Material Design aesthetics.

## Features

### Core AI Capabilities
- **Conversational AI API**: FastAPI-based HTTP interface for chat and tool use with authentication
- **Agentic Loop**: The agent can call external tools (weather, web search, memory recall, etc.) as part of its reasoning process
- **Persistent Memory**: Long-term storage and recall of conversations, topics, and user data
- **Natural Language Date Parsing**: Understands queries like "yesterday" or "last week" for memory recall
- **Topic Classification**: Automatic categorization of conversations for better memory organization

### Authentication & Security
- **Session-Based Authentication**: Modern session management with secure cookies
- **Comprehensive User Management**: Create, authenticate, and manage users with roles and groups
- **Password Security**: PBKDF2 hashing with unique salts for each user
- **Role-Based Access Control**: Users can have multiple roles (user, admin, moderator)
- **Group Management**: Users can belong to multiple groups (users, admins, moderators)
- **Admin Endpoints**: Special endpoints requiring admin privileges
- **User Data Isolation**: Each user has their own memory database for complete privacy

### Web Interface
- **Modern Admin Dashboard**: Complete user, role, and group management interface
- **User Profile Management**: Self-service profile editing and password changes
- **Debug Console**: Real-time JSON logging of server interactions for development
- **Material Design Icons**: Professional, consistent iconography throughout the interface
- **Dark/Light Mode Toggle**: User preference for theme switching
- **Responsive Design**: Works on desktop and mobile devices
- **Chat Sidepane**: Integrated chat interface on all pages for assistance

### Modular Architecture
- **Brain-Inspired Design**: Codebase organized into modules inspired by brain regions
- **Extensible Tools**: Easily add new tools and skills for the agent to use
- **Offline Capability**: Material Icons and static assets work without internet connection
- **Service Management**: Optional auto-starting service for production deployments

## Current Implementation Status

### Fully Implemented Modules
- **cortex**: Core agent logic with tool dispatch and agentic loop
- **hippocampus**: Complete memory system with user-specific databases
- **stem**: Authentication, admin dashboard, tools, and utilities

### Planned Modules (Future Development)
- **amygdala**: Emotional processing and mood awareness
- **cerebellum**: Procedural memory and task automation
- **occipital**: Visual processing and image analysis
- **parietal**: Spatial reasoning and sensory integration
- **temporal**: Language processing and temporal context
- **thalamus**: Information routing and coordination

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

   The script will automatically create a `.env` file with all required environment variables and generate a secure `STARLETTE_SECRET` key.

   **Note**: If a `.env` file already exists, the script will ask if you want to overwrite it or keep the existing configuration.

   The script also creates a Python virtual environment in the `.venv` directory for isolated dependency management.

   **Note**: The script safely handles existing virtual environments and will only recreate them if explicitly requested or if they appear to be corrupted.

   The script also makes `wakeup.sh` executable for easy application startup.

   The script optionally offers to install Tatlock as an auto-starting service for automatic startup on system boot.

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
   - **Login Page**: `http://localhost:8000/login`
   - **Admin Dashboard**: `http://localhost:8000/admin/dashboard`
   - **User Profile**: `http://localhost:8000/profile`
   - **Debug Console**: `http://localhost:8000/chat`
   - **API Documentation**: `http://localhost:8000/docs`

   **Note**: The default port is 8000. You can change this by modifying the `PORT` variable in your `.env` file.

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

**Restart the service:**
```bash
sudo systemctl restart tatlock
```

**Enable auto-start on boot:**
```bash
sudo systemctl enable tatlock
```

**Disable auto-start on boot:**
```bash
sudo systemctl disable tatlock
```

**View service logs:**
```bash
# View recent logs
sudo journalctl -u tatlock

# Follow logs in real-time
sudo journalctl -u tatlock -f

# View logs from today
sudo journalctl -u tatlock --since today
```

#### macOS (launchd)

**Check if service is loaded:**
```bash
launchctl list | grep tatlock
```

**Load (start) the service:**
```bash
launchctl load ~/Library/LaunchAgents/com.tatlock.plist
```

**Unload (stop) the service:**
```bash
launchctl unload ~/Library/LaunchAgents/com.tatlock.plist
```

**View service logs:**
```bash
# View standard output logs
tail -f /tmp/tatlock.log

# View error logs
tail -f /tmp/tatlock.error.log

# View both logs
tail -f /tmp/tatlock*.log
```

#### Manual vs Service Mode

**Running manually (development):**
```bash
./wakeup.sh
```

**Running as service (production):**
- Service starts automatically on boot/login
- Runs in the background
- Automatically restarts if it crashes
- Logs are written to system logs or files

**Switching between modes:**
- To stop the service and run manually: Stop the service first, then run `./wakeup.sh`
- To switch back to service mode: Stop manual process, then start the service

**Troubleshooting service issues:**
- If the service won't start, check the logs for error messages
- Ensure the `.env` file exists and has valid API keys
- Verify that Ollama is running (required for Tatlock to start)
- Check that the port specified in `.env` is not already in use

## Architecture Overview

### Core Modules

#### cortex
The central processing unit that orchestrates all interactions. Handles the agentic loop, tool dispatch, and conversation management.

#### hippocampus  
The memory system that provides persistent storage for conversations, topics, and user data. Each user has their own isolated database.

#### stem
The foundational module containing authentication, admin dashboard, tool definitions, and utility functions.

### Available Tools

The agent can currently use these tools:
- **web_search**: Search the web for current information
- **get_weather_forecast**: Get weather forecasts for specific cities and dates
- **find_personal_variables**: Look up personal information about the user
- **recall_memories**: Search conversation history by keyword
- **recall_memories_with_time**: Search conversation history with temporal filtering
- **get_user_conversations**: List all conversations for the current user
- **get_conversation_details**: Get detailed information about a specific conversation
- **search_conversations**: Search conversations by title or content
- **get_conversations_by_topic**: Find conversations containing specific topics
- **get_topics_by_conversation**: Get all topics in a specific conversation
- **get_conversation_summary**: Get comprehensive conversation summaries
- **get_topic_statistics**: Get statistics about topics across conversations

## API Usage

### Authentication
All API endpoints require session-based authentication. Users must first log in through the web interface or `/login/auth` endpoint.

### Chat Endpoint
```bash
POST /cortex
Content-Type: application/json

{
  "message": "What's the weather like in Amsterdam?",
  "history": [],
  "conversation_id": "optional-conversation-id"
}
```

### Response Format
```json
{
  "response": "The weather in Amsterdam is...",
  "topic": "weather",
  "history": [...],
  "conversation_id": "2024-01-15-14-30-00"
}
```

## Development

### Project Structure
```
tatlock/
├── cortex/           # Core agent logic
├── hippocampus/      # Memory and database management
├── stem/            # Authentication, tools, and utilities
├── amygdala/        # Planned: Emotional processing
├── cerebellum/      # Planned: Procedural memory
├── occipital/       # Planned: Visual processing
├── parietal/        # Planned: Spatial reasoning
├── temporal/        # Planned: Language processing
├── thalamus/        # Planned: Information routing
├── main.py          # FastAPI application entry point
├── config.py        # Configuration management
└── requirements.txt # Python dependencies
```

### Adding New Tools
1. Define the tool in `stem/tools.py`
2. Add the tool to the `AVAILABLE_TOOLS` dictionary in `cortex/agent.py`
3. Update the tool documentation in the relevant README files

### Database Schema
- **system.db**: Shared authentication and user management
- **{username}_longterm.db**: Per-user conversation memory and topics

## Troubleshooting

If you encounter installation issues, especially repository-related errors, see the [Installation Troubleshooting Guide](INSTALLATION_TROUBLESHOOTING.md) for detailed solutions.

### Common Issues

**Ollama not running:**
```bash
# Start Ollama service
ollama serve
```

**Port already in use:**
```bash
# Change port in .env file
PORT=8001
```

**Database errors:**
```bash
# Recreate databases
python -m stem.installation.database_setup
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.