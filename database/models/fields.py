"""Custom field types for marshmallow schemas."""

from enum import Enum
from typing import Any, Optional, Type, Union

from marshmallow import fields, ValidationError


class EnumField(fields.Field):
    """Field that serializes to/from an Enum value."""

    def __init__(self, enum: Type[Enum], by_value: bool = True, **kwargs: Any) -> None:
        """Initialize the enum field.
        
        Args:
            enum: The Enum class to use
            by_value: If True, use enum values for serialization. If False, use names.
            **kwargs: Additional arguments to pass to the parent
        """
        self.enum = enum
        self.by_value = by_value
        super().__init__(**kwargs)

    def _serialize(self, value: Union[Enum, str, None], attr: str, obj: Any, **kwargs: Any) -> Any:
        """Serialize enum instance to string.
        
        Args:
            value: The value to serialize
            attr: The attribute/key in the raw data to get the value from
            obj: The object that the value was pulled from
            **kwargs: Additional arguments
            
        Returns:
            The serialized value
        """
        if value is None:
            return None
            
        if isinstance(value, str):
            # Already serialized
            return value
            
        if isinstance(value, self.enum):
            if self.by_value:
                return value.value
            return value.name
            
        return str(value)

    def _deserialize(self, value: Any, attr: str, data: Any, **kwargs: Any) -> Optional[Enum]:
        """Deserialize string to enum instance.
        
        Args:
            value: The value to deserialize
            attr: The attribute/key in the raw data to get the value from
            data: The raw data to pull the value from
            **kwargs: Additional arguments
            
        Returns:
            The enum instance or None if value is None
            
        Raises:
            ValidationError: If the value is invalid for this enum
        """
        if value is None:
            return None
            
        if isinstance(value, self.enum):
            return value
            
        try:
            if self.by_value:
                return self.enum(value)
            return getattr(self.enum, str(value).upper())
        except (ValueError, AttributeError) as error:
            values = [e.value if self.by_value else e.name for e in self.enum]
            raise ValidationError(
                f"{value} is not a valid value for {self.enum.__name__}. "
                f"Valid values are: {values}"
            ) from error
