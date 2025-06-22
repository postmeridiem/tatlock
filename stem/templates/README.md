# Jinja2 Templating System

This directory contains the Jinja2 templates for Tatlock's HTML pages. The templating system provides server-side rendering with shared components and layouts.

## Structure

```
templates/
├── base.html                 # Base layout template
├── login.html               # Login page template
├── chat.html                # Debug console template
├── profile.html             # User profile template
├── admin.html               # Admin dashboard template
├── components/              # Reusable components
│   ├── header.html          # Page header component
│   ├── footer.html          # Page footer component
│   ├── chat_sidebar.html    # Chat sidebar component
│   ├── navigation.html      # Sidebar navigation component
│   ├── modal.html           # Modal dialog component
│   ├── form.html            # Form component
│   └── snackbar.html        # Notification component
└── README.md               # This file
```

## Backend Integration

The templating system is managed by `stem/htmlcontroller.py` which provides:

- **TemplateManager**: Jinja2 environment and template rendering
- **render_template()**: Render template as string
- **render_page()**: Render template as HTMLResponse
- **get_common_context()**: Generate common template variables

## Base Layout

The `base.html` template provides the foundation for all pages:

- **Meta tags**: Viewport, theme, favicon, etc.
- **Stylesheets**: Material Icons, main CSS, page-specific CSS
- **Header**: Navigation bar (conditionally shown)
- **Main content**: Page-specific content area
- **Chat sidebar**: AI assistant (conditionally shown)
- **Footer**: Page footer (conditionally shown)
- **Scripts**: Common JS, page-specific JS

### Template Variables

The base layout uses these context variables:

- `app_name`: Application name (default: "Tatlock")
- `app_version`: Application version (default: "3.0.0")
- `user`: Current user data (if authenticated)
- `is_authenticated`: Whether user is logged in
- `is_admin`: Whether user has admin role
- `hide_header`: Skip header (for login page)
- `hide_footer`: Skip footer (for login page)
- `show_chat_sidebar`: Include chat sidebar
- `welcome_message`: Chat sidebar welcome message

## Page Templates

### Login Page (`login.html`)
- Extends base layout
- Hides header and footer
- Contains login form with validation
- Redirects to chat page on success

### Chat Page (`chat.html`)
- Debug console interface
- Includes chat sidebar with debug-specific welcome message
- Mobile-responsive design
- Real-time JSON logging

### Profile Page (`profile.html`)
- User profile management
- Includes chat sidebar with formal welcome message
- Profile editing and password change forms

### Admin Page (`admin.html`)
- Admin dashboard
- Includes chat sidebar with admin-specific welcome message
- User, role, and group management
- System statistics

## Shared Components

### Header Component (`components/header.html`)
- Application logo and title
- Navigation links (Profile, Admin, Debug)
- User dropdown with logout
- Responsive design

### Footer Component (`components/footer.html`)
- Copyright information
- User info (if authenticated)
- Links to API docs and debug console

### Chat Sidebar Component (`components/chat_sidebar.html`)
- AI assistant interface
- Message history
- Voice input support
- Configurable welcome message

### Navigation Component (`components/navigation.html`)
- Sidebar navigation menu
- Dynamic navigation items
- Active state highlighting

### Modal Component (`components/modal.html`)
- Reusable modal dialogs
- Dynamic form fields
- Password fields with toggle
- Cancel/Save buttons

### Form Component (`components/form.html`)
- Reusable form layouts
- Dynamic field types
- Validation support
- Help text

### Snackbar Component (`components/snackbar.html`)
- Notification container
- Used by JavaScript for user feedback

## Usage

### Rendering Templates

```python
from stem.htmlcontroller import render_template, render_page, get_common_context

# Get common context
context = get_common_context(request, user)

# Render template as string
html = render_template('login.html', context)

# Render template as HTMLResponse
response = render_page('login.html', context)
```

### Template Context

```python
context = {
    'user': user_data,
    'app_name': 'Tatlock',
    'app_version': '3.0.0',
    'is_authenticated': True,
    'is_admin': False,
    'show_chat_sidebar': True,
    'welcome_message': 'Custom welcome message'
}
```

### Including Components

```html
<!-- Include component with context -->
{% include 'components/header.html' %}

<!-- Include component with custom context -->
{% with custom_var='value' %}
    {% include 'components/modal.html' %}
{% endwith %}
```

## Benefits

1. **Server-side Rendering**: True server-side includes, not client-side string replacement
2. **Shared Components**: Reusable UI components across pages
3. **Consistent Layout**: Base template ensures consistent structure
4. **Dynamic Content**: Context variables for personalized content
5. **Maintainable**: Centralized template management
6. **Type Safety**: Template variables are properly typed
7. **Performance**: Templates are compiled and cached

## Migration from Static HTML

The old static HTML files in `stem/static/` have been replaced with Jinja2 templates:

- `login.html` → `templates/login.html`
- `chat.html` → `templates/chat.html`
- `profile.html` → `templates/profile.html`
- `admin.html` → `templates/admin.html`
- `chat-sidebar.html` → `templates/components/chat_sidebar.html`

The `stem/static.py` module has been updated to use the new templating system via `stem/htmlcontroller.py`.

## Future Enhancements

- **Template Inheritance**: More granular template inheritance
- **Custom Filters**: Jinja2 filters for common operations
- **Template Caching**: Compile-time template optimization
- **Component Library**: More reusable UI components
- **Theme Support**: Dynamic theme switching
- **Internationalization**: Multi-language support 