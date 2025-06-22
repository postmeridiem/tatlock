"""
tests/test_cleanup.py

Cleanup utilities for test artifacts and temporary files.
"""

import os
import shutil
import sqlite3
from pathlib import Path

def cleanup_test_databases():
    """Remove all test database files."""
    test_dirs = [
        "hippocampus/longterm",
        "hippocampus/shortterm",
        "tests/.pytest_cache",
        "tests/.coverage"
    ]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            if os.path.isdir(test_dir):
                shutil.rmtree(test_dir)
            else:
                os.remove(test_dir)
            print(f"Cleaned up: {test_dir}")

def cleanup_test_files():
    """Remove test-specific files."""
    test_files = [
        "tatlock.log",
        "tests/test_output.txt",
        "tests/test_cookies.txt"
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"Cleaned up: {test_file}")

def cleanup_python_cache():
    """Remove Python cache files."""
    cache_dirs = []
    
    # Find all __pycache__ directories
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_dirs.append(os.path.join(root, dir_name))
    
    for cache_dir in cache_dirs:
        shutil.rmtree(cache_dir)
        print(f"Cleaned up: {cache_dir}")

def cleanup_test_screenshots():
    """Remove test screenshot directories."""
    screenshot_dirs = [
        "test_screenshots",
        "test_baselines", 
        "test_comparisons"
    ]
    
    for screenshot_dir in screenshot_dirs:
        if os.path.exists(screenshot_dir):
            shutil.rmtree(screenshot_dir)
            print(f"Cleaned up: {screenshot_dir}")

def cleanup_user_databases():
    """Remove user-specific test databases."""
    longterm_dir = Path("hippocampus/longterm")
    if longterm_dir.exists():
        for db_file in longterm_dir.glob("*.db"):
            if "test" in db_file.name or "admin_" in db_file.name:
                db_file.unlink()
                print(f"Cleaned up user database: {db_file}")

def cleanup_all():
    """Perform comprehensive cleanup of all test artifacts."""
    print("Starting comprehensive test cleanup...")
    
    cleanup_test_databases()
    cleanup_test_files()
    cleanup_python_cache()
    cleanup_test_screenshots()
    cleanup_user_databases()
    
    print("Test cleanup completed!")

if __name__ == "__main__":
    cleanup_all() 