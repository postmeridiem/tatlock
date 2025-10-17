#!/usr/bin/env bash
# security_scan.sh
# Comprehensive security scanning for Tatlock project

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔒 Tatlock Security Scan${NC}"
echo "=================================="

# Check if we're in the correct directory (stem/scripts)
if [ ! -f "../../main.py" ] || [ ! -d "../../stem" ]; then
    echo -e "${RED}Error: This script must be run from the stem/scripts directory.${NC}"
    echo "Usage: cd stem/scripts && ./security_scan.sh"
    exit 1
fi

# Change to project root directory
cd ../..

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source .venv/bin/activate
elif [ -d "test_env" ]; then
    echo -e "${BLUE}Activating test environment...${NC}"
    source test_env/bin/activate
else
    echo -e "${YELLOW}Warning: No virtual environment found. Using system Python.${NC}"
fi

echo -e "\n${BLUE}1. Running Safety Check (Vulnerability Scanning)${NC}"
echo "----------------------------------------"
if command -v safety &> /dev/null; then
    safety check --json --output safety-report.json
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Safety check passed - no known vulnerabilities found${NC}"
    else
        echo -e "${RED}✗ Safety check failed - vulnerabilities found${NC}"
        echo "Check safety-report.json for details"
    fi
else
    echo -e "${YELLOW}⚠ Safety not installed. Run: pip install safety${NC}"
fi

echo -e "\n${BLUE}2. Running Bandit (Code Security Analysis)${NC}"
echo "----------------------------------------"
if command -v bandit &> /dev/null; then
    bandit -r . -f json -o bandit-report.json -ll
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Bandit scan passed - no security issues found${NC}"
    else
        echo -e "${RED}✗ Bandit scan found security issues${NC}"
        echo "Check bandit-report.json for details"
    fi
else
    echo -e "${YELLOW}⚠ Bandit not installed. Run: pip install bandit${NC}"
fi

echo -e "\n${BLUE}3. Running pip-audit (Dependency Auditing)${NC}"
echo "----------------------------------------"
if command -v pip-audit &> /dev/null; then
    pip-audit --format=json --output=audit-report.json
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ pip-audit passed - no vulnerable dependencies found${NC}"
    else
        echo -e "${RED}✗ pip-audit found vulnerable dependencies${NC}"
        echo "Check audit-report.json for details"
    fi
else
    echo -e "${YELLOW}⚠ pip-audit not installed. Run: pip install pip-audit${NC}"
fi

echo -e "\n${BLUE}4. Checking Dependency Pinning${NC}"
echo "----------------------------------------"
unpinned_deps=0
if [ -f "requirements.txt" ]; then
    while IFS= read -r line; do
        if [[ ! "$line" =~ ^# ]] && [[ ! "$line" =~ ^$ ]] && [[ ! "$line" =~ == ]]; then
            if [[ ! "$line" =~ ^- ]]; then
                echo -e "${RED}✗ Unpinned dependency: $line${NC}"
                unpinned_deps=$((unpinned_deps + 1))
            fi
        fi
    done < requirements.txt
    
    if [ $unpinned_deps -eq 0 ]; then
        echo -e "${GREEN}✓ All dependencies are pinned to specific versions${NC}"
    else
        echo -e "${RED}✗ Found $unpinned_deps unpinned dependencies${NC}"
    fi
fi

echo -e "\n${BLUE}5. Checking for Lock File${NC}"
echo "----------------------------------------"
if [ -f "requirements-lock.txt" ]; then
    echo -e "${GREEN}✓ Lock file found: requirements-lock.txt${NC}"
    lock_count=$(wc -l < requirements-lock.txt)
    echo "   Contains $lock_count pinned dependencies"
else
    echo -e "${YELLOW}⚠ No lock file found. Consider creating requirements-lock.txt${NC}"
fi

echo -e "\n${BLUE}6. Python Version Check${NC}"
echo "----------------------------------------"
python_version=$(python --version 2>&1 | cut -d' ' -f2)
if [[ "$python_version" == "3.10"* ]]; then
    echo -e "${GREEN}✓ Python version $python_version is correct (3.10.x)${NC}"
else
    echo -e "${RED}✗ Python version $python_version is not 3.10.x${NC}"
    echo "   Tatlock requires Python 3.10 exactly"
fi

echo -e "\n${BLUE}Security Scan Summary${NC}"
echo "====================="
if [ $unpinned_deps -eq 0 ] && [[ "$python_version" == "3.10"* ]]; then
    echo -e "${GREEN}✓ Security scan completed successfully${NC}"
    echo -e "${GREEN}✓ All security checks passed${NC}"
    exit 0
else
    echo -e "${RED}✗ Security scan found issues${NC}"
    echo -e "${YELLOW}Please review the reports and fix any issues${NC}"
    exit 1
fi
