# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.24] - 2025-01-20

### Added

- **Performance Optimization**: Major improvements to response times and system reliability
  - Switched default model from phi4-mini:3.8b-q4_K_M to mistral:7b for better performance
  - Added explicit 20-second timeouts to Ollama calls to prevent indefinite hangs
  - Implemented per-phase timing logs to identify performance bottlenecks
  - Added health endpoint (/health) for basic server status checking
  - Enhanced debug logger to force file creation regardless of DEBUG_MODE setting

### Fixed

- **CAPABILITY_GUARD Performance**: Dramatic improvement in identity/temporal query handling
  - Added regex-based fallback detection for identity/temporal queries ("What is your name?", etc.)
  - Implemented fast-return path for guard cases to avoid LLM latency
  - Reduced guard query response time from 60s timeout to ~22.5s
  - Fixed "What is your name?" timeout issues with reliable fast-path routing

### Changed

- **Tool System Architecture**: Improved maintainability and user-driven configuration
  - Removed hard-coded tool short-circuits in favor of LLM-driven tool catalog decisions
  - Added UI-driven action hook: when API keys are saved, tools are automatically enabled/disabled via database
  - Removed startup auto-toggling; tool availability is now purely UI-driven
  - Fixed hippocampus tool exports to resolve "Function not found" warnings at startup

### Performance

- **Response Time Improvements**: Significant reduction in query processing times
  - DIRECT queries: ~19s (down from 60s+ timeouts)
  - GUARD queries: ~22.5s (down from 60s timeouts) 
  - TOOLS_NEEDED queries: Proper routing with tool availability checking
  - Overall system responsiveness improved by 60-70% for most query types

## [0.3.23] - 2025-01-17

### Added

- **Comprehensive Security Hardening**: Complete security strategy implementation
  - Pinned all package versions to exact versions (84 dependencies) to prevent supply chain attacks
  - Created requirements-lock.txt with all transitive dependencies for reproducible builds
  - Added security scanning tools: safety==3.2.0, bandit==1.7.10, pip-audit==2.7.3
  - Created comprehensive security scan script in stem/scripts/security_scan.sh
  - Updated AGENTS.md with security guidelines for LLMs to prevent "poisoned well" attacks
  - Created stem/SECURITY_STRATEGY.md with complete security strategy documentation
  - Added security startup tests to verify compatibility after version pinning
  - Updated README to specify Python 3.10 exactly (matching install script requirements)
  - Fixed greenlet compatibility issue with Python 3.10 (was causing build failures on Python 3.13)

### Security

- **Supply Chain Protection**: All dependencies now pinned to exact versions
- **Vulnerability Scanning**: Automated security scanning with Safety, Bandit, and pip-audit
- **Dependency Auditing**: Comprehensive dependency vulnerability detection
- **AI Assistant Security**: Mandatory security guidelines for all LLM interactions
- **Version Control**: Lock files ensure reproducible builds across environments
- **Compatibility Testing**: Verified Tatlock starts successfully with all pinned dependencies

## [0.3.22] - 2025-01-16

### Added

- **Bazzite Support**: Full compatibility with Bazzite immutable Fedora-based gaming distro
  - Automatic detection of Bazzite system using rpm-ostree and /etc/os-release
  - Homebrew-based installation for all dependencies (Python 3.10, Ollama, etc.)
  - User systemd service support (no root privileges required)
  - Comprehensive troubleshooting documentation for immutable systems
  - PATH configuration for Homebrew Python 3.10 vs system Python 3.13

### Fixed

- **Model Fallback Updates**: Replaced gemma2:2b fallbacks with phi4-mini:3.8b-q4_K_M for better tool support
  - Updated hardware classification fallback from gemma2:2b to phi4-mini:3.8b-q4_K_M
  - Updated config.py fallback models to use tool-capable phi4-mini model
  - Fixed hardware config generation to properly escape JSON in HARDWARE_SUMMARY
  - Ensures all fallback scenarios use models that support function calling
  - Prevents tool execution failures when hardware classification fails

- **Documentation Accuracy**: Updated MEMORY_SYSTEM.md to reflect actual implemented state
  - Removed outdated "Future Schema Refactoring" section (schema already implemented)
  - Updated "Known Issues" to reflect resolved problems
  - Documented active dual-write system as current implementation
  - Corrected schema status from "planned" to "completed" for message-level storage
  - Updated optimization opportunities to reflect current state vs future plans

## [0.3.21] - 2025-10-08

### Added

- **Version-Based Migration System**: Complete database migration infrastructure
  - database_migrations.md for tracking SQL migrations by version
  - migration_runner.py for automated migration execution on startup
  - Pre-boot admin mode prevents user connections during migrations
  - Automatic integrity checks (foreign keys, schema validation)
  - Transaction-based rollback support
  - migrate_database.sh CLI tool for manual migrations

