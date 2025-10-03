# Developer Guide

This guide contains developer-specific information for working with Tatlock, including logging, debugging, performance monitoring, and development practices.

## AI Instructions

This section provides guidelines for AI assistants (like Cursor, GitHub Copilot, Claude, GPT, etc.) contributing to the Tatlock project.

**Primary Directive**: Always adhere to the coding standards, patterns, and development practices described in this file. If a request conflicts with these standards, ask for clarification or permission before deviating.

### Core Workflows

- **Versioning**: When asked to update the application version, you must follow the full "Versioning and Releases" workflow. This includes updating `changelog.md` with all changes since the last version, committing it with the `pyproject.toml` update, and creating a Git tag.
- **Troubleshooting**: When a fix resolves a common installation or runtime issue, suggest an addition to `troubleshooting.md` to help future users.
- **Testing**: All new code, whether adding features or fixing bugs, must be accompanied by corresponding tests to ensure correctness and prevent regressions. **CRITICAL**: Always use authenticated testing fixtures (`authenticated_admin_client`, `authenticated_user_client`) for API endpoints and core functionality tests.
- **Code Organization**: Keep the codebase clean and maintainable. If code is used in multiple places, refactor it into a new shared file, following the Don't Repeat Yourself (DRY) principle. When creating new files, place them in the appropriate module directory, adhering to the existing filesystem structure patterns.

### General Guidance

1. **Always Include Standards**: When using coding AI assistants, always include the Tatlock coding standards from this `AGENTS.md` file as part of your prompt.
2. **Reference Specific Sections**: Reference relevant sections like "Python Coding Standards", "JavaScript Coding Standards", or "Security Standards" based on the task.
3. **Validate Generated Code**: Review AI-generated code to ensure it follows our established patterns and conventions.
4. **Update Standards**: If AI suggests improvements to our coding standards, evaluate and update this document accordingly.

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
html = render_template('page.login.html', context)

# Render template as HTMLResponse
response = render_page('page.login.html', context)
```

#### Template Structure

```
stem/templates/
├── base.html                 # Base layout template
├── page.login.html               # Login page template
├── page.conversation.html        # Main conversation interface template
├── page.profile.html             # User profile template
├── page.admin.html               # Admin dashboard template
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

1. **Update the Changelog**: Before bumping the version, you must update `changelog.md`.
    - Create a new release section (e.g., `## [0.2.0] - YYYY-MM-DD`).
    - Move all changes from the `[Unreleased]` section to this new version.
    - **Separate changes by type**: Place major new features under `### Added` or `### Changed`, while smaller bugfixes go under `### Fixed`. This separation is important for release notes.

2. **Update the Version**: Modify the `version` field in `pyproject.toml`.

3. **Commit the Changes**: Commit both `changelog.md` and `pyproject.toml` together.

    ```bash
    git add changelog.md pyproject.toml
    git commit -m "Bump version to 0.2.0"
    ```

4. **Tag the Release**: Create an annotated Git tag for the new version.

    ```bash
    git tag -a v0.2.0 -m "Release version 0.2.0"
    ```

5. **Push to GitHub**: Push your commits and the new tag to the remote repository.

    ```bash
    git push origin main --tags
    ```

### Code Organization

- **Brain-Inspired Design**: Codebase organized into modules inspired by brain regions

### Tool Organization

Tatlock follows a modular tool organization pattern where each tool is implemented in its own file within the appropriate brain module. **Tools belong in the root of their respective modules, not in subdirectories.** This promotes maintainability, testability, and clear separation of concerns.

