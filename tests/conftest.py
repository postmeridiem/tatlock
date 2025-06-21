"""
pytest configuration and shared fixtures for Tatlock tests.
"""

import os
import tempfile
import pytest
import sqlite3
from unittest.mock import patch, MagicMock

# Patch SYSTEM_DB_PATH before any app/security_manager import
_db_fd, _db_path = tempfile.mkstemp(suffix='.db')
os.close(_db_fd)
os.environ["SYSTEM_DB"] = _db_path

from fastapi.testclient import TestClient
from main import app
from stem.security import SecurityManager
from stem.installation.database_setup import create_system_db_tables, create_longterm_db_tables


@pytest.fixture(scope="session")
def temp_system_db():
    db_path = os.environ["SYSTEM_DB"]
    create_system_db_tables(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def temp_longterm_db():
    """Create a temporary longterm database for testing."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Initialize the database with tables
    create_longterm_db_tables(db_path)
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def security_manager(temp_system_db):
    """Create a SecurityManager instance with a temporary database."""
    manager = SecurityManager()
    manager.db_path = temp_system_db
    return manager


@pytest.fixture
def client():
    """Create a test client for FastAPI."""
    return TestClient(app)


@pytest.fixture
def admin_user(security_manager):
    """Create an admin user for testing."""
    # Use unique username to avoid conflicts
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    username = f'admin_{unique_id}'
    
    security_manager.create_user(username, 'Admin', 'User', 'admin123', 'admin@test.com')
    security_manager.add_user_to_role(username, 'admin')
    security_manager.add_user_to_group(username, 'admins')
    return {
        'username': username,
        'password': 'admin123',
        'first_name': 'Admin',
        'last_name': 'User',
        'email': 'admin@test.com'
    }


@pytest.fixture
def test_user(security_manager):
    """Create a regular test user."""
    # Use unique username to avoid conflicts
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    username = f'testuser_{unique_id}'
    
    security_manager.create_user(username, 'Test', 'User', 'password123', 'test@test.com')
    security_manager.add_user_to_role(username, 'user')
    security_manager.add_user_to_group(username, 'users')
    return {
        'username': username,
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@test.com'
    }


@pytest.fixture
def authenticated_admin_client(client, admin_user):
    """Create a test client authenticated as admin."""
    # Login as admin
    response = client.post("/login/auth", json={
        "username": admin_user['username'],
        "password": admin_user['password']
    })
    assert response.status_code == 200
    
    return client


@pytest.fixture
def authenticated_user_client(client, test_user):
    """Create a test client authenticated as regular user."""
    # Login as test user
    response = client.post("/login/auth", json={
        "username": test_user['username'],
        "password": test_user['password']
    })
    assert response.status_code == 200
    
    return client


@pytest.fixture(autouse=True)
def mock_ollama():
    """Mock Ollama calls to avoid external dependencies in tests."""
    with patch('cortex.agent.ollama') as mock_ollama:
        # Mock the chat method to return a message with 'role': 'assistant'
        mock_ollama.chat.return_value = {
            'message': {
                'role': 'assistant',
                'content': 'This is a mocked response from the AI assistant.'
            }
        }
        yield mock_ollama


@pytest.fixture(autouse=True)
def mock_tools():
    """Mock tool calls to avoid external dependencies in tests."""
    with patch('cortex.agent.TOOLS') as mock_tools:
        mock_tools.return_value = []
        yield mock_tools 