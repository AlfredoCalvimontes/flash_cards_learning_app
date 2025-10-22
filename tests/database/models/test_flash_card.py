"""Tests for FlashCard model."""

import pytest

from database.models.category import Category
from database.models.flash_card import FlashCard


def test_calculate_weight_with_default_params(session):
    """Test weight calculation with default parameters."""
    # Create a category with priority 2
    category = Category(
        name="Test Category",
        priority=2
    )
    session.add(category)
    session.flush()  # To get the UUID
    
    # Create a card with difficulty 5 (default)
    card = FlashCard(
        name="Test Card",
        question="Test Question",
        answer="Test Answer",
        category_uuid=category.uuid,
    )
    card.category = category  # Set relationship
    
    # Calculate weight with default params (alpha=0.7, beta=0.4)
    weight = card.calculate_weight()
    
    # Expected: (2^0.7) * (5^0.4) ≈ 3.0839
    expected = (2 ** 0.7) * (5 ** 0.4)
    assert abs(weight - expected) < 0.0001


def test_calculate_weight_without_category(session):
    """Test weight calculation fails without category."""
    card = FlashCard(
        name="Test Card",
        question="Test Question",
        answer="Test Answer",
        # We don't set category_uuid to create an invalid state
    )
    
    with pytest.raises(ValueError, match="Card must have an associated category"):
        card.calculate_weight()


def test_weight_increases_with_priority(session):
    """Test that higher category priority increases weight."""
    # Create two categories with different priorities
    cat1 = Category(name="Low Priority", priority=1)
    cat2 = Category(name="High Priority", priority=3)
    session.add_all([cat1, cat2])
    session.flush()
    
    # Create identical cards in different categories
    card1 = FlashCard(
        name="Card 1",
        question="Q",
        answer="A",
        category_uuid=cat1.uuid,
    )
    card2 = FlashCard(
        name="Card 2",
        question="Q",
        answer="A",
        category_uuid=cat2.uuid,
    )
    card1.category = cat1
    card2.category = cat2
    
    # Higher priority category should result in higher weight
    assert card1.calculate_weight() < card2.calculate_weight()


def test_weight_increases_with_difficulty(session):
    """Test that higher difficulty increases weight."""
    category = Category(name="Test", priority=1)
    session.add(category)
    session.flush()
    
    # Create two cards with different difficulties
    card1 = FlashCard(
        name="Easy Card",
        question="Q",
        answer="A",
        category_uuid=category.uuid,
    )
    card2 = FlashCard(
        name="Hard Card",
        question="Q",
        answer="A",
        category_uuid=category.uuid,
    )
    card1.category = category
    card2.category = category
    
    card1.difficulty = 3
    card2.difficulty = 7
    
    # Higher difficulty should result in higher weight
    assert card1.calculate_weight() < card2.calculate_weight()
