"""
Logging Configuration Module

Provides centralized logging configuration for the ML Pipeline.
"""

import logging
import os

_DEFAULT_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')


def setup_logger(name='ml_pipeline', log_dir=None):
    """
    Set up and configure logger with file and console handlers.

    Args:
        name (str): Logger name
        log_dir (str): Directory for log files

    Returns:
        logging.Logger: Configured logger instance
    """
    if log_dir is None:
        log_dir = _DEFAULT_LOG_DIR
    # Create log directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler (append mode, utf-8 encoding)
    log_file = os.path.join(log_dir, 'training.log')
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_section_header(logger, title):
    """
    Log a section header for better log readability.
    
    Args:
        logger: Logger instance
        title (str): Section title
    """
    separator = "=" * 60
    logger.info(separator)
    logger.info(f"  {title}")
    logger.info(separator)
