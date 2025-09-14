import logging
import os

LOG_FILE = "logs/backend.log"
LOG_LEVEL = logging.INFO

def setup_logging():
    # Ensure logs directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # Create logger
    logger = logging.getLogger("backendbot")
    logger.setLevel(LOG_LEVEL)

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)

    # Create file handler and set level to debug
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(LOG_LEVEL)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add formatter to handlers
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add handlers to logger
    if not logger.handlers: # Avoid adding handlers multiple times
        logger.addHandler(ch)
        logger.addHandler(fh)
    
    return logger

# Initialize logger
logger = setup_logging()
