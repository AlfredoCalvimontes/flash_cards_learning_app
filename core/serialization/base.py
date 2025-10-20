"""Base serialization interfaces."""

from typing import Any, Dict, Optional, TypeVar

from marshmallow import Schema, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from database.models.base import BaseModel
else:
    BaseModel = Any  # Placeholder for runtime

T = TypeVar("T", bound=BaseModel)  # Used for type hints in schema methods





class BaseSchema(Schema):
    """Base schema class with common functionality."""

    class Meta:
        """Schema metadata configuration."""
        
        ordered = True  # Preserve field order
        unknown = "exclude"  # Exclude unknown fields by default
        
    __version__ = "1.0.0"  # Schema version for migration support

    def load_safe(
        self, data: Dict[str, Any], *, partial: bool = False
    ) -> Optional[BaseModel]:
        """Safely load data with validation, returning None on failure.
        
        Args:
            data: Dictionary of data to deserialize
            partial: If True, ignore missing fields that are required
            
        Returns:
            Deserialized model instance or None if validation fails
            
        Note:
            This method catches ValidationError and returns None instead of raising.
            For strict validation, use the standard load() method.
        """
        try:
            result = self.load(data, partial=partial)
            return result if isinstance(result, BaseModel) else None
        except ValidationError:
            return None


class BaseModelSchema(SQLAlchemyAutoSchema):
    """Base schema class for SQLAlchemy models."""
    
    __version__ = "1.0.0"  # Schema version for migration support

    class Meta:
        """Schema metadata configuration."""
        
        load_instance = True  # Deserialize to model instances
        include_fk = True  # Include foreign keys
        include_relationships = True  # Include relationship fields
        unknown = "exclude"  # Exclude unknown fields

    def handle_error(
        self, error: ValidationError, data: Any, *, many: bool, **kwargs: Any
    ) -> None:
        """Custom error handler for validation errors.
        
        Args:
            error: The ValidationError that was raised
            data: The input data that caused the error
            many: Whether the input data was a collection
            **kwargs: Additional keyword arguments
        
        Note:
            This method can be overridden by child classes to customize error handling.
        """
        # Log validation errors here when logging is implemented
        super().handle_error(error, data, many=many, **kwargs)