- **Message-Level Storage Schema**: New conversation_messages table for efficient message storage
  - Sequential message numbering (1, 2, 3...) for direct range queries
  - Separate rows for user and assistant messages
  - Eliminates ~93% data duplication from full_conversation_history JSON blobs
  - Indexed on conversation_id, message_number, and timestamp
  - Schema version tracking in conversations table

- **Git Commit Guidelines**: Explicit rules added to CLAUDE.md and AGENTS.md
  - Prohibits unsolicited co-authored-by messages
  - Prohibits "Generated with Claude Code" attribution
  - Enforces clean, professional commit messages only

### Changed

- **Memory System Architecture**: Migrated from interaction-level to message-level storage
  - Primary storage: conversation_messages table (one row per message)
  - Analytics storage: memories table retained for interaction-level queries
  - Conversations table extended with schema_version, compact_summary, compacted_up_to
  - All read operations now use conversation_messages for better performance
  - Simplified write path with single transaction for both tables

- **Database Baseline Schema**: Updated to include v0.3.20 schema by default
  - New databases created with conversation_messages table
  - Default schema_version=2 for new conversations
  - Existing databases migrated automatically on startup

- **Test Infrastructure**: Enhanced Ollama mocking for conversation compacting tests
  - Mock now covers both cortex.tatlock.ollama and hippocampus.conversation_compact.ollama
  - All 37 memory system tests passing

### Fixed

- **Foreign Key Bug**: Fixed conversation_topics foreign key reference
  - Changed from memories(conversation_id) to conversations(conversation_id)
  - Resolved integrity check failures on migration

- **Query Performance**: Eliminated UNION ALL pattern for message retrieval
  - Direct indexed queries using message_number
  - Range queries: WHERE message_number > ? ORDER BY message_number
  - Significantly faster than timestamp-based sorting

### Removed

- MEMORY_SYSTEM_ANALYSIS.md (analysis complete, refactoring implemented)

## [0.3.20] - 2025-10-04

### Added

- **Conversation Compacting System**: Automatic conversation summarization to reduce token usage
  - Conservative LLM-based summarization preserving ALL facts, names, dates, and numbers
  - Automatic compacting every 50 messages (25 user+assistant interaction pairs)
  - Non-overlapping compact mechanism (messages 1-50, 51-100, 101-150, etc.)
  - Smart context loading combining compact summary with recent uncompacted messages
  - New `conversation_compacts` table with indexes for efficient querying
  - Background thread execution for transparent user experience
  - Enables conversations of 200+ messages without context window limitations

- **Memory System Documentation**: Comprehensive documentation for memory architecture
  - `hippocampus/MEMORY_SYSTEM.md` (43KB) - Complete reference covering database architecture, Multi-phase prompt system, conversation compacting, and implementation patterns
  - Clear terminology definitions (message vs interaction vs turn)
  - Complete Multi-phase flow examples with CAPABILITY_GUARD
  - Conservative summarization prompt design
  - Database context loading patterns

- **Conversation Compacting Tests**: Comprehensive test suite for compacting system
  - 7 test functions covering threshold detection, context loading, incremental compacting, and data preservation
  - Tests validate non-overlapping guarantee and conservative summarization
  - Full API stack integration following Tatlock testing standards
  - 100% test coverage of compacting functionality

### Changed

- **Cortex Integration**: Multi-phase architecture now uses database context loading
  - Phase 1 assessment loads compact summary + recent messages from database
  - Eliminates client-side history management (passes empty array for `full_llm_history`)
  - Solves exponential data duplication problem in `full_conversation_history` field
  - Background compacting triggered automatically after each interaction
  - Context loading integrated into `ProcessingContext` model

- **Documentation Updates**: Corrected COMPACT_INTERVAL documentation across all files
  - Fixed AGENTS.md, CLAUDE.md, and hippocampus/readme.md to reflect COMPACT_INTERVAL=50
  - Updated all examples to show correct boundaries (1-50, 51-100, 101-150)
  - Clarified terminology: 50 messages = 25 interactions

### Fixed

- **Message Count Tracking**: Fixed conversation message_count increment bug
  - Changed from +1 to +2 per interaction in `remember.py`
  - Ensures `conversations.message_count` accurately reflects total messages (user + assistant)
  - Each `save_interaction()` adds 1 user message + 1 assistant reply = 2 messages

### Removed

- **Old Flow Documentation**: Removed obsolete `tatlock_prompt_flow_examples.md` (1014 lines)
  - Replaced by comprehensive MEMORY_SYSTEM.md documentation

## [0.3.19] - 2025-10-03

### Added

- **User-Selectable Performance Tier**: Installation now prompts for automatic or manual tier selection
  - Choose between automatic hardware detection (recommended) or manual tier selection
  - Manual selection offers three options: Low (phi4-mini:3.8b-q4_K_M), Medium (mistral:7b), High (gemma3-cortex:latest)
  - Re-running installer detects existing configuration and offers reconfiguration without breaking install
  - Added `SELECTION_METHOD` field to `hardware_config.py` tracking whether tier was auto or manually selected
  - Updated installer to display hardware detection results before prompting user
  - Enhanced user experience with clear tier descriptions and model information

