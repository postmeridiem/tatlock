# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Created `manage-service.sh`, a unified, interactive script for starting, stopping, restarting, and viewing logs for the Tatlock service on Linux and macOS.

### Changed
- The `install_tatlock.sh` script now makes `manage-service.sh` executable and informs the user about it.

### Deprecated
-

### Removed
- Deleted `start.sh` and `stop.sh` in favor of the more comprehensive `manage-service.sh`.

### Fixed
-

### Security
-

## [0.2.1] - 2024-08-01

### Changed
- Improved formatting of service management commands in `README.md` for easier copy-pasting.

## [0.2.0] - 2024-08-01

### Added
- Centralized application versioning using `pyproject.toml`.
- Version number is now dynamically loaded into the FastAPI application and HTML templates.
- Added application version to the `<head>` of all HTML pages.
- Created `changelog.md` to track project changes.
- Created a dedicated "AI Instructions" section in `developer.md`.

### Changed
- Refactored versioning to remove hardcoded versions in `main.py` and `stem/htmlcontroller.py`.
- Consolidated all AI-related development guidelines into a single section in `developer.md`.
- Refactored version-reading logic from a standalone file into `config.py`.

### Fixed
- Resolved version inconsistency between the backend API (`0.1.0`) and a hardcoded frontend variable (`3.0.0`).

## [0.1.0] - 2024-07-31

### Added
- Initial setup of the Tatlock application. 