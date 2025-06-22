"""
Tests for user cleanup functionality.
"""

import pytest
import os
import sqlite3
from pathlib import Path
from tests.conftest import cleanup_user_data
from stem.security import SecurityManager
from hippocampus.user_database import get_user_database_path


class TestUserCleanup:
    """Test user cleanup functionality."""
    
    def test_cleanup_user_data(self, security_manager):
        """Test that cleanup_user_data removes all user data."""
        # Create a test user
        username = "cleanup_test_user"
        
        # Create user in security manager
        security_manager.create_user(
            username=username,
            first_name="Cleanup",
            last_name="Test",
            password="password123",
            email="cleanup@test.com"
        )
        
        # Verify user was created
        user = security_manager.get_user_by_username(username)
        assert user is not None
        assert user['username'] == username
        
        # Create user database (this would normally happen when user first logs in)
        db_path = get_user_database_path(username)
        
        # Create the database file
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO test_table (id) VALUES (1)")
        conn.close()
        
        # Verify database exists
        assert os.path.exists(db_path)
        
        # Create user directory
        user_dir = Path("hippocampus") / "shortterm" / username
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a test file in the directory
        test_file = user_dir / "test.txt"
        test_file.write_text("test content")
        
        # Verify directory and file exist
        assert user_dir.exists()
        assert test_file.exists()
        
        # Clean up the user data
        cleanup_user_data(username)
        
        # Verify user database is deleted
        assert not os.path.exists(db_path)
        
        # Verify user directory is deleted
        assert not user_dir.exists()
        
        # Verify user is still in security manager (cleanup doesn't remove from system db)
        user = security_manager.get_user_by_username(username)
        assert user is not None
        
        # Clean up the user from security manager too
        security_manager.delete_user(username)
        
        # Verify user is completely removed
        user = security_manager.get_user_by_username(username)
        assert user is None
    
    def test_cleanup_nonexistent_user(self):
        """Test that cleanup_user_data handles nonexistent users gracefully."""
        username = "nonexistent_user"
        
        # This should not raise an exception
        cleanup_user_data(username)
        
        # Verify no files were created
        db_path = get_user_database_path(username)
        user_dir = Path("hippocampus") / "shortterm" / username
        
        assert not os.path.exists(db_path)
        assert not user_dir.exists()
    
    def test_cleanup_with_partial_data(self):
        """Test cleanup when only some user data exists."""
        username = "partial_test_user"
        
        # Create only the database
        db_path = get_user_database_path(username)
        conn = sqlite3.connect(db_path)
        conn.close()
        
        # Verify database exists
        assert os.path.exists(db_path)
        
        # Clean up
        cleanup_user_data(username)
        
        # Verify database is deleted
        assert not os.path.exists(db_path)
        
        # Test with only directory
        user_dir = Path("hippocampus") / "shortterm" / username
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Verify directory exists
        assert user_dir.exists()
        
        # Clean up
        cleanup_user_data(username)
        
        # Verify directory is deleted
        assert not user_dir.exists() 