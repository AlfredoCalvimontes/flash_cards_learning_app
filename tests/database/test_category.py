"""Unit tests for Category model and schema."""

import pytest
from datetime import datetime, timezone
from uuid import UUID

from database.models.category import Category
from database.models.schemas import CategorySchema
from marshmallow import ValidationError


def test_category_creation(db_session):
    """Test creating a new category with valid data."""
    category = Category(name="Test Category", priority=1)
    db_session.add(category)
    db_session.commit()

    assert isinstance(category.uuid, UUID)
    assert category.name == "Test Category"
    assert category.priority == 1
    assert category.active is True
    assert category.deleted is False
    assert isinstance(category.created_at, datetime)
    assert isinstance(category.updated_at, datetime)
    assert len(category.flash_cards) == 0


def test_category_required_fields():
    """Test that category creation fails without required fields."""
    with pytest.raises(ValueError, match="name is required"):
        Category(priority=1)
    
    with pytest.raises(ValueError, match="priority is required"):
        Category(name="Test")


def test_category_invalid_priority():
    """Test that category creation fails with invalid priority."""
    with pytest.raises(ValueError, match="priority must be greater than 0"):
        Category(name="Test", priority=0)


def test_category_unique_name(db_session):
    """Test that category names must be unique."""
    category1 = Category(name="Unique Name", priority=1)
    db_session.add(category1)
    db_session.commit()

    category2 = Category(name="Unique Name", priority=2)
    db_session.add(category2)
    
    with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
        db_session.commit()


def test_category_timestamp_update(db_session, sample_category):
    """Test that updated_at is modified when category is updated."""
    original_timestamp = sample_category.updated_at
    
    sample_category.name = "Updated Name"
    sample_category.update_timestamp()
    db_session.commit()
    
    assert sample_category.updated_at > original_timestamp


def test_category_string_representation(sample_category):
    """Test the string representation of a category."""
    expected = f"Category: {sample_category.name} (Priority: {sample_category.priority})"
    assert str(sample_category) == expected


class TestCategorySchema:
    """Test suite for CategorySchema."""

    def test_serialize_category(self, sample_category):
        """Test serializing a category to JSON."""
        schema = CategorySchema()
        result = schema.dump(sample_category)
        assert isinstance(result, dict)  # Type guard for static analysis

        # Test all serialized fields
        serialized_uuid = str(sample_category.uuid)
        assert isinstance(result.get("uuid"), str)
        assert result.get("uuid") == serialized_uuid
        assert result.get("name") == sample_category.name
        assert result.get("priority") == sample_category.priority
        assert result.get("active") is True
        assert result.get("deleted") is False
        assert "created_at" in result
        assert "updated_at" in result
        assert "schema_version" in result
        
        flash_cards = result.get("flash_cards")
        assert isinstance(flash_cards, list)

    def test_deserialize_valid_data(self, db_session):
        """Test deserializing valid JSON data to a category."""
        schema = CategorySchema()
        data = {
            "name": "New Category",
            "priority": 5,
        }
        schema._session = db_session  # Set session for context manager
        with schema.session_context():
            result = schema.load(data)

        assert isinstance(result, Category)
        assert result.name == "New Category"
        assert result.priority == 5

    def test_deserialize_invalid_data(self, db_session):
        """Test validation errors for invalid data."""
        schema = CategorySchema()
        schema._session = db_session  # Set session for context manager
        
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            with schema.session_context():
                schema.load({})
        assert "name" in exc_info.value.messages
        assert "priority" in exc_info.value.messages

        # Test invalid priority
        with pytest.raises(ValidationError) as exc_info:
            with schema.session_context():
                schema.load({"name": "Test", "priority": 0})
        assert "priority" in exc_info.value.messages

        # Test invalid name length
        with pytest.raises(ValidationError) as exc_info:
            with schema.session_context():
                schema.load({"name": "", "priority": 1})
        assert "name" in exc_info.value.messages

    def test_schema_version_handling(self, db_session):
        """Test schema version handling in serialization."""
        schema = CategorySchema()
        category = Category(name="Test", priority=1)
        
        result = schema.dump(category)
        assert isinstance(result, dict)  # Type guard for static analysis
        assert result.get("schema_version") == schema.__version__

        # Test incompatible version
        schema._session = db_session  # Set session for context manager
        with pytest.raises(ValidationError) as exc_info:
            with schema.session_context():
                schema.load({
                    "schema_version": "999.0.0", 
                    "name": "Test", 
                    "priority": 1
                })
        assert "Data schema version 999.0.0 is newer than supported 1.0.0" in str(exc_info.value)
