// Common JavaScript functions for Tatlock
// Shared functionality used across both authenticated and non-authenticated pages

// Password visibility toggle
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const toggleBtn = input.parentElement.querySelector('.password-toggle');
    const icon = toggleBtn.querySelector('.material-icons');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = 'visibility_off';
        toggleBtn.title = 'Hide password';
    } else {
        input.type = 'password';
        icon.textContent = 'visibility';
        toggleBtn.title = 'Show password';
    }
}

// Comprehensive Snackbar notification system
class SnackbarManager {
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
    
    // Replace confirm dialogs
    confirm(message, title = 'Confirm') {
        return new Promise((resolve) => {
            const snackbar = this.show({
                title,
                message: `${message}<br><br><button onclick="this.parentElement.parentElement.parentElement.remove(); window.snackbarConfirmResult = true;" class="button">Yes</button> <button onclick="this.parentElement.parentElement.parentElement.remove(); window.snackbarConfirmResult = false;" class="button">No</button>`,
                type: 'warning',
                duration: 0,
                closable: false
            });
            
            // Listen for result
            const checkResult = setInterval(() => {
                if (typeof window.snackbarConfirmResult !== 'undefined') {
                    clearInterval(checkResult);
                    const result = window.snackbarConfirmResult;
                    delete window.snackbarConfirmResult;
                    resolve(result);
                }
            }, 100);
        });
    }
}

// Global snackbar instance
window.snackbar = new SnackbarManager();

// User dropdown functionality
function toggleUserDropdown() {
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('show');
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('user-dropdown');
    const dropdownBtn = document.querySelector('.user-dropdown-button');
    
    if (dropdown && dropdownBtn) {
        if (!dropdown.contains(event.target) && !dropdownBtn.contains(event.target)) {
            dropdown.classList.remove('show');
        }
    }
});

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

// Load user info and update header
async function loadUserInfo() {
    try {
        const response = await fetch('/profile/pageheader', {
            credentials: 'include'  // Include session cookies
        });
        if (response.ok) {
            const userInfo = await response.json();
            
            // Update username in the header if it exists
            const usernameElement = document.querySelector('.user-dropdown-button .username');
            if (usernameElement) {
                usernameElement.textContent = userInfo.username || 'User';
            }
        } else {
            console.error('Failed to load user info:', response.status);
            // If unauthorized, redirect to login with current path
            if (response.status === 401) {
                const currentPath = window.location.pathname + window.location.search;
                window.location.href = `/login?redirect=${encodeURIComponent(currentPath)}`;
            }
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Prevent default anchor link scrolling behavior
function setupAnchorLinkHandling() {
    // Handle clicks on anchor links
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a[href^="#"]');
        if (link) {
            e.preventDefault();
            
            const targetId = link.getAttribute('href').substring(1);
            scrollToElement(targetId);
        }
    });
    
    // Handle direct URL navigation with hash
    if (window.location.hash) {
        // Wait for DOM to be fully loaded
        setTimeout(() => {
            const targetId = window.location.hash.substring(1);
            scrollToElement(targetId);
        }, 100);
    }
    
    // Handle hash changes (back/forward navigation)
    window.addEventListener('hashchange', function() {
        if (window.location.hash) {
            const targetId = window.location.hash.substring(1);
            scrollToElement(targetId);
        }
    });
}

// Scroll to element within the appropriate scrollable container
function scrollToElement(targetId) {
    const targetElement = document.getElementById(targetId);
    
    if (targetElement) {
        // Find the scrollable container that contains the target element
        const scrollableContainer = findScrollableContainer(targetElement);
        
        if (scrollableContainer) {
            // Calculate the position relative to the scrollable container
            const containerRect = scrollableContainer.getBoundingClientRect();
            const targetRect = targetElement.getBoundingClientRect();
            const scrollTop = scrollableContainer.scrollTop;
            
            // Calculate the target position within the container
            const targetPosition = scrollTop + (targetRect.top - containerRect.top) - 20; // 20px offset
            
            // Smooth scroll to the target within the container
            scrollableContainer.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    }
}

// Find the scrollable container that contains the given element
function findScrollableContainer(element) {
    let parent = element.parentElement;
    
    while (parent) {
        const style = window.getComputedStyle(parent);
        const overflowY = style.overflowY;
        
        // Check if this container is scrollable
        if (overflowY === 'auto' || overflowY === 'scroll') {
            return parent;
        }
        
        parent = parent.parentElement;
    }
    
    // If no scrollable container found, return the main content area
    return document.querySelector('.main-content');
}

// Shared section switching utility for all authenticated/admin pages
// Usage:
//   registerSectionLoader('users', loadUsers);
//   showSection('users');
//   (Call showSection on navigation, hash change, etc.)

const sectionLoaders = {};

function registerSectionLoader(sectionId, loaderFn) {
    sectionLoaders[sectionId] = loaderFn;
}

function showSection(sectionId) {
    if (window.location.hash.substring(1) !== sectionId) {
        window.location.hash = sectionId;
    }
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    // Show the requested section
    const section = document.getElementById(sectionId);
    if (section) {
        section.style.display = '';
        // Call the loader if registered
        if (sectionLoaders[sectionId]) {
            sectionLoaders[sectionId]();
        }
    }
}

/**
 * Handles showing the correct section based on the URL hash on page load.
 * @param {string} defaultSectionId - The ID of the section to show if no valid hash is found.
 */
function initializeHashNavigation(defaultSectionId) {
    const hash = window.location.hash.substring(1);
    const sectionIdToShow = hash || defaultSectionId;

    // Check if a section with this ID exists before showing
    if (document.getElementById(sectionIdToShow)) {
        showSection(sectionIdToShow);
    } else if (document.getElementById(defaultSectionId)) {
        showSection(defaultSectionId);
    }
}

// Legacy showSnackbar function for backward compatibility
function showSnackbar(message, type = 'info', duration = 4000) {
    return window.snackbar.show({ message, type, duration });
}

// Make functions globally available for non-module scripts
window.initializeHashNavigation = initializeHashNavigation;
window.showSection = showSection;
window.registerSectionLoader = registerSectionLoader;
window.showSnackbar = showSnackbar;
window.toggleUserDropdown = toggleUserDropdown;
window.toggleTheme = toggleTheme;
window.loadUserInfo = loadUserInfo;
window.setupAnchorLinkHandling = setupAnchorLinkHandling;
window.scrollToElement = scrollToElement;
window.findScrollableContainer = findScrollableContainer;

// Initialize common functionality
document.addEventListener('DOMContentLoaded', function() {
    // Load user info (only on authenticated pages)
    if (document.querySelector('.user-dropdown-button')) {
        loadUserInfo();
    }
    
    // Set initial theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Setup anchor link handling
    setupAnchorLinkHandling();
}); 