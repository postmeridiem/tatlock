# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **System Settings Management**: Admin dashboard now includes a "System Settings" section for managing global configuration.
  - All system settings (Ollama model, version, API keys, server config, security, etc.) are now stored in new tables in `hippocampus/system.db`.
  - Settings are organized by category and can be edited from the UI.
  - Added backend endpoints for listing, updating, and categorizing system settings.
  - Added support for allowed options (e.g., model selection) via a `settings_options` table.
  - Ollama model selector only shows tool-enabled models.
  - Added a "Refresh" button to update the model list from the Ollama API.
  - Modal dialog prompts to remove the previous model from disk when changing models (except the initial model).
  - Backend downloads new model on save and can remove the previous model if requested.
  - All settings changes are reflected live in the application configuration.
- **API Key Dependency System**: Tools requiring API keys are now automatically managed
  - Tools requiring API keys are disabled by default during installation
  - Weather tool (`get_weather_forecast`) requires `openweather_api_key`
  - Web search tool (`web_search`) requires both `google_api_key` and `google_cse_id`
  - Tools are automatically enabled when API keys are configured through admin interface
  - Tools are automatically disabled when API keys are removed or invalidated
  - No manual intervention required - system automatically manages tool availability
- **Dynamic System Prompts Architecture**: System prompts now dynamically include tool-specific instructions
  - Added `prompts` column to tools table for tool-specific instructions
  - Moved tool-specific prompts from `rise_and_shine` table to individual tool records
  - System prompts now combine base instructions with enabled tool prompts
  - Disabled tools automatically exclude their prompts from system instructions
  - Ensures LLM only receives instructions for available tools
  - Maintains clean separation between base system behavior and tool-specific guidance
- **Tools Management Interface**: Admin dashboard now includes comprehensive tools management
  - New "Tools" section in admin navigation for managing all system tools
  - Tools table displays tool key, description, module, and current status
  - Enable/disable toggles for each tool with visual status indicators
  - Tool details modal shows comprehensive information including:
    - Tool metadata (key, description, module, function name)
    - Current status (enabled/disabled)
    - System prompts associated with the tool
    - Tool parameters with types, descriptions, and required flags
  - Real-time status updates with success/error feedback
  - Responsive design that works on mobile and desktop
- **Jinja2 Template Refactoring**: Improved template architecture and patterns
  - Refactored admin dashboard to follow proper Jinja2 templating patterns
  - HTML structure now defined in templates, JavaScript only handles dynamic content
  - Eliminated HTML string building in JavaScript for better maintainability
  - Added comprehensive documentation for Jinja2 template integration patterns
  - Improved separation of concerns between templates and JavaScript
  - Better error handling and loading states for dynamic content
  - Consistent DOM manipulation patterns across all admin sections
- **Frontend Enhancements**:
  - System settings are displayed in a categorized table with edit actions.
  - Ollama model is rendered as a dropdown with refresh and save actions.
  - Modal dialog for model removal confirmation.
  - Responsive and accessible UI for settings management.
- **Memory Insights Tool**: Advanced analytics for conversation patterns, topic analysis, and usage statistics
  - Overview analysis with conversation counts, memory totals, and averages
  - Pattern analysis showing most active days, hours, and conversation length statistics
  - Topic analysis with trending topics and engagement metrics
  - Temporal analysis for usage patterns over time
- **Memory Cleanup Tool**: Database health and maintenance utilities
  - Duplicate detection with configurable similarity thresholds
  - Orphaned record detection and cleanup recommendations
  - Data quality analysis with health scores and issue identification
  - Comprehensive database health assessment
- **Memory Export Tool**: Data export capabilities in multiple formats
  - JSON export with full conversation and memory data
  - CSV export for spreadsheet analysis
  - Summary export with key statistics and insights
  - Configurable date ranges and topic inclusion options
- **Comprehensive Test Coverage**: Full test suite for all new memory tools
  - 16 test cases covering all tool functionality
  - Unit tests for individual tool features
  - Integration tests for helper functions
  - Error handling and edge case testing
  - Mock database and file operations for reliable testing
- **Database Architecture**: Moved rise_and_shine table from user databases to system database
  - System prompts now stored centrally in hippocampus/system.db
  - All users share the same base instructions
  - Simplified database schema for user databases
  - Improved consistency across user sessions
- **Comprehensive Documentation Cleanup**: Standardized and condensed all module documentation
  - Updated all module README files to reference developer.md as single source of truth
  - Removed verbose examples and duplicated content across documentation
  - Condensed module descriptions to focus on purpose, features, and integration
  - Standardized documentation structure and reduced maintenance overhead
  - Improved navigation with consistent references to developer.md for standards
  - Cleaned up root README.md to focus on high-level overview and installation

