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

## Installation

### Prerequisites
- **Linux**: Ubuntu/Debian-based system (apt), CentOS/RHEL/Fedora (yum), or Arch Linux (pacman)
- **macOS**: Intel or Apple Silicon (M1/M2) with Homebrew
- Python 3.10 or higher
- Git

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

3. Update your API keys:
   ```bash
   # Edit .env and update the following variables with your actual API keys:
   # OPENWEATHER_API_KEY - Get from https://openweathermap.org/api
   # GOOGLE_API_KEY - Get from https://console.cloud.google.com/
   # GOOGLE_CSE_ID - Get from https://programmablesearchengine.google.com/
   ```

4. Start the application:
   ```bash
   python main.py
   ```

5. Access the interface:
   - **Login Page**: `http://localhost:8000/login`
   - **Admin Dashboard**: `http://localhost:8000/admin/dashboard`
   - **User Profile**: `http://localhost:8000/profile`
   - **Debug Console**: `http://localhost:8000/chat`
   - **API Documentation**: `http://localhost:8000/docs`

### Troubleshooting

If you encounter installation issues, especially repository-related errors, see the [Installation Troubleshooting Guide](INSTALLATION_TROUBLESHOOTING.md) for detailed solutions.

### Default Login
- **Username**: admin
- **Password**: admin
- **Role**: admin
- **Groups**: admins, users

## LLM Model
Tatlock uses the **ebdm/gemma3-enhanced:12b** model as its base LLM. During installation, this model is downloaded and copied to `gemma3-cortex:latest` for use by the application. The enhanced version provides improved reasoning capabilities and tool usage for the agentic interactions.

## Directory Structure

### Core Files
- **main.py**: Entry point. Defines the FastAPI app and HTTP endpoints with authentication
- **config.py**: Loads environment variables and API keys
- **requirements.txt**: Python dependencies
- **install_tatlock.sh**: Automated installation script for system dependencies, Python packages, and database setup
- **wakeup.sh**: Startup script

### Core Modules
- **cortex/**: Core agent logic and API implementation. Orchestrates all subsystems and exposes the FastAPI interface
- **hippocampus/**: Persistent memory, database access, and recall logic. All system prompts (except the current date) are stored in the `rise_and_shine` table
- **stem/**: Shared utilities, tool definitions, authentication system, admin dashboard, and static file serving

### Web Interface
- **stem/static/**: Web interface files including HTML, CSS, JavaScript, and Material Icons
  - **stem/static/admin.html**: Admin dashboard with user, role, and group management
  - **stem/static/profile.html**: User profile management interface
  - **stem/static/chat.html**: Debug console with JSON logging
  - **stem/static/style.css**: Consolidated styling with dark/light mode support
  - **stem/static/js/**: JavaScript modules for each page functionality
  - **stem/static/fonts/**: Material Icons font files for offline use

### Brain-Inspired Subsystems (Planned)
- **amygdala/**: Mood and emotional context, based on news and external inputs
- **cerebellum/**: Procedural memory, routines, and background tasks
- **occipital/**: Visual processing and perception
- **parietal/**: Spatial reasoning and sensory integration
- **temporal/**: Auditory processing, language, and time context
- **thalamus/**: Routing, filtering, and relaying information between subsystems

### Installation & Setup
- **stem/installation/**: Database setup utilities for system.db and longterm.db initialization

## Available Tools
- **web_search**: Search the web for current information
- **find_personal_variables**: Look up personal information about the user
- **get_weather_forecast**: Get weather forecasts for specific cities and dates
- **recall_memories**: Search conversation history by keyword
- **recall_memories_with_time**: Search conversation history with temporal filtering
- **get_user_conversations**: List all conversations for the current user
- **get_conversation_details**: Get detailed information about a specific conversation
- **search_conversations**: Search conversations by title or content
- **get_conversations_by_topic**: Find conversations containing specific topics
- **get_topics_by_conversation**: Get all topics in a specific conversation
- **get_conversation_summary**: Get comprehensive conversation summaries
- **get_topic_statistics**: Get statistics about topics across conversations

## API Endpoints

### Protected Endpoints (Require Authentication)
- `GET /` - Root endpoint with automatic redirects based on authentication
- `POST /cortex` - Main chat API endpoint
- `GET /chat` - Debug console interface
- `GET /admin/dashboard` - Admin dashboard (requires admin role)
- `GET /profile` - User profile management
- `GET /docs` - API documentation (Swagger UI)

### Authentication Endpoints
- `GET /login` - Login page
- `POST /login/auth` - Session-based login endpoint
- `GET /logout` - Logout page (clears session and redirects)
- `POST /logout` - Session-based logout endpoint

### Admin Endpoints (Require Admin Role)
- `GET /admin/stats` - System statistics
- `GET /admin/users` - List all users
- `POST /admin/users` - Create new user
- `PUT /admin/users/{username}` - Update user
- `DELETE /admin/users/{username}` - Delete user
- `GET /admin/roles` - List all roles
- `POST /admin/roles` - Create new role
- `PUT /admin/roles/{id}` - Update role
- `DELETE /admin/roles/{id}` - Delete role
- `GET /admin/groups` - List all groups
- `POST /admin/groups` - Create new group
- `PUT /admin/groups/{id}` - Update group
- `DELETE /admin/groups/{id}` - Delete group

### Profile Endpoints
- `GET /profile/` - Get user profile information
- `PUT /profile/` - Update user profile
- `PUT /profile/password` - Change user password

### Static Files
- `/static/*` - Static file serving (HTML, CSS, JS, fonts)
- `/favicon.ico` - App favicon

## Environment Variables
Required environment variables (set in `.env` file):
```
# API Keys (Required)
OPENWEATHER_API_KEY=your_openweather_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id

# LLM Configuration
OLLAMA_MODEL=gemma3-cortex:latest

# Database Configuration
DATABASE_ROOT=hippocampus/

# Security
STARLETTE_SECRET=auto_generated_uuid
```

## Testing
The project includes comprehensive test coverage with 244 tests covering all major functionality:
- API endpoints and authentication
- Database operations and memory management
- User management and security
- Tool system and agent logic
- Web interface components

Run tests with:
```bash
python -m pytest
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License
This project is licensed under the MIT License.