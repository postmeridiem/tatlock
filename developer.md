# Developer Guide

This guide contains developer-specific information for working with Tatlock, including logging, debugging, performance monitoring, and development practices.

## AI Instructions

This section provides guidelines for AI assistants (like Cursor, GitHub Copilot, Claude, GPT, etc.) contributing to the Tatlock project.

**Primary Directive**: Always adhere to the coding standards, patterns, and development practices described in this file. If a request conflicts with these standards, ask for clarification or permission before deviating.

### Core Workflows
- **Versioning**: When asked to update the application version, you must follow the full "Versioning and Releases" workflow. This includes updating `changelog.md` with all changes since the last version, committing it with the `pyproject.toml` update, and creating a Git tag.
- **Troubleshooting**: When a fix resolves a common installation or runtime issue, suggest an addition to `troubleshooting.md` to help future users.
- **Testing**: All new code, whether adding features or fixing bugs, must be accompanied by corresponding tests to ensure correctness and prevent regressions.
- **Code Organization**: Keep the codebase clean and maintainable. If code is used in multiple places, refactor it into a new shared file, following the Don't Repeat Yourself (DRY) principle. When creating new files, place them in the appropriate module directory, adhering to the existing filesystem structure patterns.

### General Guidance
1.  **Always Include Standards**: When using coding AI assistants, always include the Tatlock coding standards from this `developer.md` file as part of your prompt.
2.  **Reference Specific Sections**: Reference relevant sections like "Python Coding Standards", "JavaScript Coding Standards", or "Security Standards" based on the task.
3.  **Validate Generated Code**: Review AI-generated code to ensure it follows our established patterns and conventions.
4.  **Update Standards**: If AI suggests improvements to our coding standards, evaluate and update this document accordingly.

**Example AI Prompt:**
```
Please help me implement [specific feature] following the Tatlock coding standards:

Python standards:
- Use type hints for all functions (Python 3.10+ syntax)
- Include comprehensive docstrings
- Use structured logging with logger = logging.getLogger(__name__)
- Follow database patterns with proper error handling
- Use Pydantic models for input validation

Security standards:
- Use parameterized queries only
- Validate all inputs
- Implement proper user isolation

[Your specific request here]
```

## Frontend Development

### Jinja2 Templating System

Tatlock uses Jinja2 for server-side templating with shared components and layouts. This provides true server-side rendering instead of client-side string replacement.

#### Architecture

- **Template Manager**: `stem/htmlcontroller.py` manages Jinja2 environment and template rendering
- **Base Layout**: `stem/templates/base.html` provides foundation for all pages
- **Shared Components**: Reusable UI components in `stem/templates/components/`
- **Page Templates**: Individual page templates in `stem/templates/`

#### Key Components

```python
from stem.htmlcontroller import render_template, render_page, get_common_context

# Get common context with user info
context = get_common_context(request, user)

# Render template as string
html = render_template('login.html', context)

# Render template as HTMLResponse
response = render_page('login.html', context)
```

#### Template Structure

```
stem/templates/
├── base.html                 # Base layout template
├── login.html               # Login page template
├── chat.html                # Debug console template
├── profile.html             # User profile template
├── admin.html               # Admin dashboard template
├── components/              # Reusable components
│   ├── header.html          # Page header component
│   ├── footer.html          # Page footer component
│   ├── chat_sidebar.html    # Chat sidebar component
│   ├── navigation.html      # Sidebar navigation component
│   ├── modal.html           # Modal dialog component
│   ├── form.html            # Form component
│   └── snackbar.html        # Notification component
└── README.md               # Template documentation
```

#### Template Variables

Common context variables available in all templates:

- `app_name`: Application name (default: "Tatlock")
- `app_version`: Application version (default: "3.0.0")
- `user`: Current user data (if authenticated)
- `is_authenticated`: Whether user is logged in
- `is_admin`: Whether user has admin role
- `hide_header`: Skip header (for login page)
- `hide_footer`: Skip footer (for login page)
- `show_chat_sidebar`: Include chat sidebar
- `welcome_message`: Chat sidebar welcome message

#### Creating New Pages

1. **Create Template**: Add new template file in `stem/templates/`
2. **Extend Base**: Use `{% extends "base.html" %}` for consistent layout
3. **Set Variables**: Use `{% set variable = value %}` for page-specific settings
4. **Add Content**: Define content in `{% block content %}` blocks
5. **Update Backend**: Add route in appropriate module (main.py, admin.py, etc.)

#### Adding Components

1. **Create Component**: Add new component in `stem/templates/components/`
2. **Include in Templates**: Use `{% include 'components/component.html' %}`
3. **Pass Context**: Use `{% with variable = value %}` for component-specific data

#### Benefits

- **Server-side Rendering**: True server-side includes, not client-side replacement
- **Shared Components**: Reusable UI components across pages
- **Consistent Layout**: Base template ensures uniform structure
- **Dynamic Content**: Context variables for personalized content
- **Maintainable**: Centralized template management
- **Type Safety**: Template variables are properly typed
- **Performance**: Templates are compiled and cached

For detailed template documentation, see `stem/templates/README.md`.

