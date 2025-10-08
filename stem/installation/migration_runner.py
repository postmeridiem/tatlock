"""
stem/installation/migration_runner.py

Version-based database migration system for Tatlock.

This module handles automatic database schema migrations during application startup.
It compares the current DB_VERSION in config.py with the version in pyproject.toml,
and applies any pending migrations from database_migrations.md.

Migration Flow:
1. Check current DB_VERSION vs pyproject.toml version
2. If versions match, skip migration
3. If versions differ, enter pre-boot admin mode
4. Parse database_migrations.md for relevant SQL blocks
5. Apply migrations to system.db first
6. Apply migrations to all user databases
7. Run integrity checks on each database
8. Update config.py with new DB_VERSION
9. Continue normal startup

Rollback Behavior:
- DEBUG=true: Halt on failure with detailed error
- DEBUG=false: Rollback transaction and log error (continue startup)
"""

import os
import sys
import sqlite3
import logging
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Import configuration
try:
    import config
    from hippocampus.user_database import get_all_usernames
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


class MigrationError(Exception):
    """Raised when a migration fails"""
    pass


class MigrationRunner:
    """Handles database schema migrations based on version numbers"""

    def __init__(self):
        self.migrations_file = Path(__file__).parent / "database_migrations.md"
        self.config_file = Path(__file__).parent.parent.parent / "config.py"

    def get_current_db_version(self) -> str:
        """Get current database version from config.py"""
        return config.DB_VERSION

    def get_target_version(self) -> str:
        """Get target version from pyproject.toml"""
        return config.APP_VERSION

    def versions_match(self) -> bool:
        """Check if current DB version matches target version"""
        current = self.get_current_db_version()
        target = self.get_target_version()
        return current == target

    def parse_migrations(self, from_version: str, to_version: str) -> Dict[str, List[str]]:
        """
        Parse database_migrations.md and extract SQL blocks for version range.

        Args:
            from_version: Current database version
            to_version: Target version from pyproject.toml

        Returns:
            Dictionary with 'system' and 'user' keys containing SQL block lists
        """
        if not self.migrations_file.exists():
            raise MigrationError(f"Migrations file not found: {self.migrations_file}")

        migrations = {
            'system': [],
            'user': []
        }

        with open(self.migrations_file, 'r') as f:
            content = f.read()

        # Pattern to find SQL blocks with version tags inside markdown code fences
        # Example: ```sql\n-- [system:0.3.19→0.3.20:start] ... -- [system:0.3.19→0.3.20:end]\n```
        system_pattern = rf'```sql\s*-- \[system:{re.escape(from_version)}→{re.escape(to_version)}:start\](.*?)-- \[system:{re.escape(from_version)}→{re.escape(to_version)}:end\]\s*```'
        user_pattern = rf'```sql\s*-- \[user:{re.escape(from_version)}→{re.escape(to_version)}:start\](.*?)-- \[user:{re.escape(from_version)}→{re.escape(to_version)}:end\]\s*```'

        # Find system migrations
        system_matches = re.findall(system_pattern, content, re.DOTALL)
        for match in system_matches:
            sql = match.strip()
            # Remove comment lines and check if there's actual SQL
            sql_lines = [line for line in sql.split('\n') if line.strip() and not line.strip().startswith('--')]
            if sql_lines:
                migrations['system'].append(sql)

        # Find user migrations
        user_matches = re.findall(user_pattern, content, re.DOTALL)
        for match in user_matches:
            sql = match.strip()
            # Remove comment lines and check if there's actual SQL
            sql_lines = [line for line in sql.split('\n') if line.strip() and not line.strip().startswith('--')]
            if sql_lines:
                migrations['user'].append(sql)

        logger.info(f"Parsed migrations {from_version}→{to_version}: "
                   f"{len(migrations['system'])} system, {len(migrations['user'])} user")

        return migrations

    def apply_migrations_to_system_db(self, migrations: List[str]) -> None:
        """
        Apply migrations to system.db

        Args:
            migrations: List of SQL statements to execute

        Raises:
            MigrationError: If migration fails
        """
        if not migrations:
            logger.info("No system database migrations to apply")
            return

        db_path = config.SYSTEM_DB_PATH
        logger.info(f"Applying {len(migrations)} migration(s) to system.db")

        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Start transaction
            cursor.execute("BEGIN")

            for idx, sql in enumerate(migrations, 1):
                logger.debug(f"Executing system migration {idx}/{len(migrations)}")
                cursor.executescript(sql)

            conn.commit()
            logger.info("System database migrations applied successfully")

        except Exception as e:
            if conn:
                conn.rollback()
            raise MigrationError(f"System database migration failed: {e}")
        finally:
            if conn:
                conn.close()

    def apply_migrations_to_user_db(self, username: str, migrations: List[str]) -> None:
        """
        Apply migrations to a user's longterm database

        Args:
            username: Username whose database to migrate
            migrations: List of SQL statements to execute

        Raises:
            MigrationError: If migration fails
        """
        if not migrations:
            return

        from hippocampus.user_database import ensure_user_database

        db_path = ensure_user_database(username)
        logger.info(f"Applying {len(migrations)} migration(s) to {username}_longterm.db")

        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Start transaction
            cursor.execute("BEGIN")

            for idx, sql in enumerate(migrations, 1):
                logger.debug(f"Executing user migration {idx}/{len(migrations)} for {username}")
                cursor.executescript(sql)

            conn.commit()
            logger.info(f"User database migrations applied successfully for {username}")

        except Exception as e:
            if conn:
                conn.rollback()
            raise MigrationError(f"User database migration failed for {username}: {e}")
        finally:
            if conn:
                conn.close()

    def run_integrity_checks(self, db_path: str, db_name: str) -> bool:
        """
        Run integrity checks on a database after migration

        Args:
            db_path: Path to database file
            db_name: Name of database (for logging)

        Returns:
            True if all checks pass, False otherwise
        """
        logger.info(f"Running integrity checks on {db_name}")

        conn = None
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # PRAGMA integrity_check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            if result[0] != 'ok':
                logger.error(f"Integrity check failed for {db_name}: {result[0]}")
                return False

            # PRAGMA foreign_key_check
            cursor.execute("PRAGMA foreign_key_check")
            violations = cursor.fetchall()
            if violations:
                logger.error(f"Foreign key violations in {db_name}: {violations}")
                return False

            logger.info(f"All integrity checks passed for {db_name}")
            return True

        except Exception as e:
            logger.error(f"Integrity check error for {db_name}: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def update_config_version(self, new_version: str) -> None:
        """
        Update DB_VERSION in config.py

        Args:
            new_version: New version string to write

        Raises:
            MigrationError: If update fails
        """
        logger.info(f"Updating config.py DB_VERSION to {new_version}")

        try:
            with open(self.config_file, 'r') as f:
                content = f.read()

            # Replace DB_VERSION line
            pattern = r'DB_VERSION = "[^"]*"'
            replacement = f'DB_VERSION = "{new_version}"'
            new_content = re.sub(pattern, replacement, content)

            if new_content == content:
                raise MigrationError("Failed to find DB_VERSION in config.py")

            with open(self.config_file, 'w') as f:
                f.write(new_content)

            logger.info(f"Updated DB_VERSION to {new_version}")

        except Exception as e:
            raise MigrationError(f"Failed to update config.py: {e}")

    def migrate_if_needed(self) -> None:
        """
        Main migration orchestrator - called at application startup.

        Checks version mismatch and applies migrations if needed.
        Handles rollback based on DEBUG_MODE setting.
        """
        current = self.get_current_db_version()
        target = self.get_target_version()

        if self.versions_match():
            logger.info(f"Database version {current} matches target, no migration needed")
            return

        logger.info(f"=" * 80)
        logger.info(f"DATABASE MIGRATION REQUIRED: {current} → {target}")
        logger.info(f"=" * 80)
        logger.info("Entering PRE-BOOT ADMIN MODE (no user connections)")

        try:
            # Parse migrations
            migrations = self.parse_migrations(current, target)

            # Apply to system.db
            self.apply_migrations_to_system_db(migrations['system'])

            # Verify system.db integrity
            if not self.run_integrity_checks(config.SYSTEM_DB_PATH, 'system.db'):
                raise MigrationError("System database integrity check failed after migration")

            # Apply to all user databases
            usernames = get_all_usernames()
            logger.info(f"Migrating {len(usernames)} user database(s)")

            for username in usernames:
                self.apply_migrations_to_user_db(username, migrations['user'])

                # Verify user database integrity
                from hippocampus.user_database import ensure_user_database
                user_db_path = ensure_user_database(username)
                if not self.run_integrity_checks(user_db_path, f'{username}_longterm.db'):
                    raise MigrationError(f"User database integrity check failed for {username}")

            # Update config.py
            self.update_config_version(target)

            logger.info(f"=" * 80)
            logger.info(f"MIGRATION COMPLETE: {current} → {target}")
            logger.info(f"=" * 80)

        except MigrationError as e:
            logger.error(f"Migration failed: {e}")

            # Handle based on DEBUG_MODE
            if config.DEBUG_MODE:
                logger.critical("DEBUG_MODE=true: Halting startup due to migration failure")
                raise
            else:
                logger.error("DEBUG_MODE=false: Migration failed but continuing startup")
                logger.error("WARNING: Database schema may be inconsistent!")
                # In production, we continue but log the error


# Global instance
_migration_runner = None

def get_migration_runner() -> MigrationRunner:
    """Get or create the global MigrationRunner instance"""
    global _migration_runner
    if _migration_runner is None:
        _migration_runner = MigrationRunner()
    return _migration_runner


def migrate_if_needed() -> None:
    """
    Entry point for migration system - call this at application startup.

    Usage in main.py:
        from stem.installation.migration_runner import migrate_if_needed

        # BEFORE creating FastAPI app
        migrate_if_needed()

        # NOW start application
        app = FastAPI(...)
    """
    runner = get_migration_runner()
    runner.migrate_if_needed()
