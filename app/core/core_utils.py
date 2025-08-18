from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
import re
import uuid
import hashlib
from pathlib import Path
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder for handling Decimal types"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique identifier with optional prefix"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id

def hash_file(file_path: Union[str, Path], chunk_size: int = 65536) -> str:
    """
    Generate SHA-256 hash of a file
    Args:
        file_path: Path to the file
        chunk_size: Size of chunks to read
    Returns:
        str: Hex digest of file hash
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def sanitize_filename(filename: str) -> str:
    """
    Clean filename to prevent path traversal and ensure safe characters
    Args:
        filename: Original filename
    Returns:
        str: Sanitized filename
    """
    # Remove path components
    filename = Path(filename).name
    # Replace potentially dangerous characters
    filename = re.sub(r'[^\w\s.-]', '_', filename)
    return filename.strip()

def format_currency(amount: Union[float, Decimal], currency: str = "EUR") -> str:
    """
    Format currency amount with proper separators and currency symbol
    Args:
        amount: Amount to format
        currency: Currency code (default: EUR)
    Returns:
        str: Formatted currency string
    """
    if currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"

def parse_date(date_str: str) -> Optional[date]:
    """
    Parse date string in multiple formats
    Args:
        date_str: Date string to parse
    Returns:
        date: Parsed date object or None if invalid
    """
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

def calculate_percentage(value: Union[float, Decimal], total: Union[float, Decimal]) -> float:
    """
    Calculate percentage safely handling division by zero
    Args:
        value: Value to calculate percentage for
        total: Total value
    Returns:
        float: Calculated percentage
    """
    try:
        if total == 0:
            return 0.0
        return float(value) / float(total) * 100
    except (TypeError, ValueError):
        return 0.0

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten nested dictionary with custom separator
    Args:
        d: Dictionary to flatten
        parent_key: Base key for nested items
        sep: Separator between nested keys
    Returns:
        Dict: Flattened dictionary
    """
    items: List = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def round_decimal(value: Union[float, Decimal], places: int = 2) -> Decimal:
    """
    Round decimal values consistently
    Args:
        value: Value to round
        places: Number of decimal places
    Returns:
        Decimal: Rounded value
    """
    try:
        return Decimal(str(value)).quantize(Decimal(10) ** -places)
    except (TypeError, ValueError):
        return Decimal('0.00')

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    Args:
        size_bytes: Size in bytes
    Returns:
        str: Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove None values and empty strings from dictionary
    Args:
        data: Dictionary to clean
    Returns:
        Dict: Cleaned dictionary
    """
    return {k: v for k, v in data.items() if v is not None and v != ""}

def validate_email(email: str) -> bool:
    """
    Validate email format
    Args:
        email: Email address to validate
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))