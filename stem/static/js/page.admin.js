// Functions are now globally available from common.js
// import { showSection, registerSectionLoader } from './common.js';

// Admin dashboard specific functionality

let currentUserId = null;
let isEditMode = false;

// Ollama Model Modal State
let ollamaModelPendingValue = null;
let ollamaModelRemovePrevious = false;
let ollamaModelPreviousValue = null;

// Register section loaders
registerSectionLoader('stats', loadStats);
registerSectionLoader('users', loadUsers);
registerSectionLoader('roles-section', loadRoles);
registerSectionLoader('groups-section', loadGroups);
registerSectionLoader('tools-section', loadTools);
registerSectionLoader('settings-section', loadSystemSettings);

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    setupAdminEventListeners();
    new TatlockChat({
        chatInput: document.getElementById('sidepane-input'),
        chatSendBtn: document.getElementById('sidepane-send-btn'),
        chatMessages: document.getElementById('sidepane-messages'),
        chatMicBtn: document.getElementById('sidepane-mic-btn'),
        sidebarTitle: 'Admin Assistant',
        welcomeMessage: 'I\'m here to help you manage Tatlock. Ask me about user management, system administration, or any administrative tasks.',
        placeholder: 'Ask Tatlock...'
    });
    handleHashNavigation();
    loadSystemSettings();
    window.addEventListener('hashchange', handleHashNavigation);
});

function setupAdminEventListeners() {
    // All event listeners are already set up in the individual functions
    // This function is here for consistency and future use
}

// Load system statistics
async function loadStats() {
    const statsGrid = document.getElementById('stats-grid');
    
    try {
        const response = await fetch('/admin/stats', {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load stats');
        
        const stats = await response.json();
        
        statsGrid.innerHTML = `
            <div class="stat-card">
                <div class="stat-number">${stats.total_users}</div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.total_roles}</div>
                <div class="stat-label">Total Roles</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.total_groups}</div>
                <div class="stat-label">Total Groups</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${stats.users_by_role.admin || 0}</div>
                <div class="stat-label">Admin Users</div>
            </div>
        `;
        
    } catch (error) {
        statsGrid.innerHTML = `
            <div class="error">
                Error loading statistics: ${error.message}
            </div>
        `;
    }
}

// Load users
async function loadUsers() {
    const usersTableBody = document.getElementById('users-table-body');
    if (!usersTableBody) return;
    usersTableBody.innerHTML = '<tr><td colspan="7" class="loading">Loading users...</td></tr>';
    try {
        const response = await fetch('/admin/users', { credentials: 'include' });
        if (!response.ok) throw new Error('Failed to load users');
        const users = await response.json();
        if (!users.length) {
            usersTableBody.innerHTML = '<tr><td colspan="7" class="loading">No users found.</td></tr>';
            return;
        }
        usersTableBody.innerHTML = '';
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.first_name}</td>
                <td>${user.last_name}</td>
                <td>${user.email}</td>
                <td>${user.roles.join(', ')}</td>
                <td>${user.groups.join(', ')}</td>
                <td><button onclick="showUserModal('${user.username}')">Edit</button></td>
            `;
            usersTableBody.appendChild(row);
        });
    } catch (error) {
        usersTableBody.innerHTML = `<tr><td colspan="7" class="loading">Error: ${error.message}</td></tr>`;
    }
}

// Load roles
async function loadRoles() {
    const rolesTableBody = document.getElementById('roles-table-body');
    
    // Check if the roles section exists (might not be visible yet)
    if (!rolesTableBody) {
        console.log('Roles table body not found, skipping roles load');
        return;
    }
    
    try {
        const response = await fetch('/admin/roles', {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load roles');
        
        const roles = await response.json();
        
        // Clear existing rows
        rolesTableBody.innerHTML = '';
        
        // Add role rows dynamically
        roles.forEach(role => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${role.role_name}</td>
                <td>${role.description || ''}</td>
                <td>
                    <button class="action-button edit-btn" onclick="showRoleModal('${role.role_name}')">Edit</button>
                    <button class="action-button delete-btn" onclick="deleteRole('${role.role_name}')">Delete</button>
                </td>
            `;
            
            rolesTableBody.appendChild(row);
        });
        
    } catch (error) {
        rolesTableBody.innerHTML = `
            <tr>
                <td colspan="3">
                    <div class="error">
                        Error loading roles: ${error.message}
                    </div>
                </td>
            </tr>
        `;
    }
}