**Lean System Note**: Tools are now categorized as **Core** (always available) or **Extended** (catalog-based). See the [Lean Agent System Architecture](#lean-agent-system-architecture) section for details on this performance optimization.

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

Tools use a **dynamic loading system** with database-driven registration:

```python
# stem/tools.py - Dynamic system with backward compatibility
from stem.dynamic_tools import tool_registry, initialize_tool_system, get_tool_function

# Initialize the dynamic tool system
initialize_tool_system()

# The TOOLS list is loaded from database for Ollama compatibility
TOOLS = get_enabled_tools_from_db()

def execute_tool(tool_key: str, **kwargs) -> Dict[str, Any]:
    """Execute a tool by key with dynamic loading."""
    tool_func = get_tool_function(tool_key)
    if not tool_func:
        return {"status": "error", "message": f"Tool '{tool_key}' not found"}

    result = tool_func(**kwargs)
    return result

# Backward compatibility: LazyToolDict that loads tools on demand
AVAILABLE_TOOLS = LazyToolDict()
```

**Database Registration**: Tools are registered in the `tools` table:

```sql
INSERT INTO tools (tool_key, description, module, function_name, enabled)
VALUES (
    'web_search',
    'Perform a web search using Google Custom Search API.',
    'cerebellum.web_search_tool',
    'execute_web_search',
    1
);
```

#### Module Assignment Guidelines

- **Cerebellum**: External API tools (web search, weather, etc.)
- **Hippocampus**: Memory and database-related tools
- **Occipital**: Visual processing and screenshot tools
- **Stem**: Core system tools and dynamic tool loading infrastructure

#### Benefits of Dynamic Tool System

- **Modularity**: Each tool is self-contained and can be developed/tested independently
- **Performance**: Tools are loaded on-demand, reducing startup time and memory usage
- **Database-Driven**: Tool registration and configuration stored in database for runtime control
- **Plugin Architecture**: Supports built-in tools, plugins, and external tool packages
- **Backward Compatibility**: Existing code continues to work via `LazyToolDict`
- **Testing**: Mock-friendly design with comprehensive test coverage
- **Maintainability**: Easy to enable/disable tools without code changes
- **Scalability**: New tools can be added without modifying core files
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

1. **Add to `tools_to_insert`**: Add a new tuple for your tool with its `tool_key`, `description`, and `module`.
2. **Add to `params_to_insert`**: Add tuples for each of your tool's parameters, specifying the `tool_key`, `parameter_name`, `type`, `description`, and whether it is `required` (1 for true, 0 for false).

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

1. Import your new `execute_` function.
2. Add a new entry to the `ALL_TOOL_FUNCTIONS` dictionary.

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

### Hardware Configuration Testing

Tatlock automatically selects the optimal model based on hardware detection during installation. For testing different models or performance tiers, you can manually override the hardware configuration.

#### Manual Model Override

The `hardware_config.py` file controls which model is used:

```python
# hardware_config.py
RECOMMENDED_MODEL = "mistral:7b"        # Current model
PERFORMANCE_TIER = "medium"             # Current tier
```

To test different models, simply edit this file:

```bash
# Test low-spec model (phi4-mini with tool support)
echo 'RECOMMENDED_MODEL = "phi4-mini:3.8b-q4_K_M"' > hardware_config.py
echo 'PERFORMANCE_TIER = "low"' >> hardware_config.py

# Test high-spec model (gemma3-cortex)
echo 'RECOMMENDED_MODEL = "gemma3-cortex:latest"' > hardware_config.py
echo 'PERFORMANCE_TIER = "high"' >> hardware_config.py

# Test medium-spec model (mistral for Apple Silicon)
echo 'RECOMMENDED_MODEL = "mistral:7b"' > hardware_config.py
echo 'PERFORMANCE_TIER = "medium"' >> hardware_config.py
```

#### Available Model Tiers

- **Low**: `phi4-mini:3.8b-q4_K_M` - Quantized model with tool support for low-spec hardware, M1 processors, or Apple Silicon ≤16GB RAM
- **Medium**: `mistral:7b` - Balanced performance for mid-range systems or Apple Silicon M2/M3 with >16GB RAM
- **High**: `gemma3-cortex:latest` - Maximum performance for high-spec non-Apple Silicon systems (8GB+ RAM, 4+ cores)

#### Testing Performance

After changing the model, restart the application to test performance:

```bash
# Restart with new model
./wakeup.sh

# Test simple query performance
time curl -X POST http://localhost:8000/cortex \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"message": "What is 2+2?", "history": [], "conversation_id": "test"}'

# Test tool-assisted query performance
time curl -X POST http://localhost:8000/cortex \
  -b cookies.txt \
  -H "Content-Type: application/json" \
  -d '{"message": "What did we discuss before?", "history": [], "conversation_id": "test"}'
```

**Note**: Manual edits to `hardware_config.py` will be overwritten on next installation. This approach is intended for testing and development only.

#### Comprehensive Performance Benchmarking

For systematic performance testing across all hardware tiers, use the comprehensive benchmark script:

```bash
# Run complete benchmark across all three hardware tiers
python tests/benchmark_all_tiers.py

# This will test:
# - Phase 1 queries (simple responses without tools)
# - Phase 2 queries (tool-assisted responses)
# - All three hardware tiers (low/medium/high)
# - Generate CSV output with timing and response data
```

The benchmark script automatically:
- Tests each tier with appropriate models (phi4-mini, mistral:7b, gemma3-cortex)
- Handles authentication and session management
- Outputs incremental results to CSV for real-time monitoring
- Provides comprehensive performance and quality analysis

Sample benchmark commands tested:
- **Phase 1**: "What is 2+2?" (simple mathematical query)
- **Phase 2**: "What did we discuss before?" (memory/tool-assisted query)

Results are saved as `benchmark_results_[timestamp].csv` in the tests directory for analysis.

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

Access the debug console at `http://localhost:8000/conversation` for:

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
- **Hardware classification for automatic model selection**

#### Hardware-Dependent Model Selection

The parietal module now includes `classify_hardware_performance()` which:

- **Detects System Capabilities**: RAM, CPU cores, architecture, OS
- **Classifies Performance Tiers**: High, Medium, Low based on resources
- **Apple Silicon Optimization**: Special handling for M1/M2 compatibility
- **Automatic Model Selection**: Returns optimal LLM model for the hardware

**Usage Example**:

```python
from parietal.hardware import classify_hardware_performance

result = classify_hardware_performance()
print(f"Recommended model: {result['recommended_model']}")
print(f"Performance tier: {result['performance_tier']}")
```

**API Endpoint**: `GET /parietal/hardware/classification`

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

## Lean Agent System Architecture

Tatlock implements a **two-phase lean agent system** optimized for performance and maintainability. This system reduces prompt overhead from 27+ prompts to 6 prompts (78% reduction) while maintaining full functionality.

### Two-Tier Tool Architecture

**Core Tools (Always Available)**:
- **Memory Tools**: `recall_memories`, `recall_memories_with_time`
- **Personal Data**: `find_personal_variables`
- **Loading**: Included in base instructions for immediate access
- **Purpose**: Essential capabilities that should always be available

**Extended Tools (Catalog-Based)**:
- **External Services**: Weather, web search, screenshots
- **Advanced Memory**: Analytics, exports, cleanup, insights
- **Visual Processing**: File analysis, website testing
- **Loading**: Loaded only when needed via capability assessment
- **Purpose**: Specialized capabilities accessed through catalog system

### Performance Benefits

- **Reduced Overhead**: From 27 prompts to 6 prompts per request
- **Faster Response**: Capability assessment uses minimal context
- **Smart Routing**: Direct responses for knowledge-based questions
- **Tool Efficiency**: Only relevant tools loaded when needed
- **Memory Preserved**: Core memory functionality always accessible

### Implementation Details

**Phase 1: Capability Assessment**
```python
# Minimal context for fast assessment
capability_messages = [
    {'role': 'system', 'content': f'Current date: {date}, Location: {location}'},
    {'role': 'system', 'content': capability_prompt},
    {'role': 'user', 'content': user_message}
]
```

**Phase 2: Tool-Enabled Processing**
```python
# Only if tools needed - uses full context + selected tools
if assessment.assessment == "TOOLS_NEEDED":
    selected_tools = get_selected_tools(assessment.tools)
    response = ollama.chat(messages=full_messages, tools=selected_tools)
```

**Core Tools Configuration**
```python
# hippocampus/database.py
CORE_TOOLS = [
    'recall_memories',
    'recall_memories_with_time',
    'find_personal_variables'
]
```

### Structured Output Parsing

Uses industry-standard **Instructor + Pydantic** approach:
- **Primary**: Instructor with JSON Schema validation
- **Fallback**: Enhanced parsing for reliability
- **Benefits**: Works across Mistral, Gemma2, Gemma3 models
- **Reliability**: Graceful fallback prevents parsing failures

```python
class CapabilityAssessment(BaseModel):
    assessment: Literal["DIRECT", "TOOLS_NEEDED"]
    tools: List[str] = Field(default=[])
    response: str
```

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
├── config.py       # Configuration with automatic hardware-dependent model selection
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

#### JavaScript File Naming Patterns

Tatlock follows a structured naming convention for JavaScript files to ensure clarity, maintainability, and consistency across the codebase.

##### File Type Categories

**Page-Specific Scripts**

- **Pattern**: `page.{pagename}.js`
- **Purpose**: Functionality specific to individual pages
- **Examples**:
  - `page.login.js` - Login page functionality
  - `page.conversation.js` - Conversation/debug console functionality
  - `page.profile.js` - User profile management
  - `page.admin.js` - Admin dashboard functionality
- **Loading**: Loaded only on their respective pages
- **Scope**: Page-specific DOM manipulation, event handlers, and business logic

**Component Scripts**

- **Pattern**: `component.{componentname}.js`
- **Purpose**: Reusable UI component functionality
- **Examples**:
  - `component.chatbar.js` - Chat sidebar component functionality
- **Loading**: Loaded on pages that use the specific component
- **Scope**: Component-specific behavior, state management, and interactions

**Shared Scripts**

- **Pattern**: `{functionality}.js` (for core shared functionality)
- **Purpose**: Common functionality used across multiple pages
- **Examples**:
  - `common.js` - Shared utilities, authentication, UI components, and navigation
- **Loading**: Loaded on all pages that require shared functionality
- **Scope**: Global utilities, authentication handling, theme management, snackbar system

**Plugin Scripts**

- **Pattern**: `plugin.{library}.js`
- **Purpose**: Third-party libraries and external dependencies
- **Examples**:
  - `plugin.chart.min.js` - Chart.js library
  - `plugin.chart.umd.min.js.map` - Chart.js source map
  - `plugin.json-highlight.js` - JSON syntax highlighting library
  - `plugin.marked.min.js` - Markdown parsing library
- **Loading**: Loaded on pages that require the specific library
- **Scope**: External library functionality, no custom code

##### Script Loading Order

Templates follow a consistent script loading order to ensure proper dependency resolution:

1. **`common.js`** - Shared utilities and core functionality first
2. **Component scripts** - Reusable component functionality
3. **Page-specific scripts** - Page-specific functionality
4. **Plugin scripts** - External libraries as needed

**Example Loading Pattern:**

```html
{% block scripts %}
<script src="/static/js/common.js"></script>
<script src="/static/js/component.chatbar.js"></script>
<script src="/static/js/page.conversation.js"></script>
<script src="/static/js/plugin.marked.min.js"></script>
{% endblock %}
```

##### Naming Guidelines

**Consistency**

- Use lowercase with hyphens for multi-word names
- Follow established patterns exactly
- Maintain clear separation between categories

**Descriptive Names**

- Page names should match the route/functionality
- Component names should describe the UI element
- Plugin names should match the library name

**Avoid Confusion**

- Don't mix patterns (e.g., don't use `page.` prefix for components)
- Don't use generic names that could apply to multiple categories
- Don't create exceptions to established patterns

