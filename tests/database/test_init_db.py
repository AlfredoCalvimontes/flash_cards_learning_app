"""Tests for database initialization and migration utilities."""

import os
from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session as SQLAlchemySession

from database.init_db import (
    create_engine_with_config,
    create_session_factory,
    get_db_path,
    get_schema_version,
    init_database,
    set_schema_version,
)
from database.models.base import BaseModel


def test_get_db_path():
    """Test database path generation."""
    db_path = get_db_path()
    assert isinstance(db_path, Path)
    assert db_path.name == "flashcards.db"
    assert ".flash_cards_learning_app" in str(db_path)


def test_create_engine_with_config(tmp_path):
    """Test engine creation with custom path."""
    db_path = tmp_path / "test.db"
    engine = create_engine_with_config(db_path)
    
    # Test basic engine configuration
    assert engine is not None
    assert isinstance(engine, Engine)
    
    # Test SQLite-specific settings
    assert engine.dialect.name == "sqlite"
    
    # Test that engine was created with our path
    assert str(db_path) in str(engine.url)
    
    # Verify engine options through raw connection
    with engine.connect() as conn:
        # Begin a transaction to ensure the connection is ready
        with conn.begin():
            # Execute pragmas in a way that ensures we get results
            result = conn.execute(text("SELECT name, file FROM pragma_database_list WHERE name = 'main'")).first()
            assert result is not None
            
            # Check SQLite is using the correct database file
            db_name = result[1]  # The file path is in the second column
            assert str(db_path) in db_name


def test_init_database(tmp_path):
    """Test database initialization."""
    db_path = tmp_path / "test.db"
    engine = create_engine_with_config(db_path)
    
    # Test initial creation
    init_database(engine)
    inspector = inspect(engine)
    for table in BaseModel.metadata.sorted_tables:
        assert table.name in inspector.get_table_names()
        
    # Test recreation with drop
    init_database(engine, drop_all=True)
    inspector = inspect(engine)
    for table in BaseModel.metadata.sorted_tables:
        assert table.name in inspector.get_table_names()


def test_create_session_factory(tmp_path):
    """Test session factory creation and configuration."""
    db_path = tmp_path / "test.db"
    engine = create_engine_with_config(db_path)
    init_database(engine)
    
    SessionFactory = create_session_factory(engine)
    session = SessionFactory()
    
    # Check if session is a SQLAlchemy Session instance
    from sqlalchemy.orm.session import Session as SQLAlchemySession
    assert isinstance(session, SQLAlchemySession)
    assert session.bind == engine
    assert not session.autoflush
    assert not session.expire_on_commit
    
    session.close()


def test_schema_version_management(tmp_path):
    """Test schema version getter and setter."""
    db_path = tmp_path / "test.db"
    engine = create_engine_with_config(db_path)
    init_database(engine)
    
    Session = create_session_factory(engine)
    
    with Session() as session:
        # Test initial version
        version = get_schema_version(session)
        assert version == "0.0.0"
        
        # Test version update
        set_schema_version(session, "1.0.0")
        version = get_schema_version(session)
        assert version == "1.0.0"
        
        # Test version update with existing setting
        set_schema_version(session, "1.1.0")
        version = get_schema_version(session)
        assert version == "1.1.0"


def test_database_directory_creation(tmp_path):
    """Test database directory is created if it doesn't exist."""
    nested_path = tmp_path / "deep" / "nested" / "path" / "test.db"
    engine = create_engine_with_config(nested_path)
    
    assert nested_path.parent.exists()
    init_database(engine)
    assert nested_path.exists()


def test_init_database_handles_errors(tmp_path, monkeypatch):
    """Test error handling during database initialization."""
    db_path = tmp_path / "test.db"
    engine = create_engine_with_config(db_path)
    
    def mock_create_all(*args, **kwargs):
        raise PermissionError("Access denied")
    
    # Patch SQLAlchemy's create_all to simulate a database error
    monkeypatch.setattr(BaseModel.metadata, "create_all", mock_create_all)
    
    with pytest.raises(RuntimeError, match="Failed to initialize database"):
        init_database(engine)