## Logging & Debugging

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
    format='%(levelname)s:\t  %(name)s - %(message)s %(asctime)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
    ]
)
```

**Note**: The actual format used in Tatlock is:
- `%(levelname)s:\t  %(name)s - %(message)s %(asctime)s`
- This places the timestamp at the end of the log message
- Uses tab characters for alignment
- Includes the module name for better debugging context

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

## Development Practices

### Versioning and Releases

This project uses **Semantic Versioning (SemVer)** and a `changelog.md` to track changes. Adhering to this process is crucial for maintaining a clear and predictable development cycle.

**Single Source of Truth**: The official version number is stored in `pyproject.toml` in the project root. This is the **only** place the version should be updated.

#### Release Workflow

When preparing a new release, follow these steps:

1.  **Update the Changelog**: Before bumping the version, you must update `changelog.md`.
    *   Create a new release section (e.g., `## [0.2.0] - YYYY-MM-DD`).
    *   Move all changes from the `[Unreleased]` section to this new version.
    *   **Separate changes by type**: Place major new features under `### Added` or `### Changed`, while smaller bugfixes go under `### Fixed`. This separation is important for release notes.

2.  **Update the Version**: Modify the `version` field in `pyproject.toml`.

3.  **Commit the Changes**: Commit both `changelog.md` and `pyproject.toml` together.
    ```bash
    git add changelog.md pyproject.toml
    git commit -m "Bump version to 0.2.0"
    ```

4.  **Tag the Release**: Create an annotated Git tag for the new version.
    ```bash
    git tag -a v0.2.0 -m "Release version 0.2.0"
    ```

5.  **Push to GitHub**: Push your commits and the new tag to the remote repository.
    ```bash
    git push origin main --tags
    ```

### Code Organization

- **Brain-Inspired Design**: Codebase organized into modules inspired by brain regions

### Tool Organization

Tatlock follows a modular tool organization pattern where each tool is implemented in its own file within the appropriate brain module. **Tools belong in the root of their respective modules, not in subdirectories.** This promotes maintainability, testability, and clear separation of concerns.

#### Tool File Structure

```
cerebellum/
├── web_search_tool.py      # Web search functionality
└── weather_tool.py         # Weather forecast functionality

hippocampus/
├── find_personal_variables_tool.py
├── recall_memories_tool.py
├── recall_memories_with_time_tool.py
├── get_conversations_by_topic_tool.py
├── get_topics_by_conversation_tool.py
├── get_conversation_summary_tool.py
├── get_topic_statistics_tool.py
├── get_user_conversations_tool.py
├── get_conversation_details_tool.py
├── search_conversations_tool.py
├── database.py             # Database access functions
├── recall.py               # Memory recall functions
└── remember.py             # Memory storage functions

occipital/
├── take_screenshot_from_url_tool.py  # Screenshot and analysis tools
├── website_tester.py                 # Website testing functionality
└── visual_analyzer.py                # Visual analysis functionality

stem/
└── tools.py                # Tool registration and dispatcher
```

#### Tool Implementation Pattern

Each tool file follows this structure:

```python
# cerebellum/web_search_tool.py
import requests
import logging
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID

def execute_web_search(query: str) -> dict:
    """
    Perform a web search using the Google Custom Search JSON API.
    Args:
        query (str): The search query.
    Returns:
        dict: Status and search results or error message.
    """
    # Tool implementation here
    pass
```

#### Tool Registration

All tools are registered in `stem/tools.py`:

```python
# stem/tools.py
from cerebellum.web_search_tool import execute_web_search
from cerebellum.weather_tool import execute_get_weather_forecast
from hippocampus.find_personal_variables_tool import execute_find_personal_variables
# ... other imports

# Tool definitions for LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Perform a web search using Google Custom Search API.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to send to the search engine."
                    }
                },
                "required": ["query"],
            },
        },
    },
    # ... other tool definitions
]

# Tool dispatcher
AVAILABLE_TOOLS = {
    "web_search": execute_web_search,
    "find_personal_variables": execute_find_personal_variables,
    # ... other tool mappings
}
```

#### Module Assignment Guidelines

- **Cerebellum**: External API tools (web search, weather, etc.)
- **Hippocampus**: Memory and database-related tools
- **Occipital**: Visual processing and screenshot tools
- **Stem**: Core system tools and tool registration

#### Benefits

- **Modularity**: Each tool is self-contained and can be developed/tested independently
- **Maintainability**: Easy to locate and modify specific tool functionality
- **Testability**: Individual tools can be unit tested in isolation
- **Scalability**: New tools can be added without cluttering existing files
- **Clear Dependencies**: Each tool file only imports what it needs
- **Brain-Inspired Organization**: Tools are grouped by functional area

#### Adding New Tools (Database-Driven)

As of version 3.0, Tatlock's tool system is database-driven, allowing for dynamic management of tools without code changes. Here's the new process for registering a tool:

#### Step 1: Create the Tool Function

First, create the core Python function for your tool in its appropriate module. For example, a new tool for the `cerebellum` would go in `cerebellum/my_new_tool.py`.

```python
# cerebellum/my_new_tool.py
def execute_my_new_tool(parameter_one: str, parameter_two: bool) -> dict:
    """
    This is the description of what my new tool does.
    It will be stored in the database.
    """
    # Your tool's logic here...
    return {"status": "success", "result": f"Used {parameter_one}"}
```

#### Step 2: Add the Tool to the Database Schema

Next, you must add the tool's definition to the canonical list in the database setup script. This ensures the tool is available in the system.

Open `stem/installation/database_setup.py` and update the `populate_tools_table` function:

1.  **Add to `tools_to_insert`**: Add a new tuple for your tool with its `tool_key`, `description`, and `module`.
2.  **Add to `params_to_insert`**: Add tuples for each of your tool's parameters, specifying the `tool_key`, `parameter_name`, `type`, `description`, and whether it is `required` (1 for true, 0 for false).

