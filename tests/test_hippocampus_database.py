"""
Tests for hippocampus.database
"""
import os
import pytest
import uuid
from hippocampus.user_database import ensure_user_database, delete_user_database, execute_user_query, get_database_connection
from hippocampus.database import get_base_instructions, query_personal_variables

def test_get_base_instructions():
    username = f"testbase_{uuid.uuid4().hex[:8]}"
    ensure_user_database(username)
    # The rise_and_shine table is read-only and contains default instructions
    instructions = get_base_instructions(username)
    print(f"DEBUG: get_base_instructions returned: {instructions}")
    # Check that default instructions are present and contain expected content
    assert len(instructions) >= 3  # Should have at least 3 default instructions
    assert any("Tatlock" in instr for instr in instructions)
    assert any("tool" in instr.lower() for instr in instructions)
    delete_user_database(username)

def test_query_personal_variables():
    username = f"testpv_{uuid.uuid4().hex[:8]}"
    ensure_user_database(username)
    
    # Use a single connection for the entire operation
    conn = get_database_connection(username)
    if not conn:
        pytest.fail("Failed to get database connection")
    
    cursor = conn.cursor()
    
    try:
        # Create tables first (they may not exist in the default schema)
        cursor.execute("CREATE TABLE IF NOT EXISTS personal_variables_keys (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS personal_variables (id INTEGER PRIMARY KEY AUTOINCREMENT, value TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS personal_variables_join (key_id INTEGER, variable_id INTEGER, PRIMARY KEY (key_id, variable_id), FOREIGN KEY (key_id) REFERENCES personal_variables_keys (id) ON DELETE CASCADE, FOREIGN KEY (variable_id) REFERENCES personal_variables (id) ON DELETE CASCADE)")
        
        # Clear any existing data
        cursor.execute("DELETE FROM personal_variables_join")
        cursor.execute("DELETE FROM personal_variables_keys")
        cursor.execute("DELETE FROM personal_variables")
        
        # Insert test data
        cursor.execute("INSERT INTO personal_variables_keys (key) VALUES (?)", ("nickname",))
        cursor.execute("INSERT INTO personal_variables (value) VALUES (?)", ("TatlockBot",))
        
        # Get the IDs for the join
        cursor.execute("SELECT id FROM personal_variables_keys WHERE key = ?", ("nickname",))
        key_id = cursor.fetchone()[0]
        cursor.execute("SELECT id FROM personal_variables WHERE value = ?", ("TatlockBot",))
        variable_id = cursor.fetchone()[0]
        
        # Create the join relationship
        cursor.execute("INSERT INTO personal_variables_join (key_id, variable_id) VALUES (?, ?)", (key_id, variable_id))
        
        # Commit the changes
        conn.commit()
        
        # Debug: check each table individually
        cursor.execute("SELECT id, key FROM personal_variables_keys")
        keys_data = [dict(row) for row in cursor.fetchall()]
        cursor.execute("SELECT id, value FROM personal_variables")
        values_data = [dict(row) for row in cursor.fetchall()]
        cursor.execute("SELECT key_id, variable_id FROM personal_variables_join")
        join_data = [dict(row) for row in cursor.fetchall()]
        print(f"DEBUG: Keys table: {keys_data}")
        print(f"DEBUG: Values table: {values_data}")
        print(f"DEBUG: Join table: {join_data}")
        
        # Test the query_personal_variables function
        results = query_personal_variables("nickname", username)
        print(f"DEBUG: query_personal_variables returned: {results}")
        assert any(r["value"] == "TatlockBot" for r in results)
        
    finally:
        conn.close()
        delete_user_database(username) 