"""Category model definition."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import BaseModel

if TYPE_CHECKING:
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
