from flask import Blueprint

# Defines the Blueprint for the 'hydronic_heating' feature
hydronic_heating_bp = Blueprint(
    'hydronic_heating', 
    __name__,
    template_folder='../templates'
)

# This import registers the routes with this blueprint
from . import routes