##### Benefits

- **Clear Purpose**: File names immediately indicate their purpose and scope
- **Maintainability**: Easy to locate and modify specific functionality
- **Consistency**: Uniform naming across the entire codebase
- **Separation of Concerns**: Clear distinction between different types of functionality
- **Scalability**: Easy to add new files following established patterns
- **Dependency Management**: Clear loading order prevents conflicts

##### Migration Guidelines

When renaming or reorganizing JavaScript files:

1. **Follow Established Patterns**: Use the appropriate prefix for the file type
2. **Update All References**: Update all template files and documentation
3. **Maintain Backward Compatibility**: Ensure existing functionality continues to work
4. **Update Documentation**: Keep naming pattern documentation current
5. **Test Thoroughly**: Verify all pages load correctly after changes

##### Exception Handling

**Login Page Isolation**

- The login page is an exception that duplicates `togglePassword` function from `common.js`
- This isolation prevents unnecessary dependencies on unauthenticated pages
- Document exceptions clearly in code comments and changelog

**Legacy Files**

- Some files may not follow current patterns
- Legacy files should be renamed when practical
- Document why legacy naming exists

#### Comprehensive File Naming Patterns

Tatlock follows consistent naming patterns across all file types to ensure clarity, maintainability, and organization throughout the codebase.

