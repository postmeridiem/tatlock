# Jinja2 Templates Documentation

This directory contains all Jinja2 templates for Tatlock's web interface. These templates follow specific patterns for maintainability, performance, and consistency.

## Template Structure

### Base Template
- **`base.html`**: The foundation template that all other templates extend
- Provides common layout, header, navigation, and footer
- Defines blocks for content injection: `content`, `title`, `extra_css`, `page_styles`

### Page Templates
- **`page.login.html`**: Authentication page
- **`page.conversation.html`**: Main conversation interface
- **`page.profile.html`**: User profile management
- **`page.admin.html`**: Admin dashboard

### Components
- **`components/`**: Reusable UI components
  - **`header.html`**: Page header component
  - **`navigation.html`**: Sidebar navigation
  - **`modal.html`**: Modal dialog component
  - **`form.html`**: Form component
  - **`snackbar.html`**: Notification component
  - **`chat_sidebar.html`**: Chat sidebar component

## JavaScript File Organization

### File Naming Conventions
JavaScript files in `stem/static/js/` follow specific naming patterns for clarity and maintainability:

#### Page-Specific Scripts
- **Pattern**: `page.{pagename}.js`
- **Examples**:
  - `page.login.js` - Login page functionality
  - `page.conversation.js` - Conversation/debug console functionality
  - `page.profile.js` - User profile management
  - `page.admin.js` - Admin dashboard functionality

#### Shared Scripts
- **`common.js`** - Shared utilities and functions used across multiple pages
- **`component.chatbar.js`** - Chat sidebar functionality (separated from conversation page)

#### Plugin Scripts
- **Pattern**: `plugin.{library}.js`
- **Examples**:
  - `plugin.chart.min.js` - Chart.js library
  - `plugin.chart.umd.min.js.map` - Chart.js source map
  - `plugin.json-highlight.js` - JSON syntax highlighting library
  - `plugin.marked.min.js` - Markdown parsing library

#### Component Scripts
- **Pattern**: `component.{componentname}.js`
- **Examples**:
  - `component.chatbar.js` - Chat sidebar component functionality

#### Script Loading Order
Templates follow a consistent script loading order:
1. `common.js` - Shared utilities first
2. `auth.js` - Authentication functionality
3. Page-specific script (e.g., `page.admin.js`)
4. Plugin scripts as needed

### Benefits
- **Clear Purpose**: File names immediately indicate their purpose
- **Maintainability**: Easy to locate and modify specific functionality
- **Consistency**: Uniform naming across the codebase
- **Separation of Concerns**: Page-specific vs. shared functionality clearly separated
- **Plugin Management**: Third-party libraries clearly identified

## Jinja2 Template Integration Pattern

### Core Principle
**Keep HTML structure in templates, use JavaScript only for dynamic content updates.**

### Template Structure Pattern

```html
<!-- ✅ Correct: HTML structure in template -->
<div id="data-section" class="section">
    <div class="section-title">Data Management</div>
    <table class="data-table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Value</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="data-table-body">
            <!-- Dynamic content populated by JavaScript -->
        </tbody>
    </table>
</div>
```

### JavaScript Implementation Pattern

```javascript
// ✅ Correct: Update only dynamic content
async function loadData() {
    const tableBody = document.getElementById('data-table-body');
    
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        
        // Clear existing rows
        tableBody.innerHTML = '';
        
        // Add rows dynamically
        data.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.name}</td>
                <td>${item.value}</td>
                <td>
                    <button onclick="editItem('${item.id}')">Edit</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (error) {
        tableBody.innerHTML = `
            <tr><td colspan="3">Error: ${error.message}</td></tr>
        `;
    }
}
```

### What Goes Where

#### In Jinja2 Templates (Static Structure)
- Page layout and structure
- Table headers and column definitions
- Form structures and field labels
- Navigation elements
- CSS classes and styling structure
- Modal containers and static content
- Error message placeholders

#### In JavaScript (Dynamic Content)
- Table row data population
- Form value updates
- Real-time data updates
- User interaction responses
- AJAX content loading
- Dynamic element creation

## Template Variables

### Common Context Variables
All templates receive these variables from the backend:

