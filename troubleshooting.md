# Installation Troubleshooting Guide

This guide helps resolve common issues encountered during Tatlock installation.

## Role Types in Tatlock

Tatlock uses several distinct types of "roles" that serve different purposes. Understanding these distinctions is crucial for troubleshooting and development.

### 1. Chat Message Roles (Conversation Flow)

**Purpose**: Define the role of each message in the conversation flow
**Location**: In-memory during chat processing, stored in conversation history
**Values**: 
- `"user"` - Messages from the human user
- `"assistant"` - Responses from the AI assistant (Tatlock)
- `"system"` - System instructions and prompts
- `"tool"` - Output from tool executions

**Example**:
```python
messages = [
    {"role": "user", "content": "What's the weather?"},
    {"role": "assistant", "content": "Let me check that for you."},
    {"role": "tool", "content": '{"temperature": "22°C"}'},
    {"role": "assistant", "content": "The temperature is 22°C."}
]
```

**Common Issues**:
- Missing `role` field in mock responses causes `KeyError: 'role'`
- Function expects `role` field to identify assistant responses
- Tests fail when mock responses don't include proper role field

### 2. User Roles (Access Control)

**Purpose**: Define user permissions and access levels in the system
**Location**: `hippocampus/system.db` in the `roles` table
**Values**:
- `"user"` - Basic user role with standard access
- `"admin"` - Administrator role with full system access
- `"moderator"` - Moderator role with limited administrative access

**Database Schema**:
```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**User-Role Relationship**:
```sql
CREATE TABLE user_roles (
    username TEXT,
    role_id INTEGER,
    PRIMARY KEY (username, role_id),
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE
);
```

**Common Issues**:
- Roles table only exists in system database, not longterm databases
- Attempting to create roles in longterm database causes `no such table: roles`
- User roles are separate from chat message roles

### 3. Tool Roles (Function Execution)

**Purpose**: Define the role of tools in the AI's decision-making process
**Location**: `hippocampus/system.db` in the `tools` table
**Values**: Tools are identified by their `tool_key` and have enabled/disabled status

**Database Schema**:
```sql
CREATE TABLE tools (
    tool_key TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    module TEXT NOT NULL,
    function_name TEXT NOT NULL,
    enabled INTEGER DEFAULT 0 NOT NULL
);
```

**Example Tools**:
- `"web_search"` - Web search functionality
- `"get_weather_forecast"` - Weather information
- `"recall_memories"` - Memory retrieval
- `"find_personal_variables"` - Personal information lookup

**Common Issues**:
- Tools table only exists in system database
- Tool configuration is global, not user-specific
- Tool execution uses chat message roles for communication

### 4. Group Roles (User Organization)

**Purpose**: Organize users into groups for easier management
**Location**: `hippocampus/system.db` in the `groups` table
**Values**: Custom group names defined by administrators

**Database Schema**:
```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**User-Group Relationship**:
```sql
CREATE TABLE user_groups (
    username TEXT,
    group_id INTEGER,
    PRIMARY KEY (username, group_id),
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES groups (id) ON DELETE CASCADE
);
```

### Database Separation

**System Database** (`hippocampus/system.db`):
- User roles and groups
- Tool configurations
- Authentication data
- System-wide settings

**Longterm Database** (`hippocampus/longterm/<username>.db`):
- Conversation history
- Memory storage
- Personal variables
- User-specific data

**Important**: Never try to create user roles, groups, or tool configurations in longterm databases. These belong exclusively in the system database.

### Troubleshooting Role-Related Issues

#### Chat Message Role Issues

**Symptoms**: `KeyError: 'role'` in tests or chat processing
**Solution**: Ensure mock responses include the `role` field:
```python
# Correct
mock_ollama.chat.return_value = {
    'message': {'role': 'assistant', 'content': 'Hello!'}
}

# Incorrect
mock_ollama.chat.return_value = {
    'message': {'content': 'Hello!'}
}
```

