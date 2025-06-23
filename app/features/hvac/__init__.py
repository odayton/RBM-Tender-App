from flask import Blueprint

# Defines the Blueprint object for the 'hvac' feature.
hvac_bp = Blueprint(
    'hvac', 
    __name__,
    template_folder='../templates'
)

# This import registers the routes with this blueprint
from . import routes