"""
Tests for stem.installation.database_setup
"""

import os
import sqlite3
import pytest
import uuid
from stem.installation.database_setup import (
    create_system_db_tables,
    create_longterm_db_tables,
    create_default_roles,
    create_default_groups,
    create_default_rise_and_shine
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
        assert any("rise and shine" in text.lower() for text in instruction_texts)
        
        conn.close()
    
    def test_database_schema_integrity(self, temp_system_db):
        """Test that database schema is properly structured."""
        conn = sqlite3.connect(temp_system_db)
        cursor = conn.cursor()
        
        # Test users table structure
        cursor.execute("PRAGMA table_info(users)")
        user_columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        expected_user_columns = {
            'username': 'TEXT',
            'first_name': 'TEXT',
            'last_name': 'TEXT',
            'email': 'TEXT',
            'password_hash': 'TEXT',
            'salt': 'TEXT',
            'created_at': 'TIMESTAMP',
            'updated_at': 'TIMESTAMP'
        }
        
        for col, col_type in expected_user_columns.items():
            assert col in user_columns
            # Note: SQLite type checking is loose, so we just check existence
        
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
        
        # Insert a user first
        cursor.execute("""
            INSERT INTO users (username, first_name, last_name, password_hash, salt)
            VALUES (?, ?, ?, ?, ?)
        """, (username, "Test", "User", "hash", "salt"))
        
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
        
        conn.close() 