### Changed

- **Installer Flow**: Enhanced `install_tatlock.sh` with user-friendly tier selection prompts
  - Detects existing `hardware_config.py` and offers to keep or reconfigure
  - Shows automatic hardware detection results with reasoning
  - Presents clear choice between automatic (recommended) and manual selection
  - Displays final configuration summary before continuing
  - Safe to re-run without reinstalling dependencies unnecessarily

- **Documentation**: Updated AGENTS.md with comprehensive performance tier selection guide
  - Added "Performance Tier Selection" section with installation workflow
  - Documented reconfiguration process for existing installations
  - Updated manual override instructions for testing
  - Cleaned up CLAUDE.md to simple pointer to AGENTS.md for authoritative guidance

### Fixed

- **Dependency Resolution**: Updated jinja2 from 3.1.3 to 3.1.4 to resolve conflict with instructor==1.7.5
- **Ollama Startup**: Added wait and verification logic for Ollama service initialization
  - macOS: 3-second initial wait + up to 10 verification attempts
  - Linux: 2-second wait after systemctl start
  - Prevents EOF errors when models download before Ollama is ready
- **Hardware Config Syntax**: Fixed HARDWARE_SUMMARY quote escaping in generated `hardware_config.py`

### Added

- **Hardware-Dependent Model Selection**: Automatic LLM model selection based on system hardware capabilities
  - Hardware classification system in `parietal/hardware.py` (`classify_hardware_performance()`)
  - Automatic detection of Apple Silicon with Mistral optimization for M1/M2 compatibility
  - Three performance tiers: High (gemma3-cortex:latest), Medium (mistral:7b), Low (phi4-mini:3.8b-q4_K_M)
  - Upgraded low-tier model from gemma2:2b to phi4-mini for better tool support with smaller size
  - Removed manual `ollama_model` database configuration in favor of automatic selection
  - Updated installer to download optimal model during installation
  - New API endpoint: `GET /parietal/hardware/classification`
  - Installation-time hardware config file generation (`hardware_config.py`)
  - Manual override documentation for testing different models via `hardware_config.py` editing

- **Advanced Multi-Phase Prompt Architecture**: Complete redesign for optimal performance and reliability
  - **Phase 1**: Initial Assessment - Structured capability detection with CAPABILITY_GUARD routing
  - **Phase 2**: Tool Selection - Intelligent tool catalog selection when needed
  - **Phase 3**: Tool Execution - Parallel execution of selected tools with error handling
  - **Phase 4**: Response Formatting - Butler persona application with context integration
  - **Phase Multi**: Quality Gate - Final validation and edge case detection with fallback mechanisms
  - **CAPABILITY_GUARD**: LLM-based detection system preventing identity/capability leakage in lean phases
  - **File renamed**: `cortex/agent.py` → `cortex/tatlock.py` using `git mv` (represents the essence of the butler)
  - **Code optimization**: Removed 319 lines (24% reduction) while adding comprehensive functionality
  - **Performance**: Phase 1: 5-7 seconds, Total response: 8-27 seconds with graceful degradation

- **Middleware Architecture Refactoring**: Clean separation following FastAPI best practices
  - New `stem/middleware.py` for request timing, exception handling, and logging
  - Enhanced `stem/security.py` with modular security middleware setup
  - Clean startup logging with minimal emoji usage (keeping only status indicators)
  - WebSocket authentication middleware

### Changed

- **Configuration**: `config.py` now uses `get_automatic_ollama_model()` instead of database lookup
- **Database Schema**: Removed `ollama_model` setting from system_settings with migration support
- **Tool Loading**: Core tools (memory/personal data) always loaded, extended tools (weather/web) catalog-based only
- **Agent Processing**: `cortex/tatlock.py` (renamed from `agent.py`) now uses advanced Multi-phase system
  - Completely refactored `TatlockProcessor` class with phase-specific prompt construction
  - Implemented `PromptBuilder` class for consistent prompt formatting across phases
  - Added `QualityGate` class for edge case detection and response validation
  - Enhanced structured parsing with Pydantic models (`CapabilityAssessment`, `ToolSelection`)
  - Improved error handling with graceful fallback mechanisms for LLM parsing failures
- **Database Optimization**: Updated `hippocampus/database.py` for core vs extended tool separation
- **Installer**: Hardware detection and model-specific downloads during `install_tatlock.sh`
- **Documentation**: Updated README.md, AGENTS.md, CLAUDE.md, and parietal/readme.md with hardware selection info

- **Enhanced Testing Infrastructure**: Comprehensive test suite for new architecture
  - New `tests/test_5_phase_architecture.py` with full authentication-based testing patterns
  - Updated `tests/benchmark_all_tiers.py` compatible with Multi-phase system performance measurement
  - Systematic testing of all phase flows (direct answers, CAPABILITY_GUARD, tool execution, edge cases)
  - Test isolation with proper user data cleanup and session management
  - Authentication fixtures following existing patterns in `tests/conftest.py`

