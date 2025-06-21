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
- **Comprehensive User Management**: Create, authenticate, and manage users with roles and groups
- **Password Security**: PBKDF2 hashing with unique salts for each user
- **Role-Based Access Control**: Users can have multiple roles (user, admin, moderator)
- **Group Management**: Users can belong to multiple groups (users, admins, moderators)
- **HTTP Basic Authentication**: All API endpoints require authentication
- **Admin Endpoints**: Special endpoints requiring admin privileges

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

## LLM Model
Tatlock uses the **ebdm/gemma3-enhanced:12b** model as its base LLM. During installation, this model is downloaded and copied to `gemma3-cortex:latest` for use by the application. The enhanced version provides improved reasoning capabilities and tool usage for the agentic interactions.

## Directory Structure

### Core Files
- **main.py**: Entry point. Defines the FastAPI app and HTTP endpoints with authentication (ReDoc disabled)
- **config.py**: Loads environment variables and API keys
- **requirements.txt**: Python dependencies
- **install_tatlock.sh**: Automated installation script for system dependencies, Python packages, and database setup
- **wakeup.sh**: Startup and auto-commit script

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

## Authentication & Security

Tatlock includes a comprehensive authentication system:

### User Management
- **User CRUD Operations**: Create, read, update, and delete users through admin interface
- **Profile Management**: Users can edit their own profiles and change passwords
- **Password Security**: PBKDF2 hashing with unique salts for each user
- **Show/Hide Password**: Toggle buttons for password visibility

### Access Control
- **Role-Based Access Control**: Users can have multiple roles (user, admin, moderator)
- **Group Management**: Users can belong to multiple groups (users, admins, moderators)
- **Admin Protection**: Critical roles and groups cannot be deleted or renamed
- **Last Admin Protection**: Prevents deletion of the last admin user

### Default Setup
- **Admin User**: Created during installation with username/password and admin privileges
- **Default Roles**: user, admin, moderator
- **Default Groups**: users, admins, moderators

## Web Interface Features

### Admin Dashboard (`/admin/dashboard`)
- **System Statistics**: Total users, roles, groups, and admin users
- **User Management**: Complete CRUD operations for users
- **Role Management**: Create, edit, and delete roles
- **Group Management**: Create, edit, and delete groups
- **Real-time Updates**: Automatic refresh of data after changes
- **Snackbar Notifications**: User-friendly success/error messages

### User Profile (`/profile`)
- **Profile Information**: Display user details, roles, and groups
- **Profile Editing**: Update personal information
- **Password Management**: Change password with current password verification
- **Responsive Design**: Works on all device sizes

### Debug Console (`/chat`)
- **JSON Logging**: Real-time display of all server interactions
- **System Information**: Display system status and configuration
- **Export Functionality**: Export logs for analysis
- **Auto-scroll**: Automatic scrolling to latest entries

### Global Features
- **Material Icons**: Professional iconography throughout
- **Dark/Light Mode**: User preference with persistent storage
- **Chat Sidepane**: Integrated chat interface on all pages
- **Responsive Navigation**: Collapsible sidebar navigation
- **User Dropdown**: Profile access, theme toggle, and logout

## System Prompts
All system prompts (base instructions) for the LLM should be stored as records in the `rise_and_shine` table in the hippocampus database, except for the current date, which is injected dynamically.

## Available Tools
- **web_search**: Search the web for current information
- **find_personal_variables**: Look up personal information about the user
- **get_weather_forecast**: Get weather forecasts for specific cities and dates
- **recall_memories**: Search conversation history by keyword
- **recall_memories_with_time**: Search conversation history with temporal filtering

## API Endpoints

### Protected Endpoints (Require Authentication)
- `GET /` - Root endpoint with user information
- `POST /cortex` - Main chat API endpoint
- `GET /chat` - Debug console interface
- `GET /admin/dashboard` - Admin dashboard (requires admin role)
- `GET /profile` - User profile management
- `GET /docs` - API documentation (Swagger UI)

### Admin Endpoints (Require Admin Role)
- `GET /admin/stats` - System statistics
- `GET /admin/users` - List all users
- `POST /admin/users` - Create new user
- `PUT /admin/users/{id}` - Update user
- `DELETE /admin/users/{id}` - Delete user
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

## Getting Started

### 1. Installation
Run the automated installer:
```bash
bash install_tatlock.sh
```
This will:
- Install system dependencies and Python packages
- Download and install Ollama
- Download the LLM model (ebdm/gemma3-enhanced:12b)
- Initialize databases (system.db and longterm.db)
- Create default admin user with roles and groups

### 2. Environment Setup
Set up environment variables (see `config.py`):
```bash
OPENWEATHER_API_KEY=your_openweather_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
OLLAMA_MODEL=gemma3-cortex:latest
LONGTERM_DB=hippocampus/longterm.db
SYSTEM_DB=hippocampus/system.db
```

### 3. Start the Application
```bash
python main.py
```

### 4. Access the Interface
- **Admin Dashboard**: `http://localhost:8000/admin/dashboard`
- **User Profile**: `http://localhost:8000/profile`
- **Debug Console**: `http://localhost:8000/chat`
- **API Documentation**: `http://localhost:8000/docs`
- **API Endpoint**: `http://localhost:8000/cortex`

### 5. Default Login
- **Username**: admin (created during installation)
- **Password**: admin (created during installation)
- **Role**: admin
- **Groups**: admins, users

## Environment Variables
Required environment variables (set in `.env` file):
```
OPENWEATHER_API_KEY=your_openweather_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
OLLAMA_MODEL=gemma3-cortex:latest
LONGTERM_DB=hippocampus/longterm.db
SYSTEM_DB=hippocampus/system.db
```

## Technical Details

### Database Schema
- **system.db**: User authentication, roles, and groups
- **longterm.db**: Conversation memory, topics, and system prompts

### Security Features
- **Password Hashing**: PBKDF2 with unique salts
- **Session Management**: HTTP Basic Authentication
- **Role-Based Access**: Granular permission control
- **Input Validation**: Pydantic models for all API requests

### Frontend Technologies
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS variables for theming
- **JavaScript**: Modular ES6+ code with async/await
- **Material Icons**: Professional iconography (offline-capable)

## Contributing
Contributions are welcome! Please see the codebase for module-level readmes and follow the modular, brain-inspired structure for new features. All system prompts should be added to the `rise_and_shine` table rather than hardcoded.

### Development Guidelines
- Follow the brain-inspired module structure
- Add comprehensive documentation for new features
- Include proper error handling and validation
- Test authentication and authorization thoroughly
- Maintain consistent styling with Material Design principles 

# Memory Databases
- Each user now has a separate long-term memory database at `hippocampus/longterm/<username>.db`.
- The admin user's memory is stored at `hippocampus/longterm/admin.db`.
- Databases are created automatically when a user is added and deleted when a user is removed. 