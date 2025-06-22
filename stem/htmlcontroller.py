"""
stem/htmlcontroller.py

Jinja2 template management for Tatlock HTML pages.
Provides server-side templating with shared components and layouts.
"""

import os
from typing import Dict, Any, Optional
from fastapi import Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, Template
import logging

logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages Jinja2 templates for Tatlock HTML pages."""
    
    def __init__(self):
        """Initialize the template manager with Jinja2 environment."""
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Register custom filters and functions
        self._register_filters()
        
    def _register_filters(self):
        """Register custom Jinja2 filters."""
        # Add any custom filters here if needed
        pass
    
    def render_template(self, template_name: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name (str): Name of the template file
            context (Optional[Dict[str, Any]]): Template context variables
            
        Returns:
            str: Rendered HTML content
        """
        try:
            template = self.env.get_template(template_name)
            context = context or {}
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}")
            return f"<h1>Error rendering template: {str(e)}</h1>"
    
    def render_page(self, template_name: str, context: Optional[Dict[str, Any]] = None) -> HTMLResponse:
        """
        Render a template and return as HTMLResponse.
        
        Args:
            template_name (str): Name of the template file
            context (Optional[Dict[str, Any]]): Template context variables
            
        Returns:
            HTMLResponse: Rendered HTML page
        """
        content = self.render_template(template_name, context)
        return HTMLResponse(content=content)
    
    def get_common_context(self, request: Request, user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get common context variables for all templates.
        
        Args:
            request (Request): FastAPI request object
            user (Optional[Dict[str, Any]]): Current user data
            
        Returns:
            Dict[str, Any]: Common template context
        """
        return {
            'user': user,
            'request': request,
            'app_name': 'Tatlock',
            'app_version': '3.0.0',
            'is_authenticated': user is not None,
            'is_admin': user and 'admin' in user.get('roles', []) if user else False
        }

# Global template manager instance
template_manager = TemplateManager()

# Convenience functions for backward compatibility
def render_template(template_name: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Render a template with the given context."""
    return template_manager.render_template(template_name, context)

def render_page(template_name: str, context: Optional[Dict[str, Any]] = None) -> HTMLResponse:
    """Render a template and return as HTMLResponse."""
    return template_manager.render_page(template_name, context)

def get_common_context(request: Request, user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get common context variables for all templates."""
    return template_manager.get_common_context(request, user) 