#### User Role Issues

**Symptoms**: `sqlite3.OperationalError: no such table: roles`
**Solution**: Ensure roles are only created in system database:
```python
# Correct - in system database setup
create_default_roles(cursor)  # Only in create_system_db_tables()

# Incorrect - in longterm database setup
create_default_roles(cursor)  # Don't do this in create_longterm_db_tables()
```

#### Tool Configuration Issues

**Symptoms**: Tools not available or configuration errors
**Solution**: Check tool configuration in system database:
```bash
sqlite3 hippocampus/system.db "SELECT tool_key, enabled FROM tools;"
```

## What the Installation Script Does

The automated installation script performs the following steps:
1. **Checks and installs Python 3.10+** (required for modern type hints)
2. Installs system dependencies (pip, sqlite3, build tools)
3. Creates and activates Python virtual environment (.venv) with Python 3.10+
4. Installs and configures Ollama with the Gemma3-enhanced model
5. Installs Python dependencies from requirements.txt
6. **Configures server settings**: Prompts for HOSTNAME and PORT (defaults to localhost:8000)
7. Creates a `.env` configuration file with auto-generated secret key (safely handles existing files)
8. **Handles existing `.env` files intelligently**: Offers to update HOSTNAME and PORT even when keeping existing configuration
9. **Includes Material Icons**: Fonts are now included in the repository (no download required)
10. Initializes system.db and longterm.db with authentication and memory tables
11. Creates default roles, groups, and system prompts
12. **Intelligently handles admin user creation**: Checks for existing admin users and offers to keep or replace them
13. **Provides detailed debugging**: Enhanced error reporting and system diagnostics
14. **Cleans up existing services**: If you choose not to install as a service, any existing Tatlock services are automatically stopped and removed
15. Optionally installs Tatlock as an auto-starting service

## System Requirements

- **OS**: Ubuntu 20.04+, Debian 11+, CentOS 8+, RHEL 8+, Fedora 33+, macOS 10.15+, Arch Linux
- **Architecture**: x86_64, ARM64 (Apple Silicon)
- **Python**: 3.10 or higher (required for modern type hints like `list[dict]` and `str | None`)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Network**: Internet connection for initial setup

## Supported Systems

The installation script now supports:
- **Ubuntu/Debian-based systems** (apt package manager)
- **CentOS/RHEL/Fedora systems** (yum/dnf package manager)
- **macOS** (Intel and Apple Silicon, using Homebrew)
- **Arch Linux** (pacman package manager)
- **Bazzite** (immutable Fedora, using Homebrew)

## Bazzite (Immutable System) Installation

Bazzite is an immutable Fedora-based gaming distro. The installer automatically detects Bazzite and uses Homebrew instead of system package managers.

### Requirements
- Homebrew must be installed (usually pre-installed on Bazzite)
- Python 3.10 will be installed via Homebrew
- User systemd services are supported (no root required)

### Installation Process
1. The installer detects Bazzite's immutable filesystem
2. Uses Homebrew to install Python 3.10 and dependencies
3. Ollama is installed via Homebrew
4. Creates user systemd service for auto-start (no root required)

### Common Issues

**Python 3.13 vs 3.10 Conflict:**
- System has Python 3.13, but Tatlock needs 3.10
- Installer automatically installs Python 3.10 via Homebrew
- Ensure PATH prioritizes Homebrew Python: `export PATH="/home/linuxbrew/.linuxbrew/opt/python@3.10/bin:$PATH"`

**Service Management:**
- Uses user systemd services (no root required)
- Service auto-starts on login
- Manage with: `systemctl --user status/start/stop/restart tatlock`

**Homebrew PATH Issues:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/home/linuxbrew/.linuxbrew/bin:$PATH"
export PATH="/home/linuxbrew/.linuxbrew/opt/python@3.10/bin:$PATH"
```

**Service Commands:**
```bash
# Check service status
systemctl --user status tatlock

