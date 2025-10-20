"""Test fixtures and configuration."""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from core.serialization.base import BaseModel

@pytest.fixture(scope="session")
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture(scope="session")
def test_db_path(temp_dir):
    """Create a temporary database path."""
    return str(temp_dir / "test.db")

@pytest.fixture(scope="session")
def test_engine(test_db_path):
    """Create a test database engine."""
    engine = create_engine(f"sqlite:///{test_db_path}")
    BaseModel.metadata.create_all(engine)
    return engine

@pytest.fixture
def db_session(test_engine):
    """Create a new database session for a test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
