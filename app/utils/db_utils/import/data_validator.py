# app/utils/db_utils/import/data_validator.py

from typing import Dict, Any, Optional
import logging
import re
from decimal import Decimal
from app.core.core_database import DatabaseManager, DatabaseError

logger = logging.getLogger(__name__)

class DataValidator:
    """Handles data validation for imports"""

    @staticmethod
    def validate_pump_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate pump data before import"""
        try:
            # Validate SKU
            if not data.get('sku'):
                raise ValueError("SKU is required")
            
            # Validate name
            if not data.get('name'):
                raise ValueError("Name is required")
            
            # Validate numeric fields
            numeric_fields = {
                'poles': int,
                'kw': Decimal,
                'mei': Decimal,
                'weight': Decimal,
                'length': Decimal,
                'width': Decimal,
                'height': Decimal
            }
            
            for field, field_type in numeric_fields.items():
                if data.get(field) is not None:
                    try:
                        data[field] = field_type(str(data[field]))
                        if data[field] <= 0:
                            raise ValueError(f"{field} must be positive")
                    except (ValueError, TypeError):
                        raise ValueError(f"Invalid {field} value")

            # Validate IE class
            if data.get('ie_class') and not re.match(r'^IE[1-4]$', str(data['ie_class'])):
                raise ValueError("Invalid IE class format")

            return data

        except Exception as e:
            logger.error(f"Error validating pump data: {str(e)}")
            raise ValueError(f"Data validation failed: {str(e)}")

    @staticmethod
    def validate_bom_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate BOM data before import"""
        try:
            # Validate pump SKU
            if not data.get('pump_sku'):
                raise ValueError("Pump SKU is required")
            
            # Verify pump SKU exists
            query = "SELECT 1 FROM general_pump_details WHERE sku = %s"
            if not DatabaseManager.execute_query(query, (data['pump_sku'],)):
                raise ValueError(f"Pump SKU {data['pump_sku']} does not exist")

            # Validate inertia base part number if provided
            if base_num := data.get('inertia_base_part_number'):
                query = "SELECT 1 FROM inertia_bases WHERE part_number = %s"
                if not DatabaseManager.execute_query(query, (base_num,)):
                    raise ValueError(f"Inertia base part number {base_num} does not exist")

            # Validate seismic spring part number if provided
            if spring_num := data.get('seismic_spring_part_number'):
                query = "SELECT 1 FROM seismic_springs WHERE part_number = %s"
                if not DatabaseManager.execute_query(query, (spring_num,)):
                    raise ValueError(f"Seismic spring part number {spring_num} does not exist")

            return data

        except Exception as e:
            logger.error(f"Error validating BOM data: {str(e)}")
            raise ValueError(f"Data validation failed: {str(e)}")

    @staticmethod
    def validate_numeric(value: Any, field_name: str, allow_zero: bool = False) -> Decimal:
        """Validate numeric values"""
        try:
            if value is None:
                raise ValueError(f"{field_name} cannot be None")
                
            value = Decimal(str(value))
            if not allow_zero and value <= 0:
                raise ValueError(f"{field_name} must be positive")
                
            return value
        except (ValueError, TypeError):
            raise ValueError(f"Invalid {field_name} value")

    @staticmethod
    def validate_text(value: Optional[str], field_name: str, required: bool = True) -> Optional[str]:
        """Validate text values"""
        if value is None:
            if required:
                raise ValueError(f"{field_name} is required")
            return None
            
        value = str(value).strip()
        if required and not value:
            raise ValueError(f"{field_name} cannot be empty")
            
        return value

    @staticmethod
    def validate_reference(
        value: str,
        field_name: str,
        table: str,
        column: str
    ) -> None:
        """Validate reference exists in database"""
        query = f"SELECT 1 FROM {table} WHERE {column} = %s"
        if not DatabaseManager.execute_query(query, (value,)):
            raise ValueError(f"Referenced {field_name} {value} does not exist")