# Start/stop service
systemctl --user start tatlock
systemctl --user stop tatlock

# View logs
journalctl --user -u tatlock -f

# Enable/disable auto-start
systemctl --user enable tatlock
systemctl --user disable tatlock
```

## Password Management and Authentication

### Password Table Migration

Tatlock has migrated from storing passwords in the `users` table to a separate `passwords` table for improved security and data organization.

#### Migration Process

The migration system automatically:
- Detects if the old schema exists (users table with `password_hash` and `salt` columns)
- Creates the new `passwords` table with proper foreign key constraints
- Copies all password data from the old table to the new table
- Removes the password columns from the `users` table
- Records the migration in a `migrations` table to prevent re-running

#### Schema Changes

**Old Schema:**
```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    password_hash TEXT NOT NULL,  -- REMOVED
    salt TEXT NOT NULL,           -- REMOVED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**New Schema:**
```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE passwords (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users (username) ON DELETE CASCADE
);
```

### Common Authentication Issues

#### "401 Unauthorized" After Migration

If you're getting authentication errors after the password migration:

**Symptoms:**
- Login fails with "401 Unauthorized" error
- Same username/password that worked before migration
- User exists in the `users` table but authentication fails

**Causes:**
1. **Migration didn't run**: Password data wasn't copied to the new `passwords` table
2. **Migration failed**: Password data was corrupted during migration
3. **User created after migration**: User exists but has no password entry

**Diagnosis:**
Use the password inspection script:
```bash
python scripts/check_user_passwords.py <username>
```

This will show:
- Whether the user exists in the `users` table
- Whether password data exists in the `passwords` table
- The password hash and salt values

**Solutions:**

1. **Password Entry Missing:**
   ```bash
   # Reset the password using the reset script
   ./stem/reset_password.sh
   ```

2. **Migration Not Applied:**
   ```bash
   # Re-run database setup to trigger migration
   python -c "from stem.installation.database_setup import create_system_db_tables; create_system_db_tables('hippocampus/system.db')"
   ```

3. **Database Corruption:**
   ```bash
   # Backup and recreate the database
   cp hippocampus/system.db hippocampus/system.db.backup
   rm hippocampus/system.db
   python -c "from stem.installation.database_setup import create_system_db_tables; create_system_db_tables('hippocampus/system.db')"
   ```

#### Password Reset Script

The `stem/reset_password.sh` script provides a secure way to reset user passwords:

**Features:**
- Interactive password input with confirmation
- Password strength validation
- Secure bcrypt hashing
- Database verification
- User information display

**Usage:**
```bash
./stem/reset_password.sh
```

**Process:**
1. Prompts for username
2. Verifies user exists in database
3. Prompts for new password (with confirmation)
4. Updates password hash in `passwords` table
5. Verifies the password update worked
6. Displays updated user information

**Security Features:**
- Passwords are never logged or stored in plain text
- Uses bcrypt with secure salt generation
- Validates password strength (minimum 8 characters)
- Records password update timestamps

#### Manual Password Reset

If the reset script is unavailable, you can manually reset passwords:

```python
import sqlite3
import bcrypt

# Connect to database
conn = sqlite3.connect('hippocampus/system.db')
cursor = conn.cursor()

# Hash new password
password = "newpassword123"
salt = bcrypt.gensalt()
password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)

# Update password
cursor.execute('''
    INSERT OR REPLACE INTO passwords (username, password_hash, salt, updated_at)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
''', ('username', password_hash.decode('utf-8'), salt.decode('utf-8')))

conn.commit()
conn.close()
```

### Database Inspection Tools

#### Check User Passwords Script

Located at `scripts/check_user_passwords.py`, this script inspects the database for a specific user:

```bash
python scripts/check_user_passwords.py <username> [db_path]
```

