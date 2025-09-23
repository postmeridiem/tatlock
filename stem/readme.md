# Stem

**Status: Production Ready - Core Infrastructure & Authentication**

The Stem module provides authentication, admin dashboard, tool registration, static file serving, and shared utilities for Tatlock. It is the backbone for user management, session security, and system-wide services.

## Core Features

- Session-based authentication and user management
- Role and group management
- Admin dashboard and profile management
- Tool registration and dispatch (see AGENTS.md for tool patterns)
- Static file and template serving
- Shared utility modules (logging, text, JSON, time awareness)

## Integration

- All authentication and admin endpoints are routed through Stem
- Tools are registered and dispatched via Stem, following the patterns in AGENTS.md
- Static assets and templates are managed here for the web interface

## Standards & Patterns

- All coding, tool, and security standards are defined in [AGENTS.md](../AGENTS.md). Refer to it for:
  - Tool implementation and registration
  - Logging and error handling
  - Pydantic models and validation
  - Security and user isolation

## API & Endpoints

- Admin: `/admin/dashboard`, `/admin/users`, `/admin/roles`, `/admin/groups`, `/admin/tools`, `/admin/settings`
- Profile: `/profile`
- Static: `/static/`, `/templates/`

## See Also

- [Developer Guide](../AGENTS.md) – All standards and patterns
- [Troubleshooting](../troubleshooting.md)
- [Module Docs](../README.md)

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
- **Tools Management**: Centralized registry for all system tools, enable/disable, view details
- **System Settings**: Categorized global configuration, live updates, model management
- **UI/UX Standards**: Right-aligned "Add New" buttons above section headers for all admin tables, consistent section header underline, responsive design
- **Pydantic Models**: Request/response models for all admin operations
- **Error Handling**: Comprehensive error handling and validation
- **Real-time Updates**: Dynamic interface updates without page refresh

### 👤 **Profile Management** (`profile.py`)

User self-service profile management:

- **Profile Information**: Display user details, roles, and groups
- **Profile Editing**: Update personal information (first name, last name, email)
- **Password Management**: Change password with current password verification
- **Memory Management**: Search, view, and purge conversation history
- **FastAPI Router**: Dedicated router for profile endpoints
- **Security Validation**: Ensures users can only modify their own profiles

### 🧠 **Tool System** (`tools.py`)

Defines and implements all available tools for the Tatlock agent:

- **External API Tools**: Web search, weather, etc.
- **Memory Tools**: Conversation and memory analytics, export, cleanup, insights
- **Visual Tools**: Screenshot, file analysis

### 📄 **Static File Serving & Templates** (`static.py`)

Handles web interface and static file management:

- **Template Naming**: All main page templates use the `page.*.html` pattern (e.g., `page.admin.html`, `page.profile.html`, `page.conversation.html`, `page.login.html`)
- **Component System**: Reusable components in `templates/components/` (header, navigation, chat sidebar, modal, form, snackbar)
- **Modern UI**: Material Design principles, dark/light mode, responsive design
- **Static Assets**: Fonts, favicons, images, modular JS files

### 💻 **JavaScript Modules** (`static/js/`)

- **Naming Conventions**:
  - Page-specific scripts: `page.[pagename].js` (e.g., `page.admin.js`, `page.profile.js`, `page.login.js`, `page.conversation.js`)
  - Component scripts: `component.[componentname].js` (e.g., `component.chatbar.js`)
  - Plugin scripts: `plugin.[library].js` (e.g., `plugin.marked.min.js`)
- **Key Modules**:
  - `common.js`: Shared functionality (snackbar, theme, anchor links, etc.)
  - `page.admin.js`: Admin dashboard logic (users, roles, groups, tools, settings)
  - `page.profile.js`: Profile management (info, password, memory)
  - `page.conversation.js`: Main conversation interface, system info, benchmarks
  - `page.login.js`: Login page logic
  - `component.chatbar.js`: Chat sidebar functionality (used on all main pages)
- **Removed/Merged**: Old files like `chat.js`, `debug.js`, and `sidebar_chat.js` have been removed or merged into the new structure.

### 🖼️ **Static Assets** (`static/`)

- **Fonts**: Material Icons font files
- **Favicons**: Complete favicon and app icon set
- **Images**: Logo and branding assets
- **JS**: Modular JavaScript files

## 🧰 **Utility Modules**

### **JSON Utilities** (`jsonutils.py`)

- JSON serialization/deserialization utilities
- Error handling for JSON operations
- Safe JSON parsing with fallback handling

### **Text Utilities** (`textutils.py`)

- Text cleaning and formatting functions
- String manipulation utilities
- Text normalization and sanitization

### **Logging** (`logging.py`)

