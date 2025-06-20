from flask import Blueprint

# Defines the Blueprint for the static server feature.
# This is often used for serving documentation or other static assets.
static_server_bp = Blueprint(
    'static_server', 
    __name__,
    static_folder='static',
    static_url_path='/static/docs' # Example URL path
)

# This import is at the bottom to avoid circular dependencies.
from . import routes