// Load groups
async function loadGroups() {
    const groupsTableBody = document.getElementById('groups-table-body');
    
    // Check if the groups section exists (might not be visible yet)
    if (!groupsTableBody) {
        console.log('Groups table body not found, skipping groups load');
        return;
    }
    
    try {
        const response = await fetch('/admin/groups', {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load groups');
        
        const groups = await response.json();
        
        // Clear existing rows
        groupsTableBody.innerHTML = '';
        
        // Add group rows dynamically
        groups.forEach(group => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${group.group_name}</td>
                <td>${group.description || ''}</td>
                <td>
                    <button class="action-button edit-btn" onclick="showGroupModal('${group.group_name}')">Edit</button>
                    <button class="action-button delete-btn" onclick="deleteGroup('${group.group_name}')">Delete</button>
                </td>
            `;
            
            groupsTableBody.appendChild(row);
        });
        
    } catch (error) {
        groupsTableBody.innerHTML = `
            <tr>
                <td colspan="3">
                    <div class="error">
                        Error loading groups: ${error.message}
                    </div>
                </td>
            </tr>
        `;
    }
}

// Load tools
async function loadTools() {
    const toolsTableBody = document.getElementById('tools-table-body');
    
    // Check if the tools section exists (might not be visible yet)
    if (!toolsTableBody) {
        console.log('Tools table body not found, skipping tools load');
        return;
    }
    
    try {
        const response = await fetch('/admin/tools', {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load tools');
        
        const tools = await response.json();
        
        // Clear existing rows
        toolsTableBody.innerHTML = '';
        
        // Add tool rows dynamically
        tools.forEach(tool => {
            const row = document.createElement('tr');
            
            const statusClass = tool.enabled ? 'status-enabled' : 'status-disabled';
            const statusText = tool.enabled ? 'Enabled' : 'Disabled';
            const toggleText = tool.enabled ? 'Disable' : 'Enable';
            const toggleClass = tool.enabled ? 'disable-btn' : 'enable-btn';
            
            row.innerHTML = `
                <td><strong>${tool.tool_key}</strong></td>
                <td>${tool.description}</td>
                <td>${tool.module}</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
                <td>
                    <button class="action-button ${toggleClass}" onclick="toggleToolStatus('${tool.tool_key}', ${!tool.enabled})">${toggleText}</button>
                    <button class="action-button view-btn" onclick="showToolModal('${tool.tool_key}')">View Details</button>
                </td>
            `;
            
            toolsTableBody.appendChild(row);
        });
        
    } catch (error) {
        toolsTableBody.innerHTML = `
            <tr>
                <td colspan="5">
                    <div class="error">
                        Error loading tools: ${error.message}
                    </div>
                </td>
            </tr>
        `;
    }
}

// Toggle tool status (enable/disable)
async function toggleToolStatus(toolKey, enabled) {
    try {
        const response = await fetch(`/admin/tools/${toolKey}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ enabled: enabled })
        });
        
        if (!response.ok) throw new Error('Failed to update tool status');
        
        const result = await response.json();
        snackbar.success(result.message);
        
        // Reload tools to reflect the change
        loadTools();
        
    } catch (error) {
        snackbar.error(`Error updating tool status: ${error.message}`);
    }
}

// Show tool details modal
async function showToolModal(toolKey) {
    try {
        const response = await fetch(`/admin/tools/${toolKey}`, {
            credentials: 'include'
        });
        
        if (!response.ok) throw new Error('Failed to load tool details');
        
        const tool = await response.json();
        
        // Populate modal with tool details
        document.getElementById('toolKey').textContent = tool.tool_key;
        document.getElementById('toolDescription').textContent = tool.description;
        document.getElementById('toolModule').textContent = tool.module;
        document.getElementById('toolFunctionName').textContent = tool.function_name;
        document.getElementById('toolStatus').textContent = tool.enabled ? 'Enabled' : 'Disabled';
        
        // Format prompts
        const promptsText = tool.prompts ? tool.prompts : 'No system prompts configured';
        document.getElementById('toolPrompts').textContent = promptsText;
        
        // Format parameters
        let parametersText = 'No parameters';
        if (tool.parameters && tool.parameters.length > 0) {
            parametersText = tool.parameters.map(param => 
                `${param.name} (${param.type})${param.required ? ' *' : ''} - ${param.description}`
            ).join('\n');
        }
        document.getElementById('toolParameters').textContent = parametersText;
        
        // Show modal
        document.getElementById('toolModal').style.display = 'flex';
        
    } catch (error) {
        snackbar.error(`Error loading tool details: ${error.message}`);
    }
}

