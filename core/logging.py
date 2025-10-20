"""Logging configuration and utilities.

This module provides centralized logging configuration and utilities for the entire application.
It ensures consistent logging format, levels, and handlers across all modules.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Global logger instance
_logger: Optional[logging.Logger] = None

def setup_logging(config: dict) -> None:
    """Initialize application-wide logging configuration.
    
    Args:
        config: Application configuration dictionary containing logging settings
    """
    global _logger
    
    log_dir = Path(config['LOG_DIR'])
    log_dir.mkdir(exist_ok=True)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Create and configure handlers
    file_handler = logging.FileHandler(log_dir / 'app.log')
    file_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config['LOG_LEVEL'])
    
    # Remove any existing handlers and add our configured ones
    root_logger.handlers.clear()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create our application logger
    _logger = logging.getLogger('flashcards')
    _logger.info('Logging system initialized')

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Optional name for the logger. If None, returns the main application logger.
             If provided, returns a child logger of the main application logger.
    
    Returns:
        logging.Logger: Configured logger instance
    
    Examples:
        >>> logger = get_logger()  # Get main application logger
        >>> logger = get_logger(__name__)  # Get module-specific logger
    """
    if _logger is None:
        raise RuntimeError("Logging system not initialized. Call setup_logging first.")
    
    if name is None:
        return _logger
    
    return logging.getLogger(f'flashcards.{name}')
