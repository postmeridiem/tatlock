"""
stem/profile.py

User profile management functionality for Tatlock.
Provides endpoints for users to manage their own profile information.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from stem.security import get_current_user, security_manager
from stem.models import UpdateUserRequest, UserResponse, PasswordChangeRequest

# Set up logging for this module
logger = logging.getLogger(__name__)

# Create profile router
profile_router = APIRouter(prefix="/profile", tags=["profile"])

@profile_router.get("/", response_model=UserResponse)
async def get_profile(user: dict = Depends(get_current_user)):
    """
    Get current user's profile information.
    Requires authentication.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        roles = security_manager.get_user_roles(user['username'])
        groups = security_manager.get_user_groups(user['username'])
        
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
        raise HTTPException(status_code=500, detail=f"Error getting profile: {str(e)}")

@profile_router.put("/", response_model=UserResponse)
async def update_profile(request: UpdateUserRequest, user: dict = Depends(get_current_user)):
    """
    Update current user's profile information.
    Requires authentication.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        # Update user information (username cannot be changed via profile)
        success = security_manager.update_user(
            username=user['username'],
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password=request.password
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update profile")
        
        # Get updated user info
        user_info = security_manager.get_user_by_username(user['username'])
        if not user_info:
            raise HTTPException(status_code=500, detail="Failed to retrieve updated user information")
        roles = security_manager.get_user_roles(user['username'])
        groups = security_manager.get_user_groups(user['username'])
        
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
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")

@profile_router.put("/password")
async def change_password(request: PasswordChangeRequest, user: dict = Depends(get_current_user)):
    """
    Change current user's password.
    Requires authentication and current password verification.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        # Verify current password
        auth_user = security_manager.authenticate_user(user['username'], request.current_password)
        if not auth_user:
            logger.info(f"Password verification failed for user: {user['username']}")
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        success = security_manager.update_user(
            username=user['username'],
            password=request.new_password
        )
        
        if not success:
            logger.info(f"Password update failed for user: {user['username']}")
            raise HTTPException(status_code=500, detail="Failed to update password")
        
        return {"message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in password change: {e}")
        raise HTTPException(status_code=500, detail=f"Error changing password: {str(e)}")

@profile_router.get("/pageheader")
async def get_page_header(user: dict = Depends(get_current_user)):
    """
    Returns user info for page header/nav bar: username, roles, is_admin.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    roles = security_manager.get_user_roles(user['username'])
    return {
        "username": user['username'],
        "roles": roles,
        "is_admin": "admin" in roles
    } 