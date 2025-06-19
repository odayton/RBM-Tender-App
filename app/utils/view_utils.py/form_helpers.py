from typing import Dict, Any, List, Optional
from werkzeug.datastructures import MultiDict
from flask_wtf import FlaskForm
from wtforms import SelectField

def populate_form_choices(form: FlaskForm, field_name: str, choices: List[tuple]) -> None:
    """
    Populate select field choices.
    
    Args:
        form: The form instance
        field_name: Name of the field to populate
        choices: List of tuples containing (value, label)
    """
    if hasattr(form, field_name):
        field = getattr(form, field_name)
        if isinstance(field, SelectField):
            field.choices = choices

def convert_form_errors(form: FlaskForm) -> Dict[str, List[str]]:
    """
    Convert WTForms validation errors to dictionary.
    
    Args:
        form: The form instance
        
    Returns:
        Dict with field names as keys and list of error messages as values
    """
    errors = {}
    for field_name, field_errors in form.errors.items():
        errors[field_name] = field_errors
    return errors

def prepare_form_data(data: Dict[str, Any]) -> MultiDict:
    """
    Prepare dictionary data for form population.
    
    Args:
        data: Dictionary of form data
        
    Returns:
        MultiDict suitable for form population
    """
    form_data = MultiDict()
    for key, value in data.items():
        if isinstance(value, (list, tuple)):
            for item in value:
                form_data.add(key, item)
        else:
            form_data.add(key, value)
    return form_data

def update_form_from_model(form: FlaskForm, model_instance: Any) -> None:
    """
    Update form data from model instance.
    
    Args:
        form: The form instance
        model_instance: Database model instance
    """
    for field in form:
        if hasattr(model_instance, field.name):
            field.data = getattr(model_instance, field.name)

def get_form_data(form: FlaskForm) -> Dict[str, Any]:
    """
    Get cleaned data from form.
    
    Args:
        form: The form instance
        
    Returns:
        Dict of cleaned form data
    """
    data = {}
    for field in form:
        if field.data:
            data[field.name] = field.data
    return data