"""Unit tests for Schedule and ScheduledEvent models."""

from datetime import datetime, timedelta, timezone
import pytest
from uuid import UUID

from database.models.schedule import (
    Schedule,
    ScheduledEvent,
    Scope,
    FrequencyMode,
    EventStatus,
)
from database.models.schedule_schema import ScheduleSchema, ScheduledEventSchema
from marshmallow import ValidationError


@pytest.fixture
def sample_schedule(db_session, sample_category):
    """Create a sample schedule for testing."""
    schedule = Schedule(
        scope=Scope.CATEGORY,
        category_uuid=sample_category.uuid,
        allowed_days="Mon,Wed,Fri",
        start_hour=9,
        end_hour=17,
        frequency_mode=FrequencyMode.TIMES_PER_WEEK,
        times_per_week=3,
    )
    db_session.add(schedule)
    db_session.commit()
    return schedule


@pytest.fixture
def sample_scheduled_event(db_session, sample_schedule, sample_flash_card):
    """Create a sample scheduled event for testing."""
    event = ScheduledEvent(
        schedule_uuid=sample_schedule.uuid,
        flash_card_uuid=sample_flash_card.uuid,
        scheduled_datetime=datetime.now(timezone.utc) + timedelta(hours=1),
        status=EventStatus.PENDING,
    )
    db_session.add(event)
    db_session.commit()
    return event


class TestSchedule:
    """Test suite for Schedule model."""

    def test_schedule_creation(self, sample_category):
        """Test creating a schedule with valid data."""
        schedule = Schedule(
            scope=Scope.CATEGORY,
            category_uuid=sample_category.uuid,
            allowed_days="Mon,Wed,Fri",
            start_hour=9,
            end_hour=17,
            frequency_mode=FrequencyMode.TIMES_PER_WEEK,
            times_per_week=3,
        )
        
        assert isinstance(schedule.uuid, UUID)
        assert schedule.scope == Scope.CATEGORY
        assert schedule.category_uuid == sample_category.uuid
        assert schedule.allowed_days == "Mon,Wed,Fri"
        assert schedule.start_hour == 9
        assert schedule.end_hour == 17
        assert schedule.frequency_mode == FrequencyMode.TIMES_PER_WEEK
        assert schedule.times_per_week == 3
        assert schedule.active is True
        assert schedule.deleted is False

    def test_schedule_missing_required_fields(self):
        """Test that schedule creation fails without required fields."""
        with pytest.raises(ValueError, match="scope is required"):
            Schedule(
                allowed_days="Mon,Wed,Fri",
                start_hour=9,
                end_hour=17,
                frequency_mode=FrequencyMode.TIMES_PER_WEEK,
                times_per_week=3,
            )

    def test_schedule_invalid_hours(self, sample_category, db_session):
        """Test that schedule creation fails with invalid hours."""
        # Test invalid start hour
        schedule = Schedule(
            scope=Scope.CATEGORY,
            category_uuid=sample_category.uuid,
            allowed_days="Mon,Wed,Fri",
            start_hour=24,  # Invalid
            end_hour=17,
            frequency_mode=FrequencyMode.TIMES_PER_WEEK,
            times_per_week=3,
        )
        db_session.add(schedule)
        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            db_session.commit()
        db_session.rollback()

        # Test invalid end hour
        schedule = Schedule(
            scope=Scope.CATEGORY,
            category_uuid=sample_category.uuid,
            allowed_days="Mon,Wed,Fri",
            start_hour=9,
            end_hour=24,  # Invalid
            frequency_mode=FrequencyMode.TIMES_PER_WEEK,
            times_per_week=3,
        )
        db_session.add(schedule)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

        # Test end hour before start hour
        schedule = Schedule(
            scope=Scope.CATEGORY,
            category_uuid=sample_category.uuid,
            allowed_days="Mon,Wed,Fri",
            start_hour=17,
            end_hour=9,  # Invalid: before start_hour
            frequency_mode=FrequencyMode.TIMES_PER_WEEK,
            times_per_week=3,
        )
        db_session.add(schedule)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

    def test_schedule_invalid_frequency(self, sample_category, db_session):
        """Test that schedule creation fails with invalid frequency settings."""
        # Test invalid times per week
        schedule = Schedule(
            scope=Scope.CATEGORY,
            category_uuid=sample_category.uuid,
            allowed_days="Mon,Wed,Fri",
            start_hour=9,
            end_hour=17,
            frequency_mode=FrequencyMode.TIMES_PER_WEEK,
            times_per_week=8,  # Invalid: > 7
        )
        db_session.add(schedule)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

        # Test invalid times per day
        schedule = Schedule(
            scope=Scope.CATEGORY,
            category_uuid=sample_category.uuid,
            allowed_days="Mon,Wed,Fri",
            start_hour=9,
            end_hour=17,
            frequency_mode=FrequencyMode.TIMES_PER_DAY,
            min_times_per_day=5,
            max_times_per_day=3,  # Invalid: less than min
        )
        db_session.add(schedule)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

        # Test invalid interval
        schedule = Schedule(
            scope=Scope.CATEGORY,
            category_uuid=sample_category.uuid,
            allowed_days="Mon,Wed,Fri",
            start_hour=9,
            end_hour=17,
            frequency_mode=FrequencyMode.FIXED_INTERVAL,
            interval_minutes=0,  # Invalid: must be positive
        )
        db_session.add(schedule)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

    def test_schedule_string_representation(self, sample_schedule):
        """Test the string representation of a schedule."""
        expected = f"Schedule: {sample_schedule.scope.value} ({sample_schedule.frequency_mode.value})"
        assert str(sample_schedule) == expected


