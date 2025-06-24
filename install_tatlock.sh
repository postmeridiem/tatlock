#!/usr/bin/env bash
# install_tatlock.sh
# CLI installer for Tatlock: sets up system dependencies, Python packages, 
# Ollama LLM, Material Icons, and initializes databases with authentication.
#
# IMPORTANT: This script will NEVER modify the system's default Python interpreter
# (e.g., /usr/bin/python3 symlink). It only installs Python 3.10+ alongside the
# existing system Python and uses it specifically for Tatlock's virtual environment.
# This ensures system tools and scripts continue to work normally.

set -e

# Color definitions
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Read version from pyproject.toml
APP_VERSION="N/A"
if [ -f "pyproject.toml" ]; then
    APP_VERSION=$(grep -E '^version = ".*"' pyproject.toml | sed -E 's/version = "(.*)"/\1/')
fi

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
echo "                                  Version: $APP_VERSION"
echo "══════════════════════════════════════════════════════════════════════════════════════════"
echo -e "${NC}"
echo ""

# --- Check if we're in the correct directory ---
if [ ! -f "main.py" ] || [ ! -d "stem" ] || [ ! -d "hippocampus" ]; then
    echo -e "${RED}Error: This script must be run from the Tatlock project root directory.${NC}"
    echo -e "Please ensure you're in the directory containing main.py, stem/, and hippocampus/ folders."
    exit 1
fi

# --- Instructions ---
echo -e "${BOLD}${CYAN}"
echo "══════════════════════════════════════════════════════════════════════════════════════════"
echo "                        Tatlock Installation Script                                      "
echo "                    Brain-Inspired Conversational AI Platform                            "
echo "══════════════════════════════════════════════════════════════════════════════════════════"
echo -e "${NC}"

echo -e "${BOLD}This script will perform the following steps:${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo -e "  ${GREEN}1.${NC} Install required system packages (Python 3.10+, pip, sqlite3)${NC}"
echo -e "  ${GREEN}2.${NC} Create and activate Python virtual environment (.venv)${NC}"
echo -e "  ${GREEN}3.${NC} Install and configure Ollama with Gemma3-enhanced model${NC}"
echo -e "  ${GREEN}4.${NC} Install Python dependencies from requirements.txt${NC}"
echo -e "  ${GREEN}5.${NC} Create .env configuration file with auto-generated secret key${NC}"
echo -e "  ${GREEN}6.${NC} Download Material Icons for offline web interface${NC}"
echo -e "  ${GREEN}7.${NC} Initialize system.db and longterm.db with authentication tables${NC}"
echo -e "  ${GREEN}8.${NC} Create default roles, groups, and system prompts${NC}"
echo -e "  ${GREEN}9.${NC} Optionally create a new admin account if one does not exist${NC}"
echo -e "  ${GREEN}10.${NC} Optionally install Tatlock as an auto-starting service${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} This script requires Python 3.10 or higher for modern type hint support."
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
                "ubuntu"|"debian"|"linuxmint"|"zorin"|"pop")
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

echo -e "${BOLD}${CYAN}System Detection:${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo -e "  ${GREEN}Detected System:${NC}    ${BOLD}$SYSTEM${NC}${CYAN}${NC}"
echo -e "  ${GREEN}Package Manager:${NC}    ${BOLD}$PACKAGE_MANAGER${NC}${CYAN}${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo ""

# --- Check if package manager is available ---
check_package_manager() {
    case $PACKAGE_MANAGER in
        "apt")
            if ! command -v apt &> /dev/null; then
                echo -e "${RED}Error: apt package manager not found.${NC}"
                exit 1
            fi
            ;;
        "yum")
            if ! command -v yum &> /dev/null; then
                echo -e "${RED}Error: yum package manager not found.${NC}"
                exit 1
            fi
            ;;
        "brew")
            if ! command -v brew &> /dev/null; then
                echo -e "${RED}Error: Homebrew not found. Please install Homebrew first:${NC}"
                echo -e "  ${CYAN}/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"${NC}"
                exit 1
            fi
            ;;
        "pacman")
            if ! command -v pacman &> /dev/null; then
                echo -e "${RED}Error: pacman package manager not found.${NC}"
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}Error: Unsupported system or package manager not detected.${NC}"
            echo -e "Please install dependencies manually or use a supported system."
            exit 1
            ;;
    esac
}

check_package_manager

# --- Install system dependencies ---
echo -e "${BLUE}[1/10] Installing system dependencies...${NC}"

