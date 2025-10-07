#!/bin/bash

# migrate_database.sh
# CLI tool for manually triggering database migrations
#
# Usage:
#   ./migrate_database.sh [options]
#
# Options:
#   --check      Check current and target versions without migrating
#   --force      Force migration even if versions match
#   --help       Show this help message

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show help
show_help() {
    cat << EOF
Database Migration Tool for Tatlock

Usage: $0 [options]

Options:
    --check      Check current and target versions without migrating
    --force      Force migration even if versions match
    --help       Show this help message

Examples:
    $0 --check              # Check versions only
    $0                      # Run migration if needed
    $0 --force              # Force migration

Description:
    This tool manages database schema migrations for Tatlock.
    It compares the current DB_VERSION in config.py with the version
    in pyproject.toml and applies any pending migrations from
    database_migrations.md.

    Migrations are applied in this order:
    1. System database (system.db)
    2. All user databases ({username}_longterm.db)
    3. Integrity checks on each database
    4. Update config.py with new DB_VERSION

    Rollback behavior:
    - DEBUG=true:  Halt on failure with detailed error
    - DEBUG=false: Rollback transaction and continue

EOF
    exit 0
}

# Parse arguments
CHECK_ONLY=false
FORCE_MIGRATION=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --check)
            CHECK_ONLY=true
            shift
            ;;
        --force)
            FORCE_MIGRATION=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    print_error "Virtual environment not found at $PROJECT_ROOT/.venv"
    print_info "Please run ./install_tatlock.sh first"
    exit 1
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source "$PROJECT_ROOT/.venv/bin/activate"

# Change to project root
cd "$PROJECT_ROOT"

# Create Python script to check/run migrations
PYTHON_SCRIPT=$(cat <<'PYTHON_EOF'
import sys
sys.path.insert(0, '.')

from stem.installation.migration_runner import get_migration_runner
import config

runner = get_migration_runner()
current = runner.get_current_db_version()
target = runner.get_target_version()

print(f"Current DB Version: {current}")
print(f"Target Version:     {target}")

if current == target:
    print("\n✓ Database version is up to date")
    sys.exit(0)
else:
    print(f"\n⚠ Migration needed: {current} → {target}")
    sys.exit(1)
PYTHON_EOF
)

# Check versions
print_info "Checking database versions..."
echo ""

if python3 -c "$PYTHON_SCRIPT"; then
    VERSION_MATCH=true
else
    VERSION_MATCH=false
fi

echo ""

# If check only, exit here
if [ "$CHECK_ONLY" = true ]; then
    if [ "$VERSION_MATCH" = true ]; then
        print_success "No migration needed"
        exit 0
    else
        print_warning "Migration required"
        print_info "Run without --check flag to apply migrations"
        exit 0
    fi
fi

# If versions match and not forcing, exit
if [ "$VERSION_MATCH" = true ] && [ "$FORCE_MIGRATION" = false ]; then
    print_success "Database is up to date, no migration needed"
    exit 0
fi

# Show migration plan
print_info "Migration plan:"
echo ""
echo "  1. Parse database_migrations.md for SQL blocks"
echo "  2. Apply migrations to system.db"
echo "  3. Apply migrations to all user databases"
echo "  4. Run integrity checks"
echo "  5. Update config.py with new version"
echo ""

# Confirm migration
if [ "$FORCE_MIGRATION" = false ]; then
    read -p "Proceed with migration? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Migration cancelled"
        exit 0
    fi
fi

# Run migration
print_info "Running database migration..."
echo ""

MIGRATION_SCRIPT=$(cat <<'PYTHON_EOF'
import sys
sys.path.insert(0, '.')

from stem.installation.migration_runner import migrate_if_needed

try:
    migrate_if_needed()
    print("\n✓ Migration completed successfully")
    sys.exit(0)
except Exception as e:
    print(f"\n✗ Migration failed: {e}")
    sys.exit(1)
PYTHON_EOF
)

if python3 -c "$MIGRATION_SCRIPT"; then
    print_success "Database migration completed successfully!"
    echo ""
    print_info "New database version: $(python3 -c 'import config; print(config.DB_VERSION)')"
    exit 0
else
    print_error "Database migration failed"
    print_warning "Check the logs above for details"
    exit 1
fi
