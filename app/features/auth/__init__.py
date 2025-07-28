from flask import Blueprint

# Create the authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Import routes to register them with the blueprint
from . import routes 