# Function to check Python version
check_python_version() {
    local python_cmd="$1"
    if command -v "$python_cmd" &> /dev/null; then
        local version=$("$python_cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        if [ $? -eq 0 ]; then
            local major=$(echo "$version" | cut -d. -f1)
            local minor=$(echo "$version" | cut -d. -f2)
            if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
                echo -e "${GREEN}[✓]${NC} Found Python $version (meets requirement: 3.10+)" >&2
                return 0
            else
                echo -e "${RED}[✗]${NC} Found Python $version (requires 3.10+)" >&2
                return 1
            fi
        fi
    fi
    
    # Also check common installation paths
    local common_paths=("/usr/bin/python3.10" "/usr/local/bin/python3.10" "/opt/homebrew/bin/python3.10")
    for path in "${common_paths[@]}"; do
        if [ -f "$path" ]; then
            local version=$("$path" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
            if [ $? -eq 0 ]; then
                local major=$(echo "$version" | cut -d. -f1)
                local minor=$(echo "$version" | cut -d. -f2)
                if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ]; then
                    echo -e "${GREEN}[✓]${NC} Found Python $version at $path (meets requirement: 3.10+)" >&2
                    return 0
                fi
            fi
        fi
    done
    
    return 1
}

# Function to install Python 3.10+ based on system
install_python310() {
    case $PACKAGE_MANAGER in
        "apt")
            echo "Installing Python 3.10+ on Debian/Ubuntu..."
            
            # Add deadsnakes PPA for newer Python versions
            echo "Adding deadsnakes PPA for Python 3.10+..."
            if ! sudo add-apt-repository ppa:deadsnakes/ppa -y; then
                echo "Warning: Failed to add deadsnakes PPA. This might be due to network issues or unsupported system."
                echo "Trying to install Python 3.10 from source..."
                
                # Install build dependencies
                sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
                
                # Download and compile Python 3.10 from source
                cd /tmp
                wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz
                tar xzf Python-3.10.12.tgz
                cd Python-3.10.12
                ./configure --enable-optimizations --prefix=/usr/local
                make -j$(nproc)
                sudo make altinstall
                cd -
                rm -rf /tmp/Python-3.10.12*
                
                # Install pip for the compiled Python
                curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
                
                # Create symlink for pip3.10
                sudo ln -sf /usr/local/bin/pip3.10 /usr/bin/pip3.10
            else
                sudo apt update
                
                # Install Python 3.10 and related packages
                echo "Installing Python 3.10..."
                if ! sudo apt install -y python3.10 python3.10-venv python3.10-dev; then
                    echo "Warning: python3.10 packages not available. Trying alternative installation..."
                    
                    # Try installing just python3.10 and use get-pip.py
                    if sudo apt install -y python3.10 python3.10-venv python3.10-dev; then
                        echo "Python 3.10 installed successfully. Installing pip separately..."
                        
                        # Download and install pip for Python 3.10
                        curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
                        
                        # Create symlink for pip3.10
                        sudo ln -sf /usr/local/bin/pip3.10 /usr/bin/pip3.10
                    else
                        echo "Error: Failed to install Python 3.10 from repositories."
                        echo "Trying to install from source..."
                        
                        # Install build dependencies
                        sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
                        
                        # Download and compile Python 3.10 from source
                        cd /tmp
                        wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz
                        tar xzf Python-3.10.12.tgz
                        cd Python-3.10.12
                        ./configure --enable-optimizations --prefix=/usr/local
                        make -j$(nproc)
                        sudo make altinstall
                        cd -
                        rm -rf /tmp/Python-3.10.12*
                        
                        # Install pip for the compiled Python
                        curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
                    fi
                else
                    # Try to install python3.10-pip if available
                    if ! sudo apt install -y python3.10-pip; then
                        echo "python3.10-pip not available, installing pip separately..."
                        curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
                    fi
                fi
            fi
            
            # Create symlinks if they don't exist
            if [ ! -f /usr/bin/python3.10 ] && [ ! -f /usr/local/bin/python3.10 ]; then
                echo "Error: Python 3.10 installation failed."
                exit 1
            fi
            
            # Update pip
            python3.10 -m pip install --upgrade pip
            ;;
            
        "yum")
            echo "Installing Python 3.10+ on RHEL/CentOS/Fedora..."
            
            # For RHEL/CentOS, we need to enable EPEL and IUS
            if [ -f /etc/redhat-release ]; then
                # Enable EPEL
                sudo yum install -y epel-release
                
                # For CentOS/RHEL 8+, use dnf and enable PowerTools
                if command -v dnf &> /dev/null; then
                    sudo dnf install -y python3.10 python3.10-pip python3.10-devel
                else
                    # For older versions, try to install from source
                    echo "Installing Python 3.10 from source..."
                    sudo yum groupinstall -y "Development Tools"
                    sudo yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel
                    
                    # Download and compile Python 3.10
                    cd /tmp
                    wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz
                    tar xzf Python-3.10.12.tgz
                    cd Python-3.10.12
                    ./configure --enable-optimizations
                    sudo make altinstall
                    cd -
                    rm -rf /tmp/Python-3.10.12*
                fi
            else
                # For Fedora
                sudo dnf install -y python3.10 python3.10-pip python3.10-devel
            fi
            ;;
            
        "brew")
            echo "Installing Python 3.10+ on macOS..."
            brew install python@3.10
            
            # Add to PATH
            echo 'export PATH="/opt/homebrew/opt/python@3.10/bin:$PATH"' >> ~/.zshrc
            export PATH="/opt/homebrew/opt/python@3.10/bin:$PATH"
            ;;
            
        "pacman")
            echo "Installing Python 3.10+ on Arch Linux..."
            sudo pacman -S --noconfirm python310 python310-pip
            ;;
    esac
}