- **Dynamic Tool System Enhancements**: Improved modularity and error handling
  - Enhanced `stem/tools.py` with better LazyToolDict implementation for testing compatibility
  - Updated tool execution error handling and user context management
  - Fixed `execute_find_personal_variables` parameter compatibility issues
  - Improved tool loading and caching mechanisms for better performance

- **Comprehensive Documentation Updates**: Complete specification and usage guides
  - **New `sample.md`**: 1000+ line comprehensive Multi-phase architecture specification
  - Detailed flow examples for all scenarios (direct answers, identity questions, weather queries, complex memory)
  - CAPABILITY_GUARD mechanism documentation with reasoning examples
  - Quality Gate implementation guide with edge case database and mitigation strategies
  - Updated `CLAUDE.md` with complete Multi-phase architecture section and debugging guidance
  - Enhanced `AGENTS.md` with authentication testing patterns and development standards

- **Agent Response Optimization**: Fixed system prompts to reduce verbosity and tool bias
  - Updated personality prompt to preserve British butler character while emphasizing conciseness
  - Modified memory tool prompts to be conditional and specific, reducing unnecessary tool usage
  - Added explicit guidance to answer name questions directly without memory checks
  - Fixed overly verbose responses for simple questions like "what is your name?"
  - Updated database setup script (`stem/installation/database_setup.py`) with improved prompts for fresh installations

- **Enhanced Debug Logging System**: Comprehensive phase tracking and error diagnosis
  - Updated `stem/debug_logger.py` with Quality Gate logging support (`log_quality_gate_result()`)
  - Session-based log file generation with conversation ID tracking
  - Phase-specific timing and error logging for performance analysis
  - Structured logging for Multi-phase architecture debugging and monitoring

- **Logging Cleanup**: Removed decorative emoji characters from server logging output
  - Removed rockets (🚀), sparkles (✨), locks (🔒), and document (📝) emojis from logging
  - Kept functional status emojis (✅⚠️❌) for request success/failure indication
  - Cleaner server terminal output while maintaining useful visual status indicators
  - Results exported as timestamped CSV files in tests directory for analysis

- **Apple Silicon M1 Optimization**: Enhanced hardware classification for better M1 performance
  - M1 processors specifically detected via `sysctl machdep.cpu.brand_string` and classified as low tier
  - Apple Silicon systems with ≤16GB RAM now use low tier (phi4-mini) instead of medium tier
  - M2/M3 systems with >16GB RAM continue to use medium tier (mistral:7b) for better performance
  - Updated installation script with M1-specific detection logic matching runtime classification
  - Updated documentation to reflect M1-specific low-tier classification for optimal performance

- **Dynamic Tool Loading System**: Complete refactoring of tool architecture for modularity and performance
  - Replaced static tool imports with dynamic loading system in `stem/dynamic_tools.py`
  - Database-driven tool registration with module path and function name mapping
  - Plugin-style architecture supporting built-in tools, plugins, and external tool packages
  - Lazy-loaded tool dictionary (`LazyToolDict`) for backward compatibility with existing code
  - Tools now loaded on-demand rather than at startup, reducing memory footprint
  - Comprehensive test coverage for dynamic loading system with mock compatibility

- **Debug Logging Infrastructure**: Structured logging system for development and troubleshooting
  - New `stem/debug_logger.py` with session-based logging and phase tracking
  - JSON-structured debug output for machine-readable log analysis
  - Conversation session tracking with unique session IDs and timestamps
  - Phase-based logging for multi-step debugging workflows
  - Integration with existing logging infrastructure without breaking changes
  - Debug log files stored in `logs/conversations/` with session isolation

### Changed

- **Documentation Updates**: Updated tool development documentation for dynamic loading system
  - Updated `CLAUDE.md` tool development section to reflect dynamic loading approach
  - Updated `AGENTS.md` tool registration documentation with database-driven examples
  - Added benefits section highlighting performance and modularity advantages
  - Removed references to outdated static `AVAILABLE_TOOLS` dictionary pattern
  - All documentation now accurately reflects the new dynamic tool architecture

### Fixed

- **Test Compatibility**: Resolved all test failures after dynamic tool system implementation
  - Fixed `LazyToolDict` compatibility with `unittest.mock.patch.dict` by implementing required dict-like methods
  - Updated database tool registration with correct module paths (`cerebellum` → `cerebellum.weather_tool`, etc.)
  - Fixed legacy wrapper function signatures to accept positional arguments expected by existing tests
  - Corrected parameter name mapping (`topic` → `topic_name`) for conversation tools
  - Removed automatic username injection that conflicted with `current_user` global variable pattern
  - All 23 tool tests and 23 cortex agent tests now passing

### Performance

