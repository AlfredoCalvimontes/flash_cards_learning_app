"""Base model definitions."""

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import UUID, uuid4

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

# Define naming convention for constraints
NAMING_CONVENTION: Dict[str, Any] = {
    "ix": "ix_%(column_0_label)s",  # Index
    "uq": "uq_%(table_name)s_%(column_0_name)s",  # Unique constraint
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # Check constraint
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # Foreign key
    "pk": "pk_%(table_name)s",  # Primary key
}

# Create metadata with naming convention
metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(MappedAsDataclass, DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    metadata = metadata
    type_annotation_map = {
        datetime: DateTime(timezone=True),
    }

    @classmethod
    def create_tables(cls, engine: Any) -> None:
        """Create all database tables.
        
        Args:
            engine: SQLAlchemy engine instance
        """
        cls.metadata.create_all(engine)


class BaseModel(Base):
    """Base model with common fields for all models."""

    __abstract__ = True

    uuid: Mapped[UUID] = mapped_column(
        primary_key=True,
        default_factory=uuid4,
        init=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        init=False,
    )
    active: Mapped[bool] = mapped_column(default=True)
    deleted: Mapped[bool] = mapped_column(default=False)
