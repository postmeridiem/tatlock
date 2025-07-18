// Profile page specific functionality

// Functions are now globally available from common.js
// import { showSection, registerSectionLoader } from './common.js';

// Profile management
let currentSection = 'profile';
let isEditing = false;

// Register section loaders
registerSectionLoader('profile', loadProfileInfo);
registerSectionLoader('change-password', setupPasswordEventListeners);
registerSectionLoader('memory-management', initializeMemoryManagement);

// Navigation handler
function handleHashNavigation() {
    const hash = window.location.hash.substring(1);
    const validSections = ['profile', 'change-password', 'memory-management'];
    const sectionId = validSections.includes(hash) ? hash : 'profile';
    showSection(sectionId);
}

document.addEventListener('DOMContentLoaded', function() {
    handleHashNavigation();
    window.addEventListener('hashchange', handleHashNavigation);
});

function showProfileSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });

    // Remove active class from all nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });

    // Show the selected section
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }

    // Add active class to the clicked nav item
    const activeNavItem = document.querySelector(`[onclick="showProfileSection('${sectionId}')"]`);
    if (activeNavItem) {
        activeNavItem.classList.add('active');
    }
}

// Toggle between view and edit modes
function toggleProfileEdit() {
    try {
        isEditing = !isEditing;
        const editBtn = document.getElementById('editProfileBtn');
        const profileContent = document.getElementById('profile-content');
        
        if (!editBtn || !profileContent) {
            console.error('Required elements not found: editBtn or profileContent');
            return;
        }
        
        if (isEditing) {
            // Hide the edit button when in edit mode
            editBtn.style.display = 'none';
            loadProfileEditForm();
        } else {
            // Show the edit button when in view mode
            editBtn.style.display = 'inline-block';
            editBtn.textContent = 'Edit Profile';
            editBtn.classList.remove('primary');
            editBtn.classList.add('secondary');
            loadProfileInfo();
        }
    } catch (error) {
        console.error('Error in toggleProfileEdit:', error);
        if (typeof snackbar !== 'undefined') {
            snackbar.error('Error toggling profile edit mode: ' + error.message);
        }
    }
}

// Load profile information in view mode
async function loadProfileInfo() {
    const profileContent = document.getElementById('profile-content');
    
    if (!profileContent) {
        console.error('profile-content element not found in loadProfileInfo');
        // Retry after a short delay
        setTimeout(loadProfileInfo, 100);
        return;
    }
    
    try {
        const response = await fetch('/profile/', {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load profile');
        
        const profile = await response.json();
        
        const infoHtml = `
            <div class="profile-grid">
                <div class="profile-item">
                    <label>Username</label>
                    <span>${profile.username}</span>
                </div>
                <div class="profile-item">
                    <label>First Name</label>
                    <span>${profile.first_name || '<span class="empty-value">Not set</span>'}</span>
                </div>
                <div class="profile-item">
                    <label>Last Name</label>
                    <span>${profile.last_name || '<span class="empty-value">Not set</span>'}</span>
                </div>
                <div class="profile-item">
                    <label>Email</label>
                    <span>${profile.email || '<span class="empty-value">Not set</span>'}</span>
                </div>
                <div class="profile-item">
                    <label>Roles</label>
                    <span>${profile.roles.length > 0 ? profile.roles.join(', ') : '<span class="empty-value">No roles assigned</span>'}</span>
                </div>
                <div class="profile-item">
                    <label>Groups</label>
                    <span>${profile.groups.length > 0 ? profile.groups.join(', ') : '<span class="empty-value">No groups assigned</span>'}</span>
                </div>
                <div class="profile-item">
                    <label>Member Since</label>
                    <span>${new Date(profile.created_at).toLocaleDateString('en-US', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                    })}</span>
                </div>
            </div>
        `;
        
        profileContent.innerHTML = infoHtml;
        
    } catch (error) {
        console.error('Error in loadProfileInfo:', error);
        if (profileContent) {
            profileContent.innerHTML = `
                <div class="error">
                    Error loading profile: ${error.message}
                </div>
            `;
        }
    }
}

// Load profile information in edit mode
async function loadProfileEditForm() {
    const profileContent = document.getElementById('profile-content');
    
    if (!profileContent) {
        console.error('profile-content element not found in loadProfileEditForm');
        // Retry after a short delay
        setTimeout(loadProfileEditForm, 100);
        return;
    }
    
    try {
        const response = await fetch('/profile/', {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load profile');
        
        const profile = await response.json();
        
        const formHtml = `
            <form id="profileForm">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" value="${profile.username}" readonly class="readonly-field">
                    <small>Username cannot be changed</small>
                </div>
                <div class="form-group">
                    <label for="firstName">First Name *</label>
                    <input type="text" id="firstName" value="${profile.first_name || ''}" required>
                </div>
                <div class="form-group">
                    <label for="lastName">Last Name *</label>
                    <input type="text" id="lastName" value="${profile.last_name || ''}" required>
                </div>
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" value="${profile.email || ''}">
                </div>
                <div class="form-actions">
                    <button type="submit" class="button">
                        Save Profile
                    </button>
                    <button type="button" class="button secondary" onclick="toggleProfileEdit()">
                        Cancel
                    </button>
                </div>
            </form>
        `;
        
        profileContent.innerHTML = formHtml;
        
        // Set up form submission
        setupProfileFormSubmission();
        
    } catch (error) {
        console.error('Error in loadProfileEditForm:', error);
        if (profileContent) {
            profileContent.innerHTML = `
                <div class="error">
                    Error loading profile: ${error.message}
                </div>
            `;
        }
    }
}

// Set up profile form submission
function setupProfileFormSubmission() {
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                first_name: document.getElementById('firstName').value,
                last_name: document.getElementById('lastName').value,
                email: document.getElementById('email').value
            };
            
            try {
                const response = await fetch('/profile/', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',  // Include session cookies
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Failed to update profile');
                
                const result = await response.json();
                snackbar.success('Profile updated successfully!');
                isEditing = false;
                toggleProfileEdit(); // This will switch back to view mode
                
            } catch (error) {
                snackbar.error('Error updating profile: ' + error.message);
            }
        });
    }
}

// Profile form submission
function initializeProfile() {
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeProfile);
        return;
    }
    
    // Check if required elements exist
    const profileContent = document.getElementById('profile-content');
    if (!profileContent) {
        console.error('profile-content element not found, retrying in 100ms...');
        setTimeout(initializeProfile, 100);
        return;
    }
    
    console.log('Profile page initializing...');
    loadProfileInfo();
    setupPasswordEventListeners();
    initializeMemoryManagement();
    
    // Initialize chat with profile-specific settings
    new TatlockChat({
        chatInput: document.getElementById('sidepane-input'),
        chatSendBtn: document.getElementById('sidepane-send-btn'),
        chatMessages: document.getElementById('sidepane-messages'),
        chatMicBtn: document.getElementById('sidepane-mic-btn'),
        sidebarTitle: 'Profile Assistant',
        welcomeMessage: 'How can I assist you with your profile settings today?',
        placeholder: 'Ask Tatlock...'
    });
}