install_system_dependencies() {
    # First, check if we have Python 3.10+ available
    echo -e "${BOLD}Checking Python version...${NC}"
    
    # Quick check - if python3 --version shows 3.10+, we can skip installation
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        if [ $? -eq 0 ]; then
            MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
            MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
            if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ]; then
                echo -e "${GREEN}[✓]${NC} Found Python $PYTHON_VERSION - meets requirements" >&2
                echo -e "${CYAN}Skipping Python installation since Python 3.10+ is already available.${NC}"
                PYTHON_AVAILABLE=true
            else
                echo -e "${RED}[✗]${NC} Found Python $PYTHON_VERSION - requires 3.10+" >&2
                PYTHON_AVAILABLE=false
            fi
        else
            echo -e "${RED}[✗]${NC} Could not determine Python version" >&2
            PYTHON_AVAILABLE=false
        fi
    else
        echo -e "${RED}[✗]${NC} python3 command not found" >&2
        PYTHON_AVAILABLE=false
    fi
    
    # Only install Python if not available
    if [ "$PYTHON_AVAILABLE" != "true" ]; then
        echo -e "${YELLOW}Installing Python 3.10+...${NC}"
        install_python310
        
        # Verify installation
        if check_python_version "python3" || check_python_version "python3.10" || check_python_version "python"; then
            echo -e "${GREEN}[✓]${NC} Python 3.10+ successfully installed" >&2
            PYTHON_AVAILABLE=true
        else
            echo -e "${RED}[✗]${NC} Failed to install Python 3.10+. Please install manually." >&2
            exit 1
        fi
    fi
    
    case $PACKAGE_MANAGER in
        "apt")
            echo -e "${BOLD}Using apt package manager...${NC}"
            
            # --- Temporarily disable command-not-found hook to prevent apt update errors ---
            CNF_CONF_FILE="/etc/apt/apt.conf.d/50command-not-found"
            RENAMED_CNF_CONF_FILE="${CNF_CONF_FILE}.disabled_by_tatlock_installer"
            
            cleanup_apt_hook() {
                if [ -f "$RENAMED_CNF_CONF_FILE" ]; then
                    echo -e "${CYAN}Re-enabling command-not-found apt hook...${NC}"
                    sudo mv "$RENAMED_CNF_CONF_FILE" "$CNF_CONF_FILE"
                fi
            }
            
            # Set up a trap to re-enable the hook on script exit
            trap cleanup_apt_hook EXIT
            
            if [ -f "$CNF_CONF_FILE" ]; then
                echo -e "${YELLOW}Temporarily disabling command-not-found apt hook to prevent errors...${NC}"
                sudo mv "$CNF_CONF_FILE" "$RENAMED_CNF_CONF_FILE"
            fi
            # --- End of temporary disabling logic ---

            # Clean up any problematic repositories first
            echo -e "${CYAN}Cleaning up package lists...${NC}"
            sudo apt clean
            sudo rm -f /var/lib/apt/lists/lock
            sudo rm -f /var/cache/apt/archives/lock
            sudo rm -f /var/lib/dpkg/lock*
            
            # Update package lists with error handling
            echo -e "${CYAN}Updating package lists...${NC}"
            if ! sudo apt update; then
                echo -e "${YELLOW}Warning: Package list update failed. This might be due to repository issues.${NC}"
                echo -e "${CYAN}Attempting to continue with existing package lists...${NC}"
            fi
            
            # Install packages with error handling (excluding Python as we handled it above)
            echo -e "${CYAN}Installing required packages...${NC}"
            if ! sudo apt install -y python3-pip python3-venv sqlite3 build-essential curl wget; then
                echo -e "${RED}Error: Failed to install required packages.${NC}"
                echo -e "Please check your package manager configuration and try again."
                exit 1
            fi
            ;;
            
        "yum")
            echo -e "${BOLD}Using yum package manager...${NC}"
            
            # Update package lists
            echo -e "${CYAN}Updating package lists...${NC}"
            if ! sudo yum update -y; then
                echo -e "${YELLOW}Warning: Package list update failed. Attempting to continue...${NC}"
            fi
            
            # Install packages (excluding Python as we handled it above)
            echo -e "${CYAN}Installing required packages...${NC}"
            if ! sudo yum install -y python3-pip python3-venv sqlite gcc gcc-c++ make curl wget; then
                echo -e "${RED}Error: Failed to install required packages.${NC}"
                echo -e "Please check your package manager configuration and try again."
                exit 1
            fi
            ;;
            
        "brew")
            echo -e "${BOLD}Using Homebrew package manager...${NC}"
            
            # Update Homebrew
            echo -e "${CYAN}Updating Homebrew...${NC}"
            if ! brew update; then
                echo -e "${YELLOW}Warning: Homebrew update failed. Attempting to continue...${NC}"
            fi
            
            # Install packages (excluding Python as we handled it above)
            echo -e "${CYAN}Installing required packages...${NC}"
            
            # Handle keg-only packages properly on macOS
            # sqlite and curl are keg-only on macOS but that's normal
            if ! brew install sqlite curl wget 2>&1 | tee /tmp/brew_install.log; then
                # Check if the error is just keg-only warnings (which are normal on macOS)
                if grep -q "keg-only" /tmp/brew_install.log && ! grep -q "Error:" /tmp/brew_install.log; then
                    echo -e "${GREEN}[✓]${NC} Some packages are keg-only (normal on macOS). Installation successful."
                    echo -e "${CYAN}The following packages are available but not symlinked:${NC}"
                    echo -e "  ${YELLOW}- sqlite:${NC} Use system sqlite or add to PATH if needed"
                    echo -e "  ${YELLOW}- curl:${NC} Use system curl or add to PATH if needed"
                else
                    echo -e "${RED}Error: Failed to install required packages.${NC}"
                    echo -e "Please check your Homebrew installation and try again."
                    rm -f /tmp/brew_install.log
                    exit 1
                fi
            fi
            rm -f /tmp/brew_install.log
            
            # On macOS, we need to ensure we're using the Homebrew Python
            if [[ "$SYSTEM" == "macos_arm" ]]; then
                echo -e "${CYAN}Setting up Python for Apple Silicon...${NC}"
                # Add Homebrew Python to PATH if not already there
                if ! command -v python3 &> /dev/null; then
                    echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
                    export PATH="/opt/homebrew/bin:$PATH"
                fi
            fi
            ;;
            
        "pacman")
            echo -e "${BOLD}Using pacman package manager...${NC}"
            
            # Update package lists
            echo -e "${CYAN}Updating package lists...${NC}"
            if ! sudo pacman -Sy; then
                echo -e "${YELLOW}Warning: Package list update failed. Attempting to continue...${NC}"
            fi
            
            # Install packages (excluding Python as we handled it above)
            echo -e "${CYAN}Installing required packages...${NC}"
            if ! sudo pacman -S --noconfirm python-pip python-venv sqlite base-devel curl wget; then
                echo -e "${RED}Error: Failed to install required packages.${NC}"
                echo -e "Please check your package manager configuration and try again."
                exit 1
            fi
            ;;
    esac
}

