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
- Jinja2 templating for server-side rendering
"""

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, Request, Form, status, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
import uvicorn
from cortex.tatlock import process_chat_interaction
from stem.static import mount_static_files, get_conversation_page, get_profile_page, get_login_page
from stem.security import get_current_user, require_admin_role, security_manager, login_user, logout_user, current_user, setup_security_middleware
from stem.middleware import setup_middleware, setup_logging_config, websocket_auth_middleware
from stem.models import (
    ChatRequest, ChatResponse, UserModel
)
from stem.admin import admin_router
from stem.profile import profile_router
from hippocampus.hippocampus import router as hippocampus_router
from parietal.parietal import router as parietal_router
from fastapi.openapi.utils import get_openapi
from config import (
    OLLAMA_MODEL, PORT, HOSTNAME, APP_VERSION, SYSTEM_DB_PATH
)
from temporal.voice_service import VoiceService
from contextlib import asynccontextmanager
from stem.installation.database_setup import check_and_run_migrations
from stem.installation.migration_runner import migrate_if_needed
import base64
from hippocampus.user_database import get_user_image_path
from fastapi.logger import logger
from stem.api_metadata import tags_metadata
from stem.system_settings import system_settings_manager

# Load environment variables from .env file
load_dotenv()

# Configure application logging
setup_logging_config()

# Set up logger for this module
logger = logging.getLogger(__name__)

# Initialize voice service
voice_service = VoiceService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application startup and shutdown.
    Runs system database migrations and initializes services on startup.
    """
    # Startup
    logger.info("Wake up (wake up)")
    logger.info("Grab a brush and put a little make-up")
    logger.info(f"Tatlock starting up with LLM model: {OLLAMA_MODEL}")

    logger.info("Starting Tatlock application...")

    # Run version-based database migrations (new system)
    try:
        logger.info("Checking database schema version...")
        migrate_if_needed()
        logger.info("Database schema version check completed")
    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}", exc_info=True)
        raise  # Critical - can't start without proper database schema

    # Run legacy system database migrations (to be phased out)
    try:
        logger.info("Checking and running legacy system database migrations...")
        check_and_run_migrations(SYSTEM_DB_PATH)
        logger.info("Legacy system database migrations completed")
    except Exception as e:
        logger.error(f"Failed to run legacy system database migrations: {e}", exc_info=True)
        raise  # Critical - can't start without system database

    # Initialize voice service
    try:
        logger.info("Initializing voice service...")
        await voice_service.initialize()
        logger.info("Voice service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize voice service: {e}", exc_info=True)
        # Continue startup even if voice service fails

    yield

    # Shutdown
    logger.info("Shutting down Tatlock application...")
    # Add any cleanup logic here if needed

