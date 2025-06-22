# Stem

**Status: Production Ready - Core Infrastructure & Authentication**

The Stem module provides shared utilities, tool definitions, session-based authentication system, admin dashboard, and static file serving for Tatlock. Named after the brain stem responsible for basic life functions and autonomic processes, this module contains essential helper functions, tool implementations, and infrastructure components used across the system.

## ✅ **Core Features**

### 🔐 **Authentication & Security** (`security.py`)
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

### 🛠️ **Admin Dashboard** (`admin.py`)
Complete administrative interface with FastAPI router:

- **Admin Dashboard Page**: `/admin/dashboard` endpoint for web interface
- **System Statistics**: Total users, roles, groups, and admin users
- **User CRUD Operations**: Create, read, update, and delete users
- **Role Management**: Complete role lifecycle management
- **Group Management**: Complete group lifecycle management
- **Pydantic Models**: Request/response models for all admin operations
- **Error Handling**: Comprehensive error handling and validation
- **Real-time Updates**: Dynamic interface updates without page refresh

### 👤 **Profile Management** (`profile.py`)
User self-service profile management:

- **Profile Information**: Display user details, roles, and groups
- **Profile Editing**: Update personal information (first name, last name, email)
- **Password Management**: Change password with current password verification
- **FastAPI Router**: Dedicated router for profile endpoints
- **Security Validation**: Ensures users can only modify their own profiles

### 🧰 **Tool System** (`tools.py`)
Defines and implements all available tools for the Tatlock agent:

#### **External API Tools**
- **`web_search`**: Google Custom Search API integration for web queries
- **`get_weather_forecast`**: OpenWeather API integration for weather data

#### **Memory Tools** (imported from hippocampus/tools/)
- **`find_personal_variables`**: Personal information lookup system
- **`recall_memories`**: Memory search by keyword (user-scoped)
- **`recall_memories_with_time`**: Memory search with temporal filtering (user-scoped)
- **`get_user_conversations`**: List all conversations for the current user
- **`get_conversation_details`**: Get detailed conversation information for current user
- **`search_conversations`**: Search conversations by title or content for current user
- **`get_conversations_by_topic`**: Find conversations containing specific topics for current user
- **`get_topics_by_conversation`**: Get all topics in a specific conversation for current user
- **`get_conversation_summary`**: Get comprehensive conversation summaries for current user
- **`get_topic_statistics`**: Get statistics about topics across conversations for current user

#### **Visual Tools** (imported from occipital/)
- **`screenshot_from_url`**: Take screenshots of web pages
- **`analyze_file`**: Analyze and interpret image files

### 📁 **Static File Serving** (`static.py`)
Handles web interface and static file management:

- **`mount_static_files()`**: Mounts static files directory to FastAPI
- **`get_admin_page()`**: Returns the admin dashboard HTML
- **`get_profile_page()`**: Returns the user profile HTML
- **`get_chat_page()`**: Returns the debug console HTML
- **`get_login_page()`**: Returns the login page HTML

### 📊 **Data Models** (`models.py`)
Pydantic models for API requests and responses:

- **Chat Models**: ChatRequest, ChatResponse, ChatMessage
- **User Models**: CreateUserRequest, UpdateUserRequest, UserResponse
- **Admin Models**: AdminStatsResponse, CreateRoleRequest, RoleResponse
- **Group Models**: CreateGroupRequest, UpdateGroupRequest, GroupResponse
- **Profile Models**: PasswordChangeRequest

## 🎨 **Web Interface Components**

### **HTML Templates** (`templates/`)
Jinja2-based server-side templating system:

- **`base.html`**: Base layout template with navigation and common elements
- **`login.html`**: Session-based login page
- **`chat.html`**: Debug console with JSON logging
- **`profile.html`**: User profile management interface
- **`admin.html`**: Complete admin dashboard with user, role, and group management

### **Reusable Components** (`templates/components/`)
- **`header.html`**: Site header with navigation and user menu
- **`navigation.html`**: Left sidebar navigation
- **`chat_sidebar.html`**: Chat interface sidebar
- **`modal.html`**: Reusable modal dialog component
- **`form.html`**: Form component with validation
- **`snackbar.html`**: Notification system component

### **Styling** (`static/`)
- **`style.css`**: Consolidated CSS with dark/light mode support
- **`material-icons.css`**: Material Design Icons font definitions
- **`json-highlight.css`**: JSON syntax highlighting styles
- **Responsive Design**: Works on desktop and mobile devices
- **Theme System**: CSS variables for consistent theming
- **Modern UI**: Material Design principles throughout

### **JavaScript Modules** (`static/js/`)
- **`common.js`**: Shared functionality (snackbar, dark mode, chat sidepane)
- **`admin.js`**: Admin dashboard functionality
- **`profile.js`**: Profile management functionality
- **`chat.js`**: Chat interface with voice input support
- **`debug.js`**: Debug console functionality

