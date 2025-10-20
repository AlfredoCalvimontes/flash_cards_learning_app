"""Test fixtures and configuration for database tests."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from typing import Generator

from database.models.base import Base
from database.models.category import Category
from database.models.flash_card import FlashCard


@pytest.fixture(scope="session")
def engine():
    """Create a SQLite in-memory engine for testing.
    
    Returns:
        SQLAlchemy engine instance
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
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
def sample_category(db_session: Session, request: pytest.FixtureRequest) -> Category:
    """Create a sample category for testing.
    
    Args:
        db_session: SQLAlchemy session fixture
        request: Pytest fixture request object for test context
        
    Returns:
        Category instance
    """
    # Create a unique name using the test name
    unique_name = f"Test Category - {request.node.name}"
    
    category = Category(
        name=unique_name,
        priority=1,
    )
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def sample_flash_card(db_session: Session, sample_category: Category, request: pytest.FixtureRequest) -> FlashCard:
    """Create a sample flash card for testing.
    
    Args:
        db_session: SQLAlchemy session fixture
        sample_category: Category fixture
        request: Pytest fixture request object for test context
        
    Returns:
        FlashCard instance
    """
    # Create a unique name using the test name
    unique_name = f"Test Card - {request.node.name}"
    
    card = FlashCard(
        name=unique_name,
        question=f"What is the test question for {request.node.name}?",
        answer=f"This is the test answer for {request.node.name}",
        category_uuid=sample_category.uuid,
    )
    db_session.add(card)
    db_session.commit()
    return card