##### HTML Template Files

**Page Templates**

- **Pattern**: `page.{pagename}.html`
- **Purpose**: Main page templates for different application sections
- **Examples**:
  - `page.login.html` - Authentication page template
  - `page.conversation.html` - Main conversation interface template
  - `page.profile.html` - User profile management template
  - `page.admin.html` - Admin dashboard template
- **Location**: `stem/templates/` and `stem/static/`
- **Scope**: Complete page layouts with navigation, content areas, and script loading

**Component Templates**

- **Pattern**: `{componentname}.html`
- **Purpose**: Reusable UI component templates
- **Examples**:
  - `chat-sidebar.html` - Chat sidebar component
  - `header.html` - Page header component
  - `navigation.html` - Navigation menu component
- **Location**: `stem/templates/components/`
- **Scope**: Modular UI components included in page templates

**Base Templates**

- **Pattern**: `{purpose}.html`
- **Purpose**: Foundation templates for inheritance
- **Examples**:
  - `base.html` - Base layout template with common structure
- **Location**: `stem/templates/`
- **Scope**: Common HTML structure, navigation, and script loading patterns

##### JavaScript Files

**Page-Specific Scripts**

- **Pattern**: `page.{pagename}.js`
- **Purpose**: Functionality specific to individual pages
- **Examples**:
  - `page.login.js` - Login page functionality
  - `page.conversation.js` - Conversation/debug console functionality
  - `page.profile.js` - User profile management
  - `page.admin.js` - Admin dashboard functionality
- **Loading**: Loaded only on their respective pages
- **Scope**: Page-specific DOM manipulation, event handlers, and business logic

**Component Scripts**

- **Pattern**: `component.{componentname}.js`
- **Purpose**: Reusable UI component functionality
- **Examples**:
  - `component.chatbar.js` - Chat sidebar component functionality
- **Loading**: Loaded on pages that use the specific component
- **Scope**: Component-specific behavior, state management, and interactions

**Shared Scripts**

- **Pattern**: `{functionality}.js` (for core shared functionality)
- **Purpose**: Common functionality used across multiple pages
- **Examples**:
  - `common.js` - Shared utilities, authentication, UI components, and navigation
- **Loading**: Loaded on all pages that require shared functionality
- **Scope**: Global utilities, authentication handling, theme management, snackbar system

**Plugin Scripts**

- **Pattern**: `plugin.{library}.js`
- **Purpose**: Third-party libraries and external dependencies
- **Examples**:
  - `plugin.chart.min.js` - Chart.js library
  - `plugin.chart.umd.min.js.map` - Chart.js source map
  - `plugin.json-highlight.js` - JSON syntax highlighting library
  - `plugin.marked.min.js` - Markdown parsing library
- **Loading**: Loaded on pages that require the specific library
- **Scope**: External library functionality, no custom code

##### CSS Files

**Main Stylesheets**

- **Pattern**: `{purpose}.css`
- **Purpose**: Main application styling
- **Examples**:
  - `style.css` - Main application stylesheet
  - `material-icons.css` - Material Icons font styles
  - `json-highlight.css` - JSON syntax highlighting styles
- **Location**: `stem/static/`
- **Scope**: Application-wide styling, component styles, and utility classes

##### Asset Files

**Images**

- **Pattern**: `{purpose}.{format}`
- **Purpose**: Application images and graphics
- **Examples**:
  - `logo-tatlock.png` - Application logo
  - `logo-tatlock-transparent.png` - Transparent logo variant
- **Location**: `stem/static/images/`
- **Scope**: Logos, icons, and other visual assets

**Favicon Files**

- **Pattern**: `{size}-{format}` or `{purpose}.{format}`
- **Purpose**: Browser favicon and app icons
- **Examples**:
  - `favicon.ico` - Standard favicon
  - `favicon-16x16.png` - 16x16 favicon
  - `android-chrome-192x192.png` - Android Chrome icon