# --- FastAPI App ---
app = FastAPI(
    title="Tatlock",
    description="As a child I used to play board games against a bucket with a face painted on it.",
    version=APP_VERSION,
    redoc_url=None,  # Disable ReDoc for security
    lifespan=lifespan
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
        tags=tags_metadata,
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

# Setup all middleware (order matters - outermost first)
setup_security_middleware(app)  # Security middleware (outermost)
setup_middleware(app)           # Request timing, ID, exception handling

# Mount static files directory (HTML, CSS, JS, Material Icons)
mount_static_files(app)

# Include admin router for user, role, and group management
app.include_router(admin_router)

# Include profile router for user profile management
app.include_router(profile_router)

# Include longterm management router for conversation history
app.include_router(hippocampus_router)

# Include parietal router for hardware monitoring and benchmarking
app.include_router(parietal_router)

@app.get("/", tags=["root"])
async def read_root(request: Request):
    """
    Root endpoint that redirects to the appropriate page based on authentication status.
    Redirects to /conversation if authenticated, /login if not.
    """
    try:
        # Try to get current user to check if authenticated
        current_user = get_current_user(request)
        # If we get here, user is authenticated
        return RedirectResponse(url="/conversation", status_code=302)
    except HTTPException:
        # User is not authenticated, redirect to login with original path
        original_path = str(request.url.path)
        if request.url.query:
            original_path += f"?{request.url.query}"
        login_url = f"/login?redirect={original_path}"
        return RedirectResponse(url=login_url, status_code=302)

# --- API Endpoint Definition ---
@app.post("/cortex", tags=["api"], response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, user: UserModel = Depends(get_current_user)):
    """
    Main chat endpoint for the AI. Processes user messages and returns AI responses.
    Requires authentication. Request timing is handled by middleware.
    """
    try:
        if not user:
            raise HTTPException(status_code=401, detail="User not authenticated")

        # Pydantic models in a list are not automatically converted to dicts,
        # so we do it manually before passing to the agent.
        history_dicts = [msg.model_dump(exclude_none=True) for msg in request.history]

        # Process the chat interaction
        result_dict = process_chat_interaction(
            user_message=request.message,
            history=history_dicts,
            username=user.username,
            conversation_id=request.conversation_id
        )

        if result_dict is None:
            raise HTTPException(status_code=500, detail="Agent processing returned an unexpected null result.")

        return ChatResponse(**result_dict)
        
    except Exception as e:
        logger.error(f"An error occurred in the endpoint: {e}", exc_info=True)
        # Re-raise as HTTPException to be caught by the handler
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation", tags=["html"],  response_class=HTMLResponse)
async def conversation_page(request: Request, user: UserModel = Depends(get_current_user)):
    """
    Conversation page.
    Requires authentication via session-based authentication.
    """
    if user is None:
        original_path = str(request.url.path)
        if request.url.query:
            original_path += f"?{request.url.query}"
        login_url = f"/login?redirect={original_path}"
        return RedirectResponse(url=login_url, status_code=302)
    return get_conversation_page(request, user)

@app.get("/profile", tags=["html"])
async def profile_page(request: Request, user: UserModel = Depends(get_current_user)):
    """
    User profile page.
    Requires authentication via session-based authentication.
    """
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return get_profile_page(request, user)

@app.get("/login", tags=["html"], response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Login page.
    No authentication required.
    """
    return get_login_page(request)

@app.get("/logout", tags=["html"], response_class=HTMLResponse)
async def logout_page(request: Request):
    """
    Logout page. Logs the user out and redirects to root.
    """
    # Actually log the user out
    logout_user(request)
    
    # Redirect to root (which will redirect to login since user is now logged out)
    return RedirectResponse(url="/", status_code=302)

@app.get("/login/test", tags=["debug"])
async def test_auth(_: None = Depends(get_current_user)):
    """
    Simple test endpoint to verify authentication is working.
    """
    user = current_user
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"message": "Authentication working", "user": user.model_dump()}

@app.post("/login/auth", tags=["api"])
async def login(request: Request):
    """
    Session-based login endpoint. Accepts JSON or form data.
    Sets session on success.
    """
    data = await request.json() if request.headers.get("content-type", "").startswith("application/json") else await request.form()
    username = str(data.get("username", ""))
    password = str(data.get("password", ""))
    logger.debug(f"/login/auth called with username='{username}' and password length={len(password)}")
    if not username or not password:
        logger.warning("/login/auth missing username or password")
        return HTMLResponse(content="Missing username or password", status_code=status.HTTP_400_BAD_REQUEST)
    result = login_user(request, username, password)
    logger.debug(f"/login/auth authentication result for '{username}': {result}")
    if result["success"]:
        return {"success": True}
    else:
        return HTMLResponse(content=result["message"], status_code=status.HTTP_401_UNAUTHORIZED)

# Serve favicon.ico from the new location
@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse("stem/static/favicon/favicon.ico")

@app.get("/.well-known/appspecific/com.chrome.devtools.json", include_in_schema=False)
async def chrome_devtools_config():
    """
    Endpoint to handle Chrome DevTools-specific requests and prevent 404s in logs.
    """
    return JSONResponse(content={})

@app.websocket("/ws/voice")
async def websocket_voice_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice/audio streaming.
    Only allows authenticated users.
    Receives audio chunks, transcribes, processes, and returns results.
    """
    # Authenticate user using middleware
    user = await websocket_auth_middleware(websocket, get_current_user)
    if not user:
        return

    try:
        # Now handle audio streaming
        await voice_service.handle_websocket_connection(websocket, path="/ws/voice")
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011)

# Exception handling is now managed by middleware in stem/middleware.py

# This allows running the app directly with `python main.py`
if __name__ == "__main__":
    uvicorn.run(app, host=HOSTNAME, port=PORT)