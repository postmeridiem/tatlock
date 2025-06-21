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

### Logging & Debugging

Tatlock includes a comprehensive logging system integrated with FastAPI for debugging and monitoring tool execution.

### Log Levels

The application uses standard Python logging levels:
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about tool execution and requests
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages with stack traces

### Tool Execution Logging

When the agent executes tools, you'll see detailed logs like this:

```
2024-01-15 14:30:45,123 - cortex.agent - INFO - Tool Iteration 1
2024-01-15 14:30:45,456 - cortex.agent - INFO - LLM Response: 1 tool calls
2024-01-15 14:30:45,789 - cortex.agent - INFO - TOOL: find_personal_variables | Args: {"searchkey": "name"}
2024-01-15 14:30:46,012 - cortex.agent - INFO - Tool Iteration 2
2024-01-15 14:30:46,345 - cortex.agent - INFO - LLM Response: Final response (no tools)
```

### Logging Configuration

The logging is configured in `main.py` with the following settings:

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
    ]
)
```

### Customizing Log Levels

To change the log level for debugging:

```python
# In main.py, change the level:
logging.basicConfig(level=logging.DEBUG)
```

### Environment-Specific Logging

**Development Mode:**
- Set log level to DEBUG for maximum information
- All tool calls and parameters are logged
- Error stack traces are included

**Production Mode:**
- Set log level to INFO or WARNING
- Reduce log verbosity for performance
- Focus on errors and warnings

### Log Output Locations

**Manual Mode:**
- Logs appear in the console where you run `./wakeup.sh`

**Service Mode:**
- **Linux**: `sudo journalctl -u tatlock -f`
- **macOS**: `tail -f /tmp/tatlock.log`

### Debugging Tool Issues

If tools are failing, check the logs for:
1. **Tool call parameters**: Verify the arguments being passed
2. **Error messages**: Look for specific error details
3. **API key issues**: Check if external APIs are accessible
4. **Database errors**: Verify database connectivity and permissions

### Performance Monitoring

The logs include:
- Tool execution times
- Number of iterations per request
- Success/failure rates
- API response times

### Adding Custom Logging

To add logging to your own modules:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Your message here")
logger.error("Error message", exc_info=True)
```

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

### Modular Architecture
- **Brain-Inspired Design**: Codebase organized into modules inspired by brain regions
- **Extensible Tools**: Easily add new tools and skills for the agent to use
- **Offline Capability**: Material Icons and static assets work without internet connection
- **Service Management**: Optional auto-starting service for production deployments