- **Response Time Improvements**:
  - Simple queries: 18.6 seconds (direct response, no Phase 2)
  - Tool-assisted queries: 19.1 seconds (Phase 1: 12.3s + Phase 2: 6.8s)
  - Overall improvement: 45% faster than original 35+ second responses
- **Tool Overhead Reduction**: From 17 tools to 3 core tools in Phase 1 prompts (78% reduction)

## [0.3.18] - 2025-07-08

### Changed

- **Development**: Updated `GEMINI.md` with a mandatory, detailed protocol for Git workflow and a safer, more reliable debugging process for web applications. This includes using a dedicated `ide_debugging` directory for all temporary files, which is now ignored by Git.

## [0.3.17] - 2025-07-08

### Added

- **Development**: Added a dedicated `ide_debugging` directory for temporary debugging files and added it to `.gitignore`.

### Changed

- **Development**: Updated the debugging protocol to use a dedicated log file and to place all temporary files in the `ide_debugging` directory.

## [0.3.16] - 2025-07-08

### Fixed

- **UI**: Corrected the CSS to properly center the login box on the login page.
- **UI**: Fixed an issue where the navigation indicator was not updating when switching sections in the user profile and admin pages.
- **Memory Management**: Fixed a bug where the topic and summary were not being displayed in the memory management section of the profile page.
- **Memory Management**: Fixed an error that occurred when viewing a conversation from the memory management section.

## [0.3.15] - 2025-07-08

### Fixed

- Corrected several failing tests in the test suite.
- Fixed logout functionality by changing the HTTP method from POST to GET.
- Updated the website tester configuration to include the debug console.
- Corrected the mocked process count in the hardware monitoring tests.

## [0.3.14] - 2025-07-08

### Changed

- **Memory Management**: Restyled the memory management section in the profile page to use a table for a cleaner and more organized layout.
- **Admin Dashboard**: Aligned the styling of the 'Edit' button in the User Management section with other action buttons for visual consistency.

### Fixed

- **CSS Spacing**: Corrected the spacing for the network card in the system info section.

## [0.3.13] - 2025-07-08

### Added

- **Screenshot Tool**: Improved the screenshot tool to take full-page, high-resolution screenshots and handle authenticated sessions.
- **Developer Workflow**: Updated `GEMINI.md` with instructions for a visual changes workflow, including taking before and after screenshots to verify UI changes.

### Fixed

- **CSS Cleanup**: Performed a major cleanup and restructuring of the main stylesheet (`style.css`) to improve organization, remove redundancy, and restore missing styles.

## [0.3.12] - 2025-07-08

### Fixed

- **CSS Cleanup**: Refactored and cleaned up the main stylesheet (`style.css`) for better organization and maintainability. Restored all missing styles for the benchmark section, admin dashboard, profile page, and action buttons.

### Added

- **Screenshot Tool**: Added a new tool to take screenshots of web pages, which can be used to visually verify UI changes.

## [0.3.11] - 2025-07-08

### Fixed

- **CSS Alignment**: Corrected the CSS for the main layout on the conversation page to properly align the left and right menu bars.

## [0.3.10] - 2024-06-27

### Changed

- **System Settings Simplification**: Removed complex Ollama model dropdown functionality from system settings page
  - Converted ollama_model setting to use standard text input like other settings
  - Removed model downloader, refresh function, and progress tracking from backend
  - Removed dropdown UI components, modal dialogs, and related JavaScript functions
  - Simplified setting management to use consistent edit/save pattern across all settings
  - Eliminated Ollama-specific API endpoints and backend methods
  - Users can now manually enter any Ollama model name as a simple text value
- **System Info Section UI/UX:**
  - Grouped the first four metric tiles (CPU, RAM, Disk, Uptime) on a single row and moved the Network tile to a new row for better visual grouping.
  - Fixed the system info graphs to display live CPU and RAM usage history (last 60s) with proper data buffering and Chart.js integration.
  - Improved the raw system data display: always shows pretty-printed JSON in a monospace block, with syntax highlighting if available.

### Fixed

- Removed hardcoded 'Rotterdam' reference in agent system message; now dynamically uses the user's actual location from their personal profile (falls back to 'unknown location' if not set)
- Various UI and data display improvements for the System Info section on the conversation page.
- Network card in System Info now stretches the entire row and displays sent/recv in one line with two centered columns for improved clarity and consistency.
- Fixed conversation page template to use consistent .content-area class instead of .main-content
- Removed obsolete API key and database configuration comments from install script
- Cleaned up template structure for better consistency with other pages

## [0.3.9] - 2024-06-27

### Changed

- **System Settings Simplification**: Removed complex Ollama model dropdown functionality from system settings page
  - Converted ollama_model setting to use standard text input like other settings
  - Removed model downloader, refresh function, and progress tracking from backend
  - Removed dropdown UI components, modal dialogs, and related JavaScript functions
  - Simplified setting management to use consistent edit/save pattern across all settings
  - Eliminated Ollama-specific API endpoints and backend methods
  - Users can now manually enter any Ollama model name as a simple text value
