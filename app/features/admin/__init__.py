from flask import Blueprint

# Defines the Blueprint object for the 'admin' feature.
admin_bp = Blueprint(
    'admin', 
    __name__,
    template_folder='../templates' # Points to the app's main templates folder
)

# This import registers the routes from routes.py with this blueprint
from . import routes