#!/usr/bin/env bash
# install_tatlock.sh
# CLI installer for Tatlock: sets up system dependencies, Python packages, 
# Ollama LLM, Material Icons, and initializes databases with authentication.

set -e

# --- Instructions ---
echo "Tatlock Installation Script"
echo "--------------------------"
echo "This script will:"
echo "1. Install required system packages (Python 3, pip, sqlite3, build tools)"
echo "2. Install and configure Ollama with the Gemma3-enhanced model"
echo "3. Install Python dependencies from requirements.txt"
echo "4. Create .env configuration file with auto-generated secret key (safely handles existing files)"
echo "5. Download Material Icons for offline web interface"
echo "6. Initialize system.db and longterm.db with authentication and memory tables"
echo "7. Create default roles, groups, and system prompts"
echo "8. Optionally create a new admin account if one does not exist yet"
echo ""

# --- Detect system and package manager ---
detect_system() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if [[ $(uname -m) == "arm64" ]]; then
            SYSTEM="macos_arm"
            PACKAGE_MANAGER="brew"
        else
            SYSTEM="macos_intel"
            PACKAGE_MANAGER="brew"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            case $ID in
                "ubuntu"|"debian"|"linuxmint"|"zorin")
                    SYSTEM="debian"
                    PACKAGE_MANAGER="apt"
                    ;;
                "centos"|"rhel"|"fedora"|"rocky"|"almalinux")
                    SYSTEM="rhel"
                    PACKAGE_MANAGER="yum"
                    ;;
                "arch"|"manjaro")
                    SYSTEM="arch"
                    PACKAGE_MANAGER="pacman"
                    ;;
                *)
                    SYSTEM="unknown"
                    PACKAGE_MANAGER="unknown"
                    ;;
            esac
        else
            SYSTEM="unknown"
            PACKAGE_MANAGER="unknown"
        fi
    else
        SYSTEM="unknown"
        PACKAGE_MANAGER="unknown"
    fi
}

detect_system

echo "Detected system: $SYSTEM"
echo "Package manager: $PACKAGE_MANAGER"
echo ""

# --- Check if package manager is available ---
check_package_manager() {
    case $PACKAGE_MANAGER in
        "apt")
            if ! command -v apt &> /dev/null; then
                echo "Error: apt package manager not found."
                exit 1
            fi
            ;;
        "yum")
            if ! command -v yum &> /dev/null; then
                echo "Error: yum package manager not found."
                exit 1
            fi
            ;;
        "brew")
            if ! command -v brew &> /dev/null; then
                echo "Error: Homebrew not found. Please install Homebrew first:"
                echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            ;;
        "pacman")
            if ! command -v pacman &> /dev/null; then
                echo "Error: pacman package manager not found."
                exit 1
            fi
            ;;
        *)
            echo "Error: Unsupported system or package manager not detected."
            echo "Please install dependencies manually or use a supported system."
            exit 1
            ;;
    esac
}

check_package_manager

# --- Install system dependencies ---
echo "[1/7] Installing system dependencies..."

