"""
stem/logging.py

Logging utilities for Tatlock.
Provides centralized logging configuration and utility functions.
"""

import logging
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tatlock.log')
    ]
)

def log_error(msg: str, logger_name: Optional[str] = None) -> None:
    """Log an error message."""
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger(__name__)
    logger.error(msg)

def log_info(msg: str, logger_name: Optional[str] = None) -> None:
    """Log an info message."""
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger(__name__)
    logger.info(msg) 