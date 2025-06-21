# Installation Troubleshooting Guide

This guide helps resolve common issues encountered during Tatlock installation.

## What the Installation Script Does

The automated installation script performs the following steps:
1. Installs system dependencies (Python, pip, sqlite3, build tools)
2. Installs and configures Ollama with the Gemma3-enhanced model
3. Installs Python dependencies from requirements.txt
4. Creates a `.env` configuration file with auto-generated secret key (safely handles existing files)
5. Downloads Material Icons for offline web interface
6. Initializes system.db and longterm.db with authentication and memory tables
7. Creates default roles, groups, and system prompts
8. Optionally creates a new admin account

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