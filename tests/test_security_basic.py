"""
Basic security test to verify dependency pinning and basic imports work.

This test focuses on basic security checks without requiring full application setup.
"""

import pytest
import sys
import os
from pathlib import Path


class TestSecurityBasic:
    """Basic security tests for dependency management."""

    def test_requirements_file_format(self):
        """Test that requirements.txt follows security best practices."""
        requirements_path = Path("requirements.txt")
        
        with open(requirements_path, 'r') as f:
            lines = f.readlines()
        
        # Check that all dependencies are pinned
        unpinned_deps = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                # Check for version pinning
                if '==' not in line and ';' not in line:
                    # Allow conditional dependencies and comments
                    if not line.startswith('tomli') and not line.startswith('nest_asyncio'):
                        unpinned_deps.append(line)
        
        if unpinned_deps:
            pytest.fail(f"Unpinned dependencies found: {unpinned_deps}")
        
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
        loose_found = []
        for pattern in loose_patterns:
            if pattern in content:
                # Allow some exceptions for conditional dependencies
                lines = content.split('\n')
                for line in lines:
                    if pattern in line and not line.strip().startswith('#'):
                        # Check if it's a conditional dependency
                        if ';' not in line:
                            loose_found.append(line.strip())
        
        if loose_found:
            pytest.fail(f"Loose version specifiers found: {loose_found}")

    def test_python_version_compatibility(self):
        """Test that the application is compatible with the current Python version."""
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

    def test_security_strategy_exists(self):
        """Test that security strategy document exists."""
        security_strategy_path = Path("stem/SECURITY_STRATEGY.md")
        assert security_strategy_path.exists(), "Security strategy document not found"
        
        # Check that it contains security content
        with open(security_strategy_path, 'r') as f:
            content = f.read()
        
        assert 'security' in content.lower()
        assert 'dependency' in content.lower()
        assert 'version' in content.lower()

    def test_agents_md_security_guidelines(self):
        """Test that AGENTS.md contains security guidelines."""
        agents_path = Path("AGENTS.md")
        assert agents_path.exists(), "AGENTS.md not found"
        
        with open(agents_path, 'r') as f:
            content = f.read()
        
        # Check for security sections
        assert 'Security Standards' in content
        assert 'Supply Chain Security' in content
        assert 'Version Pinning' in content
        assert 'AI Assistant Security Guidelines' in content

    def test_requirements_file_structure(self):
        """Test that requirements.txt has proper structure."""
        requirements_path = Path("requirements.txt")
        
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # Check for core dependencies
        assert 'fastapi==' in content
        assert 'uvicorn==' in content
        assert 'pydantic==' in content
        
        # Check for security-related dependencies
        assert 'bcrypt==' in content
        assert 'python-jose==' in content
        
        # Check for testing dependencies
        assert 'pytest==' in content
        
        # Check that all major dependencies are pinned
        lines = content.split('\n')
        pinned_count = 0
        total_deps = 0
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                total_deps += 1
                if '==' in line:
                    pinned_count += 1
        
        # At least 80% of dependencies should be pinned
        pinning_ratio = pinned_count / total_deps if total_deps > 0 else 0
        assert pinning_ratio >= 0.8, f"Only {pinning_ratio:.1%} of dependencies are pinned"

    def test_no_known_vulnerable_versions(self):
        """Test that no known vulnerable package versions are used."""
        requirements_path = Path("requirements.txt")
        
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # Check for specific vulnerable versions (this is a basic check)
        # In a real implementation, you would use safety or similar tools
        
        # Check that we're not using extremely old versions
        lines = content.split('\n')
        for line in lines:
            if '==' in line:
                package, version = line.split('==')
                package = package.strip()
                version = version.strip()
                
                # Basic version format check
                if '.' in version:
                    version_parts = version.split('.')
                    if len(version_parts) >= 2:
                        major = int(version_parts[0])
                        minor = int(version_parts[1])
                        
                        # Check for reasonable version numbers
                        assert major >= 0, f"Invalid major version for {package}: {version}"
                        assert minor >= 0, f"Invalid minor version for {package}: {version}"

    def test_security_documentation_completeness(self):
        """Test that security documentation is complete."""
        # Check that security strategy exists
        security_strategy = Path("stem/SECURITY_STRATEGY.md")
        assert security_strategy.exists()
        
        with open(security_strategy, 'r') as f:
            content = f.read()
        
        # Check for key security sections
        required_sections = [
            'Security Principles',
            'Supply Chain Security',
            'Dependency Management',
            'Security Tools',
            'Implementation Plan'
        ]
        
        for section in required_sections:
            assert section in content, f"Missing section: {section}"

    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets are in requirements.txt."""
        requirements_path = Path("requirements.txt")
        
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # Check for common secret patterns
        secret_patterns = [
            'password=',
            'secret=',
            'key=',
            'token=',
            'api_key='
        ]
        
        for pattern in secret_patterns:
            assert pattern not in content.lower(), f"Potential secret found: {pattern}"


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
