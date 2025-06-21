// Common JavaScript functionality for Tatlock

// Snackbar notification system
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

// User dropdown menu management
function createUserDropdown() {
    const userDropdownContainer = document.getElementById('user-dropdown-container');
    if (!userDropdownContainer) {
        console.error('User dropdown container not found');
        return;
    }

    // Clear existing content
    userDropdownContainer.innerHTML = '';

    // Create dropdown button
    const dropdownButton = document.createElement('button');
    dropdownButton.className = 'user-dropdown-button';
    dropdownButton.id = 'user-dropdown-button';
    dropdownButton.innerHTML = `
        <span class="material-icons">account_circle</span>
        <span class="username" id="username-display">Loading...</span>
        <span class="material-icons">arrow_drop_down</span>
    `;

    // Create dropdown content
    const dropdownContent = document.createElement('div');
    dropdownContent.className = 'user-dropdown-content';
    dropdownContent.id = 'user-dropdown-content';
    dropdownContent.innerHTML = `
        <a href="/profile" class="user-dropdown-item">
            <span class="material-icons icon">person</span>
            Profile
        </a>
        <div class="user-dropdown-divider"></div>
        <div class="user-dropdown-item">
            <span class="material-icons icon">dark_mode</span>
            <span>Dark Mode</span>
            <label class="theme-toggle">
                <input type="checkbox" id="theme-toggle-checkbox">
                <span class="slider"></span>
            </label>
        </div>
        <div class="user-dropdown-divider"></div>
        <a href="/logout" class="user-dropdown-item">
            <span class="material-icons icon">logout</span>
            Logout
        </a>
    `;

    // Add elements to container
    userDropdownContainer.appendChild(dropdownButton);
    userDropdownContainer.appendChild(dropdownContent);

    // Add event listeners
    setupDropdownEventListeners();
    setupThemeToggle();
}

function setupDropdownEventListeners() {
    const dropdownButton = document.getElementById('user-dropdown-button');
    const dropdownContent = document.getElementById('user-dropdown-content');

    if (dropdownButton && dropdownContent) {
        dropdownButton.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownContent.classList.toggle('show');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!dropdownButton.contains(e.target) && !dropdownContent.contains(e.target)) {
                dropdownContent.classList.remove('show');
            }
        });
    }
}

function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle-checkbox');
    if (!themeToggle) return;

    // Set initial state based on current theme
    const currentTheme = localStorage.getItem('theme') || 'dark';
    themeToggle.checked = currentTheme === 'dark';

    // Update theme icon and label
    updateThemeToggleDisplay(currentTheme);

    themeToggle.addEventListener('change', function() {
        const newTheme = this.checked ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateThemeToggleDisplay(newTheme);
    });
}

function updateThemeToggleDisplay(theme) {
    const themeToggle = document.getElementById('theme-toggle-checkbox');
    if (!themeToggle) return;

    const iconElement = themeToggle.closest('.user-dropdown-item').querySelector('.material-icons');
    if (iconElement) {
        iconElement.textContent = theme === 'dark' ? 'light_mode' : 'dark_mode';
    }
}

// Sidebar navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    // Show selected section
    document.getElementById(sectionId).style.display = 'block';
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Header/nav bar logic
async function setupHeaderBar() {
    try {
        const resp = await fetch('/profile/pageheader', {
            credentials: 'include'  // Include session cookies
        });
        if (!resp.ok) {
            console.error('Failed to get page header info:', resp.status);
            // Still set up basic navigation even if auth fails
            setupBasicNavigation();
            return;
        }
        
        const info = await resp.json();
        
        // Navigation links
        let navHtml = '';
        navHtml += `<a href="/chat" id="nav-chat">Debug Console</a>`;
        if (info.is_admin) {
            navHtml += `<a href="/admin/dashboard" id="nav-admin">Admin Dashboard</a>`;
        }
        navHtml += `<a href="/docs" id="nav-docs">ApiDocs</a>`;
        
        const mainNav = document.getElementById('main-nav');
        if (mainNav) {
            mainNav.innerHTML = navHtml;
        }
        
        // Highlight current page
        highlightActivePage();
        
    } catch (e) {
        console.error('Error setting up header bar:', e);
        setupBasicNavigation();
    }
}

function setupBasicNavigation() {
    const mainNav = document.getElementById('main-nav');
    if (mainNav) {
        mainNav.innerHTML = `
            <a href="/chat" id="nav-chat">Debug Console</a>
            <a href="/docs" id="nav-docs">ApiDocs</a>
        `;
        highlightActivePage();
    }
}

