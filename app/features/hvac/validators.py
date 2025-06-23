from typing import Dict, Any, Optional
from wtforms.validators import ValidationError
from app.core.core_errors import ValidationError as AppValidationError
import re
from app.models.pumps.pump_model import Pump, PumpSeries

def validate_flow_rate(form: Any, field: Any) -> None:
    """
    Validate flow rate value
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If flow rate is invalid
    """
    if field.data <= 0:
        raise ValidationError('Flow rate must be greater than 0')
    
    if field.data > 10000:  # Example maximum value
        raise ValidationError('Flow rate exceeds maximum allowed value')

def validate_head(form: Any, field: Any) -> None:
    """
    Validate head value
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If head is invalid
    """
    if field.data <= 0:
        raise ValidationError('Head must be greater than 0')
    
    if field.data > 1000:  # Example maximum value
        raise ValidationError('Head exceeds maximum allowed value')

def validate_sku_format(form: Any, field: Any) -> None:
    """
    Validate SKU format
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If SKU format is invalid
    """
    if not re.match(r'^[A-Z0-9-]+$', field.data):
        raise ValidationError('SKU must contain only uppercase letters, numbers, and hyphens')

def validate_power_range(form: Any, field: Any) -> None:
    """
    Validate power value is within acceptable range
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If power is invalid
    """
    if field.data <= 0:
        raise ValidationError('Power must be greater than 0')
    
    if field.data > 1000:  # Example maximum value
        raise ValidationError('Power exceeds maximum allowed value')

def validate_efficiency(form: Any, field: Any) -> None:
    """
    Validate efficiency value
    Args:
        form: Form instance
        field: Field to validate
    Raises:
        ValidationError: If efficiency is invalid
    """
    if field.data is not None:
        if field.data < 0 or field.data > 100:
            raise ValidationError('Efficiency must be between 0 and 100')

def validate_pump_series(series: str) -> bool:
    """
    Validate pump series
    Args:
        series: Pump series to validate
    Returns:
        bool: True if valid
    Raises:
        AppValidationError: If series is invalid
    """
    try:
        PumpSeries(series)
        return True
    except ValueError:
        raise AppValidationError(f"Invalid pump series: {series}")

def validate_unique_sku(sku: str, pump_id: Optional[int] = None) -> bool:
    """
    Validate SKU uniqueness
    Args:
        sku: SKU to validate
        pump_id: Optional pump ID to exclude from check
    Returns:
        bool: True if valid
    Raises:
        AppValidationError: If SKU is not unique
    """
    query = Pump.query.filter(Pump.sku == sku)
    if pump_id:
        query = query.filter(Pump.id != pump_id)
    
    if query.first():
        raise AppValidationError(f"SKU {sku} already exists")
    return True

def validate_operating_point(flow_rate: float, head: float, pump: Pump) -> bool:
    """
    Validate if operating point is within pump's range
    Args:
        flow_rate: Flow rate to validate
        head: Head to validate
        pump: Pump instance
    Returns:
        bool: True if valid
    Raises:
        AppValidationError: If operating point is invalid
    """
    # Assuming pump has min/max flow and head attributes
    if hasattr(pump, 'min_flow') and pump.min_flow is not None:
        if flow_rate < pump.min_flow:
            raise AppValidationError("Flow rate below pump's minimum")
            
    if hasattr(pump, 'max_flow') and pump.max_flow is not None:
        if flow_rate > pump.max_flow:
            raise AppValidationError("Flow rate above pump's maximum")
            
    if hasattr(pump, 'min_head') and pump.min_head is not None:
        if head < pump.min_head:
            raise AppValidationError("Head below pump's minimum")
            
    if hasattr(pump, 'max_head') and pump.max_head is not None:
        if head > pump.max_head:
            raise AppValidationError("Head above pump's maximum")
    
    return True

def validate_pump_data(data: Dict[str, Any]) -> None:
    """
    Validate pump data dictionary
    Args:
        data: Dictionary of pump data
    Raises:
        AppValidationError: If validation fails
    """
    required_fields = ['sku', 'series', 'power_kw']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        raise AppValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
    # Validate individual fields
    validate_sku_format(None, type('Field', (), {'data': data['sku']}))
    validate_pump_series(data['series'])
    
    if data.get('power_kw'):
        validate_power_range(None, type('Field', (), {'data': float(data['power_kw'])}))
        
    if data.get('efficiency'):
        validate_efficiency(None, type('Field', (), {'data': float(data['efficiency'])}))