"""Configuration management module."""

import os
from pathlib import Path
from typing import Dict, Any

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent

def load_config() -> Dict[str, Any]:
    """Load application configuration."""
    config = {
        'APP_NAME': 'Flash Cards Learning App',
        'VERSION': '0.1.0',
        'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
        'DB_PATH': os.getenv('DB_PATH', str(get_project_root() / 'database' / 'flashcards.db')),
        'BACKUP_DIR': os.getenv('BACKUP_DIR', str(get_project_root() / 'backup')),
        'LOG_DIR': os.getenv('LOG_DIR', str(get_project_root() / 'logs')),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
        'MAX_BACKUP_DAYS': int(os.getenv('MAX_BACKUP_DAYS', '7')),
        'AUTO_BACKUP': os.getenv('AUTO_BACKUP', 'True').lower() == 'true',
    }
    return config
