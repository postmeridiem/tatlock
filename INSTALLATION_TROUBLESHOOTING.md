# Installation Troubleshooting Guide

This guide helps resolve common issues encountered during Tatlock installation.

## What the Installation Script Does

The automated installation script performs the following steps:
1. Installs system dependencies (Python, pip, sqlite3, build tools)
2. Creates and activates Python virtual environment (.venv)
3. Installs and configures Ollama with the Gemma3-enhanced model
4. Installs Python dependencies from requirements.txt
5. Creates a `.env` configuration file with auto-generated secret key (safely handles existing files)
6. Downloads Material Icons for offline web interface
7. Initializes system.db and longterm.db with authentication and memory tables
8. Creates default roles, groups, and system prompts
9. Optionally creates a new admin account
10. Optionally installs Tatlock as an auto-starting service

## Supported Systems

The installation script now supports:
- **Ubuntu/Debian-based systems** (apt package manager)
- **CentOS/RHEL/Fedora systems** (yum/dnf package manager)
- **macOS** (Intel and Apple Silicon, using Homebrew)
- **Arch Linux** (pacman package manager)

## Repository Issues

### "Repository does not have a Release file" Error

This error typically occurs when:
1. You're using an unsupported distribution
2. There are conflicting or broken repositories in your system
3. The package manager is locked

#### Solutions:

**For Ubuntu/Debian systems:**

1. **Clean up package manager locks:**
   ```bash
   sudo rm -f /var/lib/apt/lists/lock
   sudo rm -f /var/cache/apt/archives/lock
   sudo rm -f /var/lib/dpkg/lock*
   sudo dpkg --configure -a
   ```

2. **Remove problematic repositories:**
   ```bash
   sudo apt clean
   sudo apt update --fix-missing
   ```

3. **Check for conflicting repositories:**
   ```bash
   ls /etc/apt/sources.list.d/
   ```
   Remove any files that might be causing issues:
   ```bash
   sudo rm /etc/apt/sources.list.d/problematic-file.list
   ```

4. **Update package lists:**
   ```bash
   sudo apt update
   ```

**For CentOS/RHEL/Fedora systems:**

1. **Clean up package manager:**
   ```bash
   sudo yum clean all
   sudo yum update
   ```

2. **Check for repository issues:**
   ```bash
   sudo yum repolist
   ```

**For macOS:**

1. **Update Homebrew:**
   ```bash
   brew update
   brew doctor
   ```

2. **Fix Homebrew issues:**
   ```bash
   brew cleanup
   brew upgrade
   ```

## Manual Installation

If the automated script fails, you can install dependencies manually:

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv sqlite3 build-essential curl wget
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip sqlite gcc gcc-c++ make curl wget
```

**macOS (Intel):**
```bash
# Install Homebrew first if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python sqlite curl wget
```

**macOS (Apple Silicon):**
```bash
# Install Homebrew first if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python sqlite curl wget
# Add Homebrew to PATH
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Arch Linux:**
```bash
sudo pacman -Sy
sudo pacman -S --noconfirm python python-pip sqlite base-devel curl wget
```

### Ollama Installation
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**On Linux:**
```bash
sudo systemctl enable ollama
sudo systemctl start ollama
```

**On macOS:**
```bash
# Ollama runs as a user service on macOS
ollama serve &
```

### Python Dependencies
```bash
pip3 install -r requirements.txt
```

### Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies in virtual environment
pip install -r requirements.txt

# Make wakeup.sh executable
chmod +x wakeup.sh

# Start the application (recommended)
./wakeup.sh
```

### Model Download
```bash
ollama pull ebdm/gemma3-enhanced:12b
ollama cp ebdm/gemma3-enhanced:12b gemma3-cortex:latest
ollama rm ebdm/gemma3-enhanced:12b
```

### Environment Configuration
The installation script automatically creates a `.env` file with all required environment variables. If you need to create it manually:

```bash
# Generate a secure secret key
STARLETTE_SECRET=$(python3 -c "import uuid; print(str(uuid.uuid4()))")

# Create .env file
cat > .env << EOF
# Tatlock Environment Configuration

