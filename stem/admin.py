"""
stem/admin.py

Admin dashboard and user management functionality for Tatlock.
Provides admin endpoints for user management, statistics, and system administration.
"""

import logging
import os
import shutil
from pathlib import Path
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from stem.security import get_current_user, require_admin_role, security_manager, current_user
from stem.static import get_admin_page
from stem.system_settings import system_settings_manager
from stem.models import (
    CreateUserRequest, UpdateUserRequest, UserResponse, AdminStatsResponse,
    CreateRoleRequest, UpdateRoleRequest, RoleResponse,
    CreateGroupRequest, UpdateGroupRequest, GroupResponse, UserModel,
    SystemSettingResponse, UpdateSystemSettingRequest,
    SystemSettingCategoryResponse, CreateSystemSettingCategoryRequest, UpdateSystemSettingCategoryRequest
)

# Set up logging for this module
logger = logging.getLogger(__name__)

def create_user_directories(username: str) -> bool:
    """
    Create user directories for hippocampus shortterm image storage.
    
    Args:
        username (str): The username to create directories for
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create user directory and images subdirectory in shortterm
        user_dir = Path("hippocampus") / "shortterm" / username
        images_dir = user_dir / "images"
        
        # Create directories
        images_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created user directories for {username}: {images_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating user directories for {username}: {e}")
        return False

def delete_user_directories(username: str) -> bool:
    """
    Delete user directories for hippocampus shortterm image storage.
    
    Args:
        username (str): The username to delete directories for
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get user directory path in shortterm
        user_dir = Path("hippocampus") / "shortterm" / username
        
        if user_dir.exists():
            # Remove the entire user directory and all contents
            shutil.rmtree(user_dir)
            logger.info(f"Deleted user directories for {username}: {user_dir}")
        else:
            logger.info(f"User directories for {username} do not exist, skipping deletion")
        
        return True
        
    except Exception as e:
        logger.error(f"Error deleting user directories for {username}: {e}")
        return False

# Create admin router
admin_router = APIRouter(prefix="/admin", tags=["admin"])

@admin_router.get("/dashboard", response_class=HTMLResponse)
async def admin_page(request: Request, user: UserModel = Depends(require_admin_role)):
    """
    Admin dashboard page.
    Provides user, role, and group management interface.
    """
    if user is None:
        logger.warning("admin_page: No user from require_admin_role")
        raise HTTPException(status_code=401, detail="Not authenticated")
    return get_admin_page(request, user)

@admin_router.get("/")
async def admin_endpoint(_: None = Depends(require_admin_role)):
    """
    Admin-only endpoint for administrative functions.
    Requires admin role.
    """
    user = current_user
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return {
        "message": "Admin access granted",
        "user": {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": security_manager.get_user_roles(user.username),
            "groups": security_manager.get_user_groups(user.username)
        }
    }

@admin_router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(_: None = Depends(require_admin_role)):
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
async def list_users(_: None = Depends(require_admin_role)):
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
async def get_user(username: str, _: None = Depends(require_admin_role)):
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
async def create_user(request: CreateUserRequest, _: None = Depends(require_admin_role)):
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
        
        # Create user directories for hippocampus shortterm image storage
        if not create_user_directories(request.username):
            logger.warning(f"Failed to create user directories for {request.username}, but user was created successfully")
        
        # Get updated user info
        user_info = security_manager.get_user_by_username(request.username)
        if not user_info:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated user info")
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
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@admin_router.put("/users/{username}", response_model=UserResponse)
async def update_user(username: str, request: UpdateUserRequest, _: None = Depends(require_admin_role)):
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
        if not user_info:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated user info")
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
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@admin_router.delete("/users/{username}")
async def delete_user(username: str, request: Request, user: UserModel = Depends(require_admin_role)):
    """
    Delete a user.
    Requires admin role.
    """
    # Debug: log cookies and headers
    logger.warning(f"DELETE /users/{{username}} cookies: {request.cookies}")
    logger.warning(f"DELETE /users/{{username}} headers: {request.headers}")
    try:
        # Check if user exists
        user_to_delete = security_manager.get_user_by_username(username)
        if not user_to_delete:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent admin from deleting themselves
        if username == user.username:
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
        
        # Delete user directories for hippocampus shortterm image storage
        if not delete_user_directories(username):
            logger.warning(f"Failed to delete user directories for {username}, but user was deleted successfully")
        
        return {"message": f"User {user_to_delete['username']} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting user: {e}")

@admin_router.get("/roles")
async def list_roles(_: None = Depends(require_admin_role)):
    """
    List all available roles.
    Requires admin role.
    """
    try:
        return security_manager.get_all_roles()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing roles: {str(e)}")

@admin_router.get("/groups")
async def list_groups(_: None = Depends(require_admin_role)):
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
async def create_role(request: CreateRoleRequest, _: None = Depends(require_admin_role)):
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
        logger.error(f"Error creating role: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating role: {str(e)}")

