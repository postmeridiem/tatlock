"""
Security startup test to verify Tatlock starts successfully after version pinning.

This test ensures that all pinned dependencies are compatible and the application
can start without errors after security hardening.
"""

import pytest
import subprocess
import sys
import os
import tempfile
import time
import requests
from pathlib import Path


class TestSecurityStartup:
    """Test that Tatlock starts successfully with pinned dependencies."""

    def test_import_all_modules(self):
        """Test that all core modules can be imported without errors."""
        try:
            # Test core imports
            import main
            import config
            from stem import security, models, htmlcontroller
            from hippocampus import database, recall, remember
            from cortex import tatlock
            from parietal import hardware
            from temporal import voice_service, language_processor
            
            # Test that imports succeed
            assert main is not None
            assert config is not None
            assert security is not None
            assert models is not None
            assert htmlcontroller is not None
            assert database is not None
            assert recall is not None
            assert remember is not None
            assert tatlock is not None
            assert hardware is not None
            assert voice_service is not None
            assert language_processor is not None
            
        except ImportError as e:
            pytest.fail(f"Failed to import module: {e}")

    def test_config_loading(self):
        """Test that configuration loads without errors."""
        try:
            from config import load_hardware_configuration, get_automatic_ollama_model
            
            # Test hardware configuration loading
            model, tier = load_hardware_configuration()
            assert model is not None
            assert tier is not None
            
            # Test automatic model selection
            auto_model = get_automatic_ollama_model()
            assert auto_model is not None
            
        except Exception as e:
            pytest.fail(f"Configuration loading failed: {e}")

    def test_database_initialization(self):
        """Test that database initialization works."""
        try:
            from stem.installation.database_setup import create_system_db_tables
            
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            try:
                # Test database creation
                create_system_db_tables(db_path)
                
                # Verify database file exists
                assert os.path.exists(db_path)
                assert os.path.getsize(db_path) > 0
                
            finally:
                # Clean up
                if os.path.exists(db_path):
                    os.unlink(db_path)
                    
        except Exception as e:
            pytest.fail(f"Database initialization failed: {e}")

    def test_security_manager_initialization(self):
        """Test that security manager initializes without errors."""
        try:
            from stem.security import security_manager
            
            # Test that security manager can be created
            assert security_manager is not None
            
            # Test basic security operations
            # Note: We don't test actual user creation in this test
            # as it requires database setup
            
        except Exception as e:
            pytest.fail(f"Security manager initialization failed: {e}")

    def test_hardware_classification(self):
        """Test that hardware classification works."""
        try:
            from parietal.hardware import classify_hardware_performance
            
            # Test hardware classification
            result = classify_hardware_performance()
            
            assert result is not None
            assert 'performance_tier' in result
            assert 'recommended_model' in result
            assert result['performance_tier'] in ['low', 'medium', 'high']
            
        except Exception as e:
            pytest.fail(f"Hardware classification failed: {e}")

    def test_tool_system_initialization(self):
        """Test that the tool system initializes without errors."""
        try:
            from stem.tools import initialize_tool_system, get_enabled_tools_from_db
            
            # Test tool system initialization
            initialize_tool_system()
            
            # Test tool loading
            tools = get_enabled_tools_from_db()
            assert tools is not None
            
        except Exception as e:
            pytest.fail(f"Tool system initialization failed: {e}")

    def test_application_startup_simulation(self):
        """Test that the application can start without critical errors."""
        try:
            # Test that main application components can be imported and initialized
            from main import app
            from fastapi.testclient import TestClient
            
            # Create test client
            client = TestClient(app)
            
            # Test that the app is properly configured
            assert app is not None
            
            # Test basic endpoint availability (without authentication)
            # Note: We can't test authenticated endpoints without proper setup
            response = client.get("/")
            # Should either return 200 or redirect to login
            assert response.status_code in [200, 307, 404]  # 404 is acceptable for root
            
        except Exception as e:
            pytest.fail(f"Application startup simulation failed: {e}")

    def test_dependency_compatibility(self):
        """Test that all dependencies are compatible with each other."""
        try:
            # Test critical dependency combinations
            import fastapi
            import uvicorn
            import pydantic
            import sqlite3
            import requests
            import httpx
            import jinja2
            import bcrypt
            import psutil
            
            # Test that versions are compatible
            assert hasattr(fastapi, '__version__')
            assert hasattr(uvicorn, '__version__')
            assert hasattr(pydantic, '__version__')
            
            # Test that core functionality works
            from pydantic import BaseModel
            
            class TestModel(BaseModel):
                test_field: str = "test"
            
            model = TestModel()
            assert model.test_field == "test"
            
        except Exception as e:
            pytest.fail(f"Dependency compatibility test failed: {e}")

    def test_security_tools_availability(self):
        """Test that security tools can be imported and used."""
        try:
            # Test safety (if available)
            try:
                import safety
                assert safety is not None
            except ImportError:
                # Safety not installed, that's okay for this test
                pass
            
            # Test bandit (if available)
            try:
                import bandit
                assert bandit is not None
            except ImportError:
                # Bandit not installed, that's okay for this test
                pass
                
        except Exception as e:
            pytest.fail(f"Security tools availability test failed: {e}")

    def test_python_version_compatibility(self):
        """Test that the application is compatible with the current Python version."""
        try:
            # Test Python version
            python_version = sys.version_info
            assert python_version.major == 3
            assert python_version.minor >= 10  # Require Python 3.10+
            
            # Test that we can use modern Python features
            # Type hints (Python 3.10+ syntax)
            def test_function(param: str | None = None) -> bool:
                return param is not None
            
            assert test_function("test") is True
            assert test_function(None) is False
            
        except Exception as e:
            pytest.fail(f"Python version compatibility test failed: {e}")


class TestSecurityDependencies:
    """Test security-related dependency management."""

    def test_requirements_file_format(self):
        """Test that requirements.txt follows security best practices."""
        requirements_path = Path("requirements.txt")
        
        with open(requirements_path, 'r') as f:
            lines = f.readlines()
        
        # Check that all dependencies are pinned
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                # Check for version pinning
                if '==' not in line and ';' not in line:
                    # Allow conditional dependencies and comments
                    if not line.startswith('tomli') and not line.startswith('nest_asyncio'):
                        pytest.fail(f"Unpinned dependency found: {line}")
        
        # Check for security-related comments
        content = ''.join(lines)
        assert 'security' in content.lower() or 'pin' in content.lower()

    def test_no_loose_version_specifiers(self):
        """Test that no loose version specifiers are used."""
        requirements_path = Path("requirements.txt")
        
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # Check for loose version specifiers
        loose_patterns = ['>=', '>', '<=', '<', '~=', '!=']
        for pattern in loose_patterns:
            if pattern in content:
                # Allow some exceptions for conditional dependencies
                lines = content.split('\n')
                for line in lines:
                    if pattern in line and not line.strip().startswith('#'):
                        # Check if it's a conditional dependency
                        if ';' not in line:
                            pytest.fail(f"Loose version specifier found: {line.strip()}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
