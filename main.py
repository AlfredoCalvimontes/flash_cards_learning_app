"""Main application entry point."""

import sys

from core import load_config, setup_logging, get_logger
from ui import get_app

def main():
    """Initialize and start the application."""
    # Load configuration
    config = load_config()
    
    # Setup logging
    setup_logging(config)
    logger = get_logger()
    
    logger.info("Starting Flash Cards Learning App")
    
    # Initialize application
    app = get_app()
    
    # TODO: Initialize main window
    logger.info("Application initialized")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
