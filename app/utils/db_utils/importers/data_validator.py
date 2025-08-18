from typing import Dict, Any, Optional
import re
from decimal import Decimal, InvalidOperation
from app.core.core_database import DatabaseManager
from app.core.core_errors import DatabaseError
from app.core.core_logging import logger # Use central app logger

class DataValidator:
    """Handles data validation for imports."""

    @staticmethod
    def validate_pump_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize pump data before import."""
        try:
            validated_data = {}
            # Use generic helpers for validation and sanitization
            validated_data['sku'] = DataValidator.validate_text(data.get('sku'), 'sku')
            validated_data['name'] = DataValidator.validate_text(data.get('name'), 'name')
            
            # Optional fields
            validated_data['ie_class'] = DataValidator.validate_text(data.get('ie_class'), 'ie_class', required=False)
            if validated_data['ie_class'] and not re.match(r'^IE[1-5]$', validated_data['ie_class']):
                raise ValueError(f"Invalid IE class format for value: {validated_data['ie_class']}")

            # Numeric fields
            numeric_fields = ['poles', 'kw', 'mei', 'weight', 'length', 'width', 'height']
            for field in numeric_fields:
                if data.get(field) is not None:
                    validated_data[field] = DataValidator.validate_numeric(data[field], field)
            
            return validated_data
        except ValueError as e:
            logger.error(f"Pump data validation failed: {e}", exc_info=True)
            raise # Re-raise the specific ValueError

    @staticmethod
    def validate_bom_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate BOM data before import, checking foreign key references."""
        try:
            validated_data = {}
            # Validate required pump SKU and its existence
            pump_sku = DataValidator.validate_text(data.get('pump_sku'), 'pump_sku')
            DataValidator.validate_reference(pump_sku, 'pump_sku', 'general_pump_details', 'sku')
            validated_data['pump_sku'] = pump_sku
            
            # Validate optional inertia base and its existence
            if base_num := data.get('inertia_base_part_number'):
                base_num_clean = DataValidator.validate_text(base_num, 'inertia_base_part_number', required=False)
                if base_num_clean:
                    DataValidator.validate_reference(base_num_clean, 'inertia_base_part_number', 'inertia_bases', 'part_number')
                    validated_data['inertia_base_part_number'] = base_num_clean

            # Validate optional seismic spring and its existence
            if spring_num := data.get('seismic_spring_part_number'):
                spring_num_clean = DataValidator.validate_text(spring_num, 'seismic_spring_part_number', required=False)
                if spring_num_clean:
                    DataValidator.validate_reference(spring_num_clean, 'seismic_spring_part_number', 'seismic_springs', 'part_number')
                    validated_data['seismic_spring_part_number'] = spring_num_clean

            return validated_data
        except (ValueError, DatabaseError) as e:
            logger.error(f"BOM data validation failed: {e}", exc_info=True)
            raise ValueError(f"BOM data validation failed: {e}")

    @staticmethod
    def validate_numeric(value: Any, field_name: str, allow_zero: bool = False, required: bool = True) -> Optional[Decimal]:
        """Validates that a value is a valid Decimal."""
        if value is None or str(value).strip() == '':
            if required:
                raise ValueError(f"Numeric field '{field_name}' is required.")
            return None
        
        try:
            d_value = Decimal(str(value))
            if not allow_zero and d_value <= 0:
                raise ValueError(f"Numeric field '{field_name}' must be positive.")
            return d_value
        except InvalidOperation:
            raise ValueError(f"Invalid value for numeric field '{field_name}': '{value}'")

    @staticmethod
    def validate_text(value: Any, field_name: str, required: bool = True) -> Optional[str]:
        """Validates that a value is a non-empty string."""
        if value is None:
            if required:
                raise ValueError(f"Text field '{field_name}' is required.")
            return None
        
        s_value = str(value).strip()
        if required and not s_value:
            raise ValueError(f"Text field '{field_name}' cannot be empty.")
        
        return s_value if s_value else None

    @staticmethod
    def validate_reference(value: str, field_name: str, table: str, column: str) -> None:
        """Validates that a reference exists in the database using secure identifiers."""
        # Sanitize table and column names to prevent SQL injection
        if not re.match(r'^[a-zA-Z0-9_]+$', table) or not re.match(r'^[a-zA-Z0-9_]+$', column):
            logger.error(f"Invalid characters in table ('{table}') or column ('{column}') name during validation.")
            raise ValueError("Invalid table or column name for validation.")
            
        try:
            query = f'SELECT 1 FROM "{table}" WHERE "{column}" = %s'
            if not DatabaseManager.execute_query(query, (value,)):
                raise ValueError(f"Referenced {field_name} '{value}' does not exist in table '{table}'.")
        except DatabaseError as e:
            logger.error(f"Database error while validating reference for {field_name} '{value}': {e}", exc_info=True)
            raise