function setupPasswordEventListeners() {
    // Password form submission
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (newPassword !== confirmPassword) {
                snackbar.error('New passwords do not match!');
                return;
            }
            
            const formData = {
                current_password: document.getElementById('currentPassword').value,
                new_password: newPassword
            };
            
            try {
                const response = await fetch('/profile/password', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',  // Include session cookies
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Failed to change password');
                
                snackbar.success('Password changed successfully!');
                passwordForm.reset();
                
            } catch (error) {
                snackbar.error('Error changing password: ' + error.message);
            }
        });
    }
}

/**
 * Initializes the memory management section.
 */
function initializeMemoryManagement() {
    const searchInput = document.getElementById('memory-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', (event) => {
            if (event.key === 'Enter') {
                loadConversations(event.target.value);
            }
        });
    }
    loadConversations();
}

async function loadConversations(searchTerm = '') {
    const conversationTableBody = document.getElementById('conversation-list-table-body');
    conversationTableBody.innerHTML = '<tr><td colspan="4" class="loading">Loading conversations...</td></tr>';

    try {
        let url = '/hippocampus/longterm/conversations';
        if (searchTerm) {
            url += `?search=${encodeURIComponent(searchTerm)}`;
        }
        const response = await fetch(url, { credentials: 'include' });

        if (!response.ok) {
            throw new Error(`Failed to fetch conversations: ${response.statusText}`);
        }

        const conversations = await response.json();
        renderConversations(conversations);
    } catch (error) {
        conversationTableBody.innerHTML = `<tr><td colspan="4" class="error-message">${error.message}</td></tr>`;
    }
}

function renderConversations(conversations) {
    const conversationTableBody = document.getElementById('conversation-list-table-body');
    if (!conversationTableBody) {
        console.error('conversation-list-table-body element not found');
        return;
    }
    if (conversations.length === 0) {
        conversationTableBody.innerHTML = '<tr><td colspan="4">No conversations found.</td></tr>';
        return;
    }

    let html = '';
    conversations.forEach(convo => {
        html += `
            <tr id="convo-${convo.id}">
                <td>${convo.topic || 'No Topic'}</td>
                <td>${convo.summary || 'No summary available.'}</td>
                <td>${new Date(convo.last_activity).toLocaleString()}</td>
                <td>
                    <button class="action-button view-btn" onclick="viewConversation('${convo.id}')">View</button>
                    <button class="action-button delete-btn" onclick="deleteConversation('${convo.id}')">Delete</button>
                </td>
            </tr>
        `;
    });
    conversationTableBody.innerHTML = html;
}

