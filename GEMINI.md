# Gemini AI Assistant Guide for Tatlock

This guide provides instructions for AI assistants to contribute to the Tatlock project, ensuring adherence to its coding standards, patterns, and development practices.

**IMPORTANT**: The `developer.md` file contains the authoritative instruction set for all developers and LLMs working on this project. Any conflicting guidance between this file and `developer.md` should defer to `developer.md`, which supersedes all other instruction files including this one.

### Core Workflows

- **Versioning**: When asked to update the application version, you must follow the full "Versioning and Releases" workflow. This includes updating `changelog.md` with all changes since the last version, committing it with the `pyproject.toml` update, and creating a Git tag.
- **Troubleshooting**: When a fix resolves a common installation or runtime issue, suggest an addition to `troubleshooting.md` to help future users.
- **Testing**: All new code, whether adding features or fixing bugs, must be accompanied by corresponding tests to ensure correctness and prevent regressions.
- **Code Organization**: Keep the codebase clean and maintainable. If code is used in multiple places, refactor it into a new shared file, following the Don't Repeat Yourself (DRY) principle. When creating new files, place them in the appropriate module directory, adhering to the existing filesystem structure patterns.

### General Guidance

1. **Always Include Standards**: When using coding AI assistants, always include the Tatlock coding standards from this file as part of your prompt.
2. **Reference Specific Sections**: Reference relevant sections like "Python Coding Standards", "JavaScript Coding Standards", or "Security Standards" based on the task.
3. **Validate Generated Code**: Review AI-generated code to ensure it follows our established patterns and conventions.
4. **Update Standards**: If AI suggests improvements to our coding standards, evaluate and update this document accordingly.

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

## Project Organization

### Brain-Inspired Architecture

- **Module Naming**: Modules are named after brain regions (cortex, hippocampus, stem, parietal, etc.).
- **Clear Separation**: Core logic, authentication, memory, and utilities are in separate modules.
- **Consistent Structure**: Each module has `__init__.py`, `readme.md`, and relevant functionality.
- **Test Organization**: Comprehensive test suite in the `tests/` directory.
- **User Isolation**: Each user has their own separate database for long-term memory, located at `hippocampus/longterm/{username}.db`. This is a critical security and privacy feature.
- **System Database**: Global data, including user authentication, tools, and system prompts, is stored in `system.db`.

### File Naming Conventions

- **HTML Page Templates**: `page.{pagename}.html` (e.g., `page.login.html`) in `stem/templates/`.
- **HTML Component Templates**: `{componentname}.html` (e.g., `chat_sidebar.html`) in `stem/templates/components/`.
- **JavaScript Page-Specific Scripts**: `page.{pagename}.js` (e.g., `page.login.js`).
- **JavaScript Component Scripts**: `component.{componentname}.js` (e.g., `component.chatbar.js`).
- **JavaScript Shared Scripts**: `common.js` for shared utilities.
- **JavaScript Plugin Scripts**: `plugin.{library}.js` for third-party libraries.
- **Python Test Files**: `test_{module_name}.py` (e.g., `test_cortex_agent.py`) in `tests/`.

## Coding Standards

### Python

- **Python 3.10+**: Use modern type hints (`list[dict]`, `str | None`).
- **Type Hints**: All functions must have parameter and return type annotations.
- **Docstrings**: Include comprehensive docstrings for all functions and modules.
- **Logging**: Use `logging.getLogger(__name__)` for structured logging.
- **Error Handling**: Use `try...except` blocks with specific exception types and log errors.
- **Database**: Use parameterized queries to prevent SQL injection. User-specific data is stored in a separate database per user.
- **Pydantic**: Use Pydantic models for API request/response validation.
- **User Context**: Access the current user via `from stem.current_user_context import get_current_user_ctx`. Do not pass user objects as parameters.

### JavaScript

- **ES6+ Syntax**: Use modern JavaScript features like `async/await`, arrow functions, and classes.
- **File Organization**: Keep JavaScript in separate files following the naming conventions. Use shared libraries to avoid code duplication.
- **Jinja2 Integration**:
  - Keep all HTML structure in Jinja2 templates.
  - Use JavaScript to populate dynamic content into existing DOM elements, not to build HTML strings.
  - Control visibility with CSS `display` properties, not by adding/removing elements from the DOM.
- **Error Handling**: Use `try...catch` blocks for `async` operations and provide user-friendly feedback.

### CSS

- **CSS Variables**: Use CSS variables for theming and consistency.
- **Responsive Design**: Employ a mobile-first approach with `flexbox` or `grid`.
- **Component Styling**: Style components in a modular and reusable way.

### Security

- **Input Validation**: Validate all inputs using Pydantic models.
- **SQL Injection**: Use parameterized queries exclusively.
- **User Isolation**: Ensure tools and database queries respect user boundaries. Each user has their own database.
- **Authentication**: Use `Depends(get_current_user)` for endpoint protection.

## Development Practices

### Versioning and Releases

**Do not initiate the release process unless explicitly instructed by the user.**

1. **Update `changelog.md`**: Create a new release section and move changes from `[Unreleased]`.
2. **Update `pyproject.toml`**: Increment the `version` number.
3. **Commit**: Commit `changelog.md` and `pyproject.toml` together with the message `Bump version to X.Y.Z`.
4. **Tag**: Create a git tag `vX.Y.Z`.
5. **Push to Remote**: Push the `main` branch and all tags to the remote repository using `git push origin main --tags`.

