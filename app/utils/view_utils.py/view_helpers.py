from typing import Dict, Any, List, Optional, Union
from flask import flash, url_for, redirect, request
from werkzeug.wrappers import Response
from functools import wraps

def flash_errors(form) -> None:
    """Flash form validation errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}", "error")

def redirect_back(default: str = 'index', **kwargs) -> Response:
    """Redirect back to referrer or default"""
    return redirect(request.referrer or url_for(default, **kwargs))

def get_pagination_params() -> Dict[str, int]:
    """Get pagination parameters from request"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        return {'page': max(1, page), 'per_page': min(100, max(1, per_page))}
    except (TypeError, ValueError):
        return {'page': 1, 'per_page': 20}

def get_sort_params() -> Dict[str, str]:
    """Get sorting parameters from request"""
    sort_by = request.args.get('sort_by', 'created_at')
    sort_dir = request.args.get('sort_dir', 'desc')
    return {'sort_by': sort_by, 'sort_dir': sort_dir}

def handle_view_errors(func):
    """Decorator to handle view exceptions"""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            flash(str(e), "error")
            return redirect_back()
    return decorated_function

def get_filter_params() -> Dict[str, Any]:
    """Get filter parameters from request"""
    filters = {}
    for key, value in request.args.items():
        if key not in ['page', 'per_page', 'sort_by', 'sort_dir'] and value:
            filters[key] = value
    return filters