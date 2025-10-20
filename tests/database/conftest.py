"""Test fixtures and configuration for database tests."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from typing import Generator

from core.serialization.base import BaseModel
from database.models.category import Category
from database.models.flash_card import FlashCard


@pytest.fixture(scope="session")
def engine():
    """Create a SQLite in-memory engine for testing.
    
    Returns:
        SQLAlchemy engine instance
    """
    engine = create_engine("sqlite:///:memory:")
    BaseModel.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Create a new database session for a test.
    
    Args:
        engine: SQLAlchemy engine fixture
        
    Yields:
        SQLAlchemy session
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_category(db_session: Session) -> Category:
    """Create a sample category for testing.
    
    Args:
        db_session: SQLAlchemy session fixture
        
    Returns:
        Category instance
    """
    category = Category(
        name="Test Category",
        priority=1,
    )
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def sample_flash_card(db_session: Session, sample_category: Category) -> FlashCard:
    """Create a sample flash card for testing.
    
    Args:
        db_session: SQLAlchemy session fixture
        sample_category: Category fixture
        
    Returns:
        FlashCard instance
    """
    card = FlashCard(
        name="Test Card",
        question="What is the test question?",
        answer="This is the test answer",
        category_uuid=sample_category.uuid,
    )
    db_session.add(card)
    db_session.commit()
    return card
