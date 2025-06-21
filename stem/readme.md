# stem

This module provides shared utilities, tool definitions, session-based authentication system, admin dashboard, and static file serving for Tatlock. It contains essential helper functions, tool implementations, and infrastructure components used across the system.

## Core Components

### Authentication & Security (`security.py`)
Comprehensive user management and security system with session-based authentication:

- **User Management**: Create, authenticate, update, and delete users
- **Password Security**: PBKDF2 hashing with unique salts for each user
- **Session Management**: Secure cookie-based session authentication
- **Role Management**: Create, assign, and manage user roles (user, admin, moderator)
- **Group Management**: Create, assign, and manage user groups (users, admins, moderators)
- **Access Control**: Role-based and group-based permission checking
- **Security Protection**: Prevents deletion of critical roles/groups and last admin user
- **Login/Logout**: Session-based authentication with proper redirects

### Admin Dashboard (`admin.py`)
Complete administrative interface with FastAPI router:

- **Admin Dashboard Page**: `/admin/dashboard` endpoint for web interface
- **System Statistics**: Total users, roles, groups, and admin users
- **User CRUD Operations**: Create, read, update, and delete users
- **Role Management**: Complete role lifecycle management
- **Group Management**: Complete group lifecycle management
- **Pydantic Models**: Request/response models for all admin operations
- **Error Handling**: Comprehensive error handling and validation

### Profile Management (`profile.py`)
User self-service profile management:

- **Profile Information**: Display user details, roles, and groups
- **Profile Editing**: Update personal information (first name, last name, email)
- **Password Management**: Change password with current password verification
- **FastAPI Router**: Dedicated router for profile endpoints

### Tool System (`tools.py`)
Defines and implements all available tools for the Tatlock agent:

- **`web_search`**: Google Custom Search API integration for web queries
- **`find_personal_variables`**: Personal information lookup system
- **`get_weather_forecast`**: OpenWeather API integration for weather data
- **`recall_memories`**: Memory search by keyword (user-scoped)
- **`recall_memories_with_time`**: Memory search with temporal filtering (user-scoped)
- **`get_user_conversations`**: List all conversations for the current user
- **`get_conversation_details`**: Get detailed conversation information for current user
- **`search_conversations`**: Search conversations by title or content for current user
- **`get_conversations_by_topic`**: Find conversations containing specific topics for current user
- **`get_topics_by_conversation`**: Get all topics in a specific conversation for current user
- **`get_conversation_summary`**: Get comprehensive conversation summaries for current user
- **`get_topic_statistics`**: Get statistics about topics across conversations for current user

### Static File Serving (`static.py`)
Handles web interface and static file management:

- **`mount_static_files()`**: Mounts static files directory to FastAPI
- **`get_admin_page()`**: Returns the admin dashboard HTML
- **`get_profile_page()`**: Returns the user profile HTML
- **`get_chat_page()`**: Returns the debug console HTML
- **`get_login_page()`**: Returns the login page HTML

### Data Models (`models.py`)
Pydantic models for API requests and responses:

- **Chat Models**: ChatRequest, ChatResponse, ChatMessage
- **User Models**: CreateUserRequest, UpdateUserRequest, UserResponse
- **Admin Models**: AdminStatsResponse, CreateRoleRequest, RoleResponse
- **Group Models**: CreateGroupRequest, UpdateGroupRequest, GroupResponse
- **Profile Models**: PasswordChangeRequest

### Utility Modules

#### `jsonutils.py`
JSON manipulation and validation helpers:
- JSON serialization/deserialization utilities
- Error handling for JSON operations

#### `textutils.py`
Text processing and manipulation:
- Text cleaning and formatting functions
- String manipulation utilities

#### `logging.py`
Logging configuration and utilities:
- Structured logging setup
- Log formatting and output management

#### `timeawareness.py`
Natural language date parsing:
- **`parse_natural_date_range()`**: Converts expressions like "yesterday", "last week" to date ranges
- Supports various date formats and relative time expressions
- Returns ISO date strings for database queries

### Installation Support (`installation/`)
Database setup and initialization utilities:

- **`database_setup.py`**: Creates and populates system.db and user longterm.db templates
- **`create_system_db_tables()`**: Shared authentication database initialization
- **`create_longterm_db_tables()`**: User memory database template initialization
- **`create_default_roles()`**: Sets up default user roles
- **`create_default_groups()`**: Sets up default user groups
- **`create_default_rise_and_shine()`**: Populates system prompts (copied to each user's database)

## Web Interface Components

### HTML Pages
- **admin.html**: Complete admin dashboard with user, role, and group management
- **profile.html**: User profile management interface
- **chat.html**: Debug console with JSON logging
- **login.html**: Session-based login page

### Styling
- **style.css**: Consolidated CSS with dark/light mode support
- **material-icons.css**: Material Design Icons font definitions
- **Responsive Design**: Works on desktop and mobile devices
- **Theme System**: CSS variables for consistent theming

### JavaScript Modules
- **common.js**: Shared functionality (snackbar, dark mode, chat sidepane)
- **admin.js**: Admin dashboard functionality
- **profile.js**: Profile management functionality
- **debug.js**: Debug console functionality

### Static Assets
- **fonts/**: Material Icons font files for offline use
- **js/**: Modular JavaScript files
- **favicon/**: Complete favicon and app icon set
- **Icons**: Material Design Icons throughout the interface

## API Endpoints

### Admin Endpoints (Require Admin Role)
- `GET /admin/dashboard` - Admin dashboard page
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
- `GET /profile` - User profile page
- `GET /profile/` - Get user profile information
- `PUT /profile/` - Update user profile
- `PUT /profile/password` - Change user password

### Authentication Endpoints
- `GET /login` - Login page
- `POST /login/auth` - Session-based login endpoint
- `GET /logout` - Logout page (clears session and redirects)
- `POST /logout` - Session-based logout endpoint

### Web Interface Endpoints
- `GET /chat` - Debug console page

## Tool Integration

All tools are defined in the `tools.py` module and are automatically scoped to the current user's data. The agent automatically injects the current user's username into tool calls to ensure complete data isolation and privacy.