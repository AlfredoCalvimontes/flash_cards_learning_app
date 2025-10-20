"""Schema for Settings model."""

from __future__ import annotations

from typing import Any, Dict

from marshmallow import fields, validates_schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from core.serialization.schema_version import SchemaVersionMixin
from database.models.settings import Settings


class SettingsSchema(SQLAlchemyAutoSchema, SchemaVersionMixin):
    """Schema for serializing/deserializing Settings model."""

    class Meta:
        """Schema metadata."""
        model = Settings
        include_relationships = True
        include_fk = True
        load_instance = True
        # Only include fields marked with init=True in constructor
        constructor_fields = [
            "setting_key",
            "setting_value",
        ]
        
    __version__ = "1.0.0"  # Initial schema version

    # Required fields
    setting_key = fields.String(required=True)
    setting_value = fields.Dict(keys=fields.String(), values=fields.Raw(), required=True)
    
    # Base model fields
    active = fields.Boolean(load_default=True)
    deleted = fields.Boolean(load_default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_schema(self, data: Dict[str, Any], **_: Any) -> None:
        """Validate schema data.
        
        Args:
            data: The data to validate
            **_: Additional arguments (unused)
            
        Raises:
            ValidationError: If validation fails
        """
        # Check setting_key format
        key = data.get("setting_key", "")
        if not key.strip():
            raise ValidationError("setting_key cannot be empty or whitespace")
        if len(key) > 100:
            raise ValidationError("setting_key cannot be longer than 100 characters")
        
        # Ensure setting_value is not empty
        if not data.get("setting_value"):
            raise ValidationError("setting_value cannot be empty")
