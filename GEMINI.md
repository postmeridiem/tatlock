# Gemini AI Assistant Guide for Tatlock

This guide provides instructions for AI assistants to contribute to the Tatlock project, ensuring adherence to its coding standards, patterns, and development practices.

## Primary Directive
Always adhere to the coding standards, patterns, and development practices described in this file. If a request conflicts with these standards, ask for clarification or permission before deviating.

### Core Workflows
- **Versioning**: When asked to update the application version, you must follow the full "Versioning and Releases" workflow. This includes updating `changelog.md` with all changes since the last version, committing it with the `pyproject.toml` update, and creating a Git tag.
- **Troubleshooting**: When a fix resolves a common installation or runtime issue, suggest an addition to `troubleshooting.md` to help future users.
- **Testing**: All new code, whether adding features or fixing bugs, must be accompanied by corresponding tests to ensure correctness and prevent regressions.
- **Code Organization**: Keep the codebase clean and maintainable. If code is used in multiple places, refactor it into a new shared file, following the Don't Repeat Yourself (DRY) principle. When creating new files, place them in the appropriate module directory, adhering to the existing filesystem structure patterns.

### General Guidance
1.  **Always Include Standards**: When using coding AI assistants, always include the Tatlock coding standards from this file as part of your prompt.
2.  **Reference Specific Sections**: Reference relevant sections like "Python Coding Standards", "JavaScript Coding Standards", or "Security Standards" based on the task.
3.  **Validate Generated Code**: Review AI-generated code to ensure it follows our established patterns and conventions.
4.  **Update Standards**: If AI suggests improvements to our coding standards, evaluate and update this document accordingly.

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
1.  **Update `changelog.md`**: Create a new release section and move changes from `[Unreleased]`.
2.  **Update `pyproject.toml`**: Increment the `version` number.
3.  **Commit**: Commit `changelog.md` and `pyproject.toml` together with the message `Bump version to X.Y.Z`.
4.  **Tag**: Create a git tag `vX.Y.Z`.
5.  **Push to Remote**: Push the `main` branch and all tags to the remote repository using `git push origin main --tags`.

### Git Workflow
- **Branching Strategy**: Before making any code changes, check the current Git branch.
- **Never commit to `main`**: You must never commit changes directly to the `main` branch. All work must be done in a feature or fix branch.
- **Create a new branch from `main`**: If you are on the `main` branch, you must create a new branch before making any changes. Use a descriptive name like `fix/bug-description` or `feature/new-feature-name`.
- **Stay in the current branch**: If you are already in a feature or fix branch, stay in that branch unless explicitly instructed to switch.
- **Do not merge branches**: Do not merge any branch into `main` unless explicitly instructed to do so by the user.

### Visual Changes Workflow
- **Always take screenshots**: When making changes to CSS, JavaScript, or HTML, you must always take "before" and "after" screenshots to verify the changes.
- **Authentication**: The first time you need to take a screenshot in a session, ask the user for their username and password. Store these credentials in your own session memory to avoid asking again.
- **Use the `sync_take_screenshot` tool**: This is the standard for capturing the UI.
- **Default Behavior**: The tool waits 5 seconds, sets a 2000px viewport width, and captures the full page.
- **Analyze the screenshots**: After capturing, use the `analyze_screenshot_file` tool or visual inspection to compare the "before" and "after" images.

### Adding New Tools
1.  **Create Tool Function**: Add the `execute_my_new_tool` function in the appropriate module (e.g., `cerebellum/my_new_tool.py`).
2.  **Update Database Schema**: In `stem/installation/database_setup.py`, add the tool and its parameters to `tools_to_insert` and `params_to_insert`.
3.  **Register Tool Function**: In `stem/tools.py`, import the function and add it to the `ALL_TOOL_FUNCTIONS` dictionary.
4.  **Enable Tool**: In `system.db`, set `enabled = 1` for the new tool in the `tools` table.

## Testing
- **Run all tests**: `python -m pytest tests/`
- **Run specific test file**: `python -m pytest tests/test_cortex_agent.py`
- **Test Cleanup**: The test suite automatically cleans up test users and their data. Use fixtures like `cleanup_test_users` and `cleanup_after_test`.

## Documentation
- **`README.md`**: Project overview and installation.
- **`developer.md`**: The source of truth for all development standards. Do not alter coding standards or AI instructions without permission.
- **`GEMINI.md`**: This file. Your guide for contributing to the project.
- **`moreinfo.md`**: In-depth technical project description.
- **`troubleshooting.md`**: Common installation and runtime issues. Suggest updates when applicable.
- **Module `readme.md`**: Each module has its own `readme.md` describing its purpose, features, and file system.