// User dropdown functionality
function toggleUserDropdown() {
    const dropdown = document.getElementById('user-dropdown-content');
    dropdown.classList.toggle('show');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('user-dropdown-content');
    const dropdownBtn = document.querySelector('.user-dropdown-btn');
    
    if (dropdown && dropdownBtn) {
        if (!dropdown.contains(event.target) && !dropdownBtn.contains(event.target)) {
            dropdown.classList.remove('show');
        }
    }
});

// Logout functionality
async function logout() {
    const confirmed = await snackbar.confirm('Are you sure you want to logout?');
    if (!confirmed) return;
    
    try {
        // Clear any stored authentication data
        localStorage.removeItem('auth_token');
        sessionStorage.clear();
        
        // Redirect to login or show logout message
        snackbar.success('Logged out successfully!');
        
        // Redirect to a login page or refresh the page
        setTimeout(() => {
            window.location.href = '/'; // or wherever the login page is
        }, 1000);
        
    } catch (error) {
        snackbar.error('Error during logout: ' + error.message);
    }
}

// Chat sidepane functionality
function setupChatSidepane() {
    const chatInput = document.getElementById('chat-input');
    const chatSendBtn = document.getElementById('chat-send-btn');
    const chatMessages = document.getElementById('chat-messages');
    
    if (!chatInput || !chatSendBtn || !chatMessages) return;
    
    // Chat input handling
    chatInput.addEventListener('input', () => {
        chatSendBtn.disabled = !chatInput.value.trim();
        // Auto-resize textarea
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 100) + 'px';
    });
    
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });
    
    chatSendBtn.addEventListener('click', sendChatMessage);
    
    // Chat conversation history
    let chatHistory = [];
    let currentConversationId = null;
    
    function sendChatMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addChatMessage(message, 'user');
        
        // Add to conversation history
        chatHistory.push({ role: 'user', content: message });
        
        // Clear input
        chatInput.value = '';
        chatInput.style.height = 'auto';
        chatSendBtn.disabled = true;
        
        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.className = 'chat-message ai';
        typingDiv.innerHTML = '<em>Typing...</em>';
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Send to Tatlock
        fetch('/cortex', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',  // Include session cookies
            body: JSON.stringify({ 
                message: message, 
                history: chatHistory,
                conversation_id: currentConversationId
            })
        })
        .then(response => response.json())
        .then(data => {
            // Remove typing indicator
            chatMessages.removeChild(typingDiv);
            
            // Add AI response
            const aiResponse = data.response || 'I apologize, but I encountered an error processing your request.';
            addChatMessage(aiResponse, 'ai');
            
            // Add to conversation history
            chatHistory.push({ role: 'assistant', content: aiResponse });
            
            // Update conversation ID from response
            if (data.conversation_id) {
                currentConversationId = data.conversation_id;
            }
            
            // Keep history manageable (last 20 messages)
            if (chatHistory.length > 20) {
                chatHistory = chatHistory.slice(-20);
            }
        })
        .catch(error => {
            // Remove typing indicator
            chatMessages.removeChild(typingDiv);
            
            // Add error message
            addChatMessage('Sorry, I encountered an error. Please try again.', 'ai');
            console.error('Chat error:', error);
        });
    }
    
    function addChatMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Load user info and update dropdown
async function loadUserInfo() {
    try {
        const response = await fetch('/profile/pageheader', {
            credentials: 'include'  // Include session cookies
        });
        if (response.ok) {
            const userInfo = await response.json();
            updateUserDropdown(userInfo);
        } else {
            console.error('Failed to load user info:', response.status);
            // If unauthorized, redirect to login
            if (response.status === 401) {
                window.location.href = '/login';
            }
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

function updateUserDropdown(userInfo) {
    const usernameDisplay = document.getElementById('username-display');
    if (usernameDisplay) {
        usernameDisplay.textContent = userInfo.username || 'User';
    }
}

// Highlight active page in navigation
function highlightActivePage() {
    const path = window.location.pathname;
    const navItems = document.querySelectorAll('#main-nav a');
    
    navItems.forEach(item => {
        item.classList.remove('active');
    });
    
    if (path.startsWith('/admin')) {
        const adminLink = document.getElementById('nav-admin');
        if (adminLink) adminLink.classList.add('active');
    } else if (path.startsWith('/chat')) {
        const chatLink = document.getElementById('nav-chat');
        if (chatLink) chatLink.classList.add('active');
    } else if (path.startsWith('/profile')) {
        // Profile page doesn't have a nav link, so don't highlight anything
    } else {
        const docsLink = document.getElementById('nav-docs');
        if (docsLink) docsLink.classList.add('active');
    }
}

// Initialize common functionality
document.addEventListener('DOMContentLoaded', function() {
    // Create user dropdown
    createUserDropdown();
    
    // Setup header bar
    setupHeaderBar();
    
    // Load user info
    loadUserInfo();
    
    // Set initial theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    // Highlight active page in navigation
    highlightActivePage();
}); 