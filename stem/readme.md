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

## 🧑‍💻 User Context and Authentication

Tatlock uses a context-based, per-request user model for all authentication, admin, and profile operations, as described in the main developer documentation. All user access in the Stem module is type-safe and uses the current user context, which is set automatically for each request.

- The current user is available as a Pydantic `UserModel` via:
  ```python
  from stem.current_user_context import get_current_user_ctx
  user = get_current_user_ctx()
  if user is None:
      raise HTTPException(status_code=401, detail="Not authenticated")
  # Access fields as attributes, e.g. user.username
  ```
- All admin, profile, and authentication operations use the current user context for security and personalization.
- When passing the user to templates or tools, use `user.model_dump()` to convert to a dict if needed.
- See the [developer.md](../developer.md) for full details and examples of the context-based user pattern.

**Note:** All legacy patterns using `current_user` as a dict have been removed. Always use the context-based UserModel for user access in new code.

## Core Components

### Security Management (`security.py`)

Handles user authentication, authorization, and password management.

#### Key Features

- **User Authentication**: Secure login with bcrypt password hashing
- **Password Management**: Passwords stored in separate `passwords` table for security
- **Role-Based Access Control**: Fine-grained permissions via roles and groups
- **Session Management**: Secure session handling with proper cleanup

#### Password Table Migration

The password data has been migrated from the `users` table to a separate `passwords` table:

- **Old Schema**: `users` table contained `password_hash` and `salt` columns
- **New Schema**: `passwords` table with foreign key relationship to `users` table
- **Benefits**: Better separation of concerns, improved security, easier password management

#### Database Schema

```sql
-- Users table (no longer contains password data)
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Passwords table (separate for security)
CREATE TABLE passwords (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
);
```

### User Context Management (`current_user_context.py`)

Provides context-local user storage to avoid passing user data through function parameters.

#### Usage

```python
from stem.current_user_context import get_current_user_ctx, UserModel

# In FastAPI dependency
def get_current_user(request: Request):
    # ... authentication logic ...
    user_model = UserModel(
        username=user_data['username'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        email=user_data['email'],
        roles=roles,
        groups=groups
    )
    set_current_user_ctx(user_model)
    return user_model

# In endpoint functions
def some_endpoint(_: None = Depends(get_current_user)):
    user = get_current_user_ctx()
    # Access user attributes directly
    username = user.username
    roles = user.roles
```

### Database Setup (`installation/`)

Handles database initialization and migrations.

#### Migration System

The migration system automatically handles database schema updates:

- **Automatic Detection**: Detects if the old schema exists (users table with `password_hash` and `salt` columns)
- **Data Preservation**: Maintains existing data during schema changes
- **Idempotent**: Safe to run multiple times
- **Tracking**: Records applied migrations in `migrations` table

#### Key Functions

- `create_system_db_tables()`: Creates system database tables
- `create_longterm_db_tables()`: Creates user-specific memory databases
- `check_and_run_migrations()`: Runs pending migrations
- `migrate_users_table()`: Migrates password data to separate table

### Password Management Tools

#### Password Reset Script (`reset_password.sh`)

A comprehensive CLI script for resetting user passwords with the same visual style as the installation script.

**Features:**
- **Interactive Interface**: Prompts for username and password with confirmation
- **Password Validation**: Checks password strength and confirms input
- **Secure Hashing**: Uses bcrypt with proper salt generation
- **Database Verification**: Confirms password update and displays user info
- **Error Handling**: Comprehensive error checking and user-friendly messages

**Usage:**
```bash
./stem/reset_password.sh
```

**Process:**
1. **Prerequisites Check**: Verifies virtual environment and database exist
2. **User Input**: Prompts for username and validates existence
3. **Password Input**: Securely prompts for new password with confirmation
4. **Database Update**: Updates password hash in `passwords` table
5. **Verification**: Confirms password was updated correctly
6. **User Info Display**: Shows updated user information

**Security Features:**
- Passwords never logged or stored in plain text
- Uses bcrypt with secure salt generation
- Validates password strength (minimum 8 characters with warning)
- Records password update timestamps
- Handles both new and existing password entries

**Example Output:**
```
══════════════════════════════════════════════════════════════════════════════════════════
                        Tatlock Password Reset Script                                     
                    Reset user passwords in the system database                          
══════════════════════════════════════════════════════════════════════════════════════════

[1/5] Checking if user exists in database...
[✓] User 'admin' found in database

[2/5] Setting new password...
Enter new password: 
Confirm new password: 
[✓] Password confirmed

[3/5] Updating password in database...
[✓] Password updated successfully

[4/5] Verifying password update...
[✓] Password verification successful

[5/5] Retrieving updated user information...
[✓] User information retrieved

Updated User Information:
──────────────────────────────────────────────────────────────────────────────────
  Username:         admin
  Name:             Admin User
  Email:            admin@example.com
  Password Updated: 2024-01-01 12:00:00
──────────────────────────────────────────────────────────────────────────────────

══════════════════════════════════════════════════════════════════════════════════════════
                                    Password Reset Complete!                              
══════════════════════════════════════════════════════════════════════════════════════════
```

