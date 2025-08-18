from flask import Blueprint

# Defines the Blueprint for the 'plumbing' feature.
plumbing_bp = Blueprint(
    'plumbing', 
    __name__,
    template_folder='../templates'
)

# This import registers the routes with this blueprint
from . import routes