"""
security.py

Authentication and authorization system for Tatlock.
Handles user management, password hashing, and role-based access control.
"""

import sqlite3
import hashlib
import os
import secrets
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys
sys.path.append('..')
from config import SYSTEM_DB_PATH
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from hippocampus.user_database import ensure_user_database, delete_user_database

# Security setup
security = HTTPBasic()

class SecurityManager:
    """Manages authentication, authorization, and user management."""
    
    def __init__(self):
        self.db_path = SYSTEM_DB_PATH
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Hash a password with a salt.
        Args:
            password (str): Plain text password
            salt (Optional[str]): Salt to use. If None, generates a new one.
        Returns:
            tuple[str, str]: (password_hash, salt)
        """
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA256
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        password_hash = hash_obj.hex()
        
        return password_hash, salt
    
    def verify_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        """
        Verify a password against stored hash and salt.
        Args:
            password (str): Plain text password to verify
            stored_hash (str): Stored password hash
            stored_salt (str): Stored salt
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            # Hash the provided password with the stored salt
            test_hash, _ = self.hash_password(password, stored_salt)
            # Compare the hashes
            return test_hash == stored_hash
        except Exception as e:
            return False
    
    def create_user(self, username: str, first_name: str, last_name: str, 
                   password: str, email: Optional[str] = None) -> bool:
        """
        Create a new user.
        Args:
            username (str): Unique username
            first_name (str): User's first name
            last_name (str): User's last name
            password (str): Plain text password
            email (Optional[str]): User's email address
        Returns:
            bool: True if user created successfully, False otherwise
        """
        try:
            password_hash, salt = self.hash_password(password)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO users (username, first_name, last_name, email, password_hash, salt)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, first_name, last_name, email or "", password_hash, salt))
            
            conn.commit()
            conn.close()
            
            # Create user's longterm database
            try:
                ensure_user_database(username)
                print(f"Created longterm database for user '{username}'")
            except Exception as e:
                print(f"Warning: Failed to create longterm database for user '{username}': {e}")
            
            return True
            
        except sqlite3.IntegrityError:
            print(f"User '{username}' already exists")
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with username and password.
        Args:
            username (str): Username
            password (str): Password
        Returns:
            Optional[Dict[str, Any]]: User data if authentication successful, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT username, first_name, last_name, email, password_hash, salt, created_at
                FROM users WHERE username = ?
            """, (username,))
            row = cursor.fetchone()
            conn.close()
            if not row:
                return None
            db_username, first_name, last_name, email, stored_hash, stored_salt, created_at = row
            # Verify password
            if self.verify_password(password, stored_hash, stored_salt):
                return {
                    'username': db_username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'created_at': created_at
                }
            else:
                return None
        except Exception as e:
            return None
    
    def get_user_roles(self, username: str) -> List[str]:
        """
        Get all roles for a user.
        Args:
            username (str): Username
        Returns:
            List[str]: List of role names
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT r.role_name
                FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.username = ?
            """, (username,))
            
            roles = [row[0] for row in cursor.fetchall()]
            conn.close()
            return roles
            
        except Exception as e:
            print(f"Error getting user roles: {e}")
            return []
    
    def get_user_groups(self, username: str) -> List[str]:
        """
        Get all groups for a user.
        Args:
            username (str): Username
        Returns:
            List[str]: List of group names
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT g.group_name
                FROM groups g
                JOIN user_groups ug ON g.id = ug.group_id
                WHERE ug.username = ?
            """, (username,))
            
            groups = [row[0] for row in cursor.fetchall()]
            conn.close()
            return groups
            
        except Exception as e:
            print(f"Error getting user groups: {e}")
            return []
    
    def add_user_to_role(self, username: str, role_name: str) -> bool:
        """
        Add a user to a role.
        Args:
            username (str): Username
            role_name (str): Role name
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get role ID
            cursor.execute("SELECT id FROM roles WHERE role_name = ?", (role_name,))
            role_row = cursor.fetchone()
            
            if not role_row:
                print(f"Role '{role_name}' not found")
                return False
            
            # Add user to role
            cursor.execute("""
                INSERT OR IGNORE INTO user_roles (username, role_id)
                VALUES (?, ?)
            """, (username, role_row[0]))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding user to role: {e}")
            return False
    
    def add_user_to_group(self, username: str, group_name: str) -> bool:
        """
        Add a user to a group.
        Args:
            username (str): Username
            group_name (str): Group name
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get group ID
            cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
            group_row = cursor.fetchone()
            
            if not group_row:
                print(f"Group '{group_name}' not found")
                return False
            
            # Add user to group
            cursor.execute("""
                INSERT OR IGNORE INTO user_groups (username, group_id)
                VALUES (?, ?)
            """, (username, group_row[0]))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding user to group: {e}")
            return False
    
    def user_has_role(self, username: str, role_name: str) -> bool:
        """
        Check if a user has a specific role.
        Args:
            username (str): Username
            role_name (str): Role name to check
        Returns:
            bool: True if user has the role, False otherwise
        """
        return role_name in self.get_user_roles(username)
    
    def user_has_group(self, username: str, group_name: str) -> bool:
        """
        Check if a user belongs to a specific group.
        Args:
            username (str): Username
            group_name (str): Group name to check
        Returns:
            bool: True if user belongs to the group, False otherwise
        """
        return group_name in self.get_user_groups(username)
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user information by ID.
        Args:
            user_id (int): User ID
        Returns:
            Optional[Dict[str, Any]]: User data if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, first_name, last_name, email, created_at
                FROM users WHERE id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'username': row[1],
                    'first_name': row[2],
                    'last_name': row[3],
                    'email': row[4],
                    'created_at': row[5]
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user information by username.
        Args:
            username (str): Username
        Returns:
            Optional[Dict[str, Any]]: User data if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT username, first_name, last_name, email, created_at
                FROM users WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'username': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'email': row[3],
                    'created_at': row[4]
                }
            return None
            
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None

    def get_all_users(self) -> List[Dict[str, Any]]:
        """
        Get all users in the system.
        Returns:
            List[Dict[str, Any]]: List of all users
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT username, first_name, last_name, email, created_at
                FROM users ORDER BY username
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                users.append({
                    'username': row[0],
                    'first_name': row[1],
                    'last_name': row[2],
                    'email': row[3],
                    'created_at': row[4]
                })
            
            return users
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []

    def get_all_roles(self) -> List[Dict[str, Any]]:
        """
        Get all roles in the system.
        Returns:
            List[Dict[str, Any]]: List of all roles
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, role_name, description, created_at
                FROM roles ORDER BY role_name
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            roles = []
            for row in rows:
                roles.append({
                    'id': row[0],
                    'role_name': row[1],
                    'description': row[2],
                    'created_at': row[3]
                })
            
            return roles
            
        except Exception as e:
            print(f"Error getting all roles: {e}")
            return []

    def get_all_groups(self) -> List[Dict[str, Any]]:
        """
        Get all groups in the system.
        Returns:
            List[Dict[str, Any]]: List of all groups
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, group_name, description, created_at
                FROM groups ORDER BY group_name
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            groups = []
            for row in rows:
                groups.append({
                    'id': row[0],
                    'group_name': row[1],
                    'description': row[2],
                    'created_at': row[3]
                })
            
            return groups
            
        except Exception as e:
            print(f"Error getting all groups: {e}")
            return []

    def update_user(self, username: str, first_name: Optional[str] = None, 
                   last_name: Optional[str] = None, email: Optional[str] = None, 
                   password: Optional[str] = None) -> bool:
        """
        Update user information.
        Args:
            username (str): Username
            first_name (Optional[str]): New first name
            last_name (Optional[str]): New last name
            email (Optional[str]): New email
            password (Optional[str]): New password
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if first_name is not None:
                updates.append("first_name = ?")
                params.append(first_name)
            if last_name is not None:
                updates.append("last_name = ?")
                params.append(last_name)
            if email is not None:
                updates.append("email = ?")
                params.append(email)
            if password is not None:
                password_hash, salt = self.hash_password(password)
                updates.append("password_hash = ?")
                updates.append("salt = ?")
                params.append(password_hash)
                params.append(salt)
            
            # Add updated_at timestamp
            updates.append("updated_at = CURRENT_TIMESTAMP")
            
            if not updates:
                return True  # Nothing to update
            
            # Add username for WHERE clause
            params.append(username)
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE username = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def set_user_roles(self, username: str, roles: List[str]) -> bool:
        """
        Set all roles for a user (replaces existing roles).
        Args:
            username (str): Username
            roles (List[str]): List of role names
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Remove existing roles
            cursor.execute("DELETE FROM user_roles WHERE username = ?", (username,))
            
            # Add new roles
            for role_name in roles:
                cursor.execute("SELECT id FROM roles WHERE role_name = ?", (role_name,))
                role_row = cursor.fetchone()
                
                if role_row:
                    cursor.execute("""
                        INSERT INTO user_roles (username, role_id)
                        VALUES (?, ?)
                    """, (username, role_row[0]))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error setting user roles: {e}")
            return False

    def set_user_groups(self, username: str, groups: List[str]) -> bool:
        """
        Set all groups for a user (replaces existing groups).
        Args:
            username (str): Username
            groups (List[str]): List of group names
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Remove existing groups
            cursor.execute("DELETE FROM user_groups WHERE username = ?", (username,))
            
            # Add new groups
            for group_name in groups:
                cursor.execute("SELECT id FROM groups WHERE group_name = ?", (group_name,))
                group_row = cursor.fetchone()
                
                if group_row:
                    cursor.execute("""
                        INSERT INTO user_groups (username, group_id)
                        VALUES (?, ?)
                    """, (username, group_row[0]))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error setting user groups: {e}")
            return False

    def delete_user(self, username: str) -> bool:
        """
        Delete a user from the system.
        Args:
            username (str): Username
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if not cursor.fetchone():
                print(f"User '{username}' not found")
                return False
            
            # Check if this is the last admin user
            if self.user_has_role(username, "admin"):
                admin_users = [user for user in self.get_all_users() if "admin" in self.get_user_roles(user['username'])]
                if len(admin_users) <= 1:
                    print("Cannot delete the last admin user")
                    return False
            
            # Delete user (cascading will handle user_roles and user_groups)
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    # Role CRUD Operations
    def create_role(self, role_name: str, description: Optional[str] = None) -> bool:
        """
        Create a new role.
        Args:
            role_name (str): Unique role name
            description (Optional[str]): Role description
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO roles (role_name, description)
                VALUES (?, ?)
            """, (role_name, description))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            print(f"Role '{role_name}' already exists")
            return False
        except Exception as e:
            print(f"Error creating role: {e}")
            return False

    def get_role_by_id(self, role_id: int) -> Optional[Dict[str, Any]]:
        """
        Get role information by ID.
        Args:
            role_id (int): Role ID
        Returns:
            Optional[Dict[str, Any]]: Role data if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, role_name, description, created_at
                FROM roles WHERE id = ?
            """, (role_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'role_name': row[1],
                    'description': row[2],
                    'created_at': row[3]
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting role by ID: {e}")
            return None

    def get_role_by_name(self, role_name: str) -> Optional[Dict[str, Any]]:
        """
        Get role information by name.
        Args:
            role_name (str): Role name
        Returns:
            Optional[Dict[str, Any]]: Role data if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, role_name, description, created_at
                FROM roles WHERE role_name = ?
            """, (role_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'role_name': row[1],
                    'description': row[2],
                    'created_at': row[3]
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting role by name: {e}")
            return None

    def update_role(self, role_id: int, role_name: Optional[str] = None, 
                   description: Optional[str] = None) -> bool:
        """
        Update role information.
        Args:
            role_id (int): Role ID
            role_name (Optional[str]): New role name
            description (Optional[str]): New description
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if role_name is not None:
                updates.append("role_name = ?")
                params.append(role_name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if not updates:
                return True  # Nothing to update
            
            params.append(role_id)
            
            query = f"UPDATE roles SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            print(f"Role name already exists")
            return False
        except Exception as e:
            print(f"Error updating role: {e}")
            return False

    def delete_role(self, role_id: int) -> bool:
        """
        Delete a role and all associated user assignments.
        Args:
            role_id (int): Role ID
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete role (cascading will handle user_roles)
            cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error deleting role: {e}")
            return False

    def get_role_user_count(self, role_id: int) -> int:
        """
        Get the number of users assigned to a role.
        Args:
            role_id (int): Role ID
        Returns:
            int: Number of users with this role
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM user_roles WHERE role_id = ?
            """, (role_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
            
        except Exception as e:
            print(f"Error getting role user count: {e}")
            return 0

    # Group CRUD Operations
    def create_group(self, group_name: str, description: Optional[str] = None) -> bool:
        """
        Create a new group.
        Args:
            group_name (str): Unique group name
            description (Optional[str]): Group description
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO groups (group_name, description)
                VALUES (?, ?)
            """, (group_name, description))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            print(f"Group '{group_name}' already exists")
            return False
        except Exception as e:
            print(f"Error creating group: {e}")
            return False

    def get_group_by_id(self, group_id: int) -> Optional[Dict[str, Any]]:
        """
        Get group information by ID.
        Args:
            group_id (int): Group ID
        Returns:
            Optional[Dict[str, Any]]: Group data if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, group_name, description, created_at
                FROM groups WHERE id = ?
            """, (group_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'group_name': row[1],
                    'description': row[2],
                    'created_at': row[3]
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting group by ID: {e}")
            return None

    def get_group_by_name(self, group_name: str) -> Optional[Dict[str, Any]]:
        """
        Get group information by name.
        Args:
            group_name (str): Group name
        Returns:
            Optional[Dict[str, Any]]: Group data if found, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, group_name, description, created_at
                FROM groups WHERE group_name = ?
            """, (group_name,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'group_name': row[1],
                    'description': row[2],
                    'created_at': row[3]
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting group by name: {e}")
            return None

    def update_group(self, group_id: int, group_name: Optional[str] = None, 
                    description: Optional[str] = None) -> bool:
        """
        Update group information.
        Args:
            group_id (int): Group ID
            group_name (Optional[str]): New group name
            description (Optional[str]): New description
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            params = []
            
            if group_name is not None:
                updates.append("group_name = ?")
                params.append(group_name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if not updates:
                return True  # Nothing to update
            
            params.append(group_id)
            
            query = f"UPDATE groups SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.IntegrityError:
            print(f"Group name already exists")
            return False
        except Exception as e:
            print(f"Error updating group: {e}")
            return False

    def delete_group(self, group_id: int) -> bool:
        """
        Delete a group and all associated user assignments.
        Args:
            group_id (int): Group ID
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete group (cascading will handle user_groups)
            cursor.execute("DELETE FROM groups WHERE id = ?", (group_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error deleting group: {e}")
            return False

    def get_group_user_count(self, group_id: int) -> int:
        """
        Get the number of users assigned to a group.
        Args:
            group_id (int): Group ID
        Returns:
            int: Number of users in this group
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM user_groups WHERE group_id = ?
            """, (group_id,))
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
            
        except Exception as e:
            print(f"Error getting group user count: {e}")
            return 0

# Global security manager instance
security_manager = SecurityManager()

# FastAPI security dependency functions
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Authenticate user and return user data.
    Args:
        credentials: HTTP Basic credentials from request
    Returns:
        dict: User data if authentication successful
    Raises:
        HTTPException: If authentication fails
    """
    user = security_manager.authenticate_user(credentials.username, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

def require_admin_role(current_user: dict = Depends(get_current_user)):
    """
    Check if current user has admin role.
    Args:
        current_user: Authenticated user data
    Returns:
        dict: User data if admin
    Raises:
        HTTPException: If user doesn't have admin role
    """
    if not security_manager.user_has_role(current_user['username'], 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required"
        )
    return current_user

def create_initial_admin():
    """Create the initial admin user with specified credentials and roles."""
    # Create admin user
    if security_manager.create_user(
        username="admin",
        first_name="Administrator",
        last_name="User",
        password="breaker",
        email="admin@tatlock.local"
    ):
        print("Admin user created successfully")
        
        # Add roles
        security_manager.add_user_to_role("admin", "user")
        security_manager.add_user_to_role("admin", "admin")
        
        # Add groups
        security_manager.add_user_to_group("admin", "users")
        security_manager.add_user_to_group("admin", "admins")
        
        print(f"Admin user configured with roles and groups")
    else:
        print("Admin user already exists or creation failed")

if __name__ == "__main__":
    # Create initial admin user when script is run directly
    create_initial_admin() 