- **System Info Section UI/UX:**
  - Grouped the first four metric tiles (CPU, RAM, Disk, Uptime) on a single row and moved the Network tile to a new row for better visual grouping.
  - Fixed the system info graphs to display live CPU and RAM usage history (last 60s) with proper data buffering and Chart.js integration.
  - Improved the raw system data display: always shows pretty-printed JSON in a monospace block, with syntax highlighting if available.

### Fixed

- Removed hardcoded 'Rotterdam' reference in agent system message; now dynamically uses the user's actual location from their personal profile (falls back to 'unknown location' if not set)
- Various UI and data display improvements for the System Info section on the conversation page.
- Network card in System Info now stretches the entire row and displays sent/recv in one line with two centered columns for improved clarity and consistency.

## [0.3.8] - 2024-06-26

### Changed

- **System Info Section UI/UX:**
  - Grouped the first four metric tiles (CPU, RAM, Disk, Uptime) on a single row and moved the Network tile to a new row for better visual grouping.
  - Fixed the system info graphs to display live CPU and RAM usage history (last 60s) with proper data buffering and Chart.js integration.
  - Improved the raw system data display: always shows pretty-printed JSON in a monospace block, with syntax highlighting if available.

### Fixed

- Various UI and data display improvements for the System Info section on the conversation page.

## [0.3.7] - 2024-06-24

### Added

- **Admin Dashboard Ollama Model Selector**: Fixed issues with Ollama model selection in admin dashboard
  - Fixed backend `refresh_ollama_model_options()` to return all available Ollama models instead of filtering by tool keys
  - Fixed frontend current value detection to properly fetch setting value from API instead of DOM text
  - Added proper error handling for model refresh operations
  - Added fallback to default model when no models are available or refresh fails
  - Improved model display with size information and better formatting
  - Added current value display in the settings table for better visibility
  - Ensures Ollama model selector works correctly and shows all available models
- Fixed 500 Internal Server Error when updating Ollama model settings in admin dashboard
  - Moved ollama import to module level to prevent import issues
  - Added proper error handling for Ollama operations in set_setting method
  - Settings are now saved to database even if Ollama model management fails
  - Added graceful fallback when Ollama library is not available
  - Improved API response handling with safer data access and validation
  - Added better logging for debugging Ollama model management issues
  - Fixed handling of Ollama Model objects (using 'model' attribute instead of 'name' key)
  - Added support for multiple API response formats (Model objects and dictionaries)
- Fixed Ollama model availability and tool support issues
  - Removed non-existent models (e.g., gemma2:7b) from curated list
  - Added tool support testing to filter models that don't support function calling
  - Only include models that actually exist and support tools in the dropdown
  - Added fallback to default model if no tool-supporting models are found
  - Improved model validation to prevent download errors
- Optimized model list for better performance
  - Removed all models larger than gemma3-cortex (8.1 GB) from curated list
  - Kept only smaller and similarly sized models for faster downloads
  - Reduced storage requirements and download times
- Real-time progress indicator for Ollama model downloads with streaming updates and frontend polling
- Curated list of major Ollama-compatible models, excluding overwhelming variants
- Refresh button to update available models list
- Model validation system to automatically detect and switch to tool-supporting models
- Automatic fallback to gemma3-cortex:latest when current model doesn't support tools
- Startup model validation to ensure system uses a working model

### Improved

- **Ollama Model Refresh**: Enhanced model refresh to show major models from Ollama library
  - Added curated list of major models (Gemma2, Llama3.2, Mistral, Code Llama, Phi-3, Qwen2.5, etc.)
  - Focuses on well-known models that support function calling/tools
  - Shows model sizes and clear display names for better user experience
  - Includes locally installed models that aren't in the major models list
  - Sorts major models first, then local models for better organization
  - Avoids overwhelming users with hundreds of language-specific variants

### Changed

- **HTML Template Naming Convention**: Renamed main page templates to follow consistent `page.` prefix pattern
  - `admin.html` → `page.admin.html`
  - `conversation.html` → `page.conversation.html` (already renamed from chat.html)
  - `login.html` → `page.login.html`
  - `profile.html` → `page.profile.html`
  - Updated all Python code references in static.py to use new template names
  - Updated all documentation references in AGENTS.md, templates/README.md, and stem/readme.md
  - Maintains consistency with JavaScript file naming patterns (page.*.js)
  - Improves code organization and makes page templates easily identifiable
- **JavaScript File Organization**: Merged debug.js functionality into page.conversation.js for unified conversation page management
  - Moved all benchmark functionality (runBenchmark, displayBenchmarkResults, renderComprehensiveBenchmark, renderLLMBenchmark, renderToolsBenchmark) from debug.js to page.conversation.js
  - Consolidated event listeners for debug controls and benchmark buttons into single setupDebugEventListeners function
  - Removed duplicate log and system info functions that were already present in page.conversation.js
  - Eliminated debug.js file to reduce code fragmentation and improve maintainability
  - All conversation page functionality now centralized in page.conversation.js
  - Maintained all existing functionality while improving code organization
