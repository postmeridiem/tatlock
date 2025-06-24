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

// Shared section switching utility for all authenticated/admin pages
// Usage:
//   registerSectionLoader('users', loadUsers);
//   showSection('users');
//   (Call showSection on navigation, hash change, etc.)

const sectionLoaders = {};

export function registerSectionLoader(sectionId, loaderFn) {
    sectionLoaders[sectionId] = loaderFn;
}

export function showSection(sectionId) {
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

// Make functions globally available for non-module scripts
window.initializeHashNavigation = initializeHashNavigation;
window.showSection = showSection;

/**
 * Displays a snackbar notification.
 * @param {string} message - The message to display.
 * @param {string} type - The type of snackbar (e.g., 'success', 'error', 'info').
 * @param {number} duration - How long to display the snackbar in ms.
 */
function showSnackbar(message, type = 'info', duration = 4000) {
    const container = document.getElementById('snackbar-container');
    if (!container) {
        console.error('Snackbar container not found!');
        return;
    }

    const snackbar = document.createElement('div');
    snackbar.className = `snackbar ${type}`;
    
    const iconMap = {
        success: 'check_circle',
        error: 'error',
        warning: 'warning',
        info: 'info'
    };
    
    snackbar.innerHTML = `
        <div class="snackbar-icon">
            <span class="material-icons">${iconMap[type] || 'info'}</span>
        </div>
        <div class="snackbar-content">
            <p class="snackbar-message">${message}</p>
        </div>
        <button class="snackbar-close" onclick="this.parentElement.remove()">
            <span class="material-icons">close</span>
        </button>
    `;

    container.appendChild(snackbar);
    
    // Animate in
    setTimeout(() => {
        snackbar.classList.add('show');
    }, 10);

    // Automatically remove after duration
    setTimeout(() => {
        snackbar.classList.remove('show');
        // Remove from DOM after transition
        snackbar.addEventListener('transitionend', () => snackbar.remove());
    }, duration);
} 