install_system_dependencies

# --- Create and activate Python virtual environment ---
echo -e "${BLUE}[2/10] Creating Python virtual environment...${NC}"

# Function to find the correct Python executable
find_python_executable() {
    # Try different Python commands in order of preference
    for cmd in "python3.10" "python3" "python"; do
        if check_python_version "$cmd"; then
            echo "$cmd"
            return 0
        fi
    done
    
    # Also check common installation paths directly
    local common_paths=("/usr/bin/python3.10" "/usr/local/bin/python3.10" "/opt/homebrew/bin/python3.10")
    for path in "${common_paths[@]}"; do
        if [ -f "$path" ] && check_python_version "$path"; then
            echo "$path"
            return 0
        fi
    done
    
    # Debug: Show what Python versions are available
    echo "Debug: Available Python versions:" >&2
    which python3.10 2>/dev/null || echo "python3.10 not found" >&2
    which python3 2>/dev/null || echo "python3 not found" >&2
    which python 2>/dev/null || echo "python not found" >&2
    
    return 1
}

# Find the correct Python executable
PYTHON_CMD=$(find_python_executable)
if [ $? -ne 0 ] || [ -z "$PYTHON_CMD" ]; then
    echo "Error: No suitable Python 3.10+ executable found."
    echo "Please ensure Python 3.10+ is installed and available in PATH."
    echo ""
    echo "To install Python 3.10+ on Ubuntu/Debian:"
    echo "  sudo apt update"
    echo "  sudo apt install python3.10 python3.10-venv python3.10-pip"
    echo ""
    echo "To install Python 3.10+ on CentOS/RHEL/Fedora:"
    echo "  sudo dnf install python3.10 python3.10-pip python3.10-devel"
    echo ""
    echo "To install Python 3.10+ on macOS:"
    echo "  brew install python@3.10"
    exit 1
fi

echo "Using Python executable: $PYTHON_CMD"

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
    if ! $PYTHON_CMD -m venv .venv; then
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
    echo -e "${BLUE}[3/10] Installing Ollama...${NC}"
    
    # Use different installation methods based on system
    if [[ "$SYSTEM" == "macos_arm" || "$SYSTEM" == "macos_intel" ]]; then
        # On macOS, use Homebrew
        echo "Installing Ollama via Homebrew on macOS..."
        if ! brew install ollama; then
            echo "Error: Failed to install Ollama via Homebrew."
            echo "Please check your Homebrew installation and try again."
            exit 1
        fi
    else
        # On Linux, use the official install script
        echo "Installing Ollama via official install script on Linux..."
        if ! curl -fsSL https://ollama.ai/install.sh | sh; then
            echo "Error: Failed to install Ollama."
            echo "Please check your internet connection and try again."
            exit 1
        fi
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
    echo "Downloading and setting up ebdm/gemma3-enhanced:12b model..."
    if ! ollama pull "ebdm/gemma3-enhanced:12b"; then
        echo "Error: Failed to download Gemma3 model."
        echo "Please check your internet connection and try again."
        exit 1
    fi
    ollama cp "ebdm/gemma3-enhanced:12b" "gemma3-cortex:latest"
    ollama rm "ebdm/gemma3-enhanced:12b"
fi

echo -e "${BLUE}[4/10] Installing Python dependencies...${NC}"

# Check CUDA availability and driver version to prevent PyTorch warnings
echo -e "${CYAN}Checking CUDA availability...${NC}"
CUDA_AVAILABLE=false
CUDA_DRIVER_VERSION=""

