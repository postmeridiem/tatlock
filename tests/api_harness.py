"""
tests/api_harness.py

Test harness for the Tatlock API.
"""

from fastapi.testclient import TestClient
from main import app
from stem.security import SecurityManager

class TestAPIHarness:
    """A test harness for the Tatlock API."""

    def __init__(self):
        self.client = TestClient(app)
        self.security_manager = SecurityManager()

    def create_user(self, username_prefix: str, roles: list = None, groups: list = None):
        """Create a test user with a unique username."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        username = f'{username_prefix}_{unique_id}'
        password = 'password123'

        self.security_manager.create_user(username, 'Test', 'User', password, f'{username}@test.com')
        
        if roles:
            for role in roles:
                self.security_manager.add_user_to_role(username, role)
        
        if groups:
            for group in groups:
                self.security_manager.add_user_to_group(username, group)

        return {
            'username': username,
            'password': password
        }

    def get_authenticated_client(self, username, password):
        """Get an authenticated client for a specific user."""
        client = TestClient(app)
        response = client.post("/login/auth", json={
            "username": username,
            "password": password
        })
        assert response.status_code == 200
        return client
