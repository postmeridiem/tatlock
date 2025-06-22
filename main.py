"""
main.py

Entry point for the Tatlock conversational AI API using FastAPI.
Defines the API contract and HTTP endpoints with comprehensive session-based authentication,
user management, admin dashboard, and web interface.

Features:
- FastAPI-based HTTP interface with session-based authentication
- Admin dashboard for user, role, and group management (moved to stem/admin.py)
- User profile management and password changes
- Debug console with JSON logging
- Material Design web interface with dark/light mode
- ReDoc documentation disabled for security
- Session-based login/logout with proper redirects
- Conversation tracking and user data isolation
- Structured logging for tool execution and debugging
"""

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
import uvicorn
from cortex.agent import process_chat_interaction
from stem.static import mount_static_files, get_chat_page, get_profile_page, get_login_page
from stem.security import get_current_user, require_admin_role, security_manager, login_user, logout_user
from stem.models import (
    ChatRequest, ChatResponse
)
from stem.admin import admin_router
from stem.profile import profile_router
from fastapi.security import HTTPBasicCredentials
from fastapi.security import HTTPBasic
from starlette.middleware.sessions import SessionMiddleware
from fastapi.openapi.utils import get_openapi
from config import (
    OPENWEATHER_API_KEY, GOOGLE_API_KEY, GOOGLE_CSE_ID, 
    OLLAMA_MODEL, SYSTEM_DB_PATH, PORT
)
from parietal.hardware import get_comprehensive_system_info

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console handler
    ]
)

# Get secret key from environment variable with fallback
SECRET_KEY = os.getenv("STARLETTE_SECRET", "this-is-not-a-secret-key")

# --- FastAPI App ---
app = FastAPI(
    title="Tatlock",
    description="As a child I used to play board games against a bucket with a face painted on it.",
    version="3.0.0",
    redoc_url=None,  # Disable ReDoc for security
)

# Configure security schemes for OpenAPI documentation
app.openapi_schema = None  # Force regeneration

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "sessionAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "session",
            "description": "Session-based authentication using cookies"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"sessionAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add session middleware for session-based authentication
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Mount static files directory (HTML, CSS, JS, Material Icons)
mount_static_files(app)

# Include admin router for user, role, and group management
app.include_router(admin_router)

# Include profile router for user profile management
app.include_router(profile_router)

# Serve favicon.ico from the new location
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("stem/static/favicon/favicon.ico")

@app.post("/login/auth")
async def login(request: Request):
    """
    Session-based login endpoint. Accepts JSON or form data.
    Sets session on success.
    """
    data = await request.json() if request.headers.get("content-type", "").startswith("application/json") else await request.form()
    username = str(data.get("username", ""))
    password = str(data.get("password", ""))
    if not username or not password:
        return HTMLResponse(content="Missing username or password", status_code=status.HTTP_400_BAD_REQUEST)
    
    result = login_user(request, username, password)
    if result["success"]:
        return {"success": True}
    else:
        return HTMLResponse(content=result["message"], status_code=status.HTTP_401_UNAUTHORIZED)

@app.post("/logout")
async def logout(request: Request):
    """
    Session-based logout endpoint. Clears the session.
    """
    result = logout_user(request)
    return {"success": True}

@app.get("/login", tags=["html"], response_class=HTMLResponse)
async def login_page():
    """
    Login page.
    No authentication required.
    """
    return HTMLResponse(content=get_login_page())

@app.get("/login/test", tags=["debug"])
async def test_auth(current_user: dict = Depends(get_current_user)):
    """
    Simple test endpoint to verify authentication is working.
    """
    return {"message": "Authentication working", "user": current_user}

@app.get("/logout", tags=["html"], response_class=HTMLResponse)
async def logout_page(request: Request):
    """
    Logout page. Logs the user out and redirects to root.
    """
    # Actually log the user out
    logout_user(request)
    
    # Redirect to root (which will redirect to login since user is now logged out)
    return RedirectResponse(url="/", status_code=302)

# --- Exception Handlers ---
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions, redirecting 401 errors to login page.
    """
    if exc.status_code == 401:
        # Redirect to login page with current URL as redirect parameter
        current_url = str(request.url)
        login_url = f"/login?redirect={current_url}"
        return RedirectResponse(url=login_url, status_code=302)
    
    # For other HTTP exceptions, return the default response
    return HTMLResponse(
        content=f"<h1>Error {exc.status_code}</h1><p>{exc.detail}</p>",
        status_code=exc.status_code
    )

# --- API Endpoint Definition ---
@app.post("/cortex", tags=["api"], response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    HTTP entrypoint for chat interactions.
    Validates the request and calls the backend agent logic.
    Requires authentication via session-based authentication.
    Returns AI response with topic classification and updated history.
    """
    logger = logging.getLogger(__name__)
    
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
        logger.error(f"An error occurred in the endpoint: {e}", exc_info=True)
        # In a real app, you would log the full exception traceback here
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

@app.get("/", tags=["root"])
async def read_root(request: Request):
    """
    Root endpoint that redirects to the appropriate page based on authentication status.
    Redirects to /chat if authenticated, /login if not.
    """
    try:
        # Try to get current user to check if authenticated
        current_user = get_current_user(request)
        # If we get here, user is authenticated
        return RedirectResponse(url="/chat", status_code=302)
    except HTTPException:
        # User is not authenticated, redirect to login
        return RedirectResponse(url="/login", status_code=302)

@app.get("/chat", tags=["html"],  response_class=HTMLResponse)
async def chat_page(current_user: dict = Depends(get_current_user)):
    """
    Debug console interface page.
    Requires authentication via session-based authentication.
    Provides real-time JSON logging of server interactions.
    """
    return get_chat_page()

@app.get("/profile")
async def profile_page(current_user: dict = Depends(get_current_user)):
    """
    User profile management page.
    Requires authentication via session-based authentication.
    Allows users to view and edit their profile information.
    """
    return HTMLResponse(content=get_profile_page())

@app.get("/parietal/system-info", tags=["api"])
async def system_info_api(current_user: dict = Depends(get_current_user)):
    """
    Returns comprehensive system and hardware information for the debug console.
    Requires authentication.
    """
    return get_comprehensive_system_info()

# This allows running the app directly with `python main.py`
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)