```python
context = {
    'app_name': 'Tatlock',
    'app_version': '3.0.0',
    'user': user_data,  # Current user information
    'is_authenticated': True/False,
    'is_admin': True/False,
    'hide_header': False,  # Skip header (login page)
    'hide_footer': False,  # Skip footer
    'show_chat_sidebar': True/False,
    'welcome_message': 'Custom welcome message'
}
```

### Setting Template Variables
Use `{% set variable = value %}` for page-specific variables:

```html
{% extends "base.html" %}
{% set show_chat_sidebar = true %}
{% set welcome_message = 'Good day, sir. I am Tatlock, your AI assistant.' %}
```

## Template Inheritance

### Extending Base Template
```html
{% extends "base.html" %}

{% block title %}Page Title{% endblock %}

{% block content %}
    <!-- Page-specific content -->
{% endblock %}

{% block extra_css %}
    <!-- Additional CSS for this page -->
{% endblock %}
```

### Including Components
```html
{% from 'components/navigation.html' import render_nav %}
{% from 'components/modal.html' import render_modal %}

<!-- Use components -->
{{ render_nav(nav_items) }}
{{ render_modal('userModal', 'User Details') }}
```

## Best Practices

### 1. Template Organization
- Keep templates focused and single-purpose
- Use components for reusable UI elements
- Maintain consistent naming conventions

### 2. Variable Usage
- Always check for variable existence: `{{ user.name if user else 'Guest' }}`
- Use safe navigation: `{{ user.get('name', 'Unknown') }}`
- Provide fallbacks for optional data

### 3. JavaScript Integration
- Use data attributes for JavaScript hooks: `data-user-id="{{ user.id }}"`
- Keep event handlers in JavaScript files, not templates
- Use consistent ID naming: `{section}-{element}-{type}`

### 4. Error Handling
- Provide meaningful error messages in templates
- Use try-catch blocks in JavaScript for dynamic content
- Show loading states for async operations

### 5. Performance
- Minimize template logic and calculations
- Use efficient DOM manipulation in JavaScript
- Cache frequently accessed elements

## Common Patterns

### Modal Pattern
```html
<!-- Template: Modal container -->
<div id="userModal" class="modal">
    <div class="modal-content">
        <h2 id="modalTitle">User Details</h2>
        <form id="userForm">
            <!-- Form fields -->
        </form>
    </div>
</div>
```

```javascript
// JavaScript: Modal control
function showUserModal(userId = null) {
    const modal = document.getElementById('userModal');
    modal.style.display = 'block';
    
    if (userId) {
        loadUserData(userId);
    }
}
```

### Table Pattern
```html
<!-- Template: Table structure -->
<table class="data-table">
    <thead>
        <tr>
            <th>Name</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody id="data-table-body">
        <!-- Dynamic rows -->
    </tbody>
</table>
```

```javascript
// JavaScript: Row population
function populateTable(data) {
    const tbody = document.getElementById('data-table-body');
    tbody.innerHTML = '';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${item.name}</td><td>...</td>`;
        tbody.appendChild(row);
    });
}
```

## Debugging Templates

### Common Issues
1. **Syntax Errors**: Check Jinja2 syntax with proper `{% %}` and `{{ }}`
2. **Missing Variables**: Ensure all template variables are provided in context
3. **JavaScript Errors**: Check browser console for JavaScript issues
4. **CSS Issues**: Verify CSS classes and styling

### Debugging Tools
- Browser developer tools for JavaScript debugging
- Template syntax highlighting in your editor
- Jinja2 template testing with sample data

## Security Considerations

### Template Security
- Always escape user input: `{{ user_input|escape }}`
- Use safe filters for HTML content: `{{ content|safe }}`
- Validate all template variables from backend

### JavaScript Security
- Sanitize data before inserting into DOM
- Use parameterized queries for database operations
- Validate all user inputs on both client and server

## Maintenance

### Template Updates
1. Test templates with various data scenarios
2. Update documentation when adding new patterns
3. Maintain consistency across all templates
4. Review and refactor complex template logic

### Performance Monitoring
- Monitor template rendering times
- Optimize database queries that feed templates
- Cache static template content where appropriate
- Minimize JavaScript bundle size

This documentation should be updated whenever new patterns are introduced or existing patterns are modified. 