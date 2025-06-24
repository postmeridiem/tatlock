#!/bin/bash

# Test script to verify Python version checking
# This simulates what would happen with different Python versions

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check Python version (copied from install_tatlock.sh)
check_python_version() {
    local python_cmd="$1"
    if command -v "$python_cmd" &> /dev/null; then
        local version=$("$python_cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        if [ $? -eq 0 ]; then
            local major=$(echo "$version" | cut -d. -f1)
            local minor=$(echo "$version" | cut -d. -f2)
            if [ "$major" -eq 3 ] && [ "$minor" -eq 10 ]; then
                echo -e "${GREEN}[✓]${NC} Found Python $version (exactly 3.10 - perfect!)" >&2
                return 0
            elif [ "$major" -eq 3 ] && [ "$minor" -gt 10 ]; then
                echo -e "${RED}[✗]${NC} Found Python $version (requires exactly 3.10, not higher)" >&2
                return 1
            else
                echo -e "${RED}[✗]${NC} Found Python $version (requires exactly 3.10)" >&2
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
                if [ "$major" -eq 3 ] && [ "$minor" -eq 10 ]; then
                    echo -e "${GREEN}[✓]${NC} Found Python $version at $path (exactly 3.10 - perfect!)" >&2
                    return 0
                elif [ "$major" -eq 3 ] && [ "$minor" -gt 10 ]; then
                    echo -e "${RED}[✗]${NC} Found Python $version at $path (requires exactly 3.10, not higher)" >&2
                    return 1
                else
                    echo -e "${RED}[✗]${NC} Found Python $version at $path (requires exactly 3.10)" >&2
                    return 1
                fi
            fi
        fi
    done
    
    return 1
}

echo "Testing Python version checking function..."
echo "=========================================="

# Test with current Python
echo "Testing with current Python:"
if check_python_version "python3"; then
    echo "✓ Current Python version is acceptable"
else
    echo "✗ Current Python version is not acceptable"
fi

echo ""
echo "Simulating different Python versions:"
echo "====================================="

# Simulate Python 3.9 (should fail)
echo "Simulating Python 3.9:"
if check_python_version "python3.9" 2>/dev/null; then
    echo "✓ Python 3.9 would be accepted (this is wrong!)"
else
    echo "✗ Python 3.9 would be rejected (correct)"
fi

# Simulate Python 3.11 (should fail)
echo "Simulating Python 3.11:"
if check_python_version "python3.11" 2>/dev/null; then
    echo "✓ Python 3.11 would be accepted (this is wrong!)"
else
    echo "✗ Python 3.11 would be rejected (correct)"
fi

# Simulate Python 3.12 (should fail)
echo "Simulating Python 3.12:"
if check_python_version "python3.12" 2>/dev/null; then
    echo "✓ Python 3.12 would be accepted (this is wrong!)"
else
    echo "✗ Python 3.12 would be rejected (correct)"
fi

# Simulate Python 3.13 (should fail)
echo "Simulating Python 3.13:"
if check_python_version "python3.13" 2>/dev/null; then
    echo "✓ Python 3.13 would be accepted (this is wrong!)"
else
    echo "✗ Python 3.13 would be rejected (correct)"
fi

echo ""
echo "Test completed!" 