### Development Protocols

#### Mandatory Git Workflow Protocol

For any task that involves modifying code or documentation, you MUST follow this protocol without deviation.

**1. Branch Verification & Creation:**

- **Action:** Immediately upon receiving the task, run `git branch`.
- **Condition:** If the current branch is `main`, you MUST create a new branch before proceeding.
- **Branch Naming:** The new branch name MUST follow the pattern `fix/<short-description>` for bug fixes or `feature/<short-description>` for new features.
- **Confirmation:** Announce the branch you are working on.

**2. Implementation:**

- Perform all necessary code modifications, file creations, or other requested actions within the designated branch.

**3. Pre-Commit Verification:**

- **Action:** Before committing, you MUST run `git status` to review all changes.
- **Staging:** Use `git add <file>` to stage only the files directly related to the completed task. Avoid using `git add .`.
- **Review:** After staging, you MUST run `git diff --staged` to review the exact changes that will be committed.

**4. Merging Protocol (Upon User Request):**

- **Action:** When the user approves the changes and requests a merge, you MUST follow these steps in order:
    1. `git checkout main`
    2. `git merge <your-branch-name>`
    3. `git push origin main` (Only if explicitly asked to push)

**5. Cleanup:**

- **Action:** After a successful merge into `main`, you MUST delete the feature/fix branch and any temporary files created during the task.
- **Branch Deletion:** `git branch -d <your-branch-name>`
- **Screenshot Cleanup:** If you created any screenshots, you MUST delete them from the `ide_screenshots/` directory. Use `rm ide_screenshots/<screenshot-file-name>.png`.

#### Revised Debugging Protocol for Web Applications

To ensure I can correctly diagnose issues with web applications, I will now follow this strict protocol:

1. **Setup:** Create the `ide_debugging` directory if it doesn't exist.
2. **Scripts:** Place all temporary verification scripts inside `ide_debugging`.
3. **Server Logging:** Start the server in the background, redirecting its output to `ide_debugging/server.log`.
    - **Command:** `python main.py > ide_debugging/server.log 2>&1 &`
4. **Verification:** Run the verification script from the root directory.
5. **Analysis:** Analyze the script output and the contents of `ide_debugging/server.log`.
6. **Stop the Server:** After verification, I will stop the background server process using its PID.
7. **Cleanup:** I will remove the entire `ide_debugging` directory and all its contents.

### Visual Changes Workflow

- **Always take screenshots**: When making changes to CSS, JavaScript, or HTML, you must always take "before" and "after" screenshots to verify the changes.
- **Follow Debugging Protocol**: Adhere to the "Revised Debugging Protocol for Web Applications" for starting the server and managing temporary scripts.
- **Screenshot Directory**: Place all screenshots in the `ide_screenshots/` directory as specified in the Git workflow. Do not use the `ide_debugging` directory for images.
- **Authentication**: The first time you need to take a screenshot in a session, ask the user for their username and password. Store these credentials in your own session memory to avoid asking again.
- **Use `ide_login.py`**: For logging in to the application to take screenshots, use the `get_session_cookie` function from the `ide_login.py` script. This provides a standard way to get the necessary authentication cookie.
- **Use the `sync_take_screenshot` tool**: This is the standard for capturing the UI.
- **Default Behavior**: The tool waits 5 seconds, sets a 2000px viewport width, and captures the full page.
- **Analyze the screenshots**: After capturing, use the `analyze_screenshot_file` tool or visual inspection to compare the "before" and "after" images.
- **Cleanup**: Remember to remove the screenshots from `ide_screenshots/` and the temporary scripts from `ide_debugging/` upon task completion, as per the respective protocols.

### Adding New Tools

1. **Create Tool Function**: Add the `execute_my_new_tool` function in the appropriate module (e.g., `cerebellum/my_new_tool.py`).
2. **Update Database Schema**: In `stem/installation/database_setup.py`, add the tool and its parameters to `tools_to_insert` and `params_to_insert`.
3. **Register Tool Function**: In `stem/tools.py`, import the function and add it to the `ALL_TOOL_FUNCTIONS` dictionary.
4. **Enable Tool**: In `system.db`, set `enabled = 1` for the new tool in the `tools` table.

## Testing

- **Run all tests**: `python -m pytest tests/`
- **Run specific test file**: `python -m pytest tests/test_cortex_agent.py`
- **Test Cleanup**: The test suite automatically cleans up test users and their data. Use fixtures like `cleanup_test_users` and `cleanup_after_test`.
- **Test Harness**: A `TestAPIHarness` class in `tests/api_harness.py` should be used for API tests to manage user creation and authentication.

## Documentation

- **`README.md`**: Project overview and installation.
- **`developer.md`**: The source of truth for all development standards. Do not alter coding standards or AI instructions without permission.
- **`GEMINI.md`**: This file. Your guide for contributing to the project.
- **`moreinfo.md`**: In-depth technical project description.
- **`troubleshooting.md`**: Common installation and runtime issues. Suggest updates when applicable.
- **Module `readme.md`**: Each module has its own `readme.md` describing its purpose, features, and file system.
