"""Schedule model definitions."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum, unique
from typing import TYPE_CHECKING, Optional, List
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum as SQLEnum, ForeignKey, Integer, String, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import BaseModel

if TYPE_CHECKING:
    from database.models.category import Category
    from database.models.flash_card import FlashCard


@unique
class Scope(str, Enum):
    """Valid scope values for schedules."""
    
    GLOBAL = "global"
    CATEGORY = "category"
    CARD = "card"


@unique
class FrequencyMode(str, Enum):
    """Valid frequency modes for schedules."""
    
    TIMES_PER_WEEK = "times_per_week"
    TIMES_PER_DAY = "times_per_day"
    FIXED_INTERVAL = "fixed_interval"


class Schedule(BaseModel):
    """Schedule model for defining when flash cards should be shown."""

    __tablename__ = "schedules"

    # Scope and relationships
    scope: Mapped[Scope] = mapped_column(
        SQLEnum(Scope),
        nullable=False,
        init=True,
        default=None,
    )
    category_uuid: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("categories.uuid", ondelete="CASCADE"),
        nullable=True,
        init=True,
        default=None,
    )
    flash_card_uuid: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("flash_cards.uuid", ondelete="CASCADE"),
        nullable=True,
        init=True,
        default=None,
    )

    # Relationship references (not in init)
    category: Mapped[Optional[Category]] = relationship(
        init=False,
        lazy="selectin",
    )
    flash_card: Mapped[Optional[FlashCard]] = relationship(
        init=False,
        lazy="selectin",
    )
    events: Mapped[List[ScheduledEvent]] = relationship(
        back_populates="schedule",
        cascade="all, delete-orphan",
        init=False,
    )

    # Time constraints
    allowed_days: Mapped[str] = mapped_column(
        String(21),  # Mon,Tue,Wed,Thu,Fri,Sat,Sun
        nullable=False,
        init=True,
        default=None,
    )
    start_hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        init=True,
        default=None,
    )
    end_hour: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        init=True,
        default=None,
    )

    # Frequency settings
    frequency_mode: Mapped[FrequencyMode] = mapped_column(
        SQLEnum(FrequencyMode),
        nullable=False,
        init=True,
        default=None,
    )
    times_per_week: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint("times_per_week BETWEEN 1 AND 7", name="valid_times_per_week"),
        nullable=True,
        init=True,
        default=None,
    )
    min_times_per_day: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        init=True,
        default=None,
    )
    max_times_per_day: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        init=True,
        default=None,
    )
    interval_minutes: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        init=True,
        default=None,
    )

    __table_args__ = (
        # Hours must be valid 24-hour values
        CheckConstraint(
            "start_hour >= 0 AND start_hour <= 23",
            name="ck_schedules_start_hour_range",
        ),
        CheckConstraint(
            "end_hour >= 0 AND end_hour <= 23",
            name="ck_schedules_end_hour_range",
        ),
        # End hour must be after start hour
        CheckConstraint(
            "end_hour > start_hour",
            name="ck_schedules_hour_order",
        ),
        # Times per week must be 1-7
        CheckConstraint(
            "(frequency_mode != 'times_per_week' OR "
            "(times_per_week >= 1 AND times_per_week <= 7))",
            name="ck_schedules_times_per_week_range",
        ),
        # Times per day must be valid and min <= max
        CheckConstraint(
            "(frequency_mode != 'times_per_day' OR "
            "(min_times_per_day >= 1 AND max_times_per_day >= min_times_per_day))",
            name="ck_schedules_times_per_day_range",
        ),
        # Interval must be positive minutes
        CheckConstraint(
            "(frequency_mode != 'fixed_interval' OR interval_minutes > 0)",
            name="ck_schedules_interval_minutes_range",
        ),
    )

    def __post_init__(self) -> None:
        """Validate required fields and relationships after initialization.
        
        Raises:
            ValueError: If required fields are missing or invalid
        """
        if self.scope is None:
            raise ValueError("scope is required")
        if self.scope == Scope.CATEGORY and not self.category_uuid:
            raise ValueError("category_uuid is required for category scope")
        if self.scope == Scope.CARD and not self.flash_card_uuid:
            raise ValueError("flash_card_uuid is required for card scope")
        if self.allowed_days is None:
            raise ValueError("allowed_days is required")
        if self.start_hour is None:
            raise ValueError("start_hour is required")
        if self.end_hour is None:
            raise ValueError("end_hour is required")
        if self.frequency_mode is None:
            raise ValueError("frequency_mode is required")

        # Validate frequency mode specific fields
        if self.frequency_mode == FrequencyMode.TIMES_PER_WEEK:
            if self.times_per_week is None:
                raise ValueError("times_per_week is required for times_per_week mode")

        if self.frequency_mode == FrequencyMode.TIMES_PER_DAY:
            if self.min_times_per_day is None:
                raise ValueError("min_times_per_day is required for times_per_day mode")
            if self.max_times_per_day is None:
                raise ValueError("max_times_per_day is required for times_per_day mode")

        if self.frequency_mode == FrequencyMode.FIXED_INTERVAL:
            if self.interval_minutes is None:
                raise ValueError("interval_minutes is required for fixed_interval mode")

    def __str__(self) -> str:
        """Return string representation of the schedule.
        
        Returns:
            String representation including scope and frequency mode
        """
        return f"Schedule: {self.scope.value} ({self.frequency_mode.value})"

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current UTC time."""
        self.updated_at = datetime.now(timezone.utc)


