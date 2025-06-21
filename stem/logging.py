"""
stem/logging.py

Simple logging helpers for Tatlock project.
"""

from datetime import datetime

def log_error(msg: str):
    """
    Log an error message with a timestamp.
    Args:
        msg (str): The error message to log.
    """
    print(f"[ERROR] {datetime.now().isoformat()} - {msg}")

def log_info(msg: str):
    """
    Log an info message with a timestamp.
    Args:
        msg (str): The info message to log.
    """
    print(f"[INFO] {datetime.now().isoformat()} - {msg}") 