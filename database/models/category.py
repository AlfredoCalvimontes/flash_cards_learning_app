"""Category model and schema definition."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, List

from marshmallow import fields, validate
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.serialization.json import UUIDField, VersionedSchema
from database.models.base import BaseModel
from database.models.flash_card import FlashCard


class Category(BaseModel):
    """Category model for organizing flash cards."""

    __tablename__ = "categories"

    # Required fields with default=None for dataclass compatibility
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        init=True,
        default=None,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        init=True,
        default=None,
    )

    # Relationships (excluded from init)
    flash_cards: Mapped[List[FlashCard]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        init=False,
    )

    def __post_init__(self) -> None:
        """Validate required fields after initialization.
        
        Raises:
            ValueError: If any required field is None or invalid
        """
        if self.name is None:
            raise ValueError("name is required")
        if self.priority is None:
            raise ValueError("priority is required")
        if self.priority < 1:
            raise ValueError("priority must be greater than 0")

    def __str__(self) -> str:
        """Return string representation of the category.
        
        Returns:
            String in format: "Category: {name} (Priority: {priority})"
        """
        return f"Category: {self.name} (Priority: {self.priority})"
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current UTC time."""
        self.updated_at = datetime.now(timezone.utc)


class CategorySchema(VersionedSchema):
    """Schema for serializing/deserializing Category models."""

    class Meta:
        """Schema metadata."""
        model = Category
        load_instance = True
        include_relationships = True

    # Primary fields
    uuid = UUIDField(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "Name is required."},
    )
    priority = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        error_messages={
            "required": "Priority is required.",
            "invalid": "Priority must be a positive integer.",
        },
    )
    
    # Status fields
    active = fields.Boolean(load_default=True)
    deleted = fields.Boolean(load_default=False)

    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Relationships
    flash_cards = fields.List(
        fields.Nested("FlashCardSchema", exclude=("category",)),
        dump_only=True,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the schema with version information.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.__version__ = "1.0.0"  # Initial schema version
