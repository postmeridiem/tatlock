// Login/Logout page JavaScript for Tatlock
// Used on pages that don't require authentication (login, logout)

// Snackbar notification system for login pages
class LoginSnackbarManager {
    constructor() {
        this.container = document.getElementById('snackbar-container');
        this.notifications = [];
    }
    
    show(options) {
        const {
            title = '',
            message = '',
            type = 'info',
            duration = 5000,
            closable = true
        } = options;
        
        const snackbar = document.createElement('div');
        snackbar.className = `snackbar ${type}`;
        
        const icons = {
            success: '<span class="material-icons">check_circle</span>',
            error: '<span class="material-icons">error</span>',
            warning: '<span class="material-icons">warning</span>',
            info: '<span class="material-icons">info</span>'
        };
        
        snackbar.innerHTML = `
            <div class="snackbar-icon">${icons[type]}</div>
            <div class="snackbar-content">
                ${title ? `<div class="snackbar-title">${title}</div>` : ''}
                <div class="snackbar-message">${message}</div>
            </div>
            ${closable ? '<button class="snackbar-close" onclick="this.parentElement.remove()">×</button>' : ''}
        `;
        
        this.container.appendChild(snackbar);
        
        // Trigger animation
        setTimeout(() => {
            snackbar.classList.add('show');
        }, 10);
        
        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.hide(snackbar);
            }, duration);
        }
        
        return snackbar;
    }
    
    hide(snackbar) {
        snackbar.classList.remove('show');
        setTimeout(() => {
            if (snackbar.parentElement) {
                snackbar.remove();
            }
        }, 300);
    }
    
    // Convenience methods
    success(message, title = 'Success') {
        return this.show({ title, message, type: 'success' });
    }
    
    error(message, title = 'Error') {
        return this.show({ title, message, type: 'error' });
    }
    
    warning(message, title = 'Warning') {
        return this.show({ title, message, type: 'warning' });
    }
    
    info(message, title = 'Info') {
        return this.show({ title, message, type: 'info' });
    }
}

// Global snackbar instance for login pages
window.snackbar = new LoginSnackbarManager();

// Theme toggle functionality
function toggleTheme() {
    const html = document.documentElement;
    const currentTheme = html.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    html.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update theme toggle checkbox if it exists
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.checked = newTheme === 'light';
    }
}

// Initialize login page functionality
document.addEventListener('DOMContentLoaded', function() {
    // Set initial theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Handle login form submission
    const loginForm = document.getElementById('login-form') || document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(loginForm);
            const username = formData.get('username');
            const password = formData.get('password');
            const loginBtn = document.getElementById('loginBtn');
            const btnText = loginBtn?.querySelector('.btn-text');
            const loading = loginBtn?.querySelector('.loading');
            const errorMessage = document.getElementById('errorMessage');
            
            console.log('Login attempt for username:', username);
            
            // Show loading state
            if (loginBtn) {
                loginBtn.disabled = true;
                if (btnText) btnText.style.display = 'none';
                if (loading) loading.style.display = 'inline';
            }
            if (errorMessage) errorMessage.style.display = 'none';
            
            try {
                console.log('Sending request to /login/auth...');
                const response = await fetch('/login/auth', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password }),
                    credentials: 'include'
                });
                
                console.log('Response status:', response.status);
                
                if (response.ok) {
                    console.log('Login successful, redirecting...');
                    // Login successful, redirect to the original page or default
                    const urlParams = new URLSearchParams(window.location.search);
                    const redirectUrl = urlParams.get('redirect') || '/chat';
                    console.log('Redirecting to:', redirectUrl);
                    window.location.href = redirectUrl;
                } else {
                    console.log('Login failed with status:', response.status);
                    // Login failed
                    const errorData = await response.json();
                    const errorMsg = errorData.detail || 'Invalid username or password';
                    
                    if (errorMessage) {
                        errorMessage.textContent = errorMsg;
                        errorMessage.style.display = 'block';
                    } else {
                        snackbar.error(errorMsg, 'Authentication Error');
                    }
                }
            } catch (error) {
                console.error('Login error:', error);
                const errorMsg = 'Network error. Please try again.';
                
                if (errorMessage) {
                    errorMessage.textContent = errorMsg;
                    errorMessage.style.display = 'block';
                } else {
                    snackbar.error(errorMsg, 'Connection Error');
                }
            } finally {
                // Reset button state
                if (loginBtn) {
                    loginBtn.disabled = false;
                    if (btnText) btnText.style.display = 'inline';
                    if (loading) loading.style.display = 'none';
                }
            }
        });
    }
    
    // Handle logout
    const logoutLink = document.querySelector('a[href="/logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', async function(e) {
            e.preventDefault();
            
            // Redirect to GET /logout endpoint which will handle the logout and redirect
            window.location.href = '/logout';
        });
    }
    
    // Focus username field on page load
    const usernameField = document.getElementById('username');
    if (usernameField) {
        usernameField.focus();
    }
}); 