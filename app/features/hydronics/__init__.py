from flask import Blueprint

# Defines the Blueprint for the 'hydronics' feature
hydronics_bp = Blueprint(
    'hydronics', 
    __name__,
    template_folder='../templates'
)

from . import routes