**Output:**
```
Checking user 'admin' in database: hippocampus/system.db

[users] table entry:
  username:   admin
  first_name: Admin
  last_name:  User
  email:      admin@example.com
  created_at: 2024-01-01 12:00:00

[passwords] table entry:
  username:      admin
  password_hash: $2b$12$...
  salt:          $2b$12$...
  created_at:    2024-01-01 12:00:00
```

#### Migration Status Check

Check if migrations have been applied:

```bash
sqlite3 hippocampus/system.db "SELECT * FROM migrations;"
```

Expected output:
```
1|users_password_separation|2024-01-01 12:00:00
```

### Authentication Debugging

#### Enable Debug Logging

Add debug logging to see authentication details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Check Authentication Flow

The authentication process:
1. User submits username/password
2. System queries `users` table for user info
3. System queries `passwords` table for password hash and salt
4. System verifies password using bcrypt
5. If valid, creates session and returns user data

#### Common Debug Points

1. **User not found**: Check `users` table
2. **Password not found**: Check `passwords` table
3. **Hash verification fails**: Check bcrypt implementation
4. **Session creation fails**: Check session middleware configuration

## Python 3.10+ Installation

The installation script automatically handles Python 3.10+ installation with multiple fallback methods:

### Ubuntu/Debian Systems
1. **Primary**: Uses deadsnakes PPA to install Python 3.10 packages
2. **Fallback 1**: Installs Python 3.10 without pip, then installs pip separately
3. **Fallback 2**: Compiles Python 3.10 from source if packages are unavailable

### CentOS/RHEL/Fedora Systems
1. **Primary**: Uses EPEL and dnf to install Python 3.10 packages
2. **Fallback**: Compiles Python 3.10 from source for older systems

### macOS Systems
1. **Primary**: Uses Homebrew to install Python 3.10
2. **Apple Silicon**: Automatically configures PATH for ARM64

### Arch Linux
1. **Primary**: Uses pacman to install Python 3.10 packages

## Common Python Installation Issues

### "python3.10-pip package not found" Error

This error occurs on older Ubuntu/Debian systems where the `python3.10-pip` package is not available.

**What the script does automatically:**
- Detects missing `python3.10-pip` package
- Installs pip separately using `get-pip.py`
- Creates necessary symlinks for `pip3.10`

**Manual fix if needed:**
```bash
# Install pip for Python 3.10 manually
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

# Create symlink
sudo ln -sf /usr/local/bin/pip3.10 /usr/bin/pip3.10
```

### "deadsnakes PPA not available" Error

This can happen due to network issues or unsupported systems.

**What the script does automatically:**
- Falls back to source compilation if PPA fails
- Installs all required build dependencies
- Compiles Python 3.10 from source

**Manual fix if needed:**
```bash
# Install build dependencies
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev

# Download and compile Python 3.10
cd /tmp
wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz
tar xzf Python-3.10.12.tgz
cd Python-3.10.12
./configure --enable-optimizations --prefix=/usr/local
make -j$(nproc)
sudo make altinstall
cd -
rm -rf /tmp/Python-3.10.12*

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
```

### "TypeError: 'type' object is not subscriptable" Error

This error occurs when using Python versions below 3.9 with modern type hints.

**Solution:**
- Ensure Python 3.10+ is installed and being used
- The installation script automatically handles this requirement

**Manual verification:**
```bash
# Check Python version
python3 --version

# Should show Python 3.10.x or higher
# If not, the installation script will install Python 3.10+
```

## Admin User Management

The installation script now intelligently handles admin user creation and provides detailed debugging information.

### Admin User Creation Process

**Step 1: Check for Existing Admin**
- The script checks if an admin user already exists in the database
- If found, displays "Admin account already exists."

**Step 2: User Choice**
- **Keep Existing Admin**: Use the default credentials (username: `admin`, password: `admin123`)
- **Replace Admin**: Delete the existing admin and create a new one with your chosen credentials

