import logging

logger = logging.getLogger(__name__)

def log_action(action, message):
    logger.info(f"{action}: {message}")

def log_info(message):
    logger.info(f"INFO: {message}")

def log_error(message):
    logger.error(f"ERROR: {message}")

def log_warning(message):
    logger.warning(f"WARNING: {message}")

def log_debug(message):
    logger.debug(f"DEBUG: {message}")