- **Location**: `stem/static/favicon/`
- **Scope**: Browser and mobile app icons

**Fonts**

- **Pattern**: `{fontname}.{format}`
- **Purpose**: Custom fonts and icon fonts
- **Examples**:
  - `material-icons.ttf` - Material Icons TrueType font
  - `material-icons.woff` - Material Icons Web Open Font
- **Location**: `stem/static/fonts/`
- **Scope**: Custom typography and icon fonts

##### Configuration Files

**Application Config**

- **Pattern**: `{purpose}.{format}`
- **Purpose**: Application configuration and metadata
- **Examples**:
  - `manifest.json` - Web app manifest
  - `pyproject.toml` - Python project configuration
  - `requirements.txt` - Python dependencies
- **Location**: Project root or specific directories
- **Scope**: Application configuration, dependencies, and metadata

##### Benefits of Consistent Naming

**Organization**

- **Clear Purpose**: File names immediately indicate their purpose and scope
- **Easy Navigation**: Developers can quickly locate files by type and function
- **Logical Grouping**: Related files follow similar naming patterns
- **Scalability**: Easy to add new files following established patterns

**Maintainability**

- **Consistent Structure**: Uniform naming across the entire codebase
- **Reduced Confusion**: Clear distinction between different types of files
- **Easier Refactoring**: Predictable naming makes reorganization straightforward
- **Documentation**: File names serve as self-documenting code

**Development Workflow**

- **Quick Identification**: Developers can immediately understand file purpose
- **Dependency Management**: Clear loading order and relationships
- **Code Reviews**: Easier to review changes when file purposes are clear
- **Onboarding**: New developers can quickly understand project structure

##### Migration and Maintenance

**When Adding New Files**

1. **Follow Established Patterns**: Use the appropriate prefix for the file type
2. **Be Descriptive**: Choose names that clearly indicate purpose
3. **Maintain Consistency**: Don't create exceptions to established patterns
4. **Update Documentation**: Keep naming pattern documentation current

**When Renaming Files**

1. **Update All References**: Update all template files, imports, and documentation
2. **Maintain Backward Compatibility**: Ensure existing functionality continues to work
3. **Test Thoroughly**: Verify all pages and functionality work after changes
4. **Update Changelog**: Document significant naming changes

**Exception Handling**

- **Legacy Files**: Some files may not follow current patterns
- **Third-Party Libraries**: External libraries may have their own naming conventions
- **Documentation**: Always document why exceptions exist
- **Migration**: Plan to rename legacy files when practical

#### Jinja2 Template Integration Pattern

**IMPORTANT**: Follow the proper Jinja2 templating pattern for dynamic content:

**✅ Correct Pattern:**

- **HTML Structure in Templates**: Keep all HTML structure, table headers, and static content in Jinja2 templates
- **Always Present DOM**: HTML structure should always be present in the DOM, not conditionally created
- **JavaScript for Dynamic Updates**: Use JavaScript only to populate dynamic content (table rows, form values, etc.)
- **DOM Manipulation**: Create and append DOM elements for dynamic content instead of building HTML strings
- **Visibility Control**: Use CSS display properties to show/hide sections, not conditional HTML creation

**❌ Incorrect Pattern:**

- Building complete HTML strings in JavaScript
- Replacing entire container content with HTML strings
- Mixing template logic with JavaScript HTML generation
- Conditionally creating HTML structure based on visibility
- Hiding sections by removing them from DOM instead of using CSS

#### Template Structure Example

```html
<!-- In Jinja2 template (page.admin.html) - HTML structure always present -->
<div id="users-section" class="section">
    <div class="section-title">User Management</div>
    <table class="user-table">
        <thead>
            <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="users-table-body">
            <!-- Dynamic content populated by JavaScript -->
        </tbody>
    </table>
</div>

<!-- CSS controls visibility, not JavaScript -->
<style>
.section { display: none; }
.section.active { display: block; }
</style>
```

#### JavaScript Implementation Example

```javascript
// ✅ Correct: Update only dynamic content, HTML structure always exists
async function loadUsers() {
    const usersTableBody = document.getElementById('users-table-body');
    
    try {
        const response = await fetch('/admin/users');
        const users = await response.json();
        
        // Clear existing rows
        usersTableBody.innerHTML = '';
        
        // Add rows dynamically
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td>
                    <button onclick="editUser('${user.username}')">Edit</button>
                </td>
            `;
            usersTableBody.appendChild(row);
        });
    } catch (error) {
        usersTableBody.innerHTML = `
            <tr><td colspan="3">Error: ${error.message}</td></tr>
        `;
    }
}

// ✅ Correct: Control visibility with CSS, not DOM manipulation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected section
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }
    
    // Load data when section is shown
    if (sectionId === 'users' && typeof loadUsers === 'function') {
        loadUsers();
    }
}

