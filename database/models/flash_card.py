"""FlashCard model and schema definition."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from marshmallow import fields, validate
from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.serialization.json import UUIDField, VersionedSchema
from database.models.base import BaseModel
from database.models.category import Category


class FlashCard(BaseModel):
    """FlashCard model representing a single flash card in the system."""

    __tablename__ = "flash_cards"

    # Required fields with default_factory to maintain dataclass compatibility
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        init=True,  # Include in __init__
        default=None,  # Required for dataclass ordering
    )
    question: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        init=True,  # Include in __init__
        default=None,  # Required for dataclass ordering
    )
    answer: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
        init=True,  # Include in __init__
        default=None,  # Required for dataclass ordering
    )
    category_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("categories.uuid", ondelete="CASCADE"),
        nullable=False,
        init=True,  # Include in __init__
        default=None,  # Required for dataclass ordering
    )
    
    # Optional fields with real defaults
    difficulty: Mapped[int] = mapped_column(
        default=5,
        nullable=False,
        info={"validate": validate.Range(min=1, max=10)},
        init=False,  # Exclude from __init__
    )
    
    # Relationship reference (excluded from init)
    category: Mapped[Category] = relationship(
        back_populates="flash_cards",
        init=False,  # Exclude from __init__
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "difficulty >= 1 AND difficulty <= 10",
            name="ck_flash_cards_difficulty_range",
        ),
    )
    
    def __post_init__(self) -> None:
        """Validate required fields after initialization.
        
        Raises:
            ValueError: If any required field is None
        """
        if self.name is None:
            raise ValueError("name is required")
        if self.question is None:
            raise ValueError("question is required")
        if self.answer is None:
            raise ValueError("answer is required")
        if self.category_uuid is None:
            raise ValueError("category_uuid is required")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "difficulty >= 1 AND difficulty <= 10",
            name="ck_flash_cards_difficulty_range",
        ),
    )

    def __str__(self) -> str:
        """Return string representation of the flash card.
        
        Returns:
            String in format: "FlashCard: {name} (Difficulty: {difficulty})"
        """
        return f"FlashCard: {self.name} (Difficulty: {self.difficulty})"
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current UTC time."""
        self.updated_at = datetime.now(timezone.utc)


class FlashCardSchema(VersionedSchema):
    """Schema for serializing/deserializing FlashCard models."""

    class Meta:
        """Schema metadata."""
        model = FlashCard
        load_instance = True
        include_relationships = True

    # Primary fields
    uuid = UUIDField(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "Name is required."},
    )
    question = fields.String(
        required=True,
        validate=validate.Length(min=1, max=1000),
        error_messages={"required": "Question is required."},
    )
    answer = fields.String(
        required=True,
        validate=validate.Length(min=1, max=2000),
        error_messages={"required": "Answer is required."},
    )
    
    # Secondary fields
    difficulty = fields.Integer(
        required=True,
        validate=validate.Range(min=1, max=10),
        load_default=5,
    )
    active = fields.Boolean(load_default=True)
    deleted = fields.Boolean(load_default=False)

    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Relationships
    category_uuid = UUIDField(required=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the schema with version information.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.__version__ = "1.0.0"  # Initial schema version