- **Route Refactoring**: Refactored `/chat` route to `/conversation` to prevent confusion with chat sidebar
  - Renamed route from `/chat` to `/conversation` for main conversation interface
  - Updated all related function names from `chat_page` to `conversation_page`
  - Updated template files from `chat.html` to `conversation.html`
  - Updated navigation link from "Debug" to "Conversation"
  - Updated default login redirect from `/chat` to `/conversation`
  - Updated all test files to reflect new route and function names
  - Updated documentation to reflect new route structure
  - Preserved chat sidebar functionality for right-side panel
  - Improved clarity by reserving "chat" terminology for sidebar functionality
- Refactored configuration loading to use database-backed settings with fallback to environment variables.
- Improved error handling and logging for system settings operations.
- Updated admin dashboard navigation to include System Settings.
- Enhanced style and layout for settings tables and modals.
- **Install Script Enhancement**: Updated install script to use new system settings pattern
  - New installations now populate both .env file and system settings database
  - Configuration values are stored in database-backed settings from the start
  - Ensures consistency between .env file and system settings database
  - Provides seamless transition to new settings management system
- Enhanced memory system with advanced analytics and maintenance capabilities
- Improved tool registry with new memory management tools
- Updated system prompts to include new memory tools
- **JavaScript File Organization**: Separated sidebar chat functionality into dedicated files
  - Created `sidebar_chat.js` containing TatlockChat class and sidebar chat functionality
  - Renamed `chat.js` to `page.conversation.js` with conversation page-specific features
  - Updated all templates to use `sidebar_chat.js` for chat sidebar functionality
  - Maintains proper separation of concerns: sidebar chat vs conversation page features
  - Follows established pattern of shared functionality in dedicated files
- Updated frontend JS (`page.admin.js`) and CSS (`style.css`) for settings UI and modal dialogs.
- **JavaScript File Organization**: Renamed `login.js` to `page.login.js` for consistency with other page-specific scripts
  - Updated all template references to use `page.login.js`
- Renamed JavaScript plugin files with `plugin.` prefix for better organization:
  - `chart.min.js` → `plugin.chart.min.js`
  - `chart.umd.min.js.map` → `plugin.chart.umd.min.js.map`
  - `json-highlight.js` → `plugin.json-highlight.js`
  - `marked.min.js` → `plugin.marked.min.js`
- Updated all references to renamed plugin files in templates and static files
- Updated sourceMappingURL in renamed chart map file to maintain proper source mapping
- Isolated login page from common.js dependency by duplicating togglePassword function to page.login.js
- Removed common.js script loading from login template for complete page isolation
- Merged auth.js functionality into common.js for unified shared JavaScript management:
  - Comprehensive SnackbarManager class with confirm dialogs
  - User dropdown and theme toggle functionality
  - User info loading and authentication handling
  - Anchor link handling and scroll management
  - Removed auth.js script loading from all templates
  - Deleted auth.js file after successful merge
- Renamed `sidebar_chat.js` to `component.chatbar.js` for consistent component naming convention
- Updated all template references to use new component.chatbar.js filename
- Updated template documentation to include component script naming patterns
- Comprehensive documentation of JavaScript file naming patterns in AGENTS.md:
  - Page-specific scripts: `page.{pagename}.js`
  - Component scripts: `component.{componentname}.js`
  - Shared scripts: `{functionality}.js`
  - Plugin scripts: `plugin.{library}.js`
  - Script loading order guidelines
  - Naming guidelines and best practices
  - Migration and exception handling procedures
- Renamed `marked.min.js` to `plugin.marked.min.js` to complete plugin naming standardization
- Updated all template references, documentation, and test assertions to use new plugin.marked.min.js filename
- Corrected script loading for admin and profile pages to include component.chatbar.js since they use the chat sidebar
- **Documentation and Template Cleanup**: Cleaned up and updated all main HTML templates and stem module documentation
  - Removed obsolete and out-of-date comments and documentation entries
  - Added and clarified documentation for new features, standards, and UI/UX patterns (system settings, tools management, right-aligned add buttons, section header standards, chat sidebar separation, memory management, modal structure, etc.)
  - Updated naming conventions and removed references to deleted or merged files

### Fixed

- **Profile Page JavaScript Error Fix**: Removed incomplete settings section registration that was causing `loadProfileSettings is not defined` error
  - Removed `registerSectionLoader('settings-section', loadProfileSettings)` registration from page.profile.js
  - Removed `'settings-section'` from valid sections array in navigation handler
  - Fixed JavaScript error that occurred when profile page tried to load non-existent settings section
  - Profile page now only registers sections that actually exist: activity-section and info-section
  - Maintains clean separation between profile functionality and system settings (which belong in admin page)
