# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
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

### Improved
- **Ollama Model Refresh**: Enhanced model refresh to show major models from Ollama library
  - Added curated list of major models (Gemma2, Llama3.2, Mistral, Code Llama, Phi-3, Qwen2.5, etc.)
  - Focuses on well-known models that support function calling/tools
  - Shows model sizes and clear display names for better user experience
  - Includes locally installed models that aren't in the major models list
  - Sorts major models first, then local models for better organization
  - Avoids overwhelming users with hundreds of language-specific variants

## [0.3.6] - 2024-06-25
### Fixed
- **Admin Dashboard Ollama Model Selector**: Fixed issues with Ollama model selection in admin dashboard
  - Fixed backend `refresh_ollama_model_options()` to return all available Ollama models instead of filtering by tool keys
  - Fixed frontend current value detection to properly fetch setting value from API instead of DOM text
  - Added proper error handling for model refresh operations
  - Added fallback to default model when no models are available or refresh fails
  - Improved model display with size information and better formatting
  - Added current value display in the settings table for better visibility
  - Ensures Ollama model selector works correctly and shows all available models

## [0.3.5] - 2024-06-25
### Fixed
- **Benchmark Element ID Error**: Fixed null reference error in benchmark functionality
  - Fixed element ID mismatch between `benchmark-content` and `benchmark-results`
  - Added null checks to prevent "Cannot set properties of null" errors
  - Updated `runBenchmark()` and `displayBenchmarkResults()` to use correct element ID
  - Added error logging for debugging when benchmark container is not found
  - Ensures benchmark buttons work correctly without JavaScript errors

## [0.3.4] - 2024-06-25
### Fixed
- **Conversation Page Navigation**: Fixed hash-based navigation not working on conversation page
  - Added proper initialization of hash navigation with `initializeHashNavigation('conversation')`
  - Updated section loaders to match navigation item IDs (`conversation`, `system-info`, `benchmarks`)
  - Added hash change event listener for proper navigation handling
  - Fixed section loader registration to use correct section IDs
  - Added proper content loading for system-info and benchmarks sections
  - Ensures navigation links work correctly and sections display properly

## [0.3.3] - 2024-06-25
### Fixed
- **Install Script .env Creation**: Modified installer to automatically create .env file when none exists
  - Removed unnecessary prompt when no .env file is present
  - Script now automatically creates .env file with default values when none exists
  - Only prompts for overwrite confirmation when .env file already exists
  - Added HOSTNAME, PORT, and ALLOWED_ORIGINS to the generated .env file
  - Improves user experience by reducing unnecessary prompts during fresh installations

## [0.3.2] - 2024-06-25
### Fixed
- **Python Version Requirement**: Modified installer to require exactly Python 3.10 instead of 3.10+
  - Updated `check_python_version()` function to reject Python versions higher than 3.10
  - Modified installer instructions and error messages to specify exact Python 3.10 requirement
  - Added Python version constraint to `pyproject.toml` with `requires-python = "==3.10.*"`
  - Added warning comments to `requirements.txt` about Python 3.10 requirement
  - Prevents dependency conflicts (e.g., greenlet wheel building issues) that occur with Python 3.11+
  - Ensures optimal compatibility and prevents installation issues on systems with newer Python versions

## [0.3.1] - 2024-06-24
### Fixed
- Added support for Pop!_OS Linux in the installer. Pop!_OS is now detected and treated as a Debian-based system for package installation.

## [0.3.0] - 2024-06-24

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
- **HTML Template Naming Convention**: Renamed main page templates to follow consistent `page.` prefix pattern
  - `admin.html` → `page.admin.html`
  - `conversation.html` → `page.conversation.html` (already renamed from chat.html)
  - `login.html` → `page.login.html`
  - `profile.html` → `page.profile.html`
  - Updated all Python code references in static.py to use new template names
  - Updated all documentation references in developer.md, templates/README.md, and stem/readme.md
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
- Comprehensive documentation of JavaScript file naming patterns in developer.md:
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

### Technical
- Added new tables: `system_settings`, `system_setting_categories`, `system_setting_categories_map`, and `settings_options` to `system.db`.
- Updated `stem/installation/database_setup.py` to create and populate default settings and categories.
- Added new Pydantic models for system settings and categories in `stem/models.py`.
- Refactored backend logic in `stem/admin.py` to support full CRUD for settings and categories.
- Updated frontend JS (`page.admin.js`) and CSS (`style.css`) for settings UI and modal dialogs.