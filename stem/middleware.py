"""
stem/middleware.py

FastAPI middleware components for request logging, timing, monitoring, and error handling.
Following official FastAPI/Starlette patterns for production-ready middleware.
Excludes security middleware which is handled in stem/security.py
"""

import time
import logging
from fastapi import Request, HTTPException, WebSocket
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import uuid

# Set up logging for this module
logger = logging.getLogger(__name__)


async def request_timing_middleware(request: Request, call_next: Callable) -> None:
    """
    Official FastAPI HTTP middleware for request timing and logging.

    Features:
    - Human-readable request/response logging with emojis
    - Precise timing using time.perf_counter()
    - Adds X-Process-Time header for debugging
    - Status code-based emoji indicators

    Usage:
        @app.middleware("http")
        async def timing(request: Request, call_next):
            return await request_timing_middleware(request, call_next)
    """
    start_time = time.perf_counter()

    # Log request start with method and path
    logger.info(f"[REQUEST] {request.method} {request.url.path} - Request started")

    # Process the request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}"

    # Log completion with status-based emoji
    if 200 <= response.status_code < 400:
        status_emoji = "✅"  # Success
    elif response.status_code < 500:
        status_emoji = "⚠️"   # Client error
    else:
        status_emoji = "❌"  # Server error

    logger.info(f"{status_emoji} {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

    return response


async def request_id_middleware(request: Request, call_next: Callable) -> None:
    """
    Add unique request ID to each request for tracing.
    Follows Starlette's RequestIdMiddleware pattern.

    Usage:
        @app.middleware("http")
        async def req_id(request: Request, call_next):
            return await request_id_middleware(request, call_next)
    """
    import uuid

    # Generate or extract request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])

    # Add to request state for access in endpoints
    request.state.request_id = request_id

    response = await call_next(request)

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id

    return response


async def exception_handling_middleware(request: Request, call_next: Callable):
    """
    Global exception handling middleware for HTTP requests.
    Handles 401 redirects for browser vs API requests.

    Usage:
        @app.middleware("http")
        async def exception_handler(request: Request, call_next):
            return await exception_handling_middleware(request, call_next)
    """
    try:
        response = await call_next(request)
        return response
    except HTTPException as exc:
        if exc.status_code == 401:
            # Check if this is a browser navigation (GET request) or API call
            if request.method == "GET":
                # Browser navigation - redirect to login with original path
                original_path = str(request.url.path)
                if request.url.query:
                    original_path += f"?{request.url.query}"
                login_url = f"/login?redirect={original_path}"
                return RedirectResponse(url=login_url, status_code=302)
            else:
                # API call - return JSON
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": exc.detail}
                )

        # Default behavior for other HTTP errors
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in request: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )


async def websocket_auth_middleware(websocket: WebSocket, auth_function: Callable):
    """
    WebSocket authentication middleware.
    Handles session-based authentication for WebSocket connections.

    Args:
        websocket: WebSocket connection
        auth_function: Function to validate user (e.g., get_current_user)

    Returns:
        UserModel if authenticated, None if failed (connection will be closed)
    """
    try:
        await websocket.accept()

        # Use session cookie for authentication
        session_cookie = websocket.cookies.get("session")
        if not session_cookie:
            await websocket.close(code=4401)
            return None

        # Create a mock request object for authentication
        from starlette.requests import Request
        request = Request({
            'type': 'websocket',
            'headers': websocket.headers.raw,
            'cookies': websocket.cookies
        })

        try:
            user = auth_function(request)
            return user
        except Exception:
            await websocket.close(code=4401)
            return None

    except Exception as e:
        logger.error(f"WebSocket authentication error: {e}")
        await websocket.close(code=1011)
        return None


def setup_logging_config():
    """
    Configure application-wide logging with human-readable timestamps.
    Call this early in main.py before other components.
    """
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:\t  %(name)s - %(message)s %(asctime)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),  # Console handler
        ]
    )

    logger.info("Application logging configured with human-readable timestamps")


def setup_middleware(app):
    """
    Setup all non-security middleware for the FastAPI application.
    Call this from main.py after app creation.
    Security middleware is configured in stem/security.py

    Args:
        app: FastAPI application instance
    """
    # Add exception handling middleware (outermost - catches all errors)
    @app.middleware("http")
    async def exception_middleware(request: Request, call_next):
        return await exception_handling_middleware(request, call_next)

    # Add request timing middleware (runs after exception handling)
    @app.middleware("http")
    async def timing_middleware(request: Request, call_next):
        return await request_timing_middleware(request, call_next)

    # Add request ID middleware (innermost - runs closest to endpoints)
    @app.middleware("http")
    async def id_middleware(request: Request, call_next):
        return await request_id_middleware(request, call_next)

    logger.info("Request timing, ID, and exception handling middleware configured")