// Close tool modal
function closeToolModal() {
    document.getElementById('toolModal').style.display = 'none';
}

// User modal functions
function showUserModal(username = null) {
    const modal = document.getElementById('userModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('userForm');
    const passwordField = document.getElementById('password');
    const passwordRequired = document.getElementById('password-required');
    
    modal.style.display = 'block';
    
    if (username) {
        modalTitle.textContent = 'Edit User';
        isEditMode = true;
        // Make password optional when editing
        passwordField.required = false;
        passwordRequired.textContent = '(leave blank to keep current password)';
        // Load roles and groups first, then load user data
        loadRolesAndGroups().then(() => {
            loadUserData(username);
        });
    } else {
        modalTitle.textContent = 'Add New User';
        form.reset();
        isEditMode = false;
        // Make password required when adding new user
        passwordField.required = true;
        passwordRequired.textContent = '*';
        loadRolesAndGroups();
    }
}

function closeUserModal() {
    document.getElementById('userModal').style.display = 'none';
    isEditMode = false;
}

async function loadUserData(username) {
    try {
        const response = await fetch(`/admin/users/${username}`, {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load user data');
        
        const user = await response.json();
        
        document.getElementById('username').value = user.username;
        document.getElementById('firstName').value = user.first_name || '';
        document.getElementById('lastName').value = user.last_name || '';
        document.getElementById('email').value = user.email || '';
        document.getElementById('password').value = '';
        
        // Set roles and groups
        const rolesSelect = document.getElementById('roles');
        const groupsSelect = document.getElementById('groups');
        
        // Clear previous selections
        Array.from(rolesSelect.options).forEach(option => option.selected = false);
        Array.from(groupsSelect.options).forEach(option => option.selected = false);
        
        // Set selected roles
        user.roles.forEach(role => {
            const option = rolesSelect.querySelector(`option[value="${role}"]`);
            if (option) option.selected = true;
        });
        
        // Set selected groups
        user.groups.forEach(group => {
            const option = groupsSelect.querySelector(`option[value="${group}"]`);
            if (option) option.selected = true;
        });
        
    } catch (error) {
        alert('Error loading user data: ' + error.message);
    }
}

async function loadRolesAndGroups() {
    try {
        // Load roles for select
        const rolesResponse = await fetch('/admin/roles', {
            credentials: 'include'  // Include session cookies
        });
        
        if (!rolesResponse.ok) {
            throw new Error(`Failed to load roles: ${rolesResponse.status}`);
        }
        
        const roles = await rolesResponse.json();
        const rolesSelect = document.getElementById('roles');
        rolesSelect.innerHTML = roles.map(role => `<option value="${role.role_name}">${role.role_name}</option>`).join('');
        
        // Load groups for select
        const groupsResponse = await fetch('/admin/groups', {
            credentials: 'include'  // Include session cookies
        });
        
        if (!groupsResponse.ok) {
            throw new Error(`Failed to load groups: ${groupsResponse.status}`);
        }
        
        const groups = await groupsResponse.json();
        const groupsSelect = document.getElementById('groups');
        groupsSelect.innerHTML = groups.map(group => `<option value="${group.group_name}">${group.group_name}</option>`).join('');
        
    } catch (error) {
        console.error('Error loading roles and groups:', error);
    }
}

// Role modal functions
function showRoleModal(roleName = null) {
    const modal = document.getElementById('roleModal');
    const modalTitle = document.getElementById('roleModalTitle');
    const form = document.getElementById('roleForm');
    
    if (roleName) {
        modalTitle.textContent = 'Edit Role';
        document.getElementById('roleName').value = roleName;
        // Load role description if available
    } else {
        modalTitle.textContent = 'Add New Role';
        form.reset();
    }
    
    modal.style.display = 'block';
}

function closeRoleModal() {
    document.getElementById('roleModal').style.display = 'none';
}

// Group modal functions
function showGroupModal(groupName = null) {
    const modal = document.getElementById('groupModal');
    const modalTitle = document.getElementById('groupModalTitle');
    const form = document.getElementById('groupForm');
    
    if (groupName) {
        modalTitle.textContent = 'Edit Group';
        document.getElementById('groupName').value = groupName;
        // Load group description if available
    } else {
        modalTitle.textContent = 'Add New Group';
        form.reset();
    }
    
    modal.style.display = 'block';
}

function closeGroupModal() {
    document.getElementById('groupModal').style.display = 'none';
}

// Form submissions
document.addEventListener('DOMContentLoaded', function() {
    // User form submission
    const userForm = document.getElementById('userForm');
    if (userForm) {
        userForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                username: document.getElementById('username').value,
                first_name: document.getElementById('firstName').value,
                last_name: document.getElementById('lastName').value,
                email: document.getElementById('email').value,
                roles: Array.from(document.getElementById('roles').selectedOptions).map(option => option.value),
                groups: Array.from(document.getElementById('groups').selectedOptions).map(option => option.value)
            };
            
            // Only include password if it's not empty (for new users) or if it's provided (for editing)
            const password = document.getElementById('password').value;
            if (!isEditMode || password.trim() !== '') {
                formData.password = password;
            }
            
            console.log('Sending user data:', formData);
            
            try {
                const url = isEditMode ? `/admin/users/${formData.username}` : '/admin/users';
                const method = isEditMode ? 'PUT' : 'POST';
                
                const response = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',  // Include session cookies
                    body: JSON.stringify(formData)
                });
                
                console.log('Response status:', response.status);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('Error response:', errorText);
                    throw new Error(`Failed to save user: ${response.status} - ${errorText}`);
                }
                
                const responseData = await response.json();
                console.log('Response data:', responseData);
                
                snackbar.success(isEditMode ? 'User updated successfully!' : 'User created successfully!');
                closeUserModal();
                loadUsers();
                
            } catch (error) {
                console.error('Error saving user:', error);
                snackbar.error('Error saving user: ' + error.message);
            }
        });
    }
    
    // Role form submission
    const roleForm = document.getElementById('roleForm');
    if (roleForm) {
        roleForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                role_name: document.getElementById('roleName').value,
                description: document.getElementById('roleDescription').value
            };
            
            try {
                const response = await fetch('/admin/roles', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',  // Include session cookies
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Failed to save role');
                
                snackbar.success('Role saved successfully!');
                closeRoleModal();
                loadRoles();
                
            } catch (error) {
                snackbar.error('Error saving role: ' + error.message);
            }
        });
    }
    
    // Group form submission
    const groupForm = document.getElementById('groupForm');
    if (groupForm) {
        groupForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                group_name: document.getElementById('groupName').value,
                description: document.getElementById('groupDescription').value
            };
            
            try {
                const response = await fetch('/admin/groups', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',  // Include session cookies
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Failed to save group');
                
                snackbar.success('Group saved successfully!');
                closeGroupModal();
                loadGroups();
                
            } catch (error) {
                snackbar.error('Error saving group: ' + error.message);
            }
        });
    }
});