```python
# stem/installation/database_setup.py

# ... inside populate_tools_table ...

# 1. Add the tool
tools_to_insert = [
    # ... other tools
    ('my_new_tool', 'This is the description of what my new tool does.', 'cerebellum.my_new_tool'),
]

# 2. Add its parameters
params_to_insert = [
    # ... other parameters
    ('my_new_tool', 'parameter_one', 'string', 'Description for the first parameter.', 1),
    ('my_new_tool', 'parameter_two', 'boolean', 'Description for the second parameter.', 0),
]
```

#### Step 3: Register the Tool Function

Now, make the function available to the agent by adding it to the master function map in `stem/tools.py`.

1.  Import your new `execute_` function.
2.  Add a new entry to the `ALL_TOOL_FUNCTIONS` dictionary.

```python
# stem/tools.py
from cerebellum.my_new_tool import execute_my_new_tool
# ... other imports

ALL_TOOL_FUNCTIONS = {
    # ... other tools
    "my_new_tool": execute_my_new_tool,
}
```

*Note: If your tool function requires access to the current user's context (e.g., username), you may need to create a simple wrapper function in `tools.py` to handle passing this context.*

#### Step 4: Enable the Tool

By default, all tools are disabled when first added to the database. To enable your new tool, you must manually update its entry in the `system.db`.

You can do this using a SQLite client:
```sql
UPDATE tools
SET enabled = 1
WHERE tool_key = 'my_new_tool';
```

Once these steps are complete, your tool will be loaded by the agent at runtime and will be available for use. This architecture allows you to enable or disable tools on the fly simply by changing the `enabled` flag in the database.

### Testing

Run the test suite to ensure everything is working correctly:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_cortex_agent.py

# Run with verbose output
python -m pytest -v tests/
```

### Test Cleanup System

Tatlock includes a comprehensive test cleanup system to ensure tests don't leave behind user data or interfere with each other.

#### Automatic Cleanup

The test system automatically cleans up user data after tests:

- **User Databases**: Individual user databases in `hippocampus/longterm/`
- **User Directories**: Short-term storage directories in `hippocampus/shortterm/{username}/`
- **Test Users**: Users created during testing with test-related names

#### Cleanup Functions

```python
from tests.conftest import cleanup_user_data

def test_example():
    username = "test_user"
    # ... test code that creates user data ...
    
    # Clean up after test
    cleanup_user_data(username)
```

#### Cleanup Fixtures

The test configuration includes several cleanup fixtures:

- **`cleanup_test_users`**: Session-scoped fixture that cleans up all test users at the end of the test session
- **`cleanup_after_test`**: Function-scoped fixture that runs after each test
- **User fixtures**: `admin_user` and `test_user` fixtures automatically clean up their created users

#### Cleanup Patterns

```python
@pytest.fixture
def test_user_with_cleanup(security_manager):
    """Create a test user with automatic cleanup."""
    username = f'testuser_{uuid.uuid4()[:8]}'
    
    # Create user
    security_manager.create_user(username, 'Test', 'User', 'password123', 'test@test.com')
    
    user_data = {
        'username': username,
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@test.com'
    }
    
    yield user_data
    
    # Automatic cleanup
    cleanup_user_data(username)
```

#### What Gets Cleaned Up

- **User Databases**: SQLite files in `hippocampus/longterm/{username}.db`
- **User Directories**: Complete directories in `hippocampus/shortterm/{username}/`
- **Test Files**: Any files created during testing
- **Temporary Data**: Screenshots, uploaded files, etc.

#### Cleanup Safety

- **Graceful Handling**: Cleanup functions handle missing files gracefully
- **Error Logging**: Cleanup errors are logged but don't fail tests
- **Partial Cleanup**: Works even if only some user data exists
- **Non-destructive**: Only removes test-related data, not production data

#### Testing Cleanup

```bash
# Test the cleanup system itself
python -m pytest tests/test_cleanup.py -v

# Run tests with cleanup verification
python -m pytest tests/ --tb=short
```

#### Best Practices

1. **Use Unique Names**: Always use unique usernames with UUIDs or timestamps
2. **Clean Up Explicitly**: Call `cleanup_user_data()` for users created in tests
3. **Use Fixtures**: Leverage the built-in cleanup fixtures when possible
4. **Test Isolation**: Ensure tests don't depend on data from other tests
5. **Verify Cleanup**: Check that cleanup actually removes the expected data

### API Development

- **FastAPI Integration**: All endpoints use FastAPI with automatic documentation
- **Pydantic Models**: Request/response validation with Pydantic
- **Session Authentication**: Secure session-based authentication system
- **Error Handling**: Comprehensive error handling and validation

### Database Development

- **User Isolation**: Each user has their own database for complete privacy
- **Migration Support**: Database schema changes should be handled carefully
- **Connection Management**: Proper connection pooling and error handling

### Tool Development

When adding new tools:

1. **Define in `stem/tools.py`**: Add tool function with proper documentation
2. **Add to agent context**: Update the tool list in `cortex/agent.py`
3. **Test thoroughly**: Ensure tools work with user isolation
4. **Add logging**: Include appropriate logging for debugging

### Security Considerations

- **Input Validation**: All inputs must be validated through Pydantic models
- **SQL Injection Prevention**: Use parameterized queries exclusively
- **User Isolation**: Ensure tools respect user boundaries
- **Session Security**: Proper session management and cookie handling
- **Security Code**: Generic security code should live in stem/security.py
- **User Code**: User database specific code should live in hippocampus/user_database.py

## Module Development

### Adding New Modules

1. **Create module directory**: Follow the brain-inspired naming convention
2. **Add `__init__.py`**: Make it a proper Python package
3. **Create `readme.md`**: Document the module's purpose and features
4. **Add tests**: Create comprehensive test coverage
5. **Update main.py**: Integrate with the main application
6. **FastAPI only**: main.py should only be contain FastAPI routing and configuration

### Module Integration

- **FastAPI Routers**: Use FastAPI routers for module endpoints
- **Dependency Injection**: Use FastAPI's dependency injection for shared services
- **Error Handling**: Implement proper error handling and logging
- **Documentation**: Maintain clear API documentation

### Module Route Organization

**Preferred Pattern**: Consolidate all module-related routes into a single central router file within each module. This promotes clean separation, maintainability, and follows the brain-inspired architecture.

#### Central Router Pattern

Each module should have a main router file (e.g., `hippocampus/hippocampus.py`) that consolidates all related endpoints:

```python
# hippocampus/hippocampus.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from stem.security import get_current_user
from stem.models import UserModel
from hippocampus import recall
import os
from fastapi.responses import FileResponse