# Check if nvidia-smi is available
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}[✓]${NC} NVIDIA GPU detected"
    
    # Get CUDA driver version
    CUDA_DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits | head -1)
    if [ -n "$CUDA_DRIVER_VERSION" ]; then
        echo -e "${CYAN}NVIDIA Driver Version: $CUDA_DRIVER_VERSION${NC}"
        
        # Check if CUDA runtime is available
        if command -v nvcc &> /dev/null; then
            CUDA_RUNTIME_VERSION=$(nvcc --version | grep "release" | sed 's/.*release \([0-9]\+\.[0-9]\+\).*/\1/')
            echo -e "${CYAN}CUDA Runtime Version: $CUDA_RUNTIME_VERSION${NC}"
            
            # Check if driver version is compatible (driver version should be >= runtime version * 100)
            # This is a simplified check - in practice, PyTorch has specific version requirements
            if [ -n "$CUDA_RUNTIME_VERSION" ]; then
                # Convert runtime version to driver version requirement (rough estimate)
                RUNTIME_MAJOR=$(echo "$CUDA_RUNTIME_VERSION" | cut -d. -f1)
                RUNTIME_MINOR=$(echo "$CUDA_RUNTIME_VERSION" | cut -d. -f2)
                REQUIRED_DRIVER=$((RUNTIME_MAJOR * 100 + RUNTIME_MINOR * 10))
                DRIVER_NUMERIC=$(echo "$CUDA_DRIVER_VERSION" | cut -d. -f1)
                
                if [ "$DRIVER_NUMERIC" -ge "$REQUIRED_DRIVER" ]; then
                    echo -e "${GREEN}[✓]${NC} CUDA driver version is compatible"
                    CUDA_AVAILABLE=true
                else
                    echo -e "${YELLOW}[⚠]${NC} CUDA driver version ($CUDA_DRIVER_VERSION) may be too old for PyTorch"
                    echo -e "${CYAN}Will install CPU-only PyTorch to avoid warnings${NC}"
                fi
            else
                echo -e "${YELLOW}[⚠]${NC} Could not determine CUDA runtime version"
                echo -e "${CYAN}Will install CPU-only PyTorch to avoid warnings${NC}"
            fi
        else
            echo -e "${YELLOW}[⚠]${NC} CUDA runtime (nvcc) not found"
            echo -e "${CYAN}Will install CPU-only PyTorch to avoid warnings${NC}"
        fi
    else
        echo -e "${YELLOW}[⚠]${NC} Could not determine NVIDIA driver version"
        echo -e "${CYAN}Will install CPU-only PyTorch to avoid warnings${NC}"
    fi
else
    echo -e "${CYAN}[ℹ]${NC} No NVIDIA GPU detected or nvidia-smi not available"
    echo -e "${CYAN}Will install CPU-only PyTorch${NC}"
fi

# Ensure we're using the virtual environment's pip
if [ -f ".venv/bin/pip" ]; then
    PIP_CMD=".venv/bin/pip"
elif [ -f ".venv/bin/pip3" ]; then
    PIP_CMD=".venv/bin/pip3"
else
    # Fallback to system pip if virtual environment pip is not available
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        echo "Error: pip not found. Please install Python and pip first."
        exit 1
    fi
fi

echo "Using pip: $PIP_CMD"

# Upgrade pip first
echo "Upgrading pip..."
$PIP_CMD install --upgrade pip

# Install PyTorch CPU version first if CUDA is not available
if [ "$CUDA_AVAILABLE" != "true" ]; then
    echo -e "${CYAN}Installing CPU-only PyTorch to prevent CUDA warnings...${NC}"
    if ! $PIP_CMD install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu; then
        echo -e "${YELLOW}Warning: Failed to install CPU-only PyTorch. Continuing with default installation...${NC}"
    else
        echo -e "${GREEN}[✓]${NC} CPU-only PyTorch installed successfully"
    fi
fi

if ! $PIP_CMD install -r requirements.txt; then
    echo "Error: Failed to install Python dependencies."
    echo "Please check your internet connection and try again."
    exit 1
fi

# --- Create .env file with configuration ---
echo -e "${BLUE}[5/10] Creating environment configuration file...${NC}"

