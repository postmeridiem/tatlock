"""
config.py

Configuration and environment variable loading for Tatlock project.
Handles API keys, database paths, and LLM model configuration for
the conversational AI system with authentication and user management.
"""

import os
from dotenv import load_dotenv

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
PORT = int(os.getenv("PORT", "8000"))

# --- Error Checking ---
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY environment variable not set.")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")
if not GOOGLE_CSE_ID:
    raise ValueError("GOOGLE_CSE_ID environment variable not set.")