#!/usr/bin/env bash
# install_tatlock.sh
# CLI installer for Tatlock: sets up system dependencies, Python packages, 
# Ollama LLM, Material Icons, and initializes databases with authentication.

set -e

# --- Instructions ---
echo "Tatlock Installation Script"
echo "--------------------------"
echo "This script will:"
echo "1. Install required system packages via apt (Python 3, pip, sqlite3, build tools)"
echo "2. Install and configure Ollama with the Gemma3-enhanced model"
echo "3. Install Python dependencies from requirements.txt"
echo "4. Download Material Icons for offline web interface"
echo "5. Initialize system.db and longterm.db with authentication and memory tables"
echo "6. Create default roles, groups, and system prompts"
echo "7. Optionally create a new admin account if one does not exist yet"
echo ""
echo "You may be prompted for your password to install system packages."
echo ""

# --- Install system dependencies ---
echo "[1/4] Installing system dependencies via apt..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv sqlite3 build-essential curl

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "Ollama is already installed, skipping installation."
else
    echo "Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

echo "Starting Ollama service..."
sudo systemctl enable ollama
sudo systemctl start ollama

# Check if the model is already installed
if ollama list | grep -q "gemma3-cortex:latest"; then
    echo "Gemma3 model is already installed, skipping download."
else
    echo "Downloading and setting up Gemma3 model..."
    ollama pull ebdm/gemma3-enhanced:12b
    ollama cp ebdm/gemma3-enhanced:12b gemma3-cortex:latest
    ollama rm ebdm/gemma3-enhanced:12b
fi

echo "[2/4] Installing Python dependencies..."
pip3 install -r requirements.txt

# --- Download Material Icons for offline use ---
echo "[3/6] Downloading Material Icons for offline web interface..."
mkdir -p static/fonts
cd static/fonts
wget -O material-icons.woff2 "https://fonts.gstatic.com/s/materialicons/v140/flUhRq6tzZclQEJ-Vdg-IuiaDsNcIhQ8tQ.woff2"
wget -O material-icons.woff "https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/fonts/materialdesignicons-webfont.woff"
wget -O material-icons.ttf "https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/fonts/materialdesignicons-webfont.ttf"
cd ../..

# --- Initialize databases ---
echo "[4/6] Initializing databases..."
PYTHONPATH=. python3 -c "from stem.installation.database_setup import create_system_db_tables; create_system_db_tables('hippocampus/system.db')"

echo "- system.db is ready in the hippocampus/ directory. User memory databases will be created automatically when users are added."

# --- Create admin user if not exists ---
echo "[5/6] Checking for admin account..."
        # Check if admin user already exists
        admin_exists=$(PYTHONPATH=. python3 -c "from stem.security import security_manager; print('yes' if security_manager.authenticate_user('admin', 'breaker') else 'no')")
if [ "$admin_exists" = "no" ]; then
    echo "No admin account found. Let's create one."
    read -p "Enter admin username [admin]: " admin_user
    admin_user=${admin_user:-admin}
    read -p "First name [Administrator]: " admin_first
    admin_first=${admin_first:-Administrator}
    read -p "Last name [User]: " admin_last
    admin_last=${admin_last:-User}
    read -p "Email [admin@tatlock.local]: " admin_email
    admin_email=${admin_email:-admin@tatlock.local}
    read -s -p "Password: " admin_pass
    echo
    read -s -p "Confirm Password: " admin_pass2
    echo
    if [ "$admin_pass" != "$admin_pass2" ]; then
        echo "Passwords do not match. Exiting."
        exit 1
    fi
    PYTHONPATH=. python3 -c "
from stem.security import security_manager
if security_manager.create_user('$admin_user', '$admin_first', '$admin_last', '$admin_pass', '$admin_email'):
    security_manager.add_user_to_role('$admin_user', 'user')
    security_manager.add_user_to_role('$admin_user', 'admin')
    security_manager.add_user_to_group('$admin_user', 'users')
    security_manager.add_user_to_group('$admin_user', 'admins')
    print('Admin user created and configured.')
else:
    print('Failed to create admin user.')
"
else
    echo "Admin account already exists."
fi

echo ""
echo "Tatlock installation complete!"
echo "- Ollama with Gemma3-enhanced model is ready"
echo "- Material Icons downloaded for offline web interface"
echo "- system.db and longterm.db are ready in the hippocampus/ directory"
echo "- Default roles, groups, and system prompts are configured"
echo "- You can now run the application as described in the README"
echo ""
echo "If you need to re-run this script, it is safe to do so (tables will not be duplicated)." 