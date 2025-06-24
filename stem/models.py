"""
models.py

Pydantic models for the Tatlock API.
Defines the data structures for requests and responses.
"""

from pydantic import BaseModel, Field
from typing import List, Dict

class ChatMessage(BaseModel):
    """
    Represents a single message in the chat history.
    """
    role: str
    content: str
    tool_calls: List | None = None

class ChatRequest(BaseModel):
    """
    Request model for the chat endpoint.
    """
    message: str = Field(..., description="The user's message for the AI.")
    history: List[ChatMessage] = Field(default_factory=list, description="Previous conversation history.")
    conversation_id: str | None = Field(None, description="Conversation ID for grouping related messages.")

class ChatResponse(BaseModel):
    """
    Response model for the chat endpoint.
    """
    response: str = Field(..., description="The AI's response.")
    topic: str = Field(..., description="The AI's classification of the topic")
    history: List[ChatMessage] = Field(..., description="The full updated conversation history.")
    conversation_id: str = Field(..., description="Conversation ID for grouping related messages.")
    processing_time: float = Field(..., description="Processing time in seconds.")

# Admin Models
class CreateUserRequest(BaseModel):
    """
    Request model for creating a new user.
    """
    username: str = Field(..., description="Unique username")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    password: str = Field(..., description="User's password")
    email: str | None = Field(None, description="User's email address")
    roles: List[str] = Field(default_factory=list, description="Roles to assign to user")
    groups: List[str] = Field(default_factory=list, description="Groups to assign to user")

class UpdateUserRequest(BaseModel):
    """
    Request model for updating a user.
    """
    first_name: str | None = Field(None, description="User's first name")
    last_name: str | None = Field(None, description="User's last name")
    email: str | None = Field(None, description="User's email address")
    password: str | None = Field(None, description="New password (optional)")
    roles: List[str] | None = Field(None, description="Roles to assign to user")
    groups: List[str] | None = Field(None, description="Groups to assign to user")

class UserResponse(BaseModel):
    """
    Response model for user information.
    """
    username: str
    first_name: str
    last_name: str
    email: str | None
    created_at: str
    roles: List[str]
    groups: List[str]

class AdminStatsResponse(BaseModel):
    """
    Response model for admin statistics.
    """
    total_users: int
    total_roles: int
    total_groups: int
    users_by_role: Dict[str, int]
    users_by_group: Dict[str, int]

# Role Models
class CreateRoleRequest(BaseModel):
    """
    Request model for creating a new role.
    """
    role_name: str = Field(..., description="Unique role name")
    description: str | None = Field(None, description="Role description")

class UpdateRoleRequest(BaseModel):
    """
    Request model for updating a role.
    """
    role_name: str | None = Field(None, description="Role name")
    description: str | None = Field(None, description="Role description")

class RoleResponse(BaseModel):
    """
    Response model for role information.
    """
    id: int
    role_name: str
    description: str | None
    created_at: str
    user_count: int = 0

# Group Models
class CreateGroupRequest(BaseModel):
    """
    Request model for creating a new group.
    """
    group_name: str = Field(..., description="Unique group name")
    description: str | None = Field(None, description="Group description")

class UpdateGroupRequest(BaseModel):
    """
    Request model for updating a group.
    """
    group_name: str | None = Field(None, description="Group name")
    description: str | None = Field(None, description="Group description")

class GroupResponse(BaseModel):
    """
    Response model for group information.
    """
    id: int
    group_name: str
    description: str | None
    created_at: str
    user_count: int = 0

# Profile Models
class PasswordChangeRequest(BaseModel):
    """
    Request model for changing user password.
    """
    current_password: str = Field(..., description="Current password for verification")
    new_password: str = Field(..., description="New password")

class UserModel(BaseModel):
    """
    Pydantic model reflecting the users table (excluding password and salt).
    """
    username: str
    first_name: str
    last_name: str
    email: str | None
    created_at: str
    updated_at: str | None = None
    roles: List[str] = Field(default_factory=list, description="User roles")
    groups: List[str] = Field(default_factory=list, description="User groups")

# System Settings Models
class SystemSettingResponse(BaseModel):
    """
    Response model for system setting information.
    """
    setting_key: str
    setting_value: str
    setting_type: str
    description: str | None
    is_sensitive: bool
    created_at: str
    updated_at: str
    category_name: str | None
    category_display_name: str | None
    category_description: str | None
    sort_order: int | None

class UpdateSystemSettingRequest(BaseModel):
    """
    Request model for updating a system setting.
    """
    setting_value: str = Field(..., description="New setting value")
    remove_previous: bool = Field(False, description="Remove previous model from disk (ollama_model only)")

class SystemSettingCategoryResponse(BaseModel):
    """
    Response model for system setting category information.
    """
    id: int
    category_name: str
    display_name: str
    description: str | None
    sort_order: int
    created_at: str

class CreateSystemSettingCategoryRequest(BaseModel):
    """
    Request model for creating a new system setting category.
    """
    category_name: str = Field(..., description="Unique category name")
    display_name: str = Field(..., description="Human-readable display name")
    description: str | None = Field(None, description="Category description")
    sort_order: int = Field(0, description="Sort order for display")

class UpdateSystemSettingCategoryRequest(BaseModel):
    """
    Request model for updating a system setting category.
    """
    display_name: str | None = Field(None, description="Human-readable display name")
    description: str | None = Field(None, description="Category description")
    sort_order: int | None = Field(None, description="Sort order for display") 