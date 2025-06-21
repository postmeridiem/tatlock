"""
stem/profile.py

User profile management functionality for Tatlock.
Provides endpoints for users to manage their own profile information.
"""

from fastapi import APIRouter, HTTPException, Depends
from stem.security import get_current_user, security_manager
from stem.models import UpdateUserRequest, UserResponse, PasswordChangeRequest

# Create profile router
profile_router = APIRouter(prefix="/profile", tags=["profile"])

@profile_router.get("/", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user's profile information.
    Requires authentication.
    """
    try:
        user = security_manager.get_user_by_username(current_user['username'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        roles = security_manager.get_user_roles(current_user['username'])
        groups = security_manager.get_user_groups(current_user['username'])
        
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
async def update_profile(request: UpdateUserRequest, current_user: dict = Depends(get_current_user)):
    """
    Update current user's profile information.
    Requires authentication.
    """
    try:
        # Update user information (username cannot be changed via profile)
        success = security_manager.update_user(
            username=current_user['username'],
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            password=request.password
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update profile")
        
        # Get updated user info
        user_info = security_manager.get_user_by_username(current_user['username'])
        roles = security_manager.get_user_roles(current_user['username'])
        groups = security_manager.get_user_groups(current_user['username'])
        
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
async def change_password(request: PasswordChangeRequest, current_user: dict = Depends(get_current_user)):
    """
    Change current user's password.
    Requires authentication and current password verification.
    """
    try:
        # Verify current password
        user = security_manager.authenticate_user(current_user['username'], request.current_password)
        if not user:
            print(f"Password verification failed for user: {current_user['username']}")
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        # Update password
        success = security_manager.update_user(
            username=current_user['username'],
            password=request.new_password
        )
        
        if not success:
            print(f"Password update failed for user: {current_user['username']}")
            raise HTTPException(status_code=500, detail="Failed to update password")
        
        return {"message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in password change: {e}")
        raise HTTPException(status_code=500, detail=f"Error changing password: {str(e)}")

@profile_router.get("/pageheader")
async def get_page_header(current_user: dict = Depends(get_current_user)):
    """
    Returns user info for page header/nav bar: username, roles, is_admin.
    """
    roles = security_manager.get_user_roles(current_user['username'])
    return {
        "username": current_user['username'],
        "roles": roles,
        "is_admin": "admin" in roles
    } 