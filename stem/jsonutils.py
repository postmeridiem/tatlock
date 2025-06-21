"""
stem/jsonutils.py

JSON utility functions for Tatlock.
Provides safe JSON serialization and deserialization with error handling.
"""

import json
import logging
from typing import Any, Dict, List, Optional

# Set up logging for this module
logger = logging.getLogger(__name__)

def to_json(obj) -> str:
    """
    Serialize an object to a JSON string.
    Args:
        obj: The object to serialize.
    Returns:
        str: JSON string, or empty string on error.
    """
    try:
        return json.dumps(obj)
    except Exception as e:
        logger.error(f"Error serializing to JSON: {e}")
        return ""

def from_json(json_str: str):
    """
    Deserialize a JSON string to a Python object.
    Args:
        json_str (str): The JSON string to deserialize.
    Returns:
        object: The deserialized object, or None on error.
    """
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Error deserializing from JSON: {e}")
        return None 