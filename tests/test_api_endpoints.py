"""
Test API endpoints for Tatlock.

Tests authentication, protected endpoints, admin functionality, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from tests.conftest import cleanup_user_data


class TestAPIAuthentication:
    """Test authentication endpoints."""
    
    def test_root_redirect(self, client):
        """Test root endpoint redirects appropriately."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_login_page(self, client):
        """Test login page is accessible."""
        response = client.get("/login")
        assert response.status_code == 200
        assert "login" in response.text.lower()
    
    def test_login_auth_success(self, client, admin_user):
        """Test successful login authentication."""
        response = client.post("/login/auth", json={
            "username": admin_user['username'],
            "password": admin_user['password']
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
    
    def test_logout(self, authenticated_admin_client):
        """Test logout functionality."""
        response = authenticated_admin_client.post("/logout")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestAPIProtectedEndpoints:
    """Test protected endpoints that require authentication."""
    
    def test_chat_endpoint_requires_auth(self, client):
        """Test chat endpoint requires authentication."""
        response = client.post("/cortex", json={
            "message": "Hello",
            "history": []
        }, follow_redirects=False)
        # Should redirect to login page
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_chat_endpoint_with_auth(self, authenticated_admin_client):
        """Test chat endpoint with authentication."""
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
    
    def test_profile_page_requires_auth(self, client):
        """Test profile page requires authentication."""
        response = client.get("/profile", follow_redirects=False)
        # Should redirect to login page
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_profile_page_with_auth(self, authenticated_admin_client):
        """Test profile page with authentication."""
        response = authenticated_admin_client.get("/profile")
        assert response.status_code == 200
        assert "profile" in response.text.lower()


class TestAdminAPIEndpoints:
    """Test admin API endpoints."""
    
    def test_admin_dashboard_requires_auth(self, client):
        """Test admin dashboard requires authentication."""
        response = client.get("/admin/dashboard", follow_redirects=False)
        # Should redirect to login page
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_admin_dashboard_with_auth(self, authenticated_admin_client):
        """Test admin dashboard with authentication."""
        response = authenticated_admin_client.get("/admin/dashboard")
        assert response.status_code == 200
        assert "admin" in response.text.lower()
    
    def test_admin_stats_requires_auth(self, client):
        """Test admin stats requires authentication."""
        response = client.get("/admin/stats", follow_redirects=False)
        # Should redirect to login page
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_admin_stats_with_auth(self, authenticated_admin_client):
        """Test admin stats with authentication."""
        response = authenticated_admin_client.get("/admin/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_roles" in data
        assert "total_groups" in data
        assert "users_by_role" in data
        assert "users_by_group" in data
    
    def test_admin_users_list_requires_auth(self, client):
        """Test admin users list requires authentication."""
        response = client.get("/admin/users", follow_redirects=False)
        # Should redirect to login page
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_admin_users_list_with_auth(self, authenticated_admin_client):
        """Test admin users list with authentication."""
        response = authenticated_admin_client.get("/admin/users")
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        # Should have at least the admin user
        assert len(users) >= 1
    
    def test_admin_roles_list_requires_auth(self, client):
        """Test admin roles list requires authentication."""
        response = client.get("/admin/roles", follow_redirects=False)
        # Should redirect to login page
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_admin_roles_list_with_auth(self, authenticated_admin_client):
        """Test admin roles list with authentication."""
        response = authenticated_admin_client.get("/admin/roles")
        assert response.status_code == 200
        roles = response.json()
        assert isinstance(roles, list)
        # Should have default roles
        role_names = [role['role_name'] for role in roles]
        assert "user" in role_names
        assert "admin" in role_names
        assert "moderator" in role_names
    
    def test_admin_groups_list_requires_auth(self, client):
        """Test admin groups list requires authentication."""
        response = client.get("/admin/groups", follow_redirects=False)
        # Should redirect to login page
        assert response.status_code == 302
        assert "/login" in response.headers["location"]
    
    def test_admin_groups_list_with_auth(self, authenticated_admin_client):
        """Test admin groups list with authentication."""
        response = authenticated_admin_client.get("/admin/groups")
        assert response.status_code == 200
        groups = response.json()
        assert isinstance(groups, list)
        # Should have default groups
        group_names = [group['group_name'] for group in groups]
        assert "users" in group_names
        assert "admins" in group_names
        assert "moderators" in group_names


class TestAdminUserCRUD:
    """Test admin user CRUD operations."""
    
    def test_create_user(self, authenticated_admin_client):
        """Test creating a new user."""
        # Use unique username to avoid conflicts
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        username = f'newuser_{unique_id}'
        
        user_data = {
            "username": username,
            "first_name": "New",
            "last_name": "User",
            "password": "password123",
            "email": "newuser@test.com",
            "roles": ["user"],
            "groups": ["users"]
        }
        
        response = authenticated_admin_client.post("/admin/users", json=user_data)
        assert response.status_code == 200
        user = response.json()
        assert user["username"] == username
        assert user["first_name"] == "New"
        assert user["last_name"] == "User"
        assert user["email"] == "newuser@test.com"
        assert "user" in user["roles"]
        assert "users" in user["groups"]
        
        # Cleanup
        cleanup_user_data(username)
    
    def test_get_user(self, authenticated_admin_client, test_user):
        """Test getting a specific user."""
        response = authenticated_admin_client.get(f"/admin/users/{test_user['username']}")
        assert response.status_code == 200
        user = response.json()
        assert user["username"] == test_user['username']
        assert user["first_name"] == test_user['first_name']
        assert user["last_name"] == test_user['last_name']
        assert user["email"] == test_user['email']
    
    def test_update_user(self, authenticated_admin_client, test_user):
        """Test updating a user."""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@test.com",
            "roles": ["user", "moderator"],
            "groups": ["users", "moderators"]
        }
        
        response = authenticated_admin_client.put(
            f"/admin/users/{test_user['username']}", 
            json=update_data
        )
        assert response.status_code == 200
        user = response.json()
        assert user["first_name"] == "Updated"
        assert user["last_name"] == "Name"
        assert user["email"] == "updated@test.com"
        assert "user" in user["roles"]
        assert "moderator" in user["roles"]
        assert "users" in user["groups"]
        assert "moderators" in user["groups"]
    
    def test_delete_user(self, authenticated_admin_client):
        """Test deleting a user."""
        # Use unique username to avoid conflicts
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        username = f'deleteuser_{unique_id}'
        
        # First create a user to delete
        user_data = {
            "username": username,
            "first_name": "Delete",
            "last_name": "User",
            "password": "password123",
            "email": "delete@test.com",
            "roles": ["user"],
            "groups": ["users"]
        }
        
        create_response = authenticated_admin_client.post("/admin/users", json=user_data)
        assert create_response.status_code == 200
        
        # Now delete the user
        response = authenticated_admin_client.delete(f"/admin/users/{username}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify user is deleted
        get_response = authenticated_admin_client.get(f"/admin/users/{username}")
        assert get_response.status_code == 404
        
        # Cleanup
        cleanup_user_data(username)


class TestAdminRoleCRUD:
    """Test admin role CRUD operations."""
    
    def test_create_role(self, authenticated_admin_client):
        """Test creating a new role."""
        # Use unique role name to avoid conflicts
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        role_name = f'testrole_{unique_id}'
        
        role_data = {
            "role_name": role_name,
            "description": "Test role for testing"
        }
        
        response = authenticated_admin_client.post("/admin/roles", json=role_data)
        assert response.status_code == 200
        role = response.json()
        assert role["role_name"] == role_name
        assert role["description"] == "Test role for testing"
    
    def test_get_role(self, authenticated_admin_client):
        """Test getting a specific role."""
        # First create a role
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        role_name = f'getrole_{unique_id}'
        
        role_data = {
            "role_name": role_name,
            "description": "Role to get"
        }
        
        create_response = authenticated_admin_client.post("/admin/roles", json=role_data)
        assert create_response.status_code == 200
        created_role = create_response.json()
        role_id = created_role["id"]
        
        # Now get the role
        response = authenticated_admin_client.get(f"/admin/roles/{role_id}")
        assert response.status_code == 200
        role = response.json()
        assert role["role_name"] == role_name
        assert role["description"] == "Role to get"
    
    def test_update_role(self, authenticated_admin_client):
        """Test updating a role."""
        # First create a role
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        role_name = f'updaterole_{unique_id}'
        
        role_data = {
            "role_name": role_name,
            "description": "Role to update"
        }
        
        create_response = authenticated_admin_client.post("/admin/roles", json=role_data)
        assert create_response.status_code == 200
        created_role = create_response.json()
        role_id = created_role["id"]
        
        # Now update the role
        update_data = {
            "role_name": f"{role_name}_updated",
            "description": "Updated role description"
        }
        
        response = authenticated_admin_client.put(f"/admin/roles/{role_id}", json=update_data)
        assert response.status_code == 200
        role = response.json()
        assert role["role_name"] == f"{role_name}_updated"
        assert role["description"] == "Updated role description"
    
    def test_delete_role(self, authenticated_admin_client):
        """Test deleting a role."""
        # First create a role
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        role_name = f'deleterole_{unique_id}'
        
        role_data = {
            "role_name": role_name,
            "description": "Role to delete"
        }
        
        create_response = authenticated_admin_client.post("/admin/roles", json=role_data)
        assert create_response.status_code == 200
        created_role = create_response.json()
        role_id = created_role["id"]
        
        # Now delete the role
        response = authenticated_admin_client.delete(f"/admin/roles/{role_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify role is deleted
        get_response = authenticated_admin_client.get(f"/admin/roles/{role_id}")
        assert get_response.status_code == 404


class TestAdminGroupCRUD:
    """Test admin group CRUD operations."""
    
    def test_create_group(self, authenticated_admin_client):
        """Test creating a new group."""
        # Use unique group name to avoid conflicts
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        group_name = f'testgroup_{unique_id}'
        
        group_data = {
            "group_name": group_name,
            "description": "Test group for testing"
        }
        
        response = authenticated_admin_client.post("/admin/groups", json=group_data)
        assert response.status_code == 200
        group = response.json()
        assert group["group_name"] == group_name
        assert group["description"] == "Test group for testing"
    
    def test_get_group(self, authenticated_admin_client):
        """Test getting a specific group."""
        # First create a group
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        group_name = f'getgroup_{unique_id}'
        
        group_data = {
            "group_name": group_name,
            "description": "Group to get"
        }
        
        create_response = authenticated_admin_client.post("/admin/groups", json=group_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Now get the group
        response = authenticated_admin_client.get(f"/admin/groups/{group_id}")
        assert response.status_code == 200
        group = response.json()
        assert group["group_name"] == group_name
        assert group["description"] == "Group to get"
    
    def test_update_group(self, authenticated_admin_client):
        """Test updating a group."""
        # First create a group
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        group_name = f'updategroup_{unique_id}'
        
        group_data = {
            "group_name": group_name,
            "description": "Group to update"
        }
        
        create_response = authenticated_admin_client.post("/admin/groups", json=group_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Now update the group
        update_data = {
            "group_name": f"{group_name}_updated",
            "description": "Updated group description"
        }
        
        response = authenticated_admin_client.put(f"/admin/groups/{group_id}", json=update_data)
        assert response.status_code == 200
        group = response.json()
        assert group["group_name"] == f"{group_name}_updated"
        assert group["description"] == "Updated group description"
    
    def test_delete_group(self, authenticated_admin_client):
        """Test deleting a group."""
        # First create a group
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        group_name = f'deletegroup_{unique_id}'
        
        group_data = {
            "group_name": group_name,
            "description": "Group to delete"
        }
        
        create_response = authenticated_admin_client.post("/admin/groups", json=group_data)
        assert create_response.status_code == 200
        created_group = create_response.json()
        group_id = created_group["id"]
        
        # Now delete the group
        response = authenticated_admin_client.delete(f"/admin/groups/{group_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify group is deleted
        get_response = authenticated_admin_client.get(f"/admin/groups/{group_id}")
        assert get_response.status_code == 404


class TestAPIErrorHandling:
    """Test API error handling."""
    
    def test_404_not_found(self, authenticated_admin_client):
        """Test 404 error handling."""
        response = authenticated_admin_client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json(self, authenticated_admin_client):
        """Test invalid JSON handling."""
        response = authenticated_admin_client.post(
            "/cortex",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, authenticated_admin_client):
        """Test missing required fields handling."""
        response = authenticated_admin_client.post("/cortex", json={})
        assert response.status_code == 422
    
    def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints."""
        protected_endpoints = [
            ("POST", "/cortex"),
            ("GET", "/profile"),
            ("GET", "/admin/dashboard"),
            ("GET", "/admin/users"),
            ("GET", "/admin/roles"),
            ("GET", "/admin/groups")
        ]
    
        for method, endpoint in protected_endpoints:
            if method == "POST":
                response = client.post(endpoint, json={"message": "test"}, follow_redirects=False)
            else:
                response = client.get(endpoint, follow_redirects=False)
            # Should redirect to login page
            assert response.status_code == 302
            assert "/login" in response.headers["location"] 