"""
Tests for main.py application module.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app


class TestRootEndpoint:
    """Test root endpoint functionality."""
    
    def test_root_redirects_to_chat_when_authenticated(self, authenticated_admin_client):
        """Test root endpoint redirects to chat when authenticated."""
        response = authenticated_admin_client.get("/", follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "/chat"
    
    def test_root_redirects_to_login_when_not_authenticated(self, client):
        """Test root endpoint redirects to login when not authenticated."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 302
        assert "/login?redirect=" in response.headers["location"]


class TestLoginEndpoints:
    """Test login-related endpoints."""
    
    def test_login_page_accessible(self, client):
        """Test login page is accessible without authentication."""
        response = client.get("/login")
        
        assert response.status_code == 200
        assert "login" in response.text.lower()
    
    def test_login_auth_success(self, client, admin_user):
        """Test successful login authentication."""
        response = client.post("/login/auth", json={
            "username": admin_user["username"],
            "password": admin_user["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_login_auth_failure(self, client):
        """Test failed login authentication."""
        response = client.post("/login/auth", json={
            "username": "nonexistent",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    def test_login_auth_missing_credentials(self, client):
        """Test login with missing credentials."""
        response = client.post("/login/auth", json={})
        
        assert response.status_code == 400
    
    def test_login_auth_form_data(self, client, admin_user):
        """Test login with form data instead of JSON."""
        response = client.post("/login/auth", data={
            "username": admin_user["username"],
            "password": admin_user["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_logout_success(self, authenticated_admin_client):
        """Test successful logout."""
        response = authenticated_admin_client.post("/logout", follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "/"
    
    def test_logout_clears_session(self, authenticated_admin_client):
        """Test that logout actually clears the session."""
        # First verify we're authenticated
        response = authenticated_admin_client.get("/chat")
        assert response.status_code == 200
        
        # Now logout
        logout_response = authenticated_admin_client.post("/logout", follow_redirects=False)
        assert logout_response.status_code == 302
        
        # Try to access a protected endpoint - should redirect to login (302) due to custom exception handler
        response = authenticated_admin_client.get("/chat", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_logout_page_redirects(self, authenticated_admin_client):
        """Test logout page redirects to root."""
        response = authenticated_admin_client.get("/logout", follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "/"


class TestChatEndpoint:
    """Test chat endpoint functionality."""
    
    def test_chat_endpoint_requires_auth(self, client):
        """Test chat endpoint requires authentication."""
        response = client.post("/cortex", json={
            "message": "Hello",
            "history": []
        }, follow_redirects=False)
        
        assert response.status_code == 401
    
    def test_chat_endpoint_with_auth(self, authenticated_admin_client):
        """Test chat endpoint with authentication."""
        with patch('cortex.agent.process_chat_interaction') as mock_process:
            mock_process.return_value = {
                "response": "Hello! How can I help you?",
                "topic": "greeting",
                "history": [{"role": "user", "content": "Hello"}],
                "conversation_id": "test-conv-123"
            }
            
            response = authenticated_admin_client.post("/cortex", json={
                "message": "Hello",
                "history": []
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "topic" in data
            assert "history" in data
            assert "conversation_id" in data
    
    def test_chat_endpoint_with_history(self, authenticated_admin_client):
        """Test chat endpoint with conversation history."""
        with patch('cortex.agent.process_chat_interaction') as mock_process:
            mock_process.return_value = {
                "response": "I remember our previous conversation.",
                "topic": "memory",
                "history": [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi there!"},
                    {"role": "user", "content": "Do you remember?"},
                    {"role": "assistant", "content": "I remember our previous conversation."}
                ],
                "conversation_id": "test-conv-123"
            }
            
            history = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
            
            response = authenticated_admin_client.post("/cortex", json={
                "message": "Do you remember?",
                "history": history
            })
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["history"]) == 4  # Updated to match actual response
    
    def test_chat_endpoint_with_conversation_id(self, authenticated_admin_client):
        """Test chat endpoint with conversation ID."""
        with patch('cortex.agent.process_chat_interaction') as mock_process:
            mock_process.return_value = {
                "response": "Continuing conversation.",
                "topic": "continuation",
                "history": [{"role": "user", "content": "Continue"}],
                "conversation_id": "existing-conv-456"
            }
            
            response = authenticated_admin_client.post("/cortex", json={
                "message": "Continue",
                "history": [],
                "conversation_id": "existing-conv-456"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["conversation_id"] == "existing-conv-456"
    
    def test_chat_endpoint_null_result(self, authenticated_admin_client):
        """Test chat endpoint when agent returns null."""
        with patch('main.process_chat_interaction') as mock_process:
            mock_process.return_value = None
            
            response = authenticated_admin_client.post("/cortex", json={
                "message": "Hello",
                "history": []
            })
            
            assert response.status_code == 500
            assert "null result" in response.text
    
    def test_chat_endpoint_agent_exception(self, authenticated_admin_client):
        """Test chat endpoint when agent raises exception."""
        with patch('main.process_chat_interaction') as mock_process:
            mock_process.side_effect = Exception("Agent error")
            
            response = authenticated_admin_client.post("/cortex", json={
                "message": "Hello",
                "history": []
            })
            
            assert response.status_code == 500
            assert "Agent error" in response.text


class TestChatPage:
    """Test chat page endpoint."""
    
    def test_chat_page_requires_auth(self, client):
        """Test chat page requires authentication."""
        response = client.get("/chat", follow_redirects=False)
        
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_chat_page_with_auth(self, authenticated_admin_client):
        """Test chat page with authentication."""
        response = authenticated_admin_client.get("/chat")
        
        assert response.status_code == 200
        assert "chat" in response.text.lower()
    
    def test_chat_page_includes_markdown_support(self, authenticated_admin_client):
        """Test chat page includes markdown library for formatting."""
        response = authenticated_admin_client.get("/chat")
        
        assert response.status_code == 200
        assert "marked.min.js" in response.text
        assert "marked" in response.text
    
    def test_chat_page_includes_logo(self, authenticated_admin_client):
        """Test chat page includes the Tatlock logo."""
        response = authenticated_admin_client.get("/chat")
        
        assert response.status_code == 200
        assert "logo-tatlock-transparent.png" in response.text
        assert "logo-image" in response.text
    
    def test_chat_page_includes_shared_chat_js(self, authenticated_admin_client):
        """Test chat page includes the shared chat.js file."""
        response = authenticated_admin_client.get("/chat")
        
        assert response.status_code == 200
        assert "chat.js" in response.text
    
    def test_chat_page_includes_mobile_responsive_css(self, authenticated_admin_client):
        response = authenticated_admin_client.get("/chat")
        assert response.status_code == 200
        # Check that the CSS file is included
        assert 'style.css' in response.text
        
        # Check the CSS file directly for mobile responsive styles
        css_response = authenticated_admin_client.get("/static/style.css")
        assert css_response.status_code == 200
        css_content = css_response.text
        assert '@media (max-width: 768px)' in css_content
        assert 'display: none !important' in css_content
        assert 'position: fixed' in css_content


class TestFavicon:
    """Test favicon endpoint."""
    
    def test_favicon_accessible(self, client):
        """Test favicon is accessible."""
        response = client.get("/favicon.ico")
        
        assert response.status_code == 200
        assert response.headers["content-type"] in ["image/x-icon", "image/vnd.microsoft.icon"]


class TestExceptionHandling:
    """Test exception handling."""
    
    def test_401_exception_redirects_to_login(self, client):
        """Test 401 exceptions redirect to login page."""
        # Create a test endpoint that raises 401
        @app.get("/test-401")
        def test_401():
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        response = client.get("/test-401", follow_redirects=False)
        
        assert response.status_code == 302
        assert "/login?redirect=" in response.headers["location"]
    
    def test_other_exceptions_not_redirected(self, client):
        """Test other HTTP exceptions are not redirected."""
        # Create a test endpoint that raises 404
        @app.get("/test-404")
        def test_404():
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        
        response = client.get("/test-404")
        
        assert response.status_code == 404
        assert "Not Found" in response.text


class TestOpenAPISchema:
    """Test OpenAPI schema generation."""
    
    def test_openapi_schema_generated(self, client):
        """Test OpenAPI schema is generated."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
    
    def test_openapi_security_schemes(self, client):
        """Test OpenAPI schema includes security schemes."""
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        assert "components" in data
        assert "securitySchemes" in data["components"]
        assert "sessionAuth" in data["components"]["securitySchemes"]
    
    def test_redoc_disabled(self, client):
        """Test ReDoc is disabled for security."""
        response = client.get("/redoc")
        
        assert response.status_code == 404


class TestStaticFiles:
    """Test static file serving."""
    
    def test_static_files_mounted(self, client):
        """Test static files are properly mounted."""
        # Test that static files are accessible
        response = client.get("/static/style.css")
        
        # Should either return the file or redirect to login
        assert response.status_code in [200, 302]
    
    def test_static_files_structure(self, client):
        """Test static files directory structure."""
        # Test various static file paths
        static_paths = [
            "/static/js/common.js",
            "/static/images/logo-tatlock.png",
            "/static/fonts/material-icons.ttf"
        ]
        
        for path in static_paths:
            response = client.get(path)
            # Should either return the file or redirect to login
            assert response.status_code in [200, 302]


class TestMiddleware:
    """Test middleware functionality."""
    
    def test_session_middleware_present(self, client):
        """Test session middleware is configured."""
        # Try to access a protected endpoint
        response = client.get("/chat", follow_redirects=False)
        
        # Should redirect to login (indicating session middleware is working)
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_session_cookies(self, client, admin_user):
        """Test session cookies are set on login."""
        response = client.post("/login/auth", json={
            "username": admin_user["username"],
            "password": admin_user["password"]
        })
        
        assert response.status_code == 200
        
        # Check if session cookie is set
        cookies = response.cookies
        assert "session" in cookies


class TestAdminPage:
    """Test admin page endpoint."""
    
    def test_admin_page_requires_auth(self, client):
        """Test admin page requires authentication."""
        response = client.get("/admin/dashboard", follow_redirects=False)
        
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_admin_page_with_auth(self, authenticated_admin_client):
        """Test admin page with authentication."""
        response = authenticated_admin_client.get("/admin/dashboard")
        
        assert response.status_code == 200
        assert "admin" in response.text.lower()
    
    def test_admin_page_includes_logo(self, authenticated_admin_client):
        """Test admin page includes the Tatlock logo."""
        response = authenticated_admin_client.get("/admin/dashboard")
        
        assert response.status_code == 200
        assert "logo-tatlock-transparent.png" in response.text
        assert "logo-image" in response.text
    
    def test_admin_page_includes_chat_functionality(self, authenticated_admin_client):
        """Test admin page includes chat functionality."""
        response = authenticated_admin_client.get("/admin/dashboard")
        
        assert response.status_code == 200
        assert "chat-sidepane" in response.text
        assert "chat-input" in response.text
        assert "marked.min.js" in response.text
    
    def test_admin_page_includes_shared_chat_js(self, authenticated_admin_client):
        """Test admin page includes the shared chat.js file."""
        response = authenticated_admin_client.get("/admin/dashboard")
        
        assert response.status_code == 200
        assert "chat.js" in response.text


class TestProfilePage:
    """Test profile page endpoint."""
    
    def test_profile_page_requires_auth(self, client):
        """Test profile page requires authentication."""
        response = client.get("/profile", follow_redirects=False)
        
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_profile_page_with_auth(self, authenticated_admin_client):
        """Test profile page with authentication."""
        response = authenticated_admin_client.get("/profile")
        
        assert response.status_code == 200
        assert "profile" in response.text.lower()
    
    def test_profile_page_includes_chat_functionality(self, authenticated_admin_client):
        """Test profile page includes chat functionality."""
        response = authenticated_admin_client.get("/profile")
        
        assert response.status_code == 200
        assert "chat-sidepane" in response.text
        assert "chat-input" in response.text
        assert "marked.min.js" in response.text
    
    def test_profile_page_includes_shared_chat_js(self, authenticated_admin_client):
        """Test profile page includes the shared chat.js file."""
        response = authenticated_admin_client.get("/profile")
        
        assert response.status_code == 200
        assert "chat.js" in response.text 