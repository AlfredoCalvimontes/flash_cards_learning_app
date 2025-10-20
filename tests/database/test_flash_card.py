"""Unit tests for FlashCard model and schema."""

import pytest
from datetime import datetime
from uuid import UUID

from database.models.flash_card import FlashCard
from database.models.schemas import FlashCardSchema
from marshmallow import ValidationError


def test_flash_card_creation(db_session, sample_category):
    """Test creating a new flash card with valid data."""
    card = FlashCard(
        name="Test Card",
        question="What is the test?",
        answer="This is a test",
        category_uuid=sample_category.uuid,
    )
    db_session.add(card)
    db_session.commit()

    assert isinstance(card.uuid, UUID)
    assert card.name == "Test Card"
    assert card.question == "What is the test?"
    assert card.answer == "This is a test"
    assert card.difficulty == 5  # Default value
    assert card.active is True
    assert card.deleted is False
    assert isinstance(card.created_at, datetime)
    assert isinstance(card.updated_at, datetime)
    assert card.category_uuid == sample_category.uuid
    assert card.category.name == sample_category.name


def test_flash_card_required_fields(sample_category):
    """Test that flash card creation fails without required fields."""
    with pytest.raises(ValueError, match="name is required"):
        FlashCard(
            question="Test",
            answer="Test",
            category_uuid=sample_category.uuid,
        )
    
    with pytest.raises(ValueError, match="question is required"):
        FlashCard(
            name="Test",
            answer="Test",
            category_uuid=sample_category.uuid,
        )
    
    with pytest.raises(ValueError, match="answer is required"):
        FlashCard(
            name="Test",
            question="Test",
            category_uuid=sample_category.uuid,
        )
    
    with pytest.raises(ValueError, match="category_uuid is required"):
        FlashCard(
            name="Test",
            question="Test",
            answer="Test",
        )


def test_flash_card_difficulty_constraint(db_session, sample_category):
    """Test that difficulty must be between 1 and 10."""
    card = FlashCard(
        name="Test Card",
        question="Test",
        answer="Test",
        category_uuid=sample_category.uuid,
    )
    card.difficulty = 11  # Invalid value
    db_session.add(card)
    
    with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
        db_session.commit()


def test_flash_card_category_relationship(db_session, sample_category):
    """Test the relationship between flash cards and categories."""
    card = FlashCard(
        name="Test Card",
        question="Test",
        answer="Test",
        category_uuid=sample_category.uuid,
    )
    db_session.add(card)
    db_session.commit()
    
    # Test relationship from card to category
    assert card.category == sample_category
    
    # Test relationship from category to card
    assert card in sample_category.flash_cards


def test_flash_card_timestamp_update(db_session, sample_flash_card):
    """Test that updated_at is modified when flash card is updated."""
    original_timestamp = sample_flash_card.updated_at
    
    sample_flash_card.name = "Updated Name"
    sample_flash_card.update_timestamp()
    db_session.commit()
    
    assert sample_flash_card.updated_at > original_timestamp


def test_flash_card_string_representation(sample_flash_card):
    """Test the string representation of a flash card."""
    expected = f"FlashCard: {sample_flash_card.name} (Difficulty: {sample_flash_card.difficulty})"
    assert str(sample_flash_card) == expected


class TestFlashCardSchema:
    """Test suite for FlashCardSchema."""

    def test_serialize_flash_card(self, sample_flash_card):
        """Test serializing a flash card to JSON."""
        schema = FlashCardSchema()
        result = schema.dump(sample_flash_card)
        assert isinstance(result, dict)  # Type guard for static analysis
        
        # Test all serialized fields
        serialized_uuid = str(sample_flash_card.uuid)
        serialized_category_uuid = str(sample_flash_card.category_uuid)
        
        assert isinstance(result.get("uuid"), str)
        assert result.get("uuid") == serialized_uuid
        assert result.get("name") == sample_flash_card.name
        assert result.get("question") == sample_flash_card.question
        assert result.get("answer") == sample_flash_card.answer
        assert result.get("difficulty") == sample_flash_card.difficulty
        assert result.get("category_uuid") == serialized_category_uuid
        assert result.get("active") is True
        assert result["deleted"] is False
        assert "created_at" in result
        assert "updated_at" in result
        assert "schema_version" in result

    def test_deserialize_valid_data(self, sample_category, db_session):
        """Test deserializing valid JSON data to a flash card."""
        schema = FlashCardSchema()
        data = {
            "name": "New Card",
            "question": "What is new?",
            "answer": "This is new",
            "category_uuid": str(sample_category.uuid),
            "difficulty": 7,
        }
        result = schema.load(data, session=db_session)

        assert isinstance(result, FlashCard)
        assert result.name == "New Card"
        assert result.question == "What is new?"
        assert result.answer == "This is new"
        assert result.category_uuid == sample_category.uuid
        assert result.difficulty == 7

    def test_deserialize_invalid_data(self, sample_category, db_session):
        """Test validation errors for invalid data."""
        schema = FlashCardSchema()
        
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, session=db_session)
        assert "name" in exc_info.value.messages
        assert "question" in exc_info.value.messages
        assert "answer" in exc_info.value.messages
        assert "category_uuid" in exc_info.value.messages

        # Test invalid difficulty
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "name": "Test",
                "question": "Test",
                "answer": "Test",
                "category_uuid": str(sample_category.uuid),
                "difficulty": 11,
            }, session=db_session)
        assert "difficulty" in exc_info.value.messages

        # Test invalid UUID format
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "name": "Test",
                "question": "Test",
                "answer": "Test",
                "category_uuid": "not-a-uuid",
            }, session=db_session)
        assert "category_uuid" in exc_info.value.messages

    def test_schema_version_handling(self, sample_category, db_session):
        """Test schema version handling in serialization."""
        schema = FlashCardSchema()
        card = FlashCard(
            name="Test",
            question="Test",
            answer="Test",
            category_uuid=sample_category.uuid,
        )

        result = schema.dump(card)
        assert isinstance(result, dict)  # Type guard for static analysis
        assert result.get("schema_version") == schema.__version__

        # Test incompatible version
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "schema_version": "999.0.0",
                "name": "Test",
                "question": "Test",
                "answer": "Test",
                "category_uuid": str(sample_category.uuid),
            }, session=db_session)