install_system_dependencies() {
    case $PACKAGE_MANAGER in
        "apt")
            echo "Using apt package manager..."
            
            # Clean up any problematic repositories first
            echo "Cleaning up package lists..."
            sudo apt clean
            sudo rm -f /var/lib/apt/lists/lock
            sudo rm -f /var/cache/apt/archives/lock
            sudo rm -f /var/lib/dpkg/lock*
            
            # Update package lists with error handling
            echo "Updating package lists..."
            if ! sudo apt update; then
                echo "Warning: Package list update failed. This might be due to repository issues."
                echo "Attempting to continue with existing package lists..."
            fi
            
            # Install packages with error handling
            echo "Installing required packages..."
            if ! sudo apt install -y python3 python3-pip python3-venv sqlite3 build-essential curl wget; then
                echo "Error: Failed to install required packages."
                echo "Please check your package manager configuration and try again."
                exit 1
            fi
            ;;
            
        "yum")
            echo "Using yum package manager..."
            
            # Update package lists
            echo "Updating package lists..."
            if ! sudo yum update -y; then
                echo "Warning: Package list update failed. Attempting to continue..."
            fi
            
            # Install packages
            echo "Installing required packages..."
            if ! sudo yum install -y python3 python3-pip sqlite gcc gcc-c++ make curl wget; then
                echo "Error: Failed to install required packages."
                echo "Please check your package manager configuration and try again."
                exit 1
            fi
            ;;
            
        "brew")
            echo "Using Homebrew package manager..."
            
            # Update Homebrew
            echo "Updating Homebrew..."
            if ! brew update; then
                echo "Warning: Homebrew update failed. Attempting to continue..."
            fi
            
            # Install packages
            echo "Installing required packages..."
            if ! brew install python sqlite curl wget; then
                echo "Error: Failed to install required packages."
                echo "Please check your Homebrew installation and try again."
                exit 1
            fi
            
            # On macOS, we need to ensure we're using the Homebrew Python
            if [[ "$SYSTEM" == "macos_arm" ]]; then
                echo "Setting up Python for Apple Silicon..."
                # Add Homebrew Python to PATH if not already there
                if ! command -v python3 &> /dev/null; then
                    echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
                    export PATH="/opt/homebrew/bin:$PATH"
                fi
            fi
            ;;
            
        "pacman")
            echo "Using pacman package manager..."
            
            # Update package lists
            echo "Updating package lists..."
            if ! sudo pacman -Sy; then
                echo "Warning: Package list update failed. Attempting to continue..."
            fi
            
            # Install packages
            echo "Installing required packages..."
            if ! sudo pacman -S --noconfirm python python-pip sqlite base-devel curl wget; then
                echo "Error: Failed to install required packages."
                echo "Please check your package manager configuration and try again."
                exit 1
            fi
            ;;
    esac
}

install_system_dependencies

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "Ollama is already installed, skipping installation."
else
    echo "Installing Ollama..."
    if ! curl -fsSL https://ollama.ai/install.sh | sh; then
        echo "Error: Failed to install Ollama."
        echo "Please check your internet connection and try again."
        exit 1
    fi
fi

# Start Ollama service (different for different systems)
echo "Starting Ollama service..."
if [[ "$SYSTEM" == "macos_arm" || "$SYSTEM" == "macos_intel" ]]; then
    # On macOS, Ollama runs as a user service
    ollama serve &> /dev/null &
    echo "Ollama service started in background on macOS."
else
    # On Linux, use systemctl
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable ollama
        sudo systemctl start ollama
    else
        echo "Warning: systemctl not found. Ollama may need to be started manually."
    fi
fi

# Check if the model is already installed
if ollama list | grep -q "gemma3-cortex:latest"; then
    echo "Gemma3 model is already installed, skipping download."
else
    echo "Downloading and setting up Gemma3 model..."
    if ! ollama pull ebdm/gemma3-enhanced:12b; then
        echo "Error: Failed to download Gemma3 model."
        echo "Please check your internet connection and try again."
        exit 1
    fi
    ollama cp ebdm/gemma3-enhanced:12b gemma3-cortex:latest
    ollama rm ebdm/gemma3-enhanced:12b
fi

echo "[2/7] Installing Python dependencies..."

# Use the appropriate pip command
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "Error: pip not found. Please install Python and pip first."
    exit 1
fi

if ! $PIP_CMD install -r requirements.txt; then
    echo "Error: Failed to install Python dependencies."
    echo "Please check your internet connection and try again."
    exit 1
fi

# --- Create .env file with configuration ---
echo "[3/7] Creating environment configuration file..."

# Check if .env file already exists
if [ -f ".env" ]; then
    echo "A .env file already exists in the root directory."
    read -p "Do you want to overwrite it? (y/N): " overwrite_env
    if [[ ! "$overwrite_env" =~ ^[Yy]$ ]]; then
        echo "Skipping .env file creation. Using existing .env file."
    else
        echo "Overwriting existing .env file..."
        # Continue with .env creation
    fi
else
    echo "Creating new .env file..."
fi

