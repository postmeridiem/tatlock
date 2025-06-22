#!/usr/bin/env bash
# reset_password.sh
# CLI script to reset user passwords in Tatlock system database.

set -e

# Color definitions
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# --- Display Tatlock ASCII Art Logo ---
echo -e "${BOLD}${CYAN}"
echo "══════════════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "               ████████╗ █████╗ ████████╗██╗      ██████╗  ██████╗██╗  ██╗"
echo "               ╚══██╔══╝██╔══██╗╚══██╔══╝██║     ██╔═══██╗██╔════╝██║ ██╔╝"
echo "                  ██║   ███████║   ██║   ██║     ██║   ██║██║     █████╔╝ "
echo "                  ██║   ██╔══██║   ██║   ██║     ██║   ██║██║     ██╔═██╗ "
echo "                  ██║   ██║  ██║   ██║   ███████╗╚██████╔╝╚██████╗██║  ██╗"
echo "                  ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝"
echo ""
echo "                          Brain-Inspired Home Automation Butler"
echo "══════════════════════════════════════════════════════════════════════════════════════════"
echo -e "${NC}"
echo ""

# --- Check if we're in the correct directory ---
# Check if we're in the root directory or stem directory
if [ -f "main.py" ] && [ -d "stem" ] && [ -d "hippocampus" ]; then
    # We're in the root directory
    PROJECT_ROOT="."
elif [ -f "../main.py" ] && [ -d "../stem" ] && [ -d "../hippocampus" ]; then
    # We're in the stem directory
    PROJECT_ROOT=".."
else
    echo -e "${RED}Error: This script must be run from the Tatlock project root directory or the stem/ directory.${NC}"
    echo -e "Please ensure you're in the directory containing main.py, stem/, and hippocampus/ folders, or in the stem/ directory."
    exit 1
fi

# --- Instructions ---
echo -e "${BOLD}${CYAN}"
echo "══════════════════════════════════════════════════════════════════════════════════════════"
echo "                        Tatlock Password Reset Script                                     "
echo "                    Reset user passwords in the system database                          "
echo "══════════════════════════════════════════════════════════════════════════════════════════"
echo -e "${NC}"

echo -e "${BOLD}This script will perform the following steps:${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo -e "  ${GREEN}1.${NC} Get username and new password${NC}"
echo -e "  ${GREEN}2.${NC} Update password in database${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo ""

# --- Get username input ---
echo -e "${BOLD}${CYAN}User Information:${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"

read -p "Enter username to reset password for: " username

if [ -z "$username" ]; then
    echo -e "${RED}Error: Username cannot be empty.${NC}"
    exit 1
fi

# --- Get new password input ---
echo -e "${BLUE}[1/2] Setting new password...${NC}"

# Get password with confirmation
while true; do
    read -s -p "Enter new password: " password
    echo
    read -s -p "Confirm new password: " password_confirm
    echo
    
    if [ "$password" != "$password_confirm" ]; then
        echo -e "${RED}Error: Passwords do not match. Please try again.${NC}"
        continue
    fi
    
    if [ -z "$password" ]; then
        echo -e "${RED}Error: Password cannot be empty.${NC}"
        continue
    fi
    
    break
done

# --- Update password in database ---
echo -e "${BLUE}[2/2] Updating password in database...${NC}"

# Activate virtual environment and update password
update_result=$(source $PROJECT_ROOT/.venv/bin/activate && python3 -c "
import sqlite3
import bcrypt
import sys

try:
    # Hash the password
    password = '$password'
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    # Update the password in the database
    conn = sqlite3.connect('$PROJECT_ROOT/hippocampus/system.db')
    cursor = conn.cursor()
    
    # Check if password entry exists
    cursor.execute('SELECT username FROM passwords WHERE username = ?', ('$username',))
    exists = cursor.fetchone()
    
    if exists:
        # Update existing password
        cursor.execute('''
            UPDATE passwords 
            SET password_hash = ?, salt = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE username = ?
        ''', (password_hash.decode('utf-8'), salt.decode('utf-8'), '$username'))
    else:
        # Insert new password entry
        cursor.execute('''
            INSERT INTO passwords (username, password_hash, salt, created_at, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', ('$username', password_hash.decode('utf-8'), salt.decode('utf-8')))
    
    conn.commit()
    conn.close()
    
    print('SUCCESS')
except Exception as e:
    print('ERROR: ' + str(e))
    sys.exit(1)
" 2>&1)

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to update password.${NC}"
    echo -e "Database error: $update_result"
    exit 1
fi

echo -e "${GREEN}[✓]${NC} Password updated successfully"

# --- Success message ---
echo ""
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${GREEN}                                    Password Reset Complete!                              ${NC}"
echo -e "${BOLD}${GREEN}══════════════════════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}The password for user '$username' has been successfully reset.${NC}"
echo "" 