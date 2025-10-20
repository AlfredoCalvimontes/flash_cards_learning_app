"""Unit tests for Settings model and schema."""

from datetime import datetime, timezone

import pytest
from marshmallow import ValidationError

from database.models.settings import Settings
from database.models.schemas import SettingsSchema


@pytest.fixture
def sample_settings(db_session, request):
    """Create a sample settings entry for testing.
    
    Creates settings with a unique key based on the test name.
    """
    # Create unique key using test name
    unique_key = f"test.config.{request.node.name}"
    
    settings = Settings(
        setting_key=unique_key,
        setting_value={"theme": "dark", "notifications": True},
    )
    db_session.add(settings)
    db_session.commit()
    return settings


class TestSettings:
    """Test suite for Settings model."""

    def test_settings_creation(self, db_session):
        """Test creating settings with valid data."""
        settings = Settings(
            setting_key="app.theme",
            setting_value={"mode": "dark", "accent": "#FF0000"},
        )
        db_session.add(settings)
        db_session.commit()

        assert settings.setting_key == "app.theme"
        assert settings.setting_value["mode"] == "dark"
        assert settings.setting_value["accent"] == "#FF0000"
        assert settings.active is True
        assert settings.deleted is False
        assert isinstance(settings.created_at, datetime)
        assert isinstance(settings.updated_at, datetime)

    def test_settings_required_fields(self):
        """Test that settings creation fails without required fields."""
        with pytest.raises(ValueError, match="setting_key is required"):
            Settings(
                setting_value={"test": "value"},
            )

        with pytest.raises(ValueError, match="setting_value is required"):
            Settings(
                setting_key="test.key",
            )

    def test_settings_unique_key(self, db_session):
        """Test that setting keys must be unique."""
        key = "unique.key"
        settings1 = Settings(
            setting_key=key,
            setting_value={"test": 1},
        )
        db_session.add(settings1)
        db_session.commit()

        settings2 = Settings(
            setting_key=key,  # Same key
            setting_value={"test": 2},
        )
        db_session.add(settings2)
        with pytest.raises(Exception):  # SQLAlchemy will raise an integrity error
            db_session.commit()

    def test_settings_value_types(self, db_session):
        """Test that setting values support various JSON types."""
        settings = Settings(
            setting_key="types.test",
            setting_value={
                "string": "test",
                "integer": 123,
                "float": 3.14,
                "boolean": True,
                "null": None,
                "array": [1, 2, 3],
                "object": {"nested": "value"},
            },
        )
        db_session.add(settings)
        db_session.commit()

        # Test each type was stored correctly
        assert isinstance(settings.setting_value["string"], str)
        assert isinstance(settings.setting_value["integer"], int)
        assert isinstance(settings.setting_value["float"], float)
        assert isinstance(settings.setting_value["boolean"], bool)
        assert settings.setting_value["null"] is None
        assert isinstance(settings.setting_value["array"], list)
        assert isinstance(settings.setting_value["object"], dict)

    def test_settings_timestamp_update(self, db_session, sample_settings):
        """Test that updated_at is modified when settings are updated."""
        original_timestamp = sample_settings.updated_at
        
        sample_settings.setting_value["new_key"] = "new_value"
        sample_settings.update_timestamp()
        db_session.commit()
        
        assert sample_settings.updated_at > original_timestamp

    def test_settings_string_representation(self, sample_settings):
        """Test the string representation of settings."""
        expected = f"Setting: {sample_settings.setting_key} (Type: dict)"
        assert str(sample_settings) == expected


class TestSettingsSchema:
    """Test suite for SettingsSchema."""

    def test_serialize_settings(self, sample_settings):
        """Test serializing settings to JSON."""
        schema = SettingsSchema()
        result = schema.dump(sample_settings)
        
        assert isinstance(result, dict)
        assert result.get("setting_key") == sample_settings.setting_key
        assert result.get("setting_value") == sample_settings.setting_value
        assert result.get("active") is True
        assert result.get("deleted") is False
        assert "created_at" in result
        assert "updated_at" in result
        assert "schema_version" in result

    def test_deserialize_valid_data(self, db_session):
        """Test deserializing valid JSON data to settings."""
        schema = SettingsSchema()
        data = {
            "setting_key": "test.key",
            "setting_value": {
                "str_value": "test",
                "int_value": 123,
                "bool_value": True,
            },
        }
        result = schema.load(data, session=db_session)

        assert isinstance(result, Settings)
        assert result.setting_key == "test.key"
        assert result.setting_value["str_value"] == "test"
        assert result.setting_value["int_value"] == 123
        assert result.setting_value["bool_value"] is True

    def test_deserialize_invalid_data(self, db_session):
        """Test validation errors for invalid data."""
        schema = SettingsSchema()

        # Test missing required fields
        with pytest.raises(ValidationError) as exc_info:
            schema.load({}, session=db_session)
        assert "setting_key" in exc_info.value.messages
        assert "setting_value" in exc_info.value.messages

        # Test empty key
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "setting_key": "",
                "setting_value": {"test": "value"},
            }, session=db_session)
        assert "setting_key" in exc_info.value.messages

        # Test empty value
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "setting_key": "test.key",
                "setting_value": {},
            }, session=db_session)
        assert "setting_value" in exc_info.value.messages

        # Test key too long
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "setting_key": "x" * 101,  # 101 chars
                "setting_value": {"test": "value"},
            }, session=db_session)
        assert "setting_key" in exc_info.value.messages

    def test_schema_version_handling(self, db_session):
        """Test schema version handling in serialization."""
        schema = SettingsSchema()
        settings = Settings(
            setting_key="test.key",
            setting_value={"test": "value"},
        )
        
        result = schema.dump(settings)
        assert isinstance(result, dict)
        assert result.get("schema_version") == schema.__version__

        # Test incompatible version
        with pytest.raises(ValidationError) as exc_info:
            schema.load({
                "schema_version": "999.0.0",
                "setting_key": "test.key",
                "setting_value": {"test": "value"},
            }, session=db_session)
        assert "schema version" in str(exc_info.value).lower()
