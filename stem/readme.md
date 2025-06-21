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
- **User Context**: Provides user information to other modules for personalization

### Admin Dashboard (`admin.py`)
Complete administrative interface with FastAPI router:

- **Admin Dashboard Page**: `/admin/dashboard` endpoint for web interface
- **System Statistics**: Total users, roles, groups, and admin users
- **User CRUD Operations**: Create, read, update, and delete users
- **Role Management**: Complete role lifecycle management
- **Group Management**: Complete group lifecycle management
- **Pydantic Models**: Request/response models for all admin operations
- **Error Handling**: Comprehensive error handling and validation
- **Real-time Updates**: Dynamic interface updates without page refresh

### Profile Management (`profile.py`)
User self-service profile management:

- **Profile Information**: Display user details, roles, and groups
- **Profile Editing**: Update personal information (first name, last name, email)
- **Password Management**: Change password with current password verification
- **FastAPI Router**: Dedicated router for profile endpoints
- **Security Validation**: Ensures users can only modify their own profiles

### Tool System (`tools.py`)
Defines and implements all available tools for the Tatlock agent:

- **`web_search`**: Google Custom Search API integration for web queries
  - Searches the web for current information
  - Returns formatted search results with titles and snippets
  - Configurable search parameters and result limits

- **`find_personal_variables`**: Personal information lookup system
  - Retrieves user-specific information from their database
  - Supports custom personal data storage
  - User-scoped data access for privacy

- **`get_weather_forecast`**: OpenWeather API integration for weather data
  - Current weather and forecasts for any city
  - Supports date-specific forecasts
  - Returns detailed weather information

- **`recall_memories`**: Memory search by keyword (user-scoped)
  - Searches conversation history by keyword
  - Searches across user prompts, AI replies, and topics
  - Returns relevant conversation snippets

- **`recall_memories_with_time`**: Memory search with temporal filtering (user-scoped)
  - Natural language date parsing (e.g., "yesterday", "last week")
  - Combines keyword search with time filtering
  - Supports relative and absolute date ranges

- **`get_user_conversations`**: List all conversations for the current user
  - Returns conversation metadata and statistics
  - Includes conversation titles and activity timestamps
  - Supports pagination and sorting

- **`get_conversation_details`**: Get detailed conversation information for current user
  - Complete conversation history with timestamps
  - Topic information and metadata
  - Message counts and activity patterns

- **`search_conversations`**: Search conversations by title or content for current user
  - Full-text search across conversation content
  - Returns matching conversations with relevance scores
  - Supports complex search queries

- **`get_conversations_by_topic`**: Find conversations containing specific topics for current user
  - Topic-based conversation filtering
  - Returns conversations that discuss specific topics
  - Includes topic mention statistics

- **`get_topics_by_conversation`**: Get all topics in a specific conversation for current user
  - Lists all topics discussed in a conversation
  - Includes topic mention counts and timestamps
  - Provides conversation topic analysis

- **`get_conversation_summary`**: Get comprehensive conversation summaries for current user
  - Generates conversation summaries and key points
  - Includes topic breakdown and statistics
  - Provides conversation insights

- **`get_topic_statistics`**: Get statistics about topics across conversations for current user
  - Topic usage statistics and trends
  - Most discussed topics and patterns
  - Topic correlation analysis

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
- Safe JSON parsing with fallback handling

#### `textutils.py`
Text processing and manipulation:
- Text cleaning and formatting functions
- String manipulation utilities
- Text normalization and sanitization

#### `logging.py`
Logging configuration and utilities:
- Structured logging setup
- Log formatting and output management
- Configurable log levels and handlers

#### `timeawareness.py`
Natural language date parsing:
- **`parse_natural_date_range()`**: Converts expressions like "yesterday", "last week" to date ranges
- Supports various date formats and relative time expressions
- Returns ISO date strings for database queries
- Handles complex temporal expressions

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
- **Modern UI**: Material Design principles throughout

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
- `GET /login/test` - Debug endpoint to verify authentication (requires authentication)
- `GET /logout` - Logout page (clears session and redirects)
- `POST /logout` - Session-based logout endpoint

### Web Interface Endpoints
- `GET /chat` - Debug console page

## Tool Integration

All tools are defined in the `tools.py` module and are automatically scoped to the current user's data. The agent automatically injects the current user's username into tool calls to ensure complete data isolation and privacy.

### Tool Security
- **User Isolation**: All tools respect user boundaries and data access
- **Input Validation**: Comprehensive validation of tool parameters
- **Error Handling**: Graceful error handling for tool failures
- **API Key Management**: Secure handling of external API credentials

### Tool Performance
- **Caching**: Tool results can be cached to reduce API calls
- **Rate Limiting**: Built-in rate limiting for external API calls
- **Timeout Handling**: Proper timeout handling for external services
- **Fallback Responses**: Graceful degradation when tools are unavailable

## Security Features

### Authentication Security
- **Session Management**: Secure session handling with proper cookie settings
- **Password Security**: PBKDF2 hashing with unique salts per user
- **Session Expiration**: Configurable session timeouts
- **CSRF Protection**: Built-in CSRF protection for forms

### Authorization
- **Role-Based Access**: Fine-grained role-based permissions
- **Group Management**: Flexible group-based access control
- **Admin Protection**: Prevents deletion of critical system components
- **User Isolation**: Complete data separation between users

### Data Protection
- **Input Sanitization**: All user inputs are sanitized and validated
- **SQL Injection Prevention**: Parameterized queries throughout
- **XSS Protection**: Output encoding and sanitization
- **Secure Headers**: Proper security headers in responses

## Future Enhancements

### Planned Features
- **Advanced Tool System**: Plugin architecture for custom tools
- **Tool Analytics**: Usage tracking and optimization
- **Enhanced Security**: Two-factor authentication support
- **API Rate Limiting**: Per-user API rate limiting
- **Audit Logging**: Comprehensive audit trail for all actions

### Performance Improvements
- **Tool Result Caching**: Intelligent caching of tool results
- **Database Optimization**: Enhanced database performance
- **Static Asset Optimization**: Improved asset delivery
- **API Response Optimization**: Faster API response times