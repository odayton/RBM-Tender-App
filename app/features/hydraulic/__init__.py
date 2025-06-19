from flask import Blueprint

# Defines the Blueprint for the 'hydraulic' feature
hydraulic_bp = Blueprint(
    'hydraulic', 
    __name__,
    template_folder='../templates'
)

from . import routes