@admin_router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(role_id: int, _: None = Depends(require_admin_role)):
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
async def update_role(role_id: int, request: UpdateRoleRequest, _: None = Depends(require_admin_role)):
    """
    Update an existing role.
    Requires admin role.
    """
    try:
        # Check if role exists
        role = security_manager.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
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
        if not updated_role:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated role info")
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
        logger.error(f"Error updating role: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating role: {str(e)}")

@admin_router.delete("/roles/{role_id}")
async def delete_role(role_id: int, _: None = Depends(require_admin_role)):
    """
    Delete a role.
    Requires admin role.
    """
    try:
        # Check if role exists
        role = security_manager.get_role_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check if role is in use
        user_count = security_manager.get_role_user_count(role_id)
        if user_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete role '{role['role_name']}' - it is assigned to {user_count} user(s)"
            )
        
        # Delete the role
        success = security_manager.delete_role(role_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete role")
        
        return {"message": f"Role '{role['role_name']}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting role: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting role: {str(e)}")

# Group CRUD Endpoints
@admin_router.post("/groups", response_model=GroupResponse)
async def create_group(request: CreateGroupRequest, _: None = Depends(require_admin_role)):
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
        logger.error(f"Error creating group: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating group: {str(e)}")

@admin_router.get("/groups/{group_id}", response_model=GroupResponse)
async def get_group(group_id: int, _: None = Depends(require_admin_role)):
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
async def update_group(group_id: int, request: UpdateGroupRequest, _: None = Depends(require_admin_role)):
    """
    Update an existing group.
    Requires admin role.
    """
    try:
        # Check if group exists
        group = security_manager.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
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
        if not updated_group:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated group info")
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
        logger.error(f"Error updating group: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating group: {str(e)}")

@admin_router.delete("/groups/{group_id}")
async def delete_group(group_id: int, _: None = Depends(require_admin_role)):
    """
    Delete a group.
    Requires admin role.
    """
    try:
        # Check if group exists
        group = security_manager.get_group_by_id(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # Check if group is in use
        user_count = security_manager.get_group_user_count(group_id)
        if user_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete group '{group['group_name']}' - it is assigned to {user_count} user(s)"
            )
        
        # Delete the group
        success = security_manager.delete_group(group_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete group")
        
        return {"message": f"Group '{group['group_name']}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting group: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting group: {str(e)}")

# System Settings Endpoints
@admin_router.get("/settings", response_model=list[SystemSettingResponse])
async def list_system_settings(_: None = Depends(require_admin_role)):
    """
    List all system settings.
    Requires admin role.
    """
    try:
        settings = system_settings_manager.get_all_settings()
        return [SystemSettingResponse(**setting) for setting in settings]
    except Exception as e:
        logger.error(f"Error listing system settings: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing system settings: {str(e)}")

@admin_router.get("/settings/{setting_key}", response_model=SystemSettingResponse)
async def get_system_setting(setting_key: str, _: None = Depends(require_admin_role)):
    """
    Get a specific system setting.
    Requires admin role.
    """
    try:
        settings = system_settings_manager.get_all_settings()
        setting = next((s for s in settings if s['setting_key'] == setting_key), None)
        
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        
        return SystemSettingResponse(**setting)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system setting: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting system setting: {str(e)}")

@admin_router.put("/settings/{setting_key}", response_model=SystemSettingResponse)
async def update_system_setting(setting_key: str, request: UpdateSystemSettingRequest, _: None = Depends(require_admin_role)):
    """
    Update a system setting.
    Requires admin role.
    """
    try:
        remove_previous = getattr(request, 'remove_previous', False)
        success = system_settings_manager.set_setting(setting_key, request.setting_value, remove_previous=remove_previous)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update setting")
        
        # Update tool status if API keys were changed
        if setting_key in ['openweather_api_key', 'google_api_key', 'google_cse_id']:
            system_settings_manager.update_tool_status_based_on_api_keys()
        
        # Get updated setting
        settings = system_settings_manager.get_all_settings()
        setting = next((s for s in settings if s['setting_key'] == setting_key), None)
        
        if not setting:
            raise HTTPException(status_code=500, detail="Setting updated but could not be retrieved")
        
        return SystemSettingResponse(**setting)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating system setting: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating system setting: {str(e)}")

@admin_router.get("/settings/categories", response_model=list[SystemSettingCategoryResponse])
async def list_system_setting_categories(_: None = Depends(require_admin_role)):
    """
    List all system setting categories.
    Requires admin role.
    """
    try:
        categories = system_settings_manager.get_categories()
        return [SystemSettingCategoryResponse(**category) for category in categories]
    except Exception as e:
        logger.error(f"Error listing system setting categories: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing system setting categories: {str(e)}")

@admin_router.post("/settings/categories", response_model=SystemSettingCategoryResponse)
async def create_system_setting_category(request: CreateSystemSettingCategoryRequest, _: None = Depends(require_admin_role)):
    """
    Create a new system setting category.
    Requires admin role.
    """
    try:
        success = system_settings_manager.create_category(
            category_name=request.category_name,
            display_name=request.display_name,
            description=request.description or "",
            sort_order=request.sort_order
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to create category. Category name may already exist.")
        
        # Get the created category
        categories = system_settings_manager.get_categories()
        category = next((c for c in categories if c['category_name'] == request.category_name), None)
        
        if not category:
            raise HTTPException(status_code=500, detail="Category created but could not be retrieved")
        
        return SystemSettingCategoryResponse(**category)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating system setting category: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating system setting category: {str(e)}")

@admin_router.delete("/settings/categories/{category_name}")
async def delete_system_setting_category(category_name: str, _: None = Depends(require_admin_role)):
    """
    Delete a system setting category.
    Requires admin role.
    """
    try:
        success = system_settings_manager.delete_category(category_name)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete category")
        
        return {"message": f"Category '{category_name}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting system setting category: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting system setting category: {str(e)}")

@admin_router.get("/settings/options/{setting_key}")
async def get_setting_options(setting_key: str, _: None = Depends(require_admin_role)):
    """
    Get allowed options for a setting (e.g., ollama_model).
    Requires admin role.
    """
    try:
        options = system_settings_manager.get_setting_options(setting_key)
        return options
    except Exception as e:
        logger.error(f"Error getting options for {setting_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting options: {str(e)}")

@admin_router.post("/settings/options/{setting_key}")
async def set_setting_options(setting_key: str, options: list[dict], _: None = Depends(require_admin_role)):
    """
    Set allowed options for a setting (admin only).
    """
    try:
        success = system_settings_manager.set_setting_options(setting_key, options)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to set options")
        return {"message": "Options updated"}
    except Exception as e:
        logger.error(f"Error setting options for {setting_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Error setting options: {str(e)}")

@admin_router.post("/settings/options/ollama_model/refresh")
async def refresh_ollama_model_options(_: None = Depends(require_admin_role)):
    """
    Refresh the list of available Ollama models from the Ollama API.
    Requires admin role.
    """
    try:
        success = system_settings_manager.refresh_ollama_model_options()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to refresh Ollama model options")
        return {"message": "Ollama model options refreshed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing Ollama model options: {str(e)}")

# Tools Management Endpoints

@admin_router.get("/tools")
async def list_tools(_: None = Depends(require_admin_role)):
    """
    List all tools in the system with their status and basic information.
    Requires admin role.
    """
    try:
        import sqlite3
        
        conn = sqlite3.connect("hippocampus/system.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tool_key, description, module, function_name, enabled, prompts
            FROM tools
            ORDER BY tool_key
        """)
        
        tools = []
        for row in cursor.fetchall():
            tool_key, description, module, function_name, enabled, prompts = row
            tools.append({
                "tool_key": tool_key,
                "description": description,
                "module": module,
                "function_name": function_name,
                "enabled": bool(enabled),
                "has_prompts": bool(prompts and prompts.strip())
            })
        
        conn.close()
        return tools
        
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing tools: {str(e)}")

@admin_router.get("/tools/{tool_key}")
async def get_tool_details(tool_key: str, _: None = Depends(require_admin_role)):
    """
    Get detailed information about a specific tool.
    Requires admin role.
    """
    try:
        import sqlite3
        
        conn = sqlite3.connect("hippocampus/system.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT tool_key, description, module, function_name, enabled, prompts
            FROM tools
            WHERE tool_key = ?
        """, (tool_key,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        tool_key, description, module, function_name, enabled, prompts = row
        
        # Get tool parameters
        cursor.execute("""
            SELECT name, type, description, is_required
            FROM tool_parameters
            WHERE tool_key = ?
            ORDER BY name
        """, (tool_key,))
        
        parameters = []
        for param_row in cursor.fetchall():
            param_name, param_type, param_description, required = param_row
            parameters.append({
                "name": param_name,
                "type": param_type,
                "description": param_description,
                "required": bool(required)
            })
        
        conn.close()
        
        return {
            "tool_key": tool_key,
            "description": description,
            "module": module,
            "function_name": function_name,
            "enabled": bool(enabled),
            "prompts": prompts,
            "parameters": parameters
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tool details for {tool_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting tool details: {str(e)}")

@admin_router.put("/tools/{tool_key}/status")
async def update_tool_status(tool_key: str, enabled: bool, _: None = Depends(require_admin_role)):
    """
    Enable or disable a tool.
    Requires admin role.
    """
    try:
        import sqlite3
        
        conn = sqlite3.connect("hippocampus/system.db")
        cursor = conn.cursor()
        
        # Check if tool exists
        cursor.execute("SELECT tool_key FROM tools WHERE tool_key = ?", (tool_key,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Tool not found")
        
        # Update tool status
        cursor.execute("""
            UPDATE tools 
            SET enabled = ? 
            WHERE tool_key = ?
        """, (1 if enabled else 0, tool_key))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Tool {tool_key} {'enabled' if enabled else 'disabled'} by admin")
        
        return {"message": f"Tool {tool_key} {'enabled' if enabled else 'disabled'} successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tool status for {tool_key}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating tool status: {str(e)}") 