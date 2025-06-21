#!/usr/bin/env bash
# install_tatlock.sh
# CLI installer for Tatlock: sets up system dependencies, Python packages, 
# Ollama LLM, Material Icons, and initializes databases with authentication.

set -e

# --- Check if we're in the correct directory ---
if [ ! -f "main.py" ] || [ ! -d "stem" ] || [ ! -d "hippocampus" ]; then
    echo "Error: This script must be run from the Tatlock project root directory."
    echo "Please ensure you're in the directory containing main.py, stem/, and hippocampus/ folders."
    exit 1
fi

# --- Instructions ---
echo "Tatlock Installation Script"
echo "--------------------------"
echo "This script will:"
echo "1. Install required system packages (Python 3, pip, sqlite3, build tools)"
echo "2. Create and activate Python virtual environment (.venv) (safely handles existing environments)"
echo "3. Install and configure Ollama with the Gemma3-enhanced model"
echo "4. Install Python dependencies from requirements.txt"
echo "5. Create .env configuration file with auto-generated secret key (safely handles existing files)"
echo "6. Download Material Icons for offline web interface"
echo "7. Initialize system.db and longterm.db with authentication and memory tables"
echo "8. Create default roles, groups, and system prompts"
echo "9. Optionally create a new admin account if one does not exist yet"
echo "10. Optionally install Tatlock as an auto-starting service"
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
echo "[1/10] Installing system dependencies..."

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
            if ! sudo yum install -y python3 python3-pip python3-venv sqlite gcc gcc-c++ make curl wget; then
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
            if ! sudo pacman -S --noconfirm python python-pip python-venv sqlite base-devel curl wget; then
                echo "Error: Failed to install required packages."
                echo "Please check your package manager configuration and try again."
                exit 1
            fi
            ;;
    esac
}

install_system_dependencies

# --- Create and activate Python virtual environment ---
echo "[2/10] Creating Python virtual environment..."

# Check if virtual environment already exists
if [ -d ".venv" ]; then
    echo "Virtual environment already exists in .venv directory."
    
    # Check if the existing virtual environment is valid
    if [ -f ".venv/bin/activate" ] && [ -f ".venv/bin/python" ]; then
        echo "Existing virtual environment appears to be valid."
        read -p "Do you want to recreate it? (y/N): " recreate_venv
        if [[ "$recreate_venv" =~ ^[Yy]$ ]]; then
            echo "Removing existing virtual environment..."
            rm -rf .venv
        else
            echo "Using existing virtual environment."
        fi
    else
        echo "Existing virtual environment appears to be corrupted or incomplete."
        read -p "Do you want to recreate it? (Y/n): " recreate_venv
        if [[ ! "$recreate_venv" =~ ^[Nn]$ ]]; then
            echo "Removing corrupted virtual environment..."
            rm -rf .venv
        else
            echo "Keeping existing virtual environment (may cause issues)."
        fi
    fi
fi

# Create virtual environment if it doesn't exist or user chose to recreate
if [ ! -d ".venv" ]; then
    echo "Creating new virtual environment in .venv directory..."
    if ! python3 -m venv .venv; then
        echo "Error: Failed to create virtual environment."
        echo "Please ensure python3-venv is installed."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Verify virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

echo "- Virtual environment created and activated: $VIRTUAL_ENV"

# Make wakeup.sh executable
echo "Making wakeup.sh executable..."
if [ -f "wakeup.sh" ]; then
    chmod +x wakeup.sh
    echo "- wakeup.sh is now executable"
else
    echo "Warning: wakeup.sh not found. Please ensure it exists in the project root."
fi

# Check if Ollama is already installed
if command -v ollama &> /dev/null; then
    echo "Ollama is already installed, skipping installation."
else
    echo "[3/10] Installing Ollama..."
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

echo "[4/10] Installing Python dependencies..."

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
echo "[5/10] Creating environment configuration file..."

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

# Server Configuration
PORT=8000

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
echo "[6/10] Downloading Material Icons for offline web interface..."

# Store the project root directory
PROJECT_ROOT=$(pwd)

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

# Return to project root directory
cd "$PROJECT_ROOT"