- Structured logging setup with FastAPI integration
- Log formatting and output management
- Configurable log levels and handlers
- `get_logger()`: Standardized logger creation for all modules

### **Time Awareness** (`timeawareness.py`)

- Natural language date parsing and range extraction
- Supports various date formats and relative time expressions
- Returns ISO date strings for database queries

### **HTML Controller** (`htmlcontroller.py`)

- Jinja2 template management and rendering
- Automatic template/component discovery and loading

## 🚀 **Installation Support** (`installation/`)

- Database setup and initialization utilities
- Automated tools backup and restore

---

**For all coding standards, architectural patterns, and development workflows, see [AGENTS.md](../AGENTS.md).**

## 🎨 **Web Interface Components**

### **HTML Templates** (`templates/`)

Jinja2-based server-side templating system:

- **`page.login.html`**: Session-based login page
- **`page.conversation.html`**: Main conversation interface
- **`page.profile.html`**: User profile management interface
- **`page.admin.html`**: Complete admin dashboard with user, role, and group management

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
- **`page.admin.js`**: Admin dashboard functionality
- **`page.profile.js`**: Profile management functionality
- **`chat.js`**: Chat interface with voice input support
- **`debug.js`**: Debug console functionality
- **Page-specific scripts**: All scripts that are only used for a single page must follow the naming pattern `page.[pagename].js` (e.g., `page.admin.js`, `page.profile.js`, `page.login.js`, `page.conversation.js`). This ensures clarity and consistency across the codebase.

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

### **Conversation Endpoints**

- `GET /conversation` - Conversation page
- `POST /cortex` - Process conversation messages

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
- **[AGENTS.md](../AGENTS.md)** - Developer guide and practices
- **[moreinfo.md](../moreinfo.md)** - In-depth technical information
- **[cortex/readme.md](../cortex/readme.md)** - Core agent logic documentation
- **[hippocampus/readme.md](../hippocampus/readme.md)** - Memory system documentation
- **[parietal/readme.md](../parietal/readme.md)** - Hardware monitoring and performance

## 🧑‍💻 User Context and Authentication

Tatlock uses a global user variable system for all authentication and user info access. All memory and user operations in the Stem module are type-safe and use the current user context, which is set automatically for each request.

- The current user is available as a Pydantic `UserModel` via:

  ```python
  from stem.security import current_user
  user = current_user
  if user is None:
      raise HTTPException(status_code=401, detail="Not authenticated")
  # Access fields as attributes, e.g. user.username
  ```

- All memory and recall functions are scoped to the current user, ensuring privacy and isolation.
- When passing the user to templates or tools, use `user.model_dump()` to convert to a dict if needed.
- See the [AGENTS.md](../AGENTS.md) for full details and examples of the global user variable pattern.

**Note:** All legacy patterns using `current_user` as a dict have been removed. Always use the global UserModel variable for user access in new code.

## Core Components

### Authentication & Security (`security.py`)

Comprehensive user management and security system with session-based authentication:

- **User Management**: Create, authenticate, update, and delete users
- **Password Security**: PBKDF2 hashing with unique salts for each user
- **Session Management**: Secure cookie-based session authentication
- **Role Management**: Create, assign, and manage user roles (user, admin, moderator)
- **Group Management**: Create, assign, and manage user groups (users, admins, moderators)
- **Access Control**: Role-based and group-based permission checking
- **Global User Context**: Access current user via `current_user` global variable

### Development Guidelines

1. **Database Changes**: Use migration system for schema updates
2. **User Context**: Access user data via `current_user` global variable
3. **Type Safety**: Use Pydantic models for data validation
4. **Testing**: Write comprehensive tests with temporary databases
5. **Documentation**: Update relevant documentation

## 🔒 **Security Features**

### **Password Security**

- **Hashing**: bcrypt with configurable rounds
- **Salting**: Unique salt per password
- **Separation**: Password data in separate table
- **Validation**: Pydantic models for type safety

### **Session Security**

- **Secure Cookies**: HttpOnly, Secure, SameSite attributes
- **Session Cleanup**: Proper logout handling
- **Context Isolation**: Thread-local user storage

### **Authorization**

- **Role-Based**: Fine-grained permissions via roles
- **Group-Based**: User grouping for bulk operations
- **Middleware**: Automatic role checking
- **Dependencies**: FastAPI dependency injection

## 🔧 **Database Operations**

### **User CRUD Operations**

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

### **Role and Group Management**

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

## 🧪 **Testing**

### **Database Tests**

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

### **Migration Tests**

Tests verify migration process works correctly:

- **Schema Migration**: Old schema → New schema
- **Data Preservation**: Existing data maintained
- **Idempotency**: Multiple runs don't cause issues
- **Rollback Safety**: Data integrity verified
