"""CSV serialization with header mapping support."""

import csv
from dataclasses import dataclass
from typing import Any, Dict, List, TextIO, TypeVar

from marshmallow import  ValidationError

from core.serialization.base import BaseSchema

T = TypeVar("T")


@dataclass
class HeaderMap:
    """CSV header mapping configuration."""

    export_name: str
    """The name to use in CSV exports."""
    
    import_names: List[str]
    """Alternative names to accept during import."""


class CSVSchema(BaseSchema):
    """Schema for CSV serialization with header mapping."""

    # Override in subclasses to define header mappings
    header_mappings: Dict[str, HeaderMap] = {}

    def dump_to_csv(
        self, 
        data: List[Dict[str, Any]], 
        file: TextIO, 
        *,
        include_header: bool = True
    ) -> None:
        """Write data to CSV file.
        
        Args:
            data: List of data dictionaries to serialize
            file: File-like object to write to
            include_header: Whether to write header row
            
        Raises:
            ValidationError: If serialization fails
        """
        writer = csv.DictWriter(
            file,
            fieldnames=[h.export_name for h in self.header_mappings.values()],
            dialect="excel",
        )
        
        if include_header:
            writer.writeheader()
            
        for row in data:
            serialized = self.dump(row, many=False)  # Explicitly handle single item
            if isinstance(serialized, dict):  # Type guard for static analysis
                csv_row = {
                    self.header_mappings[field].export_name: value
                    for field, value in serialized.items()
                    if field in self.header_mappings
                }
                writer.writerow(csv_row)
            else:
                raise ValidationError("Expected dictionary for single row serialization")

    def load_from_csv(
        self, 
        file: TextIO, 
        *, 
        skip_header: bool = True
    ) -> List[Dict[str, Any]]:
        """Read data from CSV file.
        
        Args:
            file: File-like object to read from
            skip_header: Whether to skip the first row as header
            
        Returns:
            List of deserialized data dictionaries
            
        Raises:
            ValidationError: If deserialization fails
        """
        reader = csv.DictReader(file) if skip_header else csv.DictReader(file, [])
        
        # Create reverse mapping for import
        field_map = {}
        for field, header in self.header_mappings.items():
            for import_name in header.import_names:
                field_map[import_name.lower()] = field

        results = []
        for row in reader:
            # Convert CSV field names to schema field names
            data = {}
            for csv_field, value in row.items():
                schema_field = field_map.get(csv_field.lower())
                if schema_field:
                    data[schema_field] = value
            
            # Deserialize the mapped data
            try:
                deserialized = self.load(data)
                results.append(deserialized)
            except ValidationError as e:
                # Log error and continue
                # Will implement proper error handling when logging is ready
                continue
                
        return results
