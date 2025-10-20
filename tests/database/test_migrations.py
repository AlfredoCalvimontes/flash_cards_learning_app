"""Tests for database migration utilities."""

from unittest.mock import patch

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.init_db import create_engine_with_config, init_database, set_schema_version
from database.migrations import get_available_migrations, run_migration


def test_get_available_migrations():
    """Test migration path discovery."""
    migrations = get_available_migrations()
    assert isinstance(migrations, dict)


def test_run_migration_same_version(tmp_path):
    """Test migration when already at target version."""
    db_path = tmp_path / "test.db"
    engine = create_engine_with_config(db_path)
    init_database(engine)
    
    # Set initial version
    session = Session(engine)
    set_schema_version(session, "1.0.0")
    session.close()
    
    # Try migrating to same version
    assert run_migration(engine, "1.0.0") is True


def test_run_migration_missing_path(tmp_path):
    """Test error handling for missing migration path."""
    db_path = tmp_path / "test.db"
    engine = create_engine_with_config(db_path)
    init_database(engine)
    
    with pytest.raises(RuntimeError, match="No migration path from"):
        run_migration(engine, "2.0.0", current_version="1.0.0")


@patch("database.migrations.get_available_migrations")
def test_run_migration_success(mock_migrations, tmp_path):
    """Test successful migration execution."""
    db_path = tmp_path / "test.db"
    engine = create_engine_with_config(db_path)
    init_database(engine)
    
    # Mock migration path
    mock_migrations.return_value = {
        "1.0.0": {
            "2.0.0": "v2_0_0",
        }
    }
    
    # Set initial version
    session = Session(engine)
    set_schema_version(session, "1.0.0")
    session.close()
    
    # Create mock migration module
    with patch("builtins.__import__") as mock_import:
        class MockModule:
            @staticmethod
            def migrate(engine):
                """Mock migration."""
                pass
        
        mock_import.return_value = MockModule()
        # Configure the mock to only affect our specific import
        mock_import.side_effect = lambda name, *args, **kwargs: (
            MockModule() if name.startswith("database.migrations") else __import__(name, *args, **kwargs)
        )
        
        # Run migration
        assert run_migration(engine, "2.0.0") is True
        
        # Verify version was updated
        session = Session(engine)
        with session.begin():
            result = session.execute(
                text("SELECT setting_value FROM settings WHERE setting_key = 'schema_version'")
            ).scalar()
            assert result is not None
            assert isinstance(result, str)
            assert '"version": "2.0.0"' in result
        session.close()
