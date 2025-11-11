#!/usr/bin/env python3
"""
docker-init.py

Docker initialization script for Tatlock.
Mirrors the install_tatlock.sh logic but in a non-interactive, container-friendly way.
Handles hardware classification, model selection, database initialization, and admin user creation.
"""

import os
import sys
import json
import uuid
import time
import logging
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def wait_for_ollama(ollama_host: str = "http://ollama:11434", max_attempts: int = 30, delay: int = 2):
    """Wait for Ollama service to be ready."""
    try:
        import requests
    except ImportError:
        logger.error("requests library not available, cannot check Ollama service")
        return False
    
    logger.info(f"Waiting for Ollama service at {ollama_host}...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Ollama service is ready!")
                return True
        except Exception as e:
            if attempt < max_attempts - 1:
                if attempt % 5 == 0:  # Log every 5th attempt
                    logger.info(f"Waiting for Ollama... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(delay)
            else:
                logger.warning(f"Ollama service not available after {max_attempts} attempts: {e}")
                return False
    return False

def classify_hardware():
    """Classify hardware and recommend model using the same logic as install script."""
    try:
        from parietal.hardware import classify_hardware_performance
        classification = classify_hardware_performance()
        
        recommended_model = classification.get("recommended_model", "mistral:7b")
        performance_tier = classification.get("performance_tier", "low")
        hardware_reason = " | ".join(classification.get("reasoning", ["Automatic hardware detection"]))
        hardware_summary = classification.get("hardware_summary", {})
        
        logger.info(f"Hardware classification: {performance_tier} tier → {recommended_model}")
        logger.info(f"Reasoning: {hardware_reason}")
        
        return {
            "recommended_model": recommended_model,
            "performance_tier": performance_tier,
            "hardware_reason": hardware_reason,
            "hardware_summary": hardware_summary,
            "selection_method": "auto"
        }
    except Exception as e:
        logger.warning(f"Hardware classification failed: {e}, using safe defaults")
        return {
            "recommended_model": "mistral:7b",
            "performance_tier": "low",
            "hardware_reason": f"Hardware detection failed: {e}, using safe fallback",
            "hardware_summary": {},
            "selection_method": "auto"
        }

def create_hardware_config(hw_config: dict):
    """Create hardware_config.py file."""
    hardware_config_path = Path("hardware_config.py")
    
    # Check if hardware_config.py already exists
    if hardware_config_path.exists():
        logger.info("hardware_config.py already exists, skipping creation")
        logger.info("To regenerate, delete hardware_config.py and restart the container")
        return
    
    config_content = f'''"""
Hardware Configuration for Tatlock
Generated automatically during Docker initialization - do not edit manually.
This file contains pre-computed hardware classification to avoid
runtime hardware detection overhead.
"""

# Hardware classification results
RECOMMENDED_MODEL = "{hw_config['recommended_model']}"
PERFORMANCE_TIER = "{hw_config['performance_tier']}"
HARDWARE_REASON = "{hw_config['hardware_reason']}"
SELECTION_METHOD = "{hw_config['selection_method']}"

# Hardware details (for reference)
HARDWARE_SUMMARY = {json.dumps(hw_config['hardware_summary'], separators=(',', ':'))}
'''
    
    hardware_config_path.write_text(config_content)
    logger.info(f"Created hardware_config.py with model: {hw_config['recommended_model']}")

def download_ollama_model(model: str, ollama_host: str = "http://ollama:11434"):
    """Download Ollama model if not already present."""
    import ollama
    
    # Configure Ollama client
    client = ollama.Client(host=ollama_host)
    
    try:
        # Check if model is already available
        models = client.list()
        model_names = [m['name'] for m in models.get('models', [])]
        
        if model in model_names:
            logger.info(f"Model {model} is already available, skipping download")
            return True
        
        logger.info(f"Downloading Ollama model: {model}...")
        
        # Handle special case for gemma3-cortex:latest
        if model == "gemma3-cortex:latest":
            logger.info("Setting up enhanced Gemma3 model...")
            try:
                # Try to pull the enhanced model
                client.pull("ebdm/gemma3-enhanced:12b")
                # Copy to gemma3-cortex:latest
                client.copy("ebdm/gemma3-enhanced:12b", "gemma3-cortex:latest")
                # Remove the original
                client.delete("ebdm/gemma3-enhanced:12b")
                logger.info("Enhanced Gemma3 model installed as gemma3-cortex:latest")
                return True
            except Exception as e:
                logger.warning(f"Failed to download enhanced Gemma3: {e}, falling back to gemma2:2b")
                model = "gemma2:2b"
        
        # Download the model
        try:
            client.pull(model)
            logger.info(f"Model {model} downloaded successfully")
            return True
        except Exception as e:
            logger.warning(f"Failed to download {model}: {e}, trying fallback gemma2:2b")
            try:
                client.pull("gemma2:2b")
                logger.info("Fallback model gemma2:2b downloaded")
                return True
            except Exception as fallback_error:
                logger.error(f"Failed to download fallback model: {fallback_error}")
                return False
                
    except Exception as e:
        logger.error(f"Error downloading Ollama model: {e}")
        return False

def create_env_file(hostname: str = "0.0.0.0", port: str = "8000"):
    """Create .env file with generated secret key."""
    env_path = Path(".env")
    
    if env_path.exists():
        logger.info(".env file already exists, skipping creation")
        return
    
    # Use STARLETTE_SECRET from environment if provided, otherwise generate one
    starlette_secret = os.getenv("STARLETTE_SECRET")
    if not starlette_secret:
        starlette_secret = str(uuid.uuid4())
        logger.info("Generated new STARLETTE_SECRET")
    else:
        logger.info("Using STARLETTE_SECRET from environment")
    
    env_content = f"""# Tatlock Environment Configuration
# Generated automatically during Docker initialization

# Server Configuration
HOSTNAME={hostname}
PORT={port}
ALLOWED_ORIGINS=http://{hostname}:{port}

# Security
STARLETTE_SECRET={starlette_secret}

# Debug Configuration
DEBUG_MODE=false
"""
    
    env_path.write_text(env_content)
    logger.info(f"Created .env file with hostname={hostname}, port={port}")

def initialize_databases():
    """Initialize system database if it doesn't exist."""
    from stem.installation.database_setup import create_system_db_tables
    
    db_path = Path("hippocampus/system.db")
    
    if db_path.exists():
        logger.info("system.db already exists, skipping initialization")
        return
    
    logger.info("Initializing system database...")
    
    # Ensure hippocampus directory exists
    Path("hippocampus").mkdir(exist_ok=True)
    
    create_system_db_tables(str(db_path))
    logger.info("System database initialized successfully")

def create_admin_user(username: str = "admin", password: str = "admin123", 
                     first_name: str = "Administrator", last_name: str = "User",
                     email: str = "admin@tatlock.local"):
    """Create default admin user if it doesn't exist."""
    from stem.security import security_manager
    import sqlite3
    
    db_path = Path("hippocampus/system.db")
    
    if not db_path.exists():
        logger.warning("System database not found, cannot create admin user")
        return False
    
    # Check if admin user already exists
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            logger.info(f"Admin user '{username}' already exists, skipping creation")
            conn.close()
            return True
        conn.close()
    except Exception as e:
        logger.warning(f"Error checking for existing admin user: {e}")
    
    # Create admin user
    try:
        logger.info(f"Creating admin user: {username}")
        result = security_manager.create_user(username, first_name, last_name, password, email)
        
        if result:
            security_manager.add_user_to_role(username, "user")
            security_manager.add_user_to_role(username, "admin")
            security_manager.add_user_to_group(username, "users")
            security_manager.add_user_to_group(username, "admins")
            logger.info(f"Admin user '{username}' created successfully")
            if password == "admin123":
                logger.warning("⚠️  Using default password 'admin123' - please change it after first login!")
            return True
        else:
            logger.error("Failed to create admin user")
            return False
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        return False

def migrate_env_to_settings(hostname: str = "0.0.0.0", port: str = "8000"):
    """Migrate .env settings to system_settings database."""
    from stem.installation.database_setup import migrate_env_to_settings
    
    db_path = Path("hippocampus/system.db")
    
    if not db_path.exists():
        logger.warning("System database not found, cannot migrate settings")
        return
    
    try:
        logger.info("Migrating .env settings to system_settings database...")
        migrate_env_to_settings(str(db_path), hostname, port)
        logger.info("Settings migration completed")
    except Exception as e:
        logger.warning(f"Error migrating settings: {e}")

def main():
    """Main initialization function."""
    logger.info("=" * 80)
    logger.info("Tatlock Docker Initialization")
    logger.info("=" * 80)
    
    # Get configuration from environment variables
    hostname = os.getenv("HOSTNAME", "0.0.0.0")
    port = os.getenv("PORT", "8000")
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    admin_first_name = os.getenv("ADMIN_FIRST_NAME", "Administrator")
    admin_last_name = os.getenv("ADMIN_LAST_NAME", "User")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@tatlock.local")
    skip_model_download = os.getenv("SKIP_MODEL_DOWNLOAD", "false").lower() == "true"
    
    # Ensure required directories exist
    logger.info("Creating required directories...")
    Path("hippocampus/longterm").mkdir(parents=True, exist_ok=True)
    Path("hippocampus/shortterm").mkdir(parents=True, exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    # Step 1: Hardware classification
    logger.info("\n[1/6] Classifying hardware and selecting model...")
    hw_config = classify_hardware()
    create_hardware_config(hw_config)
    
    # Step 2: Wait for Ollama and download model
    if not skip_model_download:
        logger.info("\n[2/6] Setting up Ollama model...")
        if wait_for_ollama(ollama_host):
            download_ollama_model(hw_config["recommended_model"], ollama_host)
        else:
            logger.warning("Ollama service not available, model download skipped")
    else:
        logger.info("\n[2/6] Skipping model download (SKIP_MODEL_DOWNLOAD=true)")
    
    # Step 3: Create .env file
    logger.info("\n[3/6] Creating environment configuration...")
    create_env_file(hostname, port)
    
    # Step 4: Initialize databases
    logger.info("\n[4/6] Initializing databases...")
    initialize_databases()
    
    # Step 5: Migrate settings
    logger.info("\n[5/6] Migrating settings to database...")
    migrate_env_to_settings(hostname, port)
    
    # Step 6: Create admin user
    logger.info("\n[6/6] Creating admin user...")
    create_admin_user(admin_username, admin_password, admin_first_name, admin_last_name, admin_email)
    
    logger.info("\n" + "=" * 80)
    logger.info("Docker initialization complete!")
    logger.info("=" * 80)
    logger.info(f"Tatlock will start on http://{hostname}:{port}")
    logger.info(f"Default admin credentials: {admin_username} / {admin_password}")
    if admin_password == "admin123":
        logger.warning("⚠️  Please change the default admin password after first login!")
    logger.info("=" * 80)

if __name__ == "__main__":
    main()

