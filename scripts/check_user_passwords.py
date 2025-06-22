import sqlite3
import sys
import os
import hashlib
import secrets

DB_PATH = os.environ.get('TATLOCK_SYSTEM_DB', 'hippocampus/system.db')

def check_user_password(username, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print(f"Checking user '{username}' in database: {db_path}\n")

    # Check users table
    cursor.execute("SELECT username, first_name, last_name, email, created_at FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user:
        print("[users] table entry:")
        print(f"  username:   {user[0]}")
        print(f"  first_name: {user[1]}")
        print(f"  last_name:  {user[2]}")
        print(f"  email:      {user[3]}")
        print(f"  created_at: {user[4]}")
    else:
        print("[users] table entry: NOT FOUND")

    # Check passwords table
    cursor.execute("SELECT username, password_hash, salt, created_at FROM passwords WHERE username = ?", (username,))
    pw = cursor.fetchone()
    if pw:
        print("\n[passwords] table entry:")
        print(f"  username:      {pw[0]}")
        print(f"  password_hash: {pw[1]}")
        print(f"  salt:          {pw[2]}")
        print(f"  created_at:    {pw[3]}")
    else:
        print("\n[passwords] table entry: NOT FOUND")

    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/check_user_passwords.py <username> [db_path]")
        sys.exit(1)
    username = sys.argv[1]
    db_path = sys.argv[2] if len(sys.argv) > 2 else DB_PATH
    check_user_password(username, db_path) 