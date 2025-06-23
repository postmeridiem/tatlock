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

# --- LLM and API Keys ---
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3-cortex:latest")  # Updated default model

# --- Google Search API Credentials ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")  # CSE stands for Custom Search Engine

# --- Database Paths ---
SYSTEM_DB_PATH = os.getenv("SYSTEM_DB", "hippocampus/system.db")     # Authentication database

# --- Server Configuration ---
HOSTNAME = os.getenv("HOSTNAME", "localhost")
PORT = int(os.getenv("PORT", "8000"))

# --- Security Configuration ---
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")

# --- Error Checking ---
if not OPENWEATHER_API_KEY:
    logger.warning("WARNING: OPENWEATHER_API_KEY environment variable not set. Weather functionality will be disabled.")
if not GOOGLE_API_KEY:
    logger.warning("WARNING: GOOGLE_API_KEY environment variable not set. Web search functionality will be disabled.")
if not GOOGLE_CSE_ID:
    logger.warning("WARNING: GOOGLE_CSE_ID environment variable not set. Web search functionality will be disabled.")

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