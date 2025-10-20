"""Test configuration module."""

from core.config import load_config

def test_load_config():
    """Test configuration loading."""
    config = load_config()
    
    assert isinstance(config, dict)
    assert 'APP_NAME' in config
    assert 'VERSION' in config
    assert 'DEBUG' in config
    assert isinstance(config['DEBUG'], bool)
    
    # Test paths
    assert 'DB_PATH' in config
    assert 'BACKUP_DIR' in config
    assert 'LOG_DIR' in config
    
    # Test backup settings
    assert 'MAX_BACKUP_DAYS' in config
    assert isinstance(config['MAX_BACKUP_DAYS'], int)
    assert 'AUTO_BACKUP' in config
    assert isinstance(config['AUTO_BACKUP'], bool)