### Debugging Features

The script now provides detailed debugging information during admin creation:

**Database Diagnostics:**
- Database path and file existence
- Hippocampus directory existence
- Current working directory
- Users table existence
- Existing user detection

**Error Reporting:**
- Detailed Python exceptions and tracebacks
- Database connection status
- SQL query results
- Security manager error messages

### Common Admin Creation Issues

#### "Failed to create admin user" Error

**What the script now shows:**
- Detailed debug information about database state
- Whether the admin user already exists
- Specific Python exceptions if they occur

**Solutions:**

1. **Admin User Already Exists:**
   ```
   Debug: Admin user already exists: True
   Debug: Existing user found: admin
   ```
   - Choose to keep the existing admin user
   - Or choose to replace it with new credentials

2. **Database Issues:**
   ```
   Debug: Database file exists: False
   ```
   - The script will automatically create the database directory
   - Ensure proper file permissions

3. **Table Issues:**
   ```
   Debug: Users table exists: False
   ```
   - The script will automatically create the required tables
   - Check if the database initialization step completed successfully

#### "No admin account found" but "Admin user already exists"

This can happen if the admin user exists but has a different password than the default `admin123`.

**Solution:**
- The script now properly detects existing users regardless of password
- Choose to replace the admin user if you want to set new credentials

### Manual Admin User Creation

If you need to create an admin user manually:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the admin creation script
PYTHONPATH=. python -c "
from stem.security import security_manager
if security_manager.create_user('admin', 'Administrator', 'User', 'your_password', 'admin@tatlock.local'):
    security_manager.add_user_to_role('admin', 'admin')
    security_manager.add_user_to_group('admin', 'admins')
    print('Admin user created successfully')
else:
    print('Failed to create admin user')
"
```

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

### Python 3.10+ Installation

**Ubuntu/Debian:**
```bash
# Add deadsnakes PPA for Python 3.10
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# Install pip for Python 3.10
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10

# Set Python 3.10 as default
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
```

**CentOS/RHEL/Fedora:**
```bash
# Enable EPEL
sudo yum install -y epel-release

# Install Python 3.10 (for newer systems with dnf)
sudo dnf install -y python3.10 python3.10-pip python3.10-devel

# For older systems, compile from source
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel
cd /tmp
wget https://www.python.org/ftp/python/3.10.12/Python-3.10.12.tgz
tar xzf Python-3.10.12.tgz
cd Python-3.10.12
./configure --enable-optimizations
sudo make altinstall
cd -
rm -rf /tmp/Python-3.10.12*
```

**macOS (Intel):**
```bash
# Install Homebrew first if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.10
```

**macOS (Apple Silicon):**
```bash
# Install Homebrew first if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.10
# Add Homebrew to PATH
echo 'export PATH="/opt/homebrew/opt/python@3.10/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Arch Linux:**
```bash
sudo pacman -Sy
sudo pacman -S --noconfirm python310 python310-pip
```

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv sqlite3 build-essential curl wget
```

**CentOS/RHEL/Fedora:**
```bash
sudo yum update -y
sudo yum install -y python3-pip sqlite gcc gcc-c++ make curl wget
```

**macOS (Intel):**
```bash
brew install sqlite curl wget
```

**macOS (Apple Silicon):**
```bash
brew install sqlite curl wget
```

**Arch Linux:**
```bash
sudo pacman -Sy
sudo pacman -S --noconfirm python-pip sqlite base-devel curl wget
```

### Ollama Installation

**On macOS:**
```bash
# Install via Homebrew (recommended)
brew install ollama

# Start Ollama service
ollama serve &
```

**On Linux:**
```bash
# Install via official install script
curl -fsSL https://ollama.ai/install.sh | sh

# Enable and start service
sudo systemctl enable ollama
sudo systemctl start ollama
```

**On Arch Linux:**
```bash
# Install via pacman
sudo pacman -S ollama