# Central router for all hippocampus-related endpoints
router = APIRouter(
    prefix="/hippocampus",
    tags=["hippocampus"],
    dependencies=[Depends(get_current_user)]
)

# --- Long-Term Memory Management ---
@router.get("/longterm/conversations", response_model=List[dict])
async def get_user_conversations(
    search: Optional[str] = Query(None, description="Search term to filter conversations"),
    user: UserModel = Depends(get_current_user)
):
    """Get all conversations for the current user, with optional search."""
    # Implementation here
    pass

# --- Short-Term Memory / File Management ---
@router.get("/shortterm/files/get")
async def get_user_file(
    username: str, 
    session_id: str, 
    user: UserModel = Depends(get_current_user)
):
    """Get a specific file for a user from their session directory."""
    # Implementation here
    pass
```

#### Integration in main.py

Import and include the module router in `main.py`:

```python
# main.py
from hippocampus.hippocampus import router as hippocampus_router

# Include module router
app.include_router(hippocampus_router)
```

#### Benefits

- **Clean Separation**: All module routes are contained within the module
- **Consistent Organization**: Uniform pattern across all modules
- **Easy Maintenance**: Single file to manage all module endpoints
- **Clear Dependencies**: Module-specific imports and dependencies
- **Scalable**: Easy to add new endpoints without cluttering main.py
- **Testable**: Module routes can be tested independently
- **Documentation**: API documentation is automatically grouped by module

#### Module Router Structure

```
module_name/
├── __init__.py
├── module_name.py          # Central router file
├── tool1.py               # Individual tool implementations
├── tool2.py               # Individual tool implementations
├── database.py            # Database operations
├── utilities.py           # Module utilities
└── readme.md              # Module documentation
```

#### Route Organization Guidelines

1. **Group Related Endpoints**: Use comments to separate different functional areas
2. **Consistent Naming**: Use descriptive endpoint names that reflect functionality
3. **Proper Authentication**: Include authentication dependencies where needed
4. **Error Handling**: Implement consistent error handling across all endpoints
5. **Documentation**: Include comprehensive docstrings for all endpoints
6. **Type Safety**: Use Pydantic models for request/response validation

#### Example Module Structure

```python
# Example: parietal/parietal.py
from fastapi import APIRouter, Depends
from stem.security import get_current_user

router = APIRouter(
    prefix="/parietal",
    tags=["parietal"],
    dependencies=[Depends(get_current_user)]
)

# --- Hardware Monitoring ---
@router.get("/hardware/status")
async def get_hardware_status():
    """Get current hardware status and metrics."""
    pass

# --- Performance Analysis ---
@router.get("/performance/benchmarks")
async def get_performance_benchmarks():
    """Get system performance benchmarks."""
    pass

# --- System Health ---
@router.get("/health/check")
async def health_check():
    """Perform system health check."""
    pass
```

#### Migration from Scattered Routes

When consolidating existing scattered routes:

1. **Identify Module Routes**: Find all routes related to a specific module
2. **Create Central Router**: Create the main module router file
3. **Move Endpoints**: Transfer endpoints to the central router
4. **Update Imports**: Update main.py to use the new router
5. **Remove Old Files**: Delete any old route files that are no longer needed
6. **Test Thoroughly**: Ensure all endpoints work correctly after migration

This pattern ensures that `main.py` remains clean and focused on application configuration, while each module maintains its own routing logic in a centralized, maintainable way.

## Performance Optimization

### Database Optimization

- **Indexing**: Add appropriate database indexes for common queries
- **Query Optimization**: Use efficient query patterns
- **Connection Pooling**: Implement proper connection management
- **Caching**: Consider caching for frequently accessed data

### API Performance

- **Response Time**: Monitor and optimize API response times
- **Rate Limiting**: Implement appropriate rate limiting
- **Caching**: Cache static assets and frequently accessed data
- **Async Operations**: Use async/await for I/O operations

### Memory Management

- **Resource Cleanup**: Ensure proper cleanup of resources
- **Memory Leaks**: Monitor for memory leaks in long-running processes
- **Garbage Collection**: Understand Python's garbage collection behavior

## Debugging Tools

### Debug Console

Access the debug console at `http://localhost:8000/chat` for:
- Real-time JSON logging
- System performance monitoring
- Tool execution tracking
- Interactive debugging

### System Monitoring

Use the parietal module for:
- Hardware resource monitoring
- Performance benchmarking
- System health checks
- Bottleneck identification

### API Documentation

