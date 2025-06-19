from flask import Blueprint

# Defines the Blueprint object for the 'pumps' feature.
pumps_bp = Blueprint(
    'pumps', 
    __name__,
    template_folder='../templates'
)

# This import registers the routes with this blueprint
from . import routes