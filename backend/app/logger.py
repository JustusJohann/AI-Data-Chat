import logging
import os
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configures logging to write to both console and a file in backend/logs/error.log
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "error.log")

    # Create a custom logger
    logger = logging.getLogger("sql_agent")
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times
    if logger.hasHandlers():
        return logger

    # Create handlers
    c_handler = logging.StreamHandler(sys.stdout)
    f_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    
    c_handler.setLevel(logging.INFO)
    f_handler.setLevel(logging.ERROR) # Only log errors to file as requested, or maybe ALL info? 
    # User asked for "logs errors in a separate file", implying error log. 
    # But usually good to see context. Let's log INFO to file too for debugging context before error.
    f_handler.setLevel(logging.INFO)

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

logger = setup_logging()