Access interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`

## Contributing

### Code Style

- **PEP 8**: Follow Python PEP 8 style guidelines
- **Type Hints**: Use type hints for function parameters and return values
- **Docstrings**: Include comprehensive docstrings for all functions
- **Comments**: Add comments for complex logic

### Git Workflow

1. **Feature Branches**: Create feature branches for new development
2. **Commit Messages**: Use clear, descriptive commit messages
3. **Pull Requests**: Submit pull requests for review
4. **Testing**: Ensure all tests pass before merging

### Documentation

- **README Files**: Keep module README files up to date and properly linked
- **root readme.md**: Only should contain installarion instructions, high level project description and links to other readmes
- **developer.ms**: Help for developers to start contributing, contains coding and project standards, ai instructions. AI should not alter coding standards or ai instructions.
- **moreinfo.md**: In depth project description. Acts as overflow to main readme.md.
- **troubleshooting.md**: Contains troubleshooting information for installation or runtime issues. AI should suggest updates when fixes require informing users.
- **module level readme.md**: Contains a desciption of the module, the purpose, the planned features, describes the file system and the file purposes.
- **API Documentation**: Maintain accurate API documentation
- **Code Comments**: Include helpful code comments
- **Change Log**: Document significant changes

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Check database file permissions and paths
2. **API Key Issues**: Verify API keys are correctly set in `.env`
3. **Port Conflicts**: Ensure port 8000 is available or change in `.env`
4. **Permission Errors**: Check file permissions for scripts and databases

### Getting Help

- **Logs**: Check application logs for error details
- **Debug Console**: Use the debug console for real-time monitoring
- **API Documentation**: Review API documentation for endpoint details
- **Module READMEs**: Check individual module documentation

## Related Documentation

- **[README.md](README.md)** - Project overview and installation guide
- **[In-Depth Technical Information](moreinfo.md)** - Detailed architecture and implementation details
- **[Troubleshooting](troubleshooting.md)** - Common installation issues and solutions

## Coding Standards

This section outlines the coding standards and patterns used throughout the Tatlock project. All developers should follow these standards to maintain code consistency and quality.

### Project Organization

#### Brain-Inspired Architecture
- **Module Naming**: Modules are named after brain regions (cortex, hippocampus, stem, parietal, etc.)
- **Clear Separation**: Core logic, authentication, memory, and utilities in separate modules
- **Consistent Structure**: Each module has `__init__.py`, `readme.md`, and relevant functionality
- **Test Organization**: Comprehensive test suite in `tests/` directory

#### File Structure
```
tatlock/
├── cortex/          # Core agent logic and decision-making
├── hippocampus/     # Memory system and storage
├── stem/           # Authentication, utilities, and core services
├── parietal/       # Hardware monitoring and performance analysis
├── tests/          # Comprehensive test suite
├── main.py         # Application entry point
├── config.py       # Configuration and environment variables
└── requirements.txt # Python dependencies
```

### Python Coding Standards

#### File Structure & Documentation
```python
"""
module_name.py

Brief description of the module's purpose.
Provides specific functionality and features.
"""

import logging
import sqlite3
# ... other imports
from typing import Optional, Dict, Any, List

# Set up logging for this module
logger = logging.getLogger(__name__)
```

#### Type Hints & Modern Python
- **Required Python 3.10+**: Uses modern type hints like `list[dict]`, `str | None`
- **Comprehensive Type Hints**: All functions have parameter and return type annotations
- **Optional Parameters**: Uses `Optional[Type]` for nullable parameters
- **Union Types**: Uses `|` syntax for union types (Python 3.10+)

```python
def function_name(param1: str, param2: Optional[int] = None) -> bool:
    """
    Brief description of what the function does.
    Args:
        param1 (str): Description of parameter
        param2 (Optional[int]): Description of optional parameter
    Returns:
        bool: Description of return value
    """
```

#### Error Handling
- **Try-Catch Blocks**: Comprehensive exception handling
- **Logging**: Structured logging with appropriate levels (info, warning, error)
- **Graceful Degradation**: Functions return safe defaults on errors
- **Database Connections**: Proper connection cleanup in finally blocks

```python
try:
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table WHERE field = ?", (param,))
    result = cursor.fetchall()
    conn.close()
    return result
except Exception as e:
    logger.error(f"Error description: {e}")
    return []