#### Database Inspection Script (`scripts/check_user_passwords.py`)

A Python script to inspect user and password data in the database.

**Usage:**
```bash
python scripts/check_user_passwords.py <username> [db_path]
```

**Features:**
- **User Verification**: Checks if user exists in `users` table
- **Password Inspection**: Shows password hash and salt from `passwords` table
- **Database Flexibility**: Supports custom database paths
- **Error Handling**: Graceful handling of missing users or database errors

**Example Output:**
```
Checking user 'admin' in database: hippocampus/system.db

[users] table entry:
  username:   admin
  first_name: Admin
  last_name:  User
  email:      admin@example.com
  created_at: 2024-01-01 12:00:00

[passwords] table entry:
  username:      admin
  password_hash: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqQKqK
  salt:          $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqQKqK
  created_at:    2024-01-01 12:00:00
```

## API Endpoints

### Authentication

- `POST /login`: User login
- `POST /logout`: User logout
- `POST /register`: User registration

### User Management

- `GET /admin/users`: List all users (admin only)
- `POST /admin/users`: Create new user (admin only)
- `PUT /admin/users/{username}`: Update user (admin only)
- `DELETE /admin/users/{username}`: Delete user (admin only)

### Profile Management

- `GET /profile`: Get user profile
- `PUT /profile`: Update user profile
- `PUT /profile/password`: Change password

## Security Features

### Password Security

- **Hashing**: bcrypt with configurable rounds
- **Salting**: Unique salt per password
- **Separation**: Password data in separate table
- **Validation**: Pydantic models for type safety

### Session Security

- **Secure Cookies**: HttpOnly, Secure, SameSite attributes
- **Session Cleanup**: Proper logout handling
- **Context Isolation**: Thread-local user storage

### Authorization

- **Role-Based**: Fine-grained permissions via roles
- **Group-Based**: User grouping for bulk operations
- **Middleware**: Automatic role checking
- **Dependencies**: FastAPI dependency injection

## Database Operations

### User CRUD Operations

```python
from stem.security import SecurityManager

security = SecurityManager()

# Create user
success = security.create_user(
    username='testuser',
    first_name='Test',
    last_name='User',
    password='securepassword',
    email='test@example.com'
)

# Authenticate user
user_data = security.authenticate_user('testuser', 'securepassword')

# Update user
success = security.update_user(
    username='testuser',
    first_name='Updated',
    password='newpassword'
)

# Delete user
success = security.delete_user('testuser')
```

### Role and Group Management

```python
# Add user to role
security.add_user_to_role('testuser', 'admin')

# Check user roles
roles = security.get_user_roles('testuser')
has_admin = security.user_has_role('testuser', 'admin')

# Add user to group
security.add_user_to_group('testuser', 'moderators')

# Check user groups
groups = security.get_user_groups('testuser')
has_group = security.user_has_group('testuser', 'moderators')
```

## Testing

### Database Tests

Tests use temporary SQLite databases for isolation:

```python
def test_user_creation():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        security = SecurityManager()
        security.db_path = db_path
        create_system_db_tables(db_path)
        
        # Test user creation
        success = security.create_user('testuser', 'Test', 'User', 'password')
        assert success is True
        
        # Verify in both tables
        user_data = security.get_user_by_username('testuser')
        assert user_data is not None
        
        # Check password table
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM passwords WHERE username = ?", ('testuser',))
        password_exists = cursor.fetchone() is not None
        assert password_exists
        conn.close()
        
    finally:
        if os.path.exists(db_path):
            os.unlink(db_path)
```

### Migration Tests

Tests verify migration process works correctly:

- **Schema Migration**: Old schema → New schema
- **Data Preservation**: Existing data maintained
- **Idempotency**: Multiple runs don't cause issues
- **Rollback Safety**: Data integrity verified

## Development Guidelines

### Adding New Features

1. **Database Changes**: Use migration system for schema updates
2. **User Context**: Access user data via `get_current_user_ctx()`
3. **Type Safety**: Use Pydantic models for data validation
4. **Testing**: Write comprehensive tests with temporary databases
5. **Documentation**: Update relevant documentation

### Security Considerations

- **Password Storage**: Always use separate passwords table
- **User Context**: Validate user data in dependencies
- **Input Validation**: Use Pydantic models for all inputs
- **Session Management**: Proper session cleanup on logout
- **Authorization**: Check roles and permissions appropriately

### Database Migrations

When adding new database changes:

1. **Schema Updates**: Modify `SYSTEM_DB_SCHEMA` in `database_setup.py`
2. **Migration Function**: Create migration function
3. **Migration Tracking**: Add migration record to `migrations` table
4. **Testing**: Write tests for migration process
5. **Documentation**: Update schema documentation

### Password Management Best Practices

1. **Use Reset Script**: Always use `reset_password.sh` for password changes
2. **Inspect Database**: Use `check_user_passwords.py` for troubleshooting
3. **Migration Safety**: Test migrations on backup databases first
4. **Security Logging**: Monitor authentication attempts and failures
5. **Regular Audits**: Periodically check for orphaned password entries