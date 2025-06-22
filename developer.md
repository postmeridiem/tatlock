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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
    ]
)
```

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

## Module Development

### Adding New Modules

1. **Create module directory**: Follow the brain-inspired naming convention
2. **Add `__init__.py`**: Make it a proper Python package
3. **Create `readme.md`**: Document the module's purpose and features
4. **Add tests**: Create comprehensive test coverage
5. **Update main.py**: Integrate with the main application

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
- **ReDoc**: `http://localhost:8000/redoc`

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

- **README Files**: Keep module README files up to date
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

- [README.md](README.md) - General overview and installation
- [moreinfo.md](moreinfo.md) - In-depth technical information
- [cortex/readme.md](cortex/readme.md) - Core agent logic documentation
- [hippocampus/readme.md](hippocampus/readme.md) - Memory system documentation
- [stem/readme.md](stem/readme.md) - Core utilities and infrastructure
- [parietal/readme.md](parietal/readme.md) - Hardware monitoring and performance 