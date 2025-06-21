"""
stem/textutils.py

String normalization and truncation helpers for Tatlock project.
"""

def normalize_text(text: str) -> str:
    """
    Normalize a string by stripping whitespace and converting to lowercase.
    Args:
        text (str): The input string.
    Returns:
        str: Normalized string, or empty string if input is not a string.
    """
    return text.strip().lower() if isinstance(text, str) else ""

def truncate_text(text: str, max_length: int = 200) -> str:
    """
    Truncate a string to a maximum length, appending '...' if truncated.
    Args:
        text (str): The input string.
        max_length (int): Maximum allowed length.
    Returns:
        str: Truncated string, or empty string if input is not a string.
    """
    if not isinstance(text, str):
        return ""
    return text if len(text) <= max_length else text[:max_length] + "..." 