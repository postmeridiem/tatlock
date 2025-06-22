#!/usr/bin/env python3
"""
Test login script to diagnose authentication issues.
"""

import sqlite3
import bcrypt
import sys
import os

def test_login(username, password, db_path='hippocampus/system.db'):
    """Test login process and diagnose issues."""
    print(f"Testing login for user '{username}' with database: {db_path}")
    print("=" * 60)
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Users table not found")
            return False
        
        # Check if passwords table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='passwords'")
        if not cursor.fetchone():
            print("❌ Passwords table not found")
            return False
        
        print("✅ Database and tables exist")
        
        # Check if user exists in users table
        cursor.execute("SELECT username, first_name, last_name, email FROM users WHERE username = ?", (username,))
        user_data = cursor.fetchone()
        
        if not user_data:
            print(f"❌ User '{username}' not found in users table")
            return False
        
        print(f"✅ User found in users table: {user_data}")
        
        # Check if password exists in passwords table
        cursor.execute("SELECT username, password_hash, salt FROM passwords WHERE username = ?", (username,))
        password_data = cursor.fetchone()
        
        if not password_data:
            print(f"❌ Password entry not found for user '{username}' in passwords table")
            return False
        
        print(f"✅ Password entry found in passwords table")
        print(f"   Hash: {password_data[1][:20]}...")
        print(f"   Salt: {password_data[2][:20]}...")
        
        # Try to verify the password
        stored_hash = password_data[1]
        stored_salt = password_data[2]
        
        try:
            # Hash the provided password with the stored salt
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                print("✅ Password verification successful!")
                return True
            else:
                print("❌ Password verification failed")
                print(f"   Provided password: '{password}'")
                print(f"   Stored hash: {stored_hash}")
                
                # Let's also try hashing the password fresh to see what we get
                fresh_salt = bcrypt.gensalt()
                fresh_hash = bcrypt.hashpw(password.encode('utf-8'), fresh_salt)
                print(f"   Fresh hash for same password: {fresh_hash.decode('utf-8')}")
                
                return False
                
        except Exception as e:
            print(f"❌ Error during password verification: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def check_database_schema(db_path='hippocampus/system.db'):
    """Check the database schema to see what tables and columns exist."""
    print(f"\nChecking database schema for: {db_path}")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Tables found: {[table[0] for table in tables]}")
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users)")
        user_columns = cursor.fetchall()
        print(f"\nUsers table columns:")
        for col in user_columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check passwords table structure
        cursor.execute("PRAGMA table_info(passwords)")
        password_columns = cursor.fetchall()
        print(f"\nPasswords table columns:")
        for col in password_columns:
            print(f"  {col[1]} ({col[2]})")
        
        # Check migrations table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'")
        if cursor.fetchone():
            cursor.execute("SELECT * FROM migrations")
            migrations = cursor.fetchall()
            print(f"\nApplied migrations:")
            for migration in migrations:
                print(f"  {migration[1]} - {migration[2]}")
        else:
            print("\nNo migrations table found")
        
    except Exception as e:
        print(f"❌ Error checking schema: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/test_login.py <username> <password> [db_path]")
        print("Example: python scripts/test_login.py admin admin123")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    db_path = sys.argv[3] if len(sys.argv) > 3 else 'hippocampus/system.db'
    
    print("🔍 Tatlock Login Diagnostic Tool")
    print("=" * 60)
    
    # Check database schema first
    check_database_schema(db_path)
    
    # Test the login
    success = test_login(username, password, db_path)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Login test PASSED - authentication should work")
    else:
        print("💥 Login test FAILED - authentication will not work")
        print("\nPossible issues:")
        print("1. User doesn't exist in users table")
        print("2. Password entry missing from passwords table")
        print("3. Password hash/salt corrupted")
        print("4. Migration not applied correctly")
        print("\nTry running: ./stem/reset_password.sh")

if __name__ == "__main__":
    main() 