// Admin dashboard specific functionality

let currentUserId = null;
let isEditMode = false;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadStats();
    loadUsers();
    loadRoles();
    loadGroups();
    setupAdminEventListeners();
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
    const usersContent = document.getElementById('users-content');
    
    try {
        const response = await fetch('/admin/users', {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load users');
        
        const users = await response.json();
        
        let usersHtml = '<table class="user-table"><thead><tr><th>Username</th><th>First Name</th><th>Last Name</th><th>Email</th><th>Roles</th><th>Groups</th><th>Actions</th></tr></thead><tbody>';
        
        users.forEach(user => {
            const roles = user.roles.map(role => `<span class="role-badge">${role}</span>`).join('');
            const groups = user.groups.map(group => `<span class="group-badge">${group}</span>`).join('');
            
            usersHtml += `
                <tr>
                    <td>${user.username}</td>
                    <td>${user.first_name || ''}</td>
                    <td>${user.last_name || ''}</td>
                    <td>${user.email || ''}</td>
                    <td>${roles}</td>
                    <td>${groups}</td>
                    <td>
                        <button class="action-button edit-btn" onclick="showUserModal('${user.username}')">Edit</button>
                        <button class="action-button delete-btn" onclick="deleteUser('${user.username}')">Delete</button>
                    </td>
                </tr>
            `;
        });
        
        usersHtml += '</tbody></table>';
        usersContent.innerHTML = usersHtml;
        
    } catch (error) {
        usersContent.innerHTML = `
            <div class="error">
                Error loading users: ${error.message}
            </div>
        `;
    }
}

// Load roles
async function loadRoles() {
    const rolesContent = document.getElementById('roles-content');
    
    try {
        const response = await fetch('/admin/roles', {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load roles');
        
        const roles = await response.json();
        
        let rolesHtml = '<div class="add-btn-container"><button class="add-btn" onclick="showRoleModal()">Add New Role</button></div>';
        rolesHtml += '<table class="user-table"><thead><tr><th>Role Name</th><th>Description</th><th>Actions</th></tr></thead><tbody>';
        
        roles.forEach(role => {
            rolesHtml += `
                <tr>
                    <td>${role.role_name}</td>
                    <td>${role.description || ''}</td>
                    <td>
                        <button class="action-button edit-btn" onclick="showRoleModal('${role.role_name}')">Edit</button>
                        <button class="action-button delete-btn" onclick="deleteRole('${role.role_name}')">Delete</button>
                    </td>
                </tr>
            `;
        });
        
        rolesHtml += '</tbody></table>';
        rolesContent.innerHTML = rolesHtml;
        
    } catch (error) {
        rolesContent.innerHTML = `
            <div class="error">
                Error loading roles: ${error.message}
            </div>
        `;
    }
}

// Load groups
async function loadGroups() {
    const groupsContent = document.getElementById('groups-content');
    
    try {
        const response = await fetch('/admin/groups', {
            credentials: 'include'  // Include session cookies
        });
        if (!response.ok) throw new Error('Failed to load groups');
        
        const groups = await response.json();
        
        let groupsHtml = '<div class="add-btn-container"><button class="add-btn" onclick="showGroupModal()">Add New Group</button></div>';
        groupsHtml += '<table class="user-table"><thead><tr><th>Group Name</th><th>Description</th><th>Actions</th></tr></thead><tbody>';
        
        groups.forEach(group => {
            groupsHtml += `
                <tr>
                    <td>${group.group_name}</td>
                    <td>${group.description || ''}</td>
                    <td>
                        <button class="action-button edit-btn" onclick="showGroupModal('${group.group_name}')">Edit</button>
                        <button class="action-button delete-btn" onclick="deleteGroup('${group.group_name}')">Delete</button>
                    </td>
                </tr>
            `;
        });
        
        groupsHtml += '</tbody></table>';
        groupsContent.innerHTML = groupsHtml;
        
    } catch (error) {
        groupsContent.innerHTML = `
            <div class="error">
                Error loading groups: ${error.message}
            </div>
        `;
    }
}

// User modal functions
function showUserModal(username = null) {
    const modal = document.getElementById('userModal');
    const modalTitle = document.getElementById('modalTitle');
    const form = document.getElementById('userForm');
    
    if (username) {
        modalTitle.textContent = 'Edit User';
        loadUserData(username);
        isEditMode = true;
    } else {
        modalTitle.textContent = 'Add New User';
        form.reset();
        isEditMode = false;
    }
    
    modal.style.display = 'block';
    loadRolesAndGroups();
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
        
        // Set roles and groups (this would need to be implemented based on your select elements)
        
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
        const roles = await rolesResponse.json();
        const rolesSelect = document.getElementById('roles');
        rolesSelect.innerHTML = roles.map(role => `<option value="${role.role_name}">${role.role_name}</option>`).join('');
        
        // Load groups for select
        const groupsResponse = await fetch('/admin/groups', {
            credentials: 'include'  // Include session cookies
        });
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
                password: document.getElementById('password').value
            };
            
            try {
                const url = isEditMode ? `/admin/users/${formData.username}` : '/admin/users';
                const method = isEditMode ? 'PUT' : 'POST';
                
                const response = await fetch(url, {
                    method: method,
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',  // Include session cookies
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Failed to save user');
                
                snackbar.success(isEditMode ? 'User updated successfully!' : 'User created successfully!');
                closeUserModal();
                loadUsers();
                
            } catch (error) {
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
                name: document.getElementById('roleName').value,
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
                name: document.getElementById('groupName').value,
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
    
    if (event.target === userModal) {
        closeUserModal();
    }
    if (event.target === roleModal) {
        closeRoleModal();
    }
    if (event.target === groupModal) {
        closeGroupModal();
    }
} 