### **Static Assets** (`static/`)
- **`fonts/`**: Material Icons font files for offline use
- **`favicon/`**: Complete favicon and app icon set
- **`images/`**: Logo and branding assets
- **`js/`**: Modular JavaScript files

## 🔧 **Utility Modules**

### **JSON Utilities** (`jsonutils.py`)
JSON manipulation and validation helpers:
- JSON serialization/deserialization utilities
- Error handling for JSON operations
- Safe JSON parsing with fallback handling

### **Text Utilities** (`textutils.py`)
Text processing and manipulation:
- Text cleaning and formatting functions
- String manipulation utilities
- Text normalization and sanitization

### **Logging** (`logging.py`)
Logging configuration and utilities:
- Structured logging setup with FastAPI integration
- Log formatting and output management
- Configurable log levels and handlers
- **`get_logger()`**: Standardized logger creation for all modules

### **Time Awareness** (`timeawareness.py`)
Natural language date parsing:
- **`parse_natural_date_range()`**: Converts expressions like "yesterday", "last week" to date ranges
- Supports various date formats and relative time expressions
- Returns ISO date strings for database queries
- Handles complex temporal expressions

### **HTML Controller** (`htmlcontroller.py`)
Jinja2 template management:
- **`get_template_manager()`**: Creates and configures Jinja2 environment
- **`render_template()`**: Renders templates with context data
- **Template Loading**: Automatic template discovery and loading
- **Component System**: Support for reusable template components

## 🚀 **Installation Support** (`installation/`)
Database setup and initialization utilities:

- **`database_setup.py`**: Creates and populates system.db and user longterm.db templates
- **`create_system_db_tables()`**: Shared authentication database initialization
- **`create_longterm_db_tables()`**: User memory database template initialization
- **`create_default_roles()`**: Sets up default user roles
- **`create_default_groups()`**: Sets up default user groups
- **`create_default_rise_and_shine()`**: Populates system prompts (copied to each user's database)

## 🌐 **API Endpoints**

### **Admin Endpoints** (Require Admin Role)
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

### **Profile Endpoints** (Require Authentication)
- `GET /profile` - User profile page
- `PUT /profile` - Update profile information
- `PUT /profile/password` - Change password

### **Authentication Endpoints**
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - Logout user

### **Chat Endpoints**
- `GET /chat` - Debug console page
- `POST /chat` - Process chat messages

## 🧪 **Testing**

### **Unit Tests**
```bash
# Run stem-specific tests
python -m pytest tests/test_stem_*.py -v
```

### **Integration Tests**
```bash
# Test authentication and admin functionality
python -m pytest tests/test_security.py -v
python -m pytest tests/test_admin_frontend.py -v
```

## 📈 **Performance Considerations**

- **Template Caching**: Jinja2 templates are cached for performance
- **Static File Serving**: Efficient static file delivery with proper headers
- **Session Management**: Optimized session storage and retrieval
- **Database Connections**: Connection pooling for database operations
- **Tool Loading**: Lazy loading of tool modules for faster startup

## 🔒 **Security Considerations**

- **Password Hashing**: PBKDF2 with unique salts for each user
- **Session Security**: Secure cookie-based sessions with proper expiration
- **Input Validation**: Comprehensive input validation and sanitization
- **SQL Injection Prevention**: All database queries use parameterized statements
- **XSS Protection**: Template escaping and input sanitization
- **CSRF Protection**: Session-based CSRF protection
- **Access Control**: Role-based and group-based permission checking

## ⚠️ **Error Handling**

- **Authentication Errors**: Graceful handling of login failures
- **Permission Errors**: Clear error messages for unauthorized access
- **Database Errors**: Comprehensive error logging and fallback responses
- **Template Errors**: Graceful handling of template rendering failures
- **Tool Errors**: Standardized error responses for all tools

## 🔮 **Future Enhancements**

### **Planned Features**
- **Two-Factor Authentication**: Additional security layer
- **API Rate Limiting**: Prevent abuse of API endpoints
- **Audit Logging**: Comprehensive audit trail for all operations
- **Advanced Permissions**: Fine-grained permission system
- **User Sessions**: Multiple concurrent session support

### **Performance Improvements**
- **Template Optimization**: Further template caching and optimization
- **Static Asset Optimization**: Asset compression and CDN integration
- **Database Optimization**: Additional database indexing and query optimization
- **Caching Layer**: Redis-based caching for frequently accessed data

## 📚 **Related Documentation**

- **[README.md](../README.md)** - General overview and installation
- **[developer.md](../developer.md)** - Developer guide and practices
- **[moreinfo.md](../moreinfo.md)** - In-depth technical information
- **[cortex/readme.md](../cortex/readme.md)** - Core agent logic documentation
- **[hippocampus/readme.md](../hippocampus/readme.md)** - Memory system documentation
- **[parietal/readme.md](../parietal/readme.md)** - Hardware monitoring and performance