# Enable and start service
sudo systemctl enable ollama
sudo systemctl start ollama
```

### Python Dependencies
```bash
pip3 install -r requirements.txt
```

### Virtual Environment Setup
```bash
# Create virtual environment with Python 3.10+
python3.10 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Verify Python version in virtual environment
python --version  # Should show Python 3.10.x

# Install dependencies in virtual environment
pip install -r requirements.txt

# Make wakeup.sh executable
chmod +x wakeup.sh

# Start the application (recommended)
./wakeup.sh
```

### Model Download
```bash
ollama pull "ebdm/gemma3-enhanced:12b"
ollama cp "ebdm/gemma3-enhanced:12b" "gemma3-cortex:latest"
ollama rm "ebdm/gemma3-enhanced:12b"
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

# Security Configuration
ALLOWED_ORIGINS=http://localhost:8000

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

**API Key Configuration:**
The installation script now handles missing API keys gracefully:
- **Weather API**: If `OPENWEATHER_API_KEY` is missing, weather functionality is disabled with a warning
- **Web Search API**: If `GOOGLE_API_KEY` or `GOOGLE_CSE_ID` are missing, web search functionality is disabled with a warning
- **Application continues**: The application will start and run without these APIs, just with limited functionality

**To enable full functionality, add your API keys to .env:**
```bash
# Edit .env file
nano .env

# Add your API keys:
OPENWEATHER_API_KEY=your_actual_openweather_api_key
GOOGLE_API_KEY=your_actual_google_api_key
GOOGLE_CSE_ID=your_actual_google_cse_id
```

**Getting API Keys:**
- **OpenWeather API**: Sign up at https://openweathermap.org/api (free tier available)
- **Google Custom Search**: 
  - Get API key from https://console.cloud.google.com/
  - Create Custom Search Engine at https://programmablesearchengine.google.com/
  - Get CSE ID from your search engine settings

**Invalid API keys:**
- Verify your API keys are correct and active
- Check that you have the necessary permissions for each service
- Ensure you're using the correct API key format
- For Google Custom Search, make sure your CSE is configured for web search

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

**Keg-only package warnings:**
On macOS, you may see warnings about packages being "keg-only" during Homebrew installation:

```
sqlite is keg-only, which means it was not symlinked into /opt/homebrew,
because macOS already provides this software and installing another version in
parallel can cause all kinds of trouble.
```

**This is normal behavior on macOS!** The installation script now handles these warnings properly. These warnings occur because:

- **sqlite**: macOS already provides SQLite, so Homebrew doesn't symlink its version
- **curl**: macOS already provides curl, so Homebrew doesn't symlink its version

**What this means:**
- The packages are successfully installed
- They're just not automatically added to your PATH
- Tatlock will use the system versions (which work perfectly fine)
- No action is required from you

**If you need to use the Homebrew versions specifically:**
```bash
# Add to your shell profile (~/.zshrc or ~/.bash_profile)
export PATH="/opt/homebrew/opt/sqlite/bin:$PATH"
export PATH="/opt/homebrew/opt/curl/bin:$PATH"

# For development (if you need the headers)
export LDFLAGS="-L/opt/homebrew/opt/sqlite/lib"
export CPPFLAGS="-I/opt/homebrew/opt/sqlite/include"
export PKG_CONFIG_PATH="/opt/homebrew/opt/sqlite/lib/pkgconfig"
```

**Apple Silicon (M1/M2) specific issues:**
- Ensure you're using the correct Python installation for your architecture
- The installation script automatically detects and configures for Apple Silicon
- If you encounter issues, try: `export PATH="/opt/homebrew/bin:$PATH"`

**Homebrew not found:**
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# For Apple Silicon, you may need to add to PATH
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

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

## Ollama Service Issues

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

## Ollama Model Issues

