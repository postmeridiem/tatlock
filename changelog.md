# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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