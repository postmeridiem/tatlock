from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from stem.security import get_current_user
from stem.models import UserModel
from hippocampus import recall, forget
import os
from fastapi.responses import FileResponse

# Central router for all hippocampus-related endpoints
router = APIRouter(
    prefix="/hippocampus",
    tags=["hippocampus"],
    dependencies=[Depends(get_current_user)]
)

# --- Long-Term Memory Management ---

@router.get("/longterm/conversations", response_model=List[dict])
async def get_user_conversations(
    search: Optional[str] = Query(None, description="Search term to filter conversations by title."),
    user: UserModel = Depends(get_current_user)
):
    """Get all conversations for the current user, with optional search."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    conversations = recall.search_conversations(user, search) if search else recall.get_user_conversations(user)
    
    return [
        {
            "id": c['conversation_id'],
            "start_time": c['started_at'],
            "last_activity": c['last_activity'],
            "title": c.get('title', 'Untitled Conversation'),
            "message_count": c.get('message_count', 0)
        }
        for c in conversations
    ]

@router.get("/longterm/conversation/{conversation_id}/messages", response_model=List[dict])
async def get_conversation_messages_endpoint(
    conversation_id: str,
    user: UserModel = Depends(get_current_user)
):
    """Get all messages for a specific conversation."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_convos = recall.get_user_conversations(user)
    if not any(c['conversation_id'] == conversation_id for c in user_convos):
        raise HTTPException(status_code=403, detail="You do not have permission to view this conversation.")

    messages = recall.get_conversation_messages(user, conversation_id)
    return [
        {
            "id": m['id'],
            "role": m['role'],
            "content": m['content'],
            "timestamp": m['timestamp']
        }
        for m in messages
    ]

@router.delete("/longterm/conversation/{conversation_id}", status_code=204)
async def delete_user_conversation(
    conversation_id: str,
    user: UserModel = Depends(get_current_user)
):
    """Delete a specific conversation and all its associated memories."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        forget.delete_conversation(user, conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {}

@router.delete("/longterm/conversations/forgetall", status_code=204)
async def purge_all_user_memories(
    user: UserModel = Depends(get_current_user)
):
    """Purge all memories, topics, and conversations for the current user."""
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        forget.purge_all_memories(user)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {}

# --- Short-Term Memory / File Management ---

@router.get("/shortterm/files/get")
async def get_user_file(
    username: str, 
    session_id: str, 
    user: UserModel = Depends(get_current_user)
):
    """
    Get a specific file for a user from their session directory.
    Note: In a real-world scenario, you'd want more robust security here
    to ensure users can only access their own files.
    """
    if user.username != username:
        raise HTTPException(status_code=403, detail="You can only access your own files.")

    # Construct file path
    base_dir = "hippocampus/shortterm/sessions"
    file_path = os.path.join(base_dir, username, session_id)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_path) 