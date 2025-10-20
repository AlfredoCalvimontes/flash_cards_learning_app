"""Settings model definition."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import BaseModel


class Settings(BaseModel):
    """Settings model for application configuration storage."""

    __tablename__ = "settings"

    # Override UUID primary key with string key
    setting_key: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        unique=True,
        init=True,
        default=None,
    )
    # Store any JSON-serializable value
    setting_value: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        init=True,
        default=None,
    )

    def __post_init__(self) -> None:
        """Validate required fields after initialization.
        
        Raises:
            ValueError: If any required field is None
        """
        if self.setting_key is None:
            raise ValueError("setting_key is required")
        if self.setting_value is None:
            raise ValueError("setting_value is required")

    def __str__(self) -> str:
        """Return string representation of the setting.
        
        Returns:
            String with key and type of value
        """
        return f"Setting: {self.setting_key} (Type: {type(self.setting_value).__name__})"

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current UTC time."""
        self.updated_at = datetime.now(timezone.utc)