class TestScheduledEvent:
    """Test suite for ScheduledEvent model."""

    def test_event_creation(self, sample_schedule, sample_flash_card):
        """Test creating a scheduled event with valid data."""
        scheduled_time = datetime.now(timezone.utc) + timedelta(hours=1)
        event = ScheduledEvent(
            schedule_uuid=sample_schedule.uuid,
            flash_card_uuid=sample_flash_card.uuid,
            scheduled_datetime=scheduled_time,
            status=EventStatus.PENDING,
        )
        
        assert isinstance(event.uuid, UUID)
        assert event.schedule_uuid == sample_schedule.uuid
        assert event.flash_card_uuid == sample_flash_card.uuid
        assert event.scheduled_datetime == scheduled_time
        assert event.status == EventStatus.PENDING
        assert event.active is True
        assert event.deleted is False

    def test_event_missing_required_fields(self, sample_schedule, sample_flash_card):
        """Test that event creation fails without required fields."""
        scheduled_time = datetime.now(timezone.utc) + timedelta(hours=1)
        
        with pytest.raises(ValueError, match="schedule_uuid is required"):
            ScheduledEvent(
                flash_card_uuid=sample_flash_card.uuid,
                scheduled_datetime=scheduled_time,
                status=EventStatus.PENDING,
            )

        with pytest.raises(ValueError, match="flash_card_uuid is required"):
            ScheduledEvent(
                schedule_uuid=sample_schedule.uuid,
                scheduled_datetime=scheduled_time,
                status=EventStatus.PENDING,
            )

        with pytest.raises(ValueError, match="scheduled_datetime is required"):
            ScheduledEvent(
                schedule_uuid=sample_schedule.uuid,
                flash_card_uuid=sample_flash_card.uuid,
                status=EventStatus.PENDING,
            )

    def test_event_string_representation(self, sample_scheduled_event):
        """Test the string representation of a scheduled event."""
        expected = f"Event: {sample_scheduled_event.scheduled_datetime} ({sample_scheduled_event.status.value})"
        assert str(sample_scheduled_event) == expected


