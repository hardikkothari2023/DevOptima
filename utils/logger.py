"""
Centralized logging configuration for DevOptima.
Ensures consistent formatting and levels across all modules.
"""

import logging
import sys

def setup_logger(name: str = "devoptima") -> logging.Logger:
    """
    Configures and returns a logger instance.
    Logs are sent to stdout for compatibility with Streamlit Cloud.
    """
    logger = logging.getLogger(name)
    
    # Only configure if the logger doesn't have handlers already
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Create formatter
        # Format: [Timestamp] [Level] [Module]: Message
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create console handler (stdout)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        
        # Prevent propagation to the root logger to avoid double logs in Streamlit
        logger.propagate = False
        
    return logger

# Create a default logger instance for general use
logger = setup_logger()
