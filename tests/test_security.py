"""
Tests for stem.security module.
"""

import pytest
import uuid
import time
import tempfile
import os
from stem.security import SecurityManager


class TestSecurityManager:
    """Test SecurityManager class."""
    
    def test_init(self, security_manager):
        """Test SecurityManager initialization."""
        assert security_manager is not None
        assert hasattr(security_manager, 'db_path')
    
    def test_hash_password(self, security_manager):
        """Test password hashing and verification."""
        password = "testpassword123"
        
        # Test hashing
        hash1, salt1 = security_manager.hash_password(password)
        assert isinstance(hash1, str)
        assert isinstance(salt1, str)
        assert len(hash1) > 0
        assert len(salt1) > 0
        
        # Test verification
        assert security_manager.verify_password(password, hash1, salt1)
        assert not security_manager.verify_password("wrongpassword", hash1, salt1)
        
        # Test with same salt
        hash2, salt2 = security_manager.hash_password(password, salt1)
        assert hash2 == hash1
        assert salt2 == salt1
    
    def test_create_user(self, security_manager):
        """Test user creation."""
        # Use unique username to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        username = f'testuser_{unique_id}'
        
        # Create a user
        success = security_manager.create_user(
            username=username,
            first_name="Test",
            last_name="User",
            password="password123",
            email="test@example.com"
        )
        assert success is True
        
        # Verify user exists
        user = security_manager.get_user_by_username(username)
        assert user is not None
        assert user['username'] == username
        assert user['first_name'] == "Test"
        assert user['last_name'] == "User"
        assert user['email'] == "test@example.com"
        
        # Test duplicate username
        success = security_manager.create_user(
            username=username,
            first_name="Another",
            last_name="User",
            password="password456",
            email="another@example.com"
        )
        assert success is False
    
    def test_authenticate_user(self, security_manager):
        """Test user authentication."""
        # Use unique username to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        username = f'authuser_{unique_id}'
        
        # Create a user
        security_manager.create_user(
            username=username,
            first_name="Auth",
            last_name="User",
            password="authpass",
            email="auth@example.com"
        )
        
        # Test correct credentials
        user = security_manager.authenticate_user(username, "authpass")
        assert user is not None
        assert user['username'] == username
        
        # Test wrong password
        user = security_manager.authenticate_user(username, "wrongpass")
        assert user is None
        
        # Test non-existent user
        user = security_manager.authenticate_user("nonexistent", "password")
        assert user is None
    
    def test_roles_and_groups(self, security_manager):
        """Test role and group management."""
        # Use unique username to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        username = f'roleuser_{unique_id}'
        
        # Create a user
        security_manager.create_user(
            username=username,
            first_name="Role",
            last_name="User",
            password="password",
            email="role@example.com"
        )
        
        # Test adding roles
        assert security_manager.add_user_to_role(username, "admin")
        assert security_manager.add_user_to_role(username, "user")
        
        # Test getting user roles
        roles = security_manager.get_user_roles(username)
        assert "admin" in roles
        assert "user" in roles
        
        # Test adding groups
        assert security_manager.add_user_to_group(username, "admins")
        assert security_manager.add_user_to_group(username, "users")
        
        # Test getting user groups
        groups = security_manager.get_user_groups(username)
        assert "admins" in groups
        assert "users" in groups
        
        # Test role/group checking
        assert security_manager.user_has_role(username, "admin")
        assert security_manager.user_has_role(username, "user")
        assert not security_manager.user_has_role(username, "moderator")
        
        assert security_manager.user_has_group(username, "admins")
        assert security_manager.user_has_group(username, "users")
        assert not security_manager.user_has_group(username, "moderators")
    
    def test_set_user_roles(self, security_manager):
        """Test setting all roles for a user."""
        # Use unique username to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        username = f'setuser_{unique_id}'
        
        # Create a user
        security_manager.create_user(
            username=username,
            first_name="Set",
            last_name="User",
            password="password",
            email="set@example.com"
        )
        
        # Add initial roles
        security_manager.add_user_to_role(username, "user")
        security_manager.add_user_to_role(username, "admin")
        
        # Set new roles (should replace existing)
        success = security_manager.set_user_roles(username, ["moderator", "user"])
        assert success is True
        
        # Check roles
        roles = security_manager.get_user_roles(username)
        assert "moderator" in roles
        assert "user" in roles
        assert "admin" not in roles  # Should be removed
    
    def test_set_user_groups(self, security_manager):
        """Test setting all groups for a user."""
        # Use unique username to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        username = f'setgroupuser_{unique_id}'
        
        # Create a user
        security_manager.create_user(
            username=username,
            first_name="SetGroup",
            last_name="User",
            password="password",
            email="setgroup@example.com"
        )
        
        # Add initial groups
        security_manager.add_user_to_group(username, "users")
        security_manager.add_user_to_group(username, "admins")
        
        # Set new groups (should replace existing)
        success = security_manager.set_user_groups(username, ["moderators", "users"])
        assert success is True
        
        # Check groups
        groups = security_manager.get_user_groups(username)
        assert "moderators" in groups
        assert "users" in groups
        assert "admins" not in groups  # Should be removed
    
    def test_update_user(self, security_manager):
        """Test user information updates."""
        # Use unique username to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        username = f'updateuser_{unique_id}'
        
        # Create a user
        security_manager.create_user(
            username=username,
            first_name="Update",
            last_name="User",
            password="password",
            email="update@example.com"
        )
        
        # Update user information
        success = security_manager.update_user(
            username=username,
            first_name="Updated",
            last_name="Name",
            email="updated@example.com"
        )
        assert success is True
        
        # Verify updates
        user = security_manager.get_user_by_username(username)
        assert user['first_name'] == "Updated"
        assert user['last_name'] == "Name"
        assert user['email'] == "updated@example.com"
        
        # Test password update
        success = security_manager.update_user(
            username=username,
            password="newpassword"
        )
        assert success is True
        
        # Verify new password works
        auth_user = security_manager.authenticate_user(username, "newpassword")
        assert auth_user is not None
    
    def test_delete_user(self, security_manager):
        """Test user deletion."""
        # Use unique username to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        username = f'deleteuser_{unique_id}'
        # Create a user with roles and groups
        security_manager.create_user(
            username=username,
            first_name="Delete",
            last_name="User",
            password="password",
            email="delete@example.com"
        )
        security_manager.add_user_to_role(username, "user")
        security_manager.add_user_to_group(username, "users")
        # Verify user exists
        user = security_manager.get_user_by_username(username)
        assert user is not None
        # Delete user
        success = security_manager.delete_user(username)
        assert success is True
        # Retry a few times in case of DB propagation delay
        for _ in range(3):
            user = security_manager.get_user_by_username(username)
            roles = security_manager.get_user_roles(username)
            groups = security_manager.get_user_groups(username)
            if user is None and roles == [] and groups == []:
                break
            time.sleep(0.1)
        assert user is None
        assert roles == []
        assert groups == []
    
    def test_get_all_users(self, security_manager):
        """Test getting all users."""
        users = security_manager.get_all_users()
        assert isinstance(users, list)
        # Should have at least the default admin user
        assert len(users) >= 1
        
        # Check user structure
        if users:
            user = users[0]
            assert 'username' in user
            assert 'first_name' in user
            assert 'last_name' in user
            assert 'email' in user
            assert 'created_at' in user
    
    def test_get_all_roles(self, security_manager):
        """Test getting all roles."""
        roles = security_manager.get_all_roles()
        assert isinstance(roles, list)
        # Should have default roles
        assert len(roles) >= 3
        
        role_names = [role['role_name'] for role in roles]
        assert "user" in role_names
        assert "admin" in role_names
        assert "moderator" in role_names
    
    def test_get_all_groups(self, security_manager):
        """Test getting all groups."""
        groups = security_manager.get_all_groups()
        assert isinstance(groups, list)
        # Should have default groups
        assert len(groups) >= 3
        
        group_names = [group['group_name'] for group in groups]
        assert "users" in group_names
        assert "admins" in group_names
        assert "moderators" in group_names
    
    def test_role_management(self, security_manager):
        """Test role CRUD operations."""
        # Use unique role name to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        role_name = f'testrole_{unique_id}'
        
        # Create a role
        success = security_manager.create_role(role_name, "Test role description")
        assert success is True
        
        # Get role by name
        role = security_manager.get_role_by_name(role_name)
        assert role is not None
        assert role['role_name'] == role_name
        assert role['description'] == "Test role description"
        
        # Update role
        success = security_manager.update_role(role['id'], f"{role_name}_updated", "Updated description")
        assert success is True
        
        # Verify update
        updated_role = security_manager.get_role_by_name(f"{role_name}_updated")
        assert updated_role is not None
        assert updated_role['description'] == "Updated description"
        
        # Delete role
        success = security_manager.delete_role(updated_role['id'])
        assert success is True
        
        # Verify deletion
        deleted_role = security_manager.get_role_by_name(f"{role_name}_updated")
        assert deleted_role is None
    
    def test_group_management(self, security_manager):
        """Test group CRUD operations."""
        # Use unique group name to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        group_name = f'testgroup_{unique_id}'
        
        # Create a group
        success = security_manager.create_group(group_name, "Test group description")
        assert success is True
        
        # Get group by name
        group = security_manager.get_group_by_name(group_name)
        assert group is not None
        assert group['group_name'] == group_name
        assert group['description'] == "Test group description"
        
        # Update group
        success = security_manager.update_group(group['id'], f"{group_name}_updated", "Updated description")
        assert success is True
        
        # Verify update
        updated_group = security_manager.get_group_by_name(f"{group_name}_updated")
        assert updated_group is not None
        assert updated_group['description'] == "Updated description"
        
        # Delete group
        success = security_manager.delete_group(updated_group['id'])
        assert success is True
        
        # Verify deletion
        deleted_group = security_manager.get_group_by_name(f"{group_name}_updated")
        assert deleted_group is None

