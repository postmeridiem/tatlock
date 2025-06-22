"""
stem/static.py

Static file serving and HTML page generation for Tatlock.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os

def mount_static_files(app: FastAPI):
    """
    Mount static files directory to the FastAPI app.
    Args:
        app (FastAPI): The FastAPI application instance.
    """
    app.mount("/static", StaticFiles(directory="stem/static"), name="static")

def get_login_page() -> str:
    """Get the login HTML page."""
    with open("stem/static/login.html", "r") as f:
        return f.read()

def get_chat_page() -> str:
    """Get the chat interface HTML page."""
    with open("stem/static/chat.html", "r") as f:
        return f.read()

def get_profile_page() -> str:
    """Get the user profile HTML page."""
    with open("stem/static/profile.html", "r") as f:
        return f.read()

def get_admin_page() -> HTMLResponse:
    """
    Generate and return the admin dashboard HTML page.
    Returns:
        HTMLResponse: The admin dashboard page.
    """
    html_file_path = os.path.join("stem", "static", "admin.html")
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: admin.html not found</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading admin dashboard: {str(e)}</h1>", status_code=500) 