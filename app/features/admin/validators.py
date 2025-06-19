from typing import List, Dict, Any, Optional
from wtforms.validators import ValidationError
from app.core.core_errors import ValidationError as AppValidationError
import re
import os

def validate_part_number(form: Any, field: Any) -> None:
    """
    Validate part number format
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If part number format is invalid
    """
    # Part numbers should be alphanumeric with optional hyphens
    if not re.match(r'^[A-Z0-9-]+$', field.data):
        raise ValidationError('Part number must contain only uppercase letters, numbers, and hyphens')

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> None:
    """
    Validate file extension
    Args:
        filename: Name of file to validate
        allowed_extensions: List of allowed extensions
    Raises:
        AppValidationError: If file extension is not allowed
    """
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    if ext not in allowed_extensions:
        raise AppValidationError(f'File type .{ext} is not allowed. Allowed types: {", ".join(allowed_extensions)}')

def validate_excel_content(file_data: bytes, required_columns: List[str]) -> None:
    """
    Validate Excel file content
    Args:
        file_data: Excel file content
        required_columns: List of required column names
    Raises:
        AppValidationError: If content validation fails
    """
    try:
        import pandas as pd
        df = pd.read_excel(file_data)
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise AppValidationError(f'Missing required columns: {", ".join(missing_columns)}')
            
    except Exception as e:
        raise AppValidationError(f'Error validating Excel content: {str(e)}')

def validate_price(form: Any, field: Any) -> None:
    """
    Validate price value
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If price is invalid
    """
    if field.data <= 0:
        raise ValidationError('Price must be greater than 0')
        
    if len(str(field.data).split('.')[-1]) > 2:
        raise ValidationError('Price cannot have more than 2 decimal places')

def validate_size_format(form: Any, field: Any) -> None:
    """
    Validate size format (e.g., '800 X 600 X 125')
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If size format is invalid
    """
    if not re.match(r'^\d+\s*X\s*\d+\s*X\s*\d+$', field.data.upper()):
        raise ValidationError('Size must be in format: LENGTH X WIDTH X HEIGHT')

def validate_load_capacity(form: Any, field: Any) -> None:
    """
    Validate load capacity value
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If load capacity is invalid
    """
    if field.data <= 0:
        raise ValidationError('Load capacity must be greater than 0')
    
    if field.data > 10000:  # Example maximum value
        raise ValidationError('Load capacity exceeds maximum allowed value')

def validate_pdf_content(file_data: bytes) -> None:
    """
    Validate PDF file content
    Args:
        file_data: PDF file content
    Raises:
        AppValidationError: If content validation fails
    """
    try:
        import PyPDF2
        pdf = PyPDF2.PdfReader(file_data)
        
        if len(pdf.pages) == 0:
            raise AppValidationError('PDF file is empty')
            
    except Exception as e:
        raise AppValidationError(f'Error validating PDF content: {str(e)}')

def validate_unique_part_number(part_number: str, model: Any) -> None:
    """
    Validate part number uniqueness
    Args:
        part_number: Part number to validate
        model: Model class to check against
    Raises:
        AppValidationError: If part number is not unique
    """
    if model.query.filter_by(part_number=part_number).first():
        raise AppValidationError(f'Part number {part_number} already exists')

def validate_weight_range(form: Any, field: Any) -> None:
    """
    Validate weight is within acceptable range
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If weight is invalid
    """
    if field.data <= 0:
        raise ValidationError('Weight must be greater than 0')
    
    if field.data > 1000:  # Example maximum value
        raise ValidationError('Weight exceeds maximum allowed value')

def validate_pump_series(form: Any, field: Any) -> None:
    """
    Validate pump series selection
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If pump series is invalid
    """
    valid_series = ['NBG', 'CR', 'TP', 'CM', 'MAGNA', 'UPS', 'CRE', 'TPE', 'NK']
    if field.data not in valid_series:
        raise ValidationError('Invalid pump series selected')