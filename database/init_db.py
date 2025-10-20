"""Database initialization and migration utilities.

This module handles database initialization, table creation, and schema migrations.
It ensures proper setup of the database file in a cross-platform location and
provides utilities for schema version management.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.schema import MetaData

from database.models.base import BaseModel
from database.models.category import Category
from database.models.flash_card import FlashCard
from database.models.schedule import Schedule, ScheduledEvent
from database.models.settings import Settings

logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    """Get the database file path in user's app data directory.
    
    Returns:
        Path to the SQLite database file
    """
    # Use platform-specific app data location
    app_data = Path.home() / ".flash_cards_learning_app"
    app_data.mkdir(parents=True, exist_ok=True)
    return app_data / "flashcards.db"


def create_engine_with_config(db_path: Optional[Path] = None) -> Engine:
    """Create SQLAlchemy engine with proper configuration.
    
    Args:
        db_path: Optional custom database path. If None, uses default location.
        
    Returns:
        Configured SQLAlchemy Engine instance
    """
    if db_path is None:
        db_path = get_db_path()
        
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create engine with proper settings
    return create_engine(
        f"sqlite:///{db_path}",
        echo=False,  # Set to True for debugging
        pool_pre_ping=True,  # Verify connections before use
        connect_args={"check_same_thread": False},  # Allow multi-thread access
    )


def init_database(engine: Engine, drop_all: bool = False) -> None:
    """Initialize database schema.
    
    Args:
        engine: SQLAlchemy engine to use
        drop_all: If True, drops all tables before creating
        
    Raises:
        RuntimeError: If schema creation fails
    """
    try:
        if drop_all:
            logger.info("Dropping all tables...")
            BaseModel.metadata.drop_all(engine)
            
        logger.info("Creating database schema...")
        BaseModel.metadata.create_all(engine)
        
        # Verify all tables were created
        inspector = inspect(engine)
        expected_tables = {
            table.name 
            for table in BaseModel.metadata.sorted_tables
        }
        actual_tables = set(inspector.get_table_names())
        
        if not expected_tables.issubset(actual_tables):
            missing = expected_tables - actual_tables
            raise RuntimeError(f"Failed to create tables: {missing}")
            
        logger.info("Database schema created successfully")
        
    except Exception as e:
        logger.error("Failed to initialize database: %s", str(e))
        raise RuntimeError(f"Failed to initialize database: {str(e)}") from e


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a configured session factory.
    
    Args:
        engine: SQLAlchemy engine to use
        
    Returns:
        Session factory function
    """
    return sessionmaker(
        bind=engine,
        autoflush=False,  # Don't auto-flush for better control
        expire_on_commit=False,  # Keep objects usable after commit
    )


def get_schema_version(session: Session) -> str:
    """Get current database schema version.
    
    Args:
        session: SQLAlchemy session
        
    Returns:
        Current schema version string
    """
    version_setting = session.query(Settings).filter_by(
        setting_key="schema_version"
    ).first()
    
    return version_setting.setting_value["version"] if version_setting else "0.0.0"


def set_schema_version(session: Session, version: str) -> None:
    """Update database schema version.
    
    Args:
        session: SQLAlchemy session
        version: New version string
    """
    version_setting = session.query(Settings).filter_by(
        setting_key="schema_version"
    ).first()
    
    if version_setting:
        # Create new dict to ensure SQLAlchemy detects the change
        new_value = dict(version_setting.setting_value)
        new_value["version"] = version
        version_setting.setting_value = new_value
    else:
        version_setting = Settings(
            setting_key="schema_version",
            setting_value={"version": version},
        )
        session.add(version_setting)
    
    session.commit()
