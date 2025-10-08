"""
pytest configuration and shared fixtures for Tatlock tests.
"""

import os
import tempfile
import pytest
import sqlite3
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Patch SYSTEM_DB_PATH before any app/security_manager import
_db_fd, _db_path = tempfile.mkstemp(suffix='.db')
os.close(_db_fd)
os.environ["SYSTEM_DB"] = _db_path

from fastapi.testclient import TestClient
from main import app
from stem.security import SecurityManager
from stem.installation.database_setup import create_system_db_tables, create_longterm_db_tables
from hippocampus.user_database import get_user_database_path, delete_user_database


def cleanup_user_data(username: str):
    """
    Clean up all user data including database and directories.
    
    Args:
        username (str): The username to clean up
    """
    try:
        # Delete user database
        db_path = get_user_database_path(username)
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # Delete user directories
        user_dir = Path("hippocampus") / "shortterm" / username
        if user_dir.exists():
            shutil.rmtree(user_dir)
            
    except Exception as e:
        # Log but don't fail the test
        print(f"Warning: Failed to cleanup user data for {username}: {e}")


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_users():
    """
    Clean up any test users that might have been created during testing.
    This runs at the end of the test session.
    """
    yield
    
    # Clean up test users that might have been created
    test_usernames = []
    
    # Check longterm directory for test databases
    longterm_dir = Path("hippocampus/longterm")
    if longterm_dir.exists():
        for db_file in longterm_dir.glob("*.db"):
            username = db_file.stem
            # Clean up test users (those with test-related names)
            if any(prefix in username.lower() for prefix in ['test', 'admin_', 'user_', 'temp_']):
                test_usernames.append(username)
    
    # Clean up each test user
    for username in test_usernames:
        cleanup_user_data(username)


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """
    Clean up after each test to ensure isolation.
    This fixture runs automatically for each test.
    """
    yield
    
    # This will be called after each test
    # Individual tests can use cleanup_user_data() if they create specific users
    pass


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
    
    user_data = {
        'username': username,
        'password': 'admin123',
        'first_name': 'Admin',
        'last_name': 'User',
        'email': 'admin@test.com'
    }
    
    yield user_data
    
    # Clean up after test
    cleanup_user_data(username)


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
    
    user_data = {
        'username': username,
        'password': 'password123',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@test.com'
    }
    
    yield user_data
    
    # Clean up after test
    cleanup_user_data(username)


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
    with patch('cortex.tatlock.ollama') as mock_tatlock, \
         patch('hippocampus.conversation_compact.ollama') as mock_compact:
        # Mock the chat method for cortex
        mock_tatlock.chat.return_value = {
            'message': {
                'role': 'assistant',
                'content': 'This is a mocked response from the AI assistant.'
            }
        }
        # Mock the chat method for conversation compacting
        mock_compact.chat.return_value = {
            'message': {
                'role': 'assistant',
                'content': 'TOPICS DISCUSSED:\n- Test topics\n\nFACTUAL TIMELINE:\nUser sent test messages.\n\nCONSERVATIVE SUMMARY:\nThis is a test conversation with multiple messages.'
            }
        }
        yield mock_tatlock


@pytest.fixture(autouse=True)
def mock_tools():
    """Mock tool calls to avoid external dependencies in tests."""
    # TOOLS is no longer used in the new 4.5-phase architecture
    # The new system uses dynamic tool loading through stem.tools
    pass 