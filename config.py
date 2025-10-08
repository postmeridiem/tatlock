"""
config.py

Configuration and environment variable loading for Tatlock project.
Handles API keys, database paths, and LLM model configuration for
the conversational AI system with authentication and user management.
"""

import os
import logging
from dotenv import load_dotenv
import sys

# Set up logging for this module
logger = logging.getLogger(__name__)

load_dotenv()

# Import system settings manager
try:
    from stem.system_settings import system_settings_manager
    USE_DATABASE_SETTINGS = True
except ImportError:
    # Fallback to environment variables if system settings not available
    USE_DATABASE_SETTINGS = False
    logger.warning("System settings manager not available, using environment variables")

def get_setting_from_db_or_env(setting_key: str, env_key: str, default_value: str = "") -> str:
    """
    Get a setting value from database if available, otherwise from environment variable.
    
    Args:
        setting_key (str): Database setting key
        env_key (str): Environment variable key
        default_value (str): Default value if neither source has the setting
        
    Returns:
        str: The setting value
    """
    if USE_DATABASE_SETTINGS:
        try:
            db_value = system_settings_manager.get_setting(setting_key)
            if db_value is not None:
                return db_value
        except Exception as e:
            logger.warning(f"Failed to get {setting_key} from database: {e}")
    
    # Fallback to environment variable
    return os.getenv(env_key, default_value)

# --- LLM Configuration ---
# Model and hardware tier are pre-computed during installation for efficiency
def load_hardware_configuration() -> tuple[str, str]:
    """
    Load pre-computed hardware configuration from installation.
    Returns tuple of (model, performance_tier).
    """
    try:
        # Import the hardware config file created during installation
        import hardware_config

        model = hardware_config.RECOMMENDED_MODEL
        tier = hardware_config.PERFORMANCE_TIER

        logger.info(f"Loaded hardware config: {model} (tier: {tier})")
        return model, tier

    except ImportError:
        logger.warning("Hardware config file not found, falling back to runtime detection")
        # Fallback to runtime hardware detection if config file missing
        try:
            from parietal.hardware import classify_hardware_performance
            classification = classify_hardware_performance()
            model = classification.get("recommended_model", "gemma2:2b")
            tier = classification.get("performance_tier", "low")
            return model, tier
        except Exception as e:
            logger.warning(f"Hardware classification failed: {e}")
            fallback_model = os.getenv("OLLAMA_MODEL", "gemma2:2b")
            return fallback_model, "unknown"
    except Exception as e:
        logger.error(f"Error loading hardware config: {e}")
        fallback_model = os.getenv("OLLAMA_MODEL", "gemma2:2b")
        return fallback_model, "unknown"

# Global hardware configuration - loaded once at startup
OLLAMA_MODEL, HARDWARE_PERFORMANCE_TIER = load_hardware_configuration()
OLLAMA_HOST = get_setting_from_db_or_env("ollama_host", "OLLAMA_HOST", "http://localhost:11434")
OLLAMA_TIMEOUT = int(get_setting_from_db_or_env("ollama_timeout", "OLLAMA_TIMEOUT", "30"))

# --- Google Search API Credentials ---
GOOGLE_API_KEY = get_setting_from_db_or_env("google_api_key", "GOOGLE_API_KEY")
GOOGLE_CSE_ID = get_setting_from_db_or_env("google_cse_id", "GOOGLE_CSE_ID")

# --- Weather API Key ---
OPENWEATHER_API_KEY = get_setting_from_db_or_env("openweather_api_key", "OPENWEATHER_API_KEY")

# --- Database Paths ---
SYSTEM_DB_PATH = os.getenv("SYSTEM_DB", "hippocampus/system.db")     # Authentication database

# --- Server Configuration ---
HOSTNAME = get_setting_from_db_or_env("hostname", "HOSTNAME", "localhost")
PORT = int(get_setting_from_db_or_env("port", "PORT", "8000"))
ALLOWED_ORIGINS = get_setting_from_db_or_env("allowed_origins", "ALLOWED_ORIGINS", "http://localhost:8000").split(",")

# --- Security Configuration ---
SESSION_TIMEOUT = int(get_setting_from_db_or_env("session_timeout", "SESSION_TIMEOUT", "3600"))
MAX_LOGIN_ATTEMPTS = int(get_setting_from_db_or_env("max_login_attempts", "MAX_LOGIN_ATTEMPTS", "5"))
PASSWORD_MIN_LENGTH = int(get_setting_from_db_or_env("password_min_length", "PASSWORD_MIN_LENGTH", "8"))

# --- Debug Configuration ---
DEBUG_MODE = get_setting_from_db_or_env("debug_mode", "DEBUG_MODE", "false").lower() == "true"

# --- Error Checking ---
if not OPENWEATHER_API_KEY:
    logger.warning("WARNING: OPENWEATHER_API_KEY not set. Weather functionality will be disabled.")
if not GOOGLE_API_KEY:
    logger.warning("WARNING: GOOGLE_API_KEY not set. Web search functionality will be disabled.")
if not GOOGLE_CSE_ID:
    logger.warning("WARNING: GOOGLE_CSE_ID not set. Web search functionality will be disabled.")

# For example, if you want to use a different database for testing
if "pytest" in sys.modules:
    # Use an in-memory SQLite database for testing
    DATABASE_URL = "sqlite:///:memory:"
else:
    # Use a file-based SQLite database for development/production
    DATABASE_URL = "sqlite:///./tatlock.db"

"""
Provides application metadata, such as the version number,
read from a central location (pyproject.toml).
"""
# Use tomllib if available (Python 3.11+), otherwise use tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli
    except ImportError:
        tomli = None

def get_app_version():
    """Reads the application version from pyproject.toml."""
    try:
        # The project root is one level up from this file's location
        project_root = os.path.dirname(os.path.abspath(__file__))
        toml_path = os.path.join(project_root, 'pyproject.toml')

        if not os.path.exists(toml_path):
            # Fallback for when the script is run from a different working directory
            # This happens in some testing scenarios
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            toml_path = os.path.join(project_root, 'pyproject.toml')


        if sys.version_info >= (3, 11):
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
        elif tomli:
            with open(toml_path, "rb") as f:
                data = tomli.load(f)
        else:
            # This is a fallback if tomli is not installed on Python < 3.11
            return "0.0.0-dev (tomli not installed)"
            
        return data["project"]["version"]
    except (FileNotFoundError, KeyError):
        # Fallback for when pyproject.toml is not found or malformed
        return "0.0.0-dev (pyproject.toml not found)"

APP_VERSION = get_app_version()

# --- Database Version ---
# This tracks the current database schema version. It is automatically updated by the
# migration system during startup when pyproject.toml version is newer.
# WARNING: Do not manually edit this value - it is managed by migration_runner.py
DB_VERSION = "0.3.21"