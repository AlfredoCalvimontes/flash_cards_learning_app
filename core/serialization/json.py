"""JSON serialization with schema versioning support."""

from typing import Any, Dict, Optional, TypeVar
from uuid import UUID

from marshmallow import EXCLUDE, ValidationError, fields, post_dump, pre_load

from core.serialization.base import BaseModelSchema

T = TypeVar("T")

class VersionedSchema(BaseModelSchema):
    """Schema with version tracking for safe migrations."""

    __version__ = "1.0.0"

    class Meta:
        """Schema metadata."""
        unknown = EXCLUDE
        load_instance = True
        include_relationships = True

    schema_version = fields.String(dump_default=__version__)

    @pre_load
    def check_version(self, data: Dict[str, Any], **_: Any) -> Dict[str, Any]:
        """Check schema version before loading data.
        
        Args:
            data: Raw data to deserialize
            **_: Additional arguments (unused)
            
        Returns:
            The data to deserialize
            
        Raises:
            ValidationError: If schema version is incompatible
        """
        version = data.get("schema_version", "1.0.0")
        if version > self.__version__:
            raise ValidationError(
                f"Data schema version {version} is newer than supported {self.__version__}"
            )
        return data

    @post_dump
    def add_version(self, data: Dict[str, Any], **_: Any) -> Dict[str, Any]:
        """Add schema version to serialized data.
        
        Args:
            data: The serialized data
            **_: Additional arguments (unused)
            
        Returns:
            Data with schema version added
        """
        data["schema_version"] = self.__version__
        return data


class UUIDField(fields.UUID):
    """UUID field that handles string conversion."""

    def _serialize(
        self, value: Optional[UUID], _attr: Optional[str], _obj: Any, **_: Any
    ) -> Optional[str]:
        """Serialize UUID to string.
        
        Args:
            value: The UUID to serialize
            _attr: Unused attribute/key in the raw data
            _obj: Unused parent object
            **_: Additional unused arguments
            
        Returns:
            String representation of UUID or None
        """
        if value is None:
            return None
        return str(value)

    def _deserialize(
        self, value: Any, _attr: Optional[str], _data: Any, **_: Any
    ) -> Optional[UUID]:
        """Deserialize string to UUID.
        
        Args:
            value: The value to deserialize
            _attr: Unused attribute/key in the raw data
            _data: Unused raw input data
            **_: Additional unused arguments
            
        Returns:
            UUID object or None
            
        Raises:
            ValidationError: If value cannot be converted to UUID
        """
        if value is None:
            return None
        try:
            return UUID(str(value))
        except (ValueError, AttributeError) as e:
            raise ValidationError("Invalid UUID format") from e