**"command not found" errors with model names:**
If you see errors like `3-enhanced:12b: command not found`, this is a shell parsing issue with colons in model names.

**Solution:**
Always quote model names when using Ollama commands:
```bash
# Correct way (with quotes)
ollama pull "ebdm/gemma3-enhanced:12b"
ollama cp "ebdm/gemma3-enhanced:12b" "gemma3-cortex:latest"
ollama rm "ebdm/gemma3-enhanced:12b"

# Wrong way (without quotes - causes shell parsing issues)
ollama pull ebdm/gemma3-enhanced:12b
ollama cp ebdm/gemma3-enhanced:12b gemma3-cortex:latest
ollama rm ebdm/gemma3-enhanced:12b
```

**Model download failures:**
```bash
# Check available models
ollama list

# Check if model exists
ollama show "ebdm/gemma3-enhanced:12b"

# Try downloading with verbose output
ollama pull "ebdm/gemma3-enhanced:12b" --verbose

# Check Ollama server status
curl http://localhost:11434/api/tags
```

**Model not found errors:**
- Verify the model name is correct
- Check that Ollama is running (`ollama serve`)
- Ensure you have sufficient disk space for the model
- Try pulling the model manually first

**Model copying issues:**
```bash
# Check if source model exists
ollama list | grep "ebdm/gemma3-enhanced"

# Check if destination model already exists
ollama list | grep "gemma3-cortex"

# Remove existing destination model if needed
ollama rm "gemma3-cortex:latest"

# Try copying again
ollama cp "ebdm/gemma3-enhanced:12b" "gemma3-cortex:latest"
```

## Agent and Tool Issues

### Web Search Tool Issues

**"Tool call syntax returned instead of results" Error:**
This was a common issue where the agent would return tool call syntax instead of executing the search.

**What's been fixed:**
- The agent now properly parses tool calls from ```tool_calls``` code blocks
- Web search tool executes correctly and returns actual search results
- Improved error handling for missing API keys

**If you still see tool call syntax:**
1. Ensure your Google API keys are configured in `.env`
2. Check that the agent is using the latest code with tool call parsing fixes
3. Verify that Python 3.10+ is being used (required for modern type hints)

### Agent Tool Call Parsing

The agent now supports multiple tool call formats:
- **Standard Ollama format**: Proper tool call objects
- **Code block format**: ```tool_calls``` blocks with JSON
- **Legacy format**: `<tool_call>` XML-style tags

**Manual verification:**
```bash
# Test web search functionality
python -c "
from stem.tools import execute_web_search
result = execute_web_search('test query')
print('Web search result:', result)
"
```

### Memory and Database Issues

**"No module named 'hippocampus'" Error:**
This can occur if the Python path is not set correctly.

**Solution:**
```bash
# Ensure you're in the project root
cd /path/to/tatlock

# Set PYTHONPATH
export PYTHONPATH=$(pwd)

# Test import
python -c "import hippocampus; print('Import successful')"
```

**Database initialization errors:**
```bash
# Check database permissions
ls -la hippocampus/

# Fix permissions if needed
chmod 755 hippocampus/
chmod 644 hippocampus/*.db 2>/dev/null || true

# Reinitialize database
python -c "from stem.installation.database_setup import create_system_db_tables; create_system_db_tables('hippocampus/system.db')"
```

## Server Configuration (HOSTNAME and PORT)

The installation script now prompts for server configuration settings that determine how Tatlock will be accessible.

### Configuration Options

**HOSTNAME**: The hostname or IP address where Tatlock will be accessible
- **Default**: `localhost` (only accessible from the local machine)
- **Common alternatives**:
  - `0.0.0.0` (accessible from any network interface)
  - `192.168.1.100` (specific IP address)
  - `tatlock.local` (custom hostname)

**PORT**: The port number for the web interface
- **Default**: `8000`
- **Common alternatives**: `8080`, `3000`, `5000`

