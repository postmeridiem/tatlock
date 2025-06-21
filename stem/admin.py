"""
stem/admin.py

Admin dashboard and user management functionality for Tatlock.
Provides admin endpoints for user management, statistics, and system administration.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from stem.security import get_current_user, require_admin_role, security_manager
from stem.static import get_admin_page
from stem.models import (
    CreateUserRequest, UpdateUserRequest, UserResponse, AdminStatsResponse,
    CreateRoleRequest, UpdateRoleRequest, RoleResponse,
    CreateGroupRequest, UpdateGroupRequest, GroupResponse
)

# Create admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/dashboard", response_class=HTMLResponse)
async def admin_page(current_user: dict = Depends(require_admin_role)):
    """
    Admin dashboard page.
    Requires admin role.
    Provides user, role, and group management interface.
    """
    return get_admin_page()

@admin_router.get("/")
async def admin_endpoint(current_user: dict = Depends(require_admin_role)):
    """
    Admin-only endpoint for administrative functions.
    Requires admin role.
    """
    return {
        "message": "Admin access granted",
        "user": {
            "username": current_user['username'],
            "first_name": current_user['first_name'],
            "last_name": current_user['last_name'],
            "roles": security_manager.get_user_roles(current_user['username']),
            "groups": security_manager.get_user_groups(current_user['username'])
        }
    }

@admin_router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(current_user: dict = Depends(require_admin_role)):
    """
    Get system statistics for admin dashboard.
    Requires admin role.
    """
    try:
        # Get basic counts
        total_users = len(security_manager.get_all_users())
        
        # Get users by role and group
        users_by_role = {}
        users_by_group = {}
        
        for user in security_manager.get_all_users():
            roles = security_manager.get_user_roles(user['username'])
            groups = security_manager.get_user_groups(user['username'])
            
            for role in roles:
                users_by_role[role] = users_by_role.get(role, 0) + 1
            for group in groups:
                users_by_group[group] = users_by_group.get(group, 0) + 1
        
        return AdminStatsResponse(
            total_users=total_users,
            total_roles=len(security_manager.get_all_roles()),
            total_groups=len(security_manager.get_all_groups()),
            users_by_role=users_by_role,
            users_by_group=users_by_group
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting admin stats: {str(e)}")

@admin_router.get("/users", response_model=list[UserResponse])
async def list_users(current_user: dict = Depends(require_admin_role)):
    """
    List all users in the system.
    Requires admin role.
    """
    try:
        users = security_manager.get_all_users()
        user_responses = []
        
        for user in users:
            roles = security_manager.get_user_roles(user['username'])
            groups = security_manager.get_user_groups(user['username'])
            
            user_responses.append(UserResponse(
                username=user['username'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                email=user['email'],
                created_at=user['created_at'],
                roles=roles,
                groups=groups
            ))
        
        return user_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing users: {str(e)}")

@admin_router.get("/users/{username}", response_model=UserResponse)
async def get_user(username: str, current_user: dict = Depends(require_admin_role)):
    """
    Get detailed information about a specific user.
    Requires admin role.
    """
    try:
        user = security_manager.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        roles = security_manager.get_user_roles(username)
        groups = security_manager.get_user_groups(username)
        
        return UserResponse(
            username=user['username'],
            first_name=user['first_name'],
            last_name=user['last_name'],
            email=user['email'],
            created_at=user['created_at'],
            roles=roles,
            groups=groups
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user: {str(e)}")

@admin_router.post("/users", response_model=UserResponse)
async def create_user(request: CreateUserRequest, current_user: dict = Depends(require_admin_role)):
    """
    Create a new user.
    Requires admin role.
    """
    try:
        # Create the user
        success = security_manager.create_user(
            username=request.username,
            first_name=request.first_name,
            last_name=request.last_name,
            password=request.password,
            email=request.email
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create user. Username may already exist.")
        
        # Assign roles
        for role in request.roles:
            security_manager.add_user_to_role(request.username, role)
        
        # Assign groups
        for group in request.groups:
            security_manager.add_user_to_group(request.username, group)
        
        # Get updated user info
        user_info = security_manager.get_user_by_username(request.username)
        if not user_info:
            raise HTTPException(status_code=500, detail="User created but could not retrieve user info")
        
        roles = security_manager.get_user_roles(request.username)
        groups = security_manager.get_user_groups(request.username)
        
        return UserResponse(
            username=user_info['username'],
            first_name=user_info['first_name'],
            last_name=user_info['last_name'],
            email=user_info['email'],
            created_at=user_info['created_at'],
            roles=roles,
            groups=groups
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@admin_router.put("/users/{username}", response_model=UserResponse)
async def update_user(username: str, request: UpdateUserRequest, current_user: dict = Depends(require_admin_role)):
    """
    Update an existing user.
    Requires admin role.
    """
    try:
        # Check if user exists
        user = security_manager.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update user information
        success = security_manager.update_user(
            username=username,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password=request.password
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update user")
        
        # Update roles if provided
        if request.roles is not None:
            security_manager.set_user_roles(username, request.roles)
        
        # Update groups if provided
        if request.groups is not None:
            security_manager.set_user_groups(username, request.groups)
        
        # Get updated user info
        user_info = security_manager.get_user_by_username(username)
        roles = security_manager.get_user_roles(username)
        groups = security_manager.get_user_groups(username)
        
        return UserResponse(
            username=user_info['username'],
            first_name=user_info['first_name'],
            last_name=user_info['last_name'],
            email=user_info['email'],
            created_at=user_info['created_at'],
            roles=roles,
            groups=groups
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@admin_router.delete("/users/{username}")
async def delete_user(username: str, current_user: dict = Depends(require_admin_role)):
    """
    Delete a user.
    Requires admin role.
    """
    try:
        # Check if user exists
        user = security_manager.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent admin from deleting themselves
        if username == current_user['username']:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        # Check if this is the last admin user
        user_roles = security_manager.get_user_roles(username)
        if 'admin' in user_roles:
            # Count total admin users
            all_users = security_manager.get_all_users()
            admin_count = 0
            for u in all_users:
                if 'admin' in security_manager.get_user_roles(u['username']):
                    admin_count += 1
            
            if admin_count <= 1:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot delete the last admin user. At least one admin must remain in the system."
                )
        
        # Delete the user
        success = security_manager.delete_user(username)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete user")
        
        return {"message": f"User {user['username']} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@admin_router.get("/roles")
async def list_roles(current_user: dict = Depends(require_admin_role)):
    """
    List all available roles.
    Requires admin role.
    """
    try:
        return security_manager.get_all_roles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing roles: {str(e)}")

@admin_router.get("/groups")
async def list_groups(current_user: dict = Depends(require_admin_role)):
    """
    List all available groups.
    Requires admin role.
    """
    try:
        return security_manager.get_all_groups()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing groups: {str(e)}")

# Role CRUD Endpoints
@admin_router.post("/roles", response_model=RoleResponse)
async def create_role(request: CreateRoleRequest, current_user: dict = Depends(require_admin_role)):
    """
    Create a new role.
    Requires admin role.
    """
    try:
        success = security_manager.create_role(
            role_name=request.role_name,
            description=request.description
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create role. Role name may already exist.")
        
        # Get the created role
        role = security_manager.get_role_by_name(request.role_name)
        if not role:
            raise HTTPException(status_code=500, detail="Role created but could not be retrieved")
        
        user_count = security_manager.get_role_user_count(role['id'])
        
        return RoleResponse(
            id=role['id'],
            role_name=role['role_name'],
            description=role['description'],
            created_at=role['created_at'],
            user_count=user_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating role: {str(e)}")

@admin_router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int, current_user: dict = Depends(require_admin_role)):
    """
    Get detailed information about a specific role.
    Requires admin role.
    """
    try:
        role = security_manager.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        user_count = security_manager.get_role_user_count(role_id)
        
        return RoleResponse(
            id=role['id'],
            role_name=role['role_name'],
            description=role['description'],
            created_at=role['created_at'],
            user_count=user_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting role: {str(e)}")

@admin_router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(role_id: int, request: UpdateRoleRequest, current_user: dict = Depends(require_admin_role)):
    """
    Update an existing role.
    Requires admin role.
    """
    try:
        # Check if role exists
        role = security_manager.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Prevent renaming of critical roles
        critical_roles = ['admin', 'user']
        if role['role_name'] in critical_roles and request.role_name and request.role_name != role['role_name']:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot rename critical role '{role['role_name']}'. This role is required for system operation."
            )
        
        # Update role information
        success = security_manager.update_role(
            role_id=role_id,
            role_name=request.role_name,
            description=request.description
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update role")
        
        # Get updated role info
        updated_role = security_manager.get_role_by_id(role_id)
        user_count = security_manager.get_role_user_count(role_id)
        
        return RoleResponse(
            id=updated_role['id'],
            role_name=updated_role['role_name'],
            description=updated_role['description'],
            created_at=updated_role['created_at'],
            user_count=user_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating role: {str(e)}")

@admin_router.delete("/roles/{role_id}")
async def delete_role(role_id: int, current_user: dict = Depends(require_admin_role)):
    """
    Delete a role.
    Requires admin role.
    """
    try:
        # Check if role exists
        role = security_manager.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Prevent deletion of critical roles
        critical_roles = ['admin', 'user']
        if role['role_name'] in critical_roles:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete critical role '{role['role_name']}'. This role is required for system operation."
            )
        
        # Check if role is in use
        user_count = security_manager.get_role_user_count(role_id)
        if user_count > 0:
            raise HTTPException(status_code=400, detail=f"Cannot delete role '{role['role_name']}' - it is assigned to {user_count} user(s)")
        
        # Delete the role
        success = security_manager.delete_role(role_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete role")
        
        return {"message": f"Role '{role['role_name']}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting role: {str(e)}")

# Group CRUD Endpoints
@admin_router.post("/groups", response_model=GroupResponse)
async def create_group(request: CreateGroupRequest, current_user: dict = Depends(require_admin_role)):
    """
    Create a new group.
    Requires admin role.
    """
    try:
        success = security_manager.create_group(
            group_name=request.group_name,
            description=request.description
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create group. Group name may already exist.")
        
        # Get the created group
        group = security_manager.get_group_by_name(request.group_name)
        if not group:
            raise HTTPException(status_code=500, detail="Group created but could not be retrieved")
        
        user_count = security_manager.get_group_user_count(group['id'])
        
        return GroupResponse(
            id=group['id'],
            group_name=group['group_name'],
            description=group['description'],
            created_at=group['created_at'],
            user_count=user_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating group: {str(e)}")

@admin_router.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int, current_user: dict = Depends(require_admin_role)):
    """
    Get detailed information about a specific group.
    Requires admin role.
    """
    try:
        group = security_manager.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        user_count = security_manager.get_group_user_count(group_id)
        
        return GroupResponse(
            id=group['id'],
            group_name=group['group_name'],
            description=group['description'],
            created_at=group['created_at'],
            user_count=user_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting group: {str(e)}")

@admin_router.put("/groups/{group_id}", response_model=GroupResponse)
async def update_group(group_id: int, request: UpdateGroupRequest, current_user: dict = Depends(require_admin_role)):
    """
    Update an existing group.
    Requires admin role.
    """
    try:
        # Check if group exists
        group = security_manager.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Prevent renaming of critical groups
        critical_groups = ['admins', 'users']
        if group['group_name'] in critical_groups and request.group_name and request.group_name != group['group_name']:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot rename critical group '{group['group_name']}'. This group is required for system operation."
            )
        
        # Update group information
        success = security_manager.update_group(
            group_id=group_id,
            group_name=request.group_name,
            description=request.description
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update group")
        
        # Get updated group info
        updated_group = security_manager.get_group_by_id(group_id)
        user_count = security_manager.get_group_user_count(group_id)
        
        return GroupResponse(
            id=updated_group['id'],
            group_name=updated_group['group_name'],
            description=updated_group['description'],
            created_at=updated_group['created_at'],
            user_count=user_count
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating group: {str(e)}")

@admin_router.delete("/groups/{group_id}")
async def delete_group(group_id: int, current_user: dict = Depends(require_admin_role)):
    """
    Delete a group.
    Requires admin role.
    """
    try:
        # Check if group exists
        group = security_manager.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Prevent deletion of critical groups
        critical_groups = ['admins', 'users']
        if group['group_name'] in critical_groups:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete critical group '{group['group_name']}'. This group is required for system operation."
            )
        
        # Check if group is in use
        user_count = security_manager.get_group_user_count(group_id)
        if user_count > 0:
            raise HTTPException(status_code=400, detail=f"Cannot delete group '{group['group_name']}' - it contains {user_count} user(s)")
        
        # Delete the group
        success = security_manager.delete_group(group_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete group")
        
        return {"message": f"Group '{group['group_name']}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting group: {str(e)}") 