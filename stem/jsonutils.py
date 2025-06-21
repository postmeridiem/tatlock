"""
stem/jsonutils.py

JSON serialization and deserialization helpers for Tatlock project.
"""

import json

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
        print(f"Error serializing to JSON: {e}")
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
        print(f"Error deserializing from JSON: {e}")
        return None 