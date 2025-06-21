"""
main.py

Entry point for the Tatlock conversational AI API using FastAPI.
Defines the API contract and HTTP endpoints with comprehensive authentication,
user management, admin dashboard, and web interface.

Features:
- FastAPI-based HTTP interface with authentication
- Admin dashboard for user, role, and group management
- User profile management and password changes
- Debug console with JSON logging
- Material Design web interface with dark/light mode
- ReDoc documentation disabled for security
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from cortex.agent import process_chat_interaction
from stem.static import mount_static_files, get_chat_page, get_admin_page, get_profile_page, get_docs_page
from stem.security import get_current_user, require_admin_role, security_manager
from stem.models import (
    ChatRequest, ChatResponse
)
from stem.admin import admin_router
from stem.profile import profile_router

# --- FastAPI App ---
app = FastAPI(
    title="Tatlock",
    description="As a child I used to play board games against a bucket with a face painted on it.",
    version="3.0.0",
    redoc_url=None,  # Disable ReDoc for security
)

# Mount static files directory (HTML, CSS, JS, Material Icons)
mount_static_files(app)

# Include admin router for user, role, and group management
app.include_router(admin_router)

# Include profile router for user profile management
app.include_router(profile_router)

# --- API Endpoint Definition ---
@app.post("/cortex", tags=["api"], response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    HTTP entrypoint for chat interactions.
    Validates the request and calls the backend agent logic.
    Requires authentication via HTTP Basic Auth.
    Returns AI response with topic classification and updated history.
    """
    try:
        history_dicts = [msg.model_dump(exclude_none=True) for msg in request.history]

        result_dict = process_chat_interaction(
            user_message=request.message,
            history=history_dicts,
            username=current_user['username'],
            conversation_id=request.conversation_id
        )
        if result_dict is None:
             raise HTTPException(status_code=500, detail="Agent processing returned an unexpected null result.")

        return ChatResponse(**result_dict)

    except Exception as e:
        print(f"An error occurred in the endpoint: {e}")
        # In a real app, you would log the full exception traceback here
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

@app.get("/", tags=["root"])
async def read_root():
    """
    Root endpoint that redirects to the chat interface.
    No authentication required for redirect.
    """
    return RedirectResponse(url="/chat", status_code=302)

@app.get("/chat", tags=["html"],  response_class=HTMLResponse)
async def chat_page(current_user: dict = Depends(get_current_user)):
    """
    Debug console interface page.
    Requires authentication via HTTP Basic Auth.
    Provides real-time JSON logging of server interactions.
    """
    return get_chat_page()

@app.get("/admin/dashboard", tags=["html"], response_class=HTMLResponse)
async def admin_page(current_user: dict = Depends(require_admin_role)):
    """
    Admin dashboard page.
    Requires admin role via HTTP Basic Auth.
    Provides user, role, and group management interface.
    """
    return get_admin_page()

@app.get("/profile")
async def profile_page(current_user: dict = Depends(get_current_user)):
    """
    User profile management page.
    Requires authentication via HTTP Basic Auth.
    Allows users to view and edit their profile information.
    """
    return HTMLResponse(content=get_profile_page())

@app.get("/docs")
async def docs_page(current_user: dict = Depends(get_current_user)):
    """
    API documentation page.
    Requires authentication via HTTP Basic Auth.
    Provides Swagger UI for API exploration.
    """
    return HTMLResponse(content=get_docs_page())

# This allows running the app directly with `python main.py`
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)