import logging
import os
import sys

# Store handlers to update them later
_log_handlers = []

def setup_logger(name: str):
    """
    Sets up a logger with the specified name.
    Log level is initially determined by LOG_LEVEL env var or defaults to INFO.
    """
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger

    # Initial setup (Env var precedence)
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False
    
    _log_handlers.append((logger, handler))

    return logger

def update_log_levels(level_name: str):
    """
    Updates the log level for all configured loggers.
    """
    level = getattr(logging, level_name.upper(), logging.INFO)
    for logger, handler in _log_handlers:
        logger.setLevel(level)
        handler.setLevel(level)

def setup_raw_logger(name: str):
    """
    Sets up a logger that outputs ONLY the message (no timestamp/level).
    Used for printing tables/clean output while using the logging system.
    """
    logger = logging.getLogger(name)
    
    if logger.hasHandlers():
        return logger

    # Initial setup
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # Message only formatter
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False
    
    _log_handlers.append((logger, handler))

    return logger