// ❌ Incorrect: Building complete HTML in JavaScript
async function loadUsers() {
    const container = document.getElementById('users-content');
    let html = '<table><thead><tr><th>Username</th>...</tr></thead><tbody>';
    // ... building complete HTML string
    container.innerHTML = html;
}
```

#### Benefits of This Pattern

1. **Separation of Concerns**: HTML structure in templates, dynamic content in JavaScript
2. **Always Available DOM**: HTML elements are always present, no null reference errors
3. **Maintainability**: Easier to modify HTML structure without touching JavaScript
4. **Performance**: More efficient DOM manipulation
5. **Consistency**: Follows Jinja2 templating best practices
6. **Debugging**: Clearer separation makes debugging easier
7. **Reliability**: No timing issues with DOM element availability

#### When to Use Each Approach

**Use Jinja2 Templates For:**

- Page structure and layout
- Static content and headers
- Form structures
- Navigation elements
- CSS classes and styling structure
- **All HTML structure that should always be present**

**Use JavaScript For:**

- Populating dynamic table rows
- Updating form values
- Real-time data updates
- User interactions and events
- AJAX content loading
- **Controlling visibility with CSS display properties**

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

#### Authentication Testing Patterns

**CRITICAL**: Always test API endpoints and core functionality with proper user authentication. Tatlock has robust authentication testing infrastructure that must be used.

**Available Authentication Fixtures** (from `tests/conftest.py`):

```python
# Fixtures for authenticated testing
def test_api_endpoint(authenticated_admin_client):
    """Test API endpoint with real authenticated user session."""
    response = authenticated_admin_client.post("/cortex", json={
        "message": "Hello",
        "history": []
    })
    assert response.status_code == 200

def test_with_regular_user(authenticated_user_client):
    """Test with regular user permissions."""
    response = authenticated_user_client.get("/profile")
    assert response.status_code == 200
```

**API Test Harness** (from `tests/api_harness.py`):

```python
from tests.api_harness import TestAPIHarness

def test_custom_user_scenario():
    """Test with custom user creation and authentication."""
    harness = TestAPIHarness()

    # Create user with specific roles/groups
    user_details = harness.create_user("testuser", roles=["user"], groups=["users"])

    # Get authenticated client via real login
    client = harness.get_authenticated_client(user_details['username'], user_details['password'])

    # Test with real authentication
    response = client.post("/cortex", json={"message": "Test", "history": []})
    assert response.status_code == 200
```

**User Context Testing** (for tools and internal functions):

```python
@patch('stem.security.current_user')
def test_tool_with_user_context(mock_current_user):
    """Test tool functionality with mocked user context."""
    mock_user = MagicMock()
    mock_user.username = "testuser"
    mock_current_user.return_value = mock_user

    result = execute_memory_tool("overview")
    assert result["status"] == "success"
