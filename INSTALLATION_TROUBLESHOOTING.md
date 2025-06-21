# Installation Troubleshooting Guide

This guide helps resolve common issues encountered during Tatlock installation.

## Repository Issues

### "Repository does not have a Release file" Error

This error typically occurs when:
1. You're using a distribution that's not Ubuntu/Debian
2. There are conflicting or broken repositories in your system
3. The package manager is locked

#### Solutions:

**For non-Ubuntu/Debian systems:**
- The installation script is designed for apt-based systems (Ubuntu/Debian)
- For other distributions, you may need to manually install dependencies
- Consider using Docker or a virtual machine with Ubuntu

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

## Manual Installation

If the automated script fails, you can install dependencies manually:

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv sqlite3 build-essential curl wget

# CentOS/RHEL/Fedora
sudo yum install -y python3 python3-pip sqlite build-essential curl wget
# or
sudo dnf install -y python3 python3-pip sqlite build-essential curl wget
```

### Ollama Installation
```bash
curl -fsSL https://ollama.ai/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
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

## Common Issues

### Permission Denied Errors
- Ensure you have sudo privileges
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

### Ollama Service Issues
```bash
# Check Ollama status
sudo systemctl status ollama

# Restart Ollama service
sudo systemctl restart ollama

# Check Ollama logs
sudo journalctl -u ollama -f
```

## Getting Help

If you continue to experience issues:

1. Check the error messages carefully
2. Try the manual installation steps above
3. Ensure your system meets the minimum requirements
4. Consider using a fresh Ubuntu/Debian installation
5. Open an issue on GitHub with detailed error information

## System Requirements

- **OS**: Ubuntu 20.04+ or Debian 11+ (recommended)
- **Python**: 3.10 or higher
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection for initial setup 