# --- Initialize databases ---
echo "[7/10] Initializing databases..."
if ! PYTHONPATH="$PROJECT_ROOT" python3 -c "from stem.installation.database_setup import create_system_db_tables; create_system_db_tables('hippocampus/system.db')"; then
    echo "Error: Failed to initialize databases."
    echo "Current directory: $(pwd)"
    echo "PYTHONPATH: $PYTHONPATH"
    exit 1
fi

echo "- system.db is ready in the hippocampus/ directory. User memory databases will be created automatically when users are added."

# --- Create admin user if not exists ---
echo "[8/10] Checking for admin account..."
        # Check if admin user already exists
        admin_exists=$(PYTHONPATH="$PROJECT_ROOT" python3 -c "from stem.security import security_manager; print('yes' if security_manager.authenticate_user('admin', 'breaker') else 'no')")
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
    if ! PYTHONPATH="$PROJECT_ROOT" python3 -c "
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

# --- Install as auto-starting service ---
echo "[9/10] Service installation..."

echo "Would you like to install Tatlock as an auto-starting service?"
echo "This will make Tatlock start automatically when the system boots."
read -p "Install as service? (y/N): " install_service

if [[ "$install_service" =~ ^[Yy]$ ]]; then
    echo "Installing Tatlock as auto-starting service..."
    
    # Get the absolute path to the project directory
    SERVICE_DIR=$(pwd)
    
    case $SYSTEM in
        "debian"|"rhel"|"arch")
            # Linux - Create systemd service
            echo "Creating systemd service for Linux..."
            
            # Create service file
            cat > tatlock.service << EOF
[Unit]
Description=Tatlock Conversational AI Platform
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$SERVICE_DIR
Environment=PATH=$SERVICE_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PORT=8000
ExecStart=$SERVICE_DIR/.venv/bin/python $SERVICE_DIR/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

            # Install the service
            if command -v systemctl &> /dev/null; then
                sudo cp tatlock.service /etc/systemd/system/
                sudo systemctl daemon-reload
                sudo systemctl enable tatlock.service
                sudo systemctl start tatlock.service
                
                echo "- Tatlock service installed and started"
                echo "- Service will auto-start on boot"
                echo "- Use 'sudo systemctl status tatlock' to check status"
                echo "- Use 'sudo systemctl stop tatlock' to stop the service"
                echo "- Use 'sudo systemctl start tatlock' to start the service"
                
                # Clean up temporary file
                rm tatlock.service
            else
                echo "Error: systemctl not found. Cannot install systemd service."
                echo "Please install systemd or run Tatlock manually."
            fi
            ;;
            
        "macos_arm"|"macos_intel")
            # macOS - Create launchd service
            echo "Creating launchd service for macOS..."
            
            # Create plist file
            cat > com.tatlock.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tatlock</string>
    <key>ProgramArguments</key>
    <array>
        <string>$SERVICE_DIR/.venv/bin/python</string>
        <string>$SERVICE_DIR/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$SERVICE_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/tatlock.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/tatlock.error.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$SERVICE_DIR/.venv/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>PORT</key>
        <string>8000</string>
    </dict>
</dict>
</plist>
EOF

            # Install the service
            cp com.tatlock.plist ~/Library/LaunchAgents/
            launchctl load ~/Library/LaunchAgents/com.tatlock.plist
            
            echo "- Tatlock service installed and started"
            echo "- Service will auto-start on login"
            echo "- Use 'launchctl list | grep tatlock' to check status"
            echo "- Use 'launchctl unload ~/Library/LaunchAgents/com.tatlock.plist' to stop"
            echo "- Use 'launchctl load ~/Library/LaunchAgents/com.tatlock.plist' to start"
            
            # Clean up temporary file
            rm com.tatlock.plist
            ;;
            
        *)
            echo "Warning: Auto-starting service not supported on this system."
            echo "Please run Tatlock manually using './wakeup.sh'"
            ;;
    esac
else
    echo "Skipping service installation. You can run Tatlock manually using './wakeup.sh'"
fi

echo ""
echo "Tatlock installation complete!"
echo "- Python virtual environment created in .venv directory"
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
echo "To start the application:"
echo "  ./wakeup.sh"
echo ""
echo "If you need to re-run this script, it is safe to do so (tables will not be duplicated)." 