# Check if .env file already exists
if [ -f ".env" ]; then
    echo "A .env file already exists in the root directory."
    read -p "Do you want to overwrite it? (y/N): " overwrite_env
    if [[ ! "$overwrite_env" =~ ^[Yy]$ ]]; then
        echo "Skipping .env file creation. Using existing .env file."
        
        # Offer to update HOSTNAME and PORT values
        echo ""
        echo -e "${CYAN}Server Configuration Update:${NC}"
        echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
        echo "Would you like to update the server configuration (HOSTNAME and PORT)?"
        read -p "Update server configuration? (y/N): " update_server_config
        
        if [[ "$update_server_config" =~ ^[Yy]$ ]]; then
            # Read current values from .env file
            current_hostname=$(grep "^HOSTNAME=" .env | cut -d'=' -f2 2>/dev/null || echo "localhost")
            current_port=$(grep "^PORT=" .env | cut -d'=' -f2 2>/dev/null || echo "8000")
            
            echo ""
            echo -e "${CYAN}Current Configuration:${NC}"
            echo "HOSTNAME: $current_hostname"
            echo "PORT: $current_port"
            echo ""
            echo -e "${CYAN}Enter new values (press Enter to keep current value):${NC}"
            
            read -p "Enter hostname [$current_hostname]: " hostname_input
            hostname_input=${hostname_input:-$current_hostname}
            read -p "Enter port [$current_port]: " port_input
            port_input=${port_input:-$current_port}
            
            # Update the .env file with new values
            if [ "$hostname_input" != "$current_hostname" ] || [ "$port_input" != "$current_port" ]; then
                # Create a temporary file with updated values
                temp_env=$(mktemp)
                while IFS= read -r line; do
                    if [[ "$line" =~ ^HOSTNAME= ]]; then
                        echo "HOSTNAME=$hostname_input" >> "$temp_env"
                    elif [[ "$line" =~ ^PORT= ]]; then
                        echo "PORT=$port_input" >> "$temp_env"
                    elif [[ "$line" =~ ^ALLOWED_ORIGINS= ]]; then
                        echo "ALLOWED_ORIGINS=http://$hostname_input:$port_input" >> "$temp_env"
                    else
                        echo "$line" >> "$temp_env"
                    fi
                done < .env
                
                # Replace the original .env file
                mv "$temp_env" .env
                echo ""
                echo -e "${GREEN}✓ Server configuration updated:${NC}"
                echo "- HOSTNAME: $current_hostname → $hostname_input"
                echo "- PORT: $current_port → $port_input"
                echo "- ALLOWED_ORIGINS updated to match new configuration"
                
                # Update system settings database
                if PYTHONPATH="$PROJECT_ROOT" $PYTHON_CMD -c "
from stem.installation.database_setup import migrate_env_to_settings
migrate_env_to_settings('hippocampus/system.db', '$hostname_input', '$port_input')
print('System settings updated from .env file')
"; then
                    echo "- System settings database updated"
                fi
            else
                echo ""
                echo "No changes made to server configuration."
            fi
        fi
        echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
        echo ""
    else
        echo "Overwriting existing .env file..."
        # Continue with .env creation
    fi
else
    echo "Creating new .env file..."
fi

# Only create .env if it doesn't exist or user chose to overwrite
if [ ! -f ".env" ] || [[ "$overwrite_env" =~ ^[Yy]$ ]]; then
    # Generate a random UUID for STARLETTE_SECRET using the correct Python version
    STARLETTE_SECRET=$($PYTHON_CMD -c "import uuid; print(str(uuid.uuid4()))")
    if [ $? -ne 0 ]; then
        echo "Error: Failed to generate secret key with $PYTHON_CMD."
        exit 1
    fi

    # Get server configuration from user
    echo ""
    echo -e "${CYAN}Server Configuration:${NC}"
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
    read -p "Enter hostname [localhost]: " hostname_input
    hostname_input=${hostname_input:-localhost}
    read -p "Enter port [8000]: " port_input
    port_input=${port_input:-8000}
    echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
    echo ""

    # Create .env file with all required variables
    cat > .env << EOF
# Tatlock Environment Configuration
# Generated automatically during installation

# API Keys (Required - Please update these with your actual API keys)
OPENWEATHER_API_KEY=your_openweather_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CSE_ID=your_google_cse_id_here

# Database Configuration
DATABASE_ROOT=hippocampus/

# Security
STARLETTE_SECRET=$STARLETTE_SECRET
EOF

    echo "- .env file created in root directory"
    echo "- STARLETTE_SECRET generated automatically"
    echo "- Server configured to run on $hostname_input:$port_input"
    echo "- API keys can be configured through the admin interface after login"
    
    # Update system settings database with the new configuration
    echo ""
    echo -e "${BLUE}Updating system settings database...${NC}"
    if PYTHONPATH="$PROJECT_ROOT" $PYTHON_CMD -c "
from stem.installation.database_setup import migrate_env_to_settings
migrate_env_to_settings('hippocampus/system.db', '$hostname_input', '$port_input')
print('System settings database updated with new configuration')
"; then
        echo "- System settings database updated with new configuration"
    else
        echo "- Warning: Could not update system settings database"
    fi
else
    echo "- Using existing .env file"
fi

# --- Initialize databases ---
echo -e "${BLUE}[6/10] Initializing databases...${NC}"

# Ensure hippocampus directory exists
if [ ! -d "hippocampus" ]; then
    echo "Creating hippocampus directory..."
    mkdir -p hippocampus
fi

if ! PYTHONPATH="$PROJECT_ROOT" $PYTHON_CMD -c "from stem.installation.database_setup import create_system_db_tables; create_system_db_tables('hippocampus/system.db')"; then
    echo "Error: Failed to initialize databases."
    echo "Current directory: $(pwd)"
    echo "PYTHONPATH: $PYTHONPATH"
    exit 1
fi

echo "- system.db is ready in the hippocampus/ directory. User memory databases will be created automatically when users are added."

# --- Create admin user if not exists ---
echo -e "${BLUE}[7/10] Admin user setup...${NC}"

# Check if admin user already exists
admin_exists="no"
if [ -f "hippocampus/system.db" ]; then
    if PYTHONPATH="$PROJECT_ROOT" $PYTHON_CMD -c "
import sqlite3
try:
    conn = sqlite3.connect('hippocampus/system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username FROM users WHERE username = ?', ('admin',))
    result = cursor.fetchone()
    conn.close()
    if result:
        print('yes')
    else:
        print('no')
