# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT**: The `AGENTS.md` file contains the authoritative instruction set for all developers and LLMs working on this project. Any conflicting guidance between this file and `AGENTS.md` should defer to `AGENTS.md`, which supersedes all other instruction files including this one.

## Project Overview

Tatlock is a brain-inspired conversational AI platform with built-in authentication, security, and comprehensive user management. It provides a context-aware, tool-using agent with persistent memory, extensible skills, and a modern web interface using local LLMs via Ollama.

## Architecture

The codebase is organized into modules inspired by brain regions:

- **cortex/**: Core agent logic and decision-making with agentic loop
- **hippocampus/**: Memory system with per-user databases and conversation storage
- **stem/**: Authentication, admin dashboard, tools, utilities, and Jinja2 templating
- **parietal/**: Hardware monitoring, performance analysis, and automatic model selection
- **occipital/**: Visual processing and screenshot testing
- **cerebellum/**: External API tools (web search, weather)
- **temporal/**: Language processing and temporal context (voice disabled)
- **thalamus/**: Information routing (planned)
- **amygdala/**: Emotional processing (planned)

Key architectural principles:

- **User Isolation**: Each user has their own database (`{username}_longterm.db`) for complete privacy
- **Tool-Driven**: Modular tool system with database-driven registration
- **Session Authentication**: Secure session-based authentication with cookies
- **Brain-Inspired Design**: Modules mirror brain functions for intuitive organization

## Common Development Commands

### Application Management

```bash
# Start the application
./wakeup.sh

# Install dependencies and setup
./install_tatlock.sh

# Check Python version compatibility
./test_python_version.sh
```

### Development Workflow

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the application directly
python main.py

# Run tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_cortex_agent.py

# Run with verbose output
python -m pytest -v tests/
```

### Testing

- **Main test command**: `python -m pytest tests/`
- **Single test**: `python -m pytest tests/test_[module_name].py`
- **Verbose output**: `python -m pytest -v tests/`
- **Visual testing**: `python occipital/run_tests.py`
- **Test cleanup**: Uses comprehensive cleanup system for user data isolation

## Key Development Patterns

### Automatic Model Selection

Tatlock automatically selects the optimal LLM model based on hardware:

- **Hardware Detection**: `parietal/hardware.py` classifies system capabilities
- **Model Selection**: Removes manual `ollama_model` database configuration
- **Apple Silicon Optimized**: Special handling for M1/M2 compatibility
- **Config Flow**: `config.py` → `classify_hardware_performance()` → optimal model

### Tool Development

Tools are implemented following a specific pattern:

1. Create tool function in appropriate brain module (e.g., `cerebellum/weather_tool.py`)
2. Add to database schema in `stem/installation/database_setup.py`
3. Register function in `stem/tools.py` AVAILABLE_TOOLS dictionary
4. Enable in database by updating `enabled = 1` in tools table

### User Context Management

```python
from stem.security import current_user

# Access current user (global variable set by dependency)
user = current_user
if user is None:
    return {"status": "error", "message": "User not authenticated"}

username = user.username
```

### Database Patterns

```python
# Standard database operation with error handling
try:
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM table WHERE field = ?", (param,))
    result = cursor.fetchall()
    conn.close()
    return result
except Exception as e:
    logger.error(f"Database error: {e}")
    return []
```

### Frontend Development

- **Jinja2 Templating**: Server-side rendering with shared components
- **Material Design**: Clean, responsive web interface
- **JavaScript Patterns**: ES6+, async/await, class-based architecture
- **File naming**: `page.{name}.js` for page-specific, `component.{name}.js` for reusable components

## Important Files and Locations

### Configuration

- `pyproject.toml`: Project metadata and version (single source of truth)
- `requirements.txt`: Python dependencies
- `config.py`: Application configuration and environment variables
- `.env`: API keys and environment settings (not in repo)

### Core Application Files

- `main.py`: FastAPI application entry point and routing
- `wakeup.sh`: Application startup script
- `install_tatlock.sh`: Complete installation and setup script

### Documentation

- `AGENTS.md`: Comprehensive developer guide with all standards and patterns
- `README.md`: Installation instructions and project overview
- `troubleshooting.md`: Installation and runtime issue resolution
- `moreinfo.md`: In-depth technical information
- Module `readme.md` files in each brain module directory

### Database Schema

- `stem/installation/database_setup.py`: Database schema and migration functions
- System database (`system.db`): Users, roles, tools, global system prompts
- User databases (`{username}_longterm.db`): Per-user conversations, memories, topics

## Security Considerations

- **Input Validation**: All inputs validated through Pydantic models
- **SQL Injection Prevention**: Parameterized queries exclusively
- **User Isolation**: Complete data separation between users
- **Password Security**: bcrypt hashing with unique salts
- **Session Management**: Secure cookie-based authentication

## Testing Strategy

- **Test Isolation**: Uses temporary databases and comprehensive cleanup
- **User Fixtures**: Automatic user creation and cleanup in tests
- **Module Coverage**: Tests for all core modules and functionality
- **Visual Testing**: Screenshot comparison for UI regression testing

## Key Dependencies

- **FastAPI**: Web framework and API
- **Ollama**: Local LLM inference
- **SQLite**: Database storage
- **Jinja2**: Server-side templating
- **bcrypt**: Password hashing
- **pytest**: Testing framework
- **Playwright**: Visual testing

The project requires Python 3.10 exactly for optimal compatibility and uses a virtual environment for dependency isolation.
