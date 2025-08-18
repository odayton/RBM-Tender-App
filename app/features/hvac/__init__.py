from flask import Blueprint

# The blueprint is now correctly named 'hvac'
hvac_bp = Blueprint(
    'hvac', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/hvac/static'
)

# This line imports the routes and attaches them to the blueprint above
from . import routes