except:
    print('no')
" | grep -q "yes"; then
        admin_exists="yes"
    fi
fi

# Track if default password is used
used_default_password=false

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
    # Check if default password was used
    if [ "$admin_pass" = "admin123" ]; then
        used_default_password=true
    fi
    if ! PYTHONPATH="$PROJECT_ROOT" $PYTHON_CMD -c "
from stem.security import security_manager
import sys
import os
import sqlite3
try:
    print('Debug: Database path:', security_manager.db_path)
    print('Debug: Database file exists:', os.path.exists(security_manager.db_path))
    print('Debug: Hippocampus directory exists:', os.path.exists('hippocampus'))
    print('Debug: Current working directory:', os.getcwd())
    
    # Test database connection
    try:
        conn = sqlite3.connect(security_manager.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" AND name=\"users\"')
        users_table_exists = cursor.fetchone() is not None
        print('Debug: Users table exists:', users_table_exists)
        
        # Check if admin user already exists
        cursor.execute('SELECT username FROM users WHERE username = ?', ('$admin_user',))
        existing_user = cursor.fetchone()
        print('Debug: Admin user already exists:', existing_user is not None)
        if existing_user:
            print('Debug: Existing user found:', existing_user[0])
        
        conn.close()
    except Exception as db_error:
        print('Debug: Database connection error:', db_error)
    
    result = security_manager.create_user(
        '$admin_user', '$admin_first', '$admin_last', '$admin_pass', '$admin_email'
    )
    if result:
        security_manager.add_user_to_role('$admin_user', 'user')
        security_manager.add_user_to_role('$admin_user', 'admin')
        security_manager.add_user_to_group('$admin_user', 'users')
        security_manager.add_user_to_group('$admin_user', 'admins')
        print('Admin user created and configured.')
    else:
        print('Failed to create admin user. Return value:', result)
        if hasattr(security_manager, 'last_error'):
            print('Security manager last_error:', security_manager.last_error)
        sys.exit(1)
except Exception as e:
    import traceback
    print('Exception during admin creation:', e, file=sys.stderr)
    traceback.print_exc()
    sys.exit(2)
"; then
        echo "Error: Failed to create admin user."
        exit 1
    fi
else
    echo "Admin account already exists."
    echo ""
    read -p "Do you want to replace the existing admin user? (y/N): " replace_admin
    if [[ "$replace_admin" =~ ^[Yy]$ ]]; then
        echo "Replacing existing admin user..."
        read -p "Enter new admin username [admin]: " admin_user
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
        # Check if default password was used
        if [ "$admin_pass" = "admin123" ]; then
            used_default_password=true
        fi
        if ! PYTHONPATH="$PROJECT_ROOT" $PYTHON_CMD -c "
from stem.security import security_manager
import sys
try:
    # Delete existing admin user first
    if security_manager.delete_user('admin'):
        print('Existing admin user deleted.')
    else:
        print('Warning: Could not delete existing admin user.')
    
    # Create new admin user
    result = security_manager.create_user(
        '$admin_user', '$admin_first', '$admin_last', '$admin_pass', '$admin_email'
    )
    if result:
        security_manager.add_user_to_role('$admin_user', 'user')
        security_manager.add_user_to_role('$admin_user', 'admin')
        security_manager.add_user_to_group('$admin_user', 'users')
        security_manager.add_user_to_group('$admin_user', 'admins')
        print('New admin user created and configured.')
    else:
        print('Failed to create new admin user.')
        sys.exit(1)
except Exception as e:
    import traceback
    print('Exception during admin replacement:', e, file=sys.stderr)
    traceback.print_exc()
    sys.exit(2)
"; then
            echo "Error: Failed to replace admin user."
            exit 1
        else
            echo "Keeping existing admin user."
        fi
    fi
fi

# --- Install as auto-starting service ---
echo -e "${BLUE}[8/10] Service installation...${NC}"

echo "Would you like to install Tatlock as an auto-starting service?"
echo "This will make Tatlock start automatically when the system boots."
read -p "Install as service? (y/N): " install_service

if [[ "$install_service" =~ ^[Yy]$ ]]; then
    echo "Installing Tatlock as auto-starting service..."
    
    # Get the absolute path to the project directory
    SERVICE_DIR=$(pwd)
    
    # Read HOSTNAME and PORT from .env file if it exists
    if [ -f ".env" ]; then
        # Source the .env file to get the variables
        export $(grep -v '^#' .env | xargs)
        SERVICE_HOSTNAME=${HOSTNAME:-localhost}
        SERVICE_PORT=${PORT:-8000}
    else
        SERVICE_HOSTNAME="localhost"
        SERVICE_PORT="8000"
    fi
    
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
Environment=HOSTNAME=$SERVICE_HOSTNAME
Environment=PORT=$SERVICE_PORT
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
                echo "- Service configured to run on $SERVICE_HOSTNAME:$SERVICE_PORT"
                echo "- Use './manage-service.sh' to manage the service (status, start, stop, restart)."
                
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
        <key>HOSTNAME</key>
        <string>$SERVICE_HOSTNAME</string>
        <key>PORT</key>
        <string>$SERVICE_PORT</string>
    </dict>
</dict>
</plist>
EOF

            # Install the service
            cp com.tatlock.plist ~/Library/LaunchAgents/
            launchctl load ~/Library/LaunchAgents/com.tatlock.plist
            
            echo "- Tatlock service installed and started"
            echo "- Service will auto-start on login"
            echo "- Service configured to run on $SERVICE_HOSTNAME:$SERVICE_PORT"
            echo "- Use './manage-service.sh' to manage the service (status, start, stop, restart)."
            
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
    
    # Check for and remove any existing Tatlock services
    echo ""
    echo "Checking for existing Tatlock services..."
    
    case $SYSTEM in
        "debian"|"rhel"|"arch")
            # Linux - Check for systemd service
            if command -v systemctl &> /dev/null; then
                if systemctl is-active --quiet tatlock.service 2>/dev/null; then
                    echo "Found running Tatlock systemd service. Stopping and removing..."
                    sudo systemctl stop tatlock.service
                    sudo systemctl disable tatlock.service
                    sudo rm -f /etc/systemd/system/tatlock.service
                    sudo systemctl daemon-reload
                    echo "- Existing Tatlock systemd service removed"
                elif [ -f "/etc/systemd/system/tatlock.service" ]; then
                    echo "Found inactive Tatlock systemd service. Removing..."
                    sudo systemctl disable tatlock.service 2>/dev/null
                    sudo rm -f /etc/systemd/system/tatlock.service
                    sudo systemctl daemon-reload
                    echo "- Existing Tatlock systemd service removed"
                else
                    echo "- No existing Tatlock systemd service found"
                fi
            fi
            ;;
            
        "macos_arm"|"macos_intel")
            # macOS - Check for launchd service
            if launchctl list | grep -q "com.tatlock"; then
                echo "Found running Tatlock launchd service. Stopping and removing..."
                launchctl unload ~/Library/LaunchAgents/com.tatlock.plist 2>/dev/null
                rm -f ~/Library/LaunchAgents/com.tatlock.plist
                echo "- Existing Tatlock launchd service removed"
            elif [ -f "~/Library/LaunchAgents/com.tatlock.plist" ]; then
                echo "Found inactive Tatlock launchd service. Removing..."
                rm -f ~/Library/LaunchAgents/com.tatlock.plist
                echo "- Existing Tatlock launchd service removed"
            else
                echo "- No existing Tatlock launchd service found"
            fi
            ;;
            
        *)
            echo "- Service cleanup not supported on this system"
            ;;
    esac
