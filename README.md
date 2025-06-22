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

### Security & Privacy
- **Complete User Isolation**: Each user has their own database for complete privacy
- **Session-Based Authentication**: Secure session management with proper cookie handling
- **Role-Based Access Control**: Fine-grained permissions and user management
- **Input Validation**: Comprehensive validation and sanitization of all inputs

### Performance & Monitoring
- **Real-time System Monitoring**: CPU, RAM, disk, and network usage tracking
- **Performance Benchmarking**: LLM and tool performance analysis
- **Debug Console**: Real-time logging and system health monitoring
- **Hardware Resource Tracking**: Comprehensive system resource analysis