def test_user_creation_with_new_schema():
    """Test that user creation works with the new passwords table schema."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Create security manager with temporary database
        security = SecurityManager()
        security.db_path = db_path
        
        # Create the database tables
        from stem.installation.database_setup import create_system_db_tables
        create_system_db_tables(db_path)
        
        # Create a test user
        success = security.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpassword123',
            email='test@example.com'
        )
        
        assert success is True
        
        # Verify user was created in users table
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username, first_name, last_name, email FROM users WHERE username = ?", ('testuser',))
        user_data = cursor.fetchone()
        assert user_data is not None
        assert user_data[0] == 'testuser'
        assert user_data[1] == 'Test'
        assert user_data[2] == 'User'
        assert user_data[3] == 'test@example.com'
        
        # Verify password was created in passwords table
        cursor.execute("SELECT username, password_hash, salt FROM passwords WHERE username = ?", ('testuser',))
        password_data = cursor.fetchone()
        assert password_data is not None
        assert password_data[0] == 'testuser'
        assert password_data[1] is not None  # hash should exist
        assert password_data[2] is not None  # salt should exist
        
        conn.close()
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_user_authentication_with_new_schema():
    """Test that user authentication works with the new passwords table schema."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Create security manager with temporary database
        security = SecurityManager()
        security.db_path = db_path
        
        # Create the database tables
        from stem.installation.database_setup import create_system_db_tables
        create_system_db_tables(db_path)
        
        # Create a test user
        success = security.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpassword123',
            email='test@example.com'
        )
        
        assert success is True
        
        # Test authentication with correct password
        user_data = security.authenticate_user('testuser', 'testpassword123')
        assert user_data is not None
        assert user_data['username'] == 'testuser'
        assert user_data['first_name'] == 'Test'
        assert user_data['last_name'] == 'User'
        assert user_data['email'] == 'test@example.com'
        assert 'password_hash' not in user_data  # Password data should not be returned
        assert 'salt' not in user_data  # Salt should not be returned
        
        # Test authentication with incorrect password
        user_data = security.authenticate_user('testuser', 'wrongpassword')
        assert user_data is None
        
        # Test authentication with non-existent user
        user_data = security.authenticate_user('nonexistent', 'testpassword123')
        assert user_data is None
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_user_update_with_new_schema():
    """Test that user updates work with the new passwords table schema."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Create security manager with temporary database
        security = SecurityManager()
        security.db_path = db_path
        
        # Create the database tables
        from stem.installation.database_setup import create_system_db_tables
        create_system_db_tables(db_path)
        
        # Create a test user
        success = security.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpassword123',
            email='test@example.com'
        )
        
        assert success is True
        
        # Update user information
        success = security.update_user(
            username='testuser',
            first_name='Updated',
            last_name='Name',
            email='updated@example.com',
            password='newpassword456'
        )
        
        assert success is True
        
        # Verify user data was updated
        user_data = security.get_user_by_username('testuser')
        assert user_data is not None
        assert user_data['first_name'] == 'Updated'
        assert user_data['last_name'] == 'Name'
        assert user_data['email'] == 'updated@example.com'
        
        # Verify password was updated
        user_data = security.authenticate_user('testuser', 'newpassword456')
        assert user_data is not None
        assert user_data['username'] == 'testuser'
        
        # Old password should not work
        user_data = security.authenticate_user('testuser', 'testpassword123')
        assert user_data is None
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_user_deletion_with_new_schema():
    """Test that user deletion works with the new passwords table schema."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Create security manager with temporary database
        security = SecurityManager()
        security.db_path = db_path
        
        # Create the database tables
        from stem.installation.database_setup import create_system_db_tables
        create_system_db_tables(db_path)
        
        # Create a test user
        success = security.create_user(
            username='testuser',
            first_name='Test',
            last_name='User',
            password='testpassword123',
            email='test@example.com'
        )
        
        assert success is True
        
        # Verify user and password exist
        user_data = security.get_user_by_username('testuser')
        assert user_data is not None
        
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM passwords WHERE username = ?", ('testuser',))
        password_exists = cursor.fetchone() is not None
        assert password_exists
        conn.close()
        
        # Delete user
        success = security.delete_user('testuser')
        assert success is True
        
        # Verify user and password were deleted
        user_data = security.get_user_by_username('testuser')
        assert user_data is None
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM passwords WHERE username = ?", ('testuser',))
        password_exists = cursor.fetchone() is not None
        assert not password_exists
        conn.close()
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path) 