async function viewConversation(conversationId) {
    const modalContent = document.getElementById('conversationModalContent');
    const modalTitle = document.getElementById('conversationModalTitle');
    const modal = document.getElementById('conversationModal');
    
    // Check if modal elements exist
    if (!modalContent || !modalTitle || !modal) {
        console.error('Conversation modal elements not found. Modal may not be properly initialized.');
        alert('Error: Conversation modal not available. Please refresh the page and try again.');
        return;
    }
    
    modalContent.innerHTML = '<div class="loading">Loading messages...</div>';
    modal.style.display = 'flex';

    try {
        const response = await fetch(`/hippocampus/longterm/conversation/${conversationId}/messages`, { credentials: 'include' });
        if (!response.ok) throw new Error('Failed to fetch messages.');
        
        const messages = await response.json();
        modalTitle.textContent = `Conversation: ${messages.length > 0 ? messages[0].timestamp.split('T')[0] : ''}`;

        let html = '';
        messages.forEach(msg => {
            html += `
                <div class="message-bubble ${msg.role}">
                    <div class="message-role">${msg.role}</div>
                    <div class="message-content">${msg.content}</div>
                    <div class="message-timestamp">${new Date(msg.timestamp).toLocaleString()}</div>
                </div>
            `;
        });
        modalContent.innerHTML = html;
    } catch (error) {
        modalContent.innerHTML = `<div class="error-message">${error.message}</div>`;
    }
}

function closeConversationModal() {
    const modal = document.getElementById('conversationModal');
    if (modal) {
        modal.style.display = 'none';
    } else {
        console.error('Conversation modal not found when trying to close.');
    }
}

async function deleteConversation(conversationId) {
    if (!confirm('Are you sure you want to delete this entire conversation? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/hippocampus/longterm/conversation/${conversationId}`, {
            method: 'DELETE',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to delete conversation.');
        }

        // Remove the conversation from the view
        const convoDiv = document.getElementById(`convo-${conversationId}`);
        if (convoDiv) {
            convoDiv.remove();
        }
        showSnackbar('Conversation deleted successfully.', 'success');
    } catch (error) {
        showSnackbar(error.message, 'error');
    }
}

// Purge All Memories functionality
function showPurgeAllDialog() {
    const modal = document.getElementById('purgeAllModal');
    const confirmationInput = document.getElementById('purgeConfirmation');
    const confirmBtn = document.getElementById('confirmPurgeBtn');
    
    if (modal) {
        modal.style.display = 'flex';
        confirmationInput.value = '';
        confirmBtn.disabled = true;
        confirmationInput.focus();
        
        // Set up input validation
        confirmationInput.addEventListener('input', validatePurgeConfirmation);
    }
}

function closePurgeAllDialog() {
    const modal = document.getElementById('purgeAllModal');
    const confirmationInput = document.getElementById('purgeConfirmation');
    
    if (modal) {
        modal.style.display = 'none';
        confirmationInput.removeEventListener('input', validatePurgeConfirmation);
    }
}

function validatePurgeConfirmation() {
    const confirmationInput = document.getElementById('purgeConfirmation');
    const confirmBtn = document.getElementById('confirmPurgeBtn');
    
    if (confirmationInput.value.toLowerCase() === 'delete') {
        confirmBtn.disabled = false;
        confirmBtn.classList.add('danger');
    } else {
        confirmBtn.disabled = true;
        confirmBtn.classList.remove('danger');
    }
}

async function purgeAllMemories() {
    const confirmBtn = document.getElementById('confirmPurgeBtn');
    const confirmationInput = document.getElementById('purgeConfirmation');
    
    // Double-check the confirmation
    if (confirmationInput.value.toLowerCase() !== 'delete') {
        showSnackbar('Please type "delete" to confirm this action.', 'error');
        return;
    }
    
    // Disable the button to prevent double-clicks
    confirmBtn.disabled = true;
    confirmBtn.textContent = 'Purging...';
    
    try {
        const response = await fetch('/hippocampus/longterm/conversations/forgetall', {
            method: 'DELETE',
            credentials: 'include'
        });

        if (!response.ok) {
            throw new Error('Failed to purge all memories.');
        }

        // Close the modal
        closePurgeAllDialog();
        
        // Clear the conversation list
        const conversationList = document.getElementById('conversation-list');
        if (conversationList) {
            conversationList.innerHTML = '<p>All memories have been purged. No conversations found.</p>';
        }
        
        showSnackbar('All memories have been successfully purged.', 'success');
        
    } catch (error) {
        showSnackbar('Error purging all memories: ' + error.message, 'error');
        
        // Re-enable the button
        confirmBtn.disabled = false;
        confirmBtn.textContent = 'Purge All Memories';
    }
}

// Chat functionality - now handled by shared chat.js
// The chat functionality has been moved to stem/static/js/chat.js
// and is initialized above with logging disabled

// Example for activity list
function loadActivityList() {
    const activityList = document.getElementById('activity-list');
    if (!activityList) return;
    activityList.innerHTML = '<li class="loading">Loading activity...</li>';
    // ... fetch and populate activity items ...
}
// Repeat this pattern for any other dynamic content areas. 