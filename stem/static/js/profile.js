// Profile page specific functionality

// Profile management
let currentSection = 'profile-info';

// Password toggle functionality
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.nextElementSibling;
    
    if (input.type === 'password') {
        input.type = 'text';
        button.innerHTML = '<span class="material-icons">visibility_off</span>';
        button.title = 'Hide password';
    } else {
        input.type = 'password';
        button.innerHTML = '<span class="material-icons">visibility</span>';
        button.title = 'Show password';
    }
}

function showProfileSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected section
    document.getElementById(sectionId).style.display = 'block';
    currentSection = sectionId;
    
    // Update navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Load form data when showing edit section
    if (sectionId === 'edit-profile') {
        loadEditProfileForm();
    }
}

// Load profile information
async function loadProfileInfo() {
    const profileInfoContent = document.getElementById('profile-info-content');
    
    try {
        const response = await fetch('/profile/', {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load profile');
        
        const profile = await response.json();
        
        profileInfoContent.innerHTML = `
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
            <div class="profile-actions">
                <button class="button" onclick="showProfileSection('edit-profile')">Edit Profile</button>
            </div>
        `;
        
    } catch (error) {
        profileInfoContent.innerHTML = `
            <div class="error">
                Error loading profile: ${error.message}
            </div>
        `;
    }
}

// Load edit profile form
async function loadEditProfileForm() {
    try {
        const response = await fetch('/profile/');
        if (!response.ok) throw new Error('Failed to load profile');
        
        const profile = await response.json();
        
        document.getElementById('username').value = profile.username;
        document.getElementById('firstName').value = profile.first_name || '';
        document.getElementById('lastName').value = profile.last_name || '';
        document.getElementById('email').value = profile.email || '';
        
    } catch (error) {
        console.error('Error loading profile for edit:', error);
    }
}

// Profile form submission
document.addEventListener('DOMContentLoaded', function() {
    loadProfileInfo();
    setupProfileEventListeners();
    
    // Initialize chat with logging disabled for profile page
    initializeChat({
        enableLogging: false
    });
}); 

function setupProfileEventListeners() {
    // Profile form submission
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
                showProfileSection('profile-info');
                loadProfileInfo();
                
            } catch (error) {
                snackbar.error('Error updating profile: ' + error.message);
            }
        });
    }
    
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

// Chat functionality - now handled by shared chat.js
// The chat functionality has been moved to stem/static/js/chat.js
// and is initialized above with logging disabled 