- **JavaScript Error Fix**: Fixed `initializeHashNavigation is not defined` error in conversation page
  - Added common.js script inclusion to conversation template to ensure required functions are available
  - Made initializeHashNavigation, showSection, and showSnackbar functions globally available in common.js
  - Fixed ReferenceError that was occurring when debug.js tried to call initializeHashNavigation
  - Ensures proper script loading order and function availability across all pages
- **ES6 Export Syntax Fix**: Fixed 'Unexpected token export' error in common.js
  - Removed export statements from common.js since it's loaded as a regular script
  - Made all functions (registerSectionLoader, showSection, initializeHashNavigation, showSnackbar) globally available via window object
  - Fixed syntax error that was occurring when common.js was loaded in non-module context
  - Ensures compatibility with regular script loading across all pages
- **ES6 Import Errors Fix**: Fixed 'does not provide an export named' errors in JavaScript files
  - Removed import statements from chat.js, page.profile.js, and page.admin.js that were trying to import from common.js
  - Updated all files to use globally available functions from window object instead of ES6 imports
  - Fixed module import errors that were occurring when files tried to import from non-module common.js
  - Ensures all JavaScript files work correctly with the non-module common.js approach
- **Script Loading Order Fix**: Fixed 'registerSectionLoader is not defined' error in admin and profile pages
  - Added common.js script inclusion to admin.html and profile.html templates
  - Ensures registerSectionLoader and other functions are available before page.admin.js and page.profile.js load
  - Fixed dependency loading order that was causing functions to be undefined
  - Maintains proper script loading order across all templates
- **Script Loading Order Standardization**: Standardized script inclusion pattern across all templates
  - Reordered scripts in conversation.html to follow consistent pattern: common.js → auth.js → page-specific scripts → utilities
  - Ensures all templates follow the same dependency loading pattern
  - Maintains proper script loading order for function availability across all pages
- Fixed issue where settings dropdown would not load due to missing `settings_options` table.
- Fixed repeated errors in logs by ensuring database schema is created and migrations are applied.
- Fixed UI bugs related to model selection and modal dialog state.
- **Installer Fix**: Removed problematic `python3.10-apt` package dependency
  - Package was causing installation failures on some systems
  - Fallback to source compilation now works reliably
  - Improved compatibility across different Ubuntu versions
- **Installer Safety**: Added safeguard to prevent system Python link modification
  - Confirmed installer never changes system Python symlinks
  - Added explicit comment to prevent future changes
  - Maintains system stability during installation
- **Installer Robustness**: Improved apt hook handling during installation
  - Temporarily disables `command-not-found` apt hook to prevent deadlocks
  - Ensures smooth installation process even with system package conflicts
  - Better error handling for Python package installation
- **Service Management**: Fixed bugs in manage-service.sh script
  - Corrected service status checking logic
  - Fixed process detection and management
  - Improved error handling and user feedback
- **Installer Hardening**: Enhanced installation script reliability
  - Better error handling for Python installation
  - Improved dependency management
  - More robust system compatibility checks
- **Unified Service Management**: New `manage-service.sh` script
  - Replaces separate start.sh and stop.sh scripts
  - Provides start, stop, restart, and status commands
  - Better process management and error handling
  - Improved user experience for service control
- **Legacy Scripts**: Removed old start.sh and stop.sh files
  - Replaced by unified manage-service.sh script
  - Cleaner project structure
- **Documentation**: Updated README.md to remove redundant instructions
  - Removed duplicate installation steps
  - Streamlined getting started guide
  - Better organization of information
- **Admin Dashboard User Edit Button Fix**: Fixed ReferenceError for Edit button in user table
  - Updated the Edit button in the user table to call `showUserModal(username)` instead of the undefined `editUser(username)`
  - Resolves `Uncaught ReferenceError: editUser is not defined` in the admin dashboard
  - Edit button now correctly opens the user editing modal
- Backend filtering to return all available Ollama models instead of just local ones
- Frontend model detection to properly handle Ollama API response structure
- Model handling to support Ollama API's actual response structure (Model objects with 'model' attribute)
- Curated model list optimization by removing models larger than gemma3-cortex (8.1 GB)
- Ongoing issues with non-tool-supporting models like gemma2:9b being selected
- Model validation and automatic switching to supported models when tool calls fail
- Removed non-tool-supporting models from curated list and local installation
  - Removed gemma2:2b, gemma:latest, gemma3:12b, gemma3:latest from local Ollama installation
  - Updated curated model list to exclude Gemma2 models that don't support function calling
  - Ensures dropdown only shows models verified to support tools

### Technical

- Added new tables: `system_settings`, `system_setting_categories`, `system_setting_categories_map`, and `settings_options` to `system.db`.
- Updated `stem/installation/database_setup.py` to create and populate default settings and categories.
- Added new Pydantic models for system settings and categories in `stem/models.py`.
- Refactored backend logic in `stem/admin.py` to support full CRUD for settings and categories.
- Updated frontend JS (`page.admin.js`) and CSS (`style.css`) for settings UI and modal dialogs.