```

#### Database Patterns
```python
def database_operation(self, param: str) -> List[Dict[str, Any]]:
    """Standard database operation pattern."""
    try:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT field1, field2, field3
            FROM table_name
            WHERE condition = ?
        """, (param,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        return [{'field1': row[0], 'field2': row[1], 'field3': row[2]} for row in rows]
        
    except Exception as e:
        logger.error(f"Database error: {e}")
        return []
```

### JavaScript Coding Standards
- **library maintenance**: Keep javascript in javascript files, making sure to used shared libraries where code duplicates

#### Class-Based Architecture
```javascript
class ModuleName {
    constructor(options = {}) {
        this.property = options.property || defaultValue;
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Event listener setup
    }
    
    async methodName() {
        try {
            // Async operations
        } catch (error) {
            console.error('Error description:', error);
        }
    }
}
```

#### Modern JavaScript Features
- **ES6+ Syntax**: Arrow functions, destructuring, template literals
- **Async/Await**: Consistent use for all asynchronous operations
- **Fetch API**: Standard HTTP requests with proper error handling
- **Class Syntax**: Object-oriented approach for complex functionality

#### Error Handling & Logging
```javascript
async function apiCall(data) {
    try {
        const response = await fetch('/endpoint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        if (!response.ok) throw new Error('Request failed');
        return await response.json();
    } catch (error) {
        console.error('Error description:', error);
        // User-friendly error handling
        snackbar.error('User-friendly error message');
    }
}
```

#### Event Handling
```javascript
function setupEventListeners() {
    // Auto-resize textarea
    element.addEventListener('input', () => {
        element.style.height = 'auto';
        element.style.height = Math.min(element.scrollHeight, maxHeight) + 'px';
    });
    
    // Keyboard shortcuts
    element.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    });
}
```

### CSS/UI Standards
- **library maintenance**: Keep css in css files

#### CSS Variables & Theming
```css
:root {
    --bg-primary: #f5f5f5;
    --text-primary: #333333;
    --accent-color: #2196F3;
    --border-color: #e0e0e0;
    --shadow: 0 2px 4px rgba(0,0,0,0.1);
}

[data-theme="dark"] {
    --bg-primary: #181629;
    --text-primary: #f8f8fa;
    --accent-color: #8a63d2;
    --border-color: #2d2942;
}
```

#### Responsive Design
- **Mobile-First**: Responsive breakpoints for different screen sizes
- **Flexbox/Grid**: Modern CSS layout techniques
- **Consistent Spacing**: Standardized padding, margins, and gaps
- **Accessibility**: Proper contrast ratios and focus states

```css
/* Mobile-first responsive design */
.container {
    padding: 20px;
    max-width: 1100px;
    margin: 0 auto;
}

@media (max-width: 768px) {
    .container {
        padding: 15px;
    }
}

@media (max-width: 480px) {
    .container {
        padding: 10px;
    }
}
```

#### Component Styling
```css
.component {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 20px;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
}

.component:hover {
    box-shadow: var(--shadow-light);
    transform: translateY(-1px);
}
```

### Security Standards

#### Authentication & Authorization
- **Session-Based**: Secure session management with cookies
- **Password Hashing**: PBKDF2 with unique salts
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Prevention**: Parameterized queries only
- **User Isolation**: Complete data separation between users

```python
def require_admin_role(current_user: dict = Depends(get_current_user)):
    """Require admin role for endpoint access."""
    if 'admin' not in current_user.get('roles', []):
        raise HTTPException(status_code=403, detail="Admin access required")
```

#### Input Validation
```python
from pydantic import BaseModel, EmailStr

class UserCreateRequest(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
```

#### Database Security
```python
# ✅ Correct: Parameterized queries
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

# ❌ Incorrect: String formatting
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

### Testing Standards

#### Test Organization
- **Comprehensive Coverage**: Tests for all modules and functionality
- **Fixtures**: Reusable test data and setup
- **Mocking**: Proper isolation of external dependencies
- **Assertions**: Clear, descriptive test assertions

```python
import pytest
from unittest.mock import patch

@pytest.fixture
def sample_user():
    return {
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com'
    }

def test_create_user(sample_user):
    """Test user creation functionality."""
    with patch('module.security_manager') as mock_sm:
        mock_sm.create_user.return_value = True
        
        result = create_user(sample_user)
        
        assert result is True
        mock_sm.create_user.assert_called_once_with(
            sample_user['username'],
            sample_user['first_name'],
            sample_user['last_name'],
            sample_user['password'],
            sample_user['email']
        )
```

#### Test File Naming
- **Pattern**: `test_module_name.py`
- **Location**: `tests/` directory
- **Coverage**: Unit tests, integration tests, and end-to-end tests

### Documentation Standards

#### README Files
- **Module Purpose**: Clear description of functionality
- **API Documentation**: Endpoint descriptions and examples
- **Integration Guide**: How modules work together
- **Future Plans**: Roadmap for planned features

#### Code Comments
- **Complex Logic**: Comments for non-obvious code
- **Business Logic**: Explanation of business rules
- **TODO Comments**: Marked future improvements
- **Inline Documentation**: Docstrings for all public functions

```python
# TODO: Implement caching for frequently accessed data
def expensive_operation():
    """
    Performs an expensive operation that should be cached.
    
    This function performs complex calculations that take significant time.
    Future optimization should include Redis caching for results.
    """
    pass
```

### Performance Standards

#### Database Optimization
- **Indexing**: Appropriate database indexes for common queries
- **Connection Management**: Proper connection pooling
- **Query Efficiency**: Optimized SQL queries
- **Caching**: Strategic caching for performance

```python
# ✅ Efficient: Single query with JOIN
cursor.execute("""
    SELECT u.username, r.role_name
    FROM users u
    JOIN user_roles ur ON u.username = ur.username
    JOIN roles r ON ur.role_id = r.id
    WHERE u.username = ?
