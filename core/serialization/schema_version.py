"""Schema version handling mixin."""

from typing import Any, Dict

from marshmallow import fields, pre_load, post_dump, ValidationError
from packaging import version


class SchemaVersionMixin:
    """Mixin to add schema version handling to schemas."""

    __version__ = "1.0.0"  # Default version

    # Allow schema_version in input but don't require it
    schema_version = fields.String(load_default=None)

    @pre_load
    def validate_schema_version(self, data: Dict[str, Any], **_: Any) -> Dict[str, Any]:
        """Validate schema version compatibility.
        
        Args:
            data: Raw input data
            **_: Additional arguments
            
        Returns:
            Validated data dictionary
            
        Raises:
            ValidationError: If schema version is incompatible
        """
        schema_ver = data.get('schema_version')
        if not schema_ver:
            return data
            
        current = version.parse(self.__version__)
        incoming = version.parse(schema_ver)
        
        # If incoming major version is greater -> newer (breaking)
        if incoming.major > current.major:
            raise ValidationError(
                f"Data schema version {schema_ver} is newer than supported {self.__version__}"
            )

        # If incoming major is less -> older (potentially unsupported)
        if incoming.major < current.major:
            raise ValidationError(
                f"Data schema version {schema_ver} is older than supported {self.__version__}"
            )

        # Same major: ensure incoming minor is not greater than current minor
        if incoming.minor > current.minor:
            raise ValidationError(
                f"Data schema version {schema_ver} is newer than supported {self.__version__}"
            )

        return data

    @post_dump
    def add_schema_version(self, data: Dict[str, Any], **_: Any) -> Dict[str, Any]:
        """Add schema version to serialized data.
        
        Args:
            data: The serialized data dictionary
            **_: Additional arguments (unused)
            
        Returns:
            Updated data dictionary with schema version
        """
        data["schema_version"] = self.__version__
        return data
