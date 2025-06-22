"""
config.py

Configuration and environment variable loading for Tatlock project.
Handles API keys, database paths, and LLM model configuration for
the conversational AI system with authentication and user management.
"""

import os
import logging
from dotenv import load_dotenv

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