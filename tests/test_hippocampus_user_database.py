"""
Tests for hippocampus.user_database
"""
import os
import sqlite3
import pytest
from hippocampus.user_database import (
    get_user_database_path,
    ensure_user_database,
    delete_user_database,
    get_database_connection,
    execute_user_query
)
from stem.installation.database_setup import create_longterm_db_tables

def test_get_user_database_path():
    path = get_user_database_path("alice")
    assert path.endswith("hippocampus/longterm/alice.db")

def test_ensure_and_delete_user_database():
    username = "testuser"
    db_path = get_user_database_path(username)
    # Ensure DB does not exist
    if os.path.exists(db_path):
        os.remove(db_path)
    # Create DB
    created_path = ensure_user_database(username)
    assert os.path.exists(created_path)
    # Delete DB
    assert delete_user_database(username) is True
    assert not os.path.exists(db_path)

def test_get_database_connection_and_execute_query():
    username = "testuser2"
    db_path = ensure_user_database(username)
    conn = get_database_connection(username)
    assert isinstance(conn, sqlite3.Connection)
    # Insert and query using personal_variables table which exists in user databases
    cursor = conn.cursor()
    cursor.execute("INSERT INTO personal_variables_keys (key) VALUES (?)", ("test_key",))
    cursor.execute("INSERT INTO personal_variables (value) VALUES (?)", ("test_value",))
    conn.commit()
    conn.close()
    # Use execute_user_query
    results = execute_user_query(username, "SELECT key FROM personal_variables_keys WHERE key = 'test_key'")
    assert any(r["key"] == "test_key" for r in results)
    # Cleanup
    delete_user_database(username) 