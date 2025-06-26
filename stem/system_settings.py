"""
stem/system_settings.py

System settings management for Tatlock.
Provides functions to read, write, and manage system configuration settings
stored in the system database.
"""

import sqlite3
import logging
import os
from typing import Dict, List, Optional, Any

# Set up logging for this module
logger = logging.getLogger(__name__)

class SystemSettingsManager:
    """
    Manages system settings stored in the system database.
    Provides methods to read, write, and manage configuration settings.
    """
    
    def __init__(self, db_path: str = "hippocampus/system.db"):
        """
        Initialize the system settings manager.
        
        Args:
            db_path (str): Path to the system database file
        """
        self.db_path = db_path
    
    def get_setting(self, setting_key: str) -> Optional[str]:
        """
        Get a system setting value by key.
        
        Args:
            setting_key (str): The setting key to retrieve
            
        Returns:
            Optional[str]: The setting value, or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT setting_value FROM system_settings WHERE setting_key = ?",
                (setting_key,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            logger.error(f"Error getting setting {setting_key}: {e}")
            return None
    
    def set_setting(self, setting_key: str, setting_value: str, remove_previous: bool = False) -> bool:
        """
        Set a system setting value.
        Args:
            setting_key (str): The setting key to update
            setting_value (str): The new setting value
            remove_previous (bool): Ignored parameter kept for compatibility
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE system_settings 
                SET setting_value = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE setting_key = ?
                """,
                (setting_value, setting_key)
            )
            if cursor.rowcount == 0:
                cursor.execute(
                    """
                    INSERT INTO system_settings (setting_key, setting_value, updated_at) 
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """,
                    (setting_key, setting_value)
                )
            conn.commit()
            conn.close()
            logger.info(f"Updated setting {setting_key}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting {setting_key}: {e}")
            return False
    
    def get_all_settings(self) -> List[Dict[str, Any]]:
        """
        Get all system settings with their categories.
        
        Returns:
            List[Dict[str, Any]]: List of settings with category information
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    s.setting_key,
                    s.setting_value,
                    s.setting_type,
                    s.description,
                    s.is_sensitive,
                    s.created_at,
                    s.updated_at,
                    c.category_name,
                    c.display_name as category_display_name,
                    c.description as category_description,
                    scm.sort_order
                FROM system_settings s
                LEFT JOIN system_setting_categories_map scm ON s.setting_key = scm.setting_key
                LEFT JOIN system_setting_categories c ON scm.category_id = c.id
                ORDER BY c.sort_order, scm.sort_order, s.setting_key
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            settings = []
            for row in rows:
                setting = {
                    'setting_key': row[0],
                    'setting_value': row[1],
                    'setting_type': row[2],
                    'description': row[3],
                    'is_sensitive': bool(row[4]),
                    'created_at': row[5],
                    'updated_at': row[6],
                    'category_name': row[7],
                    'category_display_name': row[8],
                    'category_description': row[9],
                    'sort_order': row[10]
                }
                settings.append(setting)
            
            return settings
            
        except Exception as e:
            logger.error(f"Error getting all settings: {e}")
            return []
    
    def get_settings_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all system settings organized by category.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Settings organized by category
        """
        settings = self.get_all_settings()
        categorized = {}
        
        for setting in settings:
            category = setting.get('category_name', 'uncategorized')
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(setting)
        
        return categorized
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get all system setting categories.
        
        Returns:
            List[Dict[str, Any]]: List of categories
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id,
                    category_name,
                    display_name,
                    description,
                    sort_order,
                    created_at
                FROM system_setting_categories
                ORDER BY sort_order, display_name
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            categories = []
            for row in rows:
                category = {
                    'id': row[0],
                    'category_name': row[1],
                    'display_name': row[2],
                    'description': row[3],
                    'sort_order': row[4],
                    'created_at': row[5]
                }
                categories.append(category)
            
            return categories
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    def create_category(self, category_name: str, display_name: str, description: str = "", sort_order: int = 0) -> bool:
        """
        Create a new system setting category.
        
        Args:
            category_name (str): Unique category name
            display_name (str): Human-readable display name
            description (str): Category description
            sort_order (int): Sort order for display
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO system_setting_categories (category_name, display_name, description, sort_order)
                VALUES (?, ?, ?, ?)
                """,
                (category_name, display_name, description, sort_order)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created category {category_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating category {category_name}: {e}")
            return False
    
    def delete_category(self, category_name: str) -> bool:
        """
        Delete a system setting category.
        
        Args:
            category_name (str): The category name to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # First, remove all settings from this category
            cursor.execute("""
                DELETE FROM system_setting_categories_map 
                WHERE category_id = (SELECT id FROM system_setting_categories WHERE category_name = ?)
            """, (category_name,))
            
            # Then delete the category
            cursor.execute(
                "DELETE FROM system_setting_categories WHERE category_name = ?",
                (category_name,)
            )
            
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted category {category_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting category {category_name}: {e}")
            return False
    
    def get_api_keys(self) -> Dict[str, str]:
        """
        Get API key settings.
        
        Returns:
            Dict[str, str]: API key configuration
        """
        return {
            'openweather_api_key': self.get_setting('openweather_api_key') or '',
            'google_api_key': self.get_setting('google_api_key') or '',
            'google_cse_id': self.get_setting('google_cse_id') or ''
        }
    
    def get_server_config(self) -> Dict[str, str]:
        """
        Get server configuration settings.
        
        Returns:
            Dict[str, str]: Server configuration
        """
        return {
            'hostname': self.get_setting('hostname') or 'localhost',
            'port': self.get_setting('port') or '8000',
            'allowed_origins': self.get_setting('allowed_origins') or 'http://localhost:8000'
        }

    def get_setting_options(self, setting_key: str) -> list[dict]:
        """
        Get allowed options for a setting from the settings_options table.
        Returns a list of dicts with option_value and option_label.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT option_value, option_label FROM settings_options WHERE setting_key = ? AND enabled = 1 ORDER BY sort_order, option_label",
                (setting_key,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {"option_value": row[0], "option_label": row[1] or row[0]} for row in rows
            ]
        except Exception as e:
            logger.error(f"Error getting options for {setting_key}: {e}")
            return []

    def set_setting_options(self, setting_key: str, options: list[dict]) -> bool:
        """
        Set allowed options for a setting in the settings_options table.
        Each option is a dict with option_value, option_label, and optional sort_order/enabled.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Remove old options
            cursor.execute(
                "DELETE FROM settings_options WHERE setting_key = ?",
                (setting_key,)
            )
            # Insert new options
            for i, opt in enumerate(options):
                cursor.execute(
                    "INSERT INTO settings_options (setting_key, option_value, option_label, sort_order, enabled) VALUES (?, ?, ?, ?, ?)",
                    (
                        setting_key,
                        opt["option_value"],
                        opt.get("option_label", opt["option_value"]),
                        opt.get("sort_order", i),
                        int(opt.get("enabled", True)),
                    )
                )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error setting options for {setting_key}: {e}")
            return False

    def update_tool_status_based_on_api_keys(self) -> bool:
        """
        Update tool enabled status based on current API key availability.
        This should be called when API keys are updated through the admin interface.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from stem.installation.database_setup import update_tool_status_based_on_api_keys
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Call the function from database_setup
            update_tool_status_based_on_api_keys(cursor)
            
            conn.commit()
            conn.close()
            
            logger.info("Tool status updated based on API key availability")
            return True
            
        except Exception as e:
            logger.error(f"Error updating tool status: {e}")
            return False

# Global instance
system_settings_manager = SystemSettingsManager() 