""", (username,))

# ❌ Inefficient: Multiple queries
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
cursor.execute("SELECT * FROM user_roles WHERE username = ?", (username,))
```

#### Frontend Performance
- **Asset Optimization**: Minified CSS/JS
- **Lazy Loading**: On-demand resource loading
- **Efficient DOM**: Minimal DOM manipulation
- **Memory Management**: Proper cleanup of event listeners

```javascript
// ✅ Efficient: Event delegation
document.addEventListener('click', (e) => {
    if (e.target.matches('.delete-btn')) {
        handleDelete(e.target.dataset.id);
    }
});

// ❌ Inefficient: Multiple event listeners
document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', () => handleDelete(btn.dataset.id));
});
```

### Code Review Checklist

Before submitting code for review, ensure:

#### Python Code
- [ ] Type hints for all function parameters and return values
- [ ] Comprehensive docstrings for all public functions
- [ ] Proper error handling with logging
- [ ] Database connections properly closed
- [ ] Input validation using Pydantic models
- [ ] Unit tests for new functionality

#### JavaScript Code
- [ ] Modern ES6+ syntax used appropriately
- [ ] Async/await for all asynchronous operations
- [ ] Proper error handling with user feedback
- [ ] Event listeners properly cleaned up
- [ ] Responsive design considerations
- [ ] Accessibility features included

#### General
- [ ] Code follows established patterns
- [ ] No security vulnerabilities introduced
- [ ] Performance considerations addressed
- [ ] Documentation updated
- [ ] Tests pass and coverage maintained

### Best Practices

#### Code Organization
1. **Single Responsibility**: Each function/class has one clear purpose
2. **DRY Principle**: Don't repeat yourself - extract common functionality
3. **Separation of Concerns**: Keep business logic, data access, and presentation separate
4. **Consistent Naming**: Use clear, descriptive names for variables, functions, and classes

#### Error Handling
1. **Fail Fast**: Detect and handle errors as early as possible
2. **User-Friendly Messages**: Provide clear error messages to users
3. **Logging**: Log errors with appropriate context for debugging
4. **Graceful Degradation**: Provide fallback behavior when possible

#### Security
1. **Input Validation**: Validate all user inputs
2. **Output Encoding**: Properly encode output to prevent XSS
3. **Authentication**: Verify user identity for protected operations
4. **Authorization**: Check user permissions before allowing actions
4. **Package Versions**: Always use the most current version of packages that don't cause dependency conflicts. Comment if that is not possible and why.

#### Performance
1. **Database Optimization**: Use efficient queries and proper indexing
2. **Caching**: Cache frequently accessed data
3. **Lazy Loading**: Load resources only when needed
4. **Monitoring**: Track performance metrics and optimize bottlenecks

#### AI-Assisted Development
1. **Always Include Standards**: When using coding AI assistants (like Cursor, GitHub Copilot, Claude, GPT, etc.), always include the Tatlock coding standards from this `developer.md` file as part of your prompt
2. **Reference Specific Sections**: Reference relevant sections like "Python Coding Standards", "JavaScript Coding Standards", or "Security Standards" based on the task
3. **Validate Generated Code**: Review AI-generated code to ensure it follows our established patterns and conventions
4. **Update Standards**: If AI suggests improvements to our coding standards, evaluate and update this document accordingly

**Example AI Prompt:**
```
Please help me implement [specific feature] following the Tatlock coding standards:

Python standards:
- Use type hints for all functions (Python 3.10+ syntax)
- Include comprehensive docstrings
- Use structured logging with logger = logging.getLogger(__name__)
- Follow database patterns with proper error handling
- Use Pydantic models for input validation

Security standards:
- Use parameterized queries only
- Validate all inputs
- Implement proper user isolation

[Your specific request here]
```

Following these coding standards ensures consistent, maintainable, and secure code throughout the Tatlock project.

## User Authentication and Context Access

### Context-Based User Model Pattern

Tatlock now uses a context-based, per-request user model for all authentication and user info access. This ensures type safety, eliminates the need to pass usernames/roles through function calls, and makes user access DRY and consistent across the codebase.

#### How it Works
- The dependency `Depends(get_current_user)` sets the current user in a context variable for the duration of the request.
- The user is stored as a Pydantic `UserModel` (see `stem/models.py`), which matches the `users` table (excluding password and salt).
- You can access the current user anywhere in the request using:
  ```python
  from stem.current_user_context import get_current_user_ctx
  user = get_current_user_ctx()
  if user is None:
      raise HTTPException(status_code=401, detail="Not authenticated")
  # Access fields as attributes:
  username = user.username
  roles = security_manager.get_user_roles(user.username)
  ```
- When passing the user to a template function (e.g., `get_chat_page`, `get_profile_page`), convert the user to a dict:
  ```python
  return get_chat_page(request, user.model_dump())
  ```

#### Endpoint Example
```python
@app.get("/profile")
async def profile_page(request: Request, _: None = Depends(get_current_user)):
    user = get_current_user_ctx()
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return get_profile_page(request, user.model_dump())
```

#### Security/Admin Example
```python
def require_admin_role():
    current_user = get_current_user_ctx()
    if not current_user or not security_manager.user_has_role(current_user.username, 'admin'):
        raise HTTPException(status_code=403, detail="Admin role required")
```

#### Benefits
- **Type Safety:** All user access is via a Pydantic model, not a dict.
- **No More Passing Usernames:** No need to pass username/roles through function calls.
- **Per-Request Isolation:** Each request gets its own user context, safe for async/concurrent code.
- **Consistent Template Usage:** Always pass `user.model_dump()` to templates.

#### When Adding New Endpoints
- Use `_: None = Depends(get_current_user)` in the signature.
- Use `user = get_current_user_ctx()` in the body.
- Raise 401 if user is None.
- Pass `user.model_dump()` to templates.

#### Legacy Pattern Removal
- All legacy `current_user: dict = Depends(get_current_user)` and dict key access have been removed. Do not use dict-based user access in new code.

## Voice Input Implementation

### Overview
The voice input system integrates real-time audio capture with the chat interface, providing a natural way to interact with Tatlock using speech.

### Architecture
- **Frontend**: Microphone button in chat interface with WebSocket audio streaming
- **Backend**: FastAPI WebSocket endpoint with Whisper speech recognition
- **Processing**: Temporal context and language understanding pipeline

### Key Components

#### Frontend (JavaScript)
```javascript
// Voice capture class in chat.js
class TatlockChat {
    constructor() {
        this.chatMicBtn = document.getElementById('sidepane-mic-btn');
        this.keyword = 'tatlock';
        this.pauseDuration = 5000; // 5 seconds
        this.setupVoiceListeners();
    }
    
    async startVoiceCapture() {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        
        // Stream to WebSocket
        this.voiceWebSocket = new WebSocket('ws://localhost:8000/ws/voice');
        this.mediaRecorder.ondataavailable = (e) => this.sendAudioChunk(e.data);
        this.mediaRecorder.start(250); // 250ms chunks
    }
}
```

#### Backend (Python)
```python
# WebSocket endpoint in main.py
@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Authenticate user via session cookie
    await voice_service.handle_websocket_connection(websocket, path="/ws/voice")

# Voice processing in temporal/voice_service.py
class VoiceService:
    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        # Use Whisper for speech-to-text
        result = self.whisper_model.transcribe(temp_file)
        return result["text"].strip()
    
    async def process_voice_command(self, text: str) -> Dict[str, Any]:
        # Add to temporal context and extract intent
        self.temporal_context.add_interaction(text)
        intent = self.language_processor.extract_intent(text)
        return {"original_text": text, "intent": intent}
```

### Coding Patterns

#### WebSocket Audio Streaming
- **Binary Protocol**: Audio chunks sent with "audio:" prefix
- **Chunked Processing**: 250ms audio chunks for real-time processing
- **Session Authentication**: WebSocket requires valid session cookie

#### Keyword Detection
- **Client-side Processing**: JavaScript checks for "tatlock" keyword
- **Prompt Extraction**: Extracts text after keyword for chat input
- **Auto-pause**: 5-second timeout for natural conversation flow

#### Error Handling
- **Graceful Degradation**: Falls back to text input if voice unavailable
- **User Feedback**: Visual indicators for recording state
- **Connection Recovery**: Automatic WebSocket reconnection

### Security Considerations
- **Session Validation**: WebSocket endpoints require authentication
- **Audio Privacy**: Audio processed server-side, not stored
- **User Consent**: Microphone access requires explicit permission
- **Input Sanitization**: All voice input processed through language processor

### Testing
```bash
# Test voice components
python temporal/test_voice.py

# Test integration
python temporal/integration_example.py

# Test WebSocket server
python temporal/integration_example.py server
```

### Future Enhancements
- **Always-on Detection**: Background keyword spotting
- **Voice Synthesis**: Text-to-speech responses
- **Multi-language Support**: International voice recognition
- **Hardware Integration**: Raspberry Pi and embedded systems 

## Database Schema

### System Database (system.db)

The system database contains user authentication and authorization data.

#### Tables

- **users**: User account information (username, first_name, last_name, email, timestamps)
- **passwords**: Password hashes and salts (separated from users table for security)
- **roles**: Available roles in the system
- **groups**: Available groups in the system
- **user_roles**: Many-to-many relationship between users and roles
- **user_groups**: Many-to-many relationship between users and groups
- **migrations**: Tracks applied database migrations

#### Password Table Migration

The password data has been migrated from the `users` table to a separate `passwords` table for better security and data organization. The migration system automatically handles this transition:

- **Old Schema**: `users` table contained `password_hash` and `salt` columns
- **New Schema**: `passwords` table with foreign key relationship to `users` table
- **Migration**: Automatic migration preserves existing data and updates schema
- **Benefits**: Better separation of concerns, improved security, easier password management

The migration is idempotent and safe to run multiple times.

### Long-term Memory Database (longterm/<username>.db)

Each user has their own long-term memory database for storing conversation history and personal data.

#### Tables

- **memories**: Individual conversation interactions
- **topics**: Available conversation topics
- **memory_topics**: Many-to-many relationship between memories and topics
- **conversation_topics**: Topic tracking per conversation
- **conversations**: Conversation metadata
- **rise_and_shine**: System instructions and prompts
- **personal_variables_keys**: Keys for personal variables
- **personal_variables**: Values for personal variables
- **personal_variables_join**: Many-to-many relationship between keys and values

## User Context Management

### Current User Context

The application uses a context-local user storage system to avoid passing user data through function parameters:

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

### Benefits

- **Type Safety**: UserModel provides type hints and validation
- **Clean APIs**: No need to pass user data through function parameters
- **Consistency**: Uniform user access pattern across the application
- **Security**: User data is properly encapsulated and validated

## Security

### Password Management

Passwords are stored securely using:

- **Hashing**: bcrypt with configurable rounds
- **Salting**: Unique salt per password
- **Separation**: Password data stored in separate table
- **Validation**: Pydantic models for type safety

### Authentication Flow

1. User submits username/password
2. System retrieves password hash and salt from `passwords` table
3. Password is verified using bcrypt
4. User session is created with context-local storage
5. User data is available throughout the request lifecycle

### Authorization

- **Roles**: Fine-grained permissions via role system
- **Groups**: User grouping for bulk operations
- **Middleware**: Automatic role checking via dependencies
- **Context**: User roles available in current user context

## Testing

### Database Tests

Tests use temporary SQLite databases to ensure isolation:

```python
def test_example():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Test with temporary database
        create_system_db_tables(db_path)
        # ... test logic ...
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)
```

### Migration Tests

Migration tests verify that database schema changes work correctly:

- **Forward Migration**: Old schema → New schema
- **Data Preservation**: Existing data is maintained
- **Idempotency**: Multiple runs don't cause issues
- **Rollback Safety**: Tests verify data integrity

## Code Organization

### Module Structure

- **stem/**: Core application logic
  - **security.py**: Authentication and authorization
  - **current_user_context.py**: User context management
  - **installation/**: Database setup and migrations
- **hippocampus/**: Memory and conversation management
- **cortex/**: AI agent logic
- **tests/**: Comprehensive test suite

### Patterns

- **Dependency Injection**: FastAPI dependencies for authentication
- **Context Variables**: Thread-local storage for user data
- **Pydantic Models**: Type-safe data structures
- **Migration System**: Automatic database schema updates
- **Test Isolation**: Temporary databases for testing

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

1. **Schema Updates**: Modify `SYSTEM_DB_SCHEMA` or `LONGTERM_DB_SCHEMA`
2. **Migration Function**: Create migration function in `database_setup.py`
3. **Migration Tracking**: Add migration record to `migrations` table
4. **Testing**: Write tests for migration process
5. **Documentation**: Update schema documentation