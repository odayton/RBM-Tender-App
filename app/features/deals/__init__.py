from flask import Blueprint

# Defines the Blueprint object for the 'deals' feature.
deals_bp = Blueprint(
    'deals', 
    __name__,
    template_folder='templates',
    static_folder='static'
)

# This import is at the bottom to avoid circular dependencies.
# It makes the routes in routes.py aware of the deals_bp object.
from . import routes