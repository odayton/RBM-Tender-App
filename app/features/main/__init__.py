from flask import Blueprint

# This line creates the Blueprint object for all routes defined in this feature.
# The name 'main' is used for url_for(), e.g., url_for('main.home').
main_bp = Blueprint('main', __name__)

# This import is at the bottom to avoid circular dependencies.
# It makes the routes in routes.py aware of the main_bp object.
from . import routes