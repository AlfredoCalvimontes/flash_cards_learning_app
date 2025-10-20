"""Schema definitions for database models."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Generator, Optional, Set, Type, TypeVar

from marshmallow import fields, validate, post_load, pre_load, ValidationError
from packaging import version

from core.serialization.json import UUIDField, VersionedSchema
from database.models.base import BaseModel
from database.models.category import Category
from database.models.flash_card import FlashCard


T = TypeVar('T', bound=BaseModel)


class BaseModelSchema(VersionedSchema):
    """Base schema for all database models with common fields and behaviors."""
    
    class Meta:
        """Schema metadata."""
        load_instance = True
        include_relationships = True
    
    # Common fields for all models
    uuid = UUIDField(dump_only=True)
    version = fields.Integer(dump_only=True)
    active = fields.Boolean(load_default=True)
    deleted = fields.Boolean(load_default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    schema_version = fields.String(dump_only=True)
    
    @contextmanager
    def session_context(self) -> Generator:
        """Context manager for schema session handling.
        
        Usage:
            with schema.session_context():
                result = schema.load(data)
        
        Yields:
            None
        """
        session = getattr(self, '_session', None)
        try:
            yield
        finally:
            if session:
                self._session = None
    
    @pre_load
    def validate_schema_version(self, data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        """Validate schema version compatibility.
        
        Args:
            data: Raw input data
            **kwargs: Additional arguments
            
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
        
        # Major version must match, minor version must be <= current
        if (incoming.major != current.major or 
            incoming.minor > current.minor):
            raise ValidationError(
                f"Schema version {schema_ver} is incompatible with current version {self.__version__}"
            )
        
        return data
    
    @classmethod
    def _get_relationship_cycles(cls) -> Dict[str, Set[str]]:
        """Get cyclic relationships to handle nested serialization.
        
        Returns:
            Dictionary mapping field names to sets of fields to exclude
            when serializing that relationship
        """
        return {}


class FlashCardSchema(BaseModelSchema):
    """Schema for serializing/deserializing FlashCard models."""

    class Meta:
        """Schema metadata."""
        model = FlashCard
        include_relationships = True
        # Only include fields marked with init=True in constructor
        constructor_fields = ["name", "question", "answer", "category_uuid"]
        
    __version__ = "1.0.0"  # Initial schema version

    # Required fields (init=True)
    uuid = UUIDField(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    question = fields.String(required=True, validate=validate.Length(min=1, max=1000))
    answer = fields.String(required=True, validate=validate.Length(min=1, max=2000))
    category_uuid = UUIDField(required=True)
    
    # Optional fields (init=False)
    difficulty = fields.Integer(
        validate=validate.Range(min=1, max=10), 
        load_default=5,
        dump_default=5
    )
    version = fields.Integer(dump_only=True)
    active = fields.Boolean(dump_default=True)
    deleted = fields.Boolean(dump_default=False)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @classmethod
    def _get_relationship_cycles(cls) -> Dict[str, Set[str]]:
        """Define relationship cycles for FlashCard.
        
        Returns:
            Dictionary mapping field names to sets of fields to exclude
            to prevent infinite recursion
        """
        return {
            "category": {"flash_cards"}
        }
    
    @post_load
    def make_instance(self, data: Dict[str, Any], **kwargs: Any) -> FlashCard:
        """Create FlashCard instance with constructor and non-constructor fields.
        
        Args:
            data: Deserialized data dictionary
            **kwargs: Additional arguments passed to post_load
            
        Returns:
            FlashCard instance with all fields set
            
        Raises:
            ValidationError: If required constructor fields are missing
        """
        # Validate all required constructor fields are present
        missing = [f for f in self.Meta.constructor_fields if f not in data]
        if missing:
            raise ValidationError({
                f: ["Field is required."] for f in missing
            })
            
        # Split data into constructor and non-constructor fields
        constructor_args = {
            k: v for k, v in data.items() 
            if k in self.Meta.constructor_fields
        }
        
        try:
            # Create instance with constructor fields
            instance = self.opts.model(**constructor_args)
        except (TypeError, ValueError) as e:
            raise ValidationError(str(e))
            
        # Set non-constructor fields after creation
        for k, v in data.items():
            if k not in self.Meta.constructor_fields:
                try:
                    setattr(instance, k, v)
                except (AttributeError, ValueError) as e:
                    raise ValidationError({k: [str(e)]})
                
        return instance


class CategorySchema(BaseModelSchema):
    """Schema for serializing/deserializing Category models."""

    class Meta:
        """Schema metadata."""
        model = Category
        include_relationships = True
        # Only include fields marked with init=True in constructor
        constructor_fields = ["name", "priority"]
        
    __version__ = "1.0.0"  # Initial schema version
    
    @classmethod
    def _get_relationship_cycles(cls) -> Dict[str, Set[str]]:
        """Define relationship cycles for Category.
        
        Returns:
            Dictionary mapping field names to sets of fields to exclude
            to prevent infinite recursion
        """
        return {
            "flash_cards": {"category", "category_uuid"}
        }

    # Base fields
    uuid = UUIDField(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    priority = fields.Integer(required=True, validate=validate.Range(min=1))
    
    # Status fields
    version = fields.Integer(dump_only=True)
    active = fields.Boolean(load_default=True)
    deleted = fields.Boolean(load_default=False)
    
    # Timestamps
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Relationships
    flash_cards = fields.Nested(
        "FlashCardSchema",
        many=True, 
        dump_only=True,
        exclude=("category", "category_uuid")  # Prevent recursion
    )
    
    @post_load
    def make_instance(self, data: Dict[str, Any], **kwargs: Any) -> Category:
        """Create Category instance with constructor and non-constructor fields.
        
        Args:
            data: Deserialized data dictionary
            **kwargs: Additional arguments passed to post_load
            
        Returns:
            Category instance with all fields set
            
        Raises:
            ValidationError: If required constructor fields are missing
        """
        # Validate all required constructor fields are present
        missing = [f for f in self.Meta.constructor_fields if f not in data]
        if missing:
            raise ValidationError({
                f: ["Field is required."] for f in missing
            })
            
        # Split data into constructor and non-constructor fields
        constructor_args = {
            k: v for k, v in data.items() 
            if k in self.Meta.constructor_fields
        }
        
        try:
            # Create instance with constructor fields
            instance = self.opts.model(**constructor_args)
        except (TypeError, ValueError) as e:
            raise ValidationError(str(e))
            
        # Set non-constructor fields after creation
        for k, v in data.items():
            if k not in self.Meta.constructor_fields:
                try:
                    setattr(instance, k, v)
                except (AttributeError, ValueError) as e:
                    raise ValidationError({k: [str(e)]})
                
        return instance
    # Relationships
    flash_cards = fields.Nested(
        lambda: FlashCardSchema(exclude=("category_uuid",)), 
        many=True, 
        dump_only=True
    )