### Changed
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

### Fixed
- **JavaScript Error Fix**: Fixed `initializeHashNavigation is not defined` error in conversation page
  - Added common.js script inclusion to conversation template to ensure required functions are available
  - Made initializeHashNavigation, showSection, and showSnackbar functions globally available in common.js
  - Fixed ReferenceError that was occurring when debug.js tried to call initializeHashNavigation
  - Ensures proper script loading order and function availability across all pages
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

### Technical
- Added new tables: `system_settings`, `system_setting_categories`, `system_setting_categories_map`, and `settings_options` to `system.db`.
- Updated `stem/installation/database_setup.py` to create and populate default settings and categories.
- Added new Pydantic models for system settings and categories in `stem/models.py`.
- Refactored backend logic in `stem/admin.py` to support full CRUD for settings and categories.
- Updated frontend JS (`admin.js`) and CSS (`style.css`) for settings UI and modal dialogs.
- Updated `config.py` to load all configuration from the database if available.
- Added type annotations for better code maintainability
- Implemented robust error handling and logging
- Created modular design for easy extension and maintenance
- **Database Migration**: Automated migration of existing user data
  - Preserved all existing prompts during migration
  - Cleaned up user databases by removing redundant tables
  - Updated get_base_instructions() to read from system database

## [0.2.7] - 2025-06-23

### Changed
- **Installer Enhancement**: Only show default password warning when default password is actually used
  - Tracks whether user changed from default password during installation
  - Shows confirmation message instead of warning when password was changed
  - Improves user experience by reducing unnecessary warnings

## [0.2.6] - 2025-06-23

### Fixed
- **Installer Fix**: Removed problematic `python3.10-apt` package dependency
  - Package was causing installation failures on some systems
  - Fallback to source compilation now works reliably
  - Improved compatibility across different Ubuntu versions

## [0.2.5] - 2025-06-23

### Fixed
- **Installer Safety**: Added safeguard to prevent system Python link modification
  - Confirmed installer never changes system Python symlinks
  - Added explicit comment to prevent future changes
  - Maintains system stability during installation

## [0.2.4] - 2025-06-23

### Fixed
- **Installer Robustness**: Improved apt hook handling during installation
  - Temporarily disables `command-not-found` apt hook to prevent deadlocks
  - Ensures smooth installation process even with system package conflicts
  - Better error handling for Python package installation

## [0.2.3] - 2025-06-23

### Fixed
- **Service Management**: Fixed bugs in manage-service.sh script
  - Corrected service status checking logic
  - Fixed process detection and management
  - Improved error handling and user feedback
- **Installer Hardening**: Enhanced installation script reliability
  - Better error handling for Python installation
  - Improved dependency management
  - More robust system compatibility checks

## [0.2.2] - 2025-06-23

### Added
- **Unified Service Management**: New `manage-service.sh` script
  - Replaces separate start.sh and stop.sh scripts
  - Provides start, stop, restart, and status commands
  - Better process management and error handling
  - Improved user experience for service control

### Removed
- **Legacy Scripts**: Removed old start.sh and stop.sh files
  - Replaced by unified manage-service.sh script
  - Cleaner project structure

## [0.2.1] - 2025-06-23

### Fixed
- **Documentation**: Updated README.md to remove redundant instructions
  - Removed duplicate installation steps
  - Streamlined getting started guide
  - Better organization of information

## [0.2.0] - 2025-06-23

### Added
- **Centralized Versioning**: Single source of truth for version information
  - Version now managed in `pyproject.toml`
  - Dynamic version loading in `main.py` and `stem/htmlcontroller.py`
  - Consistent version display across the application
- **Changelog**: Added comprehensive changelog tracking
  - Documents all version changes and features
  - Follows Keep a Changelog format
  - Helps with release management
- **Developer Guidelines**: Added `developer.md` with coding standards
  - Defines project architecture and patterns
  - Documents development workflows
  - Establishes coding standards and best practices

### Changed
- **Version Management**: Refactored version handling
  - Removed hardcoded versions from multiple files
  - Centralized version in pyproject.toml
  - Dynamic version loading throughout application
- **Documentation**: Improved project documentation
  - Added comprehensive changelog
  - Created developer guidelines
  - Updated README with better structure

### Technical
- **Code Organization**: Better separation of concerns
  - Version logic centralized in pyproject.toml
  - Dynamic imports for version information
  - Cleaner code structure

## [0.1.0] - 2025-06-23

### Added
- Initial release of Tatlock
- Core chat functionality with memory system
- User authentication and management
- Admin interface and user management
- Memory tools for conversation management
- Hardware monitoring and system information
- Voice processing capabilities
- Web interface with modern UI
- Comprehensive testing framework 