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

# Import ollama at module level to avoid import issues
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    logger.warning("Ollama library not available - model management will be disabled")
    OLLAMA_AVAILABLE = False

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
        Set a system setting value. For ollama_model, download the model if not present and optionally remove the previous model.
        Args:
            setting_key (str): The setting key to update
            setting_value (str): The new setting value
            remove_previous (bool): If True, remove the previous model from disk (except initial model)
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            previous_value = self.get_setting(setting_key)
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
            # Ollama model management
            if setting_key == 'ollama_model' and OLLAMA_AVAILABLE:
                try:
                    # Download the new model if not present
                    models = ollama.list().get('models', [])
                    model_names = [m['name'] for m in models]
                    if setting_value not in model_names:
                        logger.info(f"Downloading Ollama model: {setting_value}")
                        ollama.pull(setting_value)
                    # Remove previous model if requested and not the initial model
                    initial_model = 'gemma3-cortex:latest'
                    if remove_previous and previous_value and previous_value != initial_model and previous_value != setting_value:
                        logger.info(f"Removing previous Ollama model: {previous_value}")
                        try:
                            ollama.delete(previous_value)
                        except Exception as e:
                            logger.warning(f"Failed to remove model {previous_value}: {e}")
                except Exception as e:
                    logger.error(f"Error managing Ollama model {setting_value}: {e}")
                    # Don't fail the setting update if Ollama operations fail
                    # The setting is still saved to the database
            elif setting_key == 'ollama_model' and not OLLAMA_AVAILABLE:
                logger.warning("Ollama library not available - skipping model management")
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
    
    def get_ollama_config(self) -> Dict[str, str]:
        """
        Get Ollama configuration settings.
        
        Returns:
            Dict[str, str]: Ollama configuration
        """
        return {
            'model': self.get_setting('ollama_model') or 'gemma3-cortex:latest',
            'host': self.get_setting('ollama_host') or 'http://localhost:11434',
            'timeout': self.get_setting('ollama_timeout') or '30'
        }
    
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

    def refresh_ollama_model_options(self) -> bool:
        """
        Fetch major Ollama models from the library repository and update settings_options.
        Focuses on well-known models that support function calling.
        Returns True if successful.
        """
        try:
            import requests
            import json
            
            # Major models that support function calling/tools
            # These are well-known models available in the Ollama library
            major_models = [
                # Gemma models (Google)
                {'name': 'gemma2:2b', 'display': 'Gemma2 2B (Google)', 'size': '1.4GB'},
                {'name': 'gemma2:7b', 'display': 'Gemma2 7B (Google)', 'size': '4.4GB'},
                {'name': 'gemma2:9b', 'display': 'Gemma2 9B (Google)', 'size': '5.6GB'},
                {'name': 'gemma2:27b', 'display': 'Gemma2 27B (Google)', 'size': '16.9GB'},
                
                # Llama models (Meta)
                {'name': 'llama3.2:3b', 'display': 'Llama3.2 3B (Meta)', 'size': '1.8GB'},
                {'name': 'llama3.2:8b', 'display': 'Llama3.2 8B (Meta)', 'size': '4.7GB'},
                {'name': 'llama3.2:70b', 'display': 'Llama3.2 70B (Meta)', 'size': '40.1GB'},
                
                # Mistral models
                {'name': 'mistral:7b', 'display': 'Mistral 7B', 'size': '4.1GB'},
                {'name': 'mixtral:8x7b', 'display': 'Mixtral 8x7B', 'size': '26.2GB'},
                
                # Code models
                {'name': 'codellama:7b', 'display': 'Code Llama 7B', 'size': '3.8GB'},
                {'name': 'codellama:13b', 'display': 'Code Llama 13B', 'size': '7.3GB'},
                {'name': 'codellama:34b', 'display': 'Code Llama 34B', 'size': '18.6GB'},
                
                # Specialized models
                {'name': 'llama3.2:3b-instruct', 'display': 'Llama3.2 3B Instruct', 'size': '1.8GB'},
                {'name': 'llama3.2:8b-instruct', 'display': 'Llama3.2 8B Instruct', 'size': '4.7GB'},
                {'name': 'llama3.2:70b-instruct', 'display': 'Llama3.2 70B Instruct', 'size': '40.1GB'},
                
                # Phi models (Microsoft)
                {'name': 'phi3:mini', 'display': 'Phi-3 Mini (Microsoft)', 'size': '1.8GB'},
                {'name': 'phi3:small', 'display': 'Phi-3 Small (Microsoft)', 'size': '2.1GB'},
                {'name': 'phi3:medium', 'display': 'Phi-3 Medium (Microsoft)', 'size': '4.2GB'},
                
                # Neural Chat models
                {'name': 'neural-chat:7b', 'display': 'Neural Chat 7B', 'size': '4.1GB'},
                {'name': 'neural-chat:8b', 'display': 'Neural Chat 8B', 'size': '4.7GB'},
                
                # Qwen models (Alibaba)
                {'name': 'qwen2.5:0.5b', 'display': 'Qwen2.5 0.5B (Alibaba)', 'size': '0.3GB'},
                {'name': 'qwen2.5:1.5b', 'display': 'Qwen2.5 1.5B (Alibaba)', 'size': '0.9GB'},
                {'name': 'qwen2.5:3b', 'display': 'Qwen2.5 3B (Alibaba)', 'size': '1.7GB'},
                {'name': 'qwen2.5:7b', 'display': 'Qwen2.5 7B (Alibaba)', 'size': '4.1GB'},
                {'name': 'qwen2.5:14b', 'display': 'Qwen2.5 14B (Alibaba)', 'size': '8.1GB'},
                {'name': 'qwen2.5:32b', 'display': 'Qwen2.5 32B (Alibaba)', 'size': '18.6GB'},
                {'name': 'qwen2.5:72b', 'display': 'Qwen2.5 72B (Alibaba)', 'size': '41.9GB'},
                
                # Default model (keep for compatibility)
                {'name': 'gemma3-cortex:latest', 'display': 'Gemma3 Cortex (Default)', 'size': 'N/A'}
            ]
            
            # Convert to options format
            options = []
            for model in major_models:
                options.append({
                    'option_value': model['name'],
                    'option_label': f"{model['display']} ({model['size']})",
                    'enabled': True
                })
            
            # Also check for locally installed models and add them if not already in the list
            try:
                import ollama
                local_models = ollama.list().get('models', [])
                for local_model in local_models:
                    model_name = local_model.get('name')
                    if model_name and not any(opt['option_value'] == model_name for opt in options):
                        # Add locally installed model that's not in our major models list
                        size = local_model.get('size', 'Unknown')
                        options.append({
                            'option_value': model_name,
                            'option_label': f"{model_name} (Local - {size})",
                            'enabled': True
                        })
            except Exception as e:
                logger.warning(f"Could not fetch local models: {e}")
            
            # Sort options: major models first, then local models
            major_model_names = {model['name'] for model in major_models}
            options.sort(key=lambda x: (x['option_value'] not in major_model_names, x['option_label']))
            
            return self.set_setting_options('ollama_model', options)
            
        except Exception as e:
            logger.error(f"Error refreshing Ollama model options: {e}")
            # Add default option if refresh fails
            default_options = [{
                'option_value': 'gemma3-cortex:latest',
                'option_label': 'gemma3-cortex:latest (default)',
                'enabled': True
            }]
            return self.set_setting_options('ollama_model', default_options)

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