# Only create .env if it doesn't exist or user chose to overwrite
if [ ! -f ".env" ] || [[ "$overwrite_env" =~ ^[Yy]$ ]]; then
    # Generate a random UUID for STARLETTE_SECRET
    if command -v python3 &> /dev/null; then
        STARLETTE_SECRET=$(python3 -c "import uuid; print(str(uuid.uuid4()))")
    elif command -v python &> /dev/null; then
        STARLETTE_SECRET=$(python -c "import uuid; print(str(uuid.uuid4()))")
    else
        echo "Error: Python not found for generating secret key."
        exit 1
    fi

    # Create .env file with all required variables
    cat > .env << EOF
# Tatlock Environment Configuration
# Generated automatically during installation

# API Keys (Required - Please update these with your actual API keys)
OPENWEATHER_API_KEY=your_openweather_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_cse_id_here

# LLM Configuration
OLLAMA_MODEL=gemma3-cortex:latest

# Database Configuration
DATABASE_ROOT=hippocampus/

# Security
STARLETTE_SECRET=$STARLETTE_SECRET
EOF

    echo "- .env file created in root directory"
    echo "- STARLETTE_SECRET generated automatically"
    echo "- Please update OPENWEATHER_API_KEY, GOOGLE_API_KEY, and GOOGLE_CSE_ID with your actual API keys"
else
    echo "- Using existing .env file"
fi

# --- Download Material Icons for offline use ---
echo "[4/7] Downloading Material Icons for offline web interface..."
mkdir -p stem/static/fonts
cd stem/static/fonts
if ! wget -O material-icons.woff2 "https://fonts.gstatic.com/s/materialicons/v140/flUhRq6tzZclQEJ-Vdg-IuiaDsNcIhQ8tQ.woff2"; then
    echo "Warning: Failed to download Material Icons WOFF2. Continuing without it."
fi
if ! wget -O material-icons.woff "https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/fonts/materialdesignicons-webfont.woff"; then
    echo "Warning: Failed to download Material Icons WOFF. Continuing without it."
fi
if ! wget -O material-icons.ttf "https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/fonts/materialdesignicons-webfont.ttf"; then
    echo "Warning: Failed to download Material Icons TTF. Continuing without it."
fi
cd ../..

# --- Initialize databases ---
echo "[5/7] Initializing databases..."
if ! PYTHONPATH=. python3 -c "from stem.installation.database_setup import create_system_db_tables; create_system_db_tables('hippocampus/system.db')"; then
    echo "Error: Failed to initialize databases."
    exit 1
fi

echo "- system.db is ready in the hippocampus/ directory. User memory databases will be created automatically when users are added."

# --- Create admin user if not exists ---
echo "[6/7] Checking for admin account..."
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
    if ! PYTHONPATH=. python3 -c "
from stem.security import security_manager
if security_manager.create_user('$admin_user', '$admin_first', '$admin_last', '$admin_pass', '$admin_email'):
    security_manager.add_user_to_role('$admin_user', 'user')
    security_manager.add_user_to_role('$admin_user', 'admin')
    security_manager.add_user_to_group('$admin_user', 'users')
    security_manager.add_user_to_group('$admin_user', 'admins')
    print('Admin user created and configured.')
else:
    print('Failed to create admin user.')
    exit(1)
"; then
        echo "Error: Failed to create admin user."
        exit 1
    fi
else
    echo "Admin account already exists."
fi

echo ""
echo "Tatlock installation complete!"
echo "- Ollama with Gemma3-enhanced model is ready"
echo "- .env configuration file created with auto-generated secret key"
echo "- Material Icons downloaded for offline web interface"
echo "- system.db and longterm.db are ready in the hippocampus/ directory"
echo "- Default roles, groups, and system prompts are configured"
echo "- You can now run the application as described in the README"
echo ""
echo "IMPORTANT: Please update the API keys in your .env file before running the application:"
echo "- OPENWEATHER_API_KEY: Get from https://openweathermap.org/api"
echo "- GOOGLE_API_KEY: Get from https://console.cloud.google.com/"
echo "- GOOGLE_CSE_ID: Get from https://programmablesearchengine.google.com/"
echo ""
echo "If you need to re-run this script, it is safe to do so (tables will not be duplicated)." 