class TestScheduleSchema:
    """Test suite for ScheduleSchema."""

    def test_serialize_schedule(self, sample_schedule):
        """Test serializing a schedule to JSON."""
        schema = ScheduleSchema()
        result = schema.dump(sample_schedule)
        
        assert isinstance(result, dict)
        serialized_uuid = str(sample_schedule.uuid)
        assert result.get("uuid") == serialized_uuid
        assert result.get("scope") == sample_schedule.scope.value
        assert result.get("allowed_days") == sample_schedule.allowed_days
        assert result.get("start_hour") == sample_schedule.start_hour
        assert result.get("end_hour") == sample_schedule.end_hour
        assert result.get("frequency_mode") == sample_schedule.frequency_mode.value
        assert result.get("times_per_week") == sample_schedule.times_per_week
        assert result.get("schema_version") == schema.__version__

    def test_deserialize_valid_data(self, sample_category, db_session):
        """Test deserializing valid JSON data to a schedule."""
        schema = ScheduleSchema()
        data = {
            "scope": "category",
            "category_uuid": str(sample_category.uuid),
            "allowed_days": "Mon,Wed,Fri",
            "start_hour": 9,
            "end_hour": 17,
            "frequency_mode": "times_per_week",
            "times_per_week": 3,
        }
        result = schema.load(data, session=db_session)

        assert isinstance(result, Schedule)
        assert result.scope == Scope.CATEGORY
        assert result.category_uuid == sample_category.uuid
        assert result.allowed_days == "Mon,Wed,Fri"
        assert result.start_hour == 9
        assert result.end_hour == 17
        assert result.frequency_mode == FrequencyMode.TIMES_PER_WEEK
        assert result.times_per_week == 3

    def test_deserialize_invalid_data(self, sample_category, db_session):
        """Test validation errors for invalid schedule data."""
        schema = ScheduleSchema()
        
        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, session=db_session)
        assert "scope" in exc_info.value.messages
        assert "allowed_days" in exc_info.value.messages
        assert "frequency_mode" in exc_info.value.messages

        # Test invalid allowed_days format
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "scope": "category",
                "category_uuid": str(sample_category.uuid),
                "allowed_days": "Monday,Wednesday",  # Invalid format
                "start_hour": 9,
                "end_hour": 17,
                "frequency_mode": "times_per_week",
                "times_per_week": 3,
            }, session=db_session)
        assert "allowed_days" in exc_info.value.messages

        # Test missing frequency-specific fields
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "scope": "category",
                "category_uuid": str(sample_category.uuid),
                "allowed_days": "Mon,Wed,Fri",
                "start_hour": 9,
                "end_hour": 17,
                "frequency_mode": "times_per_week",
                # Missing times_per_week
            }, session=db_session)
        assert "times_per_week is required" in str(exc_info.value)


class TestScheduledEventSchema:
    """Test suite for ScheduledEventSchema."""

    def test_serialize_event(self, sample_scheduled_event):
        """Test serializing a scheduled event to JSON."""
        schema = ScheduledEventSchema()
        result = schema.dump(sample_scheduled_event)
        
        assert isinstance(result, dict)
        serialized_uuid = str(sample_scheduled_event.uuid)
        assert result.get("uuid") == serialized_uuid
        assert result.get("schedule_uuid") == str(sample_scheduled_event.schedule_uuid)
        assert result.get("flash_card_uuid") == str(sample_scheduled_event.flash_card_uuid)
        assert "scheduled_datetime" in result
        assert result.get("status") == sample_scheduled_event.status.value
        assert result.get("schema_version") == schema.__version__

    def test_deserialize_valid_data(self, sample_schedule, sample_flash_card, db_session):
        """Test deserializing valid JSON data to a scheduled event."""
        schema = ScheduledEventSchema()
        scheduled_time = datetime.now(timezone.utc) + timedelta(hours=1)
        data = {
            "schedule_uuid": str(sample_schedule.uuid),
            "flash_card_uuid": str(sample_flash_card.uuid),
            "scheduled_datetime": scheduled_time.isoformat(),
            "status": "pending",
        }
        result = schema.load(data, session=db_session)

        assert isinstance(result, ScheduledEvent)
        assert result.schedule_uuid == sample_schedule.uuid
        assert result.flash_card_uuid == sample_flash_card.uuid
        assert result.status == EventStatus.PENDING

    def test_deserialize_invalid_data(self, db_session):
        """Test validation errors for invalid event data."""
        schema = ScheduledEventSchema()

        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, session=db_session)
        assert "schedule_uuid" in exc_info.value.messages
        assert "flash_card_uuid" in exc_info.value.messages
        assert "scheduled_datetime" in exc_info.value.messages

        # Test invalid status
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "schedule_uuid": "123e4567-e89b-12d3-a456-426614174000",
                "flash_card_uuid": "123e4567-e89b-12d3-a456-426614174000",
                "scheduled_datetime": datetime.now(timezone.utc).isoformat(),
                "status": "invalid_status",  # Invalid status
            }, session=db_session)
        assert "status" in exc_info.value.messages
