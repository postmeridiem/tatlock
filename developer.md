# Developer Guide

This guide contains developer-specific information for working with Tatlock, including logging, debugging, performance monitoring, and development practices.

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

### Code Organization

- **Brain-Inspired Design**: Codebase organized into modules inspired by brain regions
- **Clean Separation**: Tests go in `tests/`, security in `security.py`, etc.
- **Modular Architecture**: Each module has clear responsibilities and interfaces

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
- **[Installation Troubleshooting](INSTALLATION_TROUBLESHOOTING.md)** - Common installation issues and solutions

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
    password: str
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

#### Performance
1. **Database Optimization**: Use efficient queries and proper indexing
2. **Caching**: Cache frequently accessed data
3. **Lazy Loading**: Load resources only when needed
4. **Monitoring**: Track performance metrics and optimize bottlenecks

#### AI-Assisted Development
1. **Always Include Standards**: When using coding AI assistants (like GitHub Copilot, Claude, GPT, etc.), always include the Tatlock coding standards from this `developer.md` file as part of your prompt
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