### Updating Existing Configuration

If you have an existing `.env` file and choose not to overwrite it, the installer will offer to update just the server configuration:

```
A .env file already exists in the root directory.
Do you want to overwrite it? (y/N): n
Skipping .env file creation. Using existing .env file.

Server Configuration Update:
──────────────────────────────────────────────────────────────────────────────────
Would you like to update the server configuration (HOSTNAME and PORT)?
Update server configuration? (y/N): y

Current Configuration:
HOSTNAME: localhost
PORT: 8000

Enter new values (press Enter to keep current value):
Enter hostname [localhost]: 0.0.0.0
Enter port [8000]: 8080

✓ Server configuration updated:
- HOSTNAME: localhost → 0.0.0.0
- PORT: 8000 → 8080
- ALLOWED_ORIGINS updated to match new configuration
```

### Service Configuration

When installing as a service, the installer automatically reads the HOSTNAME and PORT from your `.env` file and configures the service accordingly.

### Common Configuration Scenarios

**Local Development**:
- HOSTNAME: `localhost`
- PORT: `8000`
- Access: `http://localhost:8000`

**Network Access**:
- HOSTNAME: `0.0.0.0`
- PORT: `8000`
- Access: `http://your-ip-address:8000`

**Custom Port**:
- HOSTNAME: `localhost`
- PORT: `8080`
- Access: `http://localhost:8080`

**Production Server**:
- HOSTNAME: `0.0.0.0`
- PORT: `80` (requires root privileges) or `8080`
- Access: `http://your-server-ip:8080`

## Service Cleanup

When you choose not to install Tatlock as a service, the installer automatically cleans up any existing Tatlock services to prevent conflicts.

### What Gets Cleaned Up

**Linux (systemd)**:
- Stops running `tatlock.service`
- Disables the service from auto-starting
- Removes the service file from `/etc/systemd/system/`
- Reloads systemd daemon

**macOS (launchd)**:
- Unloads running `com.tatlock` service
- Removes the plist file from `~/Library/LaunchAgents/`

### Example Cleanup Output

```
Skipping service installation. You can run Tatlock manually using './wakeup.sh'

Checking for existing Tatlock services...
Found running Tatlock systemd service. Stopping and removing...
- Existing Tatlock systemd service removed
```

### Manual Service Cleanup

If you need to manually clean up services:

**Linux**:
```bash
sudo systemctl stop tatlock
sudo systemctl disable tatlock
sudo rm /etc/systemd/system/tatlock.service
sudo systemctl daemon-reload
```

**macOS**:
```bash
launchctl unload ~/Library/LaunchAgents/com.tatlock.plist
rm ~/Library/LaunchAgents/com.tatlock.plist
```

## Material Icons (No Download Required)

Material Icons are now included in the repository and no longer need to be downloaded during installation.

### What Changed

- **Before**: Fonts were downloaded from external sources during installation
- **Now**: Fonts are included in the `stem/static/fonts/` directory
- **Benefits**: Faster installation, no network dependency, more reliable

### Font Files Included

- `material-icons.woff2` - Modern web font format
- `material-icons.woff` - Web font format for older browsers
- `material-icons.ttf` - TrueType font for fallback

### Manual Font Installation

If you need to manually install fonts (rare):

```bash
# Create fonts directory
mkdir -p stem/static/fonts

# Download fonts manually if needed
wget -O stem/static/fonts/material-icons.woff2 "https://fonts.gstatic.com/s/materialicons/v140/flUhRq6tzZclQEJ-Vdg-IuiaDsNcIhQ8tQ.woff2"
wget -O stem/static/fonts/material-icons.woff "https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/fonts/materialdesignicons-webfont.woff"
wget -O stem/static/fonts/material-icons.ttf "https://cdn.jsdelivr.net/npm/@mdi/font@7.2.96/fonts/materialdesignicons-webfont.ttf"
``` 