from flask import render_template
import logging

# Import the blueprint object that was created in the __init__.py file
from . import plumbing_bp

logger = logging.getLogger(__name__)

@plumbing_bp.route('/')
def index():
    """Renders the main plumbing page."""
    logger.info('Rendering plumbing main page')
    return render_template('plumbing/plumbing.html')