```

**Key Authentication Testing Principles**:

1. **Use Real Authentication**: Prefer `authenticated_admin_client` and `authenticated_user_client` fixtures for API tests
2. **Test User Isolation**: Verify users can only access their own data
3. **Session Management**: Tests use real login via `/login/auth` endpoint
4. **Automatic Cleanup**: All user fixtures automatically clean up created users
5. **Role-Based Testing**: Test different user roles (admin, user, moderator)

**When to Use Each Pattern**:

- **API Endpoints**: Always use `authenticated_admin_client` or `authenticated_user_client`
- **Tool Functions**: Use `@patch('stem.security.current_user')` for unit tests
- **Custom Scenarios**: Use `TestAPIHarness` for complex authentication scenarios
- **Integration Tests**: Use authenticated fixtures to test complete request flow

**Example: Testing New Architecture Component**:

```python
class TestNewArchitectureAuthenticated:
    """Test new architecture with proper authentication."""

    def test_capability_guard_flow(self, authenticated_admin_client):
        """Test CAPABILITY_GUARD with real user session."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "What's your name?",
            "history": []
        })

        assert response.status_code == 200
        data = response.json()
        assert "Tatlock" in data["response"]  # Should trigger butler identity

    def test_tool_execution_with_user_context(self, authenticated_admin_client):
        """Test tool execution with proper user context."""
        response = authenticated_admin_client.post("/cortex", json={
            "message": "What did we discuss before?",
            "history": []
        })

        assert response.status_code == 200
        # Tool should execute with proper username context
```

**Why This Matters**:

- **Real User Sessions**: Tests authenticate through actual login flow
- **User Isolation**: Verifies data access control works correctly
- **Tool Context**: Ensures tools receive proper user context
- **Security Validation**: Catches authentication and authorization bugs
- **Production Parity**: Tests match production authentication behavior

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

1. **Always Include Standards**: When using coding AI assistants (like Cursor, GitHub Copilot, Claude, GPT, etc.), always include the Tatlock coding standards from this `AGENTS.md` file as part of your prompt
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
      raise Exception(status_code=401, detail="Not authenticated")
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
    user = current_user
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return get_profile_page(request, user.model_dump())
```

#### Security/Admin Example

```python
def require_admin_role():
    user = current_user
    if not user or not security_manager.user_has_role(user.username, 'admin'):
        raise HTTPException(status_code=403, detail="Admin role required")
```

#### Benefits

- **Type Safety:** All user access is via a Pydantic model, not a dict.
- **No More Passing Usernames:** No need to pass username/roles through function calls.
- **Per-Request Isolation:** Each request gets its own user context, safe for async/concurrent code.
- **Consistent Template Usage:** Always pass `user.model_dump()` to templates.

#### When Adding New Endpoints

- Use `_: None = Depends(get_current_user)` in the signature.
- Use `user = current_user` in the body.
- Raise 401 if user is None.
- Pass `user.model_dump()` to templates.

#### Legacy Pattern Removal

- All legacy `current_user: dict = Depends(get_current_user)` and dict key access have been removed. Do not use dict-based user access in new code.

## Voice Input Implementation

### Overview

The voice input system integrates real-time audio capture with the chat interface, providing a natural way to interact with Tatlock using speech.

**Note**: Voice processing (audio transcription) has been removed from this version. The system operates in text-only mode.

### Architecture

- **Frontend**: Microphone button in chat interface with WebSocket audio streaming
- **Backend**: FastAPI WebSocket endpoint (voice processing disabled)
- **Processing**: Temporal context and language understanding pipeline (text-only)

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
        # Voice processing is not available
        logger.warning("Voice transcription is not available")
        return None
    
    async def process_voice_command(self, text: str) -> Dict[str, Any]:
        # Add to temporal context and extract intent
        self.temporal_context.add_interaction(text)
        intent = self.language_processor.extract_intent(text)
        return {"original_text": text, "intent": intent}
```

### Coding Patterns

#### WebSocket Audio Streaming

- **Binary Protocol**: Audio chunks sent with "audio:" prefix (returns error response)
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

- **Voice Processing**: Re-enable audio transcription with alternative libraries
- **Always-on Detection**: Background keyword spotting
- **Voice Synthesis**: Text-to-speech responses
- **Multi-language Support**: International voice recognition
- **Hardware Integration**: Raspberry Pi and embedded systems

## Database Schema

### System Database (system.db)

The system database contains global, shared data:

- **User authentication**: users, passwords, roles, groups
- **Tool registry**: tools, tool_parameters
- **Global system prompts**: rise_and_shine table

### User Databases ({username}_longterm.db)

Each user has their own isolated database containing:

- **Conversation memories**: memories, topics, memory_topics
- **Conversation metadata**: conversations, conversation_topics
- **Personal variables**: personal_variables_keys, personal_variables, personal_variables_join

### Critical: rise_and_shine Table Location

**IMPORTANT**: The `rise_and_shine` table MUST be in the system database (system.db), NOT in user databases.

**Purpose**: Contains Tatlock's global base system prompts and instructions that all users share.

**Why system database**:

- All users should have the same base instructions
- Ensures consistency across the system
- Simplifies prompt management and updates
- Prevents user-specific prompt variations

**Access**: The `get_base_instructions()` function reads from the system database and combines base prompts with enabled tool prompts.

**Dynamic System Prompts Architecture**:

- Base system prompts are stored in the `rise_and_shine` table
- Tool-specific prompts are stored in the `prompts` column of the `tools` table
- The `get_base_instructions()` function dynamically combines:
  1. Base prompts from `rise_and_shine` table (where enabled = 1)
  2. Tool prompts from `tools` table (where enabled = 1 and prompts IS NOT NULL)
- This ensures the LLM only receives instructions for available tools
- Disabled tools automatically exclude their prompts from system instructions
- Maintains clean separation between base system behavior and tool-specific guidance

**NEVER move this table to user databases** - it would break the system architecture and create inconsistencies.

## User Context Management

### Current User Context

The application uses a global user variable system to avoid passing user data through function parameters:

```python
from stem.security import current_user

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
    global current_user
    current_user = user_model
    return user_model

# In endpoint functions
def some_endpoint(_: None = Depends(get_current_user)):
    user = current_user
    # Access user attributes directly
    username = user.username
    roles = user.roles
```

### Tool Functions

For tool functions that can be called from various contexts (not just HTTP endpoints), use error responses instead of exceptions:

```python
def execute_some_tool(parameter: str) -> dict:
    """
    Example tool function that uses current user context.
    """
    try:
        user = current_user
        if user is None:
            return {"status": "error", "message": "User not authenticated"}
        
        # Tool logic here
        result = process_data(user.username, parameter)
        
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Tool error: {e}")
        return {"status": "error", "message": f"Tool failed: {e}"}
```

### Benefits

- **Type Safety**: UserModel provides type hints and validation
- **Clean APIs**: No need to pass user data through function parameters
- **Consistency**: Uniform user access pattern across the application
- **Security**: User data is properly encapsulated and validated
- **Context Flexibility**: Tools work in both HTTP and non-HTTP contexts

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
4. User session is created with global current_user variable
5. User data is available throughout the request lifecycle

> **Note:** The `stem/security.py` module is now import-clean. Only the following imports are required for authentication and authorization:
>
> ```python
> from stem.security import (
>     security_manager, get_current_user, require_admin_role, login_user, logout_user, current_user
> )
> ```
>
> All unused imports and variables have been removed for clarity and maintainability. Do not import unused dependencies or legacy variables.

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
  - **installation/**: Database setup and migrations
- **hippocampus/**: Memory and conversation management
- **cortex/**: AI agent logic
- **tests/**: Comprehensive test suite

### Patterns

- **Dependency Injection**: FastAPI dependencies for authentication
- **Global Variables**: Global current_user variable for user data
- **Pydantic Models**: Type-safe data structures
- **Migration System**: Automatic database schema updates
- **Test Isolation**: Temporary databases for testing

## Development Guidelines

### Adding New Features

1. **Database Changes**: Use migration system for schema updates
2. **User Context**: Access user data via `current_user` global variable
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

## **Logging Standards**

### **Log Level Guidelines**

- **Use `logger.debug()` by default** for all logging unless specified otherwise
- **Use `logger.error()` inside exception handlers** - always use error level for exceptions
- **Use `logger.info()` only for important business events** (user actions, system state changes, etc.)
- **Use `logger.warning()` for recoverable issues** that don't prevent normal operation

### **Logging Best Practices**

```python
# ✅ Good - Debug level by default
logger.debug(f"Processing user request: {user_id}")

# ✅ Good - Error level in exceptions
try:
    result = some_operation()
except Exception as e:
    logger.error(f"Operation failed for user {user_id}: {e}")

# ✅ Good - Info level for important events
logger.info(f"User {user_id} logged in successfully")

# ❌ Avoid - Info level for routine operations
logger.info(f"Processing request: {request_data}")  # Should be debug
```

### **Exception Logging Pattern**

```python
try:
    # Operation code
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
    # Handle specific exception
except Exception as e:
    logger.error(f"Unexpected error in {function_name}: {e}")
    # Handle general exception
```

### **Context in Log Messages**

- Include relevant context (user ID, operation name, parameters)
- Use structured logging when possible
- Avoid logging sensitive information (passwords, tokens, etc.)

### **Performance Considerations**

- Use `logger.isEnabledFor(logging.DEBUG)` for expensive debug operations
- Avoid string formatting in debug calls that might not be logged

```

### Preferred Dynamic Content Rendering Pattern (All Authenticated/Admin Pages)

- **Always render the static HTML frame** (all containers, sections, and bounding elements) in the Jinja2 template. This includes all page structure, navigation, section wrappers, and content containers.
- **Never remove or replace the frame, section, or container in JavaScript.**
- **Only update the dynamic content area** (e.g., `<tbody>`, `<ul>`, `.card-list`, etc.) for loading, error, and data states.
- **Always provide a loader pattern** (e.g., a loading row, spinner, or message) inside the dynamic content container, not by replacing the frame or section.
- **Defensive coding:** Always check for the dynamic content element in JS before updating.
- **This pattern is required for all password/authenticated pages and admin pages.**

#### Example (Jinja2 Template - Table):
```html
<table>
  <thead>...</thead>
  <tbody id="users-table-body">
    <tr><td colspan="7" class="loading">Loading users...</td></tr>
  </tbody>
</table>
```

#### Example (Jinja2 Template - List)

```html
<div class="card-list-container">
  <ul id="user-list">
    <li class="loading">Loading users...</li>
  </ul>
</div>
```

#### Example (JavaScript)

```javascript
// For tables
const usersTableBody = document.getElementById('users-table-body');
if (!usersTableBody) return;
usersTableBody.innerHTML = '<tr><td colspan="7" class="loading">Loading users...</td></tr>';
// ... fetch and populate rows ...

// For lists
const userList = document.getElementById('user-list');
if (!userList) return;
userList.innerHTML = '<li class="loading">Loading users...</li>';
// ... fetch and populate list items ...
```

- Never update or replace the frame, section, or container HTML in JS.
- Only update the dynamic content area (e.g., `<tbody>`, `<ul>`, etc.).
- Always show loading and error states inside the dynamic content area.
- This ensures the DOM is always consistent and prevents null reference errors.

**This pattern applies to all dynamic content, not just tables.**

Update the JavaScript Coding Standards and Jinja2 Template Integration Pattern sections to reflect this as the required approach for all authenticated/admin pages.

- **Page-specific JavaScript files**: All scripts that are only used for a single page must be named using the pattern `page.[pagename].js` (e.g., `page.admin.js`, `page.profile.js`, `page.login.js`, `page.conversation.js`). This convention ensures clarity, maintainability, and consistency across the codebase.

### UI/UX and Frontend Coding Standards

#### Add/Create Button Placement

- **Standard Placement:** For table sections, always place the add/create button above the section header/title and right-aligned using flexbox. This ensures a clear, consistent, and user-friendly UI.
- **Pattern:**

  ```html
  <div class="add-btn-row" style="display: flex; justify-content: flex-end; padding: 0 24px; margin-bottom: 0.5em;">
      <button class="add-btn">Add New</button>
  </div>
  <div class="section-title">Section Name</div>
  <table>...</table>
  ```

- **CSS:**

  ```css
  .add-btn-row {
      display: flex;
      justify-content: flex-end;
      margin-bottom: 0.5em;
      padding: 0 24px;
  }
  .section-title {
      font-size: 1.5em;
      font-weight: 600;
      position: relative;
      margin-bottom: 18px;
      padding: 0 24px;
  }
  .section-title::after {
      content: '';
      display: block;
      position: absolute;
      left: 24px;
      right: 24px;
      bottom: -8px;
      height: 3px;
      background: var(--accent-color);
      border-radius: 2px;
      z-index: 0;
  }
  ```

- **Apply to:** All tables with create functionality (users, roles, groups, etc.)
- **Rationale:** Ensures a consistent, modern, and user-friendly UI across all admin sections.