# API Keys (Required - Get these from the respective services)
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
```

**Required API Keys:**
- **OPENWEATHER_API_KEY**: Get from https://openweathermap.org/api
- **GOOGLE_API_KEY**: Get from https://console.cloud.google.com/
- **GOOGLE_CSE_ID**: Get from https://programmablesearchengine.google.com/

## Common Issues

### Permission Denied Errors
- Ensure you have sudo privileges (Linux) or admin access (macOS)
- Check file permissions in the project directory

### Network/Download Failures
- Check your internet connection
- Try using a different DNS server
- Use a VPN if you're behind a corporate firewall

### Python Import Errors
- Ensure you're using Python 3.10 or higher
- Check that all dependencies are installed
- Verify the PYTHONPATH is set correctly

### Virtual Environment Issues

**Virtual environment not created:**
```bash
# Check if python3-venv is installed
python3 -m venv --help

# Install python3-venv if missing
# Ubuntu/Debian:
sudo apt install python3-venv

# CentOS/RHEL/Fedora:
sudo yum install python3-venv

# Arch Linux:
sudo pacman -S python-venv
```

**Virtual environment not activated:**
```bash
# Activate manually
source .venv/bin/activate

# Verify activation
echo $VIRTUAL_ENV
which python

# Or use the wakeup script (recommended)
./wakeup.sh
```

**Permission denied on .venv:**
```bash
# Check permissions
ls -la .venv/

# Fix permissions if needed
chmod -R 755 .venv/
```

**Virtual environment corrupted:**
The installation script automatically detects corrupted virtual environments and will offer to recreate them. If you need to manually fix:

```bash
# Remove and recreate
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**wakeup.sh not executable:**
```bash
# Make wakeup.sh executable
chmod +x wakeup.sh

# Verify it's executable
ls -la wakeup.sh
```

**When does the script ask to recreate the virtual environment?**
- **Valid existing .venv**: Script asks "Do you want to recreate it? (y/N)" - default is No
- **Corrupted/incomplete .venv**: Script asks "Do you want to recreate it? (Y/n)" - default is Yes
- **No .venv**: Script creates a new one automatically

### Directory and Path Issues

**Module import errors:**
- Ensure you're running the installation script from the project root directory
- Check that all required `__init__.py` files exist in the module directories
- Verify the project structure is intact

**Running from wrong directory:**
```bash
# Always run the installation script from the project root
cd /path/to/tatlock
./install_tatlock.sh
```

**Missing __init__.py files:**
```bash
# Check if __init__.py files exist
ls -la stem/__init__.py
ls -la hippocampus/__init__.py
ls -la cortex/__init__.py

# Create missing __init__.py files if needed
touch stem/__init__.py
touch hippocampus/__init__.py
touch cortex/__init__.py
```

### Database Errors
- Ensure sqlite3 is installed
- Check write permissions in the hippocampus/ directory
- Remove and recreate the database files if corrupted

### Environment Variable Issues

**Missing .env file:**
```bash
# The installation script should create this automatically
# If missing, create it manually using the steps above
```

**Invalid API keys:**
- Verify your API keys are correct and active
- Check that you have the necessary permissions for each service
- Ensure you're using the correct API key format

**STARLETTE_SECRET issues:**
```bash
# Generate a new secret key
STARLETTE_SECRET=$(python3 -c "import uuid; print(str(uuid.uuid4()))")
echo "STARLETTE_SECRET=$STARLETTE_SECRET" >> .env
```

**Permission denied on .env:**
```bash
# Check file permissions
ls -la .env

# Fix permissions if needed
chmod 600 .env
```

**Environment variable not found errors:**
- Ensure the `.env` file is in the root directory of the project
- Check that the variable names match exactly (case-sensitive)
- Verify there are no extra spaces or special characters

**Port configuration issues:**
```bash
# Check current port setting
grep PORT .env

# Change port in .env file
sed -i 's/PORT=8000/PORT=8080/' .env

# Verify port change
grep PORT .env
```

**Port already in use:**
```bash
# Check what's using the port
sudo netstat -tlnp | grep :8000
sudo lsof -i :8000

# Kill process using the port (replace PID with actual process ID)
sudo kill -9 PID

# Or change to a different port in .env
echo "PORT=8080" >> .env
```

**"No module named 'stem'" error during database initialization:**
This error occurs when Python can't find the stem module. The installation script now handles this automatically, but if you encounter it:

```bash
# Ensure you're in the project root directory
cd /path/to/tatlock

# Set PYTHONPATH manually
export PYTHONPATH=$(pwd)

# Try the database initialization manually
python3 -c "from stem.installation.database_setup import create_system_db_tables; create_system_db_tables('hippocampus/system.db')"
```

