"""Binary serialization with compression support."""

import gzip
import pickle
from enum import Enum
from typing import Any, BinaryIO, Dict, TypeVar

from marshmallow import ValidationError

from core.serialization.base import BaseSchema

T = TypeVar("T")


class CompressionType(Enum):
    """Supported compression types."""

    NONE = "none"
    GZIP = "gzip"


class BinarySchema(BaseSchema):
    """Schema for binary serialization with compression support."""

    def dump_to_binary(
        self,
        data: Dict[str, Any],
        file: BinaryIO,
        *,
        compression: CompressionType = CompressionType.GZIP,
        protocol: int = pickle.HIGHEST_PROTOCOL,
    ) -> None:
        """Write data to binary file with optional compression.
        
        Args:
            data: Data dictionary to serialize
            file: Binary file-like object to write to
            compression: Type of compression to use
            protocol: Pickle protocol version to use
            
        Raises:
            ValidationError: If serialization fails
            ValueError: If compression type is invalid
        """
        # First serialize with marshmallow
        try:
            serialized = self.dump(data)
        except ValidationError as e:
            raise ValidationError("Failed to serialize data") from e

        # Convert to bytes using pickle for efficient binary storage
        binary_data = pickle.dumps(serialized, protocol=protocol)

        # Apply compression if requested
        if compression == CompressionType.GZIP:
            binary_data = gzip.compress(binary_data)
        elif compression != CompressionType.NONE:
            raise ValueError(f"Unsupported compression type: {compression}")

        file.write(binary_data)

    def load_from_binary(
        self,
        file: BinaryIO,
        *,
        compression: CompressionType = CompressionType.GZIP,
    ) -> Dict[str, Any]:
        """Read data from binary file with optional decompression.
        
        Args:
            file: Binary file-like object to read from
            compression: Type of compression used
            
        Returns:
            Deserialized data dictionary
            
        Raises:
            ValidationError: If deserialization fails
            ValueError: If compression type is invalid or data is corrupt
        """
        binary_data = file.read()

        # Decompress if necessary
        if compression == CompressionType.GZIP:
            try:
                binary_data = gzip.decompress(binary_data)
            except gzip.BadGzipFile as e:
                raise ValueError("Invalid gzip compressed data") from e
        elif compression != CompressionType.NONE:
            raise ValueError(f"Unsupported compression type: {compression}")

        # Unpickle the binary data
        try:
            data = pickle.loads(binary_data)
        except pickle.UnpicklingError as e:
            raise ValueError("Invalid binary data format") from e

        # Deserialize with marshmallow
        try:
            result = self.load(data, many=False)  # Explicitly handle single object
            if isinstance(result, dict):  # Type guard for static analysis
                return result
            raise ValidationError("Expected dictionary from deserialization")
        except ValidationError as e:
            raise ValidationError("Failed to deserialize data") from e
