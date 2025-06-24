"""
stem/static.py

Static file serving and HTML page generation for Tatlock.
Now uses Jinja2 templating for server-side rendering.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from .htmlcontroller import render_template, render_page, get_common_context
from .models import UserModel
import logging

logger = logging.getLogger(__name__)

def mount_static_files(app: FastAPI):
    """
    Mount static files directory to the FastAPI app.
    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.mount("/static", StaticFiles(directory="stem/static"), name="static")

def get_login_page(request: Request) -> HTMLResponse:
    """Get the login HTML page using Jinja2 templating."""
    context = get_common_context(request)
    return render_page("page.login.html", context)

def get_conversation_page(request: Request, user: UserModel) -> HTMLResponse:
    """Get the conversation interface HTML page using Jinja2 templating."""
    context = get_common_context(request, user)
    return render_page("page.conversation.html", context)

def get_profile_page(request: Request, user: UserModel) -> HTMLResponse:
    """Get the user profile HTML page using Jinja2 templating."""
    context = get_common_context(request, user)
    return render_page("page.profile.html", context)

def get_admin_page(request: Request, user: UserModel) -> HTMLResponse:
    """Get the admin dashboard HTML page using Jinja2 templating."""
    context = get_common_context(request, user)
    return render_page("page.admin.html", context)

# Legacy functions for backward compatibility (deprecated)
def get_profile_page_with_chat_sidebar(request: Request, user: UserModel) -> HTMLResponse:
    """Get the user profile HTML page with chat sidebar included (deprecated)."""
    logger.warning("get_profile_page_with_chat_sidebar is deprecated, use get_profile_page instead")
    return get_profile_page(request, user)

def get_admin_page_with_chat_sidebar(request: Request, user: UserModel) -> HTMLResponse:
    """Get the admin dashboard HTML page with chat sidebar included (deprecated)."""
    logger.warning("get_admin_page_with_chat_sidebar is deprecated, use get_admin_page instead")
    return get_admin_page(request, user)

def get_chat_sidebar() -> str:
    """Get the chat sidebar include content (deprecated)."""
    logger.warning("get_chat_sidebar is deprecated, use Jinja2 templates instead")
    return "<!-- Chat sidebar now handled by Jinja2 templates -->" 