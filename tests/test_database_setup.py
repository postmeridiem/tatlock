"""
Tests for stem.installation.database_setup
"""

import os
import sqlite3
import pytest
import uuid
import tempfile
from stem.installation.database_setup import (
    create_system_db_tables,
    create_longterm_db_tables,
    create_default_roles,
    create_default_groups,
    create_default_rise_and_shine,
    migrate_users_table,
    check_and_run_migrations,
    SYSTEM_DB_SCHEMA
)


class TestDatabaseSetup:
    """Test cases for database setup functionality."""
    
    def test_create_system_db_tables(self, temp_system_db):
        """Test system database table creation."""
        # Verify tables exist
        conn = sqlite3.connect(temp_system_db)
        cursor = conn.cursor()
        
        # Check that all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['users', 'roles', 'groups', 'user_roles', 'user_groups']
        for table in expected_tables:
            assert table in tables
        
        # Check that default roles exist
        cursor.execute("SELECT role_name FROM roles")
        roles = [row[0] for row in cursor.fetchall()]
        assert "user" in roles
        assert "admin" in roles
        assert "moderator" in roles
        
        # Check that default groups exist
        cursor.execute("SELECT group_name FROM groups")
        groups = [row[0] for row in cursor.fetchall()]
        assert "users" in groups
        assert "admins" in groups
        assert "moderators" in groups
        
        conn.close()
    
    def test_create_longterm_db_tables(self, temp_longterm_db):
        """Test longterm database table creation."""
        # Verify tables exist
        conn = sqlite3.connect(temp_longterm_db)
        cursor = conn.cursor()
        
        # Check that all tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'memories', 'topics', 'memory_topics', 'conversation_topics',
            'conversations', 'rise_and_shine'
        ]
        for table in expected_tables:
            assert table in tables
        
        # Check that default rise_and_shine instructions exist
        cursor.execute("SELECT instruction FROM rise_and_shine")
        instructions = [row[0] for row in cursor.fetchall()]
        assert len(instructions) >= 3  # Should have default instructions
        
        conn.close()
    
    def test_create_default_roles(self, temp_system_db):
        """Test default role creation."""
        conn = sqlite3.connect(temp_system_db)
        cursor = conn.cursor()
        
        # Create tables first
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create default roles
        create_default_roles(cursor)
        conn.commit()
        
        # Check roles
        cursor.execute("SELECT role_name, description FROM roles")
        roles = cursor.fetchall()
        
        expected_roles = [
            ("user", "Basic user role"),
            ("admin", "Administrator role"),
            ("moderator", "Moderator role")
        ]
        
        for expected_role in expected_roles:
            assert expected_role in roles
        
        conn.close()
    
    def test_create_default_groups(self, temp_system_db):
        """Test default group creation."""
        conn = sqlite3.connect(temp_system_db)
        cursor = conn.cursor()
        
        # Create tables first
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create default groups
        create_default_groups(cursor)
        conn.commit()
        
        # Check groups
        cursor.execute("SELECT group_name, description FROM groups")
        groups = cursor.fetchall()
        
        expected_groups = [
            ("users", "All users"),
            ("admins", "Administrators"),
            ("moderators", "Moderators")
        ]
        
        for expected_group in expected_groups:
            assert expected_group in groups
        
        conn.close()
    
    def test_create_default_rise_and_shine(self, temp_longterm_db):
        """Test default rise_and_shine instructions creation."""
        conn = sqlite3.connect(temp_longterm_db)
        cursor = conn.cursor()
        
        # Create tables first
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS rise_and_shine (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instruction TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create default instructions
        create_default_rise_and_shine(cursor)
        conn.commit()
        
        # Check instructions
        cursor.execute("SELECT instruction FROM rise_and_shine")
        instructions = cursor.fetchall()
        
        # Should have at least 3 default instructions
        assert len(instructions) >= 3
        
        # Check that instructions contain expected content
        instruction_texts = [row[0] for row in instructions]
        
        # Look for key phrases in the default instructions
        assert any("Tatlock" in text for text in instruction_texts)
        assert any("tool" in text.lower() for text in instruction_texts)
        assert any("rise_and_shine" in text.lower() for text in instruction_texts)
        
        conn.close()
    
    def test_database_schema_integrity(self, temp_system_db):
        """Test that database schema is properly structured."""
        conn = sqlite3.connect(temp_system_db)
        cursor = conn.cursor()
        
        # Test users table structure (no longer contains password data)
        cursor.execute("PRAGMA table_info(users)")
        user_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_user_columns = {
            'username': 'TEXT',
            'first_name': 'TEXT',
            'last_name': 'TEXT',
            'email': 'TEXT',
            'created_at': 'TIMESTAMP',
            'updated_at': 'TIMESTAMP'
        }
        
        for col, col_type in expected_user_columns.items():
            assert col in user_columns
            # Note: SQLite type checking is loose, so we just check existence
        
        # Test passwords table structure (new table for password data)
        cursor.execute("PRAGMA table_info(passwords)")
        password_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_password_columns = {
            'username': 'TEXT',
            'password_hash': 'TEXT',
            'salt': 'TEXT',
            'created_at': 'TIMESTAMP',
            'updated_at': 'TIMESTAMP'
        }
        
        for col, col_type in expected_password_columns.items():
            assert col in password_columns
        
        # Test roles table structure
        cursor.execute("PRAGMA table_info(roles)")
        role_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_role_columns = {
            'id': 'INTEGER',
            'role_name': 'TEXT',
            'description': 'TEXT',
            'created_at': 'TIMESTAMP'
        }
        
        for col, col_type in expected_role_columns.items():
            assert col in role_columns
        
        # Test groups table structure
        cursor.execute("PRAGMA table_info(groups)")
        group_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_group_columns = {
            'id': 'INTEGER',
            'group_name': 'TEXT',
            'description': 'TEXT',
            'created_at': 'TIMESTAMP'
        }
        
        for col, col_type in expected_group_columns.items():
            assert col in group_columns
        
        conn.close()
    
    def test_foreign_key_constraints(self, temp_system_db):
        """Test that foreign key constraints are properly set up."""
        conn = sqlite3.connect(temp_system_db)
        cursor = conn.cursor()
        
        # Enable foreign key constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        # Use a unique username to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        username = f'testuser_{unique_id}'
        
        # Insert a user first (without password data)
        cursor.execute("""
            INSERT INTO users (username, first_name, last_name, email)
            VALUES (?, ?, ?, ?)
        """, (username, "Test", "User", "test@example.com"))
        
        # Insert password data separately
        cursor.execute("""
            INSERT INTO passwords (username, password_hash, salt)
            VALUES (?, ?, ?)
        """, (username, "hash", "salt"))
        
        # Try to insert invalid role_id (should fail)
        try:
            cursor.execute("""
                INSERT INTO user_roles (username, role_id)
                VALUES (?, ?)
            """, (username, 999))  # Non-existent role_id
            assert False, "Should have failed due to foreign key constraint"
        except sqlite3.IntegrityError:
            pass  # Expected to fail
        
        # Try to insert invalid group_id (should fail)
        try:
            cursor.execute("""
                INSERT INTO user_groups (username, group_id)
                VALUES (?, ?)
            """, (username, 999))  # Non-existent group_id
            assert False, "Should have failed due to foreign key constraint"
        except sqlite3.IntegrityError:
            pass  # Expected to fail
        
        # Test that deleting user cascades to passwords table
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        cursor.execute("SELECT username FROM passwords WHERE username = ?", (username,))
        password_exists = cursor.fetchone() is not None
        assert not password_exists, "Password should be deleted when user is deleted"
        
        conn.close()

def test_password_migration():
    """Test that password migration works correctly."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Create database with old schema (users table with password columns)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create old schema
        old_schema = """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS user_roles (
            username TEXT,
            role_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (username, role_id),
            FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
        );
        
        CREATE TABLE IF NOT EXISTS user_groups (
            username TEXT,
            group_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (username, group_id),
            FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
            FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
        );
        """
        
        cursor.executescript(old_schema)
        
        # Insert test user with password data
        cursor.execute("""
            INSERT INTO users (username, first_name, last_name, email, password_hash, salt)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('testuser', 'Test', 'User', 'test@example.com', 'test_hash', 'test_salt'))
        
        conn.commit()
        conn.close()
        
        # Verify old schema exists
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        assert 'password_hash' in columns
        assert 'salt' in columns
        conn.close()
        
        # Run migration
        check_and_run_migrations(db_path)
        
        # Verify new schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        assert 'password_hash' not in columns
        assert 'salt' not in columns
        assert 'username' in columns
        assert 'first_name' in columns
        assert 'last_name' in columns
        assert 'email' in columns
        
        # Check passwords table exists
        cursor.execute("PRAGMA table_info(passwords)")
        password_columns = [column[1] for column in cursor.fetchall()]
        assert 'username' in password_columns
        assert 'password_hash' in password_columns
        assert 'salt' in password_columns
        
        # Verify data was migrated
        cursor.execute("SELECT username, first_name, last_name, email FROM users WHERE username = ?", ('testuser',))
        user_data = cursor.fetchone()
        assert user_data is not None
        assert user_data[0] == 'testuser'
        assert user_data[1] == 'Test'
        assert user_data[2] == 'User'
        assert user_data[3] == 'test@example.com'
        
        cursor.execute("SELECT username, password_hash, salt FROM passwords WHERE username = ?", ('testuser',))
        password_data = cursor.fetchone()
        assert password_data is not None
        assert password_data[0] == 'testuser'
        assert password_data[1] == 'test_hash'
        assert password_data[2] == 'test_salt'
        
        # Check migration was recorded
        cursor.execute("SELECT COUNT(*) FROM migrations WHERE migration_name = 'users_password_separation'")
        migration_count = cursor.fetchone()[0]
        assert migration_count == 1
        
        conn.close()
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path)

def test_migration_idempotent():
    """Test that running migration multiple times doesn't cause issues."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
        db_path = tmp_file.name
    
    try:
        # Create database with old schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        old_schema = """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.executescript(old_schema)
        
        # Insert test user
        cursor.execute("""
            INSERT INTO users (username, first_name, last_name, email, password_hash, salt)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('testuser', 'Test', 'User', 'test@example.com', 'test_hash', 'test_salt'))
        
        conn.commit()
        conn.close()
        
        # Run migration twice
        check_and_run_migrations(db_path)
        check_and_run_migrations(db_path)
        
        # Verify data is still intact
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT username FROM users WHERE username = ?", ('testuser',))
        user_exists = cursor.fetchone() is not None
        assert user_exists
        
        cursor.execute("SELECT username FROM passwords WHERE username = ?", ('testuser',))
        password_exists = cursor.fetchone() is not None
        assert password_exists
        
        # Check migration was only recorded once
        cursor.execute("SELECT COUNT(*) FROM migrations WHERE migration_name = 'users_password_separation'")
        migration_count = cursor.fetchone()[0]
        assert migration_count == 1
        
        conn.close()
        
    finally:
        # Clean up
        if os.path.exists(db_path):
            os.unlink(db_path) 