**Common causes:**
- Running the script from the wrong directory
- Python path issues after directory changes
- Missing __init__.py files in the stem directory

### Ollama Service Issues

**Linux:**
```bash
# Check Ollama status
sudo systemctl status ollama

# Restart Ollama service
sudo systemctl restart ollama

# Check Ollama logs
sudo journalctl -u ollama -f
```

**macOS:**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama manually
ollama serve &

# Check Ollama logs
ollama logs
```

### Tatlock Service Management

**Linux (systemd):**
```bash
# Check Tatlock service status
sudo systemctl status tatlock

# Start Tatlock service
sudo systemctl start tatlock

# Stop Tatlock service
sudo systemctl stop tatlock

# Enable auto-start on boot
sudo systemctl enable tatlock

# Disable auto-start on boot
sudo systemctl disable tatlock

# View service logs
sudo journalctl -u tatlock -f
```

**macOS (launchd):**
```bash
# Check if Tatlock service is loaded
launchctl list | grep tatlock

# Load Tatlock service
launchctl load ~/Library/LaunchAgents/com.tatlock.plist

# Unload Tatlock service
launchctl unload ~/Library/LaunchAgents/com.tatlock.plist

# View service logs
tail -f /tmp/tatlock.log
tail -f /tmp/tatlock.error.log
```

**Manual service installation:**
If the automatic service installation fails, you can install it manually:

**Linux:**
```bash
# Create service file manually
sudo tee /etc/systemd/system/tatlock.service > /dev/null << EOF
[Unit]
Description=Tatlock Conversational AI Platform
After=network.target ollama.service
Wants=ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/.venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PORT=8000
ExecStart=$(pwd)/.venv/bin/python $(pwd)/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable tatlock.service
sudo systemctl start tatlock.service
```

**macOS:**
```bash
# Create plist file manually
cat > ~/Library/LaunchAgents/com.tatlock.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tatlock</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(pwd)/.venv/bin/python</string>
        <string>$(pwd)/main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
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
        <string>$(pwd)/.venv/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>PORT</key>
        <string>8000</string>
    </dict>
</dict>
</plist>
EOF

# Load the service
launchctl load ~/Library/LaunchAgents/com.tatlock.plist
```

### macOS-Specific Issues

**Apple Silicon (M1/M2) Issues:**
- Ensure you're using the Homebrew Python: `/opt/homebrew/bin/python3`
- Add Homebrew to your PATH in `~/.zshrc`
- Some packages may need to be compiled for ARM64

**Intel Mac Issues:**
- Ensure you're using the Homebrew Python: `/usr/local/bin/python3`
- Check that Homebrew is properly installed

### Yum/DNF Issues

**Package conflicts:**
```bash
sudo yum clean all
sudo yum update
sudo yum install -y python3 python3-pip sqlite gcc gcc-c++ make curl wget
```

**Repository issues:**
```bash
sudo yum repolist
sudo yum-config-manager --enable rhel-7-server-optional-rpms
```

## Getting Help

If you continue to experience issues:

1. Check the error messages carefully
2. Try the manual installation steps above
3. Ensure your system meets the minimum requirements
4. Consider using a fresh installation of a supported system
5. Open an issue on GitHub with detailed error information

## .env File Safety Features

The installation script includes safety features to protect your existing configuration:

### Existing .env File Detection
- The script automatically detects if a `.env` file already exists
- You'll be prompted: "Do you want to overwrite it? (y/N)"
- **Default is "No"** - pressing Enter will keep your existing configuration
- Choose "y" only if you want to replace your current settings

### What to do if prompted:
- **Keep existing configuration**: Press Enter or type "n"
- **Replace with new configuration**: Type "y" (this will generate a new STARLETTE_SECRET)
- **Backup first**: If unsure, copy your existing `.env` file before proceeding

### Manual .env management:
```bash
# Backup existing .env
cp .env .env.backup

# Restore from backup if needed
cp .env.backup .env
```

## System Requirements

- **OS**: Ubuntu 20.04+, Debian 11+, CentOS 8+, RHEL 8+, Fedora 33+, macOS 10.15+, Arch Linux
- **Architecture**: x86_64, ARM64 (Apple Silicon)
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection for initial setup 