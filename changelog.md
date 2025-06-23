# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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

### Changed
- Enhanced memory system with advanced analytics and maintenance capabilities
- Improved tool registry with new memory management tools
- Updated system prompts to include new memory tools

### Technical
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