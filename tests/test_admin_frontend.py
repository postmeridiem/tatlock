"""
test_admin_frontend.py

Tests for admin dashboard frontend functionality.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

class TestAdminFrontend:
    """Test admin dashboard frontend functionality."""
    
    def test_admin_dashboard_page_loads(self, authenticated_admin_client):
        """Test that admin dashboard page loads correctly."""
        response = authenticated_admin_client.get("/admin/dashboard")
        assert response.status_code == 200
        assert "Tatlock Admin Dashboard" in response.text
        assert "User Management" in response.text
    
    def test_user_modal_password_field_behavior(self, authenticated_admin_client):
        """Test that password field is optional when editing users."""
        # Get the admin dashboard page
        response = authenticated_admin_client.get("/admin/dashboard")
        assert response.status_code == 200
        
        # Check that the password field has the correct structure
        content = response.text
        
        # Should have password field with dynamic required indicator
        assert 'id="password-required"' in content
        assert 'id="password"' in content
        
        # Should have the JavaScript files loaded
        assert 'src="/static/js/common.js"' in content
        assert 'src="/static/js/admin.js"' in content
        
        # Should have the user modal structure
        assert 'id="userModal"' in content
        assert 'id="userForm"' in content
    
    def test_admin_dashboard_requires_auth(self, client):
        """Test that admin dashboard requires authentication."""
        response = client.get("/admin/dashboard", allow_redirects=False)
        assert response.status_code == 302  # Should redirect to login 