@event.listens_for(Schedule, 'before_insert')
@event.listens_for(Schedule, 'before_update')
def validate_schedule(mapper, connection, target):
    """Validate schedule constraints before insert/update.
    
    Args:
        mapper: The mapper in use
        connection: The database connection
        target: The schedule instance being validated
        
    Raises:
        ValueError: If validation fails
    """
    # Validate times per week range
    if target.frequency_mode == FrequencyMode.TIMES_PER_WEEK:
        if not 1 <= target.times_per_week <= 7:
            raise ValueError("times_per_week must be between 1 and 7")
            
    # Validate times per day relationships
    if target.frequency_mode == FrequencyMode.TIMES_PER_DAY:
        if target.max_times_per_day < target.min_times_per_day:
            raise ValueError("max_times_per_day cannot be less than min_times_per_day")
            
    # Validate interval minutes
    if target.frequency_mode == FrequencyMode.FIXED_INTERVAL:
        if target.interval_minutes <= 0:
            raise ValueError("interval_minutes must be positive")


@unique
class EventStatus(str, Enum):
    """Valid status values for scheduled events."""
    
    PENDING = "pending"
    COMPLETED = "completed"
    IGNORED = "ignored"


class ScheduledEvent(BaseModel):
    """Model for individual scheduled events."""

    __tablename__ = "scheduled_events"

    # Required fields
    schedule_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("schedules.uuid", ondelete="CASCADE"),
        nullable=False,
        init=True,
        default=None,
    )
    flash_card_uuid: Mapped[UUID] = mapped_column(
        ForeignKey("flash_cards.uuid", ondelete="CASCADE"),
        nullable=False,
        init=True,
        default=None,
    )
    scheduled_datetime: Mapped[datetime] = mapped_column(
        nullable=False,
        init=True,
        default=None,
    )
    status: Mapped[EventStatus] = mapped_column(
        SQLEnum(EventStatus),
        nullable=False,
        default=EventStatus.PENDING,
        init=True,
    )

    # Relationship references (not in init)
    schedule: Mapped[Schedule] = relationship(
        back_populates="events",
        init=False,
        lazy="selectin",
    )
    flash_card: Mapped[FlashCard] = relationship(
        init=False,
        lazy="selectin",
    )

    def __post_init__(self) -> None:
        """Validate required fields after initialization.
        
        Raises:
            ValueError: If any required field is None
        """
        if self.schedule_uuid is None:
            raise ValueError("schedule_uuid is required")
        if self.flash_card_uuid is None:
            raise ValueError("flash_card_uuid is required")
        if self.scheduled_datetime is None:
            raise ValueError("scheduled_datetime is required")
        if self.status is None:
            raise ValueError("status is required")

    def __str__(self) -> str:
        """Return string representation of the scheduled event.
        
        Returns:
            String with datetime and status
        """
        return f"Event: {self.scheduled_datetime} ({self.status.value})"

    def update_timestamp(self) -> None:
        """Update the updated_at timestamp to current UTC time."""
        self.updated_at = datetime.now(timezone.utc)
