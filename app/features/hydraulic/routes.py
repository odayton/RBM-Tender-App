from flask import render_template
import logging

# Import the blueprint from the local package __init__.py
from . import hydraulic_bp

logger = logging.getLogger(__name__)

@hydraulic_bp.route('/hydraulic')
def hydraulic():
    """Renders the main hydraulic page."""
    logger.info('Rendering hydraulic main page')
    return render_template('hydraulic/hydraulic.html')