"""Schemas for Schedule and ScheduledEvent models."""

from __future__ import annotations

from typing import Any, Dict

from marshmallow import fields, validate, validates_schema, ValidationError
from database.models.fields import EnumField
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from core.serialization.json import UUIDField
from core.serialization.schema_version import SchemaVersionMixin
from database.models.schedule import EventStatus, FrequencyMode, Schedule, ScheduledEvent, Scope


class ScheduleSchema(SQLAlchemyAutoSchema, SchemaVersionMixin):
    """Schema for serializing/deserializing Schedule models."""

    class Meta:
        """Schema metadata."""
        model = Schedule
        include_relationships = True
        include_fk = True
        load_instance = True
        # Only include fields marked with init=True in constructor
        constructor_fields = [
            "scope",
            "category_uuid",
            "flash_card_uuid",
            "allowed_days",
            "start_hour",
            "end_hour",
            "frequency_mode",
            "times_per_week",
            "min_times_per_day",
            "max_times_per_day",
            "interval_minutes",
        ]
        
    __version__ = "1.0.0"  # Initial schema version

    # Base fields
    uuid = UUIDField(dump_only=True)
    version = fields.Integer(dump_only=True)
    active = fields.Boolean(load_default=True)
    deleted = fields.Boolean(load_default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Required fields
    scope = EnumField(Scope, by_value=True, required=True)
    allowed_days = fields.String(
        required=True,
        validate=validate.Regexp(
            r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)(,(Mon|Tue|Wed|Thu|Fri|Sat|Sun))*$",
            error="Invalid allowed_days format. Use comma-separated day abbreviations (Mon,Tue,Wed)",
        ),
    )
    start_hour = fields.Integer(
        required=True,
        validate=validate.Range(min=0, max=23),
    )
    end_hour = fields.Integer(
        required=True,
        validate=validate.Range(min=0, max=23),
    )
    frequency_mode = EnumField(FrequencyMode, by_value=True, required=True)

    # Optional relationship fields
    category_uuid = UUIDField(allow_none=True)
    flash_card_uuid = UUIDField(allow_none=True)

    # Frequency mode specific fields
    times_per_week = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1, max=7),
    )
    min_times_per_day = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1),
    )
    max_times_per_day = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1),
    )
    interval_minutes = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1),
    )

    @validates_schema
    def validate_schema(self, data: Dict[str, Any], **_: Any) -> None:
        """Validate schema based on frequency mode and scope.
        
        Args:
            data: The data to validate
            **_: Additional arguments (unused)
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate scope-specific fields
        scope = data.get("scope")
        if scope == Scope.CATEGORY and not data.get("category_uuid"):
            raise ValidationError("category_uuid is required for category scope")
        if scope == Scope.CARD and not data.get("flash_card_uuid"):
            raise ValidationError("flash_card_uuid is required for card scope")

        # Validate frequency mode specific fields
        mode = data.get("frequency_mode")
        if mode == FrequencyMode.TIMES_PER_WEEK and not data.get("times_per_week"):
            raise ValidationError("times_per_week is required for times_per_week mode")
        elif mode == FrequencyMode.TIMES_PER_DAY:
            if not data.get("min_times_per_day"):
                raise ValidationError("min_times_per_day is required for times_per_day mode")
            if not data.get("max_times_per_day"):
                raise ValidationError("max_times_per_day is required for times_per_day mode")
            if data["min_times_per_day"] > data["max_times_per_day"]:
                raise ValidationError("min_times_per_day cannot be greater than max_times_per_day")
        elif mode == FrequencyMode.FIXED_INTERVAL and not data.get("interval_minutes"):
            raise ValidationError("interval_minutes is required for fixed_interval mode")

        # Validate time range
        if data["start_hour"] >= data["end_hour"]:
            raise ValidationError("end_hour must be greater than start_hour")


class ScheduledEventSchema(SQLAlchemyAutoSchema, SchemaVersionMixin):
    """Schema for serializing/deserializing ScheduledEvent models."""

    class Meta:
        """Schema metadata."""
        model = ScheduledEvent
        include_relationships = True
        include_fk = True
        load_instance = True
        # Only include fields marked with init=True in constructor
        constructor_fields = [
            "schedule_uuid",
            "flash_card_uuid",
            "scheduled_datetime",
            "status",
        ]
        
    __version__ = "1.0.0"  # Initial schema version

    # Base fields
    uuid = UUIDField(dump_only=True)
    version = fields.Integer(dump_only=True)
    active = fields.Boolean(load_default=True)
    deleted = fields.Boolean(load_default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Required fields
    schedule_uuid = UUIDField(required=True)
    flash_card_uuid = UUIDField(required=True)
    scheduled_datetime = fields.DateTime(required=True)
    status = EnumField(EventStatus, by_value=True, load_default=EventStatus.PENDING)
