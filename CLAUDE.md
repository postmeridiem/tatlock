# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**IMPORTANT**: The `AGENTS.md` file contains the authoritative instruction set for all developers and LLMs working on this project. Any conflicting guidance between this file and `AGENTS.md` should defer to `AGENTS.md`, which supersedes all other instruction files including this one.

## Project Overview

Tatlock is a brain-inspired conversational AI platform with built-in authentication, security, and comprehensive user management. It provides a context-aware, tool-using agent with persistent memory, extensible skills, and a modern web interface using local LLMs via Ollama.

## Architecture

The codebase is organized into modules inspired by brain regions:

- **cortex/**: Core agent logic implementing 4.5-phase prompt architecture with butler personality
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

## Core Processing: 4.5-Phase Architecture

Tatlock's cortex module implements a sophisticated 4.5-phase prompt processing architecture for optimal performance and context management:

### Phase Flow Overview

```
User Request → Phase 1: Assessment → Phase 2/4: Routing → Phase 4.5: Quality Gate → Response
```

### Phase Details

**Phase 1: Initial Assessment**
- **Purpose**: Intelligent routing with CAPABILITY_GUARD protection
- **Function**: Determines if question needs tools, triggers guards, or can be answered directly
- **CAPABILITY_GUARD**: Detects sensitive topics (identity, capabilities, temporal, security) for full-context processing
- **Outputs**: `DIRECT`, `TOOLS_NEEDED`, or `CAPABILITY_GUARD: [REASON]`

**Phase 2: Tool Selection** *(Conditional)*
- **Purpose**: Efficient tool selection when tools are needed
- **Function**: Selects minimal required toolset from available tools
- **Optimization**: Reduces tool schema overhead from 17 tools to 0-5 tools per request

**Phase 3: Tool Execution** *(Conditional)*
- **Purpose**: Execute selected tools with proper user context
- **Function**: Handles tool calls, retries, and result aggregation
- **Security**: Automatic username injection for memory/personal tools

**Phase 4: Response Formatting**
- **Purpose**: Apply butler personality and format final response
- **Standard Path**: Butler formatting (concise, formal, ends with "sir")
- **CAPABILITY_GUARD Path**: Full rise_and_shine context for sensitive topics
- **Output**: Properly formatted response ready for quality validation

**Phase 4.5: Quality Gate**
- **Purpose**: Final validation and edge case protection
- **Checks**: Safety, completeness, butler persona, known edge case patterns
- **Fallbacks**: Generates appropriate responses for detected issues
- **Result**: Approved response or corrected fallback

### Key Architecture Benefits

- **Performance**: 2-7 second Phase 1 analysis, ~0.003 second routing decisions
- **Context Management**: Proper butler identity in sensitive scenarios
- **Tool Efficiency**: Dynamic tool loading with minimal overhead
- **Quality Assurance**: Comprehensive edge case detection and handling
- **Maintainability**: Clear separation of concerns across phases

### Implementation Files

- **`cortex/tatlock.py`**: Main 4.5-phase processor with all classes
- **`sample.md`**: Complete architecture specification and examples
- **`tests/test_4_5_phase_architecture.py`**: Comprehensive test suite
- **`stem/debug_logger.py`**: Phase-specific debug logging

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
python -m pytest tests/test_4_5_phase_architecture.py

# Test specific architecture components
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

Tools are implemented using the dynamic loading system:

1. Create tool function in appropriate brain module (e.g., `cerebellum/weather_tool.py`)
2. Add to database schema in `stem/installation/database_setup.py` with correct module path
3. Tool is automatically discovered and loaded by the dynamic system in `stem/dynamic_tools.py`
4. Enable in database by updating `enabled = 1` in tools table
5. Use `execute_tool(tool_key, **kwargs)` for dynamic execution or access via `AVAILABLE_TOOLS[tool_key]` for backward compatibility

### User Context Management

```python
from stem.security import current_user

# Access current user (global variable set by dependency)
user = current_user
if user is None:
    return {"status": "error", "message": "User not authenticated"}

username = user.username
```

### 4.5-Phase Architecture Debugging

The new architecture includes comprehensive debug logging for development and troubleshooting:

```python
# Debug logs are automatically created in logs/conversations/ directory
# Each conversation gets a session-specific log file

# Key log patterns to look for:
# Phase transitions: "Phase 1: Initial Assessment", "Phase 4.5: Quality Gate"
# LLM calls: Request/response pairs with timing
# Tool execution: Tool name, arguments, results, timing
# Quality Gate: Approval/rejection decisions with reasoning

# Manual testing with debug output:
from cortex.tatlock import process_chat_interaction
result = process_chat_interaction("Test message", [], "admin", "debug-session-123")
# Check logs/conversations/debug-session-123_*.log for detailed phase tracking
```

**Debug Log Structure:**
- **Session Initialization**: User, message preview, setup timing
- **Phase 1**: Assessment prompt, LLM response, routing decision
- **Phase 2**: Tool selection (if applicable)
- **Phase 3**: Tool execution with individual tool timing
- **Phase 4**: Response formatting (butler vs capability guard)
- **Phase 4.5**: Quality gate evaluation and final approval

**Performance Monitoring:**
- Phase 1: 2-7 seconds (LLM-intensive analysis)
- Phase 2: ~0.003 seconds (efficient routing)
- Tool execution: Variable based on tools used
- Phase 4: 1-3 seconds (response formatting)
- Phase 4.5: <1 second (quality validation)

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