fi

echo ""
echo -e "${BOLD}${GREEN}"
echo "════════════════════════════════════════════════════════════════════════════════"
echo "                         🎉 Installation Complete! 🎉"
echo "                           Tatlock is ready to use!"
echo "════════════════════════════════════════════════════════════════════════════════"
echo -e "${NC}"

echo -e "${BOLD}${CYAN}Installation Summary:${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo -e "  ${GREEN}[✓]${NC} Python virtual environment created in .venv directory"
echo -e "  ${GREEN}[✓]${NC} Ollama with Gemma3-enhanced model is ready"
echo -e "  ${GREEN}[✓]${NC} .env configuration file created with auto-generated secret key"
echo -e "  ${GREEN}[✓]${NC} Material Icons included for offline web interface"
echo -e "  ${GREEN}[✓]${NC} system.db and longterm.db are ready in the hippocampus/ directory"
echo -e "  ${GREEN}[✓]${NC} Default roles, groups, and system prompts are configured"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo ""

echo -e "${BOLD}${YELLOW}IMPORTANT:${NC} Please configure your API keys through the admin interface after logging in:"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo -e "  ${YELLOW}•${NC} OPENWEATHER_API_KEY: Get from https://openweathermap.org/api"
echo -e "  ${YELLOW}•${NC} GOOGLE_API_KEY: Get from https://console.cloud.google.com/"
echo -e "  ${YELLOW}•${NC} GOOGLE_CSE_ID: Get from https://programmablesearchengine.google.com/"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo ""

echo -e "${BOLD}${GREEN}To start the application:${NC}"
echo -e "${CYAN}  ${BOLD}./wakeup.sh${NC}"
echo ""

echo -e "${CYAN}If you need to re-run this script, it is safe to do so (tables will not be duplicated).${NC}"
echo ""

# --- Final Instructions ---
echo -e "${BOLD}${GREEN}Tatlock installation is complete!${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"
echo -e "To start the application, run: ${BOLD}./wakeup.sh${NC}"
echo -e "Then, open your browser to: ${YELLOW}http://localhost:8000/login${NC}"
echo -e ""

# Show appropriate message based on password used
if [ "$used_default_password" = true ]; then
    echo -e "Default admin credentials: ${BOLD}admin / admin123${NC}. ${RED}Please change this immediately!${NC}"
else
    echo -e "Admin user created with custom credentials. You can log in with your chosen username and password."
fi

echo -e "If you installed the service, it will start automatically on reboot."
echo -e "You can manage the service using: ${BOLD}./manage-service.sh${NC}"
echo -e "${CYAN}──────────────────────────────────────────────────────────────────────────────────${NC}"

# Make the wakeup and management scripts executable
chmod +x wakeup.sh
chmod +x manage-service.sh

echo -e "${GREEN}Enjoy using Tatlock!${NC}" 