// Delete functions
async function deleteUser(username) {
    const confirmed = await snackbar.confirm(`Are you sure you want to delete user "${username}"?`);
    if (!confirmed) return;
    
    try {
        const response = await fetch(`/admin/users/${username}`, {
            method: 'DELETE',
            credentials: 'include'  // Include session cookies
        });
        
        if (!response.ok) throw new Error('Failed to delete user');
        
        snackbar.success('User deleted successfully!');
        loadUsers();
        
    } catch (error) {
        snackbar.error('Error deleting user: ' + error.message);
    }
}

async function deleteRole(roleName) {
    const confirmed = await snackbar.confirm(`Are you sure you want to delete role "${roleName}"?`);
    if (!confirmed) return;
    
    try {
        const response = await fetch(`/admin/roles/${roleName}`, {
            method: 'DELETE',
            credentials: 'include'  // Include session cookies
        });
        
        if (!response.ok) throw new Error('Failed to delete role');
        
        snackbar.success('Role deleted successfully!');
        loadRoles();
        
    } catch (error) {
        snackbar.error('Error deleting role: ' + error.message);
    }
}

async function deleteGroup(groupName) {
    const confirmed = await snackbar.confirm(`Are you sure you want to delete group "${groupName}"?`);
    if (!confirmed) return;
    
    try {
        const response = await fetch(`/admin/groups/${groupName}`, {
            method: 'DELETE',
            credentials: 'include'  // Include session cookies
        });
        
        if (!response.ok) throw new Error('Failed to delete group');
        
        snackbar.success('Group deleted successfully!');
        loadGroups();
        
    } catch (error) {
        snackbar.error('Error deleting group: ' + error.message);
    }
}

// Close modals when clicking outside
window.onclick = function(event) {
    const userModal = document.getElementById('userModal');
    const roleModal = document.getElementById('roleModal');
    const groupModal = document.getElementById('groupModal');
    const toolModal = document.getElementById('toolModal');
    
    if (event.target === userModal) {
        closeUserModal();
    }
    if (event.target === roleModal) {
        closeRoleModal();
    }
    if (event.target === groupModal) {
        closeGroupModal();
    }
    if (event.target === toolModal) {
        closeToolModal();
    }
}

// Chat functionality - now handled by shared chat.js
// The chat functionality has been moved to stem/static/js/chat.js
// and is initialized above with logging disabled 

// Navigation handler
function handleHashNavigation() {
    const hash = window.location.hash.substring(1);
    const validSections = ['stats', 'users', 'roles-section', 'groups-section', 'tools-section', 'settings-section'];
    const sectionId = validSections.includes(hash) ? hash : 'stats';
    showSection(sectionId);
}

// System Settings Functions
async function loadSystemSettings() {
    const settingsContainer = document.querySelector('.settings-categories');
    
    try {
        const response = await fetch('/admin/settings', {
            credentials: 'include'
        });
        if (!response.ok) throw new Error('Failed to load system settings');
        
        const settings = await response.json();
        
        // Group settings by category
        const categorizedSettings = {};
        settings.forEach(setting => {
            const category = setting.category_name || 'uncategorized';
            if (!categorizedSettings[category]) {
                categorizedSettings[category] = {
                    display_name: setting.category_display_name || 'Uncategorized',
                    description: setting.category_description || '',
                    settings: []
                };
            }
            categorizedSettings[category].settings.push(setting);
        });
        
        // Sort settings within each category by sort_order
        Object.keys(categorizedSettings).forEach(category => {
            categorizedSettings[category].settings.sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));
        });
        
        let settingsHtml = '';
        
        Object.keys(categorizedSettings).forEach(category => {
            const categoryData = categorizedSettings[category];
            settingsHtml += `
                <div class="settings-category">
                    <h3 class="category-title">${categoryData.display_name}</h3>
                    ${categoryData.description ? `<p class="category-description">${categoryData.description}</p>` : ''}
                    <div class="settings-table-container">
                        <table class="settings-table">
                            <thead>
                                <tr>
                                    <th>Setting</th>
                                    <th>Value</th>
                                    <th>Description</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
            `;
            
            categoryData.settings.forEach(setting => {
                if (setting.setting_key === 'ollama_model') {
                    settingsHtml += renderOllamaModelRow(setting);
                } else {
                    const valueDisplay = setting.is_sensitive ? 
                        (setting.setting_value ? '••••••••' : 'Not set') : 
                        (setting.setting_value || 'Not set');
                    settingsHtml += `
                        <tr>
                            <td><strong>${setting.setting_key}</strong></td>
                            <td class="setting-value" data-setting-key="${setting.setting_key}">${valueDisplay}</td>
                            <td>${setting.description || ''}</td>
                            <td>
                                <button class="action-button edit-btn" onclick="editSetting('${setting.setting_key}', '${setting.setting_value || ''}', ${setting.is_sensitive})">Edit</button>
                            </td>
                        </tr>
                    `;
                }
            });
            
            settingsHtml += `
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        });
        
        settingsContainer.innerHTML = settingsHtml;
        // Attach event listeners for Ollama model dropdown and refresh
        setupOllamaModelDropdown();
        
    } catch (error) {
        settingsContainer.innerHTML = `
            <div class="error">
                Error loading system settings: ${error.message}
            </div>
        `;
    }
}

function renderOllamaModelRow(setting) {
    // Render the dropdown and refresh button for ollama_model
    const currentValue = setting.setting_value || 'Not set';
    return `
        <tr>
            <td><strong>${setting.setting_key}</strong></td>
            <td class="setting-value" data-setting-key="${setting.setting_key}">
                <select id="ollamaModelDropdown" class="ollama-model-dropdown">
                    <option value="">Loading...</option>
                </select>
                <div class="current-value-display">Current: ${currentValue}</div>
            </td>
            <td>${setting.description || ''}</td>
            <td>
                <button class="action-button" id="ollamaModelRefreshBtn">Refresh</button>
                <button class="action-button save-btn" id="ollamaModelSaveBtn">Save</button>
            </td>
        </tr>
    `;
}

async function setupOllamaModelDropdown() {
    const dropdown = document.getElementById('ollamaModelDropdown');
    const refreshBtn = document.getElementById('ollamaModelRefreshBtn');
    const saveBtn = document.getElementById('ollamaModelSaveBtn');
    if (!dropdown || !refreshBtn || !saveBtn) return;
    
    // Fetch options
    const options = await fetch('/admin/settings/options/ollama_model', { credentials: 'include' })
        .then(r => r.json())
        .catch(() => []);
    
    dropdown.innerHTML = '';
    options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt.option_value;
        option.textContent = opt.option_label;
        dropdown.appendChild(option);
    });
    
    // Get current value from the setting data
    const currentValue = await fetch('/admin/settings/ollama_model', { credentials: 'include' })
        .then(r => r.json())
        .then(setting => setting.setting_value)
        .catch(() => null);
    
    if (currentValue && options.some(opt => opt.option_value === currentValue)) {
        dropdown.value = currentValue;
        ollamaModelPreviousValue = currentValue;
    } else if (options.length > 0) {
        dropdown.value = options[0].option_value;
        ollamaModelPreviousValue = options[0].option_value;
    }
    
    // Refresh button
    refreshBtn.onclick = async () => {
        refreshBtn.disabled = true;
        try {
            await fetch('/admin/settings/options/ollama_model/refresh', { method: 'POST', credentials: 'include' });
            await setupOllamaModelDropdown();
        } catch (error) {
            snackbar.error('Failed to refresh Ollama models');
        } finally {
            refreshBtn.disabled = false;
        }
    };
    
    // Save button
    saveBtn.onclick = () => {
        const newValue = dropdown.value;
        if (newValue !== ollamaModelPreviousValue) {
            // Show modal if previous is not initial model
            if (ollamaModelPreviousValue && ollamaModelPreviousValue !== 'gemma3-cortex:latest') {
                ollamaModelPendingValue = newValue;
                showOllamaRemoveModal();
            } else {
                saveOllamaModel(newValue, false);
            }
        }
    };
}

function showOllamaRemoveModal() {
    document.getElementById('ollamaRemoveModal').style.display = 'block';
}
function closeOllamaRemoveModal() {
    document.getElementById('ollamaRemoveModal').style.display = 'none';
    ollamaModelPendingValue = null;
}
function confirmOllamaRemoveModal() {
    document.getElementById('ollamaRemoveModal').style.display = 'none';
    if (ollamaModelPendingValue) {
        saveOllamaModel(ollamaModelPendingValue, true);
        ollamaModelPendingValue = null;
    }
}
async function saveOllamaModel(newValue, removePrevious) {
    try {
        const response = await fetch(`/admin/settings/ollama_model`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ setting_value: newValue, remove_previous: !!removePrevious })
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update model');
        }
        snackbar.success('Ollama model updated and downloaded');
        ollamaModelPreviousValue = newValue;
        await loadSystemSettings();
    } catch (error) {
        snackbar.error(`Error updating model: ${error.message}`);
    }
}

function editSetting(settingKey, currentValue, isSensitive) {
    const newValue = prompt(`Enter new value for ${settingKey}:`, isSensitive ? '' : currentValue);
    
    if (newValue !== null) {
        updateSetting(settingKey, newValue);
    }
}

async function updateSetting(settingKey, newValue) {
    try {
        const response = await fetch(`/admin/settings/${settingKey}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                setting_value: newValue
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to update setting');
        }
        
        // Update the display
        const valueCell = document.querySelector(`[data-setting-key="${settingKey}"]`);
        if (valueCell) {
            const setting = await response.json();
            const valueDisplay = setting.is_sensitive ? 
                (setting.setting_value ? '••••••••' : 'Not set') : 
                (setting.setting_value || 'Not set');
            valueCell.textContent = valueDisplay;
        }
        
        snackbar.success(`Setting ${settingKey} updated successfully`);
        
    } catch (error) {